from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import RegisterSerializer, LoginSerializer, EmployeeSerializer, DynamicFieldSerializer
from rest_framework import generics, permissions, status, views
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from employee.models import DynamicField, Employee
from accounts.tasks import send_verification_email_task
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page'
    max_page_size = 100

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Get current site
        current_site = get_current_site(request)
        protocol = 'https' if request.is_secure() else 'http'
        try:
                
            # Trigger the Celery task to send verification email
            send_verification_email_task.delay(
                user_id=user.id,
                domain=current_site.domain,
                protocol=protocol
            )
        except Exception as e:
            print('error:', e)
        return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
    

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        response = Response({
            "message": "Login successful",
            "username": user.username,
        }, status=status.HTTP_200_OK)

        # 🔐 Store tokens in HTTP-only cookies
        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=True,      # True in production (HTTPS)
            samesite="Strict",
            max_age=15 * 60,
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=7 * 24 * 60 * 60,
        )

        return response


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            print(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class DynamicFieldListCreateAPIView(generics.ListCreateAPIView):
    queryset = DynamicField.objects.all().order_by('order')
    serializer_class = DynamicFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class DynamicFieldRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DynamicField.objects.all()
    serializer_class = DynamicFieldSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Field deleted successfully"}, status=204)


class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class EmployeeRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination


class SessionInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        session_data = {
            'session_id': request.session.session_key,
            'user_id': request.session.get('user_id'),
            'is_authenticated': request.session.get('is_authenticated', False),
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
            }
        }
        return Response(session_data)


class SessionLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        
        # Create session
        request.session['user_id'] = user.id
        request.session['is_authenticated'] = True
        request.session.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        response = Response({
            "message": "Login successful",
            "username": user.username,
            "session_id": request.session.session_key,
            "user_id": user.id,
            "access": str(access),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)
        
        # Set cookies
        response.set_cookie(
            key="access_token",
            value=str(access),
            httponly=True,
            secure=False,  # Set to True in production
            samesite="Lax",
            max_age=15 * 60,
        )
        
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60,
        )
        
        return response


class SessionLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Clear session
            request.session.flush()
            
            # Blacklist refresh token if provided
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Clear cookies
            response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            
            return response
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import render
from rest_framework import generics
from .serializers import CustomUserSerializer, UserLoginSerializer
from accounts.models import CustomUser
from rest_framework import permissions
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer

class CustomUserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        
        # Create a serializable user dictionary
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            # Add any other user fields you want to include
        }
        
        return Response({
            "message": "Login successful",
            "user": user_data,
        })


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        return Task.objects.all()
    
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            user = CustomUser.objects.get(id=2)
            serializer.save(user=user)


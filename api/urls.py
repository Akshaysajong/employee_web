from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="api-register"),
    # path("login/", TokenObtainPairView.as_view(), name="api_login"),
    path('login/', views.LoginView.as_view(), name='api_login'),
    path('session-login/', views.SessionLoginView.as_view(), name='session_login'),
    path('session-info/', views.SessionInfoView.as_view(), name='session_info'),
    path('session-logout/', views.SessionLogoutView.as_view(), name='session_logout'),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', views.LogoutView.as_view(), name='api_logout'),
    
    # Employee endpoints
    path('employees/', views.EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<int:pk>/', views.EmployeeRetrieveUpdateDeleteView.as_view(), name='employee-detail'),
    
    # DynamicField endpoints
    path('dynamic-fields/', views.DynamicFieldListCreateAPIView.as_view(), name='dynamic-field-list-create'),
    path('dynamic-fields/<int:pk>/', views.DynamicFieldRetrieveUpdateDestroyAPIView.as_view(), name='dynamic-field-detail'),
]
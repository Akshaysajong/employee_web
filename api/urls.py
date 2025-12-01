from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, LoginView, LogoutView, EmployeeListCreateView, EmployeeRetrieveUpdateDeleteView, DynamicFieldListCreateAPIView, DynamicFieldRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="api-register"),
    path('login/', LoginView.as_view(), name='api_login'),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', LogoutView.as_view(), name='api_logout'),

    path('employees/', EmployeeListCreateView.as_view(), name='employee_list_create'),
    path('employee/<int:pk>/', EmployeeRetrieveUpdateDeleteView.as_view(), name='employee_detail'),

    path('fields/', DynamicFieldListCreateAPIView.as_view(), name='dynamic_field_list_create'),
    path('fields/<int:pk>/', DynamicFieldRetrieveUpdateDestroyAPIView.as_view(), name='dynamic_field_detail'),
]
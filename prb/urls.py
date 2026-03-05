from django.urls import path
from .views import CustomUserCreateView, LoginView, TaskListCreateView

urlpatterns = [
    path('register/', CustomUserCreateView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
]
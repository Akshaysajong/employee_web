from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Form Builder URLs
    path('fields/', views.form_builder, name='form_builder'),
    path('save-fields/', views.save_dynamic_field, name='save_field'),
    path('delete-field/<int:id>/', views.delete_field, name='delete_field'),

    # Employee URLs
    path('employee/create/', views.create_employee, name='create_employee'),
    path('save-employee/', views.save_employee, name='save_employee'),
    path('employee/list/', views.list_employees, name='list_employees'),
    path('delete-employee/<int:id>/', views.delete_employees, name='delete_employee'),
]


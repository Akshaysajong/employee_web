from django.urls import path
from . import views

urlpatterns = [
    path('fields/', views.form_builder, name='form_builder'),
    path('save-fields/', views.save_dynamic_field, name='save_field'),
    path('delete-field/<int:id>/', views.delete_field, name='delete_field'),

    path('employee/create/', views.create_employee, name="create_employee"),
    path('save-employee/', views.save_employee, name="save_employee"),

    path('employee/list/', views.list_employees, name="list-employees"),
    path('delete-employee/<int:id>/', views.delete_employees, name="delete-employee"),
]


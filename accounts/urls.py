from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path("profile/", views.profile_page, name="profile"),
    path("logout/", views.logout_user, name="logout"),

    path("change-password/", views.change_password_page, name="change_password"),
]
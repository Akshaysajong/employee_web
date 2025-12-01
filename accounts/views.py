from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"message": "Username already exists"})

        User.objects.create_user(username=username, email=email, password=password)
        return redirect("/login/")

    return render(request, "register.html")


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect("/auth/profile/")
        else:
            return render(request, "login.html")
    return render(request, "login.html")

def profile_page(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    return render(request, "profile.html")

def logout_user(request):
    logout(request)
    return redirect("/auth/login/")

def change_password_page(request):
    if request.method == "POST":
        old = request.POST.get("oldpassword")
        new = request.POST.get("newpassword")

        user = request.user

        if not user.check_password(old):
            return render(request, "change_password.html", {"message": "Old password incorrect"})

        user.set_password(new)
        user.save()
        update_session_auth_hash(request, user)

        return redirect("/auth/profile/")
    return render(request, "change_password.html")
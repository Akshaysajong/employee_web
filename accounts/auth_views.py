from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.views import (
    PasswordChangeView, PasswordResetView, PasswordResetConfirmView
)
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
)
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
from .forms import CustomUserCreationForm, ProfileUpdateForm
# from .tasks import send_verification_email_task

class CustomPasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = 'registration/change_password.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        # Update the session with the new password
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, 'Your password was successfully updated!')
        return super().form_valid(form)

class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

def send_verification_email(request, user):
    """Helper function to send verification email"""
    current_site = get_current_site(request)
    protocol = 'https' if request.is_secure() else 'http'
    
    # Trigger the Celery task
    send_verification_email_task.delay(
        user_id=user.id,
        domain=current_site.domain,
        protocol=protocol
    )

def verify_email_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            send_verification_email(request, user)
            return redirect('verify_email_done')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No account is associated with this email.')
    return render(request, 'registration/verify_email_request.html')

def verify_email_confirm(request, uidb64, token):
    print('uidb64:', uidb64)
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        print('user:', user)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        print('user:', user)
        user.is_active = True
        user.is_verified = True
        user.save()
        return redirect('verify_email_complete')
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
        return redirect('login')

def verify_email_done(request):
    return render(request, 'registration/verify_email_done.html')

def verify_email_complete(request):
    return render(request, 'emails/verify_email_done.html')

def enable_2fa(request):
    if request.method == 'POST':
        # Implement 2FA setup logic here
        # This is a placeholder for actual 2FA implementation
        messages.success(request, 'Two-factor authentication has been enabled.')
        return redirect('profile')
    return render(request, 'registration/enable_2fa.html')

def disable_2fa(request):
    if request.method == 'POST':
        # Implement 2FA disable logic here
        messages.success(request, 'Two-factor authentication has been disabled.')
        return redirect('profile')
    return render(request, 'registration/disable_2fa.html')

def verify_2fa(request):
    if request.method == 'POST':
        # Implement 2FA verification logic here
        code = request.POST.get('code')
        # Verify the code and log the user in if valid
        return redirect('profile')
    return render(request, 'registration/verify_2fa.html')

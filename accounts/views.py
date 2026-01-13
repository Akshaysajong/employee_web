from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import UpdateView
from django.urls import reverse_lazy

from .models import CustomUser, UserProfile
from .forms import CustomUserCreationForm, ProfileUpdateForm
from .auth_views import (
    CustomPasswordChangeView, CustomPasswordResetView, CustomPasswordResetConfirmView,
    verify_email_request, verify_email_confirm, verify_email_done, verify_email_complete,
    enable_2fa, disable_2fa, verify_2fa
)
from .tasks import send_verification_email_task


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True  # User is inactive until email is verified
            user.save()
            
            # Create user profile
            # UserProfile.objects.create(user=user)
            
            # Get current site
            current_site = get_current_site(request)
            protocol = 'https' if request.is_secure() else 'http'
            # send_verification_email(request, user)
            
            try:
                print('1111111111111111111111')
                # Trigger the Celery task to send verification email
                send_verification_email_task.delay(
                    user_id=user.id,
                    domain=current_site.domain,
                    protocol=protocol
                )
            except Exception as e:
                print('error:', e)
            
            messages.success(request, 'Please check your email to verify your account.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Set session variables
            request.session["user_id"] = user.id
            request.session["username"] = user.username
            
            # Check if 2FA is required
            if hasattr(user, 'two_factor_enabled') and user.two_factor_enabled:
                return redirect('verify_2fa')
                
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, "login.html", {"form": form})


@login_required
def profile(request):
    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'two_factor_enabled': hasattr(request.user, 'two_factor_enabled') and request.user.two_factor_enabled
    })


@login_required
def profile_update(request):
    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = ProfileUpdateForm(
            data=request.POST, 
            files=request.FILES, 
            instance=request.user
        )
        
        if user_form.is_valid():
            user = user_form.save(commit=False)
            
            # Handle profile picture separately
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            
            user.save()
            
            # Update profile fields
            profile.bio = request.POST.get('bio', '')
            profile.address = request.POST.get('address', '')
            
            date_of_birth = request.POST.get('date_of_birth')
            if date_of_birth:
                from datetime import datetime
                try:
                    profile.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass
            
            profile.save()
            
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = ProfileUpdateForm(instance=request.user)
    
    # Initialize form with profile data
    initial_data = {
        'bio': profile.bio,
        'address': profile.address,
        'date_of_birth': profile.date_of_birth.strftime('%Y-%m-%d') if profile.date_of_birth else ''
    }
    
    return render(request, 'accounts/profile_update.html', {
        'form': user_form,
        'initial': initial_data
    })


@login_required
def account_delete(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
    return render(request, 'accounts/account_confirm_delete.html')

def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('login')

class ChangePasswordView(CustomPasswordChangeView):
    template_name = 'registration/change_password.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        messages.success(self.request, 'Your password was successfully updated!')
        return super().form_valid(form)

# def send_verification_email(request):
#     """
#     Send a verification email to the user with a verification link
#     Returns True if email was sent successfully, False otherwise
#     """
#     try:
#         sender = settings.EMAIL_HOST_USER
#         password = settings.EMAIL_HOST_PASSWORD
#         receiver = 'akshaysajong@gmail.com'
#         # current_site = get_current_site(request)
#         # print(f'[DEBUG] Sending verification email to {user.email} from {current_site.domain}')
        
#         # Generate verification URL components
#         # uid = urlsafe_base64_encode(force_bytes(user.pk))
#         # token = default_token_generator.make_token(user)
#         protocol = 'https' if request.is_secure() else 'http'
        
#         # Prepare email context
#         context = {
#             'user': "user",
#             'domain': "current_site.domain",
#             'uid': "uid",
#             'token': "token",
#             'protocol': "protocol",
#         }
        
#         # Render email content
#         mail_subject = 'Verify your email address'
#         try:
#             message = render_to_string('emails/verify_email_required.html', context)
#             # Plain text fallback
#             text_content = f"""
#             Please verify your email by clicking the link below:
            
#             """
#         except Exception as e:
#             print(f'[ERROR] Error rendering email template: {str(e)}')
#             text_content = f'Please verify your email by visiting: '
#             message = text_content
       
#         # Send the email
#         try:
#             with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
#             server.ehlo()
#             if settings.EMAIL_USE_TLS:
#                 server.starttls()
#                 server.ehlo()
#             server.login(sender, password)
#             server.sendmail(sender, [receiver], message)
        
#             return HttpResponse("✅ Test email sent successfully! Please check your inbox.")
#             # return True
            
#         except Exception as e:
#             print(f'[ERROR] Failed to send verification email to : {str(e)}')
#             # return False
            
#     except Exception as e:
#         print(f'[ERROR] Error in send_verification_email for user : {str(e)}')
#         # return False
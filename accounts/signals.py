from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        print(f"Created profile for user: {instance.username}")

# @receiver(post_save, sender=User)
# def send_verification_email_signal(sender, instance, created, **kwargs):
#     """
#     Send verification email when a new user is created
#     """

#     if created and not instance.is_verified:
#         # Trigger the Celery task
#         from django.contrib.sites.shortcuts import get_current_site
#         from django.urls import reverse
#         from django.utils.encoding import force_bytes
#         from django.utils.http import urlsafe_base64_encode
#         from django.contrib.auth.tokens import default_token_generator

#         current_site = get_current_site(None)  # We'll handle the request in the task
#         send_verification_email_task.delay(
#             user_id=instance.id,
#             domain=current_site.domain,
#             protocol='https'  # or get this from request
#         )
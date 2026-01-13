# accounts/tasks.py
import logging
from celery import shared_task
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task(bind=True, max_retries=3, default_retry_delay=60)  # Retry 3 times with 60s delay
def send_verification_email_task(self, user_id, domain, protocol):
    print('user_id:', user_id)
    """
    Celery task to send verification email with retry mechanism
    """
    from django.conf import settings
    logger.info(f'[Email Task] Starting verification email task for user_id: {user_id}')
    logger.info(f'[Email Task] Using domain: {domain}, protocol: {protocol}')
    logger.info(f'[Email Task] Email backend: {settings.EMAIL_BACKEND}')
    
    try:
        user = User.objects.get(id=user_id)
        logger.info(f'User found: {user.email}')
        
        # Generate verification URL
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        # Prepare email context
        context = {
            'user': user,
            'domain': domain,
            'uid': uid,
            'token': token,
            'protocol': protocol,
        }
        
        # Render email content
        subject = 'Verify your email address'
        try:
            html_message = render_to_string('emails/verify_email_required.html', context)
            logger.info('Email template rendered successfully')
        except Exception as e:
            logger.error(f'[Email Task] Error rendering email template: {str(e)}')
            html_message = f"Please verify your email by visiting: {protocol}://{domain}/verify-email/{uid}/{token}/"
        
        text_message = f"Please verify your email by visiting: {protocol}://{domain}/verify-email/{uid}/{token}/"
        
        try:
            logger.info(f'[Email Task] Attempting to send email to: {user.email}')
            logger.info(f'[Email Task] Email subject: {subject}')
            logger.info(f'[Email Task] Sender: {settings.EMAIL_HOST_USER}')
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            sender = settings.EMAIL_HOST_USER
            password = settings.EMAIL_HOST_PASSWORD
            recipient = [user.email]

            # Create a multipart message
            message = MIMEMultipart('alternative')
            message["From"] = sender
            message["To"] = ", ".join(recipient)  
            message["Subject"] = subject
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_message, 'plain')
            part2 = MIMEText(html_message, 'html')
            message.attach(part1)
            message.attach(part2)

            context = ssl.create_default_context()
            
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.login(sender, password)
                server.send_message(message)
                logger.info(f'[Email Task] Successfully sent verification email to {user.email}')
                return f"Verification email sent to {user.email}"


        except BadHeaderError as e:
            logger.error(f'Invalid header found in email: {str(e)}')
            # Don't retry on bad headers as it will keep failing
            return f"Failed to send verification email: Invalid header"
            
        except Exception as e:
            logger.error(f'Error sending verification email: {str(e)}')
            # Retry on other exceptions
            raise self.retry(exc=e, countdown=60 * self.request.retries)
            
    except User.DoesNotExist as e:
        logger.error(f'User with id {user_id} does not exist')
        return f"User with id {user_id} does not exist"
        
    except Exception as e:
        logger.error(f'Unexpected error in verification email task: {str(e)}', exc_info=True)
        # Retry on unexpected errors
        raise self.retry(exc=e, countdown=60 * self.request.retries)
        return f"Error sending verification email: {str(e)}"
import os
import sys
import django
from django.core.mail import send_mail
from django.conf import settings

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def send_test_email():
    """Send a test email to verify email settings"""
    try:
        # Test email configuration
        subject = 'Test Email from Django'
        message = 'This is a test email sent from Django.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['akshaysajong@gmail.com']  # Must be a list
        
        print(f"Attempting to send email from {from_email} to {recipient_list}")
        
        # Send the email
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        if result == 1:
            print("✅ Email sent successfully!")
        else:
            print(f"⚠️  Email send returned {result} (expected 1)")
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    send_test_email()
    print('______________________________________')
from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        print('1111111111111111111111111111')
        self.get_response = get_response
        

    def __call__(self, request):
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1')
        # Only check for authenticated users
        if request.user.is_authenticated:
            print('==========================')
            # Get last activity timestamp from session
            last_activity = request.session.get("last_activity")

            if last_activity:
                print('000000000000000000000000000')
                # Convert stored string to datetime object
                last_seen_time = timezone.datetime.fromisoformat(last_activity)
                print('last_seen_time:', last_seen_time)
                # Calculate inactivity time in seconds
                elapsed = (timezone.now() - last_seen_time).total_seconds()

                # If inactive for more than 60 seconds → logout
                if elapsed > 60:
                    logout(request)         # Django logout
                    request.session.flush() # Clear all session data

            # Update last activity timestamp
            request.session["last_activity"] = timezone.now().isoformat()
        else:
            print('user is not authenticated')

        return self.get_response(request)


class CheckUserActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (request.user.is_authenticated and 
            not request.user.is_active and 
            not request.path.startswith('/auth/verify-email/') and
            request.path != reverse('logout')):
            return redirect('verify_email_required')
        return self.get_response(request)
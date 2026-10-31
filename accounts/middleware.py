from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect

class AccountStatusMiddleware:
    """Checks if authenticated user is suspended and prevents access."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            if profile and profile.is_suspended:
                logout(request)
                messages.error(request, "Your account has been suspended by an administrator. Please contact support.")
                return redirect('accounts:login')

        response = self.get_response(request)
        return response

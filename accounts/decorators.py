from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Role

def role_required(*allowed_roles):
    """
    Decorator to restrict view access to specific staff roles or superusers.
    Usage: @role_required(Role.SUPERADMIN, Role.MANAGER)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in with staff credentials to access this area.")
                return redirect(f"/accounts/login/?next={request.path}")

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            profile = getattr(request.user, 'profile', None)
            if not profile or profile.role not in allowed_roles:
                messages.error(request, "Access denied. You do not have permission to view that section.")
                return redirect('catalog:home')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_or_staff_required(view_func):
    """Allows any authorized staff member or superuser into admin dashboard."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access the administration dashboard.")
            return redirect(f"/accounts/login/?next={request.path}")

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.is_staff_member:
            messages.error(request, "Access restricted to authorized administrative staff.")
            return redirect('catalog:home')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

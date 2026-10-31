from .models import Role

def auth_roles(request):
    """Context processor providing user role and permission flags to all templates."""
    context = {
        'is_staff_user': False,
        'user_role': 'anonymous',
        'can_manage_products': False,
        'can_manage_orders': False,
        'can_manage_inventory': False,
        'can_manage_support': False,
        'can_view_reports': False,
        'unread_notifications_count': 0,
    }

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile:
            context['user_role'] = profile.role
            context['is_staff_user'] = profile.is_staff_member
            context['can_manage_products'] = profile.can_manage_products
            context['can_manage_orders'] = profile.can_manage_orders
            context['can_manage_inventory'] = profile.can_manage_inventory
            context['can_manage_support'] = profile.can_manage_support
            context['can_view_reports'] = profile.can_view_reports
            context['unread_notifications_count'] = request.user.notifications.filter(is_read=False).count()
        elif request.user.is_superuser:
            context['user_role'] = 'superadmin'
            context['is_staff_user'] = True
            context['can_manage_products'] = True
            context['can_manage_orders'] = True
            context['can_manage_inventory'] = True
            context['can_manage_support'] = True
            context['can_view_reports'] = True

    return context

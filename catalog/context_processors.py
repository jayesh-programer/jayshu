from django.conf import settings
from .models import Category

def store_context(request):
    """Context processor providing active categories, settings, and site constants."""
    parent_categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories')
    return {
        'nav_categories': parent_categories,
        'currency_symbol': getattr(settings, 'CURRENCY_SYMBOL', '₹'),
        'currency_code': getattr(settings, 'CURRENCY_CODE', 'INR'),
        'free_shipping_threshold': getattr(settings, 'FREE_SHIPPING_THRESHOLD', 999.00),
        'shipping_flat_rate': getattr(settings, 'SHIPPING_FLAT_RATE', 149.00),
    }

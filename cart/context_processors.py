from .services import get_or_create_cart
from .models import Wishlist

def cart_context(request):
    """Provides current cart, item count, and wishlist count across all templates."""
    try:
        cart = get_or_create_cart(request)
        cart_total_items = cart.total_items
        cart_subtotal = cart.subtotal
    except Exception:
        cart = None
        cart_total_items = 0
        cart_subtotal = 0

    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return {
        'global_cart': cart,
        'cart_total_items': cart_total_items,
        'cart_subtotal': cart_subtotal,
        'wishlist_count': wishlist_count,
    }

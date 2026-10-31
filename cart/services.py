from .models import Cart, CartItem

def get_or_create_cart(request):
    """
    Retrieves or creates the appropriate cart for the current visitor.
    If authenticated, returns their database cart and merges any guest session cart.
    If guest, returns or creates a session-based cart.
    """
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    if request.user.is_authenticated:
        # Get or create user cart
        user_cart, _ = Cart.objects.get_or_create(user=request.user)

        # Check if there is an existing anonymous cart from this session to merge
        if session_key:
            guest_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
            if guest_cart and guest_cart != user_cart:
                # Merge guest items into user cart
                for g_item in guest_cart.items.all():
                    existing_item = user_cart.items.filter(
                        product=g_item.product,
                        variant=g_item.variant
                    ).first()
                    if existing_item:
                        existing_item.quantity += g_item.quantity
                        existing_item.save()
                    else:
                        g_item.cart = user_cart
                        g_item.save()
                guest_cart.delete()

        return user_cart
    else:
        # Anonymous user cart
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user__isnull=True)
        return cart

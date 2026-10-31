from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.conf import settings

from .models import Cart, CartItem, Wishlist
from .services import get_or_create_cart
from catalog.models import Product, ProductVariant
from orders.models import Coupon

def cart_detail_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'variant').all()
    subtotal = cart.subtotal

    # Coupon in session
    coupon_code = request.session.get('coupon_code', '')
    coupon = None
    discount = Decimal('0.00')

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid_now():
                discount = coupon.calculate_discount(subtotal)
            else:
                del request.session['coupon_code']
                messages.warning(request, "Applied coupon has expired or reached usage limits.")
        except Coupon.DoesNotExist:
            del request.session['coupon_code']

    # Shipping & tax estimation
    free_threshold = Decimal(str(getattr(settings, 'FREE_SHIPPING_THRESHOLD', 100.00)))
    flat_shipping = Decimal(str(getattr(settings, 'SHIPPING_FLAT_RATE', 15.00)))
    shipping = Decimal('0.00') if subtotal >= free_threshold or subtotal == 0 else flat_shipping

    tax_rate = Decimal(str(getattr(settings, 'TAX_RATE_PERCENTAGE', 5.00))) / Decimal('100.00')
    taxable = max(Decimal('0.00'), subtotal - discount)
    tax = round(taxable * tax_rate, 2)
    grand_total = max(Decimal('0.00'), taxable + shipping)

    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'coupon': coupon,
        'discount': discount,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
    })


@require_POST
def add_to_cart_view(request):
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id') or None
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    product = get_object_or_404(Product, id=product_id, is_active=True)
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product, is_active=True)

    available_stock = variant.stock if variant else product.stock
    if available_stock <= 0:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Sorry, this product is out of stock.'}, status=400)
        messages.error(request, f"Sorry, {product.name} is currently out of stock.")
        return redirect(product.get_absolute_url())

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > available_stock:
            new_quantity = available_stock
            msg = f"Quantity capped to maximum available stock ({available_stock})."
        else:
            msg = f"Added {quantity} more to your cart."
        cart_item.quantity = new_quantity
        cart_item.save()
    else:
        if cart_item.quantity > available_stock:
            cart_item.quantity = available_stock
            cart_item.save()
        msg = f"Added {product.name} to your shopping cart."

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': msg,
            'total_items': cart.total_items,
            'subtotal': float(cart.subtotal)
        })

    messages.success(request, msg)
    return redirect('cart:cart_detail')


@require_POST
def update_cart_item_view(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    if quantity <= 0:
        cart_item.delete()
        msg = "Item removed from cart."
    else:
        available_stock = cart_item.variant.stock if cart_item.variant else cart_item.product.stock
        if quantity > available_stock:
            quantity = available_stock
            msg = f"Quantity limited to available stock ({available_stock})."
        else:
            msg = "Cart updated."
        cart_item.quantity = quantity
        cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': msg,
            'total_items': cart.total_items,
            'subtotal': float(cart.subtotal),
            'line_total': float(cart_item.line_total) if quantity > 0 else 0
        })

    messages.info(request, msg)
    return redirect('cart:cart_detail')


@require_POST
def remove_from_cart_view(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    name = cart_item.product.name
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f"Removed {name} from cart.",
            'total_items': cart.total_items,
            'subtotal': float(cart.subtotal)
        })

    messages.info(request, f"Removed {name} from your cart.")
    return redirect('cart:cart_detail')


@require_POST
def apply_coupon_view(request):
    code = request.POST.get('code', '').strip().upper()
    cart = get_or_create_cart(request)

    if not code:
        messages.warning(request, "Please enter a coupon code.")
        return redirect('cart:cart_detail')

    try:
        coupon = Coupon.objects.get(code=code)
        if not coupon.is_valid_now():
            messages.error(request, "This coupon is either expired, inactive, or has reached its usage limit.")
        elif cart.subtotal < coupon.min_order_value:
            messages.warning(request, f"This coupon requires a minimum subtotal of ${coupon.min_order_value}.")
        else:
            request.session['coupon_code'] = coupon.code
            messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code.")

    return redirect('cart:cart_detail')


def remove_coupon_view(request):
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        messages.info(request, "Coupon removed.")
    return redirect('cart:cart_detail')


@login_required
def wishlist_view(request):
    wishlist_items = request.user.wishlist_items.select_related('product').all()
    return render(request, 'storefront/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
@require_POST
def toggle_wishlist_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        item.delete()
        saved = False
        msg = f"Removed {product.name} from wishlist."
    else:
        saved = True
        msg = f"Saved {product.name} to your wishlist."

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'saved': saved,
            'message': msg,
            'wishlist_count': request.user.wishlist_items.count()
        })

    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'catalog:product_list'))

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.conf import settings

from .models import Order, OrderStatus, Coupon, PaymentMethod
from .forms import CheckoutForm
from .services import process_order_checkout, cancel_order_and_restore_stock
from cart.services import get_or_create_cart
from accounts.models import Address

def checkout_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'variant').all()

    if not cart_items:
        messages.warning(request, "Your cart is empty. Add products before proceeding to checkout.")
        return redirect('catalog:product_list')

    subtotal = cart.subtotal
    coupon_code = request.session.get('coupon_code', '')
    coupon = None
    discount = Decimal('0.00')

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid_now():
                discount = coupon.calculate_discount(subtotal)
        except Coupon.DoesNotExist:
            pass

    free_threshold = Decimal(str(getattr(settings, 'FREE_SHIPPING_THRESHOLD', 100.00)))
    flat_shipping = Decimal(str(getattr(settings, 'SHIPPING_FLAT_RATE', 15.00)))
    shipping = Decimal('0.00') if subtotal >= free_threshold else flat_shipping

    tax_rate = Decimal(str(getattr(settings, 'TAX_RATE_PERCENTAGE', 5.00))) / Decimal('100.00')
    taxable = max(Decimal('0.00'), subtotal - discount)
    tax = round(taxable * tax_rate, 2)
    grand_total = max(Decimal('0.00'), taxable + shipping)

    saved_addresses = []
    if request.user.is_authenticated:
        saved_addresses = request.user.addresses.all()

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            checkout_data = form.cleaned_data
            checkout_data['coupon_code'] = coupon_code

            # Server-side validation for card payment simulation
            if checkout_data['payment_method'] == PaymentMethod.CARD:
                card_num = checkout_data.get('card_number', '').replace(' ', '')
                if len(card_num) < 13:
                    form.add_error('card_number', 'Please provide a valid card number.')
                    return render(request, 'cart/checkout.html', {
                        'form': form, 'cart': cart, 'cart_items': cart_items,
                        'subtotal': subtotal, 'coupon': coupon, 'discount': discount,
                        'shipping': shipping, 'tax': tax, 'grand_total': grand_total,
                        'saved_addresses': saved_addresses
                    })

            try:
                order = process_order_checkout(
                    user=request.user,
                    cart=cart,
                    checkout_data=checkout_data
                )
                # Clear session coupon
                if 'coupon_code' in request.session:
                    del request.session['coupon_code']

                messages.success(request, f"Order #{order.order_number} confirmed! Thank you for your purchase.")
                return redirect('orders:order_confirmation', order_number=order.order_number)
            except ValidationError as e:
                messages.error(request, str(e.message if hasattr(e, 'message') else e))
            except Exception as e:
                messages.error(request, f"Unable to place order: {str(e)}")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['customer_name'] = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            initial_data['customer_email'] = request.user.email
            profile = getattr(request.user, 'profile', None)
            if profile:
                initial_data['customer_phone'] = profile.phone

            default_address = request.user.addresses.filter(is_default_shipping=True).first()
            if not default_address:
                default_address = request.user.addresses.first()

            if default_address:
                initial_data.update({
                    'customer_name': default_address.full_name,
                    'customer_phone': default_address.phone,
                    'shipping_street': default_address.street_address,
                    'shipping_apartment': default_address.apartment,
                    'shipping_city': default_address.city,
                    'shipping_state': default_address.state,
                    'shipping_postal_code': default_address.postal_code,
                    'shipping_country': default_address.country,
                })
        form = CheckoutForm(initial=initial_data)

    return render(request, 'cart/checkout.html', {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'coupon': coupon,
        'discount': discount,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
        'saved_addresses': saved_addresses,
    })


def order_confirmation_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def order_history_view(request):
    orders = request.user.orders.all().select_related('coupon').prefetch_related('items')
    return render(request, 'orders/order_history.html', {'orders': orders})


def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    # Permission check: customer owner or staff
    if not (request.user.is_authenticated and (order.user == request.user or (hasattr(request.user, 'profile') and request.user.profile.is_staff_member))):
        # Allow guest tracking with session or email
        guest_verified = request.session.get(f'track_{order_number}') == True
        if not guest_verified:
            messages.warning(request, "Please enter your email to verify order access.")
            return redirect(f"/orders/track/?order_number={order_number}")

    return render(request, 'orders/order_detail.html', {'order': order})


def track_order_view(request):
    order = None
    searched = False
    order_num = request.GET.get('order_number', '').strip()
    email = request.GET.get('email', '').strip()

    if order_num:
        searched = True
        try:
            if email:
                order = Order.objects.get(order_number=order_num, customer_email__iexact=email)
                request.session[f'track_{order_num}'] = True
            elif request.user.is_authenticated:
                order = Order.objects.get(order_number=order_num, user=request.user)
            else:
                messages.info(request, "Please provide the email address used during purchase.")
        except Order.DoesNotExist:
            order = None

    return render(request, 'orders/track_order.html', {
        'order': order,
        'searched': searched,
        'order_num': order_num,
        'email': email,
    })


@login_required
def order_cancel_customer_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Cancelled by customer')
        try:
            cancel_order_and_restore_stock(order, user=request.user, reason=reason)
            messages.success(request, f"Order #{order.order_number} has been cancelled and any payment refunded.")
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))

    return redirect('orders:order_detail', order_number=order.order_number)


def order_invoice_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    # Check permissions
    if not (request.user.is_authenticated and (order.user == request.user or (hasattr(request.user, 'profile') and request.user.profile.is_staff_member))):
        if not request.session.get(f'track_{order_number}'):
            messages.error(request, "Access denied.")
            return redirect('catalog:home')

    return render(request, 'orders/invoice.html', {'order': order})

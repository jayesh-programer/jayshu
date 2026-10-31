from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import datetime
import uuid

from django.conf import settings
from .models import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus, OrderStatusHistory, Shipment, Coupon
from inventory.services import record_stock_change
from inventory.models import TransactionType
from payments.models import Payment, Refund
from accounts.models import Notification, AuditLog

@transaction.atomic
def process_order_checkout(user, cart, checkout_data):
    """
    Atomically places an order from the user's cart:
    - Validates cart contents
    - Locks rows to prevent overselling
    - Validates and applies coupon if provided
    - Calculates tax, shipping, discounts
    - Deducts stock and records inventory transactions
    - Records payment and shipment
    - Clears cart
    """
    cart_items = list(cart.items.select_related('product', 'variant').all())
    if not cart_items:
        raise ValidationError("Your cart is empty.")

    # 1. Validate stock availability for all items
    for item in cart_items:
        available_stock = item.variant.stock if item.variant else item.product.stock
        if available_stock < item.quantity:
            item_name = f"{item.product.name}" + (f" ({item.variant})" if item.variant else "")
            raise ValidationError(f"Insufficient stock for '{item_name}'. Available: {available_stock}, in your cart: {item.quantity}.")

    # 2. Calculate subtotal
    subtotal = sum(item.line_total for item in cart_items)
    subtotal = Decimal(str(subtotal))

    # 3. Calculate coupon discount
    coupon_obj = None
    discount_amount = Decimal('0.00')
    coupon_code = checkout_data.get('coupon_code', '').strip().upper()
    if coupon_code:
        try:
            coupon = Coupon.objects.select_for_update().get(code=coupon_code)
            if coupon.is_valid_now():
                discount_amount = coupon.calculate_discount(subtotal)
                if discount_amount > 0:
                    coupon_obj = coupon
                    coupon.times_used += 1
                    coupon.save()
        except Coupon.DoesNotExist:
            pass

    # 4. Calculate shipping fee
    free_threshold = Decimal(str(getattr(settings, 'FREE_SHIPPING_THRESHOLD', 100.00)))
    flat_shipping = Decimal(str(getattr(settings, 'SHIPPING_FLAT_RATE', 15.00)))
    shipping_fee = Decimal('0.00') if subtotal >= free_threshold else flat_shipping

    # 5. Calculate tax
    tax_rate = Decimal(str(getattr(settings, 'TAX_RATE_PERCENTAGE', 5.00))) / Decimal('100.00')
    taxable_amount = max(Decimal('0.00'), subtotal - discount_amount)
    tax_amount = round(taxable_amount * tax_rate, 2)

    # 6. Final total
    final_total = max(Decimal('0.00'), subtotal - discount_amount + shipping_fee + tax_amount)

    # 7. Create Order
    order_number = Order.generate_order_number()
    payment_method = checkout_data.get('payment_method', PaymentMethod.COD)

    order = Order.objects.create(
        order_number=order_number,
        user=user if user.is_authenticated else None,
        customer_name=checkout_data['customer_name'],
        customer_email=checkout_data['customer_email'],
        customer_phone=checkout_data['customer_phone'],
        shipping_street=checkout_data['shipping_street'],
        shipping_apartment=checkout_data.get('shipping_apartment', ''),
        shipping_city=checkout_data['shipping_city'],
        shipping_state=checkout_data['shipping_state'],
        shipping_postal_code=checkout_data['shipping_postal_code'],
        shipping_country=checkout_data.get('shipping_country', 'United States'),
        coupon=coupon_obj,
        subtotal=subtotal,
        discount_amount=discount_amount,
        shipping_fee=shipping_fee,
        tax_amount=tax_amount,
        total=final_total,
        status=OrderStatus.CONFIRMED,
        payment_method=payment_method,
        payment_status=PaymentStatus.PENDING,
        notes=checkout_data.get('notes', '')
    )

    # 8. Create Order Items & atomically deduct inventory
    for item in cart_items:
        variant_desc = f"{item.variant.name}: {item.variant.value}" if item.variant else ""
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            variant_info=variant_desc,
            unit_price=item.unit_price,
            quantity=item.quantity,
            line_total=item.line_total
        )

        # Deduct stock and record inventory transaction
        record_stock_change(
            product_id=item.product_id,
            quantity=-item.quantity,
            change_type=TransactionType.SALE,
            variant_id=item.variant_id if item.variant else None,
            user=user if user.is_authenticated else None,
            note=f"Sold in Order #{order.order_number}"
        )

    # 9. Handle Payment
    if payment_method == PaymentMethod.CARD:
        # Process online simulated payment
        trans_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        Payment.objects.create(
            order=order,
            transaction_id=trans_id,
            payment_method='Online Credit/Debit Card',
            amount=final_total,
            status='success',
            gateway_response='Simulated Secure Gateway: Transaction approved (AuthCode: AUTH98234)'
        )
        order.payment_status = PaymentStatus.PAID
        order.save()
    elif payment_method == PaymentMethod.COD:
        # Cash on Delivery
        order.payment_status = PaymentStatus.PENDING
        order.save()

    # 10. Record Order Status History
    OrderStatusHistory.objects.create(
        order=order,
        status=OrderStatus.CONFIRMED,
        comment=f"Order placed successfully via {order.get_payment_method_display()}.",
        changed_by=user if user.is_authenticated else None
    )

    # 11. Create Shipment Record
    est_date = (timezone.now() + datetime.timedelta(days=4)).date()
    tracking_code = f"TRK-{uuid.uuid4().hex[:8].upper()}"
    Shipment.objects.create(
        order=order,
        carrier='FastTrack Express',
        tracking_number=tracking_code,
        status='preparing',
        estimated_delivery=est_date
    )

    # 12. Create Customer Notification
    if user.is_authenticated:
        Notification.objects.create(
            user=user,
            title=f"Order Confirmed: #{order.order_number}",
            message=f"Thank you for your order of ${final_total}! We have started processing your shipment.",
            link=f"/orders/{order.order_number}/"
        )

    # 13. Audit Log
    AuditLog.objects.create(
        user=user if user.is_authenticated else None,
        action='ORDER_CREATED',
        details=f"Order #{order.order_number} created for ${final_total}."
    )

    # 14. Clear Cart
    cart.items.all().delete()

    return order


@transaction.atomic
def cancel_order_and_restore_stock(order, user=None, reason=""):
    """
    Cancels an order and automatically restores stock for all purchased items.
    """
    if not order.can_be_cancelled:
        raise ValidationError(f"Order #{order.order_number} cannot be cancelled in its current state ({order.get_status_display()}).")

    # Restore stock for each item
    for item in order.items.all():
        if item.product:
            # Find matching variant if exists
            variant = None
            if item.variant_info:
                variant = item.product.variants.filter(is_active=True).first()

            record_stock_change(
                product_id=item.product.id,
                quantity=item.quantity,
                change_type=TransactionType.CANCELLATION,
                variant_id=variant.id if variant else None,
                user=user,
                note=f"Stock restored from cancelled Order #{order.order_number}"
            )

    order.status = OrderStatus.CANCELLED

    # If paid, process refund
    if order.payment_status == PaymentStatus.PAID:
        order.payment_status = PaymentStatus.REFUNDED
        Refund.objects.create(
            order=order,
            refund_id=f"RFD-{uuid.uuid4().hex[:8].upper()}",
            amount=order.total,
            reason=f"Order cancelled: {reason}" if reason else "Order cancellation",
            status='processed',
            created_by=user
        )

    order.save()

    # Log history
    OrderStatusHistory.objects.create(
        order=order,
        status=OrderStatus.CANCELLED,
        comment=f"Order cancelled. Reason: {reason or 'Customer/Staff request'}. Stock restored.",
        changed_by=user
    )

    if order.user:
        Notification.objects.create(
            user=order.user,
            title=f"Order Cancelled: #{order.order_number}",
            message=f"Your order #{order.order_number} has been cancelled. Any payments will be refunded.",
            link=f"/orders/{order.order_number}/"
        )

    return order


@transaction.atomic
def return_order_and_restore_stock(order, user=None, reason=""):
    """
    Processes a returned order and restores inventory.
    """
    if not order.can_be_returned:
        raise ValidationError(f"Order #{order.order_number} cannot be returned in its current status.")

    for item in order.items.all():
        if item.product:
            variant = None
            if item.variant_info:
                variant = item.product.variants.filter(is_active=True).first()

            record_stock_change(
                product_id=item.product.id,
                quantity=item.quantity,
                change_type=TransactionType.RETURN,
                variant_id=variant.id if variant else None,
                user=user,
                note=f"Stock restored from returned Order #{order.order_number}"
            )

    order.status = OrderStatus.RETURNED
    if order.payment_status == PaymentStatus.PAID:
        order.payment_status = PaymentStatus.REFUNDED
        Refund.objects.create(
            order=order,
            refund_id=f"RFD-{uuid.uuid4().hex[:8].upper()}",
            amount=order.total,
            reason=f"Order returned: {reason}" if reason else "Item returned by customer",
            status='processed',
            created_by=user
        )
    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        status=OrderStatus.RETURNED,
        comment=f"Order returned. Reason: {reason or 'Customer return'}. Stock restored.",
        changed_by=user
    )

    return order

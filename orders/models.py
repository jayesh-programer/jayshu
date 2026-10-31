from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid
from catalog.models import Product, ProductVariant

class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('percent', 'Percentage (%)'),
        ('fixed', 'Fixed Amount ($)'),
    )

    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='percent')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(default=100)
    times_used = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.discount_value}{'%' if self.discount_type == 'percent' else '$'} off)"

    def clean(self):
        self.code = self.code.upper().strip()

    def is_valid_now(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to and
            self.times_used < self.usage_limit
        )

    def calculate_discount(self, subtotal):
        if not self.is_valid_now():
            return Decimal('0.00')

        subtotal = Decimal(str(subtotal))
        if subtotal < self.min_order_value:
            return Decimal('0.00')

        if self.discount_type == 'percent':
            disc = (subtotal * Decimal(str(self.discount_value))) / Decimal('100.00')
            if self.max_discount_amount and disc > self.max_discount_amount:
                disc = self.max_discount_amount
        else:
            disc = min(Decimal(str(self.discount_value)), subtotal)

        return round(disc, 2)


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PROCESSING = 'processing', 'Processing'
    SHIPPED = 'shipped', 'Shipped'
    OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'
    RETURNED = 'returned', 'Returned'


class PaymentMethod(models.TextChoices):
    COD = 'cod', 'Cash on Delivery'
    CARD = 'card_simulated', 'Credit/Debit Card (Online Payment)'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PAID = 'paid', 'Paid'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'


class Order(models.Model):
    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    # Customer info
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)

    # Shipping Address snapshot
    shipping_street = models.CharField(max_length=255)
    shipping_apartment = models.CharField(max_length=100, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='United States')

    # Amounts
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Statuses
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING, db_index=True)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.COD)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, db_index=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name}"

    @property
    def shipping_address_formatted(self):
        parts = [self.shipping_street]
        if self.shipping_apartment:
            parts.append(self.shipping_apartment)
        parts.append(f"{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}")
        parts.append(self.shipping_country)
        return ", ".join(parts)

    @property
    def can_be_cancelled(self):
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]

    @property
    def can_be_returned(self):
        return self.status == OrderStatus.DELIVERED

    @classmethod
    def generate_order_number(cls):
        date_str = timezone.now().strftime('%Y%m%d')
        random_suffix = uuid.uuid4().hex[:6].upper()
        return f"ORD-{date_str}-{random_suffix}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    variant_info = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} ({self.order.order_number})"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=30)
    comment = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Order #{self.order.order_number} changed to {self.status}"


class Shipment(models.Model):
    SHIPMENT_STATUS = (
        ('preparing', 'Preparing for Shipment'),
        ('dispatched', 'Dispatched'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    carrier = models.CharField(max_length=100, default='FastTrack Express')
    tracking_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, choices=SHIPMENT_STATUS, default='preparing')
    estimated_delivery = models.DateField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Shipment for {self.order.order_number} ({self.get_status_display()})"

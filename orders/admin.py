from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, Shipment, Coupon

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'variant_info', 'unit_price', 'quantity', 'line_total')

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status', 'comment', 'changed_by', 'created_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'total', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method')
    search_fields = ('order_number', 'customer_name', 'customer_email')
    inlines = [OrderItemInline, OrderStatusHistoryInline]

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_order_value', 'times_used', 'usage_limit', 'is_active', 'valid_to')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'carrier', 'tracking_number', 'status', 'estimated_delivery')
    list_filter = ('status', 'carrier')

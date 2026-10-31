from django.contrib import admin
from .models import Payment, Refund

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('transaction_id', 'order__order_number')

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('refund_id', 'order', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('refund_id', 'order__order_number')

from django.contrib import admin
from .models import InventoryTransaction

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'product', 'variant', 'change_type', 'quantity', 'previous_stock', 'new_stock', 'created_by')
    list_filter = ('change_type', 'created_at')
    search_fields = ('product__name', 'product__sku', 'note')
    readonly_fields = ('created_at',)

from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product, ProductVariant

class TransactionType(models.TextChoices):
    RESTOCK = 'restock', 'Restock / Purchase'
    SALE = 'sale', 'Customer Sale'
    ADJUSTMENT = 'adjustment', 'Manual Adjustment'
    RETURN = 'return', 'Order Return'
    CANCELLATION = 'cancellation', 'Order Cancellation'

class InventoryTransaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_transactions')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True, related_name='inventory_transactions')
    change_type = models.CharField(max_length=20, choices=TransactionType.choices)
    quantity = models.IntegerField(help_text="Positive for addition, negative for deduction")
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = f"{self.product.name}"
        if self.variant:
            target += f" ({self.variant.name}: {self.variant.value})"
        return f"{self.get_change_type_display()}: {self.quantity:+d} for {target}"

from django.db import transaction
from django.core.exceptions import ValidationError
from .models import InventoryTransaction, TransactionType
from catalog.models import Product, ProductVariant

@transaction.atomic
def record_stock_change(product_id, quantity, change_type, variant_id=None, user=None, note=""):
    """
    Safely and atomically adjust stock for a product (or variant) and record the transaction.
    Uses select_for_update to lock rows and prevent race conditions.
    """
    product = Product.objects.select_for_update().get(id=product_id)
    variant = None
    if variant_id:
        variant = ProductVariant.objects.select_for_update().get(id=variant_id, product=product)

    target_obj = variant if variant else product
    prev_stock = target_obj.stock
    new_stock = prev_stock + quantity

    if new_stock < 0:
        raise ValidationError(f"Insufficient stock for {target_obj}. Available: {prev_stock}, requested reduction: {abs(quantity)}")

    target_obj.stock = new_stock
    target_obj.save()

    # If variant stock changed, also update parent product's aggregate stock if appropriate
    if variant:
        # Sum of all variants
        total_var_stock = sum(v.stock for v in product.variants.all())
        product.stock = total_var_stock
        product.save()

    tx = InventoryTransaction.objects.create(
        product=product,
        variant=variant,
        change_type=change_type,
        quantity=quantity,
        previous_stock=prev_stock,
        new_stock=new_stock,
        note=note,
        created_by=user
    )
    return tx

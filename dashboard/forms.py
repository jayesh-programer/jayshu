from django import forms
from catalog.models import Product, ProductVariant, ProductImage, Category
from orders.models import Coupon, OrderStatus, PaymentStatus
from accounts.models import Profile, Role, SupportTicket

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'category', 'sku', 'short_description', 'description',
            'price', 'discount_price', 'stock', 'low_stock_threshold',
            'is_active', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'auto-generated-if-blank'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. PRD-1001'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief 1-liner summary'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Full product specifications & details'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Optional discount price'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discount_price = cleaned_data.get('discount_price')
        stock = cleaned_data.get('stock')

        if price is not None and price <= 0:
            self.add_error('price', "Price must be greater than zero.")

        if discount_price is not None and discount_price >= price:
            self.add_error('discount_price', "Discount price must be less than the regular price.")

        if stock is not None and stock < 0:
            self.add_error('stock', "Stock quantity cannot be negative.")

        return cleaned_data


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'value', 'sku', 'additional_price', 'stock', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Size, Color'}),
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Medium, Black'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Variant SKU'}),
            'additional_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductImageUploadForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image description'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'auto-generated'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CouponAdminForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            'code', 'discount_type', 'discount_value', 'min_order_value',
            'max_discount_amount', 'usage_limit', 'valid_from', 'valid_to', 'is_active'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SUMMER25'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_order_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'valid_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StockAdjustmentForm(forms.Form):
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +50 or -10'}),
        help_text="Enter positive number to add stock, negative to deduct."
    )
    change_type = forms.ChoiceField(
        choices=[
            ('restock', 'Restock / Purchase order'),
            ('adjustment', 'Physical count adjustment'),
            ('return', 'Customer return'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    note = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reason or PO reference number'}),
        max_length=200
    )


class OrderStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=OrderStatus.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    payment_status = forms.ChoiceField(choices=PaymentStatus.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    tracking_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tracking #' }))
    carrier = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Carrier name'}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Internal note on status change'}))


class StaffRoleForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
        }


class SupportTicketReplyForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['status', 'admin_response']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_response': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write reply to customer...'}),
        }

from django import forms
from .models import PaymentMethod

class CheckoutForm(forms.Form):
    customer_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}))
    customer_email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    customer_phone = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))

    shipping_street = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address'}))
    shipping_apartment = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apt, Suite, Unit (optional)'}))
    shipping_city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}))
    shipping_state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State / Province'}))
    shipping_postal_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP / Postal Code'}))
    shipping_country = forms.CharField(initial='United States', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}))

    payment_method = forms.ChoiceField(
        choices=PaymentMethod.choices,
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
        initial=PaymentMethod.COD
    )
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Special delivery notes (optional)'}))

    # Credit card simulation fields
    card_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '•••• •••• •••• ••••', 'maxlength': '19'}))
    card_expiry = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY', 'maxlength': '5'}))
    card_cvv = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVV', 'maxlength': '4'}))

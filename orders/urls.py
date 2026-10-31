from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('confirmation/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    path('history/', views.order_history_view, name='history'),
    path('track/', views.track_order_view, name='track'),
    path('<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('<str:order_number>/cancel/', views.order_cancel_customer_view, name='order_cancel'),
    path('<str:order_number>/invoice/', views.order_invoice_view, name='invoice'),
]

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('products/image/<int:pk>/delete/', views.product_image_delete, name='product_image_delete'),
    path('products/variant/<int:pk>/delete/', views.product_variant_delete, name='product_variant_delete'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Orders & Payments
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('transactions/', views.payment_transactions_list, name='payment_transactions'),

    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/<int:pk>/adjust/', views.inventory_adjust, name='inventory_adjust'),
    path('inventory/history/', views.inventory_history, name='inventory_history'),

    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/suspend/', views.customer_toggle_suspend, name='customer_toggle_suspend'),

    # Support Tickets
    path('support/', views.support_tickets_list, name='support_tickets'),
    path('support/<int:pk>/reply/', views.support_ticket_reply, name='support_ticket_reply'),

    # Coupons
    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/create/', views.coupon_create, name='coupon_create'),
    path('coupons/<int:pk>/edit/', views.coupon_edit, name='coupon_edit'),
    path('coupons/<int:pk>/toggle/', views.coupon_toggle, name='coupon_toggle'),

    # Staff
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/<int:pk>/edit/', views.staff_edit, name='staff_edit'),
]

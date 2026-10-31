from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/', views.add_to_cart_view, name='add_to_cart'),
    path('update/<int:item_id>/', views.update_cart_item_view, name='update_cart_item'),
    path('remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('coupon/apply/', views.apply_coupon_view, name='apply_coupon'),
    path('coupon/remove/', views.remove_coupon_view, name='remove_coupon'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist_view, name='toggle_wishlist'),
]

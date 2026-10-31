from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('products/', views.product_list_view, name='product_list'),
    path('products/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/<slug:slug>/', views.product_list_view, name='category_detail'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy-policy/', views.privacy_view, name='privacy'),
    path('terms-and-conditions/', views.terms_view, name='terms'),
    path('shipping-returns/', views.shipping_returns_view, name='shipping_returns'),
]

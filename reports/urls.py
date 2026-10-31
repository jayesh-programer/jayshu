from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_index, name='index'),
    path('export/orders/', views.export_orders_csv, name='export_orders'),
    path('export/products/', views.export_products_csv, name='export_products'),
]

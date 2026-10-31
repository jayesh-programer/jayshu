import csv
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, F, Q
from decimal import Decimal
import datetime

from accounts.decorators import role_required
from accounts.models import Role, User
from orders.models import Order, OrderItem, OrderStatus, PaymentStatus
from catalog.models import Product
from payments.models import Refund, Payment

@role_required(Role.SUPERADMIN, Role.MANAGER)
def reports_index(request):
    now = timezone.now()
    today = now.date()

    # Time boundaries
    start_of_today = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
    start_of_week = start_of_today - datetime.timedelta(days=today.weekday())
    start_of_month = timezone.make_aware(datetime.datetime(today.year, today.month, 1))
    start_of_year = timezone.make_aware(datetime.datetime(today.year, 1, 1))

    # Sales calculations
    daily_sales = Order.objects.filter(created_at__gte=start_of_today, payment_status=PaymentStatus.PAID).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    weekly_sales = Order.objects.filter(created_at__gte=start_of_week, payment_status=PaymentStatus.PAID).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    monthly_sales = Order.objects.filter(created_at__gte=start_of_month, payment_status=PaymentStatus.PAID).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    yearly_sales = Order.objects.filter(created_at__gte=start_of_year, payment_status=PaymentStatus.PAID).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')

    # Orders count
    total_orders = Order.objects.count()
    cancelled_orders_count = Order.objects.filter(status=OrderStatus.CANCELLED).count()
    returned_orders_count = Order.objects.filter(status=OrderStatus.RETURNED).count()

    # Refunds
    total_refunds = Refund.objects.filter(status='processed').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    refund_count = Refund.objects.count()

    # Best-selling products (top 10)
    best_sellers = OrderItem.objects.values('product__name', 'product__sku') \
        .filter(product__isnull=False) \
        .annotate(units_sold=Sum('quantity'), total_revenue=Sum('line_total')) \
        .order_by('-units_sold')[:10]

    # Low-stock products
    low_stock_products = Product.objects.filter(stock__lte=F('low_stock_threshold')).order_by('stock')

    # Payment methods breakdown
    payment_method_stats = Order.objects.values('payment_method').annotate(
        count=Count('id'),
        total_amount=Sum('total')
    ).order_by('-count')

    # Customer growth (last 6 months)
    customer_growth = []
    for i in range(5, -1, -1):
        m_date = today - datetime.timedelta(days=i * 30)
        c_count = User.objects.filter(
            profile__role=Role.CUSTOMER,
            date_joined__year=m_date.year,
            date_joined__month=m_date.month
        ).count()
        customer_growth.append({
            'label': m_date.strftime('%b %Y'),
            'count': c_count
        })

    return render(request, 'dashboard/reports/index.html', {
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'yearly_sales': yearly_sales,
        'total_orders': total_orders,
        'cancelled_orders_count': cancelled_orders_count,
        'returned_orders_count': returned_orders_count,
        'total_refunds': total_refunds,
        'refund_count': refund_count,
        'best_sellers': best_sellers,
        'low_stock_products': low_stock_products,
        'payment_method_stats': payment_method_stats,
        'customer_growth': customer_growth,
    })


@role_required(Role.SUPERADMIN, Role.MANAGER)
def export_orders_csv(request):
    """Exports orders list to CSV with customer, items, and revenue details."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="orders_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Order Number', 'Date', 'Customer Name', 'Email', 'Status',
        'Payment Method', 'Payment Status', 'Subtotal', 'Discount', 'Shipping', 'Tax', 'Total'
    ])

    orders = Order.objects.all().order_by('-created_at')
    for o in orders:
        writer.writerow([
            o.order_number,
            o.created_at.strftime('%Y-%m-%d %H:%M'),
            o.customer_name,
            o.customer_email,
            o.get_status_display(),
            o.get_payment_method_display(),
            o.get_payment_status_display(),
            o.subtotal,
            o.discount_amount,
            o.shipping_fee,
            o.tax_amount,
            o.total
        ])

    return response


@role_required(Role.SUPERADMIN, Role.MANAGER)
def export_products_csv(request):
    """Exports product catalog and inventory levels to CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="inventory_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'SKU', 'Product Name', 'Category', 'Price', 'Discount Price',
        'Stock Available', 'Low Stock Threshold', 'Stock Status', 'Active'
    ])

    products = Product.objects.all().select_related('category')
    for p in products:
        if p.stock <= 0:
            st = 'Out of Stock'
        elif p.stock <= p.low_stock_threshold:
            st = 'Low Stock'
        else:
            st = 'In Stock'

        writer.writerow([
            p.sku,
            p.name,
            p.category.name if p.category else 'None',
            p.price,
            p.discount_price or '',
            p.stock,
            p.low_stock_threshold,
            st,
            'Yes' if p.is_active else 'No'
        ])

    return response

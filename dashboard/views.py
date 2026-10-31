from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from decimal import Decimal
import datetime

from accounts.decorators import role_required, admin_or_staff_required
from accounts.models import Profile, Role, SupportTicket, AuditLog
from catalog.models import Product, ProductVariant, ProductImage, Category
from orders.models import Order, OrderItem, OrderStatus, PaymentStatus, OrderStatusHistory, Coupon, Shipment
from payments.models import Payment, Refund
from inventory.models import InventoryTransaction, TransactionType
from inventory.services import record_stock_change
from orders.services import cancel_order_and_restore_stock, return_order_and_restore_stock
from .forms import (
    ProductAdminForm, ProductVariantForm, ProductImageUploadForm, CategoryAdminForm,
    CouponAdminForm, StockAdjustmentForm, OrderStatusUpdateForm, StaffRoleForm, SupportTicketReplyForm
)

@admin_or_staff_required
def dashboard_index(request):
    # Total sales (paid orders)
    paid_sales = Order.objects.filter(payment_status=PaymentStatus.PAID).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_customers = User.objects.filter(profile__role=Role.CUSTOMER).count()

    pending_orders = Order.objects.filter(status=OrderStatus.PENDING).count()
    delivered_orders = Order.objects.filter(status=OrderStatus.DELIVERED).count()
    low_stock_count = Product.objects.filter(stock__lte=F('low_stock_threshold'), stock__gt=0).count()
    out_of_stock_count = Product.objects.filter(stock__lte=0).count()

    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:8]

    # Recent transactions
    recent_payments = Payment.objects.select_related('order').order_by('-created_at')[:6]

    # Best-selling products
    best_sellers = OrderItem.objects.values('product__id', 'product__name', 'product__price') \
        .filter(product__isnull=False) \
        .annotate(total_sold=Sum('quantity'), total_revenue=Sum('line_total')) \
        .order_by('-total_sold')[:5]

    # Monthly sales calculation for the current calendar year (real DB data)
    now = timezone.now()
    monthly_data = []
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for m in range(1, 13):
        m_sales = Order.objects.filter(
            created_at__year=now.year,
            created_at__month=m,
            payment_status=PaymentStatus.PAID
        ).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        monthly_data.append({
            'month': month_names[m - 1],
            'sales': float(m_sales)
        })

    # Low stock items list for quick action
    low_stock_products = Product.objects.filter(stock__lte=F('low_stock_threshold')).order_by('stock')[:6]

    return render(request, 'dashboard/index.html', {
        'total_sales': paid_sales,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_customers': total_customers,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'recent_orders': recent_orders,
        'recent_payments': recent_payments,
        'best_sellers': best_sellers,
        'monthly_data': monthly_data,
        'low_stock_products': low_stock_products,
        'current_year': now.year,
    })


# ---------------- Product Management ----------------
@role_required(Role.SUPERADMIN, Role.MANAGER, Role.INVENTORY_STAFF)
def product_list(request):
    products = Product.objects.all().select_related('category').prefetch_related('images')
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    stock_status = request.GET.get('stock_status', '').strip()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)
    if stock_status == 'low':
        products = products.filter(stock__lte=F('low_stock_threshold'), stock__gt=0)
    elif stock_status == 'out':
        products = products.filter(stock__lte=0)
    elif stock_status == 'in':
        products = products.filter(stock__gt=F('low_stock_threshold'))

    paginator = Paginator(products, 15)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    categories = Category.objects.filter(is_active=True)

    return render(request, 'dashboard/products/list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'stock_status': stock_status,
    })


@role_required(Role.SUPERADMIN, Role.MANAGER, Role.INVENTORY_STAFF)
def product_create(request):
    if request.method == 'POST':
        form = ProductAdminForm(request.POST)
        image_form = ProductImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()

            if request.FILES.get('image'):
                ProductImage.objects.create(
                    product=product,
                    image=request.FILES['image'],
                    alt_text=product.name,
                    is_primary=True
                )

            # Record initial inventory transaction if stock > 0
            if product.stock > 0:
                InventoryTransaction.objects.create(
                    product=product,
                    change_type=TransactionType.RESTOCK,
                    quantity=product.stock,
                    previous_stock=0,
                    new_stock=product.stock,
                    note='Initial product creation',
                    created_by=request.user
                )

            AuditLog.objects.create(
                user=request.user,
                action='PRODUCT_CREATED',
                details=f"Created product: {product.name} ({product.sku})"
            )

            messages.success(request, f"Product '{product.name}' created successfully.")
            return redirect('dashboard:product_edit', pk=product.pk)
    else:
        form = ProductAdminForm()
        image_form = ProductImageUploadForm()

    return render(request, 'dashboard/products/form.html', {
        'form': form,
        'image_form': image_form,
        'action': 'Add'
    })


@role_required(Role.SUPERADMIN, Role.MANAGER, Role.INVENTORY_STAFF)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, instance=product)
        image_form = ProductImageUploadForm(request.POST, request.FILES)
        variant_form = ProductVariantForm(request.POST)

        if 'update_product' in request.POST and form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('dashboard:product_edit', pk=product.pk)

        elif 'add_image' in request.POST and image_form.is_valid():
            img = image_form.save(commit=False)
            img.product = product
            img.save()
            messages.success(request, "Image uploaded.")
            return redirect('dashboard:product_edit', pk=product.pk)

        elif 'add_variant' in request.POST and variant_form.is_valid():
            var = variant_form.save(commit=False)
            var.product = product
            var.save()
            messages.success(request, f"Variant '{var.name}: {var.value}' added.")
            return redirect('dashboard:product_edit', pk=product.pk)
    else:
        form = ProductAdminForm(instance=product)
        image_form = ProductImageUploadForm()
        variant_form = ProductVariantForm()

    images = product.images.all()
    variants = product.variants.all()

    return render(request, 'dashboard/products/form.html', {
        'form': form,
        'image_form': image_form,
        'variant_form': variant_form,
        'product': product,
        'images': images,
        'variants': variants,
        'action': 'Edit'
    })


@role_required(Role.SUPERADMIN, Role.MANAGER)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.is_active = False
        product.save()
        AuditLog.objects.create(
            user=request.user,
            action='PRODUCT_DEACTIVATED',
            details=f"Deactivated product: {name}"
        )
        messages.success(request, f"Product '{name}' has been deactivated.")
    return redirect('dashboard:product_list')


@role_required(Role.SUPERADMIN, Role.MANAGER)
def product_image_delete(request, pk):
    image = get_object_or_404(ProductImage, pk=pk)
    product_pk = image.product.pk
    image.delete()
    messages.info(request, "Image deleted.")
    return redirect('dashboard:product_edit', pk=product_pk)


@role_required(Role.SUPERADMIN, Role.MANAGER)
def product_variant_delete(request, pk):
    variant = get_object_or_404(ProductVariant, pk=pk)
    product_pk = variant.product.pk
    variant.delete()
    messages.info(request, "Variant deleted.")
    return redirect('dashboard:product_edit', pk=product_pk)


# ---------------- Category Management ----------------
@role_required(Role.SUPERADMIN, Role.MANAGER)
def category_list(request):
    categories = Category.objects.all().prefetch_related('subcategories')
    return render(request, 'dashboard/categories/list.html', {'categories': categories})


@role_required(Role.SUPERADMIN, Role.MANAGER)
def category_create(request):
    if request.method == 'POST':
        form = CategoryAdminForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' created.")
            return redirect('dashboard:category_list')
    else:
        form = CategoryAdminForm()

    return render(request, 'dashboard/categories/form.html', {'form': form, 'action': 'Add'})


@role_required(Role.SUPERADMIN, Role.MANAGER)
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryAdminForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f"Category '{category.name}' updated.")
            return redirect('dashboard:category_list')
    else:
        form = CategoryAdminForm(instance=category)

    return render(request, 'dashboard/categories/form.html', {'form': form, 'category': category, 'action': 'Edit'})


@role_required(Role.SUPERADMIN, Role.MANAGER)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted.")
    return redirect('dashboard:category_list')


# ---------------- Order Management ----------------
@role_required(Role.SUPERADMIN, Role.MANAGER, Role.ORDER_STAFF)
def order_list(request):
    orders = Order.objects.all().select_related('user', 'coupon')
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    payment_status = request.GET.get('payment_status', '').strip()

    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(customer_email__icontains=query)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)
    if payment_status:
        orders = orders.filter(payment_status=payment_status)

    paginator = Paginator(orders, 15)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'dashboard/orders/list.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'payment_status': payment_status,
        'order_statuses': OrderStatus.choices,
        'payment_statuses': PaymentStatus.choices,
    })


@role_required(Role.SUPERADMIN, Role.MANAGER, Role.ORDER_STAFF)
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related('shipment', 'coupon'), pk=pk)
    items = order.items.select_related('product').all()
    history = order.status_history.select_related('changed_by').all()
    payments = order.payments.all()
    refunds = order.refunds.all()

    if request.method == 'POST':
        status_form = OrderStatusUpdateForm(request.POST)
        if status_form.is_valid():
            new_status = status_form.cleaned_data['status']
            new_payment_status = status_form.cleaned_data['payment_status']
            tracking = status_form.cleaned_data['tracking_number']
            carrier = status_form.cleaned_data['carrier']
            comment = status_form.cleaned_data['comment']

            old_status = order.status

            # Handle cancellation with stock restoration
            if new_status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
                cancel_order_and_restore_stock(order, user=request.user, reason=comment)
            elif new_status == OrderStatus.RETURNED and old_status != OrderStatus.RETURNED:
                return_order_and_restore_stock(order, user=request.user, reason=comment)
            else:
                order.status = new_status
                order.payment_status = new_payment_status
                order.save()

                # Status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status=new_status,
                    comment=comment or f"Status changed to {new_status} by staff.",
                    changed_by=request.user
                )

            # Update shipment if provided
            if hasattr(order, 'shipment'):
                shipment = order.shipment
                if tracking:
                    shipment.tracking_number = tracking
                if carrier:
                    shipment.carrier = carrier
                if new_status == OrderStatus.SHIPPED:
                    shipment.status = 'in_transit'
                    shipment.shipped_at = timezone.now()
                elif new_status == OrderStatus.DELIVERED:
                    shipment.status = 'delivered'
                    shipment.delivered_at = timezone.now()
                shipment.save()

            messages.success(request, f"Order #{order.order_number} updated.")
            return redirect('dashboard:order_detail', pk=order.pk)
    else:
        initial = {
            'status': order.status,
            'payment_status': order.payment_status,
        }
        if hasattr(order, 'shipment'):
            initial['tracking_number'] = order.shipment.tracking_number
            initial['carrier'] = order.shipment.carrier
        status_form = OrderStatusUpdateForm(initial=initial)

    return render(request, 'dashboard/orders/detail.html', {
        'order': order,
        'items': items,
        'history': history,
        'payments': payments,
        'refunds': refunds,
        'status_form': status_form,
    })


# ---------------- Inventory Management ----------------
@role_required(Role.SUPERADMIN, Role.MANAGER, Role.INVENTORY_STAFF)
def inventory_list(request):
    products = Product.objects.all().select_related('category').prefetch_related('variants')
    filter_type = request.GET.get('filter', 'all')
    query = request.GET.get('q', '').strip()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(sku__icontains=query))

    if filter_type == 'low':
        products = products.filter(stock__lte=F('low_stock_threshold'), stock__gt=0)
    elif filter_type == 'out':
        products = products.filter(stock__lte=0)

    paginator = Paginator(products, 15)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    adjust_form = StockAdjustmentForm()

    return render(request, 'dashboard/inventory/list.html', {
        'page_obj': page_obj,
        'filter_type': filter_type,
        'query': query,
        'adjust_form': adjust_form,
    })


@role_required(Role.SUPERADMIN, Role.MANAGER, Role.INVENTORY_STAFF)
def inventory_adjust(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity']
            change_type = form.cleaned_data['change_type']
            note = form.cleaned_data['note']
            variant_id = request.POST.get('variant_id') or None

            try:
                record_stock_change(
                    product_id=product.id,
                    quantity=qty,
                    change_type=change_type,
                    variant_id=variant_id,
                    user=request.user,
                    note=note
                )
                messages.success(request, f"Stock adjusted for {product.name} ({qty:+d} units).")
            except Exception as e:
                messages.error(request, f"Failed to adjust stock: {str(e)}")

    return redirect('dashboard:inventory_list')


@role_required(Role.SUPERADMIN, Role.MANAGER, Role.INVENTORY_STAFF)
def inventory_history(request):
    transactions = InventoryTransaction.objects.all().select_related('product', 'variant', 'created_by')
    paginator = Paginator(transactions, 25)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'dashboard/inventory/history.html', {'page_obj': page_obj})


# ---------------- Customer Management ----------------
@role_required(Role.SUPERADMIN, Role.MANAGER, Role.SUPPORT_STAFF)
def customer_list(request):
    customers = User.objects.filter(profile__role=Role.CUSTOMER).select_related('profile').prefetch_related('orders')
    query = request.GET.get('q', '').strip()

    if query:
        customers = customers.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(profile__phone__icontains=query)
        )

    paginator = Paginator(customers, 15)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'dashboard/customers/list.html', {
        'page_obj': page_obj,
        'query': query,
    })


@role_required(Role.SUPERADMIN, Role.MANAGER, Role.SUPPORT_STAFF)
def customer_detail(request, pk):
    customer = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    orders = customer.orders.all()
    total_spent = orders.filter(payment_status=PaymentStatus.PAID).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    tickets = customer.support_tickets.all()
    addresses = customer.addresses.all()

    return render(request, 'dashboard/customers/detail.html', {
        'customer': customer,
        'orders': orders,
        'total_spent': total_spent,
        'tickets': tickets,
        'addresses': addresses,
    })


@role_required(Role.SUPERADMIN, Role.MANAGER)
def customer_toggle_suspend(request, pk):
    customer = get_object_or_404(User, pk=pk)
    profile = customer.profile
    profile.is_suspended = not profile.is_suspended
    profile.save()

    action = "suspended" if profile.is_suspended else "reactivated"
    AuditLog.objects.create(
        user=request.user,
        action=f"USER_{action.upper()}",
        details=f"Staff {request.user.username} {action} customer {customer.username}."
    )
    messages.info(request, f"Customer account {customer.username} has been {action}.")
    return redirect('dashboard:customer_detail', pk=customer.pk)


# ---------------- Support Ticket Management ----------------
@role_required(Role.SUPERADMIN, Role.MANAGER, Role.SUPPORT_STAFF)
def support_tickets_list(request):
    tickets = SupportTicket.objects.all().select_related('user', 'assigned_to')
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    paginator = Paginator(tickets, 15)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'dashboard/support/list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
    })


@role_required(Role.SUPERADMIN, Role.MANAGER, Role.SUPPORT_STAFF)
def support_ticket_reply(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk)
    if request.method == 'POST':
        form = SupportTicketReplyForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.assigned_to = request.user
            ticket.save()
            messages.success(request, f"Reply saved for ticket #{ticket.id}.")
            return redirect('dashboard:support_tickets')
    else:
        form = SupportTicketReplyForm(instance=ticket)

    return render(request, 'dashboard/support/reply.html', {'ticket': ticket, 'form': form})


# ---------------- Coupon Management ----------------
@role_required(Role.SUPERADMIN, Role.MANAGER)
def coupon_list(request):
    coupons = Coupon.objects.all()
    return render(request, 'dashboard/coupons/list.html', {'coupons': coupons})


@role_required(Role.SUPERADMIN, Role.MANAGER)
def coupon_create(request):
    if request.method == 'POST':
        form = CouponAdminForm(request.POST)
        if form.is_valid():
            coupon = form.save()
            messages.success(request, f"Coupon '{coupon.code}' created.")
            return redirect('dashboard:coupon_list')
    else:
        form = CouponAdminForm()

    return render(request, 'dashboard/coupons/form.html', {'form': form, 'action': 'Add'})


@role_required(Role.SUPERADMIN, Role.MANAGER)
def coupon_edit(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        form = CouponAdminForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, f"Coupon '{coupon.code}' updated.")
            return redirect('dashboard:coupon_list')
    else:
        form = CouponAdminForm(instance=coupon)

    return render(request, 'dashboard/coupons/form.html', {'form': form, 'coupon': coupon, 'action': 'Edit'})


@role_required(Role.SUPERADMIN, Role.MANAGER)
def coupon_toggle(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    coupon.is_active = not coupon.is_active
    coupon.save()
    status_str = "activated" if coupon.is_active else "deactivated"
    messages.info(request, f"Coupon '{coupon.code}' {status_str}.")
    return redirect('dashboard:coupon_list')


# ---------------- Staff Roles Management ----------------
@role_required(Role.SUPERADMIN)
def staff_list(request):
    staff_members = User.objects.exclude(profile__role=Role.CUSTOMER).select_related('profile')
    return render(request, 'dashboard/staff/list.html', {'staff_members': staff_members})


@role_required(Role.SUPERADMIN)
def staff_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = StaffRoleForm(request.POST, instance=user.profile)
        if form.is_valid():
            form.save()
            AuditLog.objects.create(
                user=request.user,
                action='STAFF_ROLE_CHANGE',
                details=f"Changed role of {user.username} to {user.profile.role}"
            )
            messages.success(request, f"Role updated for {user.username}.")
            return redirect('dashboard:staff_list')
    else:
        form = StaffRoleForm(instance=user.profile)

    return render(request, 'dashboard/staff/form.html', {'staff_user': user, 'form': form})


# ---------------- Payment Transactions Management ----------------
@role_required(Role.SUPERADMIN, Role.MANAGER, Role.ORDER_STAFF)
def payment_transactions_list(request):
    payments = Payment.objects.all().select_related('order')
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if query:
        payments = payments.filter(
            Q(transaction_id__icontains=query) |
            Q(order__order_number__icontains=query) |
            Q(order__customer_name__icontains=query)
        )
    if status_filter:
        payments = payments.filter(status=status_filter)

    paginator = Paginator(payments, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    refunds = Refund.objects.all().select_related('order', 'created_by')[:10]

    return render(request, 'dashboard/payments/list.html', {
        'page_obj': page_obj,
        'refunds': refunds,
        'query': query,
        'status_filter': status_filter,
    })

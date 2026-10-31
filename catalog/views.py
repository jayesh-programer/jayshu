from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Avg
from .models import Category, Product, Review
from .forms import ReviewForm
from accounts.models import SupportTicket

def home_view(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True).prefetch_related('images', 'variants')[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at').prefetch_related('images')[:8]
    categories = Category.objects.filter(parent__isnull=True, is_active=True)[:6]

    return render(request, 'storefront/home.html', {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
    })


def product_list_view(request, slug=None):
    products = Product.objects.filter(is_active=True).prefetch_related('images', 'category')

    query = request.GET.get('q', '').strip()
    category_slug = slug or request.GET.get('category', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    in_stock_only = request.GET.get('in_stock', '').strip()
    sort = request.GET.get('sort', 'newest').strip()

    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        sub_ids = list(current_category.subcategories.values_list('id', flat=True))
        all_ids = [current_category.id] + sub_ids
        products = products.filter(category_id__in=all_ids)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query) |
            Q(category__name__icontains=query)
        )

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    if in_stock_only == '1':
        products = products.filter(stock__gt=0)

    # Sorting
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating', '-created_at')
    else:  # 'newest'
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    all_categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories')

    return render(request, 'storefront/product_list.html', {
        'page_obj': page_obj,
        'current_category': current_category,
        'categories': all_categories,
        'query': query,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'in_stock_only': in_stock_only,
        'total_count': paginator.count,
    })


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    images = product.images.all()
    variants = product.variants.filter(is_active=True)
    reviews = product.reviews.filter(is_approved=True).select_related('user')
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]

    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = product.reviews.filter(user=request.user).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to submit a review.")
            return redirect(f"/accounts/login/?next={product.get_absolute_url()}")

        if user_has_reviewed:
            messages.warning(request, "You have already reviewed this product.")
            return redirect(product.get_absolute_url())

        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thank you! Your product review has been submitted.")
            return redirect(product.get_absolute_url())
    else:
        review_form = ReviewForm()

    return render(request, 'storefront/product_detail.html', {
        'product': product,
        'images': images,
        'variants': variants,
        'reviews': reviews,
        'related_products': related_products,
        'review_form': review_form,
        'user_has_reviewed': user_has_reviewed,
    })


def category_list_view(request):
    categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories')
    return render(request, 'storefront/category_list.html', {'categories': categories})


# Informational Pages
def about_view(request):
    return render(request, 'storefront/about.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if request.user.is_authenticated:
            SupportTicket.objects.create(
                user=request.user,
                subject=f"Contact Form: {subject}",
                message=f"From: {name} ({email})\n\n{message}",
                priority='medium'
            )
        messages.success(request, f"Thank you, {name}! Your message has been received. Our team will contact you at {email}.")
        return redirect('catalog:contact')

    return render(request, 'storefront/contact.html')


def privacy_view(request):
    return render(request, 'storefront/privacy.html')


def terms_view(request):
    return render(request, 'storefront/terms.html')


def shipping_returns_view(request):
    return render(request, 'storefront/shipping_returns.html')

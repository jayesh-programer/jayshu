from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import UserRegistrationForm, UserLoginForm, UserProfileUpdateForm, AddressForm, SupportTicketForm
from .models import Profile, Address, SupportTicket, Notification, AuditLog

def register_view(request):
    if request.user.is_authenticated:
        return redirect('catalog:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Profile is auto-created by signal, update phone
            phone = form.cleaned_data.get('phone', '')
            if phone:
                user.profile.phone = phone
                user.profile.save()

            AuditLog.objects.create(
                user=user,
                action='USER_REGISTRATION',
                details=f"User {user.username} registered an account.",
                ip_address=request.META.get('REMOTE_ADDR')
            )

            # Auto login
            login(request, user)
            messages.success(request, f"Welcome to the store, {user.first_name or user.username}! Your account has been created.")
            return redirect('catalog:home')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('catalog:home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'catalog:home'

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if suspended
            if hasattr(user, 'profile') and user.profile.is_suspended:
                messages.error(request, "This account has been suspended. Please contact customer support.")
                return redirect('accounts:login')

            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")

            # If user has a staff role, redirect to dashboard if they didn't have a specific next param
            if not request.GET.get('next') and hasattr(user, 'profile') and user.profile.is_staff_member:
                return redirect('dashboard:index')

            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('catalog:home')


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            profile.phone = form.cleaned_data.get('phone', profile.phone)
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=user, initial={'phone': profile.phone})

    addresses = user.addresses.all()
    recent_orders = user.orders.all()[:5] if hasattr(user, 'orders') else []
    tickets = user.support_tickets.all()[:5]

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
        'addresses': addresses,
        'recent_orders': recent_orders,
        'tickets': tickets,
    })


@login_required
def address_create_view(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            # If first address, make default
            if not request.user.addresses.exists():
                address.is_default_shipping = True
                address.is_default_billing = True
            address.save()
            messages.success(request, "New address added successfully.")
            return redirect('accounts:profile')
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {'form': form, 'action': 'Add'})


@login_required
def address_edit_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('accounts:profile')
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form, 'action': 'Edit', 'address': address})


@login_required
def address_delete_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address removed.")
    return redirect('accounts:profile')


@login_required
def support_tickets_view(request):
    tickets = request.user.support_tickets.all()
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, f"Support ticket #{ticket.id} created. Our support team will get back to you shortly.")
            return redirect('accounts:support_tickets')
    else:
        form = SupportTicketForm()

    return render(request, 'accounts/support_tickets.html', {'tickets': tickets, 'form': form})


@login_required
def ticket_detail_view(request, pk):
    ticket = get_object_or_404(SupportTicket, pk=pk, user=request.user)
    return render(request, 'accounts/support_ticket_detail.html', {'ticket': ticket})


@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    return render(request, 'accounts/notifications.html', {'notifications': notifications})


@login_required
def mark_notification_read_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('accounts:notifications')

from django.contrib import admin
from .models import Profile, Address, Notification, SupportTicket, AuditLog

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'is_suspended', 'created_at')
    list_filter = ('role', 'is_suspended')
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'is_default_shipping', 'is_default_billing')
    search_fields = ('user__username', 'full_name', 'street_address', 'city')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read',)

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('subject', 'message', 'user__username')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'ip_address')
    search_fields = ('action', 'details', 'user__username')

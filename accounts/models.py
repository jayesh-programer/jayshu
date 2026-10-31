from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Role(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    SUPERADMIN = 'superadmin', 'Super Admin'
    MANAGER = 'manager', 'Manager'
    INVENTORY_STAFF = 'inventory_staff', 'Inventory Staff'
    ORDER_STAFF = 'order_staff', 'Order Staff'
    SUPPORT_STAFF = 'support_staff', 'Support Staff'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_suspended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_staff_member(self):
        return self.user.is_superuser or self.role in [
            Role.SUPERADMIN, Role.MANAGER, Role.INVENTORY_STAFF, Role.ORDER_STAFF, Role.SUPPORT_STAFF
        ]

    @property
    def is_manager_or_admin(self):
        return self.user.is_superuser or self.role in [Role.SUPERADMIN, Role.MANAGER]

    @property
    def can_manage_products(self):
        return self.user.is_superuser or self.role in [Role.SUPERADMIN, Role.MANAGER, Role.INVENTORY_STAFF]

    @property
    def can_manage_inventory(self):
        return self.user.is_superuser or self.role in [Role.SUPERADMIN, Role.MANAGER, Role.INVENTORY_STAFF]

    @property
    def can_manage_orders(self):
        return self.user.is_superuser or self.role in [Role.SUPERADMIN, Role.MANAGER, Role.ORDER_STAFF]

    @property
    def can_manage_support(self):
        return self.user.is_superuser or self.role in [Role.SUPERADMIN, Role.MANAGER, Role.SUPPORT_STAFF]

    @property
    def can_view_reports(self):
        return self.user.is_superuser or self.role in [Role.SUPERADMIN, Role.MANAGER]


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = Role.SUPERADMIN if instance.is_superuser else Role.CUSTOMER
        Profile.objects.create(user=instance, role=role)
    else:
        if hasattr(instance, 'profile'):
            if instance.is_superuser and instance.profile.role != Role.SUPERADMIN:
                instance.profile.role = Role.SUPERADMIN
                instance.profile.save()
        else:
            role = Role.SUPERADMIN if instance.is_superuser else Role.CUSTOMER
            Profile.objects.create(user=instance, role=role)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    is_default_shipping = models.BooleanField(default=False)
    is_default_billing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default_shipping', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.street_address}, {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default_shipping:
            Address.objects.filter(user=self.user, is_default_shipping=True).exclude(pk=self.pk).update(is_default_shipping=False)
        if self.is_default_billing:
            Address.objects.filter(user=self.user, is_default_billing=True).exclude(pk=self.pk).update(is_default_billing=False)
        super().save(*args, **kwargs)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.user.username}"


class SupportTicket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    order_number = models.CharField(max_length=50, blank=True, help_text="Optional related order number")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    admin_response = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.id}: {self.subject} ({self.get_status_display()})"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=100)
    details = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {user_str} - {self.action}"

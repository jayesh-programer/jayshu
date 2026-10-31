from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import datetime
from decimal import Decimal

from catalog.models import Category, Product, ProductVariant, Review
from orders.models import Order, OrderStatus, PaymentStatus, Coupon, PaymentMethod
from cart.models import Cart, CartItem, Wishlist
from orders.services import process_order_checkout, cancel_order_and_restore_stock
from accounts.models import Role, SupportTicket

class ECommerceWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Admin and staff users
        self.admin = User.objects.create_superuser(username='admin_test', email='adm@test.com', password='password123')
        self.customer = User.objects.create_user(username='cust_test', email='cust@test.com', password='password123')
        self.customer.profile.role = Role.CUSTOMER
        self.customer.profile.save()

        # Category and Product
        self.category = Category.objects.create(name='Audio', slug='audio')
        self.product = Product.objects.create(
            name='Test Earbuds',
            slug='test-earbuds',
            category=self.category,
            sku='TEST-EAR-01',
            price=Decimal('100.00'),
            discount_price=Decimal('80.00'),
            stock=10,
            low_stock_threshold=3,
            is_active=True
        )

        # Coupon
        now = timezone.now()
        self.coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percent',
            discount_value=Decimal('20.00'),
            min_order_value=Decimal('50.00'),
            usage_limit=100,
            valid_from=now,
            valid_to=now + datetime.timedelta(days=30),
            is_active=True
        )

    def test_product_pricing_and_discount(self):
        self.assertEqual(self.product.effective_price, Decimal('80.00'))
        self.assertTrue(self.product.has_discount)
        self.assertEqual(self.product.discount_percent, 20)

    def test_coupon_discount_calculation(self):
        subtotal = Decimal('100.00')
        discount = self.coupon.calculate_discount(subtotal)
        self.assertEqual(discount, Decimal('20.00'))

    def test_atomic_checkout_deducts_stock(self):
        initial_stock = self.product.stock

        cart = Cart.objects.create(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        checkout_data = {
            'customer_name': 'Test Customer',
            'customer_email': 'cust@test.com',
            'customer_phone': '1234567890',
            'shipping_street': '123 Test St',
            'shipping_city': 'Tech City',
            'shipping_state': 'CA',
            'shipping_postal_code': '94105',
            'shipping_country': 'United States',
            'payment_method': PaymentMethod.COD,
            'coupon_code': 'SAVE20'
        }

        order = process_order_checkout(
            user=self.customer,
            cart=cart,
            checkout_data=checkout_data
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 2)
        self.assertEqual(order.status, OrderStatus.CONFIRMED)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(cart.items.count(), 0)

    def test_order_cancellation_restores_stock(self):
        initial_stock = self.product.stock

        cart = Cart.objects.create(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)

        checkout_data = {
            'customer_name': 'Test Customer',
            'customer_email': 'cust@test.com',
            'customer_phone': '1234567890',
            'shipping_street': '123 Test St',
            'shipping_city': 'Tech City',
            'shipping_state': 'CA',
            'shipping_postal_code': '94105',
            'payment_method': PaymentMethod.COD
        }

        order = process_order_checkout(user=self.customer, cart=cart, checkout_data=checkout_data)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 3)

        # Now cancel order
        cancel_order_and_restore_stock(order, user=self.customer, reason='Testing stock restoration')
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock)
        self.assertEqual(order.status, OrderStatus.CANCELLED)

    def test_unauthorized_access_to_dashboard(self):
        # Anonymous user cannot view dashboard
        response = self.client.get('/dashboard/')
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/')

        # Regular customer cannot view dashboard
        self.client.login(username='cust_test', password='password123')
        response = self.client.get('/dashboard/')
        self.assertRedirects(response, '/')

        # Admin user CAN view dashboard
        self.client.login(username='admin_test', password='password123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

    def test_wishlist_toggle(self):
        self.client.login(username='cust_test', password='password123')
        # Add to wishlist
        response = self.client.post(reverse('cart:toggle_wishlist', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Wishlist.objects.filter(user=self.customer, product=self.product).exists())

        # Toggle again to remove
        response = self.client.post(reverse('cart:toggle_wishlist', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Wishlist.objects.filter(user=self.customer, product=self.product).exists())

    def test_customer_suspension_blocks_access(self):
        # Suspend customer account
        self.customer.profile.is_suspended = True
        self.customer.profile.save()

        # Login attempt should redirect with suspended message
        response = self.client.post('/accounts/login/', {
            'username': 'cust_test',
            'password': 'password123'
        }, follow=True)
        self.assertContains(response, 'suspended')

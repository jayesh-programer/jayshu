from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import datetime
import uuid

from accounts.models import Profile, Role, Address, SupportTicket, AuditLog
from catalog.models import Category, Product, ProductVariant, Review
from orders.models import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus, OrderStatusHistory, Shipment, Coupon
from payments.models import Payment, Refund
from inventory.models import InventoryTransaction, TransactionType

class Command(BaseCommand):
    help = 'Populates the database with comprehensive development sample data.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample development database...")

        # 1. Superuser / Admin
        admin_user, created = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@apexstore.local',
            'first_name': 'Alexander',
            'last_name': 'Pierce',
            'is_staff': True,
            'is_superuser': True,
        })
        if created or not admin_user.has_usable_password():
            admin_user.set_password('admin123')
            admin_user.save()
        admin_user.profile.role = Role.SUPERADMIN
        admin_user.profile.phone = '+1 (800) 555-0100'
        admin_user.profile.save()

        # 2. Staff members
        staff_data = [
            ('manager', 'Manager', 'Marcus', 'Vance', 'manager@apexstore.local', Role.MANAGER),
            ('inventory_staff', 'Inventory Staff', 'Ian', 'Miller', 'inventory@apexstore.local', Role.INVENTORY_STAFF),
            ('order_staff', 'Order Staff', 'Olivia', 'Reed', 'orders@apexstore.local', Role.ORDER_STAFF),
            ('support_staff', 'Support Staff', 'Sophia', 'Chen', 'support@apexstore.local', Role.SUPPORT_STAFF),
        ]
        for uname, title, fname, lname, email, role in staff_data:
            user, ucreated = User.objects.get_or_create(username=uname, defaults={
                'email': email,
                'first_name': fname,
                'last_name': lname,
                'is_staff': True,
            })
            if ucreated or not user.has_usable_password():
                user.set_password('pass123')
                user.save()
            user.profile.role = role
            user.profile.save()

        # 3. Sample Customers
        customers_data = [
            ('customer1', 'John', 'Doe', 'john.doe@example.com', '+1 (555) 234-5678'),
            ('customer2', 'Sarah', 'Jenkins', 'sarah.j@example.com', '+1 (555) 876-5432'),
            ('customer3', 'David', 'Miller', 'david.m@example.com', '+1 (555) 345-6789'),
        ]
        created_customers = []
        for uname, fname, lname, email, phone in customers_data:
            user, ucreated = User.objects.get_or_create(username=uname, defaults={
                'email': email,
                'first_name': fname,
                'last_name': lname,
            })
            if ucreated or not user.has_usable_password():
                user.set_password('pass123')
                user.save()
            user.profile.role = Role.CUSTOMER
            user.profile.phone = phone
            user.profile.save()
            created_customers.append(user)

            # Create default address
            Address.objects.get_or_create(user=user, defaults={
                'full_name': f"{fname} {lname}",
                'phone': phone,
                'street_address': '742 Evergreen Terrace',
                'apartment': 'Suite 101',
                'city': 'Springfield',
                'state': 'IL',
                'postal_code': '62704',
                'country': 'United States',
                'is_default_shipping': True,
                'is_default_billing': True,
            })

        # 4. Categories & Subcategories
        cats_dict = {}
        top_cats = [
            ('Electronics', 'electronics', 'High-performance computing, audio gear, and personal devices.'),
            ('Fashion & Apparel', 'fashion', 'Designer everyday apparel, outerwear, and footwear.'),
            ('Home & Living', 'home-living', 'Smart home automation, decor, and ergonomic home essentials.'),
        ]
        for name, slug, desc in top_cats:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'description': desc})
            cats_dict[slug] = cat

        sub_cats = [
            ('Smartphones & Audio', 'smartphones-audio', cats_dict['electronics']),
            ('Laptops & Tech', 'laptops-tech', cats_dict['electronics']),
            ('Men\'s Apparel', 'mens-apparel', cats_dict['fashion']),
            ('Women\'s Apparel', 'womens-apparel', cats_dict['fashion']),
            ('Smart Decor', 'smart-decor', cats_dict['home-living']),
        ]
        for name, slug, parent in sub_cats:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'parent': parent})
            cats_dict[slug] = cat

        # 5. Products & Inventory
        products_info = [
            {
                'name': 'Apex Pro Wireless Noise-Cancelling Headphones',
                'slug': 'apex-pro-wireless-headphones',
                'category': cats_dict['smartphones-audio'],
                'sku': 'AUD-PRO-900',
                'price': Decimal('299.99'),
                'discount_price': Decimal('249.99'),
                'stock': 42,
                'low_stock_threshold': 5,
                'short_description': 'Studio-grade spatial acoustic audio with 40-hour battery life and adaptive hybrid ANC.',
                'description': 'Engineered with custom titanium 45mm dynamic drivers, the Apex Pro delivers reference-grade acoustic response. Includes ultra-soft memory foam earcups, active ambient sound pass-through, and USB-C fast charging.\n\nKey Specs:\n• Weight: 250g\n• Bluetooth 5.3 with LDAC support\n• 40hr playtime with ANC active',
                'is_featured': True,
                'variants': [
                    ('Color', 'Midnight Black', 'AUD-PRO-BLK', Decimal('0.00'), 25),
                    ('Color', 'Silver Frost', 'AUD-PRO-SLV', Decimal('0.00'), 17),
                ]
            },
            {
                'name': 'Titan UltraBook X15 Titanium Laptop',
                'slug': 'titan-ultrabook-x15',
                'category': cats_dict['laptops-tech'],
                'sku': 'LAP-TTN-150',
                'price': Decimal('1499.00'),
                'discount_price': Decimal('1349.00'),
                'stock': 18,
                'low_stock_threshold': 4,
                'short_description': 'Ultra-thin aerospace aluminum chassis with 3.2K 120Hz OLED display.',
                'description': 'The Titan UltraBook X15 is the definitive workstation for developers and creative professionals. Powered by an advanced 14-core processor, dedicated neural acceleration, and 18 hours of all-day battery efficiency.',
                'is_featured': True,
                'variants': [
                    ('Configuration', '16GB RAM / 512GB SSD', 'LAP-16-512', Decimal('0.00'), 10),
                    ('Configuration', '32GB RAM / 1TB SSD', 'LAP-32-1TB', Decimal('300.00'), 8),
                ]
            },
            {
                'name': 'Merino Wool Minimalist Crewneck Sweater',
                'slug': 'merino-wool-crewneck-sweater',
                'category': cats_dict['mens-apparel'],
                'sku': 'APP-MRN-201',
                'price': Decimal('89.50'),
                'discount_price': None,
                'stock': 4,  # LOW STOCK ON PURPOSE (threshold is 5)
                'low_stock_threshold': 5,
                'short_description': '100% extra-fine Australian merino wool with thermo-regulating breathability.',
                'description': 'Woven from exceptionally soft 19.5-micron combed merino wool. Naturally moisture-wicking and odor-resistant, making it ideal for transitional seasonal styling.',
                'is_featured': True,
                'variants': [
                    ('Size', 'Medium', 'APP-MRN-M', Decimal('0.00'), 2),
                    ('Size', 'Large', 'APP-MRN-L', Decimal('0.00'), 2),
                ]
            },
            {
                'name': 'AeroGlide Carbon Fiber Mechanical Keyboard',
                'slug': 'aeroglide-carbon-mechanical-keyboard',
                'category': cats_dict['laptops-tech'],
                'sku': 'KEY-GLD-75',
                'price': Decimal('179.00'),
                'discount_price': Decimal('149.00'),
                'stock': 0,  # OUT OF STOCK ON PURPOSE
                'low_stock_threshold': 5,
                'short_description': '75% compact wireless mechanical keyboard with hot-swappable tactile switches.',
                'description': 'Crafted with a forged carbon-fiber switch plate and sound-dampening silicone gasket mount. Supports tri-mode connectivity (2.4GHz, Bluetooth 5.1, and USB-C).',
                'is_featured': False,
            },
            {
                'name': 'Aura Ambient Smart LED Light Bar Set',
                'slug': 'aura-ambient-smart-led-bars',
                'category': cats_dict['smart-decor'],
                'sku': 'LGT-AUR-2PK',
                'price': Decimal('69.99'),
                'discount_price': Decimal('54.99'),
                'stock': 35,
                'low_stock_threshold': 8,
                'short_description': 'Synchronized RGBIC room accent illumination with mobile app control.',
                'description': 'Transform your workspace and home entertainment hub with 16 million colors and reactive sound visualization modes. Integrates with smart voice assistants.',
                'is_featured': True,
            },
            {
                'name': 'Tailored Structured Trench Coat',
                'slug': 'tailored-structured-trench-coat',
                'category': cats_dict['womens-apparel'],
                'sku': 'APP-TRN-101',
                'price': Decimal('220.00'),
                'discount_price': Decimal('185.00'),
                'stock': 12,
                'low_stock_threshold': 3,
                'short_description': 'Double-breasted water-repellent gabardine twill with waist tie belt.',
                'description': 'A timeless wardrobe essential featuring storm flaps, horn-effect buttons, and deep welt pockets.',
                'is_featured': False,
            }
        ]

        created_products = []
        for p_data in products_info:
            variants_list = p_data.pop('variants', [])
            prod, pcreated = Product.objects.get_or_create(slug=p_data['slug'], defaults=p_data)
            created_products.append(prod)

            if pcreated and prod.stock > 0:
                InventoryTransaction.objects.create(
                    product=prod,
                    change_type=TransactionType.RESTOCK,
                    quantity=prod.stock,
                    previous_stock=0,
                    new_stock=prod.stock,
                    note='Initial catalog stock replenishment',
                    created_by=admin_user
                )

            for vname, vval, vsku, add_price, vstock in variants_list:
                ProductVariant.objects.get_or_create(
                    product=prod,
                    name=vname,
                    value=vval,
                    defaults={
                        'sku': vsku,
                        'additional_price': add_price,
                        'stock': vstock
                    }
                )

        # 6. Coupons
        coupons_data = [
            ('WELCOME25', 'percent', Decimal('25.00'), Decimal('50.00'), Decimal('100.00'), 500),
            ('SAVE10', 'fixed', Decimal('10.00'), Decimal('30.00'), None, 200),
            ('SUMMER50', 'percent', Decimal('50.00'), Decimal('100.00'), Decimal('150.00'), 50),
        ]
        now = timezone.now()
        created_coupons = []
        for code, dtype, dval, min_val, max_cap, limit in coupons_data:
            c, _ = Coupon.objects.get_or_create(code=code, defaults={
                'discount_type': dtype,
                'discount_value': dval,
                'min_order_value': min_val,
                'max_discount_amount': max_cap,
                'usage_limit': limit,
                'valid_from': now - datetime.timedelta(days=10),
                'valid_to': now + datetime.timedelta(days=180),
                'is_active': True
            })
            created_coupons.append(c)

        # 7. Sample Orders Across Different Statuses
        p1 = created_products[0]  # Headphones
        p2 = created_products[1]  # Laptop
        p5 = created_products[4]  # Light Bars

        # Order 1: Delivered & Paid via Card
        ord1, c1 = Order.objects.get_or_create(order_number='ORD-20261015-DELIV1', defaults={
            'user': created_customers[0],
            'customer_name': 'John Doe',
            'customer_email': 'john.doe@example.com',
            'customer_phone': '+1 (555) 234-5678',
            'shipping_street': '742 Evergreen Terrace',
            'shipping_apartment': 'Apt 4B',
            'shipping_city': 'Springfield',
            'shipping_state': 'IL',
            'shipping_postal_code': '62704',
            'subtotal': Decimal('249.99'),
            'discount_amount': Decimal('0.00'),
            'shipping_fee': Decimal('0.00'),
            'tax_amount': Decimal('12.50'),
            'total': Decimal('262.49'),
            'status': OrderStatus.DELIVERED,
            'payment_method': PaymentMethod.CARD,
            'payment_status': PaymentStatus.PAID,
            'created_at': now - datetime.timedelta(days=6)
        })
        if c1:
            OrderItem.objects.create(
                order=ord1, product=p1, product_name=p1.name,
                unit_price=p1.effective_price, quantity=1, line_total=p1.effective_price
            )
            Payment.objects.create(
                order=ord1, transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
                payment_method='Online Credit/Debit Card', amount=ord1.total,
                status='success', gateway_response='Auth approved (Code 998234)'
            )
            Shipment.objects.create(
                order=ord1, carrier='FastTrack Express', tracking_number='TRK-98234190',
                status='delivered', delivered_at=now - datetime.timedelta(days=1)
            )
            OrderStatusHistory.objects.create(order=ord1, status=OrderStatus.DELIVERED, comment='Delivered to front door.')

        # Order 2: Shipped via COD
        ord2, c2 = Order.objects.get_or_create(order_number='ORD-20261019-SHIP02', defaults={
            'user': created_customers[1],
            'customer_name': 'Sarah Jenkins',
            'customer_email': 'sarah.j@example.com',
            'customer_phone': '+1 (555) 876-5432',
            'shipping_street': '123 Market St',
            'shipping_city': 'Chicago',
            'shipping_state': 'IL',
            'shipping_postal_code': '60601',
            'subtotal': Decimal('54.99'),
            'discount_amount': Decimal('10.00'),
            'shipping_fee': Decimal('15.00'),
            'tax_amount': Decimal('2.25'),
            'total': Decimal('62.24'),
            'status': OrderStatus.SHIPPED,
            'payment_method': PaymentMethod.COD,
            'payment_status': PaymentStatus.PENDING,
            'created_at': now - datetime.timedelta(days=2)
        })
        if c2:
            OrderItem.objects.create(
                order=ord2, product=p5, product_name=p5.name,
                unit_price=p5.effective_price, quantity=1, line_total=p5.effective_price
            )
            Shipment.objects.create(
                order=ord2, carrier='FastTrack Express', tracking_number='TRK-74910283',
                status='in_transit', estimated_delivery=(now + datetime.timedelta(days=2)).date()
            )
            OrderStatusHistory.objects.create(order=ord2, status=OrderStatus.SHIPPED, comment='Dispatched from facility.')

        # Order 3: Cancelled Order with Refund
        ord3, c3 = Order.objects.get_or_create(order_number='ORD-20261012-CANC03', defaults={
            'user': created_customers[2],
            'customer_name': 'David Miller',
            'customer_email': 'david.m@example.com',
            'customer_phone': '+1 (555) 345-6789',
            'shipping_street': '456 Oak Avenue',
            'shipping_city': 'Dallas',
            'shipping_state': 'TX',
            'shipping_postal_code': '75001',
            'subtotal': Decimal('249.99'),
            'discount_amount': Decimal('0.00'),
            'shipping_fee': Decimal('0.00'),
            'tax_amount': Decimal('12.50'),
            'total': Decimal('262.49'),
            'status': OrderStatus.CANCELLED,
            'payment_method': PaymentMethod.CARD,
            'payment_status': PaymentStatus.REFUNDED,
            'created_at': now - datetime.timedelta(days=9)
        })
        if c3:
            OrderItem.objects.create(
                order=ord3, product=p1, product_name=p1.name,
                unit_price=p1.effective_price, quantity=1, line_total=p1.effective_price
            )
            Refund.objects.create(
                order=ord3, refund_id=f"RFD-{uuid.uuid4().hex[:8].upper()}",
                amount=ord3.total, reason='Customer changed mind prior to dispatch',
                status='processed', created_by=admin_user
            )
            OrderStatusHistory.objects.create(order=ord3, status=OrderStatus.CANCELLED, comment='Cancelled and refunded.')

        # 8. Product Reviews
        Review.objects.get_or_create(product=p1, user=created_customers[0], defaults={
            'rating': 5,
            'title': 'Exceptional sound quality and battery life',
            'comment': 'I commute daily on the subway and these headphones completely block out engine noise. Highs are crisp, bass is rich without being muddy. Highly recommended!',
            'is_approved': True
        })
        Review.objects.get_or_create(product=p1, user=created_customers[1], defaults={
            'rating': 5,
            'title': 'Very comfortable for long work hours',
            'comment': 'I wear them 8 hours a day during remote meetings. The ear cushions are super comfortable with zero ear fatigue.',
            'is_approved': True
        })
        Review.objects.get_or_create(product=p2, user=created_customers[2], defaults={
            'rating': 4,
            'title': 'Stunning OLED screen and fast build times',
            'comment': 'Compiles large codebases effortlessly. Only minor critique is the trackpad is slightly large, but overall 9/10 performance.',
            'is_approved': True
        })

        # 9. Support Tickets
        SupportTicket.objects.get_or_create(id=1, defaults={
            'user': created_customers[0],
            'subject': 'Inquiry regarding international plug adapter',
            'order_number': ord1.order_number,
            'message': 'Does the Apex Pro package include an EU or UK wall charger in addition to the standard US plug?',
            'status': 'resolved',
            'priority': 'medium',
            'admin_response': 'Hello John! The package includes a universal USB-C to USB-C braided charging cable that operates with any standard 110-240V adapter worldwide.',
            'assigned_to': admin_user
        })
        SupportTicket.objects.get_or_create(id=2, defaults={
            'user': created_customers[1],
            'subject': 'Tracking update notification request',
            'order_number': ord2.order_number,
            'message': 'Hello, could you let me know if signature will be required upon doorstep delivery?',
            'status': 'open',
            'priority': 'low',
            'admin_response': '',
        })

        self.stdout.write(self.style.SUCCESS("Database successfully seeded with realistic sample development data!"))
        self.stdout.write(self.style.SUCCESS("Super Admin: admin / admin123"))
        self.stdout.write(self.style.SUCCESS("Manager: manager / pass123"))
        self.stdout.write(self.style.SUCCESS("Customer: customer1 / pass123"))

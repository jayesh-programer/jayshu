import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Product, ProductVariant
from orders.models import Coupon, Order, OrderItem
from payments.models import Payment, Refund

# 1. Product INR Pricing Map
inr_pricing = {
    # Flagship GPUs & Laptops
    'asus-rog-strix-geforce-rtx-4090-oc': (Decimal('189999.00'), Decimal('174999.00')),
    'geforce-rtx-4080-super-founders-edition': (Decimal('104999.00'), Decimal('97999.00')),
    'amd-radeon-rx-7900-xtx-24gb-graphics-card': (Decimal('99999.00'), Decimal('91999.00')),
    'msi-geforce-rtx-4070-ti-super-gaming-x-slim': (Decimal('84999.00'), Decimal('79999.00')),
    'titan-ultrabook-x15': (Decimal('139999.00'), Decimal('124999.00')),

    # Flagship & Performance CPUs
    'intel-core-i9-14900ks-special-edition-processor': (Decimal('69999.00'), Decimal('64999.00')),
    'amd-ryzen-9-7950x3d-gaming-processor': (Decimal('64999.00'), Decimal('56999.00')),
    'intel-core-i7-14700k-gaming-processor': (Decimal('41999.00'), Decimal('36999.00')),
    'amd-ryzen-7-7800x3d-gaming-processor': (Decimal('42999.00'), Decimal('37999.00')),

    # Motherboards
    'asus-rog-maximus-z790-dark-hero-motherboard': (Decimal('64999.00'), Decimal('59999.00')),
    'gigabyte-z790-aorus-master-x-motherboard': (Decimal('54999.00'), Decimal('48999.00')),
    'msi-mag-b650-tomahawk-wifi-motherboard': (Decimal('24999.00'), Decimal('21999.00')),

    # Storage (NVMe SSDs)
    'crucial-t700-2tb-pcie5-nvme-ssd': (Decimal('29999.00'), Decimal('26999.00')),
    'wd-black-sn850x-4tb-gaming-nvme-ssd': (Decimal('34999.00'), Decimal('31999.00')),
    'samsung-990-pro-2tb-nvme-ssd': (Decimal('19999.00'), Decimal('17499.00')),

    # Memory (RAM)
    'gskill-trident-z5-rgb-64gb-ddr5-6400': (Decimal('24999.00'), Decimal('21999.00')),
    'corsair-dominator-titanium-rgb-ddr5-32gb': (Decimal('19999.00'), Decimal('16999.00')),
    'teamgroup-t-force-delta-rgb-32gb-ddr5-6000': (Decimal('13999.00'), Decimal('11499.00')),

    # Power Supplies (PSUs)
    'seasonic-vertex-gx-1200-modular-psu': (Decimal('24999.00'), Decimal('22499.00')),
    'corsair-rm1000x-shift-1000w-modular-psu': (Decimal('21999.00'), Decimal('18999.00')),

    # PC Cases
    'hyte-y70-touch-panoramic-glass-pc-case': (Decimal('37999.00'), Decimal('34999.00')),
    'lian-li-o11-dynamic-evo-rgb-pc-case': (Decimal('18999.00'), Decimal('16499.00')),
    'corsair-5000d-airflow-tempered-glass-case': (Decimal('16999.00'), Decimal('14999.00')),
    'fractal-design-north-charcoal-black-case': (Decimal('16499.00'), Decimal('14499.00')),

    # Cooling & Fans
    'nzxt-kraken-elite-360-rgb-liquid-cooler': (Decimal('27999.00'), Decimal('24999.00')),
    'arctic-liquid-freezer-iii-360-argb-cooler': (Decimal('14999.00'), Decimal('12999.00')),
    'noctua-nh-d15-chromax-black-cpu-cooler': (Decimal('12499.00'), Decimal('10999.00')),
    'lian-li-uni-fan-sl-infinity-120-rgb-3pack': (Decimal('10999.00'), Decimal('9499.00')),

    # Gaming Peripherals & Chairs
    'secretlab-titan-evo-esports-gaming-chair': (Decimal('54999.00'), Decimal('48999.00')),
    'steelseries-arctis-nova-pro-wireless-headset': (Decimal('34999.00'), Decimal('31999.00')),
    'apex-pro-wireless-headphones': (Decimal('28999.00'), Decimal('24999.00')),
    'shure-mv7x-streaming-microphone': (Decimal('24999.00'), Decimal('21999.00')),
    'razer-huntsman-v3-pro-optical-keyboard': (Decimal('24999.00'), Decimal('22999.00')),
    'logitech-g-pro-x-superlight-2-wireless-mouse': (Decimal('16999.00'), Decimal('14999.00')),
    'aeroglide-carbon-mechanical-keyboard': (Decimal('15999.00'), Decimal('12999.00')),

    # Lifestyle & Apparel
    'tailored-structured-trench-coat': (Decimal('14999.00'), Decimal('11999.00')),
    'merino-wool-crewneck-sweater': (Decimal('7999.00'), Decimal('6499.00')),
    'aura-ambient-smart-led-bars': (Decimal('5999.00'), Decimal('4499.00')),
}

print("Updating Product Prices to INR...")
for p in Product.objects.all():
    if p.slug in inr_pricing:
        reg, disc = inr_pricing[p.slug]
        p.price = reg
        p.discount_price = disc
    else:
        # Fallback multiplier ~85
        p.price = Decimal(str(int(p.price * 85)))
        if p.discount_price:
            p.discount_price = Decimal(str(int(p.discount_price * 85)))
    p.save()
    print(f" -> {p.name}: INR {p.effective_price} (MRP: INR {p.price})")

print("\nUpdating Product Variants to INR...")
for var in ProductVariant.objects.all():
    if var.additional_price > 0:
        if var.additional_price < 50:
            var.additional_price = Decimal(str(int(var.additional_price * 85)))
        elif var.additional_price < 200:
            var.additional_price = Decimal('4999.00')
        else:
            var.additional_price = Decimal('9999.00')
    elif var.additional_price < 0:
        var.additional_price = Decimal('-1999.00')
    var.save()
    print(f" -> {var}: +INR {var.additional_price}")

print("\nUpdating Coupons to INR...")
for c in Coupon.objects.all():
    if c.code == 'WELCOME25':
        c.min_order_value = Decimal('1999.00')
        c.max_discount_amount = Decimal('2500.00')
    elif c.code == 'SAVE10':
        c.code = 'SAVE500'
        c.discount_type = 'fixed'
        c.discount_value = Decimal('500.00')
        c.min_order_value = Decimal('2499.00')
    elif c.code == 'SUMMER50':
        c.min_order_value = Decimal('4999.00')
        c.max_discount_amount = Decimal('5000.00')
    c.save()
    print(f" -> Coupon {c.code}: {c.discount_value} ({c.discount_type}) on min INR {c.min_order_value}")

print("\nUpdating Sample Orders & Line Items to INR...")
for order in Order.objects.all():
    # Only scale up if total < 5000 (meaning it was in USD previously)
    if order.total < 5000:
        scale = Decimal('85.00')
        order.subtotal = Decimal(str(int(order.subtotal * scale)))
        order.discount_amount = Decimal(str(int(order.discount_amount * scale)))
        order.shipping_fee = Decimal('149.00') if order.shipping_fee > 0 else Decimal('0.00')
        order.tax_amount = round((order.subtotal - order.discount_amount) * Decimal('0.18'), 2)
        order.total = (order.subtotal - order.discount_amount) + order.shipping_fee + order.tax_amount
        order.shipping_country = 'India'
        order.save()

        for item in order.items.all():
            item.unit_price = Decimal(str(int(item.unit_price * scale)))
            item.line_total = item.unit_price * item.quantity
            item.save()

        # Update matching payment
        for pay in Payment.objects.filter(order=order):
            pay.amount = order.total
            pay.currency = 'INR'
            pay.save()

        print(f" -> Order {order.order_number}: INR {order.total}")

print("\nSUCCESS: Complete catalog, variants, coupons, and orders converted to INR!")

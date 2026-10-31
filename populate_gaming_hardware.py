import os
import shutil
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from catalog.models import Category, Product, ProductVariant, ProductImage, Review
from inventory.models import InventoryTransaction, TransactionType

brain_dir = r'C:\Users\Kartik\.gemini\antigravity\brain\99716db7-6308-4089-8faf-03497140f51e'
media_products_dir = r'C:\Users\Kartik\.gemini\antigravity\scratch\ecommerce\media\products'
os.makedirs(media_products_dir, exist_ok=True)

admin_user = User.objects.filter(is_superuser=True).first()
customer1 = User.objects.filter(username='customer1').first()
customer2 = User.objects.filter(username='customer2').first()

# 1. Categories
print("Creating Categories...")
cats_dict = {}

main_cats = [
    ('PC Components & Hardware', 'pc-components', 'High-performance graphics cards, processors, motherboards, liquid coolers, and memory.'),
    ('Gaming & Esports Gear', 'gaming-gear', 'Tournament-grade esports gaming mice, mechanical keyboards, spatial headsets, and ergonomic chairs.'),
]

for name, slug, desc in main_cats:
    cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'description': desc})
    cats_dict[slug] = cat

sub_cats = [
    ('Graphics Cards (GPUs)', 'graphics-cards', cats_dict['pc-components']),
    ('Processors (CPUs)', 'processors-cpus', cats_dict['pc-components']),
    ('Motherboards', 'motherboards', cats_dict['pc-components']),
    ('Cooling & Cases', 'cooling-cases', cats_dict['pc-components']),
    ('Memory & Storage', 'memory-storage', cats_dict['pc-components']),
    ('Gaming Mice', 'gaming-mice', cats_dict['gaming-gear']),
    ('Gaming Keyboards', 'gaming-keyboards', cats_dict['gaming-gear']),
    ('Gaming Headsets', 'gaming-headsets', cats_dict['gaming-gear']),
    ('Gaming Chairs & Desks', 'gaming-chairs-desks', cats_dict['gaming-gear']),
    ('Streaming & Microphones', 'streaming-audio', cats_dict['gaming-gear']),
]

for name, slug, parent in sub_cats:
    cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'parent': parent})
    cats_dict[slug] = cat

# 2. Image files mapping
image_map = {
    'asus-rog-strix-geforce-rtx-4090-oc': 'rtx_4090_commercial_1793021366891.jpg',
    'amd-ryzen-7-7800x3d-gaming-processor': 'ryzen_7800x3d_commercial_1793021369219.jpg',
    'nzxt-kraken-elite-360-rgb-liquid-cooler': 'nzxt_kraken_commercial_1793021366891.jpg',
    'corsair-dominator-titanium-rgb-ddr5-32gb': 'corsair_ram_commercial_1793021366897.jpg',
    'asus-rog-maximus-z790-dark-hero-motherboard': 'asus_motherboard_commercial_1793021374788.jpg',
    'logitech-g-pro-x-superlight-2-wireless-mouse': 'logitech_mouse_commercial_1793021378434.jpg',
    'razer-huntsman-v3-pro-optical-keyboard': 'razer_keyboard_commercial_1793021375753.jpg',
    'steelseries-arctis-nova-pro-wireless-headset': 'arctis_headset_commercial_1793021376371.jpg',
    'secretlab-titan-evo-esports-gaming-chair': 'secretlab_chair_commercial_1793021379926.jpg',
    'shure-mv7x-streaming-microphone': 'shure_mic_commercial_1793021381782.jpg',
}

for slug, src_name in image_map.items():
    src_file = os.path.join(brain_dir, src_name)
    dst_file = os.path.join(media_products_dir, f'{slug}.jpg')
    if os.path.exists(src_file):
        shutil.copy2(src_file, dst_file)
        print(f"Copied image for {slug}: {os.path.getsize(dst_file)} bytes")
    else:
        print(f"ERROR: Not found {src_file}")

# 3. Products
products_data = [
    {
        'name': 'ASUS ROG Strix GeForce RTX 4090 OC 24GB Graphics Card',
        'slug': 'asus-rog-strix-geforce-rtx-4090-oc',
        'category': cats_dict['graphics-cards'],
        'sku': 'GPU-ROG-4090',
        'price': Decimal('1799.99'),
        'discount_price': Decimal('1699.99'),
        'stock': 12,
        'low_stock_threshold': 3,
        'short_description': 'Flagship Ada Lovelace architecture with 24GB GDDR6X, axial-tech cooling, and patented vapor chamber.',
        'description': (
            "The ASUS ROG Strix GeForce RTX 4090 brings a whole new meaning to going with the flow. Inside and out, "
            "every element gives the monstrous GPU headroom to breathe freely and achieve peak performance.\n\n"
            "Key Specifications:\n"
            "• CUDA Cores: 16,384\n"
            "• Memory: 24GB GDDR6X 384-bit\n"
            "• Boost Clock: 2640 MHz (OC Mode)\n"
            "• Power Connectors: 1x 16-pin (12VHPWR)\n"
            "• Cooling: Patented vapor chamber with milled heatspreader and 3.5-slot axial fan design\n"
            "• Outputs: 2x HDMI 2.1a, 3x DisplayPort 1.4a"
        ),
        'is_featured': True,
        'variants': [
            ('Color Edition', 'Stealth Black', 'GPU-4090-BLK', Decimal('0.00'), 8),
            ('Color Edition', 'White OC Edition', 'GPU-4090-WHT', Decimal('50.00'), 4),
        ],
        'review': ('Absolute Beast of a GPU', 5, 'Runs 4K Cyberpunk at 120+ FPS with DLSS 3.5 fully maxed out. Temperatures rarely cross 62°C.', customer1)
    },
    {
        'name': 'AMD Ryzen 7 7800X3D 8-Core 16-Thread Gaming Processor',
        'slug': 'amd-ryzen-7-7800x3d-gaming-processor',
        'category': cats_dict['processors-cpus'],
        'sku': 'CPU-RYZ-7800X3D',
        'price': Decimal('449.00'),
        'discount_price': Decimal('399.00'),
        'stock': 25,
        'low_stock_threshold': 5,
        'short_description': 'The undisputed king of PC gaming with AMD 3D V-Cache technology on Socket AM5.',
        'description': (
            "Built specifically for competitive esports and AAA open-world gaming. The AMD Ryzen 7 7800X3D features "
            "stacked 3D V-Cache technology, delivering massive L3 cache directly above the compute cores to minimize latency.\n\n"
            "Key Specifications:\n"
            "• Cores / Threads: 8 Cores / 16 Threads\n"
            "• Base / Boost Clock: 4.2 GHz / 5.0 GHz\n"
            "• L3 Cache: 96MB (104MB Total Cache)\n"
            "• TDP: 120W\n"
            "• Socket: AM5 (PCIe 5.0 and DDR5 Ready)"
        ),
        'is_featured': True,
        'variants': [
            ('Packaging', 'Retail Boxed AM5 Processor', 'CPU-7800X3D-BOX', Decimal('0.00'), 25),
        ],
        'review': ('Best Gaming CPU on the Market', 5, 'Massive 1% low frame rate improvements over my older setup. Consumes very little power under load.', customer2)
    },
    {
        'name': 'NZXT Kraken Elite 360 RGB AIO Liquid CPU Cooler',
        'slug': 'nzxt-kraken-elite-360-rgb-liquid-cooler',
        'category': cats_dict['cooling-cases'],
        'sku': 'CLR-NZXT-360',
        'price': Decimal('279.99'),
        'discount_price': Decimal('259.99'),
        'stock': 18,
        'low_stock_threshold': 4,
        'short_description': '360mm high-performance radiator with custom 2.36” wide-angle LCD display and RGB Core fans.',
        'description': (
            "Deliver chilled temperatures and show off your personality. The Kraken Elite RGB combines an Asetek 7th gen pump "
            "with a vivid 640x640 LCD screen capable of displaying custom GIFs, system telemetry, and web integrations.\n\n"
            "Key Specifications:\n"
            "• Radiator Size: 360mm (3x 120mm fans)\n"
            "• Display: 2.36” TFT-LCD, 640x640 resolution, 60 Hz refresh rate\n"
            "• Fans: 3x F120 RGB Core Fans (500 - 1,800 RPM)\n"
            "• Tubing: 400mm ultra-low evaporation rubber with nylon braided sleeves\n"
            "• Socket Support: Intel LGA 1700/1200 & AMD AM5/AM4"
        ),
        'is_featured': True,
        'variants': [
            ('Color', 'Matte Black', 'CLR-NZXT-BLK', Decimal('0.00'), 10),
            ('Color', 'Matte White', 'CLR-NZXT-WHT', Decimal('0.00'), 8),
        ],
        'review': ('Gorgeous LCD and whisper quiet', 5, 'The screen looks razor sharp and keeping my 7800X3D at 35C idle and under 68C under full load.', customer1)
    },
    {
        'name': 'Corsair Dominator Titanium RGB 32GB (2x16GB) DDR5-6000',
        'slug': 'corsair-dominator-titanium-rgb-ddr5-32gb',
        'category': cats_dict['memory-storage'],
        'sku': 'RAM-DOM-6000',
        'price': Decimal('189.99'),
        'discount_price': Decimal('169.99'),
        'stock': 30,
        'low_stock_threshold': 6,
        'short_description': 'Premium forged aluminum heatspreaders with interchangeable top bars and 11 vibrant CAPELLIX LEDs.',
        'description': (
            "Push the limits of modern PC performance. Corsair Dominator Titanium DDR5 memory pairs clean, refined styling "
            "with superior die screening and DHX patented cooling for high-frequency gaming stability.\n\n"
            "Key Specifications:\n"
            "• Capacity: 32GB (2 x 16GB)\n"
            "• Tested Speed: DDR5-6000 MT/s\n"
            "• Tested Latency: CL30-36-36-76\n"
            "• Tested Voltage: 1.40V\n"
            "• Compatibility: Intel XMP 3.0 & AMD EXPO certified"
        ),
        'is_featured': True,
        'variants': [
            ('Color', 'Stealth Gray', 'RAM-DOM-GRY', Decimal('0.00'), 18),
            ('Color', 'First Edition White', 'RAM-DOM-WHT', Decimal('10.00'), 12),
        ],
        'review': ('Tight timings and flawless stability', 5, 'Enabled EXPO in BIOS with 1 click. Rock solid stability on my AM5 board.', customer2)
    },
    {
        'name': 'ASUS ROG Maximus Z790 Dark Hero Gaming Motherboard',
        'slug': 'asus-rog-maximus-z790-dark-hero-motherboard',
        'category': cats_dict['motherboards'],
        'sku': 'MB-ASUS-Z790',
        'price': Decimal('629.99'),
        'discount_price': Decimal('599.99'),
        'stock': 15,
        'low_stock_threshold': 3,
        'short_description': 'Robust 20+1+2 power stages, DDR5 support, PCIe 5.0, WiFi 7, and onboard Polymo I/O lighting.',
        'description': (
            "The ROG Maximus Z790 Dark Hero delivers monstrous power delivery, hyper-fast PCIe 5.0 storage support, "
            "and comprehensive thermal design for Intel Core 14th & 13th Gen desktop processors.\n\n"
            "Key Specifications:\n"
            "• Form Factor: ATX\n"
            "• Socket: Intel LGA 1700\n"
            "• Power Design: 20+1+2 teamed power stages (90A rating)\n"
            "• Networking: Intel Wi-Fi 7 & 2.5 Gb Ethernet\n"
            "• Storage: 5x M.2 slots (1x PCIe 5.0 x4 with massive heatsink)"
        ),
        'is_featured': False,
        'variants': [
            ('Edition', 'Standard Dark Hero ATX', 'MB-Z790-STD', Decimal('0.00'), 15),
        ],
        'review': ('The ultimate enthusiast board', 5, 'Build quality is second to none. The BIOS overclocking features and WiFi 7 speeds are insane.', customer1)
    },
    {
        'name': 'Logitech G PRO X SUPERLIGHT 2 Wireless Gaming Mouse',
        'slug': 'logitech-g-pro-x-superlight-2-wireless-mouse',
        'category': cats_dict['gaming-mice'],
        'sku': 'MSE-LOG-GPX2',
        'price': Decimal('159.99'),
        'discount_price': Decimal('149.99'),
        'stock': 40,
        'low_stock_threshold': 8,
        'short_description': 'Next-gen 60g ultralight wireless esports mouse with HERO 2 sensor and LIGHTFORCE hybrid optical switches.',
        'description': (
            "Engineered in collaboration with top esports champions. The PRO X SUPERLIGHT 2 delivers sub-micron 32,000 DPI "
            "tracking, 2000Hz polling rate, and 95 hours of continuous battery life without requiring honeycomb cutouts.\n\n"
            "Key Specifications:\n"
            "• Weight: 60 grams\n"
            "• Sensor: HERO 2 (100 – 32,000 DPI, >500 IPS)\n"
            "• Switches: LIGHTFORCE Hybrid Optical-Mechanical\n"
            "• Connectivity: LIGHTSPEED Wireless + USB-C fast charging\n"
            "• Battery Life: Up to 95 hours constant motion"
        ),
        'is_featured': True,
        'variants': [
            ('Color', 'Carbon Black', 'MSE-GPX2-BLK', Decimal('0.00'), 20),
            ('Color', 'Polar White', 'MSE-GPX2-WHT', Decimal('0.00'), 15),
            ('Color', 'Magenta Pink', 'MSE-GPX2-PNK', Decimal('0.00'), 5),
        ],
        'review': ('Esports perfection', 5, 'Glide is effortless on glass pads. Battery easily lasts 2+ weeks of intense daily gaming.', customer2)
    },
    {
        'name': 'Razer Huntsman V3 Pro Optical Analog Gaming Keyboard',
        'slug': 'razer-huntsman-v3-pro-optical-keyboard',
        'category': cats_dict['gaming-keyboards'],
        'sku': 'KBD-RZR-HV3',
        'price': Decimal('249.99'),
        'discount_price': Decimal('229.99'),
        'stock': 24,
        'low_stock_threshold': 5,
        'short_description': 'Rapid Trigger mode with adjustable optical actuation (0.1 to 4.0mm) and textured doubleshot PBT keycaps.',
        'description': (
            "Experience unprecedented response speed. The Razer Huntsman V3 Pro features Gen-2 Analog Optical switches "
            "with Rapid Trigger for lightning-fast repeated keypresses, onboard LED array indicators, and a multi-function digital dial.\n\n"
            "Key Specifications:\n"
            "• Switch Type: Razer Gen-2 Analog Optical Switches\n"
            "• Actuation Range: 0.1 mm – 4.0 mm adjustable\n"
            "• Top Plate: 5052 Brushed Aluminum\n"
            "• Wrist Rest: Magnetic firm leatherette\n"
            "• Polling Rate: 1000Hz with onboard profile storage"
        ),
        'is_featured': True,
        'variants': [
            ('Layout', 'Full-Size 104-Key', 'KBD-HV3-FULL', Decimal('0.00'), 16),
            ('Layout', 'Tenkeyless (TKL)', 'KBD-HV3-TKL', Decimal('-20.00'), 8),
        ],
        'review': ('Rapid Trigger is game changing for Counter-Strike', 5, 'Counter-strafing feels instantaneous. The adjustable actuation depth is worth every penny.', customer1)
    },
    {
        'name': 'SteelSeries Arctis Nova Pro Wireless Gaming Headset',
        'slug': 'steelseries-arctis-nova-pro-wireless-headset',
        'category': cats_dict['gaming-headsets'],
        'sku': 'AUD-SS-NOVA',
        'price': Decimal('349.99'),
        'discount_price': Decimal('319.99'),
        'stock': 18,
        'low_stock_threshold': 4,
        'short_description': 'Nova Pro Acoustic System, Active Noise Cancellation, and Infinity Power hot-swap dual battery station.',
        'description': (
            "Almighty audio paired with pro-grade dual wireless connectivity. Features premium high-fidelity drivers, "
            "active background noise cancellation, ClearCast Gen 2 AI-powered bidirectional microphone, and hot-swappable dual batteries.\n\n"
            "Key Specifications:\n"
            "• Drivers: 40mm Neodymium Hi-Res Certified (10–40,000 Hz)\n"
            "• Wireless: Simultaneous 2.4GHz Quantum 2.0 + Bluetooth 5.0\n"
            "• Battery: Dual batteries (44 hours total runtime with hot-swapping)\n"
            "• DAC: Multi-System OLED Wireless Base Station with 10-band EQ"
        ),
        'is_featured': True,
        'variants': [
            ('System Compatibility', 'PC & PlayStation Edition', 'AUD-NOVA-PS', Decimal('0.00'), 10),
            ('System Compatibility', 'Multi-System Xbox & PC Edition', 'AUD-NOVA-XBX', Decimal('0.00'), 8),
        ],
        'review': ('Hot swappable batteries make you never plug in a cable', 5, 'Soundstage in Warzone and Apex is pinpoint accurate. The base station dial is super handy.', customer2)
    },
    {
        'name': 'Secretlab TITAN Evo Ergonomic Esports Gaming Chair',
        'slug': 'secretlab-titan-evo-esports-gaming-chair',
        'category': cats_dict['gaming-chairs-desks'],
        'sku': 'CHR-SEC-EVO',
        'price': Decimal('549.00'),
        'discount_price': Decimal('499.00'),
        'stock': 12,
        'low_stock_threshold': 3,
        'short_description': 'Pebble seat base, 4-way L-ADAPT lumbar support system, and magnetic memory foam head pillow.',
        'description': (
            "The undisputed benchmark in gaming chairs. Engineered to support full-body posture during marathon gaming "
            "sessions with proprietary cold-cure foam, magnetic CloudSwap armrests, and 165° full-length recline.\n\n"
            "Key Specifications:\n"
            "• Upholstery: Secretlab NEO Hybrid Leatherette\n"
            "• Lumbar Support: 4-Way L-ADAPT integrated internal mechanism\n"
            "• Wheelbase: ADC12 Reinforced Aluminum\n"
            "• Recline: 85° to 165° multi-tilt mechanism\n"
            "• Recommended Size: Regular (170 - 189 cm / < 100 kg)"
        ),
        'is_featured': False,
        'variants': [
            ('Upholstery Material', 'Stealth Neo Hybrid Leatherette', 'CHR-EVO-STH', Decimal('0.00'), 7),
            ('Upholstery Material', 'SoftWeave Plus Frost Blue', 'CHR-EVO-SWV', Decimal('20.00'), 5),
        ],
        'review': ('No more back pain after 10hr sessions', 5, 'The built-in lumbar dial fits your lower back perfectly. Sturdy and premium materials throughout.', customer1)
    },
    {
        'name': 'Shure MV7X Dynamic Broadcast Streaming Microphone',
        'slug': 'shure-mv7x-streaming-microphone',
        'category': cats_dict['streaming-audio'],
        'sku': 'MIC-SHR-MV7X',
        'price': Decimal('249.00'),
        'discount_price': Decimal('219.00'),
        'stock': 20,
        'low_stock_threshold': 4,
        'short_description': 'Voice Isolation Technology with cardioid polar pattern for studio-grade streaming and podcasts.',
        'description': (
            "Get pro-grade vocal clarity in any room. The MV7X utilizes voice isolation dynamic cartridge design "
            "to reject ambient keyboard clicks, fan hums, and room reverberation for pristine stream broadcast audio.\n\n"
            "Key Specifications:\n"
            "• Transducer Type: Dynamic (moving coil)\n"
            "• Polar Pattern: Unidirectional (Cardioid)\n"
            "• Frequency Response: 50 Hz to 16,000 Hz\n"
            "• Output Impedance: 252 Ω at 1 kHz\n"
            "• Connector: 3-pin XLR male standard broadcast format"
        ),
        'is_featured': False,
        'variants': [
            ('Colorway', 'Matte Black', 'MIC-MV7X-BLK', Decimal('0.00'), 15),
            ('Colorway', 'Brushed Silver Limited', 'MIC-MV7X-SLV', Decimal('15.00'), 5),
        ],
        'review': ('Broadcast radio voice on Discord and Twitch', 5, 'Completely eliminates background noise from my mechanical keyboard even without RTX Voice.', customer2)
    },
]

print("\nCreating Products, Variants, Images, and Reviews...")
for p_data in products_data:
    variants_list = p_data.pop('variants', [])
    review_info = p_data.pop('review', None)
    slug = p_data['slug']

    prod, pcreated = Product.objects.get_or_create(slug=slug, defaults=p_data)
    if not pcreated:
        # Update existing
        for k, v in p_data.items():
            setattr(prod, k, v)
        prod.save()
        print(f"Updated product: {prod.name}")
    else:
        print(f"Created product: {prod.name}")

    # Inventory transaction
    if prod.stock > 0 and not InventoryTransaction.objects.filter(product=prod).exists():
        InventoryTransaction.objects.create(
            product=prod,
            change_type=TransactionType.RESTOCK,
            quantity=prod.stock,
            previous_stock=0,
            new_stock=prod.stock,
            note='Initial catalog stock replenishment for gaming gear',
            created_by=admin_user
        )

    # Image
    rel_img_path = f'products/{slug}.jpg'
    full_img_path = os.path.join(media_products_dir, f'{slug}.jpg')
    if os.path.exists(full_img_path):
        pimg, _ = ProductImage.objects.get_or_create(
            product=prod,
            image=rel_img_path,
            defaults={'alt_text': prod.name, 'is_primary': True, 'order': 1}
        )
        pimg.is_primary = True
        pimg.save()
        print(f" -> Assigned image: {rel_img_path}")

    # Variants
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

    # Review
    if review_info:
        rtitle, rrating, rcomment, ruser = review_info
        if ruser:
            Review.objects.get_or_create(
                product=prod,
                user=ruser,
                defaults={
                    'title': rtitle,
                    'rating': rrating,
                    'comment': rcomment,
                    'is_approved': True
                }
            )

print("\nSUCCESS: All gaming accessories and PC hardware added!")

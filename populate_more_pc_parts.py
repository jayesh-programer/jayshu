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
pc_components_cat = Category.objects.get(slug='pc-components')

sub_cats = [
    ('Power Supplies (PSUs)', 'power-supplies', pc_components_cat),
    ('Gaming PC Cases', 'pc-cases', pc_components_cat),
    ('High-Speed NVMe SSDs', 'storage-ssds', pc_components_cat),
]

cats_dict = {
    'graphics-cards': Category.objects.get(slug='graphics-cards'),
    'processors-cpus': Category.objects.get(slug='processors-cpus'),
    'motherboards': Category.objects.get(slug='motherboards'),
    'cooling-cases': Category.objects.get(slug='cooling-cases'),
    'memory-storage': Category.objects.get(slug='memory-storage'),
}

for name, slug, parent in sub_cats:
    cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'parent': parent})
    cats_dict[slug] = cat

# 2. Products Data
products_data = [
    {
        'name': 'Samsung 990 PRO 2TB PCIe 4.0 NVMe M.2 SSD with Heatsink',
        'slug': 'samsung-990-pro-2tb-nvme-ssd',
        'category': cats_dict['storage-ssds'],
        'sku': 'SSD-SAM-990P-2TB',
        'price': Decimal('189.99'),
        'discount_price': Decimal('169.99'),
        'stock': 45,
        'low_stock_threshold': 8,
        'short_description': 'Sequential read/write speeds up to 7,450/6,900 MB/s with integrated thermal control heatsink.',
        'description': (
            "Reach maximum gaming performance with PCIe 4.0 speeds. Powered by Samsung's in-house controller and V-NAND technology, "
            "the 990 PRO delivers lightning-fast level load times and sustained thermals compatible with PC and PlayStation 5.\n\n"
            "Key Specifications:\n"
            "• Capacity: 2TB\n"
            "• Interface: PCIe Gen 4.0 x4, NVMe 2.0\n"
            "• Sequential Read: Up to 7,450 MB/s\n"
            "• Sequential Write: Up to 6,900 MB/s\n"
            "• Form Factor: M.2 2280 with low-profile integrated heatsink\n"
            "• TBW Endurance: 1,200 TBW"
        ),
        'is_featured': True,
        'variants': [
            ('Capacity', '2TB with Heatsink', 'SSD-990P-2TB-HS', Decimal('0.00'), 30),
            ('Capacity', '4TB with Heatsink', 'SSD-990P-4TB-HS', Decimal('140.00'), 15),
        ],
        'review': ('Blazing fast game load times', 5, 'Games load almost instantly in Starfield and Cyberpunk. Heatsink keeps it under 52C under intense writes.', customer1)
    },
    {
        'name': 'Crucial T700 2TB PCIe 5.0 NVMe M.2 SSD (12,400 MB/s)',
        'slug': 'crucial-t700-2tb-pcie5-nvme-ssd',
        'category': cats_dict['storage-ssds'],
        'sku': 'SSD-CRU-T700-2TB',
        'price': Decimal('299.99'),
        'discount_price': Decimal('269.99'),
        'stock': 20,
        'low_stock_threshold': 4,
        'short_description': 'Extreme next-gen PCIe Gen5 performance with read speeds up to 12,400 MB/s and custom aluminum heatsink.',
        'description': (
            "Experience the pinnacle of Gen5 storage. Built with Micron 232-layer TLC NAND and Phison E26 controller, "
            "the Crucial T700 is nearly double the speed of Gen4 SSDs for seamless 8K video scrubbing and instantaneous asset streaming.\n\n"
            "Key Specifications:\n"
            "• Capacity: 2TB\n"
            "• Interface: PCIe Gen 5.0 x4, NVMe 2.0\n"
            "• Sequential Read: Up to 12,400 MB/s\n"
            "• Sequential Write: Up to 11,800 MB/s\n"
            "• Cooling: Extruded aluminum and copper heatsink\n"
            "• Microsoft DirectStorage Supported"
        ),
        'is_featured': True,
        'variants': [
            ('Cooling Option', 'With Premium Heatsink', 'SSD-T700-HS', Decimal('0.00'), 14),
            ('Cooling Option', 'Non-Heatsink (Motherboard M.2 Cover)', 'SSD-T700-NOHS', Decimal('-20.00'), 6),
        ],
        'review': ('Unbelievable Gen 5 bandwidth', 5, 'CrystalDiskMark benched over 12,380 MB/s on my X670E motherboard. The future of PC storage.', customer2)
    },
    {
        'name': 'Corsair RM1000x Shift 1000W 80 PLUS Gold ATX 3.0 PSU',
        'slug': 'corsair-rm1000x-shift-1000w-modular-psu',
        'category': cats_dict['power-supplies'],
        'sku': 'PSU-COR-RM1000X',
        'price': Decimal('209.99'),
        'discount_price': Decimal('189.99'),
        'stock': 28,
        'low_stock_threshold': 5,
        'short_description': 'Innovative side-mounted modular connector interface, ATX 3.0 certified with native PCIe 5.0 12VHPWR cable.',
        'description': (
            "Corsair RMx SHIFT Series fully modular power supplies boast a revolutionary side cable interface to keep all connections "
            "within quick reach for effortless clean cable management. Equipped with 105°C Japanese electrolytic capacitors.\n\n"
            "Key Specifications:\n"
            "• Wattage: 1000 Watts\n"
            "• Efficiency: 80 PLUS Gold Certified\n"
            "• Standard: ATX 3.0 & PCIe 5.0 Compliant (native 12VHPWR cable included)\n"
            "• Fan: 140mm fluid dynamic bearing with Zero RPM mode\n"
            "• Warranty: 10 Years Manufacturer Guarantee"
        ),
        'is_featured': False,
        'variants': [
            ('Wattage', '1000W 80+ Gold', 'PSU-RM1000X', Decimal('0.00'), 20),
            ('Wattage', '1200W 80+ Gold', 'PSU-RM1200X', Decimal('40.00'), 8),
        ],
        'review': ('Side connectors make cable routing a breeze', 5, 'The side interface in my O11 case made plugging in GPU cables so convenient. Whisper silent even while pulling 600W.', customer1)
    },
    {
        'name': 'Lian Li O11 Dynamic EVO RGB Dual-Chamber PC Case',
        'slug': 'lian-li-o11-dynamic-evo-rgb-pc-case',
        'category': cats_dict['pc-cases'],
        'sku': 'CAS-LL-O11DEVO',
        'price': Decimal('179.99'),
        'discount_price': Decimal('159.99'),
        'stock': 22,
        'low_stock_threshold': 4,
        'short_description': 'Dual-chamber showpiece chassis with panoramic glass, reversible layout, and integrated diffused dual ARGB strips.',
        'description': (
            "The iconic O11 Dynamic EVO RGB elevates PC building aesthetics. Features removable corner pillar for unobstructed "
            "dual-tempered glass views, reversible chassis orientation (left or right desk side), and dual L-shaped diffused ARGB lighting.\n\n"
            "Key Specifications:\n"
            "• Dimensions: 478mm (D) x 290mm (W) x 471mm (H)\n"
            "• Radiator Support: Top 420/360mm, Side 360/280mm, Bottom 360mm\n"
            "• GPU Clearance: Up to 455mm length\n"
            "• Drive Support: 4x 2.5” SSD or 2x 3.5” HDD\n"
            "• Materials: 4mm Tempered Glass, Brushed Aluminum, Steel"
        ),
        'is_featured': True,
        'variants': [
            ('Color', 'Stealth Matte Black', 'CAS-O11-BLK', Decimal('0.00'), 14),
            ('Color', 'Pure Snow White', 'CAS-O11-WHT', Decimal('10.00'), 8),
        ],
        'review': ('The cleanest PC building experience ever', 5, 'Removing the front corner pillar creates a fish-tank look that showcases custom liquid cooling loops like nothing else.', customer2)
    },
    {
        'name': 'HYTE Y70 Touch Panoramic Glass PC Case with 4K Touchscreen',
        'slug': 'hyte-y70-touch-panoramic-glass-pc-case',
        'category': cats_dict['pc-cases'],
        'sku': 'CAS-HYTE-Y70',
        'price': Decimal('359.99'),
        'discount_price': Decimal('339.99'),
        'stock': 14,
        'low_stock_threshold': 3,
        'short_description': 'Modern aesthetic 3-piece panoramic glass chassis with integrated 14.1” 4K 60Hz 10-point capacitive touchscreen.',
        'description': (
            "Transform your PC into an interactive command center. The HYTE Y70 Touch features a stunning 14.1” 4K capacitive "
            "touchscreen display on the corner pillar powered by HYTE Nexus software for live widgets, animations, and system stats.\n\n"
            "Key Specifications:\n"
            "• Integrated Display: 14.1” IPS Touchscreen (1100 x 3840 4K, 60Hz, 10-point multi-touch)\n"
            "• Included Riser: Luxury PCIe 4.0 x16 vertical GPU cable with color-matched canopy\n"
            "• GPU Clearance: 4-slot vertical GPU mounting (up to 390mm length)\n"
            "• Radiator Support: Up to 360mm on top and side\n"
            "• Glass: 3-piece panoramic panoramic viewing window"
        ),
        'is_featured': True,
        'variants': [
            ('Color Theme', 'Snow White', 'CAS-Y70-WHT', Decimal('0.00'), 8),
            ('Color Theme', 'Pitch Black', 'CAS-Y70-BLK', Decimal('0.00'), 6),
        ],
        'review': ('Worth every single dollar', 5, 'The touchscreen display running live CPU/GPU temps, Discord, and animated Spotify widgets turns heads every time friends walk in.', customer1)
    },
    {
        'name': 'Intel Core i9-14900KS 24-Core 6.2 GHz Special Edition CPU',
        'slug': 'intel-core-i9-14900ks-special-edition-processor',
        'category': cats_dict['processors-cpus'],
        'sku': 'CPU-INT-14900KS',
        'price': Decimal('689.00'),
        'discount_price': Decimal('649.00'),
        'stock': 16,
        'low_stock_threshold': 3,
        'short_description': 'The world’s fastest desktop processor with 24 cores (8P + 16E) reaching an unprecedented 6.2 GHz out of the box.',
        'description': (
            "Unleash blistering clock speeds with the Intel Core i9-14900KS Special Edition. Featuring 24 cores and 32 threads, "
            "Intel Thermal Velocity Boost pushes single-core frequencies past 6.2 GHz for uncompromising competitive frame rates.\n\n"
            "Key Specifications:\n"
            "• Cores / Threads: 24 Cores (8 Performance + 16 Efficient) / 32 Threads\n"
            "• Max Turbo Frequency: Up to 6.2 GHz\n"
            "• Intel Smart Cache (L3): 36MB\n"
            "• Socket: LGA 1700 (Intel 700 & 600 Series Motherboards)\n"
            "• Packaging: Special Edition Collector Wafer Display Tin"
        ),
        'is_featured': True,
        'variants': [
            ('Packaging', 'Special Edition Collector Wafer Tin', 'CPU-14900KS-BOX', Decimal('0.00'), 16),
        ],
        'review': ('6.2 GHz out of the box is real', 5, 'Hit 6.2 GHz on single thread effortlessly paired with a 360mm AIO. Single-core benchmark champion.', customer2)
    },
    {
        'name': 'AMD Radeon RX 7900 XTX 24GB GDDR6 Gaming Graphics Card',
        'slug': 'amd-radeon-rx-7900-xtx-24gb-graphics-card',
        'category': cats_dict['graphics-cards'],
        'sku': 'GPU-AMD-7900XTX',
        'price': Decimal('999.99'),
        'discount_price': Decimal('929.99'),
        'stock': 18,
        'low_stock_threshold': 4,
        'short_description': 'Groundbreaking AMD RDNA 3 chiplet architecture with 24GB GDDR6, DisplayPort 2.1, and AMD HYPR-RX.',
        'description': (
            "Experience flagship 4K rasterization performance. Built on the revolutionary chiplet GPU design, the AMD Radeon RX 7900 XTX "
            "delivers 24GB of high-speed GDDR6 memory, 96 compute units, and next-generation DisplayPort 2.1 high-refresh monitor support.\n\n"
            "Key Specifications:\n"
            "• Compute Units / Stream Processors: 96 CUs / 6,144 Stream Processors\n"
            "• VRAM: 24GB GDDR6 384-bit memory\n"
            "• Boost Clock: Up to 2500 MHz\n"
            "• Video Outputs: 1x HDMI 2.1a, 2x DisplayPort 2.1, 1x USB-C\n"
            "• Power Connectors: Standard 2x 8-pin PCIe (No 12VHPWR adapter needed)"
        ),
        'is_featured': True,
        'variants': [
            ('Edition', 'Reference RDNA 3 Black Edition', 'GPU-7900XTX-REF', Decimal('0.00'), 12),
            ('Edition', 'Custom Triple-Fan OC Edition', 'GPU-7900XTX-OC', Decimal('40.00'), 6),
        ],
        'review': ('Unmatched 4K rasterization value', 5, '24GB VRAM means never worrying about texture memory allocation. DisplayPort 2.1 drives my 4K 240Hz monitor natively.', customer1)
    },
    {
        'name': 'G.SKILL Trident Z5 RGB 64GB (2x32GB) DDR5-6400 CL32 RAM',
        'slug': 'gskill-trident-z5-rgb-64gb-ddr5-6400',
        'category': cats_dict['memory-storage'],
        'sku': 'RAM-GSK-Z5-64G',
        'price': Decimal('229.99'),
        'discount_price': Decimal('209.99'),
        'stock': 26,
        'low_stock_threshold': 5,
        'short_description': 'High-capacity 64GB DDR5 memory kit with tight CL32 timings and streamlined translucent RGB light bar.',
        'description': (
            "Trident Z5 RGB DDR5 memory is designed for ultra-high performance on DDR5 platforms. Featuring a sleek and streamlined "
            "aluminum heatspreader design available in metallic silver or matte black with customizable RGB lighting.\n\n"
            "Key Specifications:\n"
            "• Capacity: 64GB (2 x 32GB)\n"
            "• Tested Speed: DDR5-6400 MT/s\n"
            "• Tested Latency: CL32-39-39-102\n"
            "• Voltage: 1.40V\n"
            "• Profile: Intel XMP 3.0 & AMD EXPO Support"
        ),
        'is_featured': False,
        'variants': [
            ('Colorway', 'Matte Black Aluminum', 'RAM-Z5-BLK', Decimal('0.00'), 16),
            ('Colorway', 'Metallic Silver Aluminum', 'RAM-Z5-SLV', Decimal('0.00'), 10),
        ],
        'review': ('64GB with zero stability issues', 5, 'Loaded XMP 6400MHz with zero tweaking required. Perfect for heavy video editing and modded flight sims.', customer2)
    },
    {
        'name': 'Lian Li UNI FAN SL-INFINITY 120 RGB Triple Pack with Controller',
        'slug': 'lian-li-uni-fan-sl-infinity-120-rgb-3pack',
        'category': cats_dict['cooling-cases'],
        'sku': 'FAN-LL-SLINF-3PK',
        'price': Decimal('99.99'),
        'discount_price': Decimal('89.99'),
        'stock': 35,
        'low_stock_threshold': 6,
        'short_description': 'Daisy-chain magnetic interlocking 120mm fans with mesmerizing infinity mirror center hub and edge rings.',
        'description': (
            "Eliminate messy cable clutter. Lian Li SL-Infinity 120 fans interlock seamlessly with pin-to-pin contact points, "
            "allowing up to 4 fans in a cluster using a single cable. Features 40 individual LEDs per fan and multi-layer infinity mirrors.\n\n"
            "Key Specifications:\n"
            "• Quantity: 3x 120mm fans + L-Connect 3 Controller hub\n"
            "• Fan Speed: 200 ~ 2,100 RPM (PWM)\n"
            "• Airflow: 61.3 CFM\n"
            "• Static Pressure: 2.66 mmH2O\n"
            "• Noise Level: 29 dB(A) max"
        ),
        'is_featured': False,
        'variants': [
            ('Color', 'Black with Controller', 'FAN-SLINF-BLK', Decimal('0.00'), 20),
            ('Color', 'White with Controller', 'FAN-SLINF-WHT', Decimal('0.00'), 15),
        ],
        'review': ('The cleanest fan installation ever made', 5, 'Daisy-chaining 9 fans in my case with just 3 total cables is a miracle. The infinity mirror depth looks gorgeous.', customer1)
    },
    {
        'name': 'Noctua NH-D15 chromax.black Dual-Tower Premium Air Cooler',
        'slug': 'noctua-nh-d15-chromax-black-cpu-cooler',
        'category': cats_dict['cooling-cases'],
        'sku': 'CLR-NOC-D15-BLK',
        'price': Decimal('119.95'),
        'discount_price': Decimal('109.95'),
        'stock': 24,
        'low_stock_threshold': 5,
        'short_description': 'Award-winning flagship dual-tower heatsink with two NF-A15 140mm PWM fans in stealth all-black design.',
        'description': (
            "The king of air cooling. The NH-D15 chromax.black combines supreme quiet cooling performance with a sleek stealth black look. "
            "Equipped with 6 heatpipes, dual heatsink towers, SecuFirm2 mounting system, and legendary NT-H1 thermal compound.\n\n"
            "Key Specifications:\n"
            "• Heatsink Type: Dual-Tower with 6 Copper Heatpipes\n"
            "• Fans Included: 2x NF-A15 HS-PWM chromax.black 140mm fans\n"
            "• Acoustic Noise: Max 24.6 dB(A)\n"
            "• Socket Compatibility: Intel LGA1700/1200/115x & AMD AM5/AM4\n"
            "• Warranty: 6 Years Full Manufacturer Warranty"
        ),
        'is_featured': False,
        'variants': [
            ('Finish', 'All-Black chromax.black Edition', 'CLR-D15-BLK', Decimal('0.00'), 24),
        ],
        'review': ('Outperforms many 240mm liquid coolers silently', 5, 'Zero pump noise, zero risk of leaks, and cools my 14700K below 75C under full gaming load. Built to last a decade.', customer2)
    },
]

image_map = {
    'samsung-990-pro-2tb-nvme-ssd': 'samsung_990pro_commercial_1793022605639.jpg',
    'crucial-t700-2tb-pcie5-nvme-ssd': 'crucial_t700_commercial_png_1793022605323.jpg',
    'corsair-rm1000x-shift-1000w-modular-psu': 'corsair_rm1000x_commercial_1793022606487.jpg',
    'lian-li-o11-dynamic-evo-rgb-pc-case': 'lianli_o11_commercial_1793022604266.jpg',
    'gskill-trident-z5-rgb-64gb-ddr5-6400': 'gskill_trident_commercial_1793022618096.jpg',
}

print("\nCopying studio photographs from brain directory...")
for slug, src_name in image_map.items():
    src_file = os.path.join(brain_dir, src_name)
    dst_file = os.path.join(media_products_dir, f'{slug}.jpg')
    if os.path.exists(src_file):
        shutil.copy2(src_file, dst_file)
        print(f"Copied image for {slug}: {os.path.getsize(dst_file)} bytes")
    else:
        print(f"WARNING: source image not found: {src_file}")

print("\nInserting Products, Variants, Images, Inventory, and Reviews...")
for p_data in products_data:
    variants_list = p_data.pop('variants', [])
    review_info = p_data.pop('review', None)
    slug = p_data['slug']

    prod, pcreated = Product.objects.get_or_create(slug=slug, defaults=p_data)
    if not pcreated:
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
            note='Initial stock allocation for PC hardware parts',
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
        print(f" -> Image assigned: {rel_img_path} ({os.path.getsize(full_img_path)} bytes)")
    else:
        print(f" -> ERROR: Missing image at {full_img_path}")

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

print("\nSUCCESS: All gaming PC parts successfully added to database!")

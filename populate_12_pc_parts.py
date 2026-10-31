import os
import math
import django
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from catalog.models import Category, Product, ProductVariant, ProductImage, Review
from inventory.models import InventoryTransaction, TransactionType

media_dir = r"C:\Users\Kartik\.gemini\antigravity\scratch\ecommerce\media\products"
os.makedirs(media_dir, exist_ok=True)

admin_user = User.objects.filter(is_superuser=True).first()
customer1 = User.objects.filter(username='customer1').first()
customer2 = User.objects.filter(username='customer2').first()

# ==========================================
# 1. IMAGE RENDERING ENGINE (Pillow 1000x1000)
# ==========================================

def create_radial_gradient(W, H, center_color, edge_color):
    base = Image.new('RGB', (W, H), center_color)
    top = Image.new('RGB', (W, H), edge_color)
    mask = Image.new('L', (W, H))
    mask_data = []
    cx, cy = W / 2, H / 2
    max_d = math.sqrt(cx**2 + cy**2)
    for y in range(H):
        for x in range(W):
            d = math.sqrt((x - cx)**2 + (y - cy)**2)
            mask_data.append(int(255 * min(1.0, d / max_d)))
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def draw_circuit_grid(draw, W, H, step=45, color=(25, 32, 45)):
    for x in range(0, W, step):
        draw.line([(x, 0), (x, H)], fill=color, width=1)
    for y in range(0, H, step):
        draw.line([(0, y), (W, y)], fill=color, width=1)

def render_image(slug, title, subtitle, specs_badge, primary_color, accent_color, shape_fn):
    W, H = 1000, 1000
    img = create_radial_gradient(W, H, primary_color, (8, 10, 14))
    draw = ImageDraw.Draw(img)
    draw_circuit_grid(draw, W, H)

    # Ambient backglow
    draw.ellipse([200, 200, 800, 700], fill=accent_color, outline=None)
    # Re-blend center gradient for soft glow
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)

    # Invoke custom hardware shape drawing
    shape_fn(draw, ov_draw, W, H)
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Specs Card Badge at bottom
    draw.rounded_rectangle([140, 780, 860, 920], radius=18, fill=(14, 18, 26), outline=accent_color, width=2)
    draw.text((180, 805), title.upper(), fill=(255, 255, 255))
    draw.text((180, 845), subtitle, fill=(180, 195, 215))
    draw.text((180, 880), specs_badge, fill=accent_color)

    # Top Brand / Type Pill
    draw.rounded_rectangle([80, 80, 320, 130], radius=12, fill=accent_color)
    draw.text((105, 95), "PRO HARDWARE", fill=(255, 255, 255))

    out_path = os.path.join(media_dir, f"{slug}.jpg")
    img.save(out_path, quality=95)
    print(f"Generated photo: {out_path} ({os.path.getsize(out_path)} bytes)")
    return out_path

# ==========================================
# 2. PRODUCT HARDWARE SHAPE DEFINITIONS
# ==========================================

# 1. RTX 4080 Super Founders Edition
def draw_rtx4080s(draw, ov, W, H):
    # Iconic hourglass dual-flow-through shroud
    draw.rounded_rectangle([200, 310, 800, 620], radius=35, fill=(30, 32, 36), outline=(120, 190, 32), width=3)
    draw.rounded_rectangle([240, 340, 760, 590], radius=25, fill=(20, 22, 25), outline=(70, 75, 80), width=2)
    # Axial fan
    draw.ellipse([310, 370, 510, 570], fill=(12, 14, 16), outline=(120, 190, 32), width=3)
    draw.ellipse([385, 445, 435, 495], fill=(35, 38, 42), outline=(150, 210, 40), width=2)
    # Flow-through heatsink fins on right
    for x in range(560, 740, 12):
        draw.line([(x, 370), (x, 560)], fill=(80, 85, 95), width=3)
    draw.text((250, 320), "GEFORCE RTX 4080 SUPER", fill=(120, 190, 32))

# 2. MSI RTX 4070 Ti SUPER Gaming X Slim
def draw_msi_4070ti(draw, ov, W, H):
    # TRI FROZR 3 Triple-fan Shroud
    draw.rounded_rectangle([160, 330, 840, 600], radius=20, fill=(26, 26, 30), outline=(230, 0, 40), width=3)
    for fx in (280, 500, 720):
        draw.ellipse([fx-80, 465-80, fx+80, 465+80], fill=(16, 16, 18), outline=(220, 20, 50), width=2)
        draw.ellipse([fx-25, 465-25, fx+25, 465+25], fill=(35, 35, 40), outline=(255, 80, 90), width=2)
    # Dragon claw RGB accents
    draw.polygon([(460, 350), (480, 335), (540, 350), (520, 365)], fill=(255, 30, 50))
    draw.text((200, 345), "MSI GAMING X SLIM", fill=(255, 255, 255))

# 3. Intel Core i7-14700K
def draw_i7_14700k(draw, ov, W, H):
    # Box & IHS
    draw.rounded_rectangle([250, 240, 750, 660], radius=30, fill=(12, 40, 85), outline=(0, 150, 255), width=3)
    draw.rounded_rectangle([360, 330, 640, 570], radius=15, fill=(185, 200, 220), outline=(240, 248, 255), width=3)
    draw.text((395, 365), "intel.", fill=(0, 90, 200))
    draw.text((395, 405), "CORE i7", fill=(15, 25, 45))
    draw.text((395, 450), "14700K", fill=(15, 25, 45))
    draw.text((395, 495), "5.6 GHz TURBO", fill=(60, 80, 110))

# 4. AMD Ryzen 9 7950X3D
def draw_ryzen9_7950x3d(draw, ov, W, H):
    # AM5 IHS with 3D V-Cache emblem
    draw.rounded_rectangle([250, 240, 750, 660], radius=30, fill=(40, 20, 12), outline=(255, 100, 20), width=3)
    draw.rounded_rectangle([350, 320, 650, 580], radius=18, fill=(190, 200, 215), outline=(255, 120, 30), width=3)
    draw.text((390, 360), "AMD RYZEN 9", fill=(220, 60, 10))
    draw.text((390, 405), "7950X3D", fill=(20, 25, 30))
    draw.text((390, 455), "16-CORE / 32-THREAD", fill=(40, 45, 55))
    draw.text((390, 500), "144MB 3D V-CACHE", fill=(220, 70, 15))

# 5. MSI MAG B650 Tomahawk WiFi
def draw_b650_tomahawk(draw, ov, W, H):
    # All black military VRM heatsinks
    draw.rounded_rectangle([200, 220, 800, 680], radius=15, fill=(24, 26, 28), outline=(0, 210, 180), width=3)
    # VRM Armor
    draw.rectangle([230, 250, 450, 380], fill=(36, 40, 45), outline=(60, 70, 80), width=2)
    draw.text((250, 290), "MAG B650", fill=(0, 220, 190))
    draw.text((250, 325), "TOMAHAWK", fill=(255, 255, 255))
    # AM5 Socket
    draw.rectangle([480, 300, 660, 480], fill=(45, 48, 55), outline=(100, 110, 125), width=2)
    # PCIe 4.0 Steel Slot
    draw.rectangle([250, 540, 750, 575], fill=(70, 75, 85), outline=(180, 190, 205), width=2)

# 6. GIGABYTE Z790 AORUS Master X
def draw_z790_aorus(draw, ov, W, H):
    # Futuristic AORUS Eagle Shroud
    draw.rounded_rectangle([200, 220, 800, 680], radius=15, fill=(22, 24, 30), outline=(255, 120, 0), width=3)
    draw.polygon([(240, 250), (460, 250), (400, 380), (240, 380)], fill=(32, 36, 45), outline=(255, 140, 20), width=2)
    draw.text((260, 280), "Z790 AORUS", fill=(255, 120, 0))
    draw.text((260, 315), "MASTER X", fill=(255, 255, 255))
    draw.text((260, 345), "WIFI 7 READY", fill=(0, 200, 255))
    # M.2 Thermal Guard
    draw.rectangle([260, 530, 740, 580], fill=(40, 45, 55), outline=(255, 140, 0), width=2)

# 7. WD_BLACK SN850X 4TB NVMe SSD
def draw_wd_sn850x(draw, ov, W, H):
    # Industrial rugged M.2 Heatsink
    draw.rounded_rectangle([220, 360, 780, 560], radius=12, fill=(15, 15, 18), outline=(255, 140, 0), width=3)
    # Screws
    for sx in (245, 755):
        draw.ellipse([sx-10, 450, sx+10, 470], fill=(80, 85, 95), outline=(180, 185, 195), width=1)
    draw.text((290, 395), "WD_BLACK™ SN850X NVMe™ SSD", fill=(255, 255, 255))
    draw.text((290, 440), "4TB PCIe Gen4 x4  |  7,300 MB/s", fill=(255, 140, 0))
    draw.text((290, 485), "GAME MODE 2.0  |  SANDISK 3D NAND", fill=(160, 175, 195))

# 8. Seasonic VERTEX GX-1200 PSU
def draw_seasonic_1200(draw, ov, W, H):
    # Heavy-duty power supply
    draw.rounded_rectangle([250, 270, 750, 670], radius=20, fill=(24, 25, 28), outline=(245, 190, 30), width=3)
    # Fan grille
    draw.ellipse([340, 330, 660, 610], fill=(16, 17, 20), outline=(230, 180, 25), width=3)
    draw.ellipse([460, 430, 540, 510], fill=(35, 36, 40), outline=(250, 200, 30), width=2)
    draw.text((370, 300), "SEASONIC VERTEX GX-1200", fill=(245, 190, 30))
    draw.text((435, 625), "80 PLUS GOLD ATX 3.0", fill=(255, 255, 255))

# 9. Corsair 5000D Airflow Case
def draw_corsair_5000d(draw, ov, W, H):
    # Front triangular mesh cutouts & tempered glass
    draw.rounded_rectangle([260, 200, 740, 720], radius=18, fill=(28, 30, 34), outline=(240, 210, 0), width=3)
    draw.rectangle([290, 240, 560, 680], fill=(38, 42, 48), outline=(100, 110, 125), width=2)
    # Front airflow mesh pattern
    for y in range(250, 670, 22):
        draw.line([(580, y), (710, y)], fill=(80, 85, 95), width=4)
    draw.text((310, 260), "CORSAIR 5000D", fill=(240, 210, 0))
    draw.text((310, 290), "HIGH-AIRFLOW CHASSIS", fill=(255, 255, 255))

# 10. Fractal Design North Charcoal Walnut Case
def draw_fractal_north(draw, ov, W, H):
    # Modern Scandinavian styling with walnut slats
    draw.rounded_rectangle([270, 200, 730, 720], radius=15, fill=(25, 25, 28), outline=(200, 140, 70), width=3)
    # Real walnut wood slats
    for x in range(300, 700, 32):
        draw.rectangle([x, 240, x+20, 680], fill=(165, 105, 55), outline=(125, 75, 35), width=1)
    draw.rounded_rectangle([80, 80, 320, 130], radius=12, fill=(185, 115, 60))
    draw.text((105, 95), "NATURAL WALNUT", fill=(255, 255, 255))
    draw.text((330, 215), "FRACTAL DESIGN NORTH", fill=(230, 180, 130))

# 11. ARCTIC Liquid Freezer III 360 A-RGB Cooler
def draw_arctic_freezer3(draw, ov, W, H):
    # Massive 38mm thick radiator + VRM cooling fan
    draw.rounded_rectangle([200, 260, 800, 420], radius=15, fill=(20, 22, 26), outline=(0, 220, 255), width=3)
    for fx in (300, 500, 700):
        draw.ellipse([fx-65, 340-65, fx+65, 340+65], fill=(12, 14, 18), outline=(0, 220, 255), width=3)
    # Pump with VRM centrifugal fan
    draw.rounded_rectangle([420, 480, 580, 640], radius=20, fill=(30, 34, 40), outline=(0, 240, 255), width=3)
    draw.ellipse([460, 520, 540, 600], fill=(15, 18, 24), outline=(0, 255, 220), width=2)
    # Braided tubes
    draw.line([(350, 420), (450, 500)], fill=(70, 80, 95), width=10)
    draw.line([(650, 420), (550, 500)], fill=(70, 80, 95), width=10)
    draw.text((230, 275), "ARCTIC LIQUID FREEZER III 360", fill=(0, 240, 255))

# 12. TeamGroup T-Force Delta RGB DDR5 RAM
def draw_teamgroup_delta(draw, ov, W, H):
    # Two angular stealth sticks with wide 120° RGB top
    for rx in (340, 540):
        draw.polygon([(rx, 260), (rx+140, 260), (rx+140, 650), (rx, 650)], fill=(28, 30, 36), outline=(255, 0, 160), width=2)
        # 120-degree wide diffused RGB diffuser
        draw.polygon([(rx-10, 260), (rx+150, 260), (rx+130, 320), (rx+10, 320)], fill=(255, 40, 180))
        draw.text((rx+15, 420), "T-FORCE", fill=(255, 255, 255))
        draw.text((rx+25, 460), "DELTA", fill=(255, 40, 180))
        draw.text((rx+28, 500), "DDR5", fill=(0, 230, 255))

# ==========================================
# 3. 12 GAMING PC PARTS DATA CATALOG
# ==========================================

parts_data = [
    {
        'slug': 'geforce-rtx-4080-super-founders-edition',
        'title': 'NVIDIA GeForce RTX 4080 Super Founders Edition',
        'subtitle': '16GB GDDR6X  |  10,240 CUDA Cores  |  Ada Lovelace',
        'specs_badge': 'Dual-Slot Flow-Through Thermal Design  |  DLSS 3.5 Frame Gen',
        'cat_slug': 'graphics-cards',
        'name': 'NVIDIA GeForce RTX 4080 Super 16GB Founders Edition',
        'sku': 'GPU-NV-4080S-FE',
        'price': Decimal('999.99'),
        'discount_price': Decimal('949.99'),
        'stock': 15,
        'low_stock_threshold': 3,
        'is_featured': True,
        'primary_color': (20, 35, 15),
        'accent_color': (120, 190, 32),
        'shape_fn': draw_rtx4080s,
        'short_desc': 'Supercharged 4K gaming performance with 10,240 CUDA cores and revolutionary dual flow-through cooling.',
        'desc': (
            "The GeForce RTX 4080 SUPER delivers a supercharged leap in gaming and generative AI compute. "
            "Backed by 16GB of blazingly fast GDDR6X memory, DLSS 3.5 Ray Reconstruction, and AV1 dual NVENC encoders.\n\n"
            "Key Specifications:\n"
            "• CUDA Cores: 10,240\n"
            "• Memory: 16GB GDDR6X 256-bit (736 GB/s bandwidth)\n"
            "• Boost Clock: 2550 MHz\n"
            "• Power Connector: 1x 16-pin 12VHPWR (320W TGP)\n"
            "• Thermal: Iconic sculpted gunmetal aluminum dual-axial fan chassis"
        ),
        'variants': [
            ('Edition', 'Founders Edition Gunmetal', 'GPU-4080S-FE', Decimal('0.00'), 15),
        ],
        'review': ('Absolute 4K sweet spot GPU', 5, 'Runs silent, looks magnificent in my case, and plays Cyberpunk Phantom Liberty path-traced at over 100 FPS with DLSS 3.5.', customer1)
    },
    {
        'slug': 'msi-geforce-rtx-4070-ti-super-gaming-x-slim',
        'title': 'MSI GeForce RTX 4070 Ti SUPER 16GB Gaming X Slim',
        'subtitle': 'TRI FROZR 3 Thermal  |  TORX Fan 5.0  |  16GB GDDR6X',
        'specs_badge': 'Sleek Slim Profile Design  |  Airflow Control Heatsink',
        'cat_slug': 'graphics-cards',
        'name': 'MSI GeForce RTX 4070 Ti SUPER 16GB Gaming X Slim',
        'sku': 'GPU-MSI-4070TIS',
        'price': Decimal('829.99'),
        'discount_price': Decimal('799.99'),
        'stock': 20,
        'low_stock_threshold': 4,
        'is_featured': True,
        'primary_color': (35, 12, 16),
        'accent_color': (230, 20, 45),
        'shape_fn': draw_msi_4070ti,
        'short_desc': 'High-framerate 1440p and 4K powerhouse in a space-saving slim form factor with RGB Mystic Light.',
        'desc': (
            "GAMING SLIM series is a lighter, thinner variant of the iconic GAMING series while keeping top-tier thermal performance. "
            "Features upgraded 16GB VRAM on a 256-bit bus, nickel-plated copper baseplate, and zero-RPM ambient fan mode.\n\n"
            "Key Specifications:\n"
            "• CUDA Cores: 8,448\n"
            "• Memory: 16GB GDDR6X 256-bit\n"
            "• Extreme Performance: 2685 MHz (MSI Center)\n"
            "• Cooling: TRI FROZR 3 with TORX Fan 5.0\n"
            "• Form Factor: 2.5-slot compact length (307mm)"
        ),
        'variants': [
            ('Color', 'Stealth Black Slim', 'GPU-4070TIS-BLK', Decimal('0.00'), 14),
            ('Color', 'Arctic White Slim', 'GPU-4070TIS-WHT', Decimal('20.00'), 6),
        ],
        'review': ('Fits in compact cases without sacrificing thermals', 5, 'The slim profile fit easily in my mATX build. Stays under 64C under full gaming load.', customer2)
    },
    {
        'slug': 'intel-core-i7-14700k-gaming-processor',
        'title': 'Intel Core i7-14700K 20-Core Gaming Processor',
        'subtitle': '20 Cores (8P + 12E)  |  28 Threads  |  5.6 GHz Turbo',
        'specs_badge': '33MB Intel Smart Cache  |  LGA1700 Socket  |  PCIe 5.0',
        'cat_slug': 'processors-cpus',
        'name': 'Intel Core i7-14700K 20-Core (8P+12E) Gaming Processor',
        'sku': 'CPU-INT-14700K',
        'price': Decimal('419.99'),
        'discount_price': Decimal('389.99'),
        'stock': 30,
        'low_stock_threshold': 5,
        'is_featured': True,
        'primary_color': (10, 25, 55),
        'accent_color': (0, 150, 255),
        'shape_fn': draw_i7_14700k,
        'short_desc': 'Upgraded with 4 additional E-cores for extraordinary gaming frame pacing and heavy multitasking.',
        'desc': (
            "The 14th Gen Intel Core i7-14700K brings more compute cores than ever. With 8 Performance cores and 12 Efficient cores, "
            "it delivers blistering 5.6 GHz clock speeds for high-FPS competitive esports and stutter-free game streaming.\n\n"
            "Key Specifications:\n"
            "• Total Cores: 20 (8 Performance + 12 Efficient)\n"
            "• Total Threads: 28\n"
            "• Max Turbo Frequency: 5.60 GHz\n"
            "• L3 Cache: 33MB Intel Smart Cache\n"
            "• Memory Support: DDR5-5600 & DDR4-3200"
        ),
        'variants': [
            ('Packaging', 'Standard Boxed (No Cooler)', 'CPU-14700K-BOX', Decimal('0.00'), 30),
        ],
        'review': ('The best value high-end CPU right now', 5, 'The extra 4 E-cores make a huge difference in background encoding and video rendering while gaming.', customer1)
    },
    {
        'slug': 'amd-ryzen-9-7950x3d-gaming-processor',
        'title': 'AMD Ryzen 9 7950X3D 16-Core 32-Thread Gaming CPU',
        'subtitle': '16 Cores  |  32 Threads  |  144MB Total 3D V-Cache',
        'specs_badge': 'Up to 5.7 GHz Boost  |  Socket AM5  |  120W TDP Efficiency',
        'cat_slug': 'processors-cpus',
        'name': 'AMD Ryzen 9 7950X3D 16-Core 32-Thread Gaming & Workstation CPU',
        'sku': 'CPU-RYZ-7950X3D',
        'price': Decimal('699.00'),
        'discount_price': Decimal('599.00'),
        'stock': 16,
        'low_stock_threshold': 3,
        'is_featured': True,
        'primary_color': (35, 18, 10),
        'accent_color': (255, 95, 20),
        'shape_fn': draw_ryzen9_7950x3d,
        'short_desc': 'The ultimate do-it-all flagship processor: revolutionary 3D V-Cache for gaming paired with 16 heavy rendering cores.',
        'desc': (
            "No compromises. The AMD Ryzen 9 7950X3D packs two CCDs: one equipped with 64MB of 3D V-Cache for unmatched gaming latencies, "
            "and a second high-frequency CCD reaching 5.7 GHz for 3D animation, Blender rendering, and code compilation.\n\n"
            "Key Specifications:\n"
            "• Cores / Threads: 16 Cores / 32 Threads\n"
            "• Max Boost Clock: Up to 5.7 GHz\n"
            "• L3 Cache: 128MB (144MB Total Cache)\n"
            "• Default TDP: 120W\n"
            "• Socket: AM5 (Zen 4 Architecture)"
        ),
        'variants': [
            ('Packaging', 'Boxed AM5 Processor', 'CPU-7950X3D-BOX', Decimal('0.00'), 16),
        ],
        'review': ('Crushes both gaming and 4K rendering', 5, 'Runs Unreal Engine builds in half the time of my old chip while giving smooth 240 FPS in shooters.', customer2)
    },
    {
        'slug': 'msi-mag-b650-tomahawk-wifi-motherboard',
        'title': 'MSI MAG B650 Tomahawk WiFi AM5 Motherboard',
        'subtitle': '14+2+1 Duet Rail VRM  |  DDR5 Boost  |  Wi-Fi 6E',
        'specs_badge': 'Lightning Gen 4 M.2 Shield Frozr  |  Extended Heatsink',
        'cat_slug': 'motherboards',
        'name': 'MSI MAG B650 Tomahawk WiFi AM5 Gaming Motherboard',
        'sku': 'MB-MSI-B650T',
        'price': Decimal('219.99'),
        'discount_price': Decimal('199.99'),
        'stock': 28,
        'low_stock_threshold': 5,
        'is_featured': False,
        'primary_color': (15, 28, 25),
        'accent_color': (0, 210, 180),
        'shape_fn': draw_b650_tomahawk,
        'short_desc': 'Battlefield-proven reliability with robust 14+2+1 power stages, DDR5-6600+ support, and high-speed Wi-Fi 6E.',
        'desc': (
            "The MAG B650 TOMAHAWK WIFI is built for gamers who demand stability and value. Featuring extended VRM heatsinks, "
            "double-sided M.2 Shield Frozr, pre-installed I/O shield, and 2.5G LAN for lag-free multiplayer gaming.\n\n"
            "Key Specifications:\n"
            "• Socket: AMD AM5 (Ryzen 7000/8000/9000 Series Ready)\n"
            "• VRM: 14+2+1 Duet Rail Power System with 80A Smart Power Stages\n"
            "• Memory: 4x DDR5 DIMMs (Up to 192GB, 7600+ MHz OC)\n"
            "• Expansion: 1x PCIe 4.0 x16 Steel Armor, 3x M.2 slots\n"
            "• Networking: Wi-Fi 6E & Realtek 2.5G LAN"
        ),
        'variants': [
            ('Model', 'Standard B650 ATX', 'MB-B650T-ATX', Decimal('0.00'), 28),
        ],
        'review': ('Rock solid AM5 board for the price', 5, 'Paired with a 7800X3D, booted on the first try with EXPO 6000MHz enabled. Great VRM thermals.', customer1)
    },
    {
        'slug': 'gigabyte-z790-aorus-master-x-motherboard',
        'title': 'GIGABYTE Z790 AORUS Master X Gaming Motherboard',
        'subtitle': 'Direct 20+1+2 VRM  |  Wi-Fi 7  |  PCIe 5.0 M.2 EZ-Latch',
        'specs_badge': 'Fins-Array Heatsinks with Nanocarbon  |  DDR5 XMP 8266+',
        'cat_slug': 'motherboards',
        'name': 'GIGABYTE Z790 AORUS Master X Gaming Motherboard',
        'sku': 'MB-GIG-Z790M',
        'price': Decimal('549.99'),
        'discount_price': Decimal('499.99'),
        'stock': 14,
        'low_stock_threshold': 3,
        'is_featured': True,
        'primary_color': (30, 20, 10),
        'accent_color': (255, 120, 0),
        'shape_fn': draw_z790_aorus,
        'short_desc': 'Enthusiast motherboard featuring direct 20-phase digital power, cutting-edge Wi-Fi 7, and toolless M.2 installation.',
        'desc': (
            "Engineered to extract every ounce of performance from 14th Gen Intel Core CPUs. Features full metal thermal armor, "
            "ultra-high bandwidth Wi-Fi 7 with directional ultra-gain antenna, 10GbE LAN, and ESS SABRE Hi-Fi audio.\n\n"
            "Key Specifications:\n"
            "• Socket: Intel LGA 1700\n"
            "• Power Delivery: Direct 20+1+2 Phases with 105A Power Stages\n"
            "• Memory: DDR5-8266+ (XMP 3.0 Ready)\n"
            "• Networking: Intel Wi-Fi 7 & Marvell AQtion 10GbE LAN\n"
            "• Storage: 5x M.2 Slots (1x PCIe 5.0 with M.2 Thermal Guard XL)"
        ),
        'variants': [
            ('Edition', 'Standard Master X ATX', 'MB-Z790M-ATX', Decimal('0.00'), 14),
        ],
        'review': ('Top of the line 14900KS motherboard', 5, 'The 10GbE LAN and Wi-Fi 7 speeds are blazing. Toolless EZ-Latch for M.2 SSDs saved so much assembly time.', customer2)
    },
    {
        'slug': 'wd-black-sn850x-4tb-gaming-nvme-ssd',
        'title': 'Western Digital WD_BLACK SN850X 4TB NVMe M.2 SSD',
        'subtitle': 'Up to 7,300 MB/s Read  |  4TB Massive Capacity  |  PCIe Gen4',
        'specs_badge': 'Game Mode 2.0 Predictive Loading  |  BiCS5 3D TLC NAND',
        'cat_slug': 'storage-ssds',
        'name': 'Western Digital WD_BLACK SN850X 4TB NVMe M.2 Gaming SSD',
        'sku': 'SSD-WD-SN850X-4TB',
        'price': Decimal('329.99'),
        'discount_price': Decimal('299.99'),
        'stock': 25,
        'low_stock_threshold': 5,
        'is_featured': True,
        'primary_color': (25, 18, 12),
        'accent_color': (255, 140, 0),
        'shape_fn': draw_wd_sn850x,
        'short_desc': 'Never uninstall a game again: colossal 4TB storage paired with elite 7,300 MB/s throughput.',
        'desc': (
            "Crush load times and slash throttling with the WD_BLACK SN850X NVMe SSD. Featuring Game Mode 2.0 with predictive loading, "
            "this flagship 4TB drive holds 40+ modern AAA game installs while ensuring instant level transitions.\n\n"
            "Key Specifications:\n"
            "• Capacity: 4TB (4,000GB)\n"
            "• Form Factor: M.2 2280 Single-Sided\n"
            "• Sequential Read: Up to 7,300 MB/s\n"
            "• Sequential Write: Up to 6,600 MB/s\n"
            "• Random Read/Write: Up to 1,200,000 / 1,100,000 IOPS\n"
            "• Endurance: 2,400 TBW (5-Year Warranty)"
        ),
        'variants': [
            ('Capacity', '4TB NVMe SSD', 'SSD-SN850X-4TB', Decimal('0.00'), 18),
            ('Capacity', '2TB NVMe SSD', 'SSD-SN850X-2TB', Decimal('-140.00'), 7),
        ],
        'review': ('Holds my entire Steam library without sweating', 5, 'Game Mode 2.0 keeps level transitions buttery smooth in Microsoft Flight Simulator and Call of Duty.', customer1)
    },
    {
        'slug': 'seasonic-vertex-gx-1200-modular-psu',
        'title': 'Seasonic VERTEX GX-1200 1200W 80 PLUS Gold ATX 3.0 PSU',
        'subtitle': '1200 Watts  |  Native PCIe 5.0 12VHPWR  |  Full Modular',
        'specs_badge': '135mm FDB Fan with Hybrid Silent Mode  |  10-Year Warranty',
        'cat_slug': 'power-supplies',
        'name': 'Seasonic VERTEX GX-1200 1200W 80 PLUS Gold ATX 3.0 Modular PSU',
        'sku': 'PSU-SEA-1200GX',
        'price': Decimal('239.99'),
        'discount_price': Decimal('219.99'),
        'stock': 18,
        'low_stock_threshold': 4,
        'is_featured': False,
        'primary_color': (24, 22, 14),
        'accent_color': (245, 190, 30),
        'shape_fn': draw_seasonic_1200,
        'short_desc': 'Legendary Seasonic engineering delivering 1200W clean power for RTX 4090 builds with native 12VHPWR.',
        'desc': (
            "The VERTEX series is designed specifically for power-hungry modern GPUs. Built to full ATX 3.0 and PCIe 5.0 standards, "
            "it effortlessly handles up to 200% transient power spikes with premium Japanese 105°C capacitors.\n\n"
            "Key Specifications:\n"
            "• Total Power: 1200 Watts\n"
            "• Certification: 80 PLUS Gold (90% efficiency at 50% load)\n"
            "• ATX Standard: ATX 3.0 with native 16-pin 12V-2x6 cable (600W rating)\n"
            "• Fan: 135mm Fluid Dynamic Bearing with Seasonic Digital Hybrid Silent Control\n"
            "• Protection: OPP, OVP, UVP, OCP, OTP, SCP"
        ),
        'variants': [
            ('Wattage', '1200W 80+ Gold', 'PSU-VTX-1200', Decimal('0.00'), 18),
        ],
        'review': ('Seasonic is the gold standard for power supplies', 5, 'Powering an RTX 4090 and 14900K with zero coil whine and whisper quiet fan operation.', customer2)
    },
    {
        'slug': 'corsair-5000d-airflow-tempered-glass-case',
        'title': 'Corsair 5000D Airflow Tempered Glass PC Case',
        'subtitle': 'High-Airflow Steel Front  |  RapidRoute Cable Management',
        'specs_badge': 'Fits Dual 360mm Radiators  |  Tempered Glass Side Panel',
        'cat_slug': 'pc-cases',
        'name': 'Corsair 5000D Airflow Tempered Glass Mid-Tower PC Case',
        'sku': 'CAS-COR-5000D',
        'price': Decimal('164.99'),
        'discount_price': Decimal('149.99'),
        'stock': 22,
        'low_stock_threshold': 4,
        'is_featured': True,
        'primary_color': (25, 24, 15),
        'accent_color': (240, 210, 0),
        'shape_fn': draw_corsair_5000d,
        'short_desc': 'The benchmark for high-airflow PC cases with expansive radiator clearance and dedicated motherboard tray cable routing.',
        'desc': (
            "The Corsair 5000D AIRFLOW is a mid-tower ATX case that shows off your PC, not its cables. An optimized high-airflow "
            "steel front panel channels maximum cooling air to your graphics card and CPU.\n\n"
            "Key Specifications:\n"
            "• Dimensions: 520mm (L) x 245mm (W) x 520mm (H)\n"
            "• Radiator Capacity: Front 360mm, Top 360mm, Motherboard Tray 360mm\n"
            "• Maximum GPU Length: 400mm\n"
            "• Maximum CPU Cooler Height: 170mm\n"
            "• Included Fans: 2x Corsair 120mm AirGuide fans with anti-vortex vanes"
        ),
        'variants': [
            ('Color', 'True Black Steel', 'CAS-5000D-BLK', Decimal('0.00'), 14),
            ('Color', 'Arctic White Steel', 'CAS-5000D-WHT', Decimal('10.00'), 8),
        ],
        'review': ('Spacious and incredibly easy to build in', 5, 'The side fan mount lets you run two 360mm radiators at the same time. GPU temperatures dropped by 8°C.', customer1)
    },
    {
        'slug': 'fractal-design-north-charcoal-black-case',
        'title': 'Fractal Design North Charcoal Black PC Case',
        'subtitle': 'Real Solid Walnut Wood Slats  |  Brass Accents  |  Scandinavian Design',
        'specs_badge': 'Modern Living Room Aesthetic  |  Tinted Tempered Glass Panel',
        'cat_slug': 'pc-cases',
        'name': 'Fractal Design North Charcoal Black Walnut Wood Gaming PC Case',
        'sku': 'CAS-FRAC-NORTH',
        'price': Decimal('159.99'),
        'discount_price': Decimal('139.99'),
        'stock': 19,
        'low_stock_threshold': 3,
        'is_featured': True,
        'primary_color': (28, 20, 14),
        'accent_color': (200, 140, 70),
        'shape_fn': draw_fractal_north,
        'short_desc': 'Award-winning Scandinavian interior design incorporating genuine FSC-certified walnut wood slats and brass detailing.',
        'desc': (
            "North reimagines the gaming PC, introducing natural materials and bespoke details to make gaming an integral part "
            "of your living space. Features real solid walnut wood front slats, brass power button and I/O trim, and tinted tempered glass.\n\n"
            "Key Specifications:\n"
            "• Front Panel: Genuine FSC-certified solid American Walnut\n"
            "• Materials: Steel chassis, dark tinted tempered glass, brushed brass\n"
            "• Radiator Support: Up to 360mm front, 240mm top\n"
            "• GPU Clearance: Up to 355mm length\n"
            "• Included Fans: 2x Aspect 140mm PWM fans"
        ),
        'variants': [
            ('Style', 'Charcoal Black with Walnut & Glass', 'CAS-NORTH-BLK-TG', Decimal('0.00'), 12),
            ('Style', 'Chalk White with Oak & Glass', 'CAS-NORTH-WHT-TG', Decimal('10.00'), 7),
        ],
        'review': ('The most beautiful PC case on earth', 5, 'Looks like a piece of high-end furniture rather than an aggressive gamer tower. Extremely well ventilated too.', customer2)
    },
    {
        'slug': 'arctic-liquid-freezer-iii-360-argb-cooler',
        'title': 'ARCTIC Liquid Freezer III 360 A-RGB Liquid Cooler',
        'subtitle': '38mm Thick High-Density Radiator  |  VRM Fan  |  P12 PWM Fans',
        'specs_badge': 'Unmatched Thermal Dissipation  |  Integrated Cable Management',
        'cat_slug': 'cooling-cases',
        'name': 'ARCTIC Liquid Freezer III 360 A-RGB High-Performance Liquid Cooler',
        'sku': 'CLR-ARC-LF3-360',
        'price': Decimal('139.99'),
        'discount_price': Decimal('119.99'),
        'stock': 26,
        'low_stock_threshold': 5,
        'is_featured': False,
        'primary_color': (14, 24, 30),
        'accent_color': (0, 220, 255),
        'shape_fn': draw_arctic_freezer3,
        'short_desc': 'Extra-thick 38mm radiator paired with a dedicated centrifugal VRM fan for the coolest CPU and motherboard temperatures.',
        'desc': (
            "The multi-award-winning Liquid Freezer III takes liquid cooling to a new benchmark. Its 38mm radiator has 30% more fin surface area "
            "than standard coolers, while the redesigned pump block houses an active VRM fan to cool motherboard power delivery stages.\n\n"
            "Key Specifications:\n"
            "• Radiator Thickness: 38mm (High Heat Capacity)\n"
            "• Fans: 3x Arctic P12 PWM A-RGB (200 - 2,000 RPM)\n"
            "• VRM Fan: 40mm Controlled (400 - 2,500 RPM)\n"
            "• Cold Plate: Copper with optimized micro-skived fin stack\n"
            "• Socket Support: Intel LGA 1700 Contact Frame included & AMD AM5/AM4 Offset Mount"
        ),
        'variants': [
            ('Color', 'All-Black A-RGB', 'CLR-LF3-BLK', Decimal('0.00'), 16),
            ('Color', 'White A-RGB Edition', 'CLR-LF3-WHT', Decimal('10.00'), 10),
        ],
        'review': ('Beats 300 dollar coolers at half the price', 5, 'The contact frame and the active VRM fan dropped both my CPU and motherboard temps significantly. Phenomenal performance.', customer1)
    },
    {
        'slug': 'teamgroup-t-force-delta-rgb-32gb-ddr5-6000',
        'title': 'TeamGroup T-Force Delta RGB 32GB (2x16GB) DDR5-6000',
        'subtitle': 'CL30 Ultra-Low Latency  |  120° Wide-Angle RGB  |  Dual Channel',
        'specs_badge': 'AMD EXPO & Intel XMP 3.0  |  Power Management IC (PMIC)',
        'cat_slug': 'memory-storage',
        'name': 'TeamGroup T-Force Delta RGB 32GB (2x16GB) DDR5-6000 CL30 RAM',
        'sku': 'RAM-TMG-DLT-32G',
        'price': Decimal('129.99'),
        'discount_price': Decimal('109.99'),
        'stock': 35,
        'low_stock_threshold': 6,
        'is_featured': False,
        'primary_color': (25, 12, 28),
        'accent_color': (255, 40, 180),
        'shape_fn': draw_teamgroup_delta,
        'short_desc': 'Stealth fighter geometric heatspreaders with 120° panoramic ultra-wide RGB illumination and tight CL30 timings.',
        'desc': (
            "Modeled after stealth aircraft, the T-Force Delta RGB DDR5 memory delivers breathtaking aesthetics and performance. "
            "Optimized for high-FPS gaming with low CL30-36-36-76 latency and high-transmittance light bar compatible with all major RGB software.\n\n"
            "Key Specifications:\n"
            "• Capacity: 32GB (2 x 16GB Kit)\n"
            "• Frequency: DDR5-6000 MHz\n"
            "• Latency: CL30-36-36-76 (Low Latency Gaming Die)\n"
            "• Voltage: 1.35V\n"
            "• Profiles: Dual AMD EXPO and Intel XMP 3.0 certified"
        ),
        'variants': [
            ('Colorway', 'Stealth Black', 'RAM-DLT-BLK', Decimal('0.00'), 20),
            ('Colorway', 'Snow White', 'RAM-DLT-WHT', Decimal('0.00'), 15),
        ],
        'review': ('CL30 6000MHz is the sweet spot for Ryzen 7000', 5, 'One click in BIOS to load EXPO and it has been rock solid. The RGB lighting is super bright and smooth.', customer2)
    },
]

# ==========================================
# 4. DATABASE INSERTION & AUDITING
# ==========================================

print(f"\nProcessing {len(parts_data)} new gaming PC parts...")

for p in parts_data:
    slug = p['slug']
    cat = Category.objects.get(slug=p['cat_slug'])
    
    # 1. Render Graphic
    img_path = render_image(
        slug=slug,
        title=p['title'],
        subtitle=p['subtitle'],
        specs_badge=p['specs_badge'],
        primary_color=p['primary_color'],
        accent_color=p['accent_color'],
        shape_fn=p['shape_fn']
    )

    # 2. Create or Update Product
    prod, pcreated = Product.objects.get_or_create(
        slug=slug,
        defaults={
            'name': p['name'],
            'category': cat,
            'sku': p['sku'],
            'price': p['price'],
            'discount_price': p['discount_price'],
            'stock': p['stock'],
            'low_stock_threshold': p['low_stock_threshold'],
            'short_description': p['short_desc'],
            'description': p['desc'],
            'is_featured': p['is_featured'],
            'is_active': True,
        }
    )
    if not pcreated:
        prod.name = p['name']
        prod.category = cat
        prod.price = p['price']
        prod.discount_price = p['discount_price']
        prod.stock = p['stock']
        prod.short_description = p['short_desc']
        prod.description = p['desc']
        prod.is_featured = p['is_featured']
        prod.save()
        print(f"Updated product: {prod.name}")
    else:
        print(f"Created product: {prod.name}")

    # 3. Inventory Transaction
    if prod.stock > 0 and not InventoryTransaction.objects.filter(product=prod).exists():
        InventoryTransaction.objects.create(
            product=prod,
            change_type=TransactionType.RESTOCK,
            quantity=prod.stock,
            previous_stock=0,
            new_stock=prod.stock,
            note='Initial inventory allotment for gaming PC hardware expansion',
            created_by=admin_user
        )

    # 4. Product Image
    rel_img_path = f"products/{slug}.jpg"
    pimg, _ = ProductImage.objects.get_or_create(
        product=prod,
        image=rel_img_path,
        defaults={'alt_text': prod.name, 'is_primary': True, 'order': 1}
    )
    pimg.is_primary = True
    pimg.save()

    # 5. Variants
    for vname, vval, vsku, add_price, vstock in p['variants']:
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

    # 6. Reviews
    if 'review' in p and p['review']:
        rtitle, rrating, rcomment, ruser = p['review']
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

print("\nSUCCESS! All 12 gaming PC hardware parts populated with photos, specs, and inventory!")

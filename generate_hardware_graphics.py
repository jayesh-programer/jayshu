from PIL import Image, ImageDraw, ImageFont
import math
import os

media_dir = r"C:\Users\Kartik\.gemini\antigravity\scratch\ecommerce\media\products"
os.makedirs(media_dir, exist_ok=True)

def create_gradient(width, height, start_color, end_color):
    base = Image.new('RGB', (width, height), start_color)
    top = Image.new('RGB', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - width/2)**2 + (y - height/2)**2)
            max_dist = math.sqrt((width/2)**2 + (height/2)**2)
            val = int(255 * min(1.0, dist / max_dist))
            mask_data.append(val)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def draw_grid(draw, width, height, step=40, color=(35, 45, 60)):
    for x in range(0, width, step):
        draw.line([(x, 0), (x, height)], fill=color, width=1)
    for y in range(0, height, step):
        draw.line([(0, y), (width, y)], fill=color, width=1)

# 1. Intel Core i9-14900KS
def render_intel_14900ks():
    W, H = 1000, 1000
    img = create_gradient(W, H, (10, 20, 45), (4, 8, 18))
    draw = ImageDraw.Draw(img)
    draw_grid(draw, W, H, step=50, color=(18, 32, 60))

    # Outer ambient glow
    draw.ellipse([250, 250, 750, 750], fill=(0, 60, 150), outline=None)
    
    # Collectible Silicon Wafer Box
    draw.rounded_rectangle([320, 220, 680, 580], radius=40, fill=(15, 35, 75), outline=(0, 160, 255), width=4)
    # Inner metallic die
    draw.rectangle([380, 280, 620, 520], fill=(22, 50, 105), outline=(100, 200, 255), width=3)
    
    # CPU Heatspreader
    draw.rounded_rectangle([410, 310, 590, 490], radius=15, fill=(180, 195, 215), outline=(230, 240, 255), width=3)
    # CPU Etching
    draw.text((435, 340), "intel.", fill=(0, 100, 210))
    draw.text((435, 370), "CORE i9", fill=(10, 25, 50))
    draw.text((435, 410), "14900KS", fill=(10, 25, 50))
    draw.text((435, 450), "6.2 GHz SPECIAL ED.", fill=(50, 70, 95))

    # Decorative badges
    draw.rounded_rectangle([250, 660, 750, 780], radius=20, fill=(8, 18, 38), outline=(0, 150, 255), width=2)
    draw.text((310, 685), "INTEL CORE i9-14900KS", fill=(255, 255, 255))
    draw.text((345, 730), "24 Cores (8P+16E)  |  6.2 GHz Max Turbo  |  LGA1700", fill=(0, 200, 255))
    
    # Corner badge
    draw.rounded_rectangle([80, 80, 280, 130], radius=10, fill=(0, 100, 220))
    draw.text((105, 95), "SPECIAL EDITION", fill=(255, 255, 255))

    out_path = os.path.join(media_dir, "intel-core-i9-14900ks-special-edition-processor.jpg")
    img.save(out_path, quality=95)
    print("Saved:", out_path)

# 2. AMD Radeon RX 7900 XTX
def render_rx_7900xtx():
    W, H = 1000, 1000
    img = create_gradient(W, H, (35, 12, 18), (12, 4, 6))
    draw = ImageDraw.Draw(img)
    draw_grid(draw, W, H, step=50, color=(45, 18, 24))

    # GPU Shroud silhouette
    draw.rounded_rectangle([180, 320, 820, 600], radius=25, fill=(25, 25, 28), outline=(220, 20, 50), width=4)
    # Red accent heatsink fins
    for x in range(210, 790, 18):
        draw.line([(x, 340), (x, 580)], fill=(45, 45, 52), width=4)
    for x in (320, 480, 640):
        draw.line([(x, 340), (x, 580)], fill=(230, 25, 55), width=5)

    # Triple Fans
    centers = [(310, 460), (500, 460), (690, 460)]
    for cx, cy in centers:
        draw.ellipse([cx-75, cy-75, cx+75, cy+75], fill=(15, 15, 18), outline=(200, 30, 60), width=3)
        draw.ellipse([cx-25, cy-25, cx+25, cy+25], fill=(35, 35, 40), outline=(255, 60, 80), width=2)
        # Blades
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            bx = cx + int(55 * math.cos(rad))
            by = cy + int(55 * math.sin(rad))
            draw.line([(cx, cy), (bx, by)], fill=(50, 50, 58), width=3)

    # Info Badge
    draw.rounded_rectangle([220, 670, 780, 790], radius=20, fill=(20, 10, 14), outline=(230, 30, 60), width=2)
    draw.text((275, 695), "AMD RADEON RX 7900 XTX", fill=(255, 255, 255))
    draw.text((295, 740), "24GB GDDR6  |  RDNA 3 Chiplet  |  DisplayPort 2.1", fill=(255, 80, 100))

    # RDNA3 Badge
    draw.rounded_rectangle([80, 80, 260, 130], radius=10, fill=(210, 20, 45))
    draw.text((115, 95), "RDNA 3 FLAGSHIP", fill=(255, 255, 255))

    out_path = os.path.join(media_dir, "amd-radeon-rx-7900-xtx-24gb-graphics-card.jpg")
    img.save(out_path, quality=95)
    print("Saved:", out_path)

# 3. HYTE Y70 Touch Panoramic Glass PC Case
def render_hyte_y70():
    W, H = 1000, 1000
    img = create_gradient(W, H, (20, 25, 40), (8, 10, 18))
    draw = ImageDraw.Draw(img)
    draw_grid(draw, W, H, step=50, color=(28, 35, 52))

    # Panoramic Chassis frame (white aesthetic)
    draw.polygon([(260, 220), (580, 170), (740, 230), (740, 680), (460, 750), (260, 670)], fill=(235, 240, 250), outline=(0, 220, 255), width=3)
    # Tempered glass inner window
    draw.polygon([(280, 250), (560, 205), (560, 670), (280, 640)], fill=(30, 38, 55), outline=(150, 200, 255), width=2)

    # 4K Integrated Touchscreen Pillar
    draw.polygon([(575, 210), (720, 265), (720, 670), (575, 665)], fill=(10, 15, 25), outline=(255, 50, 140), width=3)
    # Live Touchscreen Widget simulation
    draw.rectangle([600, 290, 700, 360], fill=(20, 30, 50), outline=(0, 255, 220), width=1)
    draw.text((615, 310), "CPU 44°C", fill=(0, 255, 220))
    draw.rectangle([600, 380, 700, 450], fill=(20, 30, 50), outline=(255, 80, 160), width=1)
    draw.text((615, 400), "GPU 52°C", fill=(255, 80, 160))
    draw.rectangle([600, 480, 700, 580], fill=(15, 20, 35), outline=(255, 210, 0), width=1)
    draw.text((615, 510), "4K TOUCH", fill=(255, 210, 0))

    # Info Badge
    draw.rounded_rectangle([200, 780, 800, 900], radius=20, fill=(15, 20, 32), outline=(0, 220, 255), width=2)
    draw.text((275, 805), "HYTE Y70 TOUCH PANORAMIC CASE", fill=(255, 255, 255))
    draw.text((260, 850), "Integrated 14.1” 4K Touchscreen  |  Vertical GPU  |  Snow White", fill=(0, 230, 255))

    out_path = os.path.join(media_dir, "hyte-y70-touch-panoramic-glass-pc-case.jpg")
    img.save(out_path, quality=95)
    print("Saved:", out_path)

# 4. Lian Li UNI FAN SL-INFINITY 120
def render_lianli_fans():
    W, H = 1000, 1000
    img = create_gradient(W, H, (15, 28, 38), (6, 12, 18))
    draw = ImageDraw.Draw(img)
    draw_grid(draw, W, H, step=50, color=(20, 38, 50))

    # 3 Daisy-Chained Fans
    fan_xs = [240, 500, 760]
    cy = 440
    for fx in fan_xs:
        # Fan Frame
        draw.rounded_rectangle([fx-115, cy-115, fx+115, cy+115], radius=20, fill=(20, 22, 26), outline=(0, 230, 220), width=3)
        # Outer RGB ring
        draw.ellipse([fx-95, cy-95, fx+95, cy+95], fill=(12, 14, 18), outline=(255, 0, 180), width=4)
        # Infinity Mirror center hub
        draw.ellipse([fx-45, cy-45, fx+45, cy+45], fill=(5, 6, 8), outline=(0, 220, 255), width=3)
        draw.ellipse([fx-30, cy-30, fx+30, cy+30], outline=(150, 0, 255), width=2)
        draw.ellipse([fx-18, cy-18, fx+18, cy+18], outline=(255, 50, 180), width=2)
        draw.ellipse([fx-8, cy-8, fx+8, cy+8], fill=(0, 220, 255))

    # Info Badge
    draw.rounded_rectangle([180, 650, 820, 770], radius=20, fill=(12, 18, 25), outline=(0, 220, 255), width=2)
    draw.text((225, 675), "LIAN LI UNI FAN SL-INFINITY 120 RGB", fill=(255, 255, 255))
    draw.text((250, 720), "Daisy-Chain Cableless  |  40 LEDs  |  Infinite Mirror Hub", fill=(0, 230, 220))

    out_path = os.path.join(media_dir, "lian-li-uni-fan-sl-infinity-120-rgb-3pack.jpg")
    img.save(out_path, quality=95)
    print("Saved:", out_path)

# 5. Noctua NH-D15 chromax.black
def render_noctua_d15():
    W, H = 1000, 1000
    img = create_gradient(W, H, (28, 22, 18), (10, 8, 7))
    draw = ImageDraw.Draw(img)
    draw_grid(draw, W, H, step=50, color=(38, 28, 24))

    # Dual Heatsink Towers (All Black)
    # Left Tower
    draw.rectangle([250, 240, 440, 600], fill=(22, 22, 25), outline=(120, 70, 40), width=3)
    for y in range(260, 590, 14):
        draw.line([(255, y), (435, y)], fill=(45, 45, 50), width=2)

    # Right Tower
    draw.rectangle([560, 240, 750, 600], fill=(22, 22, 25), outline=(120, 70, 40), width=3)
    for y in range(260, 590, 14):
        draw.line([(565, y), (745, y)], fill=(45, 45, 50), width=2)

    # 140mm Middle Fan
    draw.rounded_rectangle([425, 220, 575, 620], radius=15, fill=(14, 14, 16), outline=(180, 80, 30), width=3)
    draw.ellipse([460, 380, 540, 460], fill=(28, 28, 32), outline=(180, 90, 40), width=2)

    # Copper Heatpipes at bottom
    for x in range(300, 700, 60):
        draw.line([(x, 600), (x, 660)], fill=(195, 100, 45), width=6)
    draw.rectangle([280, 660, 720, 700], fill=(160, 90, 45), outline=(220, 130, 60), width=3)

    # Info Badge
    draw.rounded_rectangle([200, 750, 800, 870], radius=20, fill=(18, 14, 12), outline=(190, 90, 40), width=2)
    draw.text((255, 775), "NOCTUA NH-D15 CHROMAX.BLACK", fill=(255, 255, 255))
    draw.text((270, 820), "Dual-Tower Design  |  2x NF-A15 140mm Fans  |  Silent King", fill=(230, 140, 70))

    # Noctua Emblem
    draw.rounded_rectangle([80, 80, 260, 130], radius=10, fill=(140, 65, 25))
    draw.text((115, 95), "NOCTUA CHROMAX", fill=(255, 255, 255))

    out_path = os.path.join(media_dir, "noctua-nh-d15-chromax-black-cpu-cooler.jpg")
    img.save(out_path, quality=95)
    print("Saved:", out_path)

render_intel_14900ks()
render_rx_7900xtx()
render_hyte_y70()
render_lianli_fans()
render_noctua_d15()
print("All 5 hardware graphics rendered successfully!")

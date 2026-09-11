import os
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

TEST_DIR = os.path.join(os.path.dirname(__file__), "test_images_for_upload")
os.makedirs(TEST_DIR, exist_ok=True)
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "backend", "sample_data")

# 1. Copy the 3 main scenario source images with clean easy names
if os.path.exists(os.path.join(SAMPLE_DIR, "flooded_urban_rgb.png")):
    shutil.copy(
        os.path.join(SAMPLE_DIR, "flooded_urban_rgb.png"),
        os.path.join(TEST_DIR, "1_sample_flooded_delta_aerial.png")
    )

if os.path.exists(os.path.join(SAMPLE_DIR, "hilly_landslide_rgb.png")):
    shutil.copy(
        os.path.join(SAMPLE_DIR, "hilly_landslide_rgb.png"),
        os.path.join(TEST_DIR, "2_sample_mountain_landslide_aerial.png")
    )

if os.path.exists(os.path.join(SAMPLE_DIR, "dense_urban_rgb.png")):
    shutil.copy(
        os.path.join(SAMPLE_DIR, "dense_urban_rgb.png"),
        os.path.join(TEST_DIR, "3_sample_city_skyscrapers_aerial.png")
    )

# 2. Generate a 4th realistic scenario: Earthquake Structural Damage & Collapsed Corridor
def generate_earthquake_zone():
    width, height = 512, 512
    img = Image.new("RGB", (width, height), (75, 75, 70))
    draw = ImageDraw.Draw(img)

    # Road network
    draw.line([(0, int(height*0.5)), (width, int(height*0.5))], fill=(45, 45, 50), width=18)
    draw.line([(int(width*0.5), 0), (int(width*0.5), height)], fill=(45, 45, 50), width=18)

    # Buildings & partial rubble
    buildings = [
        (40, 40, 110, 110, (180, 170, 160)),
        (130, 45, 220, 115, (160, 150, 140)),
        (300, 50, 380, 130, (140, 155, 170)),
        (400, 40, 470, 120, (190, 180, 165)),
        
        (40, 300, 120, 380, (170, 160, 150)),
        (140, 290, 210, 370, (160, 160, 165)),
        (310, 300, 390, 390, (150, 145, 140)),
        (410, 290, 470, 370, (180, 175, 160))
    ]

    for b in buildings:
        x1, y1, x2, y2, color = b
        draw.rectangle([x1, y1, x2, y2], fill=color, outline=(30, 30, 30), width=2)
        draw.rectangle([x1+4, y1+4, x2-4, y2-4], fill=tuple(int(c*0.85) for c in color))

    # Debris / Rubble zone in center intersection
    draw.ellipse([int(width*0.42), int(height*0.42), int(width*0.58), int(height*0.58)], fill=(155, 135, 115))
    draw.polygon([
        (int(width*0.45), int(height*0.45)), 
        (int(width*0.55), int(height*0.40)), 
        (int(width*0.60), int(height*0.55)), 
        (int(width*0.48), int(height*0.58))
    ], fill=(185, 145, 120))

    img = img.filter(ImageFilter.SMOOTH_MORE)
    img_np = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 4, img_np.shape)
    img_np = np.clip(img_np + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_np)
    
    img.save(os.path.join(TEST_DIR, "4_sample_earthquake_debris_zone.png"), quality=95)

generate_earthquake_zone()
print("All 4 test images generated in test_images_for_upload folder!")

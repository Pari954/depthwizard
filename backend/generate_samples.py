import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
os.makedirs(SAMPLE_DIR, exist_ok=True)

def generate_flooded_urban_scene():
    width, height = 512, 512
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    
    # Elevation base: 5m to 25m
    terrain = 5.0 + 15.0 * xx + 4.0 * np.sin(yy * 6) + 2.0 * np.cos(xx * 8)
    
    # River channel cutting through diagonally (low elevation, 2.0 - 4.0m)
    river_path = 0.35 + 0.25 * np.sin(yy * 3.5)
    river_dist = np.abs(xx - river_path)
    river_mask = river_dist < 0.09
    terrain = np.where(river_mask, 2.5 + 1.2 * np.sin(yy * 5), terrain)
    
    # Lowland flood basin on left
    flood_basin = (xx < 0.28) & (yy > 0.4)
    terrain[flood_basin] = np.minimum(terrain[flood_basin], 4.5)
    
    # Create RGB image
    img = Image.new("RGB", (width, height), (70, 95, 60)) # Natural vegetation green
    draw = ImageDraw.Draw(img)
    
    # Paint river
    for row in range(height):
        cx = int((0.35 + 0.25 * np.sin(row / height * 3.5)) * width)
        rw = int(width * 0.08)
        draw.line([(cx - rw, row), (cx + rw, row)], fill=(35, 75, 95))
    
    # Flood basin water/mud
    draw.polygon([(0, int(height * 0.4)), (int(width * 0.28), int(height * 0.45)), 
                  (int(width * 0.25), height), (0, height)], fill=(45, 80, 85))
    
    # Roads & bridges
    draw.rectangle([int(width * 0.5), 0, int(width * 0.53), height], fill=(60, 60, 65))
    draw.rectangle([0, int(height * 0.6), width, int(height * 0.63)], fill=(60, 60, 65))
    # Bridge over river
    draw.rectangle([int(width * 0.2), int(height * 0.59), int(width * 0.55), int(height * 0.64)], fill=(110, 110, 115))
    
    # Add buildings & raise DSM
    buildings = [
        # (x1, y1, x2, y2, height_m, color, type, label)
        (40, 60, 90, 110, 18.0, (180, 160, 140), "Residential A", "B-001"),
        (110, 70, 170, 120, 24.5, (160, 150, 140), "Commercial Complex", "B-002"),
        (40, 140, 85, 180, 14.0, (190, 175, 155), "Residential B", "B-003"),
        (300, 80, 360, 140, 32.0, (140, 155, 170), "Metropolitan Hospital (Safe Zone)", "B-004"),
        (380, 90, 440, 150, 28.0, (165, 160, 150), "Emergency Center", "B-005"),
        (320, 170, 370, 220, 22.0, (175, 170, 160), "Civic Hall", "B-006"),
        (400, 180, 470, 240, 26.5, (155, 150, 145), "School Shelter", "B-007"),
        (30, 280, 75, 330, 12.0, (170, 160, 150), "Submerged Residential 1", "B-008"),
        (35, 350, 80, 400, 11.5, (165, 155, 145), "Submerged Residential 2", "B-009"),
        (310, 340, 380, 420, 38.0, (130, 145, 160), "Tower A", "B-010"),
        (410, 350, 460, 410, 34.0, (140, 150, 155), "Tower B", "B-011"),
        (330, 440, 400, 490, 29.0, (150, 150, 150), "Logistics Center", "B-012"),
    ]
    
    structures_meta = []
    for b in buildings:
        x1, y1, x2, y2, b_height, color, b_type, label = b
        draw.rectangle([x1, y1, x2, y2], fill=color, outline=(40, 40, 40), width=2)
        # Rooftop details
        draw.rectangle([x1+4, y1+4, x2-4, y2-4], fill=tuple(int(c*0.9) for c in color))
        draw.rectangle([x1+10, y1+10, x1+22, y1+22], fill=(80, 80, 85)) # HVAC
        # Elevate terrain DSM
        terrain[y1:y2, x1:x2] += b_height
        
        # Calculate ground elevation vs top elevation
        ground_el = float(np.mean(terrain[max(0, y1-5):y1, max(0, x1-5):x1])) if y1 > 5 else 8.0
        top_el = float(terrain[(y1+y2)//2, (x1+x2)//2])
        est_h = round(top_el - ground_el, 1)
        
        structures_meta.append({
            "id": label,
            "type": b_type,
            "bbox": [x1, y1, x2, y2],
            "center": [(x1 + x2) // 2, (y1 + y2) // 2],
            "metric_height_m": est_h,
            "relative_height_units": round(est_h * 2.1, 1),
            "uncertainty_range_m": [round(est_h * 0.9, 1), round(est_h * 1.12, 1)],
            "elevation_top_m": round(top_el, 1),
            "ground_elevation_m": round(ground_el, 1),
            "risk_level": "CRITICAL - FLOODED" if ground_el < 7.5 else ("MODERATE" if ground_el < 12.0 else "SAFE / HIGH GROUND")
        })
    
    # Add subtle noise/texture to RGB
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img_np = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 4, img_np.shape)
    img_np = np.clip(img_np + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_np)
    
    # Save RGB
    rgb_path = os.path.join(SAMPLE_DIR, "flooded_urban_rgb.png")
    img.save(rgb_path, quality=95)
    
    # Save DSM numpy & metadata
    dsm_min, dsm_max = float(np.min(terrain)), float(np.max(terrain))
    
    metadata = {
        "id": "flooded_urban",
        "title": "Flooded Urban River Delta (Assam/Kerala Flood Scenario)",
        "theme": "Disaster Management - Flood Inundation & Isolation",
        "description": "Optical satellite view of a river delta with heavy monsoonal inundation, submerged residential zones, and isolated high-rise clusters.",
        "dimensions": [width, height],
        "gsd_m_per_px": 0.25,
        "georeferenced": True,
        "crs": "EPSG:32643 (UTM Zone 43N)",
        "bounds": [76.2845, 9.9812, 76.2973, 9.9940],
        "metric_elevation_range": [round(dsm_min, 1), round(dsm_max, 1)],
        "relative_elevation_range": [0.0, 100.0],
        "mean_elevation_m": round(float(np.mean(terrain)), 1),
        "flood_water_level_m": 8.5,
        "structures": structures_meta,
        "hazard_zones": {
            "critical_flood_area_pct": 34.2,
            "isolated_structures_count": 4,
            "high_ground_shelters_count": 3,
            "recommended_action": "Deploy rapid rescue boats to West Basin (Sector W-1); prioritize B-008 and B-009 evacuation."
        }
    }
    
    with open(os.path.join(SAMPLE_DIR, "flooded_urban_meta.json"), "w") as f:
        json.dump(metadata, f, indent=2)
        
    np.save(os.path.join(SAMPLE_DIR, "flooded_urban_dsm.npy"), terrain.astype(np.float32))
    print("Flooded urban scene generated successfully.")

def generate_hilly_landslide_scene():
    width, height = 512, 512
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    
    # Rugged mountain ridge (elevation 110m to 380m)
    ridge1 = 180.0 * np.exp(-((xx - 0.7)**2 + (yy - 0.3)**2) / 0.12)
    ridge2 = 220.0 * np.exp(-((xx - 0.2)**2 + (yy - 0.7)**2) / 0.18)
    valley = 110.0 + 40.0 * np.sin(xx * 4 + yy * 3) + ridge1 + ridge2
    
    # Steep scarp / landslide scar
    scar_mask = (xx > 0.4) & (xx < 0.65) & (yy > 0.3) & (yy < 0.6)
    valley[scar_mask] -= 35.0 * np.sin((xx[scar_mask]-0.4)/0.25 * np.pi)
    
    img = Image.new("RGB", (width, height), (105, 95, 75)) # Mountain rock & scrub
    draw = ImageDraw.Draw(img)
    
    # Draw mountain forest patches
    draw.polygon([(0, 0), (int(width*0.4), 0), (int(width*0.3), int(height*0.5)), (0, int(height*0.4))], fill=(45, 75, 40))
    draw.polygon([(int(width*0.6), int(height*0.6)), (width, int(height*0.4)), (width, height), (int(width*0.5), height)], fill=(50, 70, 45))
    
    # Landslide debris scar (exposed pale earth/red clay)
    draw.polygon([(int(width*0.42), int(height*0.32)), (int(width*0.62), int(height*0.35)),
                  (int(width*0.58), int(height*0.58)), (int(width*0.38), int(height*0.52))], fill=(175, 115, 80))
    
    # Mountain highway with hairpin bends
    highway = [
        (int(width*0.1), int(height*0.85)), (int(width*0.35), int(height*0.75)),
        (int(width*0.3), int(height*0.6)), (int(width*0.5), int(height*0.55)), # blocked by landslide
        (int(width*0.7), int(height*0.45)), (int(width*0.65), int(height*0.25)),
        (int(width*0.9), int(height*0.15))
    ]
    draw.line(highway, fill=(80, 80, 85), width=6)
    
    # Debris over highway at point (0.5, 0.55)
    draw.ellipse([int(width*0.44), int(height*0.51), int(width*0.54), int(height*0.58)], fill=(160, 100, 70))
    
    # Mountain settlement buildings
    buildings = [
        (70, 400, 110, 435, 10.5, (190, 180, 160), "Valley Settlement 1", "H-001"),
        (120, 390, 165, 425, 12.0, (185, 175, 155), "Valley Settlement 2", "H-002"),
        (175, 410, 220, 445, 9.0, (200, 190, 170), "Agricultural Depot", "H-003"),
        (350, 110, 395, 150, 14.0, (170, 165, 160), "Hilltop Watch Post", "H-004"),
        (410, 120, 460, 165, 11.5, (180, 170, 150), "Communications Relay", "H-005"),
        (260, 280, 300, 315, 8.5, (195, 185, 165), "Slope Dwelling (At Risk)", "H-006"),
    ]
    
    structures_meta = []
    for b in buildings:
        x1, y1, x2, y2, b_height, color, b_type, label = b
        draw.rectangle([x1, y1, x2, y2], fill=color, outline=(30, 30, 30), width=2)
        valley[y1:y2, x1:x2] += b_height
        ground_el = float(np.mean(valley[max(0, y1-5):y1, max(0, x1-5):x1])) if y1 > 5 else 130.0
        top_el = float(valley[(y1+y2)//2, (x1+x2)//2])
        est_h = round(top_el - ground_el, 1)
        structures_meta.append({
            "id": label,
            "type": b_type,
            "bbox": [x1, y1, x2, y2],
            "center": [(x1 + x2) // 2, (y1 + y2) // 2],
            "metric_height_m": est_h,
            "relative_height_units": round(est_h * 1.8, 1),
            "uncertainty_range_m": [round(est_h * 0.88, 1), round(est_h * 1.14, 1)],
            "elevation_top_m": round(top_el, 1),
            "ground_elevation_m": round(ground_el, 1),
            "risk_level": "HIGH SLOPE HAZARD" if b_type.find("At Risk") != -1 else "STABLE RIDGE"
        })
        
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img_np = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 5, img_np.shape)
    img_np = np.clip(img_np + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_np)
    
    rgb_path = os.path.join(SAMPLE_DIR, "hilly_landslide_rgb.png")
    img.save(rgb_path, quality=95)
    
    dsm_min, dsm_max = float(np.min(valley)), float(np.max(valley))
    
    metadata = {
        "id": "hilly_landslide",
        "title": "Himalayan Mountain Valley (Landslide & Road Hazard)",
        "theme": "Disaster Management - Landslide & Transport Disruption",
        "description": "Satellite imagery of steep mountainous terrain in Uttarakhand/Himachal with active slope failure severing highway connectivity.",
        "dimensions": [width, height],
        "gsd_m_per_px": 0.50,
        "georeferenced": True,
        "crs": "EPSG:32644 (UTM Zone 44N)",
        "bounds": [78.4521, 30.3120, 78.4777, 30.3376],
        "metric_elevation_range": [round(dsm_min, 1), round(dsm_max, 1)],
        "relative_elevation_range": [0.0, 100.0],
        "mean_elevation_m": round(float(np.mean(valley)), 1),
        "flood_water_level_m": 125.0,
        "structures": structures_meta,
        "hazard_zones": {
            "high_slope_area_pct": 48.6,
            "blocked_corridors": ["National Highway Sector 4 (km 42.5)"],
            "recommended_action": "Clear debris at sector KM-42.5; evacuate slope dwelling H-006 due to secondary slip hazard."
        }
    }
    
    with open(os.path.join(SAMPLE_DIR, "hilly_landslide_meta.json"), "w") as f:
        json.dump(metadata, f, indent=2)
        
    np.save(os.path.join(SAMPLE_DIR, "hilly_landslide_dsm.npy"), valley.astype(np.float32))
    print("Hilly landslide scene generated successfully.")

def generate_dense_urban_scene():
    width, height = 512, 512
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    
    # Coastal urban grid with gentle 2m to 12m slope
    terrain = 4.0 + 5.0 * xx + 3.0 * yy
    # Sea / bay on right side
    sea_mask = xx > 0.82
    terrain[sea_mask] = 1.0
    
    img = Image.new("RGB", (width, height), (50, 55, 60)) # Urban concrete base
    draw = ImageDraw.Draw(img)
    
    # Sea / ocean on right
    draw.rectangle([int(width * 0.82), 0, width, height], fill=(25, 60, 85))
    
    # Coastal seawall / promenade
    draw.rectangle([int(width * 0.79), 0, int(width * 0.82), height], fill=(130, 130, 135))
    
    # Road grid
    for rx in [0.2, 0.42, 0.62]:
        draw.rectangle([int(width * rx), 0, int(width * rx + 14), height], fill=(40, 40, 45))
    for ry in [0.25, 0.52, 0.78]:
        draw.rectangle([0, int(height * ry), int(width * 0.79), int(height * ry + 14)], fill=(40, 40, 45))
        
    # High-rise skyscrapers and commercial towers
    buildings = [
        # (x1, y1, x2, y2, height_m, color, type, label)
        (30, 30, 85, 105, 78.0, (140, 170, 200), "Financial Tower Alpha", "U-101"),
        (120, 25, 185, 115, 105.0, (160, 190, 220), "Skyline Center (105m)", "U-102"),
        (240, 35, 300, 100, 62.0, (180, 175, 165), "Commerce Plaza", "U-103"),
        (335, 40, 395, 95, 45.0, (170, 160, 150), "Harbor Office 1", "U-104"),
        
        (30, 150, 90, 245, 88.0, (150, 180, 210), "Metropolis Tower", "U-105"),
        (125, 160, 190, 240, 94.0, (170, 195, 225), "Grand Hotel & Suites", "U-106"),
        (235, 150, 305, 230, 52.0, (165, 160, 155), "City Hall Annex", "U-107"),
        (335, 160, 390, 240, 36.0, (155, 150, 145), "Harbor Logistics A", "U-108"),
        
        (35, 290, 85, 375, 58.0, (175, 170, 160), "Tech Park Unit 1", "U-109"),
        (120, 300, 195, 370, 68.0, (160, 185, 215), "Tech Park Unit 2", "U-110"),
        (240, 300, 295, 370, 42.0, (170, 165, 160), "Civic Library", "U-111"),
        (330, 290, 400, 380, 28.0, (145, 140, 135), "Port Warehouse West", "U-112"),
        
        (435, 150, 495, 250, 22.0, (140, 135, 130), "Seaport Terminal", "U-113"),
        (435, 290, 495, 380, 18.5, (135, 130, 125), "Container Yard Depot", "U-114"),
    ]
    
    structures_meta = []
    for b in buildings:
        x1, y1, x2, y2, b_height, color, b_type, label = b
        draw.rectangle([x1, y1, x2, y2], fill=color, outline=(20, 20, 25), width=2)
        # Rooftop design
        draw.rectangle([x1+4, y1+4, x2-4, y2-4], fill=tuple(int(c*0.85) for c in color))
        draw.ellipse([x1+8, y1+8, x1+22, y1+22], fill=(210, 80, 60)) # Helipad / antenna
        terrain[y1:y2, x1:x2] += b_height
        ground_el = float(np.mean(terrain[max(0, y1-5):y1, max(0, x1-5):x1])) if y1 > 5 else 6.0
        top_el = float(terrain[(y1+y2)//2, (x1+x2)//2])
        est_h = round(top_el - ground_el, 1)
        structures_meta.append({
            "id": label,
            "type": b_type,
            "bbox": [x1, y1, x2, y2],
            "center": [(x1 + x2) // 2, (y1 + y2) // 2],
            "metric_height_m": est_h,
            "relative_height_units": round(est_h * 2.4, 1),
            "uncertainty_range_m": [round(est_h * 0.92, 1), round(est_h * 1.09, 1)],
            "elevation_top_m": round(top_el, 1),
            "ground_elevation_m": round(ground_el, 1),
            "risk_level": "STORM SURGE HAZARD" if ground_el < 5.0 else "STRUCTURAL STABLE"
        })
        
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img_np = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 3, img_np.shape)
    img_np = np.clip(img_np + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_np)
    
    rgb_path = os.path.join(SAMPLE_DIR, "dense_urban_rgb.png")
    img.save(rgb_path, quality=95)
    
    dsm_min, dsm_max = float(np.min(terrain)), float(np.max(terrain))
    
    metadata = {
        "id": "dense_urban",
        "title": "Coastal Mega-City & High-Rise Infrastructure (Mumbai / Chennai)",
        "theme": "Disaster Management - Storm Surge & Structural Vulnerability",
        "description": "High-density coastal urban core with high-rise infrastructure (up to 105m) vulnerable to cyclone storm surges and coastal inundation.",
        "dimensions": [width, height],
        "gsd_m_per_px": 0.20,
        "georeferenced": True,
        "crs": "EPSG:32643 (UTM Zone 43N)",
        "bounds": [72.8250, 18.9220, 72.8450, 18.9420],
        "metric_elevation_range": [round(dsm_min, 1), round(dsm_max, 1)],
        "relative_elevation_range": [0.0, 100.0],
        "mean_elevation_m": round(float(np.mean(terrain)), 1),
        "flood_water_level_m": 5.5,
        "structures": structures_meta,
        "hazard_zones": {
            "storm_surge_risk_pct": 21.4,
            "tallest_structure": "U-102 (105.0m)",
            "recommended_action": "Reinforce coastal perimeter at Seaport Terminal U-113; monitor storm surge flood line."
        }
    }
    
    with open(os.path.join(SAMPLE_DIR, "dense_urban_meta.json"), "w") as f:
        json.dump(metadata, f, indent=2)
        
    np.save(os.path.join(SAMPLE_DIR, "dense_urban_dsm.npy"), terrain.astype(np.float32))
    print("Dense urban scene generated successfully.")

if __name__ == "__main__":
    generate_flooded_urban_scene()
    generate_hilly_landslide_scene()
    generate_dense_urban_scene()
    print("All sample scenes generated!")

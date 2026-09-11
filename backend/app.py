import os
import io
import json
import base64
import numpy as np
from PIL import Image, ImageOps
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from services.depth_service import DepthEstimationService
from services.dsm_service import DSMService
from services.reconstruction_service import Reconstruction3DService
from services.disaster_service import DisasterIntelligenceService
from services.report_service import ReportExportService

app = FastAPI(
    title="DepthWizard API",
    description="Single-View Height Estimation & 3D Flythrough for Disaster Management (SIH26175)",
    version="1.0.0"
)

# CORS middleware for frontend flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
depth_service = DepthEstimationService()
dsm_service = DSMService()
recon_service = Reconstruction3DService()
disaster_service = DisasterIntelligenceService()
report_service = ReportExportService()

# Cache active session scene in memory
active_session = {
    "scene_id": "flooded_urban",
    "scene_title": "Flooded Urban River Delta (Assam/Kerala Flood Scenario)",
    "is_calibrated": True,
    "rgb_img": None,
    "rgb_b64": "",
    "norm_depth": None,
    "elevation_grid": None,
    "scene_meta": None,
    "depth_result": None,
    "dsm_result": None,
    "disaster_eval": None,
    "recon_data": None
}

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.on_event("startup")
def load_default_scene():
    """Pre-loads the default sample scene on server launch."""
    load_scene_by_id("flooded_urban")

def load_scene_by_id(scene_id: str):
    rgb_path = os.path.join(SAMPLE_DIR, f"{scene_id}_rgb.png")
    meta_path = os.path.join(SAMPLE_DIR, f"{scene_id}_meta.json")
    dsm_path = os.path.join(SAMPLE_DIR, f"{scene_id}_dsm.npy")
    
    if not (os.path.exists(rgb_path) and os.path.exists(meta_path) and os.path.exists(dsm_path)):
        return False
        
    with open(meta_path, "r") as f:
        meta = json.load(f)
        
    img = Image.open(rgb_path).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    rgb_b64 = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
    
    depth_res = depth_service.estimate_depth(img, scene_id=scene_id)
    
    raw_dsm = np.load(dsm_path)
    d_min, d_max = float(np.min(raw_dsm)), float(np.max(raw_dsm))
    norm_depth = (raw_dsm - d_min) / (d_max - d_min + 1e-6)
    
    dsm_res = dsm_service.generate_dsm(norm_depth, is_calibrated=True, scene_meta=meta)
    disaster_eval = disaster_service.evaluate_disaster_risks(
        dsm_res["elevation_grid"], 
        water_level=meta.get("flood_water_level_m", 8.5),
        scene_meta=meta,
        is_calibrated=True
    )
    recon_data = recon_service.prepare_3d_terrain_data(dsm_res["elevation_grid"], grid_res=128)
    
    active_session["scene_id"] = scene_id
    active_session["scene_title"] = meta["title"]
    active_session["is_calibrated"] = True
    active_session["rgb_img"] = img
    active_session["rgb_b64"] = rgb_b64
    active_session["norm_depth"] = norm_depth
    active_session["elevation_grid"] = dsm_res["elevation_grid"]
    active_session["scene_meta"] = meta
    active_session["depth_result"] = depth_res
    active_session["dsm_result"] = dsm_res
    active_session["disaster_eval"] = disaster_eval
    active_session["recon_data"] = recon_data
    return True

@app.get("/api/health")
def get_health():
    return {
        "status": "online",
        "system": "DepthWizard Engine (SIH26175)",
        "theme": "Disaster Management",
        "version": "1.0.0",
        "active_mode": "Calibrated Metric Mode" if active_session["is_calibrated"] else "Relative Elevation Mode",
        "active_scene": active_session["scene_id"]
    }

@app.get("/api/scenes")
def list_demo_scenes():
    scenes = [
        {
            "id": "flooded_urban",
            "title": "Flooded Urban River Delta (Assam/Kerala)",
            "theme": "Flood Inundation & Isolation",
            "description": "Optical satellite view of a river delta with heavy monsoonal inundation, submerged residential zones, and isolated high-rise clusters.",
            "is_calibrated": True,
            "elevation_range": "2.5m – 48.5m",
            "gsd": "0.25 m/px",
            "thumbnail_b64": active_session["rgb_b64"] if active_session["scene_id"] == "flooded_urban" else ""
        },
        {
            "id": "hilly_landslide",
            "title": "Himalayan Mountain Valley (Uttarakhand)",
            "theme": "Landslide & Road Blockage",
            "description": "Satellite imagery of steep mountainous terrain in Uttarakhand/Himachal with active slope failure severing highway connectivity.",
            "is_calibrated": True,
            "elevation_range": "110m – 380m",
            "gsd": "0.50 m/px",
            "thumbnail_b64": ""
        },
        {
            "id": "dense_urban",
            "title": "Coastal Mega-City & High-Rise Infrastructure (Mumbai/Chennai)",
            "theme": "Storm Surge & Structural Vulnerability",
            "description": "High-density coastal urban core with high-rise infrastructure (up to 105m) vulnerable to cyclone storm surges.",
            "is_calibrated": True,
            "elevation_range": "1.0m – 105.0m",
            "gsd": "0.20 m/px",
            "thumbnail_b64": ""
        }
    ]
    return {"scenes": scenes}

@app.get("/api/scene/{scene_id}")
def load_scene(scene_id: str):
    success = load_scene_by_id(scene_id)
    if not success:
        raise HTTPException(status_code=404, detail="Scene not found")
    return get_current_state()

@app.get("/api/state")
def get_current_state():
    if active_session["norm_depth"] is None:
        raise HTTPException(status_code=400, detail="No active scene analyzed yet")
    return {
        "scene_id": active_session["scene_id"],
        "scene_title": active_session["scene_title"],
        "is_calibrated": active_session["is_calibrated"],
        "rgb_image_b64": active_session["rgb_b64"],
        "scene_meta": active_session["scene_meta"],
        "depth_result": {
            "is_demo_data": active_session["depth_result"]["is_demo_data"],
            "depth_map_shape": active_session["depth_result"]["depth_map_shape"],
            "colormaps": active_session["depth_result"]["colormaps"],
            "confidence_map_b64": active_session["depth_result"]["confidence_map_b64"],
            "stats": active_session["depth_result"]["stats"],
            "histogram": active_session["depth_result"]["histogram"]
        },
        "dsm_result": {
            "stats": active_session["dsm_result"]["stats"],
            "dsm_terrain_b64": active_session["dsm_result"]["dsm_terrain_b64"],
            "dsm_turbo_b64": active_session["dsm_result"]["dsm_turbo_b64"],
            "slope_map_b64": active_session["dsm_result"]["slope_map_b64"],
            "hillshade_b64": active_session["dsm_result"]["hillshade_b64"],
            "profile_slice": active_session["dsm_result"]["profile_slice"]
        },
        "disaster_eval": active_session["disaster_eval"],
        "recon_data": active_session["recon_data"],
        "input_rgb_b64": active_session["rgb_b64"],
        "output_depth_b64": active_session["depth_result"]["colormaps"]["turbo"] if active_session.get("depth_result") else "",
        "output_depth_inferno_b64": active_session["depth_result"]["colormaps"]["inferno"] if active_session.get("depth_result") else "",
        "output_depth_viridis_b64": active_session["depth_result"]["colormaps"]["viridis"] if active_session.get("depth_result") else "",
        "output_dsm_b64": active_session["dsm_result"]["dsm_terrain_b64"] if active_session.get("dsm_result") else "",
        "output_image_b64": active_session["depth_result"]["colormaps"]["turbo"] if active_session.get("depth_result") else ""
    }

@app.post("/api/analyze")
async def analyze_uploaded_image(
    file: UploadFile = File(...),
    mode: str = Form("relative"),
    gsd_m: float = Form(0.5),
    anchor_height_m: float = Form(20.0)
):
    """
    Accepts user-uploaded JPG/PNG/GeoTIFF image and runs the complete AI pipeline.
    """
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        w, h = img.size
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        rgb_b64 = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
        
        is_calibrated = (mode == "calibrated")
        
        # AI Depth Estimation using dense multi-scale monocular depth pipeline
        depth_res = depth_service.estimate_depth(img)
        
        if "norm_depth_array" in depth_res and depth_res["norm_depth_array"] is not None:
            norm_depth = depth_res["norm_depth_array"]
        else:
            gray = np.array(ImageOps.grayscale(img)).astype(np.float32) / 255.0
            norm_depth = np.clip(1.0 - (gray * 0.7 + np.linspace(0.4, 0.1, h)[:, None]), 0, 1)
        
        custom_meta = {
            "id": f"upload_{file.filename[:16]}",
            "title": f"Custom Imagery: {file.filename}",
            "theme": "Disaster Intelligence Assessment",
            "description": f"Analyzed single optical RGB view ({w}x{h} px). Mode: {'Calibrated Metric' if is_calibrated else 'Relative Elevation'}.",
            "dimensions": [w, h],
            "gsd_m_per_px": gsd_m if is_calibrated else None,
            "georeferenced": is_calibrated,
            "structures": []
        }
        
        calib_params = {
            "anchor_height_m": anchor_height_m,
            "anchor_rel_delta": 0.35,
            "base_elevation_m": 10.0
        }
        
        dsm_res = dsm_service.generate_dsm(norm_depth, is_calibrated=is_calibrated, calibration_params=calib_params, scene_meta=custom_meta)
        
        default_water = float(np.min(dsm_res["elevation_grid"])) + 0.25 * float(np.ptp(dsm_res["elevation_grid"]))
        disaster_eval = disaster_service.evaluate_disaster_risks(
            dsm_res["elevation_grid"],
            water_level=default_water,
            scene_meta=custom_meta,
            is_calibrated=is_calibrated
        )
        
        recon_data = recon_service.prepare_3d_terrain_data(dsm_res["elevation_grid"], grid_res=128)
        
        active_session["scene_id"] = custom_meta["id"]
        active_session["scene_title"] = custom_meta["title"]
        active_session["is_calibrated"] = is_calibrated
        active_session["rgb_img"] = img
        active_session["rgb_b64"] = rgb_b64
        active_session["norm_depth"] = norm_depth
        active_session["elevation_grid"] = dsm_res["elevation_grid"]
        active_session["scene_meta"] = custom_meta
        active_session["depth_result"] = depth_res
        active_session["dsm_result"] = dsm_res
        active_session["disaster_eval"] = disaster_eval
        active_session["recon_data"] = recon_data
        
        return get_current_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")

@app.post("/api/calibrate")
def set_calibration_mode(data: dict):
    """Toggles or updates scale calibration."""
    is_calibrated = bool(data.get("is_calibrated", True))
    anchor_h = float(data.get("anchor_height_m", 20.0))
    gsd = float(data.get("gsd_m_per_px", 0.25))
    
    active_session["is_calibrated"] = is_calibrated
    if active_session["scene_meta"]:
        active_session["scene_meta"]["gsd_m_per_px"] = gsd
        
    calib_params = {
        "anchor_height_m": anchor_h,
        "anchor_rel_delta": 0.35,
        "base_elevation_m": 5.0
    }
    
    dsm_res = dsm_service.generate_dsm(
        active_session["norm_depth"],
        is_calibrated=is_calibrated,
        calibration_params=calib_params,
        scene_meta=active_session["scene_meta"]
    )
    
    active_session["elevation_grid"] = dsm_res["elevation_grid"]
    active_session["dsm_result"] = dsm_res
    
    def_water = float(np.min(dsm_res["elevation_grid"])) + 0.3 * float(np.ptp(dsm_res["elevation_grid"]))
    active_session["disaster_eval"] = disaster_service.evaluate_disaster_risks(
        dsm_res["elevation_grid"],
        water_level=def_water,
        scene_meta=active_session["scene_meta"],
        is_calibrated=is_calibrated
    )
    
    active_session["recon_data"] = recon_service.prepare_3d_terrain_data(dsm_res["elevation_grid"], grid_res=128)
    return get_current_state()

@app.post("/api/inspect-point")
def inspect_point(data: dict):
    """Calculates height and risk info when user clicks on building/terrain."""
    x_pct = float(data.get("x_pct", 0.5))
    y_pct = float(data.get("y_pct", 0.5))
    
    if active_session["elevation_grid"] is None:
        raise HTTPException(status_code=400, detail="No active terrain")
        
    info = dsm_service.inspect_structure_at_point(
        active_session["elevation_grid"],
        x_pct=x_pct,
        y_pct=y_pct,
        is_calibrated=active_session["is_calibrated"],
        scene_meta=active_session["scene_meta"]
    )
    return info

@app.post("/api/disaster-eval")
def update_disaster_water_level(data: dict):
    """Updates flood water level simulation dynamically."""
    water_level = float(data.get("water_level", 8.5))
    if active_session["elevation_grid"] is None:
        raise HTTPException(status_code=400, detail="No active terrain")
        
    eval_res = disaster_service.evaluate_disaster_risks(
        active_session["elevation_grid"],
        water_level=water_level,
        scene_meta=active_session["scene_meta"],
        is_calibrated=active_session["is_calibrated"]
    )
    active_session["disaster_eval"] = eval_res
    return eval_res

@app.get("/api/export/{scene_id}/report")
def export_report_html(scene_id: str):
    """Exports printable HTML disaster brief."""
    if active_session["dsm_result"] is None:
        raise HTTPException(status_code=400, detail="No active data")
        
    html = report_service.generate_html_report(
        scene_id=active_session["scene_id"],
        scene_title=active_session["scene_title"],
        is_calibrated=active_session["is_calibrated"],
        dsm_stats=active_session["dsm_result"]["stats"],
        disaster_eval=active_session["disaster_eval"]
    )
    return HTMLResponse(content=html)

@app.get("/api/export/{scene_id}/geojson")
def export_geojson(scene_id: str):
    """Exports GIS GeoJSON feature collection."""
    if active_session["disaster_eval"] is None:
        raise HTTPException(status_code=400, detail="No active data")
        
    geojson = report_service.generate_geojson(
        scene_meta=active_session["scene_meta"] or {},
        disaster_eval=active_session["disaster_eval"],
        is_calibrated=active_session["is_calibrated"]
    )
    return JSONResponse(
        content=geojson,
        headers={"Content-Disposition": f"attachment; filename=depthwizard_{scene_id}_features.geojson"}
    )

@app.get("/api/export/{scene_id}/csv")
def export_csv(scene_id: str):
    """Exports CSV structure height table."""
    if active_session["disaster_eval"] is None:
        raise HTTPException(status_code=400, detail="No active data")
        
    csv_str = report_service.generate_csv(
        disaster_eval=active_session["disaster_eval"],
        is_calibrated=active_session["is_calibrated"]
    )
    return PlainTextResponse(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=depthwizard_{scene_id}_structures.csv"}
    )

@app.get("/api/export/{scene_id}/obj")
def export_3d_obj(scene_id: str):
    """Exports Wavefront OBJ 3D terrain mesh."""
    if active_session["elevation_grid"] is None:
        raise HTTPException(status_code=400, detail="No active terrain")
        
    obj_str = recon_service.generate_obj_file(active_session["elevation_grid"], grid_res=128)
    return PlainTextResponse(
        content=obj_str,
        headers={"Content-Disposition": f"attachment; filename=depthwizard_{scene_id}_terrain.obj"}
    )

# Serve Test Images & Frontend static files
TEST_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_images_for_upload")
if os.path.exists(TEST_IMAGES_DIR):
    app.mount("/test_images", StaticFiles(directory=TEST_IMAGES_DIR), name="test_images")

if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    print("Starting DepthWizard Server on http://0.0.0.0:8000 ...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)

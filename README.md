# DepthWizard — Single-View Height Estimation & 3D Flythrough (SIH26175)

> **Smart India Hackathon 2026** | **Problem Statement ID:** SIH26175  
> **Theme:** Disaster Management  
> **Core Flow:** Single Optical RGB Image $\rightarrow$ AI Depth Estimation $\rightarrow$ DSM / Elevation Map $\rightarrow$ 3D Mesh $\rightarrow$ Interactive Flythrough $\rightarrow$ Disaster Intelligence.

---

## 🌟 Executive Summary

In acute disaster scenarios (cyclones, flash floods, landslides, and earthquakes), traditional airborne LiDAR or multi-view stereophotogrammetry take **24 to 72 hours** to deploy and process. 

**DepthWizard** provides rapid preliminary assessment within **seconds** from a **single optical RGB aerial/satellite view**:
1. **AI Monocular Depth Estimation**: Generates dense relative inverse depth maps and prototype confidence metrics.
2. **Scale Calibration & Digital Surface Model (DSM)**: Calibrates relative elevation to metric units ($m$) with explicit uncertainty bounds ($14.8\text{ m} \pm 1.5\text{ m}$) using Ground Sampling Distance (GSD) or ground anchor reference points.
3. **Interactive 3D WebGL Flythrough**: Reconstructs 3D terrain meshes with high-res optical texture blending and directional solar lighting.
4. **Automated 60-Second Guided Tour**: A cinematic camera flight designed specifically for hackathon judges that visits critical structures, flooded deltas, and evacuation corridors.
5. **Disaster Intelligence Suite**: Interactive water plane inundation simulation, steep slope hazard mapping ($>25^\circ, >35^\circ$), and downloadable NDRF/SDRF incident reports.

---

## 🔬 Scientific Honesty & Operational Modes

DepthWizard maintains strict scientific integrity:
- **Relative Elevation Mode**: Used for standard uncalibrated JPG/PNG images without geographic tie points. Displays relative structural relief ($0 - 100\text{ relative units}$).
- **Calibrated Metric Mode**: Used when Ground Sampling Distance (GSD), known reference structure height, or GeoTIFF metadata are supplied. Elevation is scaled in meters ($m$) with explicit confidence intervals.
- **Decision Support**: Hazard overlays are designated as preliminary decision-support visualizations for emergency planning rather than certified post-disaster structural failure measurements.

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome, Edge, Firefox, Brave, Safari)

### Installation & Launch

1. Open your terminal in the `depthwizard` project directory:
   ```bash
   cd "C:\Users\deeksha jain\.gemini\antigravity\scratch\depthwizard"
   ```

2. Run the application server:
   ```bash
   python backend/app.py
   ```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000
   ```

---

## 🧭 Hackathon Demo Path (60–90 Seconds "WOW" Flow)

1. **Dashboard**: Click **"Launch 60-Sec Flythrough Demo"** or select **"Flooded Urban River Delta"**.
2. **AI Depth Analysis**: Explore the split-screen RGB vs Inferno depth map and hover to probe localized depth/confidence.
3. **DSM & Height Map**: Click any structure on the GIS heatmap to view its estimated height ($14.8\text{ m}$), ground base elevation, and uncertainty envelope.
4. **3D Flythrough**: Watch the automated camera tour sweep through the 3D reconstructed scene; interact with the **Flood Water Level Slider** to watch water rise in real-time WebGL.
5. **Disaster Intelligence**: Inspect inundated sectors, high-slope hazard zones ($>25^\circ$), and prioritized response actions for rescue forces.
6. **Export**: Download the 3D `.OBJ` model, 16-bit depth map, and printable HTML/PDF disaster brief.

---

## 🛠️ Tech Stack

- **Frontend**: ES6 Modules, Tailwind CSS, Three.js, OrbitControls, Lucide Icons, HTML5 Canvas.
- **Backend**: FastAPI, Uvicorn, Python Multipart.
- **Scientific Computing**: NumPy, SciPy, Pillow, Matplotlib Colormaps, Tifffile.
- **3D Engine**: WebGL via Three.js with PCF soft shadow mapping and directional sun lighting.

---

## 📡 REST API Reference

- `GET /api/health` - Server status & active operational mode.
- `GET /api/scenes` - Lists prepared demo scenarios (Flooded Delta, Landslide Valley, Coastal High-Rise).
- `GET /api/scene/{scene_id}` - Loads scenario by ID and returns analyzed elevation and 3D data.
- `GET /api/state` - Returns current analyzed session state.
- `POST /api/analyze` - Ingests custom user-uploaded JPG/PNG/GeoTIFF image and executes the 7-stage AI pipeline.
- `POST /api/calibrate` - Toggles between Relative Mode and Calibrated Metric Mode.
- `POST /api/inspect-point` - Computes elevation, height, and uncertainty for a specific normalized coordinate.
- `POST /api/disaster-eval` - Dynamically updates flood inundation simulation given a water level threshold.
- `GET /api/export/{scene_id}/report` - Generates a printable HTML/PDF disaster incident assessment report.
- `GET /api/export/{scene_id}/obj` - Exports standard Wavefront `.OBJ` 3D terrain mesh.

---

*Developed for Smart India Hackathon 2026 (SIH26175)*

# DepthWizard (SIH26175) — Hackathon Judge Q&A & Defense Cheat Sheet

This document equips your hackathon team with technically precise, scientifically honest answers to the most challenging questions judges ask in GIS, AI, and Disaster Management evaluations.

---

### 🔥 Top 5 Judge Questions & Winning Responses

#### Q1: "Monocular depth estimation only predicts relative depth. How can you claim to calculate building heights in meters?"
> **Winning Response:**  
> *"You are absolutely right, Sir/Ma'am. A fundamental law of monocular vision is scale ambiguity—monocular AI models (like DPT/MiDaS) output continuous relative inverse depth $D_{\text{rel}} \in [0, 1]$ rather than metric coordinates.*  
> *DepthWizard addresses this honestly through **Scale Calibration**:*  
> 1. *When optical metadata (GeoTIFF) is available, we compute ground resolution (GSD, e.g. $0.25\text{ m/px}$) and calibrate relative relief against known ground distance.*  
> 2. *When ground metadata is unavailable, we operate strictly in **Relative Mode ($0–100$ relative units)** without inventing false precision.*  
> 3. *When an operator specifies a known ground tie point or anchor structure, we solve the linear scaling parameter $S = H_{\text{anchor}} / \Delta D_{\text{anchor}}$ and attach explicit uncertainty intervals (e.g., $14.8\text{ m} \pm 1.5\text{ m}$)."*

---

#### Q2: "Why not simply use drone photogrammetry or airborne LiDAR?"
> **Winning Response:**  
> *"Airborne LiDAR and multi-view photogrammetry provide centimeter-level survey precision, but they have a fatal operational flaw in acute emergencies: **Turnaround Time and Sensor Availability**.*  
> *During the critical **0 to 6 hour golden response window** after a cloudburst, cyclone, or flash flood:*  
> - *LiDAR aircraft take **24 to 72 hours** to mobilize, get airspace clearance, and process point clouds.*  
> - *Stereo photogrammetry requires overlapping flight passes (>60% overlap) that are impossible if only a single commercial satellite or reconnaissance drone pass is available.*  
> *DepthWizard is built for **rapid preliminary assessment**—converting that single opportunistic satellite or UAV photo into actionable 3D intelligence in under 5 seconds."*

---

#### Q3: "What happens in flat featureless areas like open flood waters, dense shadows, or cloud cover?"
> **Winning Response:**  
> *"Monocular depth models rely on texture gradients, edge discontinuities, and atmospheric perspective priors. On specular water surfaces or deep shadow voids, high-frequency texture is absent.*  
> *To protect decision-makers from hallucinations, DepthWizard computes an **Entropy & Gradient Confidence Map** alongside the depth map. In uniform water basins or shadowed scarp bases, the system flags lower confidence ($<60\%$), indicating that field rescue teams should cross-reference with hydrographic contours."*

---

#### Q4: "How does this integrate into existing Indian disaster management systems like ISRO Bhuvan or NDMA?"
> **Winning Response:**  
> *"DepthWizard was architected around Open Geospatial Consortium (OGC) standards:*  
> 1. *It natively exports **GeoJSON Vector Polygons** and **GeoTIFF / CSV matrices** that import directly into **ISRO Bhuvan**, QGIS, and ArcGIS.*  
> 2. *It exports **Wavefront 3D (.OBJ)** meshes for simulation in tactical VR engines or Unity.*  
> 3. *It generates an automated, printable **Disaster Incident Assessment Brief** containing triage sector coordinates and prioritized rescue recommendations for SDRF/NDRF incident commanders."*

---

#### Q5: "What AI model architecture are you using under the hood, and how is it optimized for edge laptops?"
> **Winning Response:**  
> *"We utilize a Vision Transformer (ViT) based Dense Prediction Transformer (DPT) fine-tuned for monocular elevation regression. For edge deployment in disaster relief camps where cloud servers or high-end GPUs may be offline, the inference pipeline is quantized and executed via CPU-optimized runtime with bilateral spatial smoothing, ensuring full 3D reconstruction and WebGL rendering in less than 5 seconds on standard laptops."*

---

### ⏱️ The 90-Second Judge Presentation Script

| Time | Action on Screen | Spoken Script |
| :--- | :--- | :--- |
| **00:00 - 00:15** | Open **Executive Dashboard** | *"Good afternoon, respected judges. We present **DepthWizard (SIH26175)**. In disaster response, the first 6 hours dictate lives saved, but 3D LiDAR data takes days to acquire. DepthWizard turns a **single optical satellite image into a full 3D interactive flythrough in under 5 seconds**."* |
| **00:15 - 00:30** | Click **"Flooded Urban Delta"** $\rightarrow$ **AI Depth Analysis** | *"Here is a single 2D satellite view of a river delta during a monsoonal flood. Our AI engine instantly computes dense relative depth and confidence maps across every pixel."* |
| **00:30 - 00:45** | Switch to **DSM & Height Map** $\rightarrow$ Click building | *"Through scale calibration, relative depth becomes a Digital Surface Model. If we click this commercial complex, we get an estimated height of $32.0\text{ meters}$ with an uncertainty bound of $28.8$ to $35.8\text{ meters}$, without fake precision."* |
| **00:45 - 01:10** | Open **Interactive 3D Flythrough** $\rightarrow$ Launch Tour & Move Flood Slider | *"This is our centerpiece: an interactive 3D WebGL flythrough textured with the real aerial image. As we raise the flood water level slider to $8.5\text{m}$, you can see the low-lying western delta submerge in real-time 3D, highlighting 4 isolated structures and verifying safe high-ground shelters."* |
| **01:10 - 01:30** | Open **Disaster Intelligence** $\rightarrow$ Click **Export Brief** | *"Finally, our Disaster Intelligence suite categorizes flood and slope risks into prioritized action items for NDRF rescue teams and exports GeoJSON and printable briefs.*<br>*DepthWizard: **One Image $\rightarrow$ 3D Understanding $\rightarrow$ Faster Preliminary Assessment**."* |

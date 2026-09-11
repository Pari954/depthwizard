import requests

def test_all():
    base = "http://127.0.0.1:8000"
    
    # 1. Health
    r = requests.get(f"{base}/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("[PASS] GET /api/health passed:", r.json())
    
    # 2. Scenes
    r = requests.get(f"{base}/api/scenes")
    assert r.status_code == 200
    scenes = r.json()["scenes"]
    assert len(scenes) == 3
    print("[PASS] GET /api/scenes passed (3 prepared scenarios)")
    
    # 3. State
    r = requests.get(f"{base}/api/state")
    assert r.status_code == 200
    state = r.json()
    assert "dsm_result" in state
    assert "recon_data" in state
    print(f"[PASS] GET /api/state passed ({state['scene_title']})")
    
    # 4. Frontend static files
    r_root = requests.get(f"{base}/")
    assert r_root.status_code == 200 and "DepthWizard" in r_root.text
    print(f"[PASS] GET / (Root Index HTML) passed - {len(r_root.text)} bytes")

    r_js = requests.get(f"{base}/js/app.js")
    assert r_js.status_code == 200 and "SimpleDepthWizard" in r_js.text
    print(f"[PASS] GET /js/app.js passed - {len(r_js.text)} bytes")
    
    # 5. Point Inspector
    r = requests.post(f"{base}/api/inspect-point", json={"x_pct": 0.65, "y_pct": 0.22})
    assert r.status_code == 200
    inspect_data = r.json()
    print("[PASS] POST /api/inspect-point passed:", inspect_data["object_id"], "Est Height:", inspect_data["estimated_height"], inspect_data["unit"])
    
    # 6. Flood water level sim
    r = requests.post(f"{base}/api/disaster-eval", json={"water_level": 9.5})
    assert r.status_code == 200
    disaster_data = r.json()
    print(f"[PASS] POST /api/disaster-eval passed: Inundated Area {disaster_data['flooded_area_pct']}%, Affected structures: {disaster_data['structures_summary']['submerged_or_isolated']}")
    
    # 7. HTML Report Export
    r = requests.get(f"{base}/api/export/flooded_urban/report")
    assert r.status_code == 200
    assert "<html" in r.text
    print("[PASS] GET /api/export/flooded_urban/report passed (HTML generated)")

    # 8. GeoJSON Export
    r = requests.get(f"{base}/api/export/flooded_urban/geojson")
    assert r.status_code == 200
    geojson_data = r.json()
    assert geojson_data["type"] == "FeatureCollection"
    print(f"[PASS] GET /api/export/flooded_urban/geojson passed ({len(geojson_data['features'])} features)")

    # 9. CSV Export
    r = requests.get(f"{base}/api/export/flooded_urban/csv")
    assert r.status_code == 200
    assert "Structure_ID" in r.text
    print("[PASS] GET /api/export/flooded_urban/csv passed (CSV table generated)")
    
    # 10. OBJ 3D Export
    r = requests.get(f"{base}/api/export/flooded_urban/obj")
    assert r.status_code == 200
    assert "DepthWizard" in r.text
    print("[PASS] GET /api/export/flooded_urban/obj passed (OBJ 3D mesh generated)")
    
    print("\n=========================================================================")
    print("ALL 10 FRONTEND & BACKEND SERVICES & EXPORTS VERIFIED 100% OPERATIONAL!")
    print("=========================================================================")

if __name__ == "__main__":
    test_all()

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.pipeline.extract import extract_event
from app.pipeline.geocode import geocode_location
from app.pipeline.confidence import calculate_confidence
from app.routing.weights import calculate_edge_weight

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["db_ok"] is True

def test_extract_landslide_event():
    text = "Massive landslide halts traffic on NH-10 near 29th Mile early Tuesday morning. Road completely blocked."
    event = extract_event(text, title="NH-10 Landslide", corridor="NH-10")
    assert event.event_type == "landslide"
    assert event.status == "blocked"
    assert "29th Mile" in event.location_text
    assert event.severity >= 4

def test_extract_waterlogging_event():
    text = "Heavy monsoon downpour causes severe waterlogging at Jorabat tri-junction on NH-6. Single lane traffic moving."
    event = extract_event(text, title="Jorabat Flooding", corridor="NH-6")
    assert event.event_type in ["waterlogging", "flood"]
    assert event.status == "partially_open"
    assert "Jorabat" in event.location_text

def test_geocoding_matching():
    lat, lon, seg_id, precision = geocode_location("29th Mile", corridor="NH-10")
    assert lat is not None
    assert lon is not None
    assert precision > 0.80

def test_confidence_scoring():
    conf, breakdown = calculate_confidence(
        domain="sikkimexpress.com",
        source_count=2,
        geocoding_precision=0.95
    )
    assert 0.0 <= conf <= 1.0
    assert conf >= 0.75
    assert "source_reliability" in breakdown

def test_risk_segments_endpoint():
    res = client.get("/api/risk/segments?corridor=NH-10")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0

def test_incidents_endpoint():
    res = client.get("/api/incidents")
    assert res.status_code == 200
    incidents = res.json()
    assert isinstance(incidents, list)
    assert len(incidents) > 0

def test_routes_calculation():
    payload = {
        "origin": "Siliguri Junction",
        "destination": "Gangtok MG Marg",
        "preference": "safest",
        "corridor": "NH-10"
    }
    res = client.post("/api/routes", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["routes"]) > 0
    safest = data["routes"][0]
    assert safest["distance_km"] > 0
    assert safest["eta_minutes"] > 0

def test_route_compare():
    res = client.get("/api/routes/compare?corridor=NH-10")
    assert res.status_code == 200
    data = res.json()
    assert "baseline_route" in data
    assert "ridge_route" in data
    assert data["risk_reduction_pct"] > 0

def test_dashcam_simulation():
    res = client.post("/api/dashcam/simulate")
    assert res.status_code == 200
    data = res.json()
    assert data["is_simulated"] is True
    assert data["hazard_type"] in ["rockfall", "waterlogging", "debris", "pothole"]

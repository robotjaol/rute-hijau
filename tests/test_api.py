import pytest
from fastapi.testclient import TestClient
from engine.app import app

client = TestClient(app)

SAMPLE_REQUEST = {
    "depot": {"id": 0, "name": "Depot", "lat": -7.321, "lon": 112.718, "demand_kg": 0},
    "points": [
        {"id": 1, "name": "P1", "lat": -7.302, "lon": 112.724, "demand_kg": 90},
        {"id": 2, "name": "P2", "lat": -7.298, "lon": 112.715, "demand_kg": 120},
        {"id": 3, "name": "P3", "lat": -7.309, "lon": 112.731, "demand_kg": 80},
        {"id": 4, "name": "P4", "lat": -7.294, "lon": 112.709, "demand_kg": 110},
    ],
    "fleet": {"vehicles": 2, "capacity_kg": 300},
    "distance_mode": "haversine",
}


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_sample_structure():
    response = client.get("/api/sample")
    assert response.status_code == 200
    data = response.json()
    assert "depot" in data
    assert "points" in data
    assert "fleet" in data
    assert len(data["points"]) > 0


def test_optimize_response_shape():
    response = client.post("/api/optimize", json=SAMPLE_REQUEST)
    assert response.status_code == 200
    data = response.json()
    assert "baseline" in data
    assert "optimized" in data
    assert "savings_km" in data
    assert "savings_percent" in data
    assert "impact" in data
    assert "meta" in data


def test_optimize_impact_fields():
    response = client.post("/api/optimize", json=SAMPLE_REQUEST)
    assert response.status_code == 200
    impact = response.json()["impact"]
    assert "cost_saved_rupiah_per_cycle" in impact
    assert "cost_saved_rupiah_per_year" in impact
    assert "co2_saved_kg_per_cycle" in impact
    assert "co2_saved_kg_per_year" in impact
    assert "assumptions" in impact


def test_optimize_savings_percent_range():
    response = client.post("/api/optimize", json=SAMPLE_REQUEST)
    assert response.status_code == 200
    data = response.json()
    assert 0 <= data["savings_percent"] <= 100


def test_optimize_empty_points_returns_400():
    req = {**SAMPLE_REQUEST, "points": []}
    response = client.post("/api/optimize", json=req)
    assert response.status_code == 400


def test_optimize_over_capacity_returns_409():
    req = {
        **SAMPLE_REQUEST,
        "fleet": {"vehicles": 1, "capacity_kg": 50},
    }
    response = client.post("/api/optimize", json=req)
    assert response.status_code == 409
    assert "kapasitas" in response.json()["detail"].lower()

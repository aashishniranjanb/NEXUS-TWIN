"""
Integration and Unit Tests for AI Dynamic Route & Spillover Optimizer.
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_route_optimization_normal_mode():
    # 1. Fetch real nodes from the network graph first
    graph_res = client.get("/api/v1/network/graph?city=Philadelphia&hour=17&weekend=0")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    
    nodes = [n["intersection_id"] for n in graph_data["nodes"]]
    assert len(nodes) >= 2
    origin = nodes[0]
    destination = nodes[-1]
    
    payload = {
        "origin": origin,
        "destination": destination,
        "mode": "normal",
        "city": "Philadelphia",
        "hour": 17,
        "weekend": 0
    }
    res = client.post("/api/v1/routing/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    assert data["origin"] == origin
    assert data["destination"] == destination
    assert data["mode"] == "normal"
    
    # Check Recommended Route
    rec = data["recommended_route"]
    assert len(rec["nodes"]) >= 2
    assert rec["predicted_eta_s"] > 0.0
    assert 0.0 <= rec["congestion_risk"] <= 1.0
    
    # Check Comparison
    comp = data["comparison"]
    assert comp["baseline_eta_s"] > 0.0
    assert comp["optimized_eta_s"] > 0.0
    assert comp["eta_improvement_pct"] >= 0.0
    
    # Check Reasoning
    assert "why" in data["reasoning"]
    assert len(data["reasoning"]["evidence"]) > 0

def test_route_optimization_emergency_mode():
    graph_res = client.get("/api/v1/network/graph?city=Philadelphia&hour=17&weekend=0")
    nodes = [n["intersection_id"] for n in graph_res.json()["nodes"]]
    origin = nodes[0]
    destination = nodes[-1]
    
    payload = {
        "origin": origin,
        "destination": destination,
        "mode": "emergency",
        "city": "Philadelphia"
    }
    res = client.post("/api/v1/routing/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    assert data["mode"] == "emergency"
    assert "preemption" in data["reasoning"]["why"].lower() or "emergency" in data["reasoning"]["why"].lower()

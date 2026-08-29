"""
Unit and Integration Tests for FastAPI REST Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "version" in data

def test_traffic_state_endpoint():
    payload = {
        "city": "Philadelphia",
        "intersection_id": 463,
        "hour": 17,
        "weekend": 0,
        "entry_heading": "NW",
        "exit_heading": "SE",
        "latitude": 39.9526,
        "longitude": -75.1652
    }
    response = client.post("/api/v1/traffic/state", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intersection_id"] == 463
    assert data["predicted_stopped_time_s"] >= 0.0
    assert 0.0 <= data["congestion_score"] <= 1.0

def test_network_endpoints():
    res_graph = client.get("/api/v1/network/graph?city=Philadelphia")
    assert res_graph.status_code == 200
    assert res_graph.json()["total_nodes"] > 0

    res_intel = client.get("/api/v1/network/intelligence?city=Philadelphia")
    assert res_intel.status_code == 200
    assert "domino_chain" in res_intel.json()

def test_simulation_endpoints():
    res_scen = client.get("/api/v1/simulation/scenarios")
    assert res_scen.status_code == 200
    assert len(res_scen.json()) >= 3

    res_eval = client.post("/api/v1/simulation/evaluate", json={"scenario_type": "INCIDENT_LIKE_DISRUPTION", "city": "Philadelphia", "target_id": 0})
    assert res_eval.status_code == 200
    data = res_eval.json()
    assert "recommended_strategy" in data
    assert data["recommended_strategy"]["rank"] == 1

def test_decision_and_human_action():
    res_rec = client.post("/api/v1/decision/recommendation", json={"city": "Philadelphia", "intersection_id": 0, "scenario_type": "INCIDENT_LIKE_DISRUPTION"})
    assert res_rec.status_code == 200
    data = res_rec.json()
    assert "recommended_strategy" in data
    assert "critic_evaluation" in data
    assert data["critic_evaluation"]["approved"] is True

    # Test Human Decision
    action_payload = {
        "event_id": data["event_id"],
        "action": "APPROVE",
        "selected_strategy_id": data["recommended_strategy"]["strategy"]["strategy_id"],
        "operator_notes": "All clear."
    }
    res_action = client.post("/api/v1/decision/human-action", json=action_payload)
    assert res_action.status_code == 200
    assert res_action.json()["status"] == "DISPATCHED_TO_FIELD_SIGNALS"

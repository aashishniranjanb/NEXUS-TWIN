"""
Integration Tests for Unified Demo Pipeline Endpoint (/api/v1/demo/analyze).
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_system_status_endpoint():
    res = client.get("/api/v1/system/status")
    assert res.status_code == 200
    data = res.json()
    assert data["backend_status"] == "OPERATIONAL"
    assert data["ml_model_loaded"] is True
    assert data["isolation_forest_loaded"] is True
    assert "Philadelphia" in data["supported_cities"]

def test_unified_demo_analyze_valid_request():
    payload = {
        "city": "Philadelphia",
        "intersection_id": 0,
        "scenario": "INCIDENT_LIKE_DISRUPTION",
        "emergency_mode": False,
        "hour": 17,
        "weekend": 0,
        "seed": 42
    }
    res = client.post("/api/v1/demo/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    
    # 1. Traffic State
    assert "traffic_state" in data
    assert data["traffic_state"]["city"] == "Philadelphia"
    assert data["traffic_state"]["predicted_stopped_time_s"] >= 0.0
    
    # 2. Prediction
    assert "prediction" in data
    assert data["prediction"]["target"] == "TotalTimeStopped_p50"
    
    # 3. Anomaly
    assert "anomaly" in data
    assert 0.0 <= data["anomaly"]["anomaly_score"] <= 1.0
    
    # 4. Fingerprint
    assert "fingerprint" in data
    assert data["fingerprint"]["classification"] in [
        "NORMAL", "RECURRING_CONGESTION", "INCIDENT_LIKE", "DEMAND_SURGE", "SIGNAL_RELATED"
    ]
    assert data["fingerprint"]["limitation_disclaimer"] != ""
    
    # 5. Network & Domino
    assert "network" in data
    assert data["network"]["total_nodes"] > 0
    assert len(data["network"]["domino_sequence"]) > 0
    
    # 6. Strategies
    assert "strategies" in data
    assert len(data["strategies"]) >= 4
    
    # 7. Recommendation
    assert "recommendation" in data
    assert data["recommendation"]["rank"] == 1
    assert len(data["recommendation"]["evidence"]) > 0
    
    # 8. Responsible AI Critic
    assert "responsible_ai" in data
    assert data["responsible_ai"]["safety_status"] in ["APPROVED", "CONDITIONAL_APPROVAL"]
    assert data["responsible_ai"]["human_override_required"] is True
    
    # 9. Explainability
    assert "explainability" in data
    assert data["explainability"]["action"] != ""
    assert data["explainability"]["why"] != ""

def test_unified_demo_analyze_emergency_mode():
    payload = {
        "city": "Boston",
        "intersection_id": 1,
        "scenario": "EMERGENCY_CORRIDOR",
        "emergency_mode": True,
        "seed": 42
    }
    res = client.post("/api/v1/demo/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["recommendation"]["emergency_speedup_pct"] is not None or data["recommendation"]["strategy_type"] in ["EMERGENCY_PRIORITY", "HYBRID_ADAPTIVE", "EXTEND_GREEN"]

def test_deterministic_reproducibility():
    payload = {
        "city": "Philadelphia",
        "intersection_id": 0,
        "scenario": "INCIDENT_LIKE_DISRUPTION",
        "seed": 42
    }
    res1 = client.post("/api/v1/demo/analyze", json=payload).json()
    res2 = client.post("/api/v1/demo/analyze", json=payload).json()
    
    assert res1["recommendation"]["strategy_id"] == res2["recommendation"]["strategy_id"]
    assert res1["recommendation"]["delay_reduction_pct"] == res2["recommendation"]["delay_reduction_pct"]
    assert res1["traffic_state"]["predicted_stopped_time_s"] == res2["traffic_state"]["predicted_stopped_time_s"]

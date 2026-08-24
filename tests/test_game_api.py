"""
Unit and Integration Tests for NEXUS-TWIN FastAPI Backend & Intelligence Services.
Tests all REST endpoints, WebSocket streams, and intelligence pipeline contracts.
"""

import pytest
import time
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

class TestNexusTwinAPI:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ONLINE"
        assert "J1/J2/J3" in data["network"]

    def test_traffic_state(self):
        response = client.get("/traffic/state")
        assert response.status_code == 200
        data = response.json()
        assert "network_metrics" in data
        assert "junctions" in data
        assert "J1" in data["junctions"]
        assert "J2" in data["junctions"]
        assert "J3" in data["junctions"]
        assert data["network_metrics"]["active_vehicles"] > 0

    def test_traffic_prediction(self):
        response = client.get("/traffic/prediction?junction_id=J2")
        assert response.status_code == 200
        data = response.json()
        assert data["junction_id"] == "J2"
        assert "congestion_probability" in data
        assert 0.0 <= data["congestion_probability"] <= 1.0
        assert data["forecast_horizon_minutes"] == 5

    def test_recommendation(self):
        response = client.get("/recommendation?junction_id=J2")
        assert response.status_code == 200
        data = response.json()
        assert "recommended_strategy" in data
        assert "explanation" in data
        assert "action" in data["explanation"]
        assert "confidence" in data["explanation"]

    def test_strategy_evaluate(self):
        payload = {
            "horizon_seconds": 180,
            "junction_id": "J2",
            "strategy_type": "diversion",
            "diversion_percent": 35.0
        }
        response = client.post("/strategy/evaluate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "recommended_strategy" in data
        assert "candidates" in data
        assert len(data["candidates"]) >= 4
        # Verify candidate models
        c_types = [c["strategy_type"] for c in data["candidates"]]
        assert "do_nothing" in c_types
        assert "diversion" in c_types
        assert "green_extend" in c_types

    def test_strategy_apply(self):
        payload = {
            "strategy_id": "diversion_J2",
            "strategy_type": "diversion",
            "junction_id": "J2",
            "parameters": {"diversion_percent": 35.0}
        }
        response = client.post("/strategy/apply", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "STRATEGY_APPLIED"

    def test_incident_trigger(self):
        payload = {
            "junction_id": "J2",
            "incident_type": "accident",
            "severity": "high"
        }
        response = client.post("/incident/trigger", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "INCIDENT_TRIGGERED"

    def test_emergency_preemption(self):
        payload = {
            "corridor": "J1-J2-J3",
            "vehicle_id": "AMBULANCE_01",
            "junction_id": "J2"
        }
        response = client.post("/api/emergency", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PREEMPTION_ACTIVE"
        assert data["vehicle_id"] == "AMBULANCE_01"

    def test_game_engine_lifecycle(self):
        # Start game
        start_res = client.post("/api/game/start", json={"player_name": "TestPilot", "mode": "free_play"})
        assert start_res.status_code == 200
        session_data = start_res.json()
        assert session_data["player_name"] == "TestPilot"

        # Make move
        move_res = client.post("/api/game/move", json={"strategy_type": "diversion", "junction_id": "J2"})
        assert move_res.status_code == 200
        move_data = move_res.json()
        assert "player_score" in move_data

        # Leaderboard
        lb_res = client.get("/api/game/leaderboard")
        assert lb_res.status_code == 200

        # End game
        end_res = client.post("/api/game/end")
        assert end_res.status_code == 200
        summary = end_res.json()
        assert "total_points" in summary
        assert "decisions_made" in summary

    def test_websocket_traffic_stream(self):
        with client.websocket_connect("/ws/traffic") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "vehicle_state"
            assert "vehicles" in data
            assert len(data["vehicles"]) > 0
            assert "signals" in data
            assert len(data["signals"]) == 3
            # Check vehicle coordinates
            first_veh = data["vehicles"][0]
            assert "x" in first_veh and "z" in first_veh and "speed_mps" in first_veh

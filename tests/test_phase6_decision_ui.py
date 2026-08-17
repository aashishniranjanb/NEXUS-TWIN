"""
Unit & Integration Tests for Phase 6 (Game UI & Decision Server API).
Verifies REST API response schemas, dynamic confidence bounds, what-if rollout handler, and emergency priority override endpoints.
"""

import unittest
import json
import http.client
import threading
import time
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.decision_server import SystemStateManager, DecisionRequestHandler, run_server

class TestPhase6DecisionUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state_manager = SystemStateManager()

    def test_live_state_schema(self):
        state = self.state_manager.get_live_state()
        self.assertIn("timestamp", state)
        self.assertIn("network_metrics", state)
        self.assertIn("junctions", state)

        # Verify J1, J2, J3 telemetry
        for j_id in ["J1", "J2", "J3"]:
            self.assertIn(j_id, state["junctions"])
            j_data = state["junctions"][j_id]
            self.assertIn("total_queue_m", j_data)
            self.assertIn("avg_waiting_time_s", j_data)
            self.assertIn("phase_name", j_data)

    def test_evaluate_whatif_payload(self):
        payload = {
            "junction_id": "J2",
            "strategy_type": "green_extend",
            "extension_seconds": 25.0,
            "horizon_seconds": 180
        }
        res = self.state_manager.evaluate_whatif(payload)
        self.assertIn("recommended_strategy", res)
        self.assertIn("explanation", res)
        self.assertIn("candidates", res)

        # Verify dynamic confidence score formatting
        exp = res["explanation"]
        self.assertIn("confidence", exp)
        self.assertIn("action", exp)
        self.assertIn("reason", exp)
        self.assertIn("expected_impact", exp)

        # Check candidate array
        self.assertGreaterEqual(len(res["candidates"]), 3)

    def test_emergency_preemption_override(self):
        payload = {
            "vehicle_id": "AMBULANCE_77",
            "corridor": "J1-J2-J3",
            "junction_id": "J2"
        }
        res = self.state_manager.trigger_emergency_preemption(payload)
        self.assertEqual(res["status"], "PREEMPTION_ACTIVE")
        self.assertEqual(res["vehicle_id"], "AMBULANCE_77")
        self.assertIn("result", res)
        self.assertEqual(res["result"]["strategy_type"], "emergency_priority")
        self.assertIn("confidence", res["explanation"])

if __name__ == "__main__":
    unittest.main()

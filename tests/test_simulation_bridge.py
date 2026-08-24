"""
Tests for Traffic State Extraction, Metrics Collection, and Scenario Engine Bridge.
"""

import pytest
from unittest.mock import MagicMock
from backend.schemas.scenario_models import Strategy, ScenarioResult
from simulation.bridge.traffic_state import TrafficStateExtractor
from simulation.bridge.metrics_collector import MetricsCollector

class TestSimulationBridge:
    def test_metrics_collector_empty(self):
        mc = MetricsCollector("baseline_fixed")
        summary = mc.compute_summary()
        assert summary == {}

    def test_metrics_collector_record_step(self):
        mc = MetricsCollector("baseline_fixed")
        mock_snapshot = {
            "avg_waiting_time_s": 0.25,
            "avg_speed_kmh": 40.0,
            "junctions": {
                "J1": {"total_queue_m": 10.0},
                "J2": {"total_queue_m": 20.0},
                "J3": {"total_queue_m": 15.0}
            }
        }
        mc.record_step(mock_snapshot)
        mc.record_completed_trip(32.5)
        assert len(mc.step_history) == 1
        summary = mc.compute_summary()
        assert summary["mean_queue_length_m"] == 45.0
        assert summary["avg_waiting_time_s"] == 0.25
        assert summary["throughput_vehicles"] == 1

"""
Unit Tests for Anomaly Detection.
"""

import pytest
from pathlib import Path
from intelligence.anomaly.detector import AnomalyDetector, calculate_statistical_deviations

def test_statistical_deviations():
    base = {"mean_wait_s": 10.0, "std_wait_s": 4.0, "mean_dist_m": 20.0}
    devs = calculate_statistical_deviations(observed_wait_s=22.0, observed_dist_m=5.0, baseline_stats=base)
    assert devs["waiting_time_z"] == 3.0
    assert devs["speed_drop_ratio"] > 0.5

def test_anomaly_detector_scoring():
    detector = AnomalyDetector()
    normal_dev = {"waiting_time_z": 0.2, "distance_z": 0.1, "speed_drop_ratio": 0.05, "directional_imbalance": 0.1}
    out_normal = detector.detect(normal_dev)
    assert out_normal["anomaly_score"] < 0.65

    extreme_dev = {"waiting_time_z": 5.0, "distance_z": -3.0, "speed_drop_ratio": 0.95, "directional_imbalance": 3.0}
    out_extreme = detector.detect(extreme_dev)
    assert out_extreme["anomaly_score"] > 0.50
    assert len(out_extreme["top_contributing_signals"]) > 0

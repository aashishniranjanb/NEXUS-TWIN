"""
Regression Tests for Metric Reproducibility and Numerical Consistency.
"""

import pytest
import json
from pathlib import Path
from intelligence.prediction.predict import TrafficPredictor

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
METRICS_FILE = PROJECT_ROOT / "models" / "prediction" / "metrics.json"

def test_metrics_reproducibility():
    assert METRICS_FILE.exists(), "metrics.json must exist."
    with open(METRICS_FILE, "r") as f:
        metrics = json.load(f)
    
    assert metrics["validation_rmse_seconds"] > 0.0
    assert metrics["naive_baseline_rmse_seconds"] > metrics["validation_rmse_seconds"]
    assert metrics["rmse_improvement_percent"] > 20.0
    assert metrics["validation_r2_score"] > 0.25

def test_deterministic_inference_repeatability():
    predictor = TrafficPredictor()
    sample = {
        "IntersectionId": 12,
        "Latitude": 33.75,
        "Longitude": -84.38,
        "entry_heading_deg": 90.0,
        "exit_heading_deg": 180.0,
        "heading_delta": 90.0,
        "turn_type_encoded": 1,
        "is_same_street": 0,
        "entry_street_missing": 0,
        "exit_street_missing": 0,
        "Hour": 17,
        "hour_sin": -0.9659,
        "hour_cos": -0.2588,
        "month_sin": -0.8660,
        "month_cos": -0.5000,
        "is_peak_hour": 1,
        "is_night": 0,
        "is_weekend": 0,
        "city_encoded": 0,
        "intersection_log_freq": 6.5,
        "path_log_freq": 4.2
    }
    pred_1 = predictor.predict_single(sample)
    pred_2 = predictor.predict_single(sample)
    assert pred_1["predicted_stopped_time_s"] == pred_2["predicted_stopped_time_s"]
    assert pred_1["confidence"] == pred_2["confidence"]

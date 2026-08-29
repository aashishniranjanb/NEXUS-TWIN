"""
Unit Tests for Prediction Model and Anti-Leakage Rules.
"""

import pytest
import json
from pathlib import Path
from intelligence.prediction.predict import TrafficPredictor

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
METADATA_FILE = PROJECT_ROOT / "models" / "prediction" / "metadata.json"
METRICS_FILE = PROJECT_ROOT / "models" / "prediction" / "metrics.json"

def test_model_artifacts_and_metrics():
    assert METADATA_FILE.exists(), "Model metadata must exist."
    assert METRICS_FILE.exists(), "Model metrics must exist."
    
    with open(METRICS_FILE, "r") as f:
        metrics = json.load(f)
    assert metrics["validation_mae_seconds"] > 0.0
    assert metrics["validation_r2_score"] > 0.0

def test_predictor_inference():
    predictor = TrafficPredictor()
    sample = {
        "IntersectionId": 10,
        "Latitude": 33.75,
        "Longitude": -84.38,
        "entry_heading_deg": 0.0,
        "exit_heading_deg": 90.0,
        "heading_delta": 90.0,
        "turn_type_encoded": 1,
        "is_same_street": 0,
        "entry_street_missing": 0,
        "exit_street_missing": 0,
        "Hour": 8,
        "hour_sin": 0.866,
        "hour_cos": 0.5,
        "month_sin": 0.5,
        "month_cos": 0.866,
        "is_peak_hour": 1,
        "is_night": 0,
        "is_weekend": 0,
        "city_encoded": 0,
        "intersection_log_freq": 5.2,
        "path_log_freq": 3.1
    }
    res = predictor.predict_single(sample)
    assert "predicted_stopped_time_s" in res
    assert res["predicted_stopped_time_s"] >= 0.0
    assert 0.0 <= res["confidence"] <= 1.0

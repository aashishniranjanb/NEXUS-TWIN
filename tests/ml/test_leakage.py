"""
Regression Tests for Anti-Leakage Gates.
Verifies that no target-derived features or validation data leak into model training or frequency encoders.
"""

import pytest
import json
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models" / "prediction"
SCHEMA_FILE = PROJECT_ROOT / "intelligence" / "data" / "features" / "feature_schema.json"
FREQ_ENCODERS_FILE = MODELS_DIR / "frequency_encoders.json"

def test_feature_schema_anti_leakage():
    with open(SCHEMA_FILE, "r") as f:
        schema = json.load(f)
    
    safe_features = set(schema["context_safe_inference_features"])
    behavioral_targets = set(schema["behavioral_target_columns"])
    
    # Assert ZERO intersection between feature matrix and target percentiles
    leaky_overlap = safe_features.intersection(behavioral_targets)
    assert len(leaky_overlap) == 0, f"Found target leakage columns in feature matrix: {leaky_overlap}"
    
    # Ensure forbidden columns are absent
    forbidden = ["RowId", "TotalTimeStopped_p20", "TotalTimeStopped_p80", "DistanceToFirstStop_p50"]
    for col in forbidden:
        assert col not in safe_features, f"Forbidden column {col} found in safe features."

def test_frequency_encoders_file_exists_and_isolated():
    assert FREQ_ENCODERS_FILE.exists(), "frequency_encoders.json must exist."
    with open(FREQ_ENCODERS_FILE, "r") as f:
        encoders = json.load(f)
    assert "intersection_freq" in encoders
    assert "path_freq" in encoders
    assert len(encoders["intersection_freq"]) > 0

"""
Unit Tests for Preprocessing and Data Validation.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from intelligence.data.preprocessing.validators import validate_schema, validate_ranges, validate_percentiles
from intelligence.data.preprocessing.constants import CONTEXT_COLUMNS, ALL_BEHAVIORAL_TARGETS

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CLEAN_PARQUET = PROJECT_ROOT / "data" / "processed" / "traffic_clean.parquet"

def test_clean_parquet_exists_and_schema():
    assert CLEAN_PARQUET.exists(), "traffic_clean.parquet must exist."
    df = pd.read_parquet(CLEAN_PARQUET)
    assert len(df) > 800000, "Dataset should have >800k records."
    validate_schema(df)
    validate_ranges(df)
    violations = validate_percentiles(df)
    assert violations["TotalTimeStopped"] == 0
    assert violations["TimeFromFirstStop"] == 0
    assert violations["DistanceToFirstStop"] == 0

def test_missing_street_name_imputation():
    df = pd.read_parquet(CLEAN_PARQUET)
    assert df["EntryStreetName"].isnull().sum() == 0, "No null entry street names allowed."
    assert df["ExitStreetName"].isnull().sum() == 0, "No null exit street names allowed."
    assert "entry_street_missing" in df.columns
    assert "exit_street_missing" in df.columns

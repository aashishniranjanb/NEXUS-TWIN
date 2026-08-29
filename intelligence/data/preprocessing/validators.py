"""
Data validation functions for BigQuery-Geotab raw and cleaned datasets.
"""

from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from intelligence.data.preprocessing.constants import (
    CITIES, HEADINGS, CONTEXT_COLUMNS, PERCENTILE_TARGETS, ALL_BEHAVIORAL_TARGETS
)

class ValidationError(Exception):
    pass

def validate_schema(df: pd.DataFrame) -> bool:
    """Verifies that all required raw columns are present."""
    required = set(CONTEXT_COLUMNS + ALL_BEHAVIORAL_TARGETS)
    missing = required - set(df.columns)
    if missing:
        raise ValidationError(f"Missing required columns in dataset: {missing}")
    return True

def validate_ranges(df: pd.DataFrame) -> Dict[str, bool]:
    """Validates domain ranges for temporal and categorical columns."""
    results = {}
    
    # Temporal ranges
    results["hour_valid"] = bool((df["Hour"] >= 0).all() and (df["Hour"] <= 23).all())
    results["weekend_valid"] = bool(df["Weekend"].isin([0, 1]).all())
    results["month_valid"] = bool((df["Month"] >= 1).all() and (df["Month"] <= 12).all())
    
    # Categorical domain checks
    results["city_valid"] = bool(df["City"].isin(CITIES).all())
    results["entry_heading_valid"] = bool(df["EntryHeading"].isin(HEADINGS).all())
    results["exit_heading_valid"] = bool(df["ExitHeading"].isin(HEADINGS).all())
    
    for k, v in results.items():
        if not v:
            raise ValidationError(f"Range validation failed for: {k}")
    return results

def validate_percentiles(df: pd.DataFrame) -> Dict[str, int]:
    """Validates that percentile targets are non-negative and monotonic."""
    violations = {}
    for family, cols in PERCENTILE_TARGETS.items():
        # Check non-negative
        neg_count = int((df[cols] < 0).any(axis=1).sum())
        if neg_count > 0:
            raise ValidationError(f"Found {neg_count} negative values in {family}")
        
        # Check monotonicity
        viol_mask = (
            (df[cols[0]] > df[cols[1]]) |
            (df[cols[1]] > df[cols[2]]) |
            (df[cols[2]] > df[cols[3]]) |
            (df[cols[3]] > df[cols[4]])
        )
        violations[family] = int(viol_mask.sum())
    return violations

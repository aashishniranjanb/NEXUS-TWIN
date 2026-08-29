"""
Feature Engineering Module for BigQuery-Geotab Dataset.
Builds temporal cyclical encodings, directional movement geometry,
spatial context representations, and maintains strict anti-leakage feature tagging.
"""

import json
import os
import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from intelligence.data.preprocessing.constants import (
    HEADING_TO_DEGREES, CITIES, ALL_BEHAVIORAL_TARGETS
)

CLEAN_PARQUET_PATH = PROJECT_ROOT / "data" / "processed" / "traffic_clean.parquet"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FEATURES_DIR = PROJECT_ROOT / "intelligence" / "data" / "features"
DOCS_DIR = PROJECT_ROOT / "docs" / "data"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FEATURES_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

def classify_turn(heading_delta: float) -> str:
    """Classifies turn based on heading delta degrees."""
    delta = heading_delta % 360.0
    if delta <= 22.5 or delta >= 337.5:
        return "Straight"
    elif 22.5 < delta <= 157.5:
        return "Right"
    elif 157.5 < delta <= 202.5:
        return "U-Turn"
    else: # 202.5 < delta < 337.5
        return "Left"

TURN_MAP = {"Straight": 0, "Right": 1, "Left": 2, "U-Turn": 3}
CITY_MAP = {city: i for i, city in enumerate(CITIES)}

def run_feature_engineering(input_parquet: Path = CLEAN_PARQUET_PATH, output_parquet: Path = PROCESSED_DIR / "feature_matrix.parquet") -> pd.DataFrame:
    start_t = time.time()
    print(f"\n[A3 FeatureEng] Loading clean dataset from {input_parquet}...")
    
    if not input_parquet.exists():
        raise FileNotFoundError(f"Clean parquet not found at {input_parquet}. Run preprocessing first.")
        
    df = pd.read_parquet(input_parquet)
    print(f"[A3 FeatureEng] Input shape: {df.shape}")
    
    # 1. Temporal Cyclical & Indicator Features
    print("[A3 FeatureEng] Engineering temporal cyclical features...")
    df["hour_sin"] = np.sin(2.0 * np.pi * df["Hour"] / 24.0).astype(np.float32)
    df["hour_cos"] = np.cos(2.0 * np.pi * df["Hour"] / 24.0).astype(np.float32)
    df["month_sin"] = np.sin(2.0 * np.pi * df["Month"] / 12.0).astype(np.float32)
    df["month_cos"] = np.cos(2.0 * np.pi * df["Month"] / 12.0).astype(np.float32)
    
    # Peak & Night Indicators
    peak_hours = {7, 8, 9, 16, 17, 18}
    night_hours = {22, 23, 0, 1, 2, 3, 4, 5}
    df["is_peak_hour"] = df["Hour"].isin(peak_hours).astype(np.int8)
    df["is_night"] = df["Hour"].isin(night_hours).astype(np.int8)
    df["is_weekend"] = df["Weekend"].astype(np.int8)

    # 2. Movement & Geometry Features
    print("[A3 FeatureEng] Engineering movement geometry and turn classifications...")
    entry_deg = df["EntryHeading"].map(HEADING_TO_DEGREES).astype(np.float32)
    exit_deg = df["ExitHeading"].map(HEADING_TO_DEGREES).astype(np.float32)
    
    df["entry_heading_deg"] = entry_deg
    df["exit_heading_deg"] = exit_deg
    df["heading_delta"] = ((exit_deg - entry_deg) % 360.0).astype(np.float32)
    
    turn_types = [classify_turn(d) for d in df["heading_delta"]]
    df["turn_type"] = turn_types
    df["turn_type_encoded"] = df["turn_type"].map(TURN_MAP).astype(np.int8)
    
    # 3. Spatial & Frequency Context Features
    print("[A3 FeatureEng] Computing spatial encodings and frequency context...")
    df["city_encoded"] = df["City"].map(CITY_MAP).astype(np.int8)
    
    # Frequency encodings (log1p scale to compress heavy-tailed counts)
    inter_counts = df["IntersectionId"].value_counts().to_dict()
    df["intersection_log_freq"] = np.log1p(df["IntersectionId"].map(inter_counts)).astype(np.float32)
    
    path_counts = df["Path"].value_counts().to_dict()
    df["path_log_freq"] = np.log1p(df["Path"].map(path_counts)).astype(np.float32)

    # 4. Define Explicit Feature Schema
    context_safe_features = [
        "IntersectionId",
        "Latitude",
        "Longitude",
        "entry_heading_deg",
        "exit_heading_deg",
        "heading_delta",
        "turn_type_encoded",
        "is_same_street",
        "entry_street_missing",
        "exit_street_missing",
        "Hour",
        "hour_sin",
        "hour_cos",
        "month_sin",
        "month_cos",
        "is_peak_hour",
        "is_night",
        "is_weekend",
        "city_encoded",
        "intersection_log_freq",
        "path_log_freq"
    ]

    # Save to Parquet
    print(f"[A3 FeatureEng] Saving feature matrix to {output_parquet}...")
    df.to_parquet(output_parquet, index=False, engine="pyarrow")
    
    file_size_mb = round(os.path.getsize(output_parquet) / (1024 * 1024), 2)
    elapsed = round(time.time() - start_t, 2)
    
    feature_schema = {
        "context_safe_inference_features": context_safe_features,
        "raw_context_columns": ["RowId", "IntersectionId", "Latitude", "Longitude", "EntryStreetName", "ExitStreetName", "EntryHeading", "ExitHeading", "Hour", "Weekend", "Month", "Path", "City"],
        "behavioral_target_columns": ALL_BEHAVIORAL_TARGETS,
        "feature_types": {col: str(df[col].dtype) for col in context_safe_features},
        "target_types": {col: str(df[col].dtype) for col in ALL_BEHAVIORAL_TARGETS}
    }
    
    feature_metadata = {
        "source_clean_parquet": str(input_parquet),
        "output_feature_matrix": str(output_parquet),
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "num_context_safe_features": len(context_safe_features),
        "num_behavioral_targets": len(ALL_BEHAVIORAL_TARGETS),
        "file_size_mb": file_size_mb,
        "processing_time_seconds": elapsed,
        "turn_type_distribution": df["turn_type"].value_counts().to_dict(),
        "leakage_boundary": "Only context_safe_inference_features may be used as model inputs when predicting any behavioral_target_columns."
    }
    
    schema_path = FEATURES_DIR / "feature_schema.json"
    meta_path = FEATURES_DIR / "feature_metadata.json"
    
    with open(schema_path, "w") as f:
        json.dump(feature_schema, f, indent=2)
    with open(meta_path, "w") as f:
        json.dump(feature_metadata, f, indent=2)
        
    print(f"[A3 FeatureEng] Feature Engineering COMPLETE in {elapsed}s. Output size: {file_size_mb} MB.")
    print(f"[A3 FeatureEng] Saved schema: {schema_path}")
    print(f"[A3 FeatureEng] Saved metadata: {meta_path}")
    
    gen_feature_report_doc(feature_metadata, context_safe_features)
    return df

def gen_feature_report_doc(meta: dict, safe_features: list):
    doc = f"""# Feature Engineering Report — BigQuery-Geotab Dataset

| Metric | Value |
|---|---|
| **Rows** | {meta['total_rows']:,} |
| **Total Columns** | {meta['total_columns']} |
| **Safe Context Features** | {meta['num_context_safe_features']} |
| **Behavioral Targets** | {meta['num_behavioral_targets']} |
| **Matrix Size** | {meta['file_size_mb']} MB (Parquet) |

---

## 1. Safe Context Features (Inference-Time Legitimate)
These 21 features contain **zero target leakage** and represent conditions observable prior to measuring vehicle queues/delays:

| Feature Name | Type | Description |
|---|---|---|
| `IntersectionId` | `int32` | Physical intersection identifier |
| `Latitude` | `float32` | Geographic latitude |
| `Longitude` | `float32` | Geographic longitude |
| `entry_heading_deg` | `float32` | Compass bearing for entry direction ($0^\\circ - 315^\\circ$) |
| `exit_heading_deg` | `float32` | Compass bearing for exit direction ($0^\\circ - 315^\\circ$) |
| `heading_delta` | `float32` | Angular change in travel direction ($0^\\circ - 360^\\circ$) |
| `turn_type_encoded` | `int8` | 0: Straight, 1: Right, 2: Left, 3: U-Turn |
| `is_same_street` | `int8` | Binary flag (1 if entry street == exit street) |
| `entry_street_missing` | `int8` | Binary missingness indicator |
| `exit_street_missing` | `int8` | Binary missingness indicator |
| `Hour` | `int8` | Clock hour ($0 - 23$) |
| `hour_sin` | `float32` | $\\sin(2\\pi \\cdot \\text{{Hour}} / 24)$ |
| `hour_cos` | `float32` | $\\cos(2\\pi \\cdot \\text{{Hour}} / 24)$ |
| `month_sin` | `float32` | $\\sin(2\\pi \\cdot \\text{{Month}} / 12)$ |
| `month_cos` | `float32` | $\\cos(2\\pi \\cdot \\text{{Month}} / 12)$ |
| `is_peak_hour` | `int8` | Rush hour flag (7-9 AM, 4-6 PM) |
| `is_night` | `int8` | Night hours flag (10 PM - 5 AM) |
| `is_weekend` | `int8` | Binary weekend flag (0: Weekday, 1: Weekend) |
| `city_encoded` | `int8` | 0: Atlanta, 1: Boston, 2: Chicago, 3: Philadelphia |
| `intersection_log_freq`| `float32` | $\\log(1 + \\text{{intersection count}})$ |
| `path_log_freq` | `float32` | $\\log(1 + \\text{{path count}})$ |

---

## 2. Turn Type Distribution
"""
    for turn, count in meta["turn_type_distribution"].items():
        doc += f"- **{turn}**: {count:,} ({count/meta['total_rows']*100:.1f}%)\n"

    doc += """
---

## 3. Anti-Leakage Boundary
All 15 target percentiles (`TotalTimeStopped_p20/40/50/60/80`, `TimeFromFirstStop_p20/40/50/60/80`, `DistanceToFirstStop_p20/40/50/60/80`) are strictly isolated from the safe context feature matrix.
"""
    with open(DOCS_DIR / "FEATURE_ENGINEERING_REPORT.md", "w") as f:
        f.write(doc)
    print(f"[A3 FeatureEng] Saved feature engineering report to {DOCS_DIR / 'FEATURE_ENGINEERING_REPORT.md'}")

if __name__ == "__main__":
    run_feature_engineering()

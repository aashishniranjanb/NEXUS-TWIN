"""
Dataset Integrity and Leakage Audit Script for BigQuery-Geotab Dataset.
Analyzes data quality, column semantics, percentile consistency, and potential target leakage.
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RAW_TRAIN_PATH = PROJECT_ROOT / "data" / "train.csv"
OUTPUT_DIR = PROJECT_ROOT / "intelligence" / "data" / "inspection"
DOCS_DIR = PROJECT_ROOT / "docs" / "data"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

def run_audit():
    print(f"[A1 Audit] Loading {RAW_TRAIN_PATH}...")
    df = pd.read_csv(RAW_TRAIN_PATH)
    total_rows, total_cols = df.shape
    print(f"[A1 Audit] Loaded {total_rows:,} rows and {total_cols} columns.")

    # 1. Schema & Missing Values
    schema_info = {}
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        schema_info[col] = {
            "dtype": str(df[col].dtype),
            "null_count": null_count,
            "null_pct": round(float(null_count / total_rows * 100), 3),
            "nunique": int(df[col].nunique()),
            "sample_values": [str(x) for x in df[col].dropna().head(3).tolist()]
        }

    # 2. Duplicate Checks
    exact_duplicates = int(df.duplicated().sum())
    duplicate_row_ids = int(df["RowId"].duplicated().sum())
    context_keys = ["IntersectionId", "Hour", "Weekend", "Month", "EntryHeading", "ExitHeading", "City"]
    context_duplicates = int(df.duplicated(subset=context_keys).sum())

    # 3. Value Range & Validation Checks
    hour_valid = bool((df["Hour"].min() >= 0) and (df["Hour"].max() <= 23))
    weekend_valid = bool(set(df["Weekend"].unique()).issubset({0, 1}))
    month_valid = bool((df["Month"].min() >= 1) and (df["Month"].max() <= 12))
    
    city_counts = df["City"].value_counts().to_dict()
    cities = list(city_counts.keys())

    # Coordinate ranges by City
    geo_ranges = {}
    for city, grp in df.groupby("City"):
        geo_ranges[city] = {
            "lat_min": round(float(grp["Latitude"].min()), 5),
            "lat_max": round(float(grp["Latitude"].max()), 5),
            "lon_min": round(float(grp["Longitude"].min()), 5),
            "lon_max": round(float(grp["Longitude"].max()), 5),
            "intersections_count": int(grp["IntersectionId"].nunique()),
            "rows_count": int(len(grp))
        }

    # 4. Percentile Monotonicity Checks (p20 <= p40 <= p50 <= p60 <= p80)
    percentile_families = {
        "TotalTimeStopped": ["TotalTimeStopped_p20", "TotalTimeStopped_p40", "TotalTimeStopped_p50", "TotalTimeStopped_p60", "TotalTimeStopped_p80"],
        "TimeFromFirstStop": ["TimeFromFirstStop_p20", "TimeFromFirstStop_p40", "TimeFromFirstStop_p50", "TimeFromFirstStop_p60", "TimeFromFirstStop_p80"],
        "DistanceToFirstStop": ["DistanceToFirstStop_p20", "DistanceToFirstStop_p40", "DistanceToFirstStop_p50", "DistanceToFirstStop_p60", "DistanceToFirstStop_p80"]
    }

    monotonic_violations = {}
    negative_counts = {}
    for family, cols in percentile_families.items():
        # Check non-negative
        neg_mask = (df[cols] < 0).any(axis=1)
        negative_counts[family] = int(neg_mask.sum())
        
        # Check monotonicity: p20 <= p40 <= p50 <= p60 <= p80
        viol_mask = (
            (df[cols[0]] > df[cols[1]]) |
            (df[cols[1]] > df[cols[2]]) |
            (df[cols[2]] > df[cols[3]]) |
            (df[cols[3]] > df[cols[4]])
        )
        monotonic_violations[family] = int(viol_mask.sum())

    # 5. Column Classification & Leakage Risk Assessment
    contextual_features = [
        "IntersectionId", "Latitude", "Longitude", "EntryStreetName", "ExitStreetName",
        "EntryHeading", "ExitHeading", "Hour", "Weekend", "Month", "Path", "City"
    ]
    target_behavioral_features = []
    for fam_cols in percentile_families.values():
        target_behavioral_features.extend(fam_cols)

    leakage_assessment = {
        "contextual_safe_inference_features": contextual_features,
        "target_family_behavioral_features": target_behavioral_features,
        "leakage_rule": (
            "CRITICAL: If the prediction target is TotalTimeStopped_p50 (or any behavioral percentile), "
            "NONE of the other 14 behavioral percentile columns (TotalTimeStopped_*, TimeFromFirstStop_*, DistanceToFirstStop_*) "
            "may be used as training inputs for the same observation. They represent contemporaneous measurements "
            "and constitute severe target leakage."
        )
    }

    # Assemble Quality Report
    quality_report = {
        "dataset_name": "BigQuery-Geotab Intersection Congestion",
        "total_rows": total_rows,
        "total_columns": total_cols,
        "exact_duplicates": exact_duplicates,
        "duplicate_row_ids": duplicate_row_ids,
        "context_duplicates_same_time_movement": context_duplicates,
        "temporal_validity": {
            "hour_valid_0_23": hour_valid,
            "weekend_valid_0_1": weekend_valid,
            "month_valid_1_12": month_valid
        },
        "city_distribution": city_counts,
        "geographic_ranges_by_city": geo_ranges,
        "percentile_validation": {
            "negative_value_counts": negative_counts,
            "monotonic_ordering_violations": monotonic_violations
        },
        "leakage_assessment": leakage_assessment
    }

    # Save JSON Reports
    schema_report_path = OUTPUT_DIR / "schema_report.json"
    quality_report_path = OUTPUT_DIR / "data_quality_report.json"

    with open(schema_report_path, "w") as f:
        json.dump(schema_info, f, indent=2)
    with open(quality_report_path, "w") as f:
        json.dump(quality_report, f, indent=2)

    print(f"[A1 Audit] Saved schema report: {schema_report_path}")
    print(f"[A1 Audit] Saved quality report: {quality_report_path}")

    # Generate Markdown Documentation
    gen_markdown_reports(schema_info, quality_report)

def gen_markdown_reports(schema_info, quality_report):
    quality_md = f"""# Data Quality Report — BigQuery-Geotab Dataset

| Metric | Value |
|---|---|
| **Total Rows** | {quality_report['total_rows']:,} |
| **Total Columns** | {quality_report['total_columns']} |
| **Exact Duplicate Rows** | {quality_report['exact_duplicates']} |
| **Duplicate RowIds** | {quality_report['duplicate_row_ids']} |
| **Duplicate Context Keys** | {quality_report['context_duplicates_same_time_movement']:,} |

---

## 1. Schema and Missing Value Profile

| Column | Dtype | Null Count | Null % | Cardinality | Sample Values |
|---|---|---|---|---|---|
"""
    for col, info in schema_info.items():
        samples = ", ".join(info["sample_values"][:2])
        quality_md += f"| `{col}` | `{info['dtype']}` | {info['null_count']} | {info['null_pct']}% | {info['nunique']:,} | `{samples}` |\n"

    quality_md += f"""
---

## 2. City & Spatial Distributions

| City | Rows Count | Intersections | Latitude Range | Longitude Range |
|---|---|---|---|---|
"""
    for city, geo in quality_report["geographic_ranges_by_city"].items():
        quality_md += f"| **{city}** | {geo['rows_count']:,} | {geo['intersections_count']:,} | [{geo['lat_min']}, {geo['lat_max']}] | [{geo['lon_min']}, {geo['lon_max']}] |\n"

    quality_md += f"""
---

## 3. Percentile Monotonicity & Behavioral Integrity

- **Negative Values**: TotalTimeStopped: {quality_report['percentile_validation']['negative_value_counts']['TotalTimeStopped']}, TimeFromFirstStop: {quality_report['percentile_validation']['negative_value_counts']['TimeFromFirstStop']}, DistanceToFirstStop: {quality_report['percentile_validation']['negative_value_counts']['DistanceToFirstStop']}
- **Monotonic Violations** ($p20 \\le p40 \\le p50 \\le p60 \\le p80$):
  - `TotalTimeStopped`: {quality_report['percentile_validation']['monotonic_ordering_violations']['TotalTimeStopped']} violations
  - `TimeFromFirstStop`: {quality_report['percentile_validation']['monotonic_ordering_violations']['TimeFromFirstStop']} violations
  - `DistanceToFirstStop`: {quality_report['percentile_validation']['monotonic_ordering_violations']['DistanceToFirstStop']} violations
"""

    with open(DOCS_DIR / "DATA_QUALITY_REPORT.md", "w") as f:
        f.write(quality_md)

    leakage_md = f"""# Leakage Audit & Feature Availability Gate

## 1. Contextual Features (Legitimate at Inference Time)
These features describe the external physical and temporal context available prior to observing traffic behavior:
- `IntersectionId`, `Latitude`, `Longitude`
- `EntryStreetName`, `ExitStreetName` (with `UNKNOWN` imputation)
- `EntryHeading`, `ExitHeading`
- `Hour`, `Weekend`, `Month`
- `City`, `Path`
- **Engineered cyclical / spatial / heading features**

## 2. Behavioral Measurement Family (Contemporaneous Targets)
These features represent measurements taken during the aggregated time window:
- `TotalTimeStopped_p20`, `p40`, `p50`, `p60`, `p80`
- `TimeFromFirstStop_p20`, `p40`, `p50`, `p60`, `p80`
- `DistanceToFirstStop_p20`, `p40`, `p50`, `p60`, `p80`

## 3. The Strict Leakage Gate Rule
> **LEAKAGE GATE ENFORCEMENT**: When predicting `TotalTimeStopped_p50` (or any single percentile target), **NO OTHER BEHAVIORAL PERCENTILE** from the same row may be fed into the model. Feeding contemporaneous `p20`, `p40`, or `DistanceToFirstStop` yields artificial accuracy that cannot exist in real-world deployment where those sensor percentiles are not yet observed.
"""

    with open(DOCS_DIR / "LEAKAGE_AUDIT.md", "w") as f:
        f.write(leakage_md)

    print(f"[A1 Audit] Generated markdown reports in {DOCS_DIR}")

if __name__ == "__main__":
    run_audit()

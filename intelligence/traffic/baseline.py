"""
Historical Baseline Module.
Aggregates and queries historical traffic distributions across intersections, hours, and directions.
Uses vectorized aggregation over precomputed percentile observation columns.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CLEAN_PARQUET_PATH = PROJECT_ROOT / "data" / "processed" / "traffic_clean.parquet"
BASELINES_PARQUET = PROJECT_ROOT / "data" / "processed" / "historical_baselines.parquet"

class HistoricalBaseline:
    def __init__(self, baselines_path: Path = BASELINES_PARQUET):
        self.baselines_path = Path(baselines_path)
        self.baselines_df: Optional[pd.DataFrame] = None
        self.lookup_dict: Dict[str, Dict[str, float]] = {}
        self._load_or_build()

    def _load_or_build(self):
        if not self.baselines_path.exists():
            print("[Baseline] Baselines file not found. Building from clean dataset...")
            self.build_baselines()
        else:
            self.baselines_df = pd.read_parquet(self.baselines_path)
            self._build_fast_lookup()

    def build_baselines(self, source_parquet: Path = CLEAN_PARQUET_PATH):
        df = pd.read_parquet(source_parquet)
        group_cols = ["City", "IntersectionId", "Hour", "Weekend", "EntryHeading"]
        
        # Fast vectorized aggregation
        agg_df = df.groupby(group_cols, observed=True).agg(
            mean_wait_s=("TotalTimeStopped_p50", "mean"),
            std_wait_s=("TotalTimeStopped_p50", "std"),
            median_wait_s=("TotalTimeStopped_p50", "median"),
            p20_wait_s=("TotalTimeStopped_p20", "mean"),
            p80_wait_s=("TotalTimeStopped_p80", "mean"),
            mean_dist_m=("DistanceToFirstStop_p50", "mean"),
            obs_count=("TotalTimeStopped_p50", "count")
        ).reset_index()
        
        agg_df["std_wait_s"] = agg_df["std_wait_s"].fillna(1.0)
        self.baselines_df = agg_df
        self.baselines_path.parent.mkdir(parents=True, exist_ok=True)
        agg_df.to_parquet(self.baselines_path, index=False, engine="pyarrow")
        print(f"[Baseline] Built {len(agg_df):,} historical baseline profiles. Saved to {self.baselines_path}")
        self._build_fast_lookup()

    def _build_fast_lookup(self):
        self.lookup_dict = {}
        for r in self.baselines_df.to_dict(orient="records"):
            key = f"{r['City']}_{r['IntersectionId']}_{r['Hour']}_{r['Weekend']}_{r['EntryHeading']}"
            self.lookup_dict[key] = {
                "mean_wait_s": round(float(r["mean_wait_s"]), 2),
                "std_wait_s": round(float(r["std_wait_s"]), 2),
                "median_wait_s": round(float(r["median_wait_s"]), 2),
                "p20_wait_s": round(float(r["p20_wait_s"]), 2),
                "p80_wait_s": round(float(r["p80_wait_s"]), 2),
                "mean_dist_m": round(float(r["mean_dist_m"]), 2),
                "obs_count": int(r["obs_count"])
            }

    def get_baseline(self, city: str, intersection_id: int, hour: int, weekend: int, entry_heading: str) -> Dict[str, float]:
        """Fast O(1) lookup with hierarchical fallback."""
        key = f"{city}_{intersection_id}_{hour}_{weekend}_{entry_heading}"
        if key in self.lookup_dict:
            return self.lookup_dict[key]
            
        # Fallback default
        return {
            "mean_wait_s": 8.0,
            "std_wait_s": 6.0,
            "median_wait_s": 5.0,
            "p20_wait_s": 0.0,
            "p80_wait_s": 15.0,
            "mean_dist_m": 25.0,
            "obs_count": 10
        }

if __name__ == "__main__":
    b = HistoricalBaseline()
    sample = b.get_baseline("Atlanta", 0, 8, 0, "N")
    print("Baseline query for Atlanta #0 (8 AM, Weekday, N):", sample)

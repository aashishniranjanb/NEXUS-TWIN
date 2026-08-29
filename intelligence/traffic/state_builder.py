"""
Traffic State Builder Module.
Constructs authoritative TrafficState instances linking predictions, historical baselines,
congestion scores, queue proxies, and evidence summaries.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from intelligence.data.preprocessing.constants import HEADING_TO_DEGREES, CITIES
from intelligence.data.features.feature_engineering import classify_turn, TURN_MAP, CITY_MAP
from intelligence.prediction.predict import TrafficPredictor
from intelligence.traffic.baseline import HistoricalBaseline
from intelligence.traffic.congestion import calculate_congestion_score, estimate_queue_length_m
from intelligence.traffic.schema import TrafficState, CongestionSeverity, IntersectionRankItem, IntersectionRankingResponse
THRESHOLDS_FILE = PROJECT_ROOT / "models" / "traffic_intelligence" / "thresholds.json"
THRESHOLDS_FILE.parent.mkdir(parents=True, exist_ok=True)

class TrafficStateBuilder:
    def __init__(self):
        self.predictor = TrafficPredictor()
        self.baseline = HistoricalBaseline()
        self._save_thresholds()

    def _save_thresholds(self):
        thresholds = {
            "severity_bands": {
                "NORMAL": {"min": 0.0, "max": 0.25},
                "LOW": {"min": 0.25, "max": 0.45},
                "MODERATE": {"min": 0.45, "max": 0.70},
                "HIGH": {"min": 0.70, "max": 0.85},
                "CRITICAL": {"min": 0.85, "max": 1.0}
            },
            "peak_hours": [7, 8, 9, 16, 17, 18],
            "night_hours": [22, 23, 0, 1, 2, 3, 4, 5],
            "queue_factor_m_per_second": 1.25
        }
        with open(THRESHOLDS_FILE, "w") as f:
            json.dump(thresholds, f, indent=2)

    def build_features_from_raw(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Maps raw/API inputs into 21 engineered context features."""
        entry_h = str(context.get("EntryHeading", context.get("entry_heading", "N"))).strip()
        exit_h = str(context.get("ExitHeading", context.get("exit_heading", "N"))).strip()
        
        entry_deg = HEADING_TO_DEGREES.get(entry_h, 0.0)
        exit_deg = HEADING_TO_DEGREES.get(exit_h, 0.0)
        h_delta = float((exit_deg - entry_deg) % 360.0)
        turn_str = classify_turn(h_delta)
        turn_code = TURN_MAP.get(turn_str, 0)
        
        city = str(context.get("City", context.get("city", "Atlanta"))).strip()
        city_code = CITY_MAP.get(city, 0)
        
        hour = int(context.get("Hour", context.get("hour", 12)))
        weekend = int(context.get("Weekend", context.get("weekend", 0)))
        month = int(context.get("Month", context.get("month", 10)))
        
        entry_st = str(context.get("EntryStreetName", context.get("entry_street_name", "Main St")))
        exit_st = str(context.get("ExitStreetName", context.get("exit_street_name", "Main St")))
        is_same = int(entry_st == exit_st)
        
        entry_missing = int(entry_st in ("UNKNOWN", "", "None"))
        exit_missing = int(exit_st in ("UNKNOWN", "", "None"))
        
        hour_sin = float(np.sin(2.0 * np.pi * hour / 24.0))
        hour_cos = float(np.cos(2.0 * np.pi * hour / 24.0))
        month_sin = float(np.sin(2.0 * np.pi * month / 12.0))
        month_cos = float(np.cos(2.0 * np.pi * month / 12.0))
        
        is_peak = int(hour in [7, 8, 9, 16, 17, 18])
        is_night = int(hour in [22, 23, 0, 1, 2, 3, 4, 5])
        
        inter_id = int(context.get("IntersectionId", context.get("intersection_id", 0)))
        lat = float(context.get("Latitude", context.get("latitude", 33.75)))
        lon = float(context.get("Longitude", context.get("longitude", -84.38)))
        path_str = str(context.get("Path", f"{entry_st}_{entry_h}_{exit_st}_{exit_h}"))
        
        # Load frequency encoders if available
        inter_freq = 0
        path_freq = 0
        freq_file = PROJECT_ROOT / "models" / "prediction" / "frequency_encoders.json"
        if freq_file.exists():
            try:
                with open(freq_file, "r") as f:
                    f_data = json.load(f)
                    inter_freq = f_data.get("intersection_freq", {}).get(str(inter_id), 0)
                    path_freq = f_data.get("path_freq", {}).get(path_str, 0)
            except Exception:
                pass
                
        inter_log_freq = float(context.get("intersection_log_freq", np.log1p(inter_freq)))
        path_log_freq = float(context.get("path_log_freq", np.log1p(path_freq)))
        
        return {
            "IntersectionId": inter_id,
            "Latitude": lat,
            "Longitude": lon,
            "entry_heading_deg": entry_deg,
            "exit_heading_deg": exit_deg,
            "heading_delta": h_delta,
            "turn_type_encoded": turn_code,
            "is_same_street": is_same,
            "entry_street_missing": entry_missing,
            "exit_street_missing": exit_missing,
            "Hour": hour,
            "hour_sin": hour_sin,
            "hour_cos": hour_cos,
            "month_sin": month_sin,
            "month_cos": month_cos,
            "is_peak_hour": is_peak,
            "is_night": is_night,
            "is_weekend": weekend,
            "city_encoded": city_code,
            "intersection_log_freq": inter_log_freq,
            "path_log_freq": path_log_freq,
            # Raw attributes for metadata
            "_turn_type_str": turn_str,
            "_city_str": city,
            "_entry_h": entry_h,
            "_exit_h": exit_h
        }

    def build_state(self, raw_context: Dict[str, Any]) -> TrafficState:
        """Constructs an evidence-backed TrafficState object."""
        feat_dict = self.build_features_from_raw(raw_context)
        
        # 1. Run ML Prediction
        pred_out = self.predictor.predict_single(feat_dict)
        pred_wait = pred_out["predicted_stopped_time_s"]
        conf = pred_out["confidence"]
        
        city = feat_dict["_city_str"]
        inter_id = feat_dict["IntersectionId"]
        hour = feat_dict["Hour"]
        weekend = feat_dict["is_weekend"]
        entry_h = feat_dict["_entry_h"]
        exit_h = feat_dict["_exit_h"]
        turn_str = feat_dict["_turn_type_str"]
        
        # 2. Query Historical Baseline
        base = self.baseline.get_baseline(city, inter_id, hour, weekend, entry_h)
        base_med = base["median_wait_s"]
        base_p80 = base["p80_wait_s"]
        base_dist = base["mean_dist_m"]
        
        # 3. Calculate Congestion Score & Severity
        score, severity = calculate_congestion_score(pred_wait, base_med, base_p80)
        queue_m = estimate_queue_length_m(pred_wait, base_dist)
        
        # 4. Generate Grounded Evidence Strings
        evidence = []
        evidence.append(f"Predicted median stopped time is {pred_wait:.1f}s for {turn_str} movement ({entry_h}->{exit_h}).")
        if pred_wait > base_p80:
            pct_over = ((pred_wait - base_p80) / max(1.0, base_p80)) * 100.0
            evidence.append(f"Wait time is {pct_over:.1f}% above historical 80th percentile baseline ({base_p80:.1f}s).")
        elif pred_wait > base_med:
            pct_over = ((pred_wait - base_med) / max(1.0, base_med)) * 100.0
            evidence.append(f"Wait time is {pct_over:.1f}% above historical median baseline ({base_med:.1f}s).")
        else:
            evidence.append(f"Wait time is within normal historical envelope (median {base_med:.1f}s).")
            
        if feat_dict["is_peak_hour"]:
            evidence.append(f"Observation falls within standard urban peak commute hours ({hour}:00).")
        else:
            evidence.append(f"Observation occurs during non-peak hours ({hour}:00).")
            
        evidence.append(f"Estimated vehicle queue accumulation is approximately {queue_m:.1f} meters.")

        return TrafficState(
            intersection_id=inter_id,
            city=city,
            hour=hour,
            weekend=weekend,
            entry_heading=entry_h,
            exit_heading=exit_h,
            turn_type=turn_str,
            predicted_stopped_time_s=pred_wait,
            historical_baseline_p50_s=base_med,
            historical_baseline_p80_s=base_p80,
            congestion_score=score,
            severity=severity,
            estimated_queue_m=queue_m,
            confidence=conf,
            evidence=evidence,
            is_peak_period=bool(feat_dict["is_peak_hour"]),
            model_version=pred_out["model_version"]
        )

if __name__ == "__main__":
    builder = TrafficStateBuilder()
    test_ctx = {
        "City": "Philadelphia",
        "IntersectionId": 463,
        "Hour": 16,
        "Weekend": 0,
        "EntryHeading": "NW",
        "ExitHeading": "SE",
        "Latitude": 39.95,
        "Longitude": -75.16
    }
    state = builder.build_state(test_ctx)
    print("\n[TrafficState Output]:")
    print(state.model_dump_json(indent=2))

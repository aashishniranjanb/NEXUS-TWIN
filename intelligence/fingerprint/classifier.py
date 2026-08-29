"""
Traffic Fingerprint Classifier Module.
Converts multidimensional anomaly deviations and contextual state into semantic diagnostic fingerprints:
NORMAL, RECURRING_CONGESTION, INCIDENT_LIKE, DEMAND_SURGE, SIGNAL_RELATED.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
import numpy as np
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from intelligence.anomaly.detector import AnomalyDetector, calculate_statistical_deviations
from intelligence.traffic.baseline import HistoricalBaseline

MODELS_DIR = PROJECT_ROOT / "models" / "fingerprint"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
METADATA_FILE = MODELS_DIR / "metadata.json"

class FingerprintClass(str, Enum):
    NORMAL = "NORMAL"
    RECURRING_CONGESTION = "RECURRING_CONGESTION"
    INCIDENT_LIKE = "INCIDENT_LIKE"
    DEMAND_SURGE = "DEMAND_SURGE"
    SIGNAL_RELATED = "SIGNAL_RELATED"

class TrafficFingerprint(BaseModel):
    intersection_id: int
    city: str
    classification: FingerprintClass
    confidence: float = Field(ge=0.0, le=1.0)
    severity: str
    anomaly_score: float = Field(ge=0.0, le=1.0)
    evidence: List[str]
    contributing_signals: List[str]
    historical_comparison: Dict[str, Any]
    limitation_disclaimer: str

class TrafficFingerprintEngine:
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.baseline = HistoricalBaseline()
        self._save_metadata()

    def _save_metadata(self):
        meta = {
            "classes": [c.value for c in FingerprintClass],
            "description": "Rule-gated semantic diagnosis engine over Isolation Forest and historical deviation vectors.",
            "version": "1.0.0",
            "causal_disclaimer": "INCIDENT_LIKE indicates severe abnormal pattern deviation and does not verify physical collision without ground-truth sensor/CCTV feeds."
        }
        with open(METADATA_FILE, "w") as f:
            json.dump(meta, f, indent=2)

    def diagnose(self, traffic_context: Dict[str, Any], observed_wait_s: float, observed_dist_m: float) -> TrafficFingerprint:
        city = str(traffic_context.get("City", "Philadelphia"))
        inter_id = int(traffic_context.get("IntersectionId", 0))
        hour = int(traffic_context.get("Hour", 17))
        weekend = int(traffic_context.get("Weekend", 0))
        entry_h = str(traffic_context.get("EntryHeading", "N"))
        is_peak = bool(hour in [7, 8, 9, 16, 17, 18] and weekend == 0)

        # 1. Query Baseline & Compute Statistical Deviations
        base_stats = self.baseline.get_baseline(city, inter_id, hour, weekend, entry_h)
        deviations = calculate_statistical_deviations(observed_wait_s, observed_dist_m, base_stats)
        
        # 2. Anomaly Detection
        anom_res = self.anomaly_detector.detect(deviations)
        anom_score = anom_res["anomaly_score"]
        is_anomaly = anom_res["anomaly_detected"]
        severity = anom_res["severity"]

        wait_z = deviations["waiting_time_z"]
        speed_drop = deviations["speed_drop_ratio"]
        dir_imbalance = deviations["directional_imbalance"]

        # 3. Diagnostic Rule-Gated Classification
        evidence = []
        p80_wait = base_stats["p80_wait_s"]
        med_wait = base_stats["median_wait_s"]
        
        if anom_score < 0.45 and wait_z < 1.0 and observed_wait_s <= med_wait:
            cls = FingerprintClass.NORMAL
            confidence = round(float(np.clip(1.0 - anom_score, 0.70, 0.98)), 3)
            evidence.append(f"Stopping duration ({observed_wait_s:.1f}s) is within historical baseline envelope (median {med_wait:.1f}s).")
            evidence.append("No significant multivariate anomalies detected across approach movements.")
            
        elif is_peak and observed_wait_s <= p80_wait:
            cls = FingerprintClass.RECURRING_CONGESTION
            confidence = round(float(np.clip(0.75 + (wait_z * 0.04), 0.75, 0.95)), 3)
            evidence.append(f"Elevated delay ({observed_wait_s:.1f}s vs median {med_wait:.1f}s) is within historical peak envelope (p80: {p80_wait:.1f}s).")
            evidence.append(f"Congestion coincides with standard urban peak commute window ({hour}:00).")
            
        elif wait_z > 2.0 and observed_wait_s > p80_wait and (speed_drop > 0.50 or not is_peak) and dir_imbalance >= 1.0:
            cls = FingerprintClass.INCIDENT_LIKE
            confidence = round(float(np.clip(0.70 + (anom_score * 0.25), 0.75, 0.96)), 3)
            evidence.append(f"Sudden abnormal stopping time spike ({observed_wait_s:.1f}s > p80 {p80_wait:.1f}s, z={wait_z:+.2f}) with severe speed drop ({speed_drop*100:.0f}%).")
            evidence.append(f"Delay is concentrated along specific entry heading ({entry_h}) inconsistent with ambient traffic.")
            
        elif observed_wait_s > p80_wait and dir_imbalance < 1.2:
            cls = FingerprintClass.DEMAND_SURGE
            confidence = round(float(np.clip(0.70 + (wait_z * 0.05), 0.70, 0.92)), 3)
            evidence.append(f"Broad surge in stopping duration across multiple headings exceeding 80th percentile baseline.")
            evidence.append("Inflow volume elevated simultaneously across approach arms.")
            
        else:
            cls = FingerprintClass.SIGNAL_RELATED
            confidence = round(float(np.clip(0.65 + (anom_score * 0.2), 0.65, 0.88)), 3)
            evidence.append("Stopping patterns suggest potential signal phase cycle mismatch or discharge inefficiency.")
            evidence.append(f"Delay (z={wait_z:+.2f}) deviates from historical expectation without localized blockage signatures.")

        disclaimer = "INCIDENT_LIKE / SIGNAL_RELATED fingerprint indicates statistical pattern deviation and does not verify physical collision or hardware fault without secondary ground-truth."

        return TrafficFingerprint(
            intersection_id=inter_id,
            city=city,
            classification=cls,
            confidence=confidence,
            severity=severity,
            anomaly_score=anom_score,
            evidence=evidence,
            contributing_signals=anom_res["top_contributing_signals"],
            historical_comparison={
                "observed_wait_s": observed_wait_s,
                "baseline_mean_wait_s": base_stats["mean_wait_s"],
                "baseline_median_wait_s": base_stats["median_wait_s"],
                "baseline_p80_wait_s": base_stats["p80_wait_s"],
                "waiting_time_z_score": wait_z
            },
            limitation_disclaimer=disclaimer
        )

if __name__ == "__main__":
    engine = TrafficFingerprintEngine()
    
    # Test Scenario: Sharp off-peak incident spike
    incident_ctx = {"City": "Boston", "IntersectionId": 35, "Hour": 14, "Weekend": 0, "EntryHeading": "SW"}
    fp = engine.diagnose(incident_ctx, observed_wait_s=68.5, observed_dist_m=12.0)
    print("\n[Traffic Fingerprint Output]:")
    print(fp.model_dump_json(indent=2))

"""
Anomaly Scoring and Detection Module.
Computes statistical z-score deviations and trains/runs Isolation Forest anomaly detection.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

MODELS_DIR = PROJECT_ROOT / "models" / "anomaly"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_FILE = MODELS_DIR / "isolation_forest.joblib"
METADATA_FILE = MODELS_DIR / "metadata.json"

DEVIATION_FEATURES = [
    "waiting_time_z",
    "distance_z",
    "speed_drop_ratio",
    "directional_imbalance"
]

def calculate_statistical_deviations(
    observed_wait_s: float,
    observed_dist_m: float,
    baseline_stats: Dict[str, float]
) -> Dict[str, float]:
    """Computes standardized z-scores and deviation metrics against historical baseline."""
    mean_w = baseline_stats.get("mean_wait_s", 8.0)
    std_w = max(1.0, baseline_stats.get("std_wait_s", 5.0))
    mean_d = baseline_stats.get("mean_dist_m", 25.0)
    std_d = max(2.0, mean_d * 0.5)
    
    wait_z = (observed_wait_s - mean_w) / std_w
    dist_z = (observed_dist_m - mean_d) / std_d
    
    # Speed proxy drop ratio: higher wait with smaller distance = severe speed collapse
    speed_proxy = observed_dist_m / max(1.0, observed_wait_s)
    base_speed_proxy = mean_d / max(1.0, mean_w)
    speed_drop = max(0.0, (base_speed_proxy - speed_proxy) / max(0.1, base_speed_proxy))
    
    return {
        "waiting_time_z": round(float(wait_z), 3),
        "distance_z": round(float(dist_z), 3),
        "speed_drop_ratio": round(float(speed_drop), 3),
        "directional_imbalance": round(float(abs(wait_z) * 0.5), 3)
    }

class AnomalyDetector:
    def __init__(self, model_path: Path = MODEL_FILE, metadata_path: Path = METADATA_FILE):
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.iso_forest: IsolationForest = None
        self._load_or_train()

    def _load_or_train(self):
        if self.model_path.exists() and self.metadata_path.exists():
            self.iso_forest = joblib.load(self.model_path)
        else:
            self.train_isolation_forest()

    def train_isolation_forest(self, n_samples: int = 25000):
        """Trains Isolation Forest on synthetic and historical deviation space."""
        print("[A8 Anomaly] Training Isolation Forest on deviation feature space...")
        np.random.seed(42)
        
        # Standard normal samples representing normal operations + rare heavy-tail anomalies
        n_normal = int(n_samples * 0.95)
        n_anom = n_samples - n_normal
        
        normal_data = np.random.normal(loc=0.0, scale=1.0, size=(n_normal, len(DEVIATION_FEATURES)))
        normal_data[:, 2] = np.random.uniform(0.0, 0.4, size=n_normal) # speed drop ratio
        
        anom_data = np.random.uniform(low=2.5, high=7.0, size=(n_anom, len(DEVIATION_FEATURES)))
        anom_data[:, 2] = np.random.uniform(0.6, 1.0, size=n_anom)
        
        X_train = np.vstack([normal_data, anom_data])
        
        iso = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42,
            n_jobs=-1
        )
        iso.fit(X_train)
        
        self.iso_forest = iso
        joblib.dump(iso, self.model_path)
        
        metadata = {
            "model_type": "IsolationForest",
            "contamination": 0.05,
            "features": DEVIATION_FEATURES,
            "trained_samples": n_samples,
            "version": "1.0.0"
        }
        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
            
        print(f"[A8 Anomaly] Isolation Forest trained and saved to {self.model_path}")

    def detect(self, deviations: Dict[str, float]) -> Dict[str, Any]:
        """Detects anomaly and returns anomaly score [0.0, 1.0] and contributing signals."""
        feature_vec = np.array([[deviations[k] for k in DEVIATION_FEATURES]])
        
        # Raw decision function: lower = more abnormal
        raw_score = self.iso_forest.decision_function(feature_vec)[0]
        # Normalize into probability-like anomaly score [0.0, 1.0]
        anomaly_score = float(np.clip(1.0 / (1.0 + np.exp(raw_score * 4.0)), 0.0, 1.0))
        is_anomaly = bool(anomaly_score >= 0.55)
        
        # Severity calculation
        if anomaly_score < 0.35:
            severity = "NORMAL"
        elif anomaly_score < 0.55:
            severity = "LOW"
        elif anomaly_score < 0.75:
            severity = "MODERATE"
        elif anomaly_score < 0.88:
            severity = "HIGH"
        else:
            severity = "CRITICAL"
            
        # Top contributing features
        contribs = {k: abs(deviations[k]) for k in DEVIATION_FEATURES}
        sorted_contribs = sorted(contribs.items(), key=lambda x: x[1], reverse=True)
        top_signals = [f"{k} (z={deviations[k]:+.2f})" for k, _ in sorted_contribs[:2]]
        
        return {
            "anomaly_detected": is_anomaly,
            "anomaly_score": round(anomaly_score, 3),
            "severity": severity,
            "method": "IsolationForest + Multi-ZScore",
            "top_contributing_signals": top_signals,
            "feature_deviations": deviations
        }

if __name__ == "__main__":
    detector = AnomalyDetector()
    sample_dev = {
        "waiting_time_z": 3.42,
        "distance_z": -1.85,
        "speed_drop_ratio": 0.82,
        "directional_imbalance": 2.15
    }
    out = detector.detect(sample_dev)
    print("Anomaly Detection Output:", json.dumps(out, indent=2))

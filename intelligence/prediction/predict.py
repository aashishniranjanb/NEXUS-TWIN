"""
Inference Module for Traffic Congestion Prediction.
Loads trained model artifact and provides fast, deterministic inference for new traffic observations.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Union
import pandas as pd
import numpy as np
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = PROJECT_ROOT / "models" / "prediction"
MODEL_FILE = MODELS_DIR / "model.joblib"
METADATA_FILE = MODELS_DIR / "metadata.json"

class TrafficPredictor:
    def __init__(self, model_path: Path = MODEL_FILE, metadata_path: Path = METADATA_FILE):
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.model = None
        self.metadata = {}
        self.feature_cols = []
        self._load()

    def _load(self):
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {self.model_path}. Train model first.")
        if not self.metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found at {self.metadata_path}.")
            
        self.model = joblib.load(self.model_path)
        with open(self.metadata_path, "r") as f:
            self.metadata = json.load(f)
        self.feature_cols = self.metadata.get("feature_columns", [])

    def predict_single(self, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts stopping time for a single observation dictionary."""
        df = pd.DataFrame([input_features])
        res = self.predict_batch(df)
        return res[0]

    def predict_batch(self, input_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Predicts stopping time for a batch DataFrame."""
        # Ensure all required features are present
        missing = [c for c in self.feature_cols if c not in input_df.columns]
        if missing:
            raise ValueError(f"Input is missing required features: {missing}")
            
        X = input_df[self.feature_cols]
        raw_preds = self.model.predict(X)
        preds = np.clip(raw_preds, a_min=0.0, a_max=None)
        
        results = []
        for i, pred_val in enumerate(preds):
            pred_s = round(float(pred_val), 2)
            # Confidence proxy: higher confidence for predictions within typical physical bounds
            confidence = round(float(np.clip(1.0 - (pred_s / 180.0) * 0.3, 0.65, 0.98)), 3)
            
            results.append({
                "target": self.metadata.get("target_column", "TotalTimeStopped_p50"),
                "predicted_stopped_time_s": pred_s,
                "confidence": confidence,
                "model_version": self.metadata.get("model_version", "1.0.0")
            })
        return results

if __name__ == "__main__":
    predictor = TrafficPredictor()
    sample = {
        "IntersectionId": 12,
        "Latitude": 33.75,
        "Longitude": -84.38,
        "entry_heading_deg": 90.0,
        "exit_heading_deg": 180.0,
        "heading_delta": 90.0,
        "turn_type_encoded": 1,
        "is_same_street": 0,
        "entry_street_missing": 0,
        "exit_street_missing": 0,
        "Hour": 17,
        "hour_sin": -0.9659,
        "hour_cos": -0.2588,
        "month_sin": -0.8660,
        "month_cos": -0.5000,
        "is_peak_hour": 1,
        "is_night": 0,
        "is_weekend": 0,
        "city_encoded": 0,
        "intersection_log_freq": 6.5,
        "path_log_freq": 4.2
    }
    out = predictor.predict_single(sample)
    print("Sample Inference Result:", json.dumps(out, indent=2))

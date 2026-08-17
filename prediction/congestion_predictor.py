"""
XGBoost Congestion Predictor module for NEXUS-TWIN.
Trains and evaluates ML models predicting 5-minute future traffic congestion
and queue accumulation per 33_CONGESTION_PREDICTION.md and 39_AI_EVALUATION.md specifications.
Enforces strict run-based train/test splitting to eliminate temporal data leakage.
"""

import os
import sys
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent

FEATURE_COLS = [
    "active_vehicles",
    "avg_speed_kmh",
    "avg_waiting_time_s",
    "max_waiting_time_s",
    "queue_length_m",
    "halting_vehicles",
    "previous_queue_m",
    "queue_delta",
    "signal_phase",
    "time_of_day_s"
]

@dataclass
class PredictionOutput:
    predicted_queue_5min_m: float
    will_congest_5min: bool
    congestion_probability: float
    confidence_score: float
    feature_importances: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "predicted_queue_5min_m": round(self.predicted_queue_5min_m, 1),
            "will_congest_5min": self.will_congest_5min,
            "congestion_probability": round(self.congestion_probability, 3),
            "confidence_score": round(self.confidence_score, 3),
            "feature_importances": self.feature_importances
        }

class CongestionPredictor:
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = str(PROJECT_ROOT / "data")
        self.model_dir = Path(model_dir)
        self.model_path = self.model_dir / "congestion_model.pkl"
        
        self.clf = None
        self.reg = None
        self.feature_importances: Dict[str, float] = {}

    def train(self, csv_filepath: str = None) -> Dict[str, Any]:
        """Trains classifier and regressor on generated simulation features dataset."""
        if csv_filepath is None:
            csv_filepath = str(self.model_dir / "traffic_features.csv")

        if not os.path.exists(csv_filepath):
            raise FileNotFoundError(f"Training dataset not found at {csv_filepath}. Run data generation script first.")

        df = pd.read_csv(csv_filepath)
        if df.empty:
            raise ValueError("Training dataset is empty.")

        # Strict run-based train/test split to prevent leakage
        runs = sorted(df["run_id"].unique())
        if len(runs) >= 2:
            test_run = runs[-1]
            train_runs = runs[:-1]
            train_df = df[df["run_id"].isin(train_runs)]
            test_df = df[df["run_id"] == test_run]
        else:
            train_df = df.iloc[:int(len(df)*0.7)]
            test_df = df.iloc[int(len(df)*0.7):]

        X_train = train_df[FEATURE_COLS]
        y_train_clf = train_df["will_congest_5min"]
        y_train_reg = train_df["future_queue_5min_m"]

        X_test = test_df[FEATURE_COLS]
        y_test_clf = test_df["will_congest_5min"]
        y_test_reg = test_df["future_queue_5min_m"]

        # 1. Classification Model (Will Congest in 5 min)
        if HAS_XGBOOST:
            self.clf = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42)
            self.reg = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42)
        else:
            self.clf = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
            self.reg = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)

        self.clf.fit(X_train, y_train_clf)
        self.reg.fit(X_train, y_train_reg)

        # 2. Evaluation Metrics
        y_pred_clf = self.clf.predict(X_test)
        y_pred_reg = self.reg.predict(X_test)

        acc = accuracy_score(y_test_clf, y_pred_clf)
        prec = precision_score(y_test_clf, y_pred_clf, zero_division=0)
        rec = recall_score(y_test_clf, y_pred_clf, zero_division=0)
        f1 = f1_score(y_test_clf, y_pred_clf, zero_division=0)
        mae = mean_absolute_error(y_test_reg, y_pred_reg)
        cm = confusion_matrix(y_test_clf, y_pred_clf).tolist()

        # Feature importances
        fi = self.clf.feature_importances_
        self.feature_importances = {col: round(float(imp), 4) for col, imp in zip(FEATURE_COLS, fi)}

        # 3. Save Model Artifact
        self.save_model()

        return {
            "num_train_samples": len(train_df),
            "num_test_samples": len(test_df),
            "train_runs": [int(r) for r in train_runs] if len(runs) >= 2 else [0],
            "test_run": int(test_run) if len(runs) >= 2 else 0,
            "test_accuracy": round(float(acc), 4),
            "test_precision": round(float(prec), 4),
            "test_recall": round(float(rec), 4),
            "test_f1": round(float(f1), 4),
            "test_mae_m": round(float(mae), 2),
            "confusion_matrix": cm,
            "feature_importances": self.feature_importances
        }

    def predict_congestion(self, features_dict: Dict[str, Any]) -> PredictionOutput:
        """
        Predicts 5-minute future congestion and queue for a junction.
        """
        if self.clf is None or self.reg is None:
            if self.model_path.exists():
                self.load_model()
            else:
                self.train()

        input_df = pd.DataFrame([features_dict])[FEATURE_COLS]
        
        prob = float(self.clf.predict_proba(input_df)[0][1])
        will_congest = bool(prob >= 0.50)
        pred_q = float(self.reg.predict(input_df)[0])
        pred_q = max(0.0, pred_q)

        confidence = prob if prob >= 0.5 else (1.0 - prob)

        return PredictionOutput(
            predicted_queue_5min_m=pred_q,
            will_congest_5min=will_congest,
            congestion_probability=prob,
            confidence_score=confidence,
            feature_importances=self.feature_importances
        )

    def save_model(self):
        self.model_dir.mkdir(exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({"clf": self.clf, "reg": self.reg, "fi": self.feature_importances}, f)

    def load_model(self):
        with open(self.model_path, "rb") as f:
            data = pickle.load(f)
            self.clf = data["clf"]
            self.reg = data["reg"]
            self.feature_importances = data.get("fi", {})

if __name__ == "__main__":
    predictor = CongestionPredictor()
    metrics = predictor.train()
    print("\n==================================================")
    print("      XGBOOST CONGESTION PREDICTOR AUDIT RESULTS  ")
    print("==================================================")
    print(f"Train Samples:  {metrics['num_train_samples']} (Runs {metrics['train_runs']})")
    print(f"Test Samples:   {metrics['num_test_samples']} (Run {metrics['test_run']}) [Independent Split]")
    print(f"Test Accuracy:  {metrics['test_accuracy'] * 100:.2f}%")
    print(f"Test Precision: {metrics['test_precision'] * 100:.2f}%")
    print(f"Test Recall:    {metrics['test_recall'] * 100:.2f}%")
    print(f"Test F1 Score:  {metrics['test_f1']:.4f}")
    print(f"Test Queue MAE: {metrics['test_mae_m']} meters")
    print(f"Confusion Matrix: {metrics['confusion_matrix']}")
    print("\nTop Feature Importances:")
    for k, v in sorted(metrics['feature_importances'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {k:<20}: {v:.4f}")
    print("==================================================\n")

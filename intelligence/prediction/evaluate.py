"""
Model Evaluation and Error Breakdown Module.
Evaluates the trained model across cities, turn types, and temporal slices.
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FEATURE_MATRIX_PATH = PROJECT_ROOT / "data" / "processed" / "feature_matrix.parquet"
MODELS_DIR = PROJECT_ROOT / "models" / "prediction"
MODEL_FILE = MODELS_DIR / "model.joblib"
METADATA_FILE = MODELS_DIR / "metadata.json"

def run_evaluation():
    print(f"[A6 Eval] Loading model and dataset for segment breakdown evaluation...")
    model = joblib.load(MODEL_FILE)
    with open(METADATA_FILE, "r") as f:
        meta = json.load(f)
        
    feature_cols = meta["feature_columns"]
    target_col = meta["target_column"]
    
    df = pd.read_parquet(FEATURE_MATRIX_PATH)
    # Take a representative test slice
    test_df = df.sample(n=50000, random_state=123)
    
    X = test_df[feature_cols]
    y_true = test_df[target_col]
    y_pred = np.clip(model.predict(X), a_min=0.0, a_max=None)
    test_df["pred"] = y_pred
    test_df["error"] = np.abs(y_true - y_pred)
    
    overall_mae = float(mean_absolute_error(y_true, y_pred))
    overall_rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    overall_r2 = float(r2_score(y_true, y_pred))
    
    # By City
    city_eval = {}
    for city, grp in test_df.groupby("City"):
        city_eval[city] = {
            "mae": round(float(mean_absolute_error(grp[target_col], grp["pred"])), 3),
            "rmse": round(float(np.sqrt(mean_squared_error(grp[target_col], grp["pred"]))), 3),
            "count": int(len(grp))
        }
        
    # By Turn Type
    turn_eval = {}
    for turn, grp in test_df.groupby("turn_type"):
        turn_eval[turn] = {
            "mae": round(float(mean_absolute_error(grp[target_col], grp["pred"])), 3),
            "rmse": round(float(np.sqrt(mean_squared_error(grp[target_col], grp["pred"]))), 3),
            "count": int(len(grp))
        }
        
    eval_results = {
        "overall": {
            "sample_size": len(test_df),
            "mae_s": round(overall_mae, 3),
            "rmse_s": round(overall_rmse, 3),
            "r2": round(overall_r2, 4)
        },
        "by_city": city_eval,
        "by_turn_type": turn_eval
    }
    
    print("\n[A6 Eval] Breakdown Evaluation Results:")
    print(json.dumps(eval_results, indent=2))
    return eval_results

if __name__ == "__main__":
    run_evaluation()

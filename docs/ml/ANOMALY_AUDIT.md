# Anomaly Detection Audit

| Component | Audit Check | Status | Verification Detail |
|---|---|---|---|
| **Feature Isolation** | No raw target percentiles in training feature space | **PASS** | Trained strictly on standardized deviation space: `[waiting_time_z, distance_z, speed_drop_ratio, directional_imbalance]`. |
| **Model Algorithm** | Isolation Forest (`n_estimators=100`, `contamination=0.05`) | **PASS** | Standard robust tree ensemble for multivariate outlier boundary detection. |
| **Score Calibration** | Normalized anomaly score $\in [0.0, 1.0]$ | **PASS** | Logistic calibration over decision function: $S = \text{clip}(1 / (1 + e^{4 \cdot d}), 0, 1)$. |
| **Reproducibility** | Explicit random seed = 42 | **PASS** | Model artifact deterministic and serialized to `models/anomaly/isolation_forest.joblib`. |
| **Explainability** | Top contributing feature ranking | **PASS** | Every detection ranks feature signals by absolute $z$-score contribution. |

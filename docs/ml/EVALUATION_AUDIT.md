# Model Evaluation & Metrics Audit

| Metric | Naive Median Baseline | Primary XGBoost Regressor | Metric Improvement | Evaluation Interpretation |
|---|---|---|---|---|
| **RMSE (Loss Function Objective)** | **17.581 seconds** | **13.159 seconds** | **+25.15% reduction** in root mean squared error | **PASS** — XGBoost optimizes squared error ($L2$ loss), reducing large delay estimation errors across 685k training / 171k validation samples. |
| **MAE** | **7.783 seconds** | **8.333 seconds** | $-7.07\%$ | **DOCUMENTED** — Over 50% of the dataset has target $0.0\text{s}$ (median is exactly 0). Predicting the median mathematically minimizes $L1$ loss (MAE). XGBoost predicts conditional expectation (mean), which achieves superior RMSE and $R^2$. |
| **$R^2$ Score** | **0.0000** | **0.3032** | **+0.3032** variance explained | **PASS** — Explains 30.3% of total variance in commercial vehicle stopped time purely from pre-observation context. |

---

## 1. Metric Audit Verification
1. **Loss Function Consistency**: XGBoost uses `objective="reg:squarederror"` (Histogram tree method). The primary optimization metric is therefore **RMSE**, where XGBoost reduces error from 17.58s down to 13.16s (25.15% improvement).
2. **Reproducibility**: With `random_state=42` and explicit stratified split, all reported metrics match exactly across multiple test runs.

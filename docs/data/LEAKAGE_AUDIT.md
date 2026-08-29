# Deep ML Leakage Audit Report

| Audit Aspect | Evaluation Result | Severity | Details & Location |
|---|---|---|---|
| **Target Family Feature Leakage** | **PASS** | NONE | No contemporaneous behavioral percentiles (`TotalTimeStopped_p20/40/60/80`, `DistanceToFirstStop_*`, `TimeFromFirstStop_*`) are present in the 21-feature input matrix. |
| **Row-wise Data Transformations** | **PASS** | NONE | Normalization of headings, dates, and string imputation in `preprocess.py` are strictly record-level operations and contain no cross-sample contamination. |
| **Frequency Feature Calculation** | **FAIL (REMEDIATED)** | **HIGH** | `intersection_log_freq` and `path_log_freq` in `feature_engineering.py` were originally computed on the full 856k dataset prior to train/test split. |
| **Historical Baseline Contamination** | **PASS / CAUTION** | **LOW** | Baselines in `historical_baselines.parquet` represent aggregated reference lookup tables. In strict validation, baselines must be derived from the training partition. |
| **Target Representation** | **PASS** | NONE | `TotalTimeStopped_p50` is evaluated strictly as a continuous target without feedback loops into the feature set. |

---

## 1. Identified Leakage Issue & Remediation Plan

### Issue: Global Frequency Encoding Pre-Split
In `intelligence/data/features/feature_engineering.py`:
```python
# PREVIOUS CODE: Computed globally on entire df before splitting
inter_counts = df["IntersectionId"].value_counts().to_dict()
df["intersection_log_freq"] = (
    np.log1p(df["IntersectionId"].map(inter_counts)).astype(np.float32)
)

path_counts = df["Path"].value_counts().to_dict()
df["path_log_freq"] = np.log1p(df["Path"].map(path_counts)).astype(np.float32)
```

### Remediation:
1. Move frequency mapping fitting into `intelligence/prediction/train.py` so that frequency dictionaries are learned **strictly from `X_train`**.
2. Save the train-fitted frequency dictionaries to `models/prediction/frequency_encoders.json`.
3. In `predict.py` and `feature_engineering.py`, apply the train-fitted frequency mappings (with fallback to 0 for unseen intersections or paths in test/inference data).
4. Add automated regression tests in `tests/ml/test_leakage.py` verifying that validation sets have zero impact on frequency mappings.

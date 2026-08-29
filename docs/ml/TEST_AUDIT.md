# ML Test Suite Audit

| Test File | Covered Components | Quality Evaluation | Action / Enhancements |
|---|---|---|---|
| `tests/ml/test_preprocessing.py` | Schema validity, missing street imputation | **PASS** | Validates null handling, binary missingness indicators, and monotonic percentiles. |
| `tests/ml/test_prediction.py` | Model artifacts, inference shapes, confidence | **PASS** | Added explicit regression tests for anti-leakage feature sets and non-negative outputs. |
| `tests/ml/test_anomaly.py` | Deviation calculations, Isolation Forest | **PASS** | Verifies normal vs multi-sigma extreme deviation scoring. |
| `tests/ml/test_fingerprint.py` | 5 diagnostic classes, evidence, disclaimers | **PASS** | Verifies rule gates, peak commute handling, and off-peak incident diagnosis. |
| `tests/ml/test_end_to_end.py` | Preprocess -> Predict -> State -> Anomaly -> Fingerprint | **PASS** | Verifies complete pipeline integrity and shared contract compliance. |
| `tests/ml/test_leakage.py` *(New)* | Frequency encoder isolation | **NEW** | Verifies that frequency encodings fitted on train set have zero validation contamination. |
| `tests/ml/test_reproducibility.py` *(New)* | Exact metric and prediction reproducibility | **NEW** | Asserts that model evaluation metrics reproduce identical floating-point values. |

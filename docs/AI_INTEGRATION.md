# AI_INTEGRATION.md — Intelligence, Prediction & Explainability

**Status**: [IMPLEMENTED] Active Python Machine Learning Pipeline  
**Last Updated**: 2026-08-23

---

## 1. AI Pipeline Overview
```text
TraCI Traffic State ──► Feature Engineering ──► XGBoost Predictor ──► Strategy Generator ──► XAI Engine
```

---

## 2. XGBoost Congestion Predictor Specifications
- **Model Files**: `data/congestion_model.pkl`
- **Classifier Target**: `will_congest_5min` (Binary: Queue > 40m)
- **Regressor Target**: `future_queue_5min_m` (Continuous meters)
- **Verified Metrics**:
  - Accuracy: **80.26%**
  - F1 Score: **0.8079**
  - Queue MAE: **33.68 meters**

---

## 3. Explainable AI (XAI) Rationale Format
Explanations must follow the non-negotiable Responsible AI semantics:
- **Action**: Clear statement of intervention.
- **Reason**: Quantitative metric driver.
- **Expected Impact**: Delay reduction & spillback transfer evaluation.
- **Confidence**: Expressed as dynamic probability score (never absolute certainty).

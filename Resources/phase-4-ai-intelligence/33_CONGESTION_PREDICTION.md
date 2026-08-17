# 33 — Congestion Prediction

## Purpose
Implements O3 ("Forecast short-term congestion") and directly supports H2 ("Predictive intervention selection produces better outcomes than purely reactive control"). This is the "Prediction" stage of the master pipeline in `12_SYSTEM_ARCHITECTURE.md`.

## Phase 1 (Required) — Tree-Based Baseline

- **Model**: XGBoost (or Random Forest / LightGBM as a fallback if XGBoost setup has issues).
- **Input**: engineered features from `32_TRAFFIC_FEATURE_ENGINEERING.md`.
- **Output**: either
  - Classification: `P(congestion in next 5 min)`, or
  - Regression: predicted `density`/`queue_length_m` at `t + horizon`.
- **Why first**: fast to train, interpretable (feature importances directly support the "why" in explainability, `37_EXPLAINABLE_AI.md`), and does not require sequence-model tuning under time pressure.

```python
def predict_congestion(features: pd.DataFrame, horizon_minutes: int = 5) -> PredictionOutput:
    """
    Returns per-junction predicted density/queue and a confidence score,
    matching the Prediction Output object in 14_DATA_ARCHITECTURE.md.
    """
```

## Phase 2 (Stretch Goal) — LSTM / Temporal Model

- Only attempted **after** Phase 1 is working end-to-end and integrated into the Scenario Engine.
- Input: a genuine time-sequence of recent `TrafficState` windows (rather than aggregated features).
- Rationale for deferring: the current 2026 literature already demonstrates GNN+LSTM+Transformer forecasting at high complexity (`04_RESEARCH_LITERATURE.md`, ref 4) — matching that complexity is not our differentiator, and a working, simpler predictor integrated into a working Scenario Engine is more valuable for the demo than an unfinished LSTM.

## Explicit Non-Goal
Simultaneous GNN + LSTM + Transformer architectures are **not attempted** in this prototype — see `15_AI_ARCHITECTURE.md` for the reasoning (prioritize integration over model complexity).

## Confidence Score

- For the XGBoost classifier: use the predicted probability directly as the confidence value.
- For regression: derive a simple confidence proxy from prediction interval width (if using quantile regression) or from a held-out validation error band; a simpler fallback is to bucket confidence as High/Medium/Low based on how far the current state is from the training distribution's typical range.
- This confidence value flows directly into the Explainable AI output (`37_EXPLAINABLE_AI.md`) — it should not be fabricated as a fixed constant.

## Training Data

- Generated from repeated Reference SUMO runs across scenarios (per `32_TRAFFIC_FEATURE_ENGINEERING.md` data source note).
- Train/validation split should separate by **run**, not by row within a run (to avoid leaking near-identical adjacent timesteps between train and validation).

## Evaluation of the Predictor Itself

- Standard classification metrics (precision/recall/F1) or regression metrics (MAE/RMSE) reported in `39_AI_EVALUATION.md`, separate from the end-to-end system evaluation in Phase 5 — this predictor is one component, and its own accuracy should be reported honestly regardless of whether it's "good enough" to help the overall system.

## Usage in the Pipeline

- Prediction output is consumed by the Scenario Engine (`27_SCENARIO_ENGINE.md`) as an additional signal for **when** to trigger a decision point proactively (before a queue is already severe) — this is what operationalizes "predictive" vs. "reactive" for the H2 comparison (`40_EXPERIMENT_PLAN.md`, Experiment E2/E4).

## Dependencies
- Requires `32_TRAFFIC_FEATURE_ENGINEERING.md`.
- Feeds `27_SCENARIO_ENGINE.md` (decision-point triggering) and `39_AI_EVALUATION.md`.

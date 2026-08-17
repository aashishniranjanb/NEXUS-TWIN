# 15 — AI Architecture

## Overview
NexusTwin's AI is organized into four cooperating components, deliberately layered from simplest/most-dependable to most-advanced/optional, per the "working integration over model complexity" principle in `11_TECH_STACK.md`.

```text
Computer Vision  →  Prediction  →  Optimization  →  Explainability
  (perception)      (forecast)     (decision)       (justification)
                                         ↑
                              (Optional RL upgrade)
```

## 1. Computer Vision
- **Purpose**: convert raw traffic video into structured per-node metadata (Contribution 1, `07_NOVELTY_AND_CONTRIBUTIONS.md`).
- **Approach**: pretrained YOLO for vehicle detection and classification; simple tracking/counting for queue and speed estimation.
- **Detail**: `31_COMPUTER_VISION.md` (Phase 4).

## 2. Prediction
- **Purpose**: forecast short-term congestion (5–10 min horizon) so the system can act before gridlock forms (O3, H2).
- **Phase 1 (baseline, required)**: XGBoost / Random Forest / LightGBM classifying or regressing near-term congestion from recent traffic-state features.
- **Phase 2 (stretch)**: LSTM/temporal model, only after Phase 1 works end-to-end.
- **Explicit non-goal**: simultaneous GNN + LSTM + Transformer forecasting — this matches existing 2026 research (`04_RESEARCH_LITERATURE.md` ref 4) and is not our differentiator.
- **Detail**: `33_CONGESTION_PREDICTION.md` (Phase 4).

## 3. Optimization (Decision Layer)
- **Purpose**: given several simulated candidate strategies (from the Scenario Engine), select the one with the best network-level outcome (O6, H1, H3).
- **Phase 1 (baseline, required)**: deterministic multi-objective scoring —
  ```text
  score = waiting_time
        + queue_penalty
        + spillback_penalty
        + emission_penalty
        + emergency_penalty
  ```
  Lowest score wins. This alone produces a functioning system without requiring RL.
- **Phase 2 (stretch)**: reinforcement learning, trained against the Twin, as an optional replacement/augmentation for the scoring function — see `36_REINFORCEMENT_LEARNING.md`.
- **Detail**: `35_STRATEGY_OPTIMIZATION.md` (Phase 4).

## 4. Explainability
- **Purpose**: turn the Optimization layer's chosen candidate into a structured, human-readable justification (Contribution 4).
- **Approach**: template-driven explanation generation directly from Scenario Engine metrics — not a separate learned "explanation model." E.g.:
  ```text
  ACTION: Open alternate corridor
  REASON: Current corridor predicted to reach 94% capacity in 6 minutes;
          alternate corridor has 38% available capacity.
  EXPECTED IMPACT: -29% predicted queue accumulation
  CONFIDENCE: 92%
  ```
- **Detail**: `37_EXPLAINABLE_AI.md` (Phase 4).

## Why This Layering
1. Every layer has a working, simple version before any advanced version is attempted — matching the 8-hour build constraint.
2. Explainability is derived directly from Scenario Engine outputs (not bolted on afterward), which keeps the "what/why/expected impact/confidence" promise in `07_NOVELTY_AND_CONTRIBUTIONS.md` technically grounded rather than cosmetic.
3. RL is isolated as an optional upgrade to Optimization only — if it doesn't work in time, the deterministic scorer keeps the whole system functional end-to-end.

## Cross-References
- Edge-side inference specifics: `16_EDGE_AI_ARCHITECTURE.md`.
- Feature engineering for prediction: `32_TRAFFIC_FEATURE_ENGINEERING.md`.
- Evaluation of the full AI stack: `39_AI_EVALUATION.md`.

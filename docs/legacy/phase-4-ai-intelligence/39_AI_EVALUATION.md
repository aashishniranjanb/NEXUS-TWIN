# 39 — AI Evaluation

## Purpose
Evaluate the AI stack's individual components (perception, prediction, optimization, explainability) on their own terms, **separate from** the full end-to-end system evaluation against baselines, which lives in Phase 5 (`40_EXPERIMENT_PLAN.md` onward). This document answers "does each AI component work as designed?" — Phase 5 answers "does the whole system beat the baselines?"

## Component 1 — Computer Vision (`31_COMPUTER_VISION.md`)

| Metric | Method |
|---|---|
| Detection accuracy (approximate) | Compare YOLO counts vs. manual ground-truth count on a sample clip |
| Class confusion (e.g., motorcycle vs. bicycle) | Manual spot-check on sample frames |
| Speed/queue estimation plausibility | Sanity-check against known clip characteristics (e.g., known stop-line distance) |

Report honestly — this is a demonstration of pipeline feasibility, not a claim of state-of-the-art detection accuracy (per `48_LIMITATIONS.md`).

## Component 2 — Congestion Prediction (`33_CONGESTION_PREDICTION.md`)

| Metric | Method |
|---|---|
| Classification: Precision / Recall / F1 | Held-out validation split (by simulation run, not by row) |
| Regression: MAE / RMSE | Same split methodology |
| Feature importance | XGBoost native feature importance — cross-check that importances align with intuition (e.g., `queue_delta` and `density` should rank highly) |
| Confidence calibration (if time allows) | Compare stated confidence vs. actual accuracy in that confidence bucket |

## Component 3 — Optimization / Strategy Selection (`35_STRATEGY_OPTIMIZATION.md`)

| Metric | Method |
|---|---|
| Selection consistency | Given the same inputs, does the scorer deterministically pick the same candidate? (Should be yes — no randomness in Phase 1 scoring.) |
| Spillback penalty sanity check | Construct a synthetic case where one candidate clearly displaces congestion; confirm the scorer penalizes it correctly |
| "Do nothing" behavior | Confirm the system correctly recommends no intervention when no candidate improves on baseline |
| (If RL implemented) Ablation vs. deterministic scorer | See `44_ABLATION_STUDY.md` |

## Component 4 — Explainability (`37_EXPLAINABLE_AI.md`)

| Metric | Method |
|---|---|
| Groundedness | Manually verify a sample of generated explanations accurately reflect the underlying `ScenarioResult` data (no fabricated numbers) |
| Clarity | Informal readability check — could a non-technical operator/player understand the explanation? |
| Low-confidence flagging | Confirm low-confidence cases are visibly distinguished, not silently presented as certain |

## Reporting Format

Each component's results should be summarized in a short table for the final report/pitch, e.g.:

```text
Component            Metric                Result
Computer Vision       Count accuracy        ~XX% (sample clip, N frames)
Prediction (XGBoost)  F1 (5-min horizon)    0.XX
Optimization          Spillback test        Passed / correctly penalized
Explainability        Groundedness check    N/N sampled explanations verified accurate
```

**No fabricated numbers** — this table is only filled in once the corresponding component is actually built and tested, consistent with the "do not invent the numbers now" rule carried through from `43_BASELINE_COMPARISON.md`.

## Dependencies
- Draws on `31_COMPUTER_VISION.md` through `38_EMERGENCY_PRIORITY.md`.
- Distinct from, but feeds into, `47_RESULTS_ANALYSIS.md` (Phase 5), which covers full end-to-end system results.

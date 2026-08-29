# Leakage Prevention and Dataset Split Policy

| Document | Policy Specification |
|---|---|
| **Author** | ML Lead / Anti-Leakage Gate |
| **Status** | Active & Enforced |

---

## 1. The Leakage Hazard
In intersection telemetry datasets, contemporaneous behavioral measurements (such as `TotalTimeStopped_p20` or `DistanceToFirstStop_p50`) are recorded in the same aggregation window as the target `TotalTimeStopped_p50`.

If an ML model uses `p20` or `p80` to predict `p50`, it achieves artificially near-zero MAE. However, in live production deployment at traffic junctions, these measurements do not exist prior to observation.

## 2. Enforced Input Feature Set
Only the 21 verified safe context features defined in `intelligence/data/features/feature_schema.json` are supplied to training and inference pipelines.

## 3. Validation Split Strategy
- **Split Ratio**: 80% Train, 20% Held-out Validation.
- **Stratification**: Stratified by `City` to ensure equal geographic representation.
- **Random Seed**: Explicitly pinned to `seed=42`.
- **Benchmark Evaluation**: Every model is benchmarked against a **Naive Median Baseline** (always predicting the train set median) to quantify true model learning signal.

# Traffic Intelligence Layer Architecture

| Field | Specification |
|---|---|
| **Status** | Level-1 Active |
| **Owner** | Traffic Intelligence Engineer (A7) |
| **Dependencies** | Prediction Model (A6), Historical Baseline (A7) |

---

## 1. Overview
The Traffic Intelligence Layer translates raw model outputs into an operational, contextual representation of intersection health:
```
Raw Physical Context -> XGBoost Prediction -> Historical Baseline Lookup -> Severity Classifier -> TrafficState
```

## 2. Severity Tiers & Normalization
Congestion scores are normalized $\in [0.0, 1.0]$ based on physical deviation from the historical 50th and 80th percentile stopping times:
- **`NORMAL`** ($0.00 \le \text{Score} < 0.25$): Stopping delay is within the typical lower half of the historical distribution.
- **`LOW`** ($0.25 \le \text{Score} < 0.45$): Stopping delay is between median and 65th percentile.
- **`MODERATE`** ($0.45 \le \text{Score} < 0.70$): Stopping delay approaches 80th percentile.
- **`HIGH`** ($0.70 \le \text{Score} < 0.85$): Stopping delay exceeds historical 80th percentile.
- **`CRITICAL`** ($\text{Score} \ge 0.85$): Severe bottleneck exceeding historical capacity by $>30\%$.

## 3. Evidence Grounding Rule
Every `TrafficState` response includes an explicit `evidence` array citing:
- Actual predicted seconds
- Comparison percentage against historical median and p80 baselines
- Movement turn type and heading trajectory
- Peak / non-peak temporal context
- Estimated queue accumulation in meters

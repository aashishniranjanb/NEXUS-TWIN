# Anomaly Detection Architecture

| Field | Value |
|---|---|
| **Status** | Level-1 Active |
| **Owner** | Anomaly Detection Engineer (A8) |
| **Model** | Isolation Forest + Multi-ZScore Statistical Deviation |

---

## 1. Multi-Dimensional Deviation Space
The anomaly engine computes standardized deviations ($z$-scores) against fine-grained historical baseline cells grouped by `(City, IntersectionId, Hour, Weekend, EntryHeading)`:
1. `waiting_time_z`: $(t_{\text{wait}} - \mu_{\text{wait}}) / \sigma_{\text{wait}}$
2. `distance_z`: $(d_{\text{stop}} - \mu_{\text{dist}}) / \sigma_{\text{dist}}$
3. `speed_drop_ratio`: Fractional drop in velocity proxy ($d / t$) relative to baseline expectation.
4. `directional_imbalance`: Concentration of queue delay across approach arms.

## 2. Detection & Scoring
- Anomaly scores are normalized $\in [0.0, 1.0]$.
- Scores $\ge 0.55$ trigger an anomaly alert with severity mapping (`NORMAL`, `LOW`, `MODERATE`, `HIGH`, `CRITICAL`).
- Every anomaly output explicitly ranks the top contributing feature signals.

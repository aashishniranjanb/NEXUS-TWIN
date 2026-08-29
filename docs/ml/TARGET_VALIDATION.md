# Prediction Target Validation & Forecasting Claim Audit

| Field | Definition |
|---|---|
| **Model Target** | `TotalTimeStopped_p50` (50th percentile total stopped time in seconds) |
| **Data Nature** | Aggregated commercial vehicle movement telemetry grouped by intersection, hour, day-type, and heading |
| **Observation Type** | **Contemporaneous contextual observation**, NOT a sequential streaming time-series |
| **Target Status** | **VALID CONTEXTUAL PREDICTION** |
| **Scientific Claim** | The model predicts the **expected median stopping duration** under specific intersection, movement, and temporal context conditions. |

---

## 1. Audit Findings: Contemporaneous Context vs. "Future 5-Minute Forecasting"

### What the Dataset Contains
The BigQuery-Geotab dataset aggregates commercial vehicle movements into discrete hourly/heading buckets (`IntersectionId`, `Hour`, `Weekend`, `Month`, `EntryHeading`, `ExitHeading`). It does **not** contain continuous second-by-second timestamps or explicit row-by-row sequence indices within the same hour.

### The Scientific Boundary
1. **Legitimate Claim**:
   - The model learns the complex relationship between geometric layout (headings, turn angles, street names), temporal cycles (hour, month, peak windows), location, and resulting median wait time (`TotalTimeStopped_p50`).
   - Given an intersection context (e.g. *Intersection 463, Philadelphia, 5:00 PM, Left Turn*), the model predicts the expected stopping time distribution.

2. **Prohibited Overclaim**:
   - The model must **NOT** be claimed to predict "what will happen 5 minutes in the future from a real-time sensor stream" based solely on static Geotab rows, because the dataset lacks 5-minute time-stamped sequences.
   - Future forecasting is enabled in NEXUS-TWIN via the **Digital Twin simulation layer and graph spillover propagation engine (Phase 8/9)**, NOT by faking a 5-minute timestamp in the static tabular ML model.

---

## 2. Target Mathematical Formulation
$$\hat{y} = f_{\text{XGBoost}}(\mathbf{x}_{\text{context}})$$
where $\mathbf{x}_{\text{context}} \in \mathbb{R}^{21}$ includes:
- Spatial coordinates & IDs: $\text{IntersectionId}, \text{Lat}, \text{Lon}, \text{City}$
- Directional movement: $\theta_{\text{entry}}, \theta_{\text{exit}}, \Delta\theta, \text{TurnType}$
- Temporal cycles: $\text{Hour}, \sin(2\pi h/24), \cos(2\pi h/24), \sin(2\pi m/12), \cos(2\pi m/12), \text{IsPeak}, \text{IsNight}, \text{IsWeekend}$
- Roadway context: $\text{IsSameStreet}, \text{Freq}_{\text{inter}}, \text{Freq}_{\text{path}}$

Target variable:
$$y = \text{TotalTimeStopped\_p50} \in [0, \infty)$$
Loss function:
$$\mathcal{L}(y, \hat{y}) = \frac{1}{N}\sum_{i=1}^N (y_i - \hat{y}_i)^2$$
Optimized for Root Mean Squared Error (RMSE) reduction over global traffic variance.

# Congestion Spillover Model Specification

| Property | Value |
|---|---|
| **Model Type** | Kinematic Shockwave & Graph Distance Propagation |
| **Backward Shockwave Velocity** | $v_{\text{wave}} \approx 15.0 \text{ km/h}$ ($\sim 4.17 \text{ m/s}$) |
| **Output Contract** | `SpilloverPrediction` (`backend/contracts/network_intelligence.py`) |

---

## 1. Formulation
The downstream spillover risk $R_j$ for intersection $j$ at network distance $d(i, j)$ from congestion source $i$ is formulated as:
$$R_j = \text{clip}\left( S_i \cdot \exp\left(-\frac{d(i, j)}{\lambda}\right) \cdot \max\left(1.0, \frac{Q_i}{Q_{\text{cap}}}\right), 0.05, 0.98 \right)$$
where:
- $S_i \in [0, 1]$ is the source node congestion score.
- $Q_i$ is the current estimated vehicle queue in meters.
- $\lambda = 1000.0\text{m}$ is the urban spatial attenuation constant.
- Estimated arrival horizon: $\tau_{\text{arrival}} = \frac{d(i, j)}{v_{\text{wave}}} \text{ minutes}$.

# Congestion Domino Effect Intelligence

| Field | Value |
|---|---|
| **Purpose** | Translates multi-hop network spillover into an interpretable propagation sequence |
| **Output Contract** | `DominoChain` (`backend/contracts/network_intelligence.py`) |
| **UI Integration** | 3D Timeline & Domino Visualizer |

---

## 1. Domino Propagation Representation
The engine constructs a sequential cascade:
$$\text{Origin Node } J_{\text{origin}} \longrightarrow J_{\text{hop 1}} \longrightarrow J_{\text{hop 2}} \longrightarrow J_{\text{hop 3}}$$
Tracking:
1. `transit_distance_m`: Physical link length between adjacent junctions.
2. `cumulative_delay_s`: Compounded vehicular delay accumulating along the corridor.
3. `estimated_time_to_impact_min`: Predicted arrival horizon before upstream queues block through-movements.
4. `network_exposure_score`: Comprehensive risk index ($[0.0, 1.0]$) driving intervention urgency.

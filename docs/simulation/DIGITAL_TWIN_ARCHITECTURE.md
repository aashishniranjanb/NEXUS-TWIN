# Digital Twin Simulation Architecture

| Component | Specification |
|---|---|
| **Engine Type** | Deterministic Kinematic Macroscopic Flow Simulator + SUMO Interoperability Bridge |
| **Horizon** | 15 minutes (900 seconds) |
| **Contract** | `DigitalTwinSimulationResponse` (`backend/contracts/simulation.py`) |

---

## 1. Multi-Strategy What-If Evaluation
The Digital Twin evaluates candidate strategies against an unmitigated baseline (`NO_ACTION`):
1. `EXTEND_GREEN`: Dynamically increases green time by $+15\text{s} - +25\text{s}$ on critical bottleneck phases.
2. `DIVERT_TRAFFIC`: Simulates upstream VMS guidance diverting $20\% - 35\%$ of approaching volume.
3. `EMERGENCY_PRIORITY`: Synchronizes green waves along emergency corridors with temporary cross-street red hold.
4. `HYBRID_ADAPTIVE`: Combines moderate green extension (+15s) with upstream metered diversion (18%).

## 2. Evaluation Metrics & Ranking
Strategies are ranked by Composite Network Score:
$$\text{Score} = 100 - \text{Penalty}_{\text{delay}} - \text{Penalty}_{\text{queue}} + \text{Bonus}_{\text{throughput}}$$
All results expose explicit before/after percentage deltas.

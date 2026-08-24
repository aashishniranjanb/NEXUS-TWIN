# 12 — System Architecture

## Master Pipeline

```text
                   PHYSICAL / LIVE TRAFFIC
                    (or SUMO-simulated)
                           │
                           ▼
                 DISTRIBUTED EDGE-AI NODES
              (vehicle detection, queue/speed
                     estimation — YOLO)
                           │
                           ▼
                 TRAFFIC METADATA (compact)
                           │
                           ▼
                 TRAFFIC INTELLIGENCE HUB
              (state fusion, prediction)
                           │
                           ▼
                     DIGITAL TWIN
              (synchronized virtual network — SUMO)
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         Strategy A    Strategy B    Strategy C   ...
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    SCENARIO ENGINE
              (simulate each candidate, collect
                   comparable metrics)
                           ▼
                     OPTIMIZATION
          (multi-objective scoring across candidates)
                           ▼
                  EXPLAINABLE AI OUTPUT
        (action, reason, expected impact, confidence)
                           ▼
                 CONTROL / OPERATOR ADVICE
        (apply in Twin/sim; recommend to operator
              or player in competition build)
```

This is the canonical pipeline referenced by every other architecture document in this phase. Any component-level document (13–19) should describe *how* its layer implements a stage of this pipeline, not introduce a conflicting flow.

## Layer Responsibilities

| Layer | Responsibility | Detailed in |
|---|---|---|
| Edge-AI Nodes | Local vehicle detection → compact traffic-state metadata | `16_EDGE_AI_ARCHITECTURE.md`, `31_COMPUTER_VISION.md` |
| Traffic Intelligence Hub | Fuse multi-node state into one network view; run short-term prediction | `14_DATA_ARCHITECTURE.md`, `15_AI_ARCHITECTURE.md` |
| Digital Twin | Maintain synchronized virtual copy of the network state (SUMO) | `13_DIGITAL_TWIN_ARCHITECTURE.md`, `19_SIMULATION_ARCHITECTURE.md` |
| Scenario Engine | Generate and simulate candidate interventions | `27_SCENARIO_ENGINE.md` (Phase 3) |
| Optimization | Score and rank candidates on network-wide impact | `35_STRATEGY_OPTIMIZATION.md` (Phase 4) |
| Explainable AI | Produce structured, human-readable justification | `37_EXPLAINABLE_AI.md` (Phase 4) |
| Control / Advice | Apply the chosen action in the Twin/simulation, or present as a game choice | `29_BASELINE_CONTROLLER.md`, `51_GAMEPLAY_LOOP.md` |

## Two Deployment Framings, One Engine

The same pipeline above is exposed in two ways:

1. **Research framing** — a Streamlit/Plotly dashboard for operators/researchers, emphasizing metrics, baselines, and explanation (`55_DASHBOARD_SPECIFICATION.md`).
2. **Competition framing** — a playable web UI where the "Traffic Intelligence Hub → Scenario Engine → Optimization → Explainable AI" stages are surfaced as the `SIMULATE` action and its results (`54_UI_UX_SPECIFICATION.md`).

Both framings call the same backend (FastAPI) and the same underlying SUMO/TraCI Digital Twin — there is one engine, not two separate systems (see `18_...` MASATHON game section in the source ideation notes and `50_GAME_DESIGN.md`).

## Data Flow Summary

```text
Camera / SUMO state
   → Edge metadata (per node)
   → Hub: fused TrafficState (per junction, network-wide)
   → Hub: Prediction (short-term forecast)
   → Twin: synchronized state
   → Scenario Engine: N candidate simulations
   → Optimization: scored candidates
   → Explainable AI: structured recommendation
   → Applied to Twin / shown to operator or player
```

## Non-Functional Concerns Addressed Here

- **Latency**: each stage's contribution to end-to-end decision latency is measured explicitly in `46_LATENCY_ANALYSIS.md`.
- **Explainability**: is a pipeline *stage*, not a UI afterthought — it consumes the Scenario Engine's comparative output directly.
- **Safety/scope**: the "Control" stage in this prototype applies actions only within the Twin/simulation — see `10_SCOPE_AND_NON_SCOPE.md` and `20_SECURITY_ETHICS.md`.

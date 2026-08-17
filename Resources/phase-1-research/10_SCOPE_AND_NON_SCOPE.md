# 10 — Scope and Non-Scope

## Purpose
This document exists to prevent scope explosion during the 8-hour Round 2 build and to give judges a clear, honest boundary of what NexusTwin is (and is not) claiming to be.

## In Scope

### System scope
- A small, representative urban road network: **3–5 junctions**.
- **2–4** simulated/edge camera nodes feeding traffic state.
- **SUMO** as the traffic simulation core, with a real network imported from **OpenStreetMap** where feasible.
- **TraCI** for closed-loop control (retrieving state, injecting actions) between our Python code and SUMO.
- A **Digital Twin** layer that stays synchronized with the (simulated) physical network state.
- A **Scenario Engine** that simulates at least **3–4 candidate interventions** per decision point:
  - Signal timing extension/shortening
  - Route diversion
  - Dynamic lane allocation
  - Emergency corridor priority
- A **deterministic, multi-objective scoring** optimizer (waiting time + queue + spillback + emissions + emergency delay), with **RL as an optional Phase 2 stretch goal**, not a dependency for the core demo.
- **Explainable output** for every recommendation (action, reason, expected impact, confidence).
- **3–5 procedurally generated event types** (from `09_USE_CASES.md`): accident, traffic surge, road closure, weather capacity reduction, emergency vehicle.
- A playable interface implementing the gameplay loop (`51_GAMEPLAY_LOOP.md`) with scoring.
- Baseline comparisons: fixed-time signals and a simple rule-based reactive controller.
- Basic computer-vision perception demo (YOLO on a traffic video or synthetic SUMO-rendered footage) — enough to show the perception pipeline is real, not necessarily fully integrated end-to-end under time pressure.

### Documentation scope
- All six phases of documentation (`docs/phase-1-research` through `docs/phase-6-productization`) as the single source of truth for design decisions.

## Out of Scope (Explicitly, for This Prototype)

- **Controlling real, live traffic signals.** NexusTwin is a simulation/testbed; it does not connect to or control physical city infrastructure.
- **Full city-scale deployment** (e.g., an entire city such as Chennai). We use one small corridor/network.
- **Production-grade autonomous control** without human oversight — the framing is decision-support/explainable recommendation, not unattended automatic control of real infrastructure.
- **Dedicated hardware deployment** (real edge devices, real CCTV integration) — perception is demonstrated via recorded video and/or synthetic data, not a live camera network.
- **Facial recognition or license-plate storage** — see `20_SECURITY_ETHICS.md`; only aggregate vehicle-class counts and traffic-state metadata are used.
- **State-of-the-art model complexity for its own sake** (e.g., simultaneous GNN + LSTM + Transformer + RL) — we deliberately start with simpler models (XGBoost/rule-based) and treat deep forecasting/RL as later, optional phases, per `14_AI_ARCHITECTURE.md` / `33_CONGESTION_PREDICTION.md` / `36_REINFORCEMENT_LEARNING.md`.
- **Claims of being first-to-market or first-in-research** for any individual component (Digital Twin, RL signal control, edge AI) — see `06_RESEARCH_GAP.md` for what is and is not claimed as novel.

## Explicit "Do Not Claim" List (also in `33_STRATEGY...` pitch materials)

- ❌ "First AI traffic Digital Twin."
- ❌ "First system to use RL for traffic."
- ❌ "No existing system can predict congestion."
- ❌ "Our camera is a GPU" (informal analogy only — see `03_IDEATION.md` and `16_EDGE_AI_ARCHITECTURE.md` for correct terminology).
- ❌ "We can directly control real city traffic."

## Escalation Rule

If, during the build, a feature request would require expanding beyond this scope (e.g., "let's add a full city map," "let's add live camera integration"), the team defaults to **no** unless there is spare time after the in-scope checklist (`60_FINAL_CHECKLIST.md`) is fully satisfied.

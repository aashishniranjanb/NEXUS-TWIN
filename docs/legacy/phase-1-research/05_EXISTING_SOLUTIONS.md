# 05 — Existing Solutions

This document compares the categories of traffic-control approaches that already exist, so we know exactly what NexusTwin needs to be measured against (see `43_BASELINE_COMPARISON.md`).

## 1. Fixed-Time Signals
**What it is**: Signal phases follow a pre-programmed cycle regardless of real traffic.
**Strengths**: Simple, predictable, cheap.
**Weaknesses**: No responsiveness to actual demand; performs poorly under variable or surge conditions.
**Role in NexusTwin**: Our primary baseline (Baseline 1).

## 2. Vehicle-Actuated Signals
**What it is**: Local sensors (inductive loops, simple detectors) extend or shorten green time based on presence/absence of vehicles at that junction only.
**Strengths**: Cheap responsiveness improvement over fixed-time.
**Weaknesses**: Still purely local; no network awareness; no prediction.
**Role in NexusTwin**: Referenced as a step up from Baseline 1, not separately implemented unless time allows.

## 3. Adaptive / AI-Driven Signal Control (RL, DL, GNN, fuzzy logic)
**What it is**: Signal timing is adjusted using AI models trained to respond to sensed conditions, sometimes across a small cluster of junctions. This is an extensively researched area (400+ publications reviewed as of 2026).
**Strengths**: Demonstrated waiting-time and queue-length reductions over fixed-time and actuated control.
**Weaknesses**: Predominantly reactive (acts after conditions are sensed) and typically optimizes the observed junction/cluster rather than validating network-wide effect before acting.
**Role in NexusTwin**: Our "reactive adaptive" baseline (Baseline 2) — e.g., a simple rule such as "if queue > threshold, increase green."

## 4. Digital Twin + SUMO + Q-Learning Systems
**What it is**: An IoT-driven Digital Twin built in SUMO, using Q-learning to select signal actions, compared against fixed-time and actuated control (demonstrated in 2026 research).
**Strengths**: Brings simulation fidelity and RL-based decision-making together; reports measurable improvements.
**Weaknesses**: Still framed around single/cluster-junction control optimization rather than explicit cross-network counterfactual comparison before deployment.
**Role in NexusTwin**: Closest prior art to our Digital Twin layer — we must not claim this combination itself is new.

## 5. Edge–Cloud Digital Twin with Forecasting (GNN/LSTM/Transformer + RL)
**What it is**: A 2026 architecture (GEC-DTSP) combining graph/temporal forecasting models with an edge-cloud Digital Twin and deep RL for adaptive signal control, reporting a 17% reduction in average waiting time.
**Strengths**: State-of-the-art forecasting accuracy and demonstrated real gains; strong technical depth.
**Weaknesses**: High model complexity (GNN + LSTM + Transformer + RL simultaneously); heavier to reproduce in a hackathon setting; still framed as control optimization rather than explicit multi-strategy counterfactual comparison with explainability as a first-class output.
**Role in NexusTwin**: We explicitly avoid trying to out-engineer this — our differentiation is architectural (decision validation + explainability), not "more complex models."

## 6. Commercial / Municipal Traffic Platforms
**What it is**: Deployed traffic management platforms (city-operated adaptive signal systems, incident-management dashboards, navigation-app-informed signal timing).
**Strengths**: Real-world deployment experience, live data integration, operational tooling.
**Weaknesses**: Typically closed-source, not focused on transparent counterfactual "what-if" simulation for operators, and not built as an explainable decision-support layer for novel or rare events (accidents, emergencies).
**Role in NexusTwin**: Out of scope to reproduce — referenced only as context ("how is this different from Google Maps / a city traffic control room?" — see `59_JUDGE_QA.md`).

## Comparison Table

| Approach | Reactive/Predictive | Scope | Validates before acting? | Explainable output? |
|---|---|---|---|---|
| Fixed-time | Neither | Single junction | No | No |
| Vehicle-actuated | Reactive | Single junction | No | No |
| AI/RL adaptive signal control | Mostly reactive | Junction / small cluster | No | Rarely |
| DT + SUMO + Q-learning | Reactive/near-real-time | Junction / small network | Implicitly, via RL policy | Rarely |
| Edge-cloud DT + GNN/LSTM/Transformer + RL | Predictive | Network (forecasting-driven) | Implicitly, via learned policy | Rarely |
| **NexusTwin (proposed)** | **Predictive** | **Network** | **Explicitly — simulates candidate strategies before choosing** | **Yes — action, reason, expected impact, confidence** |

This table is the basis for the gap identified in `06_RESEARCH_GAP.md`.

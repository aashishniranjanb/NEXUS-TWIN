# 08 — Objectives and Hypotheses

## Main Research Objective

> To develop and evaluate an edge-AI-enabled Digital Twin framework that predicts urban traffic states, simulates alternative control strategies, and recommends explainable network-level interventions before deployment.

## Secondary Research Questions

1. Can distributed computer vision provide sufficiently useful traffic-state information for decision-making?
2. Can the system predict congestion before severe queue formation, rather than only reacting to it?
3. Can the Digital Twin reproduce the current traffic state with adequate fidelity?
4. Can candidate interventions be evaluated safely and quickly inside the Twin?
5. Can the system select better actions than fixed-time and conventional reactive-adaptive control?
6. Can the recommendation be explained to a human traffic operator in a way that supports trust and oversight?

## Specific Objectives

| ID | Objective |
|---|---|
| O1 | **Perception** — Detect vehicles and estimate traffic states from distributed (simulated/edge) camera nodes. |
| O2 | **State estimation** — Fuse edge observations into a single, unified network state. |
| O3 | **Prediction** — Forecast short-term congestion (e.g., 5–10 minutes ahead). |
| O4 | **Digital Twin** — Maintain a synchronized microscopic traffic simulation (SUMO) of the network. |
| O5 | **Scenario generation** — Generate multiple alternative interventions per decision point. |
| O6 | **Optimization** — Select the best intervention using a multi-objective score across candidates. |
| O7 | **Explainability** — Produce a structured explanation (action, reason, expected impact, confidence) for each recommendation. |
| O8 | **Evaluation** — Compare NexusTwin against fixed-time and reactive-adaptive baselines using measured (not fabricated) metrics. |

## Hypotheses

- **H1** — Scenario-based Digital Twin optimization reduces network-wide traffic delay and queue accumulation compared with fixed-time and reactive-adaptive control.
- **H2** — Predictive intervention selection produces better outcomes than purely reactive control during rapidly changing traffic conditions.
- **H3** — Network-level optimization reduces congestion spillback compared with isolated intersection optimization.
- **H4** — The proposed system maintains useful decision quality under noisy or incomplete edge perception (sensor error, latency, missing detections).

## Traceability

| Hypothesis | Primary Objective(s) it tests | Experiment(s) that will test it |
|---|---|---|
| H1 | O5, O6, O8 | E1 (Fixed vs NexusTwin), E3 (Local vs network optimization) — see `40_EXPERIMENT_PLAN.md` |
| H2 | O3, O8 | E2 (Reactive vs predictive), E4 (Prediction vs no prediction) |
| H3 | O5, O6 | E3 (Local vs network optimization) |
| H4 | O1, O2 | E5 (Sensor noise) — see `45_ROBUSTNESS_TESTING.md` |

These hypotheses must remain falsifiable: if experiments in Phase 5 do not support a hypothesis, `48_LIMITATIONS.md` should say so plainly rather than adjusting the claim after the fact.

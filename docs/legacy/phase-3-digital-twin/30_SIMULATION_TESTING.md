# 30 — Simulation Testing

## Purpose
Verify the simulator itself — network, demand, signals, and baselines — is correct **before** any AI layer (Phase 4) is added on top of it. Debugging AI behavior on top of a broken simulation wastes time and produces meaningless results; this gate exists to prevent that.

## Test Checklist

### Network Sanity (`22_ROAD_NETWORK.md`)
- [ ] Network loads in `sumo-gui` without errors or warnings about disconnected edges.
- [ ] Junction count matches the documented network description (3–5).
- [ ] All intended approaches/lanes are connected with sensible turning movements (no vehicles trapped or unable to reach expected destinations).

### Demand Sanity (`23_TRAFFIC_DEMAND_MODEL.md`)
- [ ] Vehicles spawn at the expected rate and vehicle-class mix.
- [ ] No routing errors (SUMO warnings about unreachable routes / disconnected trips).
- [ ] Rush-hour time-varying profile visibly produces a build-up and decay in the GUI/metrics, not just a flat load.

### Signal Sanity (`24_TRAFFIC_SIGNAL_MODEL.md`)
- [ ] Fixed-time baseline runs a stable, repeating cycle with correct phase durations.
- [ ] Reactive-adaptive baseline visibly extends green phases when queues exceed threshold, and returns to normal cycling when they don't.
- [ ] Yellow/all-red clearance intervals are never skipped or shortened by either baseline.

### State Extraction Sanity (`25_TRAFFIC_STATE_MODEL.md`)
- [ ] `TrafficState` values pulled via TraCI look plausible (e.g., queue lengths increase during rush hour and decrease after; average speed drops as density rises).
- [ ] No `None`/`NaN` values leaking into logged metrics under normal operation.

### Baseline Metrics Sanity (`29_BASELINE_CONTROLLER.md`)
- [ ] Baseline 1 (fixed) and Baseline 2 (reactive) both complete a full run of the UC1 (rush hour) scenario without crashing.
- [ ] Reactive-adaptive shows **at least a plausible directional improvement** over fixed-time on obvious metrics (e.g., lower average waiting time) — if it doesn't, the threshold/increment parameters likely need retuning before Phase 4 begins, since a broken "conventional adaptive" baseline undermines later comparisons.

### Incident Sanity (`28_INCIDENT_ENGINE.md`)
- [ ] Each incident type (`accident`, `closure`, `surge`, `weather`, `emergency`) can be manually triggered and visibly changes simulation behavior (e.g., accident visibly slows/blocks the affected edge).
- [ ] Incidents correctly resolve at their `end_time` (severity effects are not permanently stuck).

## Test Method
- Primarily manual/visual verification via `sumo-gui` for early passes, backed by printed/logged metric checks (via a simple script reading `traffic_state` rows) for repeatable verification.
- Formal automated tests are optional given the time constraints, but the checklist above should be run through explicitly (not skipped) before Phase 4 begins, and again before Phase 5 experiments are trusted.

## Sign-Off
Phase 3 is considered complete, and Phase 4 (AI layer) may begin, only once every item in the checklist above is checked. Record the completion date/person in `CHANGELOG.md` or `DECISIONS.md` at the repository root.

## Dependencies
- Exercises `21_SIMULATION_SETUP.md` through `29_BASELINE_CONTROLLER.md`.
- Gate for Phase 4 (`31_COMPUTER_VISION.md` onward) and a precondition for trustworthy Phase 5 experiments (`40_EXPERIMENT_PLAN.md`).

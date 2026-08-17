# 29 — Baseline Controller

## Purpose
Implement the two comparison baselines that NexusTwin must be measured against (per `05_EXISTING_SOLUTIONS.md` and `43_BASELINE_COMPARISON.md`). Without working baselines, no evaluation in Phase 5 is possible — this document should be completed **before** heavy investment in Phase 4 AI work, per the build-order rule below.

## Build-Order Rule (Important)

> **Prove the simulator and baselines work before building the visual interface.**
> A beautiful Digital Twin without quantitative evidence is just a visualization; a working SUMO + baseline-controller setup with measured metrics is a defensible technical project. Unity/game-UI work (Phase 6) should not begin until Baseline 1 is running end-to-end and producing metrics.

## Baseline 1 — Fixed-Time Controller

- Directly uses the fixed-time phase definitions from `24_TRAFFIC_SIGNAL_MODEL.md`.
- No TraCI intervention needed beyond starting the simulation — SUMO runs the traffic-light program as defined.
- Implementation: a `run_baseline_fixed(scenario)` script that starts SUMO with `control_mode="fixed"`, runs to completion, and logs `TrafficState` snapshots at each step to the `traffic_state` table, tagged with a `simulation_runs` row (`method="fixed"`).

## Baseline 2 — Reactive-Adaptive Controller

- Implements the rule from `24_TRAFFIC_SIGNAL_MODEL.md`:
  ```text
  IF queue_length(current_phase_red_approach) > threshold_m:
      extend current green phase by fixed_increment_s (capped)
  ```
- Implementation: a TraCI-driven loop (`run_baseline_reactive(scenario)`) that, at each check interval, reads queue length via TraCI and conditionally calls `traci.trafficlight.setPhaseDuration(...)`.
- Tagged `method="reactive"` in `simulation_runs`.

## Common Controller Interface

Both baselines (and, later, the NexusTwin controller) should implement the same function signature so the experiment harness (`40_EXPERIMENT_PLAN.md`) can swap between them via a config flag rather than separate code paths:

```python
def run_controller(method: str, scenario: str, run_id: str) -> None:
    """
    method: "fixed" | "reactive" | "nexustwin"
    Starts SUMO for `scenario`, applies the corresponding control
    logic each step, logs TrafficState + final metrics under run_id.
    """
```

The `"nexustwin"` branch of this function is implemented in Phase 4 (`35_STRATEGY_OPTIMIZATION.md`) and calls into the Scenario Engine (`27_SCENARIO_ENGINE.md`) at each decision point instead of a fixed rule.

## Threshold Tuning
- `threshold_m` and `fixed_increment_s` / `max_extension_s` for Baseline 2 should be tuned on the finalized network + baseline demand so that Baseline 2 is a **credible, working** adaptive controller — not a strawman. This matters for the credibility of the H1/H2 comparisons in Phase 5.

## Deliverables
- `experiments/baseline.py` implementing both `run_baseline_fixed` and `run_baseline_reactive`.
- Logged results for both baselines on at least the UC1 (rush hour) scenario, verified in `30_SIMULATION_TESTING.md`, before Phase 4 begins.

## Dependencies
- Requires `22_ROAD_NETWORK.md`, `23_TRAFFIC_DEMAND_MODEL.md`, `24_TRAFFIC_SIGNAL_MODEL.md`.
- Feeds `30_SIMULATION_TESTING.md` (sanity-checking these baselines) and `43_BASELINE_COMPARISON.md` (Phase 5).

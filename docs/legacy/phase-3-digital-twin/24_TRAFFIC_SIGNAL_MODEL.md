# 24 — Traffic Signal Model

## Purpose
Define the traffic light logic at each junction in the network, for three control modes: fixed-time (Baseline 1), reactive-adaptive (Baseline 2), and NexusTwin-controlled (proposed system, applied via the Scenario Engine's chosen strategy).

## Phase Structure (per junction)

A standard 4-approach junction phase cycle:

```text
Phase 1: North-South green   (+ associated yellow/all-red clearance)
Phase 2: East-West green     (+ associated yellow/all-red clearance)
```

For junctions with turning movements requiring protection (e.g., a dedicated left-turn arrow), additional phases are added as needed once the real network (`22_ROAD_NETWORK.md`) is finalized.

## Baseline 1 — Fixed-Time

```text
Phase 1 (N-S green):  30s
Yellow:                3s
All-red clearance:     2s
Phase 2 (E-W green):  30s
Yellow:                3s
All-red clearance:     2s
--------------------------------
Cycle length:         70s (example — tune per junction once network is finalized)
```

- No responsiveness to real-time conditions — this is intentional, it is our control baseline.
- Defined directly in SUMO's traffic light program format, attached to each junction.

## Baseline 2 — Reactive-Adaptive (rule-based)

```text
IF queue_length(current_phase_red_approach) > threshold_m:
    extend current green phase by fixed_increment_s
    (up to a max_extension_s cap)
ELSE:
    proceed to next phase as scheduled
```

- Implemented via TraCI: read queue length each step, conditionally extend the active phase.
- Deliberately simple — this represents "conventional adaptive control," not our proposed system, per `05_EXISTING_SOLUTIONS.md`.

## Proposed — NexusTwin-Controlled

- Signal phase/timing changes are **one of the candidate strategy types** evaluated by the Scenario Engine (`27_SCENARIO_ENGINE.md`), specifically the `green_extend` strategy:
  ```text
  green_extend(junction_id, extension_seconds)
  ```
- Unlike Baseline 2, this candidate is evaluated **inside the Twin** — its predicted network-wide effect is compared against other candidate types (diversion, dynamic lane, emergency priority) before any one of them is applied, per `13_DIGITAL_TWIN_ARCHITECTURE.md`.
- Multiple extension magnitudes can be offered as distinct candidates (e.g., +20s vs +40s), matching the example table in the original ideation notes (`03_IDEATION.md`).

## Signal Definition Storage

- Stored per-junction in `signals` table (`18_DATABASE_SCHEMA.md`) as a JSON-encoded phase definition, and as native SUMO traffic-light-logic XML in `simulation/signals/`.
- `control_mode` field distinguishes which of the three modes above is active for a given `simulation_runs` record — this is what makes baseline comparison (`43_BASELINE_COMPARISON.md`) a matter of switching a config flag, not rebuilding the network.

## Safety Constraints (kept constant across all three modes)

- Yellow and all-red clearance intervals are **never shortened** by any strategy — only green/extension durations are adjustable.
- Maximum single-phase duration is capped (`max_extension_s`) in both Baseline 2 and the NexusTwin `green_extend` candidate, to avoid starving the opposing approach indefinitely.

## Dependencies
- Requires `22_ROAD_NETWORK.md` finalized (junction IDs, approach counts).
- Feeds `25_TRAFFIC_STATE_MODEL.md` (signal_phase field) and `29_BASELINE_CONTROLLER.md` (Baseline 1/2 implementation).

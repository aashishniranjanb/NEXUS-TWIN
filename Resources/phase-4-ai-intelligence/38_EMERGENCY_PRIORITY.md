# 38 — Emergency Priority

## Purpose
Defines special handling for emergency vehicles (ambulance, fire, police) — UC3 in `09_USE_CASES.md` — which serves as one of the strongest demo moments (quantifiable, high-stakes, easy for judges to understand) and directly exercises the `emergency_priority` strategy type from `27_SCENARIO_ENGINE.md`.

## Why Emergency Vehicles Get Special Treatment

Unlike general congestion, emergency response time has a direct safety dimension. NexusTwin encodes this by weighting `predicted_emergency_delay_s` much more heavily in the Optimization scoring function than other terms (`35_STRATEGY_OPTIMIZATION.md`: `emergency: 3.0` default weight vs. `1.0` for delay/queue) — the system should strongly prefer strategies that reduce emergency response time even at some cost to general traffic efficiency.

## Trigger

- An `emergency`-class vehicle is injected into the Reference simulation (`28_INCIDENT_ENGINE.md`), with a defined origin and destination (e.g., "North entry → City Hospital").
- Injection immediately triggers a decision point (per `34_STRATEGY_GENERATION.md`'s event-driven trigger rule) — emergency events are never left for the next scheduled check.

## `emergency_priority` Strategy Behavior

```text
1. Identify the corridor: the sequence of edges/junctions between
   the emergency vehicle's current position and its destination.
2. For each junction along the corridor:
     - Extend/force green in the emergency vehicle's direction
       of travel (overriding normal cycle if needed, within safety
       clearance constraints from 24_TRAFFIC_SIGNAL_MODEL.md)
     - Optionally hold cross-traffic at red slightly longer
3. Set the emergency vehicle's simulated priority/speed factor
   elevated (representing right-of-way behavior)
```

Implemented via TraCI: `traci.vehicle.setSpeedFactor()`, `traci.trafficlight.setPhase()`/`setPhaseDuration()` along the corridor, consistent with the mechanism described in `28_INCIDENT_ENGINE.md`.

## Comparison Candidate Set

When an emergency vehicle is present, the Scenario Engine (`27_SCENARIO_ENGINE.md`) always includes:

```text
1. do_nothing            (baseline — normal signal operation)
2. emergency_priority     (dedicated corridor priority)
3. green_extend           (generic response, not emergency-specific)
```

This lets the system (and the demo) show, quantitatively, that `emergency_priority` outperforms a generic response on `predicted_emergency_delay_s` specifically — reinforcing that the weighting isn't just asserted, it's demonstrated.

## Metrics Specific to This Use Case

```text
predicted_emergency_delay_s   # primary metric — travel time along
                                # the corridor under this candidate
predicted_delay_s              # secondary — general network impact
                                # of granting priority (should be
                                # reported honestly, including any
                                # cost to general traffic)
```

## Safety Constraint

- Yellow/all-red clearance intervals are **never removed**, even under emergency priority — only green duration/timing is adjusted, consistent with the safety constraints in `24_TRAFFIC_SIGNAL_MODEL.md`.

## Demo Usage
This scenario is the recommended centerpiece for the "wow moment" in `56_DEMO_SCRIPT.md` — triggering an emergency mid-run and showing the corridor light up with the AI's prioritized response and the quantified before/after response time.

## Dependencies
- Requires `24_TRAFFIC_SIGNAL_MODEL.md`, `27_SCENARIO_ENGINE.md`, `28_INCIDENT_ENGINE.md`, `34_STRATEGY_GENERATION.md`, `35_STRATEGY_OPTIMIZATION.md`.
- Feeds `56_DEMO_SCRIPT.md` and `40_EXPERIMENT_PLAN.md` (Experiment E7 — Emergency vehicle).

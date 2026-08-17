# 19 — Simulation Architecture

## Purpose
Defines how SUMO, TraCI, and our Python controller fit together — the concrete mechanism underneath the more conceptual `13_DIGITAL_TWIN_ARCHITECTURE.md`.

## Two SUMO Instances

For the prototype, we run **two logical SUMO instances**:

1. **Reference instance** ("physical" stand-in) — advances continuously, represents ground truth for the demo/game session.
2. **Twin instance** — kept synchronized with the reference instance's state; used exclusively for scenario evaluation (clone → simulate candidate → discard).

```text
Reference SUMO instance  ──sync state──▶  Twin SUMO instance
        │                                        │
        │ (advances every demo tick)             │ (cloned per decision point,
        │                                        │  simulated forward per
        ▼                                        │  candidate, then reset/
   Game/dashboard shows                          │  discarded except for the
   this state as "current"                       ▼  chosen strategy)
                                          Scenario Engine reads
                                          back metrics per candidate
```

If time is tight, this can be simplified to a **single SUMO instance with save/load state snapshots** (SUMO supports saving and reloading simulation state) instead of two live processes — this is an acceptable implementation shortcut and should be recorded as a decision in `DECISIONS.md` if taken.

## Control Loop (per decision point)

```text
1. Read current state from Reference instance (via TraCI)
2. Sync Twin instance to match
3. For each candidate strategy:
     a. Snapshot Twin state
     b. Apply candidate action via TraCI (e.g., change phase duration,
        reroute a %, open a lane, prioritize emergency vehicle)
     c. Step simulation forward N ticks
     d. Read back metrics via TraCI (waiting time, queue, throughput,
        emissions estimate, emergency vehicle travel time)
     e. Restore Twin to the pre-candidate snapshot
4. Send collected metrics to Optimization (15_AI_ARCHITECTURE.md /
   35_STRATEGY_OPTIMIZATION.md)
5. Apply the chosen strategy to the Reference instance (not just the Twin)
6. Advance Reference instance; repeat
```

## Key TraCI Operations Used
- Retrieving per-junction/per-lane state: vehicle counts, queue length, waiting time, mean speed.
- Changing traffic light program / phase duration.
- Rerouting a vehicle or a percentage of a route's flow.
- Setting a vehicle's priority/speed factor (used for emergency corridor simulation).
- Stepping the simulation by a fixed number of steps.
- Saving/loading simulation state (if using the single-instance shortcut above).

TraCI is documented as supporting exactly this kind of "retrieve values, manipulate the running simulation" closed-loop use, which is why it was chosen as the control mechanism in `11_TECH_STACK.md`.

## Demand and Network Setup
- Road network: imported from OpenStreetMap for a real, small corridor where feasible (`22_ROAD_NETWORK.md`, Phase 3).
- Demand: synthetic (random trips) for early development, moving to observation-based demand generation for more realistic baseline comparisons (`23_TRAFFIC_DEMAND_MODEL.md`, Phase 3; `41_DATASET_PLAN.md`).

## Performance Considerations
- Prefer `libsumo` over the socket-based TraCI client for speed, if compatible with the rest of the stack — otherwise standard TraCI is fine at this network size (3–5 junctions).
- Candidate simulations should use a short horizon (a few simulated minutes) to keep `/strategy/evaluate` responsive enough for a live demo (see `46_LATENCY_ANALYSIS.md` for target latency budget).

## Testing
- `30_SIMULATION_TESTING.md` (Phase 3) covers verifying the simulator itself (network validity, demand sanity, baseline signal behavior) before any AI layer is added — this ordering is deliberate (see the build-order rule in `03_IDEATION.md` / source ideation notes: "prove AI strategy actually improves traffic" before building the visual interface).

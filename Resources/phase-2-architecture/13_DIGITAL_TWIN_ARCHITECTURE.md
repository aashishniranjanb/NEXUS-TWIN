# 13 — Digital Twin Architecture

## What We Mean by "Digital Twin" (Definition)

> A continuously updated virtual representation of the road network whose traffic state, demand, signals, and incidents correspond to the modeled physical/simulated system, and which can be used to test alternative control actions before they are applied.

**Important framing decision** (carried from `03_IDEATION.md`): the Digital Twin in NexusTwin is **not primarily a 3D visualization**. It is the **decision-validation engine** — the component that lets us ask "what happens if we do X?" before doing X. Visualization (SUMO-GUI, dashboard maps) is a secondary, optional layer on top of this engine.

## Synchronization Loop

```text
Physical / observed / simulated state
              │
              ▼
        State estimator
      (fuse edge metadata into
       one TrafficState per junction)
              │
              ▼
          Twin state
   (SUMO simulation state, updated
    to match the estimated state)
              │
              ▼
   Difference / drift check
   (is Twin state still close
     enough to observed state?)
              │
              ▼
        Update Twin
   (re-inject vehicles/queues/
    signal states as needed)
```

In the prototype, "physical state" is itself SUMO-simulated (see `10_SCOPE_AND_NON_SCOPE.md`), so synchronization is largely about keeping a **primary SUMO instance** (representing "reality") and a **secondary/cloned SUMO instance** (the Twin used for scenario testing) consistent before each round of candidate simulation.

## Twin Content Layers

### Static layer (rarely changes)
- Road topology
- Lanes
- Junctions
- Traffic light definitions
- Speed limits
- Turning connections

### Dynamic layer (updated continuously)
- Vehicle positions
- Vehicle counts
- Speeds
- Queue lengths
- Signal states
- Traffic density
- Active incidents
- Traffic demand

### Decision layer (what the Twin is used to test)
- Signal timing changes
- Route diversion
- Dynamic lane allocation
- Emergency vehicle priority
- Incident response actions

## How the Twin Is Used by the Scenario Engine

For each decision point:

1. Snapshot the current Twin state.
2. For each candidate strategy (A, B, C, D…): clone the Twin state, apply the candidate action, run the simulation forward a fixed horizon (e.g., a few simulated minutes), and record metrics (delay, queue, throughput, emissions, emergency time).
3. Discard the cloned/simulated branches — they do not affect the "real" Twin state.
4. Pass the collected metrics to Optimization (`35_STRATEGY_OPTIMIZATION.md`) to select the best candidate.
5. Only the **chosen** candidate is actually applied to advance the Twin (and, in the demo, the "physical" simulation) forward.

This clone-simulate-discard-apply pattern is the technical core of Contribution 3 in `07_NOVELTY_AND_CONTRIBUTIONS.md`.

## Relationship to SUMO/TraCI

- The Twin is implemented as a SUMO simulation instance controlled via TraCI (or `libsumo` for performance).
- TraCI's ability to retrieve live simulation values and inject changes into a running simulation is exactly what enables the snapshot → simulate → discard/apply loop above.
- See `19_SIMULATION_ARCHITECTURE.md` for the concrete TraCI call sequence and `26_DIGITAL_TWIN_SYNC.md` (Phase 3) for the implementation-level synchronization logic.

## Explicit Boundaries

- The Twin in this prototype does **not** control real infrastructure (`10_SCOPE_AND_NON_SCOPE.md`).
- The Twin's "physical" reference state is itself a SUMO simulation in the prototype, not live sensor data — this is stated plainly in `48_LIMITATIONS.md` rather than implied.

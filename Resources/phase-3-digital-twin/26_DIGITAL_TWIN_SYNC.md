# 26 — Digital Twin Synchronization

## Purpose
Implementation-level detail for the synchronization loop conceptually described in `13_DIGITAL_TWIN_ARCHITECTURE.md`, using the `TrafficState`/`NetworkState` schema from `25_TRAFFIC_STATE_MODEL.md`.

## Synchronization Sequence

```text
1. Collect latest Per-Node Traffic Metadata from all Edge-AI Nodes
   (or, in prototype mode, read directly from the Reference SUMO
   instance via TraCI — see note below)
        │
        ▼
2. State Estimator fuses node metadata into a NetworkState
   (one TrafficState per junction)
        │
        ▼
3. Compare fused NetworkState against the Twin's current internal
   state (drift check)
        │
        ▼
4. If drift exceeds a small tolerance: update the Twin instance
   (re-inject vehicle counts/queues, correct signal phase if needed)
   via TraCI calls on the Twin's SUMO process
        │
        ▼
5. Twin is now considered synchronized; safe to snapshot for
   scenario evaluation (27_SCENARIO_ENGINE.md)
```

## Prototype Mode vs. "Real" Mode

Because the prototype's "physical" reference is itself a SUMO simulation (`10_SCOPE_AND_NON_SCOPE.md`), two operating modes are supported by the same interface:

| Mode | Source of "observed" state |
|---|---|
| **Direct mode** (fastest to build) | Read state directly from the Reference SUMO instance via TraCI — skips the Edge-AI metadata step entirely. Used for early Phase 3 development and as a fallback if the CV pipeline (Phase 4) isn't ready in time. |
| **Perception mode** (fuller architecture) | Read state from simulated Edge-AI Node metadata (derived from YOLO on video, or from a "fake node" process reading SUMO's own per-edge state and packaging it as if it came from a camera) — exercises the full pipeline in `12_SYSTEM_ARCHITECTURE.md`. |

Both modes should produce a `NetworkState` of the same shape, so the rest of the system (Twin, Scenario Engine, Optimization) is unaffected by which mode is active. This lets the team build and demo end-to-end in Direct mode first, then layer in Perception mode without touching downstream code.

## Drift Tolerance

- A small tolerance (e.g., ±1–2 vehicles per queue, ±5% density) avoids re-injecting state every single tick unnecessarily.
- If using the single-SUMO-instance-with-snapshot approach (noted as an acceptable shortcut in `19_SIMULATION_ARCHITECTURE.md`), synchronization simplifies to "take a fresh state snapshot before each scenario evaluation round" — drift is not a concern because Twin and Reference are the same instance at that moment.

## Two-Instance Implementation Detail (if used)

```python
def sync_twin(reference_state: NetworkState, twin_conn):
    for junction_state in reference_state.junctions:
        twin_conn.trafficlight.setPhase(
            junction_state.junction_id, junction_state.signal_phase
        )
        # Re-inject vehicles / adjust counts on twin edges to match
        # reference queue lengths, if drift exceeds tolerance
        ...
```

## Failure Handling

- If a node/edge is missing from the latest metadata batch (`08_INCIDENT...`/`45_ROBUSTNESS_TESTING.md` sensor-failure scenario), the State Estimator should **hold the last known value** rather than zero it out, and flag `incident_state` or a data-quality flag accordingly — this is what H4 ("useful decision quality under noisy or incomplete perception") is actually testing.

## Dependencies
- Requires `25_TRAFFIC_STATE_MODEL.md` schema.
- Feeds directly into `27_SCENARIO_ENGINE.md` (every scenario evaluation round starts from a synchronized Twin state).

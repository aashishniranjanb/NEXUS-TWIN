# 16 — Edge-AI Architecture

## Terminology (Correcting the Original Analogy)
The original working analogy — "cameras = GPU, central hub = CPU" — is useful for a first, informal explanation of *why* local processing matters, but it is **not used in technical documentation**. The correct terms, used consistently from here on:

- **Edge-AI Traffic Node** — the camera + local inference unit (replaces "GPU").
- **Traffic Intelligence Hub** — the central fusion/prediction/decision system (replaces plain "CPU"/"server").

See `03_IDEATION.md` for why this renaming happened.

## Per-Node Pipeline

```text
Camera (or SUMO-rendered video feed)
        │
        ▼
YOLO (local inference)
        │
        ▼
Vehicle Detection + Classification
        │
        ▼
Local aggregation
  (counting, simple tracking,
   queue/speed estimation)
        │
        ▼
Compact Traffic Metadata
        │
        ▼
Central Traffic Intelligence Hub
```

## Why Process at the Edge

- Only **metadata** (a few dozen numbers) needs to reach the central system per node per update — not raw video.
- This reduces bandwidth and central compute load, and is consistent with feasibility shown in recent edge-deployable detection research (YOLO-Lite style models for edge computing scenarios — `04_RESEARCH_LITERATURE.md` ref 6).
- It also maps cleanly onto Contribution 1 (`07_NOVELTY_AND_CONTRIBUTIONS.md`): distributed perception feeding a decision-validation pipeline.

## Example Node Output

```text
Node 07

Cars:       84
Buses:       8
Trucks:      12
Motorcycles: 31

Density:     82%
Average speed: 17 km/h
Queue:       420 m
Incident:    None
```

This maps directly onto the "Per-Node Traffic Metadata" object defined in `14_DATA_ARCHITECTURE.md`.

## Prototype Implementation Note
For the hackathon build, "edge" nodes are simulated in software (a Python process per node reading from a video file or from SUMO's own per-junction state) rather than deployed on physical edge hardware — this is stated explicitly in `10_SCOPE_AND_NON_SCOPE.md` and `48_LIMITATIONS.md`. The architecture is designed so that swapping in real edge hardware later would not require changing the Hub-side interface (same metadata schema, same MQTT topic structure).

## Failure Modes Considered Here (feeding into Robustness testing)
- Node offline / no data.
- Delayed message (latency).
- Miscount (occlusion, poor lighting).
- Partial detection (e.g., motorcycles undercounted).

These are deliberately injectable in the experiment harness — see `45_ROBUSTNESS_TESTING.md` — to test H4 ("the system maintains useful decision quality under noisy or incomplete edge perception").

## Interface Contract with the Hub
- **Transport**: MQTT, one topic per node (e.g., `nexustwin/node/{node_id}/state`).
- **Payload**: the Per-Node Traffic Metadata JSON object from `14_DATA_ARCHITECTURE.md`.
- **Frequency**: configurable; default assumption is a short fixed interval (e.g., every 1–2 simulated seconds) appropriate to the SUMO step size used in `21_SIMULATION_SETUP.md`.

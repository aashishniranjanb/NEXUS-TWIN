# 31 — Computer Vision

## Purpose
Implements the perception layer (Contribution 1, `07_NOVELTY_AND_CONTRIBUTIONS.md`; architecture in `16_EDGE_AI_ARCHITECTURE.md`): converting raw traffic video into the Per-Node Traffic Metadata object defined in `14_DATA_ARCHITECTURE.md`.

## Pipeline

```text
Video (traffic footage or SUMO-rendered feed)
        │
        ▼
YOLO (pretrained object detection)
        │
        ▼
Detection: bounding boxes + class per frame
        │
        ▼
Tracking (simple frame-to-frame association)
        │
        ▼
Counting (per class, per time window)
        │
        ▼
Speed estimation (from tracked displacement
                   across frames, calibrated
                   to real-world distance)
        │
        ▼
Queue estimation (stationary/slow-moving
                   vehicles near the stop line)
        │
        ▼
Per-Node Traffic Metadata (14_DATA_ARCHITECTURE.md)
```

## Model Choice

- **YOLO** (pretrained, e.g., YOLOv8n or a YOLO-Lite variant) — no training from scratch required for the prototype; pretrained COCO-class weights already detect `car`, `bus`, `truck`, `motorcycle` classes well enough for a demo.
- Edge-deployable variants (YOLO-Lite style) are specifically validated in recent research for this kind of edge vehicle-detection use case (`04_RESEARCH_LITERATURE.md`, reference 6), supporting the feasibility claim even though the prototype runs it on a laptop, not real edge hardware.

## Tracking & Counting

- Simple centroid-tracking or a lightweight tracker (e.g., built into `ultralytics`' YOLO tracking mode) is sufficient — full multi-object tracking (DeepSORT-level complexity) is not required for the prototype's needs.
- Counting is windowed (e.g., per simulated minute) rather than per-frame, matching the update frequency assumed in `16_EDGE_AI_ARCHITECTURE.md`.

## Speed Estimation

- Approximate: track a vehicle's pixel displacement across N frames, convert using a calibration factor (pixels-per-meter) estimated from known road width/lane markings in the source footage.
- Acceptable to be approximate for the prototype — precision is not the differentiator; the pipeline existing and feeding the rest of the system is.

## Queue Estimation

- Vehicles below a speed threshold and within a defined "queue zone" near the stop line are counted as queued; queue length is estimated as `queued_vehicle_count × average_vehicle_length` (+ gaps), or via pixel-distance from the stop line to the last queued vehicle if the camera angle allows.

## Two Integration Modes (matches `26_DIGITAL_TWIN_SYNC.md`)

| Mode | Video source | Use |
|---|---|---|
| **Perception mode** | Real traffic video (public footage, or footage the team records) | Demonstrates the actual CV pipeline is real, not simulated |
| **Direct/SUMO-state mode** | N/A — bypasses CV, reads SUMO ground truth directly | Fallback / used for most of Phase 3 development and experiments where CV noise isn't the variable under test |

**Recommendation**: build and demo Perception mode on a **short, fixed video clip** (not live camera feed) to keep the demo deterministic and reliable — live camera dependency is a needless risk during a timed presentation.

## Output Validation

- Compare YOLO-derived counts against a manual ground-truth count on a short clip sample, to report an approximate accuracy figure (used honestly in `48_LIMITATIONS.md`, not oversold).

## Dependencies
- Feeds `14_DATA_ARCHITECTURE.md`'s Per-Node Traffic Metadata → `26_DIGITAL_TWIN_SYNC.md`'s State Estimator.
- Feeds `45_ROBUSTNESS_TESTING.md` — CV output is the natural place to inject simulated sensor noise/occlusion/miscounts for the robustness experiments (H4).

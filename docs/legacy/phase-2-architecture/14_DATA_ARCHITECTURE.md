# 14 — Data Architecture

## End-to-End Data Flow

```text
Camera / video (or SUMO-rendered feed)
        │
        ▼
Vehicle Detection (YOLO, at Edge-AI Node)
        │
        ▼
Per-node Traffic State (compact metadata)
        │
        ▼
Message (MQTT) — node → hub
        │
        ▼
Central Hub: State Fusion
        │
        ▼
Unified Network TrafficState
        │
        ▼
Digital Twin (state injected/synchronized)
        │
        ▼
Prediction (short-term forecast, per junction)
        │
        ▼
Scenario Engine (candidate simulations)
        │
        ▼
Decision (chosen strategy + explanation)
        │
        ▼
Results Store (for dashboard + experiments)
```

## Canonical Data Objects

### Per-Node Traffic Metadata (Edge → Hub)
```text
node_id
timestamp
cars
buses
trucks
motorcycles
density            # 0-100%
avg_speed_kmh
queue_length_m
incident_flag
```

### Unified TrafficState (Hub / Twin, per junction)
```text
junction_id
timestamp
north_queue_m
south_queue_m
east_queue_m
west_queue_m
average_speed_kmh
vehicle_count
density
waiting_time_s
throughput_veh_per_min
signal_phase
incident_state
```
(Matches the canonical model defined formally in `25_TRAFFIC_STATE_MODEL.md`, Phase 3 — this document defines the *flow*, that document defines the *schema in code*.)

### Prediction Output
```text
junction_id
horizon_minutes      # e.g., 5, 10
predicted_density
predicted_queue_m
confidence
```

### Scenario Result (per candidate, per decision point)
```text
strategy_id
strategy_type         # e.g., green_extend, diversion, dynamic_lane, emergency_priority
predicted_delay_s
predicted_queue_m
predicted_throughput
predicted_emissions
predicted_emergency_delay_s
score                 # from Optimization
```

### Decision / Recommendation
```text
decision_id
timestamp
chosen_strategy_id
reason_text
expected_impact       # structured, from Scenario Result
confidence
applied                # bool — was it actually applied (Twin/sim) or only recommended
```

## Transport Choices

- **Edge → Hub**: MQTT (lightweight pub/sub, standard for many small, frequent messages from distributed nodes).
- **Hub → Twin/Backend**: in-process Python calls / FastAPI internal calls (no need for a second message bus at this scale).
- **Backend → Dashboard/Game UI**: REST (FastAPI) for request/response; WebSocket only if live-updating UI is needed and time allows.

## Storage

- **Live/working state**: in-memory within the backend process (fast; matches the short session length of a demo/game run).
- **Persisted results**: SQLite tables mirroring the `results/` experiment outputs and `18_DATABASE_SCHEMA.md` schema, for post-hoc analysis (`47_RESULTS_ANALYSIS.md`) and reproducibility (`49_REPRODUCIBILITY.md`).

## Data Volume / Privacy Note
Only aggregate, non-identifying traffic metadata is transported and stored — no raw video, no license plates, no facial data leave the Edge-AI Node. See `20_SECURITY_ETHICS.md` for the full policy this constrains.

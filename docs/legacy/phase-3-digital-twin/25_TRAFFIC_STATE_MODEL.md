# 25 — Traffic State Model

## Purpose
This is the **canonical, code-level schema** for `TrafficState` — the object referenced conceptually in `14_DATA_ARCHITECTURE.md` and stored per `18_DATABASE_SCHEMA.md`. Every component (perception, prediction, Twin, Scenario Engine, dashboard) should read/write this exact shape so the pipeline stays consistent end-to-end.

## `TrafficState` (per junction, per timestamp)

```python
class TrafficState:
    junction_id: str
    timestamp: float            # simulation time (seconds) or wall-clock ISO

    # Queues, per approach
    north_queue_m: float
    south_queue_m: float
    east_queue_m: float
    west_queue_m: float

    # Aggregate
    average_speed_kmh: float
    vehicle_count: int
    density: float               # 0-100, % of jam density
    waiting_time_s: float        # avg per-vehicle waiting time at this junction
    throughput_veh_per_min: float

    # Signal
    signal_phase: str
    control_mode: str            # "fixed" | "reactive" | "nexustwin"

    # Incident
    incident_state: str | None   # None | "accident" | "closure" | "surge" | "weather" | "emergency"
```

## `NetworkState` (whole-network snapshot)

```python
class NetworkState:
    timestamp: float
    junctions: list[TrafficState]

    def total_queue_m(self) -> float: ...
    def total_delay_s(self) -> float: ...
    def worst_junction(self) -> TrafficState: ...
```

`NetworkState` is what the Digital Twin snapshots and clones for scenario evaluation (`13_DIGITAL_TWIN_ARCHITECTURE.md`), and what `/traffic/state` returns (`17_API_SPECIFICATION.md`).

## Derived / Computed Fields

| Field | Derivation |
|---|---|
| `density` | `vehicle_count / junction_jam_capacity * 100` |
| `waiting_time_s` | Mean of per-vehicle accumulated waiting time at the junction (TraCI provides this natively) |
| `throughput_veh_per_min` | Count of vehicles that cleared the junction in the last minute of sim time |
| `total_queue_m` (network) | Sum of all `*_queue_m` fields across all junctions |
| `total_delay_s` (network) | Sum of `waiting_time_s` across all junctions, weighted by vehicle_count if needed |

## Mapping to TraCI

| `TrafficState` field | TraCI source |
|---|---|
| `*_queue_m` | `traci.lane.getLastStepHaltingNumber()` × avg vehicle length, or `getLastStepLength()`, per approach lane |
| `average_speed_kmh` | `traci.edge.getLastStepMeanSpeed()`, converted from m/s |
| `vehicle_count` | `traci.edge.getLastStepVehicleNumber()` |
| `waiting_time_s` | `traci.edge.getWaitingTime()` or per-vehicle `getAccumulatedWaitingTime()` |
| `signal_phase` | `traci.trafficlight.getPhase()` |

## Mapping to Edge-AI Metadata (Perception → State)

The Per-Node Traffic Metadata object (`14_DATA_ARCHITECTURE.md`) is fused into `TrafficState` fields as follows:

```text
node.cars + node.buses + node.trucks + node.motorcycles → vehicle_count
node.density                                             → density
node.avg_speed_kmh                                       → average_speed_kmh
node.queue_length_m                                      → (assigned to the relevant approach queue)
node.incident_flag                                       → incident_state (if raised)
```

Multiple nodes covering the same junction from different approaches are fused by assigning each node's queue/speed to its specific approach, and averaging/summing as appropriate — implemented in `26_DIGITAL_TWIN_SYNC.md`'s state estimator.

## Versioning Note
If fields are added/changed during implementation (e.g., adding `emissions_estimate`), update this document **and** `14_DATA_ARCHITECTURE.md` and `18_DATABASE_SCHEMA.md` together — this file is the source of truth for the shape, the other two describe its role in flow and storage respectively.

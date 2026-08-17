# 18 — Database Schema

## Purpose
Defines the persisted (SQLite, per `11_TECH_STACK.md`) tables used for storing results, supporting the dashboard, and enabling reproducible experiments (`49_REPRODUCIBILITY.md`). Live/in-flight state during a session lives in memory (see `14_DATA_ARCHITECTURE.md`) — these tables are the durable record.

## Tables

### `camera_nodes`
| Column | Type | Notes |
|---|---|---|
| node_id | TEXT PK | e.g., "node_07" |
| junction_id | TEXT | FK → junctions.junction_id |
| label | TEXT | human-readable name |

### `junctions`
| Column | Type | Notes |
|---|---|---|
| junction_id | TEXT PK | |
| name | TEXT | |
| lat | REAL | optional, if OSM-derived |
| lon | REAL | optional |

### `traffic_state`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | |
| junction_id | TEXT | FK → junctions |
| timestamp | TEXT | ISO timestamp / sim time |
| queue_north_m | REAL | |
| queue_south_m | REAL | |
| queue_east_m | REAL | |
| queue_west_m | REAL | |
| avg_speed_kmh | REAL | |
| vehicle_count | INTEGER | |
| density | REAL | 0–100% |
| waiting_time_s | REAL | |
| throughput | REAL | veh/min |
| signal_phase | TEXT | |
| incident_state | TEXT | nullable |

### `vehicles` (optional, for detailed logging / CV validation only)
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | |
| node_id | TEXT | FK → camera_nodes |
| timestamp | TEXT | |
| vehicle_class | TEXT | car/bus/truck/motorcycle |
| speed_kmh | REAL | nullable |

### `signals`
| Column | Type | Notes |
|---|---|---|
| junction_id | TEXT PK, FK → junctions | |
| phase_definition | TEXT | JSON-encoded phase/timing plan |
| control_mode | TEXT | fixed / reactive / nexustwin |

### `incidents`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | |
| incident_type | TEXT | accident/closure/surge/weather/emergency |
| junction_id | TEXT | FK → junctions, nullable if network-wide |
| severity | TEXT | low/medium/high |
| start_time | TEXT | |
| end_time | TEXT | nullable |

### `simulation_runs`
| Column | Type | Notes |
|---|---|---|
| run_id | TEXT PK | UUID |
| method | TEXT | fixed / reactive / nexustwin |
| scenario | TEXT | e.g., "rush_hour", "accident" |
| started_at | TEXT | |
| finished_at | TEXT | nullable |
| notes | TEXT | nullable |

### `strategies`
| Column | Type | Notes |
|---|---|---|
| strategy_id | TEXT PK | UUID |
| run_id | TEXT | FK → simulation_runs |
| strategy_type | TEXT | green_extend/diversion/dynamic_lane/emergency_priority |
| params | TEXT | JSON-encoded (e.g., seconds extended) |

### `results`
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK AUTOINCREMENT | |
| run_id | TEXT | FK → simulation_runs |
| strategy_id | TEXT | FK → strategies, nullable (null = baseline/no-strategy record) |
| predicted_delay_s | REAL | |
| predicted_queue_m | REAL | |
| predicted_throughput | REAL | |
| predicted_emissions | REAL | |
| predicted_emergency_delay_s | REAL | |
| score | REAL | nullable — only set for evaluated candidates |
| applied | INTEGER | boolean 0/1 |
| reason_text | TEXT | nullable, set for applied decisions |
| confidence | REAL | nullable |

## Entity Relationships (Summary)

```text
junctions ──< camera_nodes
junctions ──< traffic_state
junctions ──< signals (1:1)
junctions ──< incidents
simulation_runs ──< strategies ──< results
simulation_runs ──< results (baseline rows, strategy_id NULL)
camera_nodes ──< vehicles (optional detail table)
```

## Usage Mapping
- `traffic_state` rows back the dashboard time series and the `43_BASELINE_COMPARISON.md` tables.
- `simulation_runs` + `strategies` + `results` together back `40_EXPERIMENT_PLAN.md` and `47_RESULTS_ANALYSIS.md` — every experiment (fixed vs reactive vs NexusTwin, ablations, robustness runs) is just a differently-tagged `simulation_runs` row.
- `incidents` rows back both real-world use cases (`09_USE_CASES.md`) and the procedural event generator (`53_PROCEDURAL_EVENTS.md`).

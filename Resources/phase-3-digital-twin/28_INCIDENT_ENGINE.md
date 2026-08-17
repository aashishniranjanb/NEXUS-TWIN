# 28 — Incident Engine

## Purpose
Procedurally generate disruptive events into the Reference simulation, both to exercise the real-world use cases in `09_USE_CASES.md` and to drive the game's replayability requirement (`53_PROCEDURAL_EVENTS.md`), satisfying the **Generative AI & Intelligent Game Systems** track relevance.

## Incident Types

| Type | Effect on simulation | Typical trigger |
|---|---|---|
| `accident` | Localized capacity reduction on one edge (reduced lanes/speed) for a duration | Random or scripted, mid-run |
| `closure` | Full edge disable for a duration | Random or scripted |
| `surge` | Localized demand spike (extra vehicles injected near one junction) | Random, or scheduled (e.g., festival/stadium egress) |
| `weather` | Network-wide speed/capacity reduction (e.g., -20% speed) for a duration | Random or scripted |
| `emergency` | A single `emergency`-class vehicle injected with a target corridor | Random or scripted, low frequency |

## Incident Object

Matches the `incidents` table in `18_DATABASE_SCHEMA.md`:

```text
incident_type   # accident | closure | surge | weather | emergency
junction_id     # nullable if network-wide (e.g., weather)
severity        # low | medium | high
start_time
end_time        # nullable while active
```

## Injection Mechanism (TraCI)

```text
accident/closure:  traci.edge.setDisallowed() or reduce
                    traci.lane.setMaxSpeed() on affected edge(s)
                    for [start_time, end_time]

surge:             traci.vehicle.add() calls injecting extra
                    vehicles with routes converging on the
                    target junction, over a short window

weather:           traci.edge.setMaxSpeed() applied network-wide,
                    scaled by severity

emergency:         traci.vehicle.add() with vClass="emergency",
                    traci.vehicle.setRoute() to the target corridor,
                    traci.vehicle.setSpeedFactor() elevated
```

## Severity Levels

| Severity | Effect multiplier (example) |
|---|---|
| low | ~15–25% capacity/speed reduction, or small surge |
| medium | ~35–50% reduction, or moderate surge |
| high | ~60–80% reduction / full closure, or large surge |

Exact multipliers should be tuned once the network (`22_ROAD_NETWORK.md`) and baseline demand (`23_TRAFFIC_DEMAND_MODEL.md`) are finalized, so effects are visible but not degenerate (e.g., not reducing capacity to exactly zero in a way that breaks routing).

## Procedural Generation Logic (Game Mode)

For the competition build, incidents are drawn probabilistically per level (see `52_LEVEL_DESIGN.md`), e.g.:

```text
Level 1 (Normal traffic):    0 incidents
Level 2 (Rush hour):         0-1 incident, low-medium severity
Level 3 (Accident):          1 guaranteed accident, medium-high
Level 4 (Emergency):         1 guaranteed emergency vehicle
Level 5 (Festival):          1 guaranteed surge, medium-high
Level 6 (Flood):             1 guaranteed weather event, high
Level 7 (Sensor failure):    0-1 incident + a perception fault
                              (see 45_ROBUSTNESS_TESTING.md)
```

Random combinations (e.g., an accident *and* an emergency vehicle in the same run) are allowed at higher levels for replayability, per the original design notes ("every run can be different").

## API Surface
Implements the backend logic behind `POST /incident/trigger` (`17_API_SPECIFICATION.md`), callable both by the procedural generator and manually (for controlled demo timing — see `56_DEMO_SCRIPT.md`, where the accident is deliberately triggered at a specific moment for the "wow moment").

## Dependencies
- Requires `22_ROAD_NETWORK.md` and `23_TRAFFIC_DEMAND_MODEL.md`.
- Consumed by `27_SCENARIO_ENGINE.md` (candidates are often generated *in response to* an active incident) and `53_PROCEDURAL_EVENTS.md` (Phase 6).

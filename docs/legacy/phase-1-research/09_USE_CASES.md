# 09 — Use Cases

NexusTwin has two parallel sets of use cases: the **real-world research framing** (what the system is meant to eventually support) and the **game framing** (what the MASATHON prototype actually plays as). Both draw on the same underlying scenario types.

## Real-World Use Cases

### UC1 — Morning/Evening Rush Hour
Recurring, predictable congestion buildup across multiple junctions. Tests baseline prediction and network-level optimization (H1, H2).

### UC2 — Accident
A sudden, localized capacity reduction. Tests responsiveness and the value of simulating diversion vs. signal-timing responses before acting.

### UC3 — Emergency Vehicle Priority
An ambulance/fire/police vehicle needs a fast corridor. Tests the emergency-priority strategy and its explicit weighting in the optimization score (see `38_EMERGENCY_PRIORITY.md`).

### UC4 — Road Closure
Planned or unplanned closure of a road segment, requiring rerouting evaluation across the network rather than just the closed segment.

### UC5 — Festival / Event Crowd
A localized demand surge near a venue, combined with pedestrian/vehicle interaction — tests network-level spillback protection (H3).

### UC6 — Flood / Weather Event
Reduced road capacity across a wider area — tests whether the system degrades sensibly under widespread, not just localized, disruption.

### UC7 — Stadium Event Egress
A sudden, large, short-duration demand spike concentrated around one area — similar to UC5 but with a sharper time profile.

### UC8 — Sensor Failure / Degraded Perception
One or more edge nodes report missing, delayed, or incorrect data. Tests robustness (H4) — see `45_ROBUSTNESS_TESTING.md`.

## Game (Competition) Use Cases

The same eight scenario types above are wrapped as **procedurally generated events** in the playable prototype (see `53_PROCEDURAL_EVENTS.md`), structured through:

- **Level progression** — scenarios increase in complexity across levels (see `52_LEVEL_DESIGN.md`): Normal traffic → Rush hour → Accident → Emergency → Festival → Flood → Sensor failure.
- **Random event injection** — within a level, one or more of UC1–UC8 can fire unpredictably, so no two playthroughs are identical.
- **Player decision loop** (see `51_GAMEPLAY_LOOP.md`):
  1. Observe current traffic state.
  2. See the short-term forecast.
  3. Investigate the triggered event (if any).
  4. Press **SIMULATE** to have the Twin evaluate candidate strategies.
  5. Review each strategy's expected impact (waiting time, queue, emissions, emergency delay).
  6. Choose a strategy (or accept the AI's top recommendation).
  7. See the city state update and the resulting score.
  8. Move to the next event.
- **Scoring** across traffic efficiency, network health, sustainability, emergency response, safety, and cost of interventions used (see `55_DASHBOARD_SPECIFICATION.md` and `51_GAMEPLAY_LOOP.md`).

## Mapping Table

| Use case | Primary track relevance | Primary metric stressed |
|---|---|---|
| UC1 Rush hour | Generative AI & Intelligent Game Systems | Delay, throughput |
| UC2 Accident | Computer Vision & Perception, Explainable AI | Decision latency, explanation quality |
| UC3 Emergency vehicle | Responsible & Explainable AI | Emergency response time |
| UC4 Road closure | Generative AI & Intelligent Game Systems | Network-level delay vs local delay |
| UC5 Festival crowd | Narrative/Social Impact | Spillback events |
| UC6 Flood/weather | Generative AI & Intelligent Game Systems | Robustness under wide disruption |
| UC7 Stadium egress | Games for Learning & Skill Development | Throughput under demand spike |
| UC8 Sensor failure | Computer Vision & Perception, Explainable AI | Decision quality under noise (H4) |

# GAME_STATE_MACHINE.md — Game State Machine Specification

**Status**: [IMPLEMENTED] Python Engine Logic / [PLANNED] Unity State Machine  
**Last Updated**: 2026-08-23

---

## 1. State Diagram

```text
[IDLE] ──► [EVENT] ──► [ANALYSIS] ──► [DECISION] ──► [SIMULATION] ──► [RESULT] ──► [SCORE] ──► [IDLE]
```

---

## 2. State Definitions

| State | Entry Condition | Valid Transitions | API Call | Timeout |
| :--- | :--- | :--- | :--- | :--- |
| `IDLE` | Game session started | `EVENT` | `GET /api/state` | N/A |
| `EVENT` | Queue > threshold or Emergency | `ANALYSIS` | `GET /api/game/event` | N/A |
| `ANALYSIS` | Event spawned | `DECISION` | `GET /api/traffic/prediction` | 10s |
| `DECISION` | AI recommendation ready | `SIMULATION` | `POST /api/game/move` | 30s |
| `SIMULATION` | Player move submitted | `RESULT` | `POST /api/evaluate` | 15s |
| `RESULT` | Horizon evaluation done | `SCORE` | None | 5s |
| `SCORE` | Result acknowledged | `IDLE`, `NEXT_EVENT` | `POST /api/game/end` | N/A |

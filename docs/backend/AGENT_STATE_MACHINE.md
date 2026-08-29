# Multi-Agent State Machine Flow

```
                     [ Incoming Crisis Event ]
                                │
                                ▼
                   ┌──────────────────────────┐
                   │ Traffic Intelligence Node │
                   └────────────┬─────────────┘
                                │ State + Fingerprint
                                ▼
                   ┌──────────────────────────┐
                   │ Network Intelligence Node│
                   └────────────┬─────────────┘
                                │ Spillover + Domino
                                ▼
                   ┌──────────────────────────┐
                   │ Strategy Generation Node │
                   └────────────┬─────────────┘
                                │ Candidate Strategies
                                ▼
                   ┌──────────────────────────┐
                   │Simulation Evaluation Node│
                   └────────────┬─────────────┘
                                │ 900s Simulation Deltas
                                ▼
                   ┌──────────────────────────┐
                   │   Safety Critic Node     │
                   └────────────┬─────────────┘
                                │ Audit & Explainability
                                ▼
                   ┌──────────────────────────┐
                   │ Human Decision Copilot   │
                   │    (Approve / Override)  │
                   └──────────────────────────┘
```

# GAMEPLAY_SYSTEM.md — Gameplay Loop & Player Mechanics

**Status**: [IMPLEMENTED] Python Core Engine / [PLANNED] Unity UI Integration  
**Player Role**: Traffic Crisis Commander  
**Last Updated**: 2026-08-23

---

## 1. Core Gameplay Loop
```text
TRAFFIC EVENT (Accident/Surge/Emergency)
  └─► AI CONGESTION DETECTION & PREDICTION
        └─► AI STRATEGY RECOMMENDATION (With XAI Rationale)
              └─► PLAYER DECISION (Accept AI / Modify / Override)
                    └─► DIGITAL TWIN SIMULATION & COMPARISON
                          └─► SCORE, STREAK & BADGE REWARD
```

---

## 2. 3-Minute Judge Demo Scenario
1. **00:00 - 00:30 (Baseline)**: Steady traffic flow through J1, J2, J3. Player views isometric 3D corridor.
2. **00:30 (Accident Spawn)**: Minor collision on approach to J2 blocking Lane 1. Queue starts building.
3. **00:45 (AI Alert & Prediction)**: AI warns: *"Congestion risk at J2 within 5 minutes (Confidence: 88%)"*.
4. **01:00 (Emergency Event)**: Ambulance enters N_to_J1 edge heading towards South Hospital.
5. **01:15 (Recommendation)**: AI recommends *"Emergency Green Corridor + Route Diversion via E1"*.
6. **01:30 (Player Action)**: Player approves recommendation. Digital Twin simulates outcomes.
7. **02:00 (Execution)**: Ambulance clears corridor with 0.0s delay. Queue dissipates.
8. **02:45 (Results & Score)**: Player earns +1200 Points, Beat-the-AI Multiplier (x2.0), and unlocks "Emergency Ace" Badge.

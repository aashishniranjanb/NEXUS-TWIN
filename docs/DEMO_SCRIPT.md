# DEMO_SCRIPT.md — 3-Minute Hackathon Judge Demo Script

**Status**: [IMPLEMENTED] Master Presentation Script  
**Scenario**: Accident at J2 + Ambulance Dispatch + Predicted Congestion  
**Last Updated**: 2026-08-23

---

## 1. Timeline & Narration Script

### 00:00 - 00:30 | Introduction & Strategic View
- **Action**: Launch Unity client. Isometric strategic view shows 3-junction corridor J1-J2-J3 with active traffic.
- **Narrator**: *"Welcome to NEXUS-TWIN. What you are seeing is an authoritative SUMO Digital Twin rendered in real time in Unity 6."*

### 00:30 - 01:00 | Incident Spawn & AI Prediction Alert
- **Action**: Trigger accident event at J2 approach. Red warning indicator pulses.
- **Narrator**: *"An accident just occurred near J2. Notice the XGBoost AI model predicting a 50m queue within 5 minutes."*

### 01:00 - 01:45 | Emergency Dispatch & Counterfactual Evaluation
- **Action**: Priority Ambulance enters J1 edge. Player clicks "Request Recommendation".
- **Narrator**: *"An emergency ambulance is inbound. The Digital Twin snapshots the simulation state and evaluates 4 counterfactual futures in parallel."*

### 01:45 - 02:30 | XAI Rationale & Player Decision
- **Action**: Recommendation panel displays: *"Extend Green at J2 by 20s + Divert E1"*. Confidence: 88%. Player clicks **Approve**.
- **Narrator**: *"The Responsible AI engine explains why this intervention works. The player approves, and SUMO applies the action."*

### 02:30 - 03:00 | Clearance, Scoring & Wrap-up
- **Action**: Ambulance passes J2 with 0.0s delay. Queue dissipates. Score popup shows **+1200 Points (Beat-the-AI x2.0)**.
- **Narrator**: *"Emergency cleared with zero delay. NEXUS-TWIN bridges human decision-making with AI intelligence."*

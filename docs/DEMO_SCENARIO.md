# Flagship Demonstration Scenario: Junction Disruption & Corridor Recovery

| Parameter | Value |
|---|---|
| **Scenario Name** | Market St Corridor Bottleneck & Domino Spillover |
| **Metropolitan Area** | Philadelphia (Geotab Empirical Dataset) |
| **Target Epicenter** | Junction #0 (Market St & 15th St) |
| **Temporal Window** | 17:00 (5:00 PM Weekday Commute Peak) |
| **Disruption Mechanism** | 60% Capacity Reduction on Major Approach |
| **Runner Script** | `python scripts/run_demo_pipeline.py` |

---

## 1. Step-by-Step Scenario Execution Walkthrough

```
[ Step 1: Real Geotab Context Ingested ]
   - City: Philadelphia, Junction #0 (NW -> SE movement)
   - Baseline historical median stopped time: 5.0s (p80: 15.0s)

[ Step 2: Contextual Prediction & Anomaly Diagnosis ]
   - Predicted stopping delay: 64.3 seconds
   - Anomaly Detector: Score 0.567 (Anomaly: True)
   - Fingerprint Engine: [INCIDENT_LIKE] (Confidence: 84%)
   - Evidence: Multi-sigma delay spike (z=+9.39) with severe speed drop (87%).

[ Step 3: Network Topology & Domino Cascade ]
   - Network Graph: 8 nodes, 16 directional links
   - Domino Cascade: J24 -> J1672
   - Network Exposure Index: 0.520 (Active localized congestion)

[ Step 4: Digital Twin Multi-Strategy Simulation ]
   - 900-second kinematic macroscopic flow simulation across 4 candidate strategies:
     1. Upstream Dynamic Diversion (25%): -28.5% delay, -66.8% queue (Score: 38.6/100)
     2. Hybrid Adaptive Coordination: 51.5% queue reduction
     3. Dynamic Green Extension (+20s): -0.0% (saturation constrained)
     4. No Action (Baseline): 0% reduction

[ Step 5: Responsible AI Safety Critic Audit ]
   - Status: CONDITIONAL_APPROVAL (Score: 78.0/100)
   - Verified Checks: Quantitative 900s kinematic simulation evidence confirmed.
   - Requirement: Human supervisor approval required.

[ Step 6: AI Recommendation & Explainability ]
   - Recommended Strategy: Upstream Dynamic Diversion (25%)
   - Reason: Clears 66.8% of vehicular queues along primary arterial.
   - Trade-off: Reroutes volume to parallel secondary network (+400m transit).
```

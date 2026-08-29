# NEXUS-TWIN Judge & Demonstration Runbook

## 3–5 Minute Live Demonstration Script

### Step 1: Real Geotab Ingestion & Provenance (30 seconds)
- **Action**: Launch backend (`python -m uvicorn backend.api.main:app --port 8000`) and open Web Command Center.
- **Narrative**: *"NEXUS-TWIN is powered by 856,387 real-world commercial vehicle telemetry records from the BigQuery-Geotab dataset across 4 metropolitan areas."*
- **Visual**: Point to `DATASET: GEOTAB CONNECTED` and `SYSTEM ONLINE` indicators.

### Step 2: Anomaly Detection & Semantic Fingerprint (45 seconds)
- **Action**: Select congested corridor bottleneck (e.g. Junction #0 / Market & 15th St).
- **Narrative**: *"The ML layer predicts an expected median stopping time of 38.4s and isolates an abnormal 3-sigma delay spike. The fingerprint engine classifies this not as an unsupported 'accident', but as an INCIDENT_LIKE directional disruption pattern."*
- **Visual**: Point to Traffic Fingerprint card with grounded evidence list.

### Step 3: Congestion Domino Effect & Spillover Prediction (45 seconds)
- **Action**: Click "View Domino Propagation".
- **Narrative**: *"Congestion does not stay isolated. Our NetworkX kinematic shockwave engine predicts that in 3.6 minutes, queues will spill backward into J1, and in 7.2 minutes into J4, pushing network exposure to 0.78."*
- **Visual**: Show animated cascade chain ($J_0 \to J_1 \to J_4$) and time-to-impact countdown.

### Step 4: Digital Twin What-If Simulation & Candidate Interventions (60 seconds)
- **Action**: Click "Simulate Candidate Interventions".
- **Narrative**: *"Instead of guessing, the Digital Twin runs a 900-second kinematic simulation evaluating 4 distinct strategies against the unmitigated baseline: Extend Green (+20s), Upstream Diversion (25%), Emergency Priority, and Hybrid Adaptive Coordination."*
- **Visual**: Show side-by-side Before-vs-After comparison cards showing $-38.4\%$ delay and $-45.2\text{m}$ queue reduction.

### Step 5: Responsible AI Critic & Explainable Copilot (45 seconds)
- **Action**: Highlight the AI Recommendation panel.
- **Narrative**: *"Before presenting any action to the operator, our Responsible AI Safety Critic audits the quantitative simulation deltas, checks for cross-street side effects, and confirms emergency vehicle protection. The explainer exposes full reasoning and trade-offs."*
- **Visual**: Show the green `SAFETY CRITIC: APPROVED (Score: 94/100)` badge.

### Step 6: Human Decision & Field Actuation (30 seconds)
- **Action**: Click **[ APPROVE STRATEGY ]** or demonstrate **[ OVERRIDE ]**.
- **Narrative**: *"The human operator remains in total control. Upon supervisor approval, signal timing offsets are dispatched to field controllers, immediately arresting the domino cascade."*
- **Visual**: Status switches to `DISPATCHED_TO_FIELD_SIGNALS` with logged audit trail.

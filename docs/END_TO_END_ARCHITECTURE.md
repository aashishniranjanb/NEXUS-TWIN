# NEXUS-TWIN End-to-End System Architecture

```
                       REAL GEOTAB TELEMATICS DATASET (856k records)
                                      │
                                      ▼
                        VALIDATED ML INTELLIGENCE LAYER
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
     XGBoost Regressor        Isolation Forest         Traffic Fingerprint
    (Median Stopped Time)    (Multivariate Anomaly)   (5 Diagnostic Classes)
             │                        │                        │
             └────────────────────────┬────────────────────────┘
                                      ▼
                         NETWORK INTELLIGENCE LAYER
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
      NetworkX Graph         Kinematic Shockwave         Domino Effect
     (Corridor Topology)     (Spillover Prediction)   (Cascade Chain J2->J1)
                                      │
                                      ▼
                      DIGITAL TWIN SIMULATION ENGINE
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
      Scenario Engine        Candidate Strategies     Kinematic Simulator
    (Disruption Models)    (Extend, Divert, EMS)      (900s Multi-Strategy)
                                      │
                                      ▼
                      DECISION INTELLIGENCE & CRITIC
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
   Responsible AI Critic     Explainability Engine     LangGraph Multi-Agent
     (Safety Audit)           (Transparent Trade-offs) (Orchestration Pipeline)
                                      │
                                      ▼
                            FASTAPI BACKEND SERVER
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
       REST Endpoints          SSE Event Stream         Contract Validation
                                      │
                                      ▼
                       AI TRAFFIC COMMAND CENTER (WEB)
             ┌────────────────────────┼────────────────────────┐
             ▼                        ▼                        ▼
     3D Network Viewport     AI Decision Copilot       Human Approval Loop
     (Interactive Canvas)    (What-If Comparisons)    (Approve / Override)
```

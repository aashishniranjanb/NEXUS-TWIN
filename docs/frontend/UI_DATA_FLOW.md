# UI Data Flow & Progressive Event Streaming

```
[ User Action / Selection ]
           │
           ▼
[ GET /api/v1/network/intelligence ] ───► Updates 3D Map, Hotspots & Domino Chain
           │
           ▼
[ POST /api/v1/decision/recommendation ]
    or [ GET /api/v1/decision/stream (SSE) ]
           │
           ├──► Step 1: Geotab Traffic State & Fingerprint Analyzed
           ├──► Step 2: Kinematic Shockwave & Domino Effect Computed
           ├──► Step 3: Candidate Interventions Generated
           ├──► Step 4: 900s Digital Twin Simulation Evaluated
           ├──► Step 5: Safety Critic Validates Recommendation
           │
           ▼
[ AI Decision Copilot Panel Populated ]
           │
           ├──► Operator clicks [ APPROVE ] ──► POST /api/v1/decision/human-action ──► Field Signal Actuation
           └──► Operator clicks [ OVERRIDE ] ──► Manual Custom Strategy Applied
```

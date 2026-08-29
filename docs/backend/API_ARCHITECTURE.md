# Backend API Architecture & Contract Suite

| Component | Framework | Details |
|---|---|---|
| **API Server** | FastAPI (Python 3.13) | REST endpoints + Server-Sent Events (SSE) streaming |
| **Validation Engine** | Pydantic v2 | Strict input/output schema validation |
| **CORS Policy** | Permissive (`allow_origins=["*"]`) | Fully accessible to Next.js command center |

---

## 1. Primary Endpoint Taxonomy

| Endpoint | Method | Input Contract | Output Contract | Purpose |
|---|---|---|---|---|
| `/health` | `GET` | None | Service Health Status | Health probe & version verification |
| `/api/v1/traffic/state` | `POST` | `TrafficStateRequest` | `TrafficState` | Comprehensive traffic state with baseline |
| `/api/v1/traffic/anomaly` | `POST` | `AnomalyEvaluationRequest` | `AnomalyEvaluationResponse` | Multi-dimensional z-score & Isolation Forest |
| `/api/v1/traffic/fingerprint` | `POST` | `AnomalyEvaluationRequest` | `FingerprintDiagnosticResponse` | 5-class semantic diagnostic classification |
| `/api/v1/network/graph` | `GET` | City, Hour, Weekend | `GraphSnapshot` | NetworkX corridor nodes & directional links |
| `/api/v1/network/intelligence` | `GET` | City, FocusNode | `NetworkIntelligenceResponse` | Master network metrics, spillover & domino |
| `/api/v1/simulation/scenarios` | `GET` | City | List of `SimulationScenario` | Canonical scenario catalog |
| `/api/v1/simulation/evaluate` | `POST` | ScenarioType, City | `DigitalTwinSimulationResponse` | 900s kinematic Digital Twin simulation |
| `/api/v1/decision/recommendation`| `POST`| City, IntersectionId | `AIRecommendationResponse` | 5-stage multi-agent reasoning decision |
| `/api/v1/decision/stream` | `GET` | City, IntersectionId | Server-Sent Events (SSE) | Live streaming of agent reasoning steps |
| `/api/v1/decision/human-action` | `POST` | `HumanDecisionRequest` | `HumanDecisionResponse` | Supervisor Approve / Override / Reject |

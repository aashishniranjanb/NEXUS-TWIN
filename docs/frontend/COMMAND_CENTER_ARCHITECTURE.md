# Command Center UI Architecture

| Layer | Technology | Details |
|---|---|---|
| **Command Center Interface** | Next.js / Web Application | Real-time traffic intelligence dashboard, decision copilot & simulator |
| **3D Network Visualization** | Three.js / Interactive Canvas | Kinetic arterial corridor rendering, shockwave heatmaps, and vehicle particles |
| **API Client** | Fetch + EventSource (SSE) | Connects to FastAPI backend (`/api/v1/...`) |
| **Decision Workflows** | AI Copilot + Operator Decision | Human APPROVE / OVERRIDE / REJECT |

---

## 1. Information Architecture & Panels
1. **Top HUD Bar**: Displays City (`Philadelphia`), System Health (`HEALTHY`), Provenance (`BigQuery-Geotab Connected`), and Active Model Status.
2. **Left Panel (Crisis & Fingerprint)**: Displays active bottleneck, XGBoost median stopped time prediction, Isolation Forest anomaly score, and 5-class semantic fingerprint.
3. **Center 3D Viewport**: Interactive network graph showing nodes ($J_1 - J_8$), directional traffic flows, queue bottlenecks, and Domino Effect shockwave propagation.
4. **Right Panel (AI Decision Copilot)**: Recommended intervention strategy, candidate alternatives, Responsible AI Safety Critic audit badge, and grounded evidence.
5. **Bottom Panel (Digital Twin What-If Simulator)**: Multi-strategy before-and-after comparison ($-\Delta\text{ Delay}$, $-\Delta\text{ Queue}$, $+\Delta\text{ Throughput}$), Emergency Corridor Mode, and human operator execution controls.

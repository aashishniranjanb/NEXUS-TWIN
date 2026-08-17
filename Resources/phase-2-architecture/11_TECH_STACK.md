# 11 — Technology Stack

## Guiding Principle
Prioritize **working integration over model/tooling complexity**. Every choice below is picked so that a 3–5 junction prototype can be built, run, and demonstrated within the Round 2 build window, with clear upgrade paths (marked "→ later") for anything more advanced.

## Stack Table

| Layer | Technology | Why |
|---|---|---|
| Traffic simulator | **SUMO** (Simulation of Urban MObility) | Mature, free, supports OSM import and programmatic control via TraCI |
| Road network source | **OpenStreetMap (OSM)** | Real road geometry importable directly into SUMO |
| Simulation control | **TraCI** (→ `libsumo` for speed later) | Standard SUMO API for retrieving state and injecting actions mid-run |
| Computer vision | **YOLO** (pretrained, e.g., YOLOv8/YOLO-Lite variant) | Fast, well-documented, edge-deployable vehicle detection |
| Backend / orchestration | **Python + FastAPI** | Fast to build REST endpoints around SUMO/TraCI and the optimizer |
| Data transport (edge → hub) | **MQTT** | Lightweight pub/sub, standard for IoT/edge telemetry |
| Congestion prediction | **XGBoost / Random Forest / LightGBM** → **LSTM later** | Establish a working, interpretable baseline before adding sequence models |
| Strategy optimization | **Deterministic scenario scoring** → **RL (stretch goal)** | Guarantees a working recommendation engine without depending on RL training time |
| Dashboard (initial) | **Streamlit** | Rapid Python-native UI for internal testing and the research-facing view |
| Game / competition UI | **Web UI (React or plain HTML/JS)** — Unity only if time allows | Faster to iterate than Unity in a time-boxed build; see `29_...`/`54_UI_UX_SPECIFICATION.md` |
| Visualization | **Plotly** (dashboard), **SUMO-GUI** (simulation) | Native to the Python stack |
| Database | **SQLite** (dev) → **PostgreSQL** (if needed) | Zero-setup for hackathon speed; upgrade path if scaling required |
| Messaging/queue (if needed) | MQTT broker (e.g., Mosquitto) | Same as data transport, avoids introducing a second protocol |
| Experiment tracking | CSV + Python scripts | Simple, reproducible, no external service dependency |
| Version control | Git / GitHub | Standard |
| Deployment (prototype) | Local machine(s) at the venue | No cloud dependency risk during the 8-hour build |

## Why SUMO Specifically
SUMO's TraCI interface supports retrieving live simulation values and manipulating a running simulation, which is exactly the closed-loop mechanism the Scenario Engine needs (simulate candidate actions, read back resulting metrics, choose the best one). SUMO also has official, documented support for importing real road networks from OpenStreetMap and for generating traffic demand synthetically or from observation/count data — covering our Stage 1–3 dataset strategy in `41_DATASET_PLAN.md`.

## Explicit Non-Choices (and why)

| Rejected / deferred | Reason |
|---|---|
| Unity for the core build | High graphics/engineering overhead; risks spending the build window on visuals instead of the working engine (see `29_...` build-order rule) |
| GNN + LSTM + Transformer forecasting from day one | State-of-the-art but heavy; matches existing 2026 research (`04_RESEARCH_LITERATURE.md` ref 4) rather than differentiating us; deferred to a stretch goal |
| RL as the core decision mechanism | Training time and reproducibility risk; deterministic scenario scoring is used as the dependable core, RL kept optional (`36_REINFORCEMENT_LEARNING.md`) |
| Cloud deployment for the prototype | Adds network/deployment risk during a time-boxed offline event |

## Dependency Notes
- Python 3.10+ recommended for SUMO/TraCI + FastAPI + ML library compatibility.
- SUMO must be installed separately (not a pip package) — see `21_SIMULATION_SETUP.md`.
- YOLO model weights should be pre-downloaded before the event to avoid depending on venue network access.

# TECH_STACK.md — NEXUS-TWIN
## Frozen Technology Decisions v1.0

**Purpose of this document**: lock the architecture so decisions are not made ad hoc during the build. Anything not listed under §32 "Frozen Decisions — USE" should not be introduced without updating this document first.

**Core architectural rule** (do not violate):
> **Unity is the game/client. Python is the intelligence server. SUMO is the authoritative Digital Twin.** Multi-agent orchestration is added later without replacing the existing XGBoost model or Scenario Engine. Unity never becomes the source of truth for traffic.

---

## 1. Technology Stack Summary

| Layer | Technology | Purpose | Status |
|---|---|---|---|
| 3D Game | Unity 6 | 3D world, vehicles, UI, gameplay | Core |
| Rendering | URP (Universal Render Pipeline) | Cross-platform optimized rendering | Core |
| Input | Unity Input System | Mouse, keyboard, touch/gamepad | Core |
| Camera | Cinemachine | Strategic/isometric camera control | Core |
| Game Logic | C# | Gameplay and client state | Core |
| Traffic Simulation | SUMO 1.27.1 | Microscopic Digital Twin | Existing |
| Simulation API | TraCI 1.27.x | External SUMO control | Existing |
| High-performance simulation | libsumo | Later optimization (same API as TraCI) | Optional |
| Prediction AI | XGBoost | Congestion prediction | Existing |
| Backend | Python 3.12+ | AI + simulation orchestration | Core |
| API | FastAPI | Unity ↔ Python communication | Core |
| Realtime | WebSocket | Live simulation events | Core |
| Data processing | Pandas / NumPy | Feature engineering | Existing |
| Agent orchestration | LangGraph | Multi-agent layer | Phase 2 |
| Explanation LLM | OpenAI / other LLM API (provider-abstracted) | Natural-language explanation | Phase 2 |
| Edge hardware | ESP32 + MQTT | Physical prototype | Phase 3 |
| Computer vision | YOLO / ONNX | Vehicle perception | Phase 3 |
| Assets | Kenney / CC0-compatible packs | Vehicles / environment | Core |
| Version control | Git + GitHub | Source control | Core |

## 2. Game Engine — Unity 6

Use **Unity 6**, not Unity 2022/2023, unless an existing dependency forces otherwise. Unity 6 supports desktop, Web, and mobile deployment from one project with dedicated build workflows for each.

**Why Unity**: mature 3D ecosystem, huge asset ecosystem, C#, native Windows/Web/Android build targets, strong UI tooling, good performance for low-poly traffic scenes, straightforward future hardware integration path.

## 3. Rendering — URP

Use **Unity 6 + URP**, not HDRP. URP is purpose-built for optimized rendering across mobile, PC, and other platforms, which matches this project's low-poly, performance-first visual target (`DESIGN_GUIDELINES.md`).

Target visual style: **stylized low-poly smart city**, not photorealistic — this yields higher FPS, smaller builds, and easier Web/Android deployment, leaving more build-window time for gameplay and AI integration rather than graphics tuning.

## 4. Unity Packages

Core packages:
```text
com.unity.inputsystem
com.unity.cinemachine
com.unity.render-pipelines.universal
com.unity.ugui
```
The Unity Input System is the current, extensible input framework and is fully supported on Unity 6.

**Input support**: keyboard, mouse, touch, gamepad. Primary control scheme is mouse + keyboard on desktop; touch on Android (later).

## 5. Camera — Cinemachine

Camera modes: **Strategic Isometric** (primary, elevated ~45–60°), **Free Camera**, **Incident Focus** (auto-move to accident/congestion/emergency), **Emergency Vehicle Follow**. Full behavior spec in `DESIGN_GUIDELINES.md` §7–8.

## 6. Game Client Architecture — Division of Responsibility

**Unity handles**: rendering, player input, game UI, animation, audio, visual traffic representation, local game state.

**Python handles**: traffic intelligence, XGBoost inference, strategy generation, SUMO orchestration, counterfactual simulation, agents (Phase 2), explainability.

Unity never runs the traffic intelligence stack itself — this is the architectural rule stated at the top of this document, restated here as the specific division it implies.

## 7. Backend — Python 3.12+

Use **Python 3.12+**, not 3.10, for the new game-server environment. Current XGBoost documentation raised its minimum supported Python version to 3.12 as of the 3.3 release line — building the environment around an older interpreter risks a dependency conflict discovered late in the build.

## 8. Existing AI — XGBoost (Unchanged)

Keep the existing trained model (`congestion_model.pkl`) as-is; it becomes a **service/tool** consumed by the game server, not something rewritten for the game. Reported baseline (verify against current model artifact before final submission):
```text
Accuracy:   80.26%
F1:         0.8079
Queue MAE:  33.68 m
```

## 9. Digital Twin — SUMO 1.27.1 (Unchanged)

SUMO remains the **authoritative** traffic simulator — the existing network (3 junctions, ~1,000 vehicles, traffic signals, TraCI integration, metrics, counterfactual scenarios per `docs/phase-3-digital-twin/`) is kept, not rebuilt for the game.

## 10. TraCI

Use `traci` (PyPI, current release line 1.27.x as of mid-2026). TraCI is the standard interface for external Python control of a live SUMO simulation, including reading and modifying vehicles and traffic lights mid-run — this is the same mechanism already specified in `19_SIMULATION_ARCHITECTURE.md`.

```text
Development:      TraCI (socket-based, easier to debug)
Performance mode: libsumo (same API surface as TraCI; SUMO's own
                   documentation recommends it when performance
                   matters and the GUI isn't required)
```

## 11. SUMO ↔ Unity Bridge

**Do not duplicate SUMO physics inside Unity.** SUMO is authoritative; Unity is a renderer of SUMO's state.

Data sent from SUMO (via the Python bridge) to Unity, per vehicle/signal:
```text
Vehicle ID, Position, Rotation, Speed, Lane, Vehicle Type
Signal State, Incident State
```

```text
SUMO → Python Bridge (TraCI) → FastAPI → Unity (renders received state)
```

**Reference implementation to evaluate**: SUMO2Unity, an existing open-source (MIT-licensed) project specifically built to import SUMO road networks into Unity and synchronize vehicle trajectories and traffic-light state in real time; its later release line adds built-in analytics. Using or adapting this project — rather than writing the bridge fully from scratch — is the recommended starting point, provided its license terms are followed and logged (see §26, `ASSETS.md`). Note: SUMO2Unity's own included example assets are CC-BY (attribution required) even though the integration code itself is MIT — track this distinction explicitly.

## 12. Backend API — FastAPI

Use **FastAPI** for the Unity ↔ Python interface. FastAPI has first-class WebSocket support, which is required for streaming simulation state (see §13).

## 13. Communication Protocol — REST + WebSocket

Two channels, not one:

**REST/HTTP** — for discrete, request/response actions:
```text
Start scenario · Load level · Request prediction · Request recommendation
Submit player action · Get final score
```
Unity's `UnityWebRequest` provides HTTP/HTTPS communication and works across Windows, Web, and Android targets.

**WebSocket** — for continuous, streamed data:
```text
Vehicle positions · Traffic signals · Congestion state
AI alerts · Emergency events · Simulation progress
```

```text
          REST
Unity ─────────────► FastAPI
Unity ◄───────────── FastAPI

       WebSocket (realtime)
Unity ◄════════════► FastAPI
```

**Why not raw TCP**: browsers do not permit arbitrary native TCP/UDP socket access. Unity's own Web networking guidance points to WebSocket/WebRTC/WebTransport as the browser-compatible realtime options — since a Web build is an explicit target (`PRD.md` §21), the realtime protocol must be WebSocket-compatible from day one, not retrofitted later.

## 14. Message Format — JSON (MVP)

```json
{
  "type": "vehicle_state",
  "simulation_time": 361,
  "vehicles": [
    { "id": "car_104", "type": "car", "x": 124.5, "y": 0, "z": 48.2,
      "speed": 8.4, "lane": "J2_N_0" }
  ]
}
```
JSON is used for the hackathon build because it is easiest to debug live. **Upgrade path**: MessagePack or Protobuf if bandwidth becomes a measured problem — not adopted preemptively.

## 15. Data Processing — Pandas / NumPy (Unchanged)

Existing dataset generation, feature engineering, analysis, and experiment-reporting pipeline (`32_TRAFFIC_FEATURE_ENGINEERING.md`) is reused unchanged for the game server.

## 16. AI Architecture — Current vs. Future

**Current (MVP):**
```text
Traffic State → Feature Engineering → XGBoost → Congestion Probability
→ Strategy Generator → SUMO
```

**Future (Phase 2):**
```text
                    Orchestrator
       ┌────────┬──────────┬─────────┬─────────┐
   Perception Prediction Strategy Simulation Safety
     Agent      Agent      Agent     Agent    Agent
       └────────┴──────────┴─────────┴─────────┘
                    → Explanation Agent → HUMAN
```

## 17. Multi-Agent Framework — LangGraph (Phase 2)

Recommended over building a bespoke agent framework. LangGraph is purpose-built as an orchestration runtime for stateful agents, with native support for durable execution, streaming, and human-in-the-loop workflows — and its **State / Nodes / Edges** graph model maps directly onto the existing traffic pipeline (Perceive → Predict → Generate → Simulate → Evaluate → Explain → Human approval).

## 18. Why LangGraph Fits This Project

The workflow is not "LLM → answer"; it is a mix of deterministic tools and agentic decisions:
```text
Perceive → Predict → Generate → Simulate → Evaluate → Explain → Human approval
```
LangGraph explicitly supports composing custom workflows that mix deterministic logic with agentic behavior, rather than forcing everything through an LLM call.

## 19. Critical Rule — Not Everything Is an LLM

| Deterministic (stays as-is) | Agentic (Phase 2 addition) |
|---|---|
| SUMO | Scenario interpretation |
| XGBoost | Strategy selection |
| Metrics | Trade-off reasoning |
| Safety constraints | Explanation generation |
| Scoring | Agent coordination |
| Traffic rules | |

This prevents the system degrading into "an LLM pretending to control traffic." **Agents orchestrate validated computational tools — they do not replace them.** This is the most important sentence in this document for any future contributor extending the system.

## 20. Agent Tools (Phase 2 interface contract)

Agents call into existing, validated functions — they never manipulate raw SUMO internals directly:
```text
get_traffic_state()
predict_congestion()
generate_strategies()
run_counterfactual()
calculate_metrics()
check_safety()
explain_decision()
```

## 21. Multi-Agent Pattern — Supervisor, Not Free-For-All

Use a **supervisor/custom workflow pattern**, not uncontrolled agent-to-agent chatting. LangGraph supports routers, subagents, and custom workflows, and its own guidance emphasizes that multi-agent decomposition is worth the complexity only when specialization, context separation, or parallelization provide genuine value — not by default.

```text
                 SUPERVISOR
                     │
            ┌────────┼────────┐
        Prediction Strategy Safety
           Agent     Agent    Agent
            │        │        │
            └────────┼────────┘
                      ↓
                Simulation Agent
                      ↓
                Explanation Agent
                      ↓
                    HUMAN
```

## 22. LLM Usage — Optional for MVP

For Round 2: **rule-based, template-driven explanation + structured AI outputs is sufficient** (matches `37_EXPLAINABLE_AI.md`'s approach exactly). Natural-language LLM explanation is a Phase 2 enhancement layered on top, not a Round-2 dependency. Provider should be abstracted behind an interface (OpenAI / Gemini / Anthropic / local model all viable) so no single vendor is hard-coded into the architecture.

## 23. Unity Local AI — Optional, Not Now

Unity's inference tooling (Inference Engine/Sentis) can import ONNX, LiteRT, and PyTorch models for on-device inference. **Do not move XGBoost into Unity** — the model is already validated in Python; moving it risks introducing subtle numerical or pipeline discrepancies for no MVP benefit. Reserve Unity-local inference for later, narrower use cases (e.g., on-device vehicle detection, offline play).

## 24. Computer Vision — Phase 3, Not MVP

```text
Camera → YOLO/ONNX → Vehicle Detection → Traffic Metadata → NexusTwin
```
For the first playable build, **do not depend on computer vision** — generate traffic state directly from SUMO (per the "Direct mode" already defined in `26_DIGITAL_TWIN_SYNC.md`). CV integration follows the plan in `31_COMPUTER_VISION.md` once the core game loop is solid.

## 25. Hardware — ESP32 + MQTT (Phase 3, Not Now)

```text
ESP32 → MQTT → Python → NexusTwin        (telemetry in)
NexusTwin → MQTT → ESP32 → LED Signal    (physical output)
```
Purpose: telemetry and a physical traffic-light prototype, not the main AI processor. Out of scope for Round 2.

## 26. Assets

Use open/permissively licensed assets exclusively. Required categories: vehicles, roads, buildings, traffic lights, trees, signs, emergency vehicles — all low-poly.

**Every external asset must be logged** in `docs/ASSETS.md` with: `asset_name, source, creator, license, URL, modification`. This is non-negotiable per the competition's originality/licensing rules — do not download assets from Google Images/Sketchfab without confirmed permissive licensing.

## 27. Audio

Lightweight Unity audio only: traffic ambience, engine sound, horn, ambulance siren, alert tone, button feedback, success/failure stings. No large streamed music tracks needed for MVP.

## 28. Save System

**MVP**: flat JSON, storing `player_score, level, decisions, scenario_seed, AI_recommendations, accepted_actions`.
**Later** (if persistent progression is needed): migrate to SQLite, consistent with the schema philosophy already used on the backend (`18_DATABASE_SCHEMA.md`).

## 29. Logging

Every player decision emits one structured event, mirroring the `Decision` object already defined in `14_DATA_ARCHITECTURE.md`:
```json
{
  "scenario_id": "accident_j2_001",
  "prediction": 0.87,
  "strategies_tested": ["extend_green", "diversion", "dynamic_lane"],
  "recommended": "diversion",
  "player_action": "approve",
  "delay_delta": -0.31,
  "queue_delta": -0.28,
  "emergency_safe": true
}
```
This log is the shared substrate for research write-ups, explainability audits, debugging, and judging — treat it as a first-class artifact, not incidental telemetry.

## 30. Deployment

| Environment | Stack |
|---|---|
| Development | Windows + Unity Editor + Python + SUMO, all local |
| Hackathon primary | Windows standalone build — fully local, zero network dependency |
| Hackathon secondary | Unity Web build — Browser → Unity Web → HTTPS/WebSocket → local or cloud server → Python → SUMO |
| Later | Android APK/AAB — Android acts as a **client only**; it does not host SUMO |

Unity's current Web workflow and browser networking constraints (§13) mean the backend interface must be designed around HTTP/WebSocket from the start — this is already reflected in §13–14, not an afterthought.

## 31. Recommended Repository Layout

```text
NEXUS-TWIN/
├── game/
│   └── unity/
│       ├── Assets/
│       ├── Packages/
│       ├── ProjectSettings/
│       └── README.md
├── backend/
│   ├── api/
│   ├── agents/
│   ├── prediction/
│   ├── strategy/
│   ├── explainability/
│   └── game_server/
├── simulation/
│   ├── network/
│   ├── routes/
│   ├── signals/
│   ├── scenarios/
│   └── configs/
├── src/
│   ├── traffic_state.py
│   ├── metrics_collector.py
│   ├── feature_engineering.py
│   └── strategy_generator.py
├── prediction/
│   └── congestion_predictor.py
├── experiments/
├── data/
├── assets/
├── hardware/
│   └── esp32/
├── tests/
├── docs/
│   ├── phase-1-research/ … phase-6-productization/   (existing)
│   └── game/
│       ├── PRD.md
│       ├── TECH_STACK.md
│       ├── DESIGN_GUIDELINES.md
│       └── ASSETS.md
└── README.md
```
This layout keeps the existing six-phase research/engineering documentation intact and adds a parallel `docs/game/` tree for the player-facing product — no existing document needs to move.

## 32. Frozen Technology Decisions

**USE:**
```text
Unity 6 + URP · C# · Python 3.12+ · FastAPI · WebSockets
SUMO 1.27.1 · TraCI · XGBoost · Pandas / NumPy
LangGraph (Phase 2) · MQTT (hardware phase)
ONNX / Unity Inference Engine (optional CV phase)
```

**DO NOT USE YET:**
```text
✗ Unreal Engine          ✗ Godot
✗ React as primary client ✗ Three.js as primary 3D engine
✗ LLM controlling SUMO directly
✗ Kubernetes             ✗ Microservices-everywhere
✗ Multiplayer networking ✗ Blockchain
✗ Cloud dependency for the core demo
```
The goal is **one coherent stack**, not twenty-five technologies. Any proposal to add something outside "USE" requires updating this document explicitly, with a stated reason, before implementation begins.

## 33. Final Architecture Diagram

```text
                    ┌──────────────────────┐
                    │       UNITY 6 / URP  │
                    │  3D World · Vehicles │
                    │  Game UI · Player     │
                    └──────────┬───────────┘
                               │ HTTP / WebSocket
                    ┌──────────▼───────────┐
                    │    FASTAPI GAME      │
                    │       SERVER          │
                    └──────────┬───────────┘
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
         XGBOOST          STRATEGY          EXPLAINER
                            ENGINE
              └────────────────┼────────────────┘
                               ▼
                    ┌──────────────────────┐
                    │  SUMO DIGITAL TWIN   │
                    └──────────┬───────────┘
                             TraCI
                               ▼
                        TRAFFIC STATE
                               │
                               ▼
                    ┌──────────────────────┐
                    │   FUTURE AGENTS      │
                    │ Perception ·          │
                    │ Prediction · Strategy │
                    │ Simulation · Safety · │
                    │ Explanation           │
                    └──────────────────────┘
```

**The single rule to defend in Q&A:** SUMO is the Digital Twin source of truth; XGBoost predicts; the Scenario Engine evaluates; agents (Phase 2) orchestrate; Unity visualizes and lets the human play. This separation is what allows building the 3D game now, adding multi-agent intelligence later, and adding camera/ESP32 hardware eventually — without rebuilding the core system each time.

## Cross-References
- Product requirements this stack implements: `PRD.md` (this folder)
- Visual/UI constraints this stack must support: `DESIGN_GUIDELINES.md` (this folder)
- Underlying engine this wraps: `docs/phase-2-architecture/`, `docs/phase-3-digital-twin/`, `docs/phase-4-ai-intelligence/`

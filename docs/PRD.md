# PRD.md — NEXUS-TWIN: Traffic Crisis
## Product Requirements Document v1.0

| Field | Value |
|---|---|
| Project | NEXUS-TWIN |
| Working Game Name | NEXUS-TWIN: Traffic Crisis |
| Product Type | AI-powered 3D traffic strategy / simulation game |
| Primary Track | Responsible & Explainable AI |
| Secondary Capability | Computer Vision / Edge AI |
| Platform | Unity Windows standalone (primary) → Unity Web (demo) → Android APK (later) |
| AI Backend | Python + XGBoost + agentic orchestration (Phase 2) |
| Digital Twin | SUMO + TraCI |
| Game Engine | Unity 6 (URP) |
| Status | Prototype → Hackathon MVP → Expanded research/game platform |
| Relationship to prior docs | Extends `docs/phase-1-research` through `phase-6-productization`; does not replace them — this is the game-specific PRD sitting on top of the validated NexusTwin engine (`07_NOVELTY_AND_CONTRIBUTIONS.md`, `27_SCENARIO_ENGINE.md`) |

---

## 1. Product Vision

NEXUS-TWIN is a playable intelligent traffic-management game in which the player acts as a human traffic operator. The game continuously generates traffic situations — congestion, accidents, road closures, emergency vehicles, traffic surges, signal failures. The AI observes the situation and predicts what may happen next. **Instead of automatically controlling the city, the AI proposes interventions.** The Digital Twin lets the player test possible futures before committing to an action. The player ultimately decides.

**Core principle:**
> AI predicts. Digital Twin tests. AI explains. Human decides.

This directly extends the concept already validated in the research documentation (`06_RESEARCH_GAP.md`, `07_NOVELTY_AND_CONTRIBUTIONS.md`) — the game is the human-facing surface of the same engine, not a separate product.

## 2. Problem

Traditional traffic-management systems detect → predict → control. This game asks a different, complementary question:

> **Can an AI recommendation be understood and verified by a human before it is acted on?**

A local intervention can improve one junction while worsening another (spillback — see `06_RESEARCH_GAP.md`). The project already identifies interconnected junction effects, queue spillback, limited scenario testing, black-box recommendations, and human/safety constraints as the core problem (`02_PROBLEM_STATEMENT.md`). NEXUS-TWIN turns that problem into an interactive experience where the player directly feels the consequence of trusting or not trusting the AI.

## 3. Game Objective

The player does **not** drive a vehicle. The player manages the traffic network.

**Primary objective:** Keep the city moving while minimizing delay, congestion, and safety risk.

**Secondary objectives:**
- Protect emergency routes.
- Minimize queue spillback.
- Maintain network speed.
- Respond to unexpected incidents.
- Evaluate AI recommendations critically.
- Learn *when* an AI recommendation should and should not be trusted.

## 4. Target Player

| Tier | Audience |
|---|---|
| Primary | Students/young adults interested in strategy games, simulation games, AI, smart cities, engineering |
| Secondary | Hackathon judges, researchers, transportation professionals, educators, smart-city demonstrators |

## 5. Core Gameplay Loop

```text
        TRAFFIC EVENT
             ↓
       AI PERCEPTION
             ↓
      FUTURE PREDICTION
             ↓
      PLAYER ALERT
             ↓
     AI RECOMMENDATIONS
             ↓
      PLAYER CHOOSES
             ↓
     DIGITAL TWIN TEST
             ↓
   COUNTERFACTUAL FUTURES
             ↓
       AI EXPLANATION
             ↓
      PLAYER APPROVES
             ↓
       TRAFFIC CHANGES
             ↓
          SCORE
             ↓
       NEXT EVENT
```

This loop is what makes the product a **game**, not a visualization — every stage from `12_SYSTEM_ARCHITECTURE.md`'s pipeline is surfaced as a player-facing beat.

## 6. Core Game Mechanics

### 6.1 Traffic State (World)
```text
J1
 │
J2
 │
J3
```
Each junction has traffic lights, multiple approaches, and mixed traffic (cars, buses, trucks, bikes, emergency vehicles) — matching the network scope frozen in `10_SCOPE_AND_NON_SCOPE.md` (3–5 junctions).

### 6.2 Dynamic Events

| Tier | Events |
|---|---|
| Normal | Rush hour, heavy traffic, demand spike |
| Disruptions | Accident, road closure, signal failure, lane blockage |
| Emergency | Ambulance, fire truck, police vehicle, emergency corridor |
| Advanced | Multiple simultaneous incidents, sudden demand surge, network spillback, conflicting objectives |

These map directly onto the use cases already defined in `09_USE_CASES.md` and the procedural generator in `28_INCIDENT_ENGINE.md` / `53_PROCEDURAL_EVENTS.md`.

## 7. AI Prediction

The existing XGBoost model (`33_CONGESTION_PREDICTION.md`) is the first intelligence layer feeding the game. Current validated prototype baseline (to be re-verified against the latest trained model before final submission):

```text
Training samples:  8,808 labeled samples
Test accuracy:     80.26%
F1 score:          0.8079
Queue MAE:         33.68 m
```

Example in-game translation:
```text
J2 CONGESTION ALERT
Probability: 87%
Expected: HIGH QUEUE / HIGH DELAY / SPILLBACK RISK
```

**No fabricated numbers rule carries over from `40_EXPERIMENT_PLAN.md`**: these figures must be re-validated against the actual current model before appearing in a demo or pitch.

## 8. Player Decision System

| Strategy | Description | Maps to Scenario Engine type (`27_SCENARIO_ENGINE.md`) |
|---|---|---|
| A — Extend Green | Increase green duration at the affected junction | `green_extend` |
| B — Divert Traffic | Redirect vehicles to an alternate route | `diversion` |
| C — Dynamic Lane | Reallocate lane priority | `dynamic_lane` |
| D — Emergency Priority | Prioritize the emergency vehicle | `emergency_priority` |
| E — No Intervention | Trust that current control is sufficient | `do_nothing` (baseline candidate, `34_STRATEGY_GENERATION.md`) |

Strategies offered to the player are strictly constrained to what the backend can actually simulate — no strategy appears in the UI unless the Scenario Engine can genuinely evaluate it.

## 9. Digital Twin Gameplay (Core Differentiator)

Instead of immediately applying a strategy, the player triggers parallel counterfactual simulation:

```text
PLAYER: "Should I divert traffic?"
          ↓
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │ FUTURE A    │  │ FUTURE B    │  │ FUTURE C    │  │ FUTURE D    │
    │ DIVERSION   │  │ GREEN EXT.  │  │ LANE CHANGE │  │ NO ACTION   │
    └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

SUMO performs the actual counterfactual simulations via TraCI (`13_DIGITAL_TWIN_ARCHITECTURE.md`, `19_SIMULATION_ARCHITECTURE.md`, `27_SCENARIO_ENGINE.md`) — this game mechanic is a direct, honest surface of the clone-simulate-discard-apply pattern already documented as Contribution 3.

## 10. Explainable AI

Every recommendation must answer **why**, using only evidence the Scenario Engine actually produced (`37_EXPLAINABLE_AI.md`):

```text
AI RECOMMENDATION: DIVERT TRAFFIC
WHY?
  Queue reduction     -28%
  Network delay       -31%
  Spillback risk       LOW
  Emergency route      SAFE
Confidence            84%
```
The player can expand to "Show evidence" and see the full comparison table across all evaluated candidates.

## 11. Human-in-the-Loop (Responsible AI Core)

The AI must never automatically control the city.

```text
┌─────────────────────┐
│ AI RECOMMENDATION   │
│ DIVERT TRAFFIC      │
│ [ APPROVE ]         │
│ [ TRY ANOTHER ]     │
└─────────────────────┘
```

This is central to the project's Responsible AI positioning and mirrors the `/strategy/evaluate` vs `/strategy/apply` API separation already frozen in `17_API_SPECIFICATION.md` and the oversight principle in `20_SECURITY_ETHICS.md`.

## 12. Scoring System

| Category | Sub-metrics |
|---|---|
| Network Efficiency | Delay reduction, queue reduction, speed improvement, throughput |
| Safety | Emergency route status, spillback, blocked junctions |
| Decision Quality | Appropriate intervention chosen, AI recommendation usage, counterfactual testing performed |

```text
NEXUS SCORE
Network Efficiency     91
Emergency Safety       100
Queue Management        87
Decision Quality        94
TOTAL                   93/100
```

## 13. AI Trust Mechanic (Signature Feature)

The player should not blindly trust the AI. Scenarios deliberately vary in reliability:

- **High-confidence, correct** — "AI confidence: 91% — Recommendation: GOOD"
- **Low-confidence, uncertain** — "AI confidence: 54% — Recommendation: UNCERTAIN"
- **Conflicting objectives** — "Delay ↓ BUT Emergency risk ↑"

```text
PLAYER PERFORMANCE
Network Efficiency        92%
Emergency Safety          100%
Queue Management          88%
AI Recommendations Used    7/10
AI Recs Correctly Accepted 6/7
AI TRUST SCORE             91%
```

This mechanic turns the game into a genuine Responsible AI learning experience and is the strongest alignment with the primary track — the AI Trust Score should be treated as a first-class design element, not a bonus stat.

## 14. Multi-Agent Evolution (Phase 2 — Not an MVP Dependency)

```text
PERCEPTION AGENT → PREDICTION AGENT → STRATEGY AGENT → SIMULATION AGENT → SAFETY AGENT → EXPLANATION AGENT → PLAYER/HUMAN
```

| Agent | Responsibility | Existing component it wraps |
|---|---|---|
| Perception | Understand traffic state | `31_COMPUTER_VISION.md` / `26_DIGITAL_TWIN_SYNC.md` |
| Prediction | Forecast congestion | `33_CONGESTION_PREDICTION.md` (XGBoost) |
| Strategy | Generate interventions | `34_STRATEGY_GENERATION.md` |
| Simulation | Test alternatives | `27_SCENARIO_ENGINE.md` (SUMO) |
| Safety | Evaluate constraints | `35_STRATEGY_OPTIMIZATION.md` (spillback/emergency weighting) |
| Explanation | Explain recommendation | `37_EXPLAINABLE_AI.md` |
| Human/Game | Present decision to player | Game UI layer |

**Existing XGBoost, Scenario Engine, and explainability modules become tools/services used by these agents — they are not rewritten.** This is a wrapping/orchestration layer, not a replacement. See `TECH_STACK.md` §17–21 for the LangGraph-based implementation plan.

**Differentiator to protect when agents are added:** *Agents do not directly control the city. They reason over counterfactual Digital Twin futures, expose the consequences, and keep the human/player in control.* This must be a gameplay mechanic (the APPROVE/TRY ANOTHER loop), not just an architecture diagram.

## 15. 3D Game World — Required Assets

| Category | Items |
|---|---|
| Vehicles | Sedan, SUV, bus, truck, motorcycle, ambulance, police vehicle, fire truck |
| Infrastructure | Roads, intersections, traffic lights, buildings, trees, signs, pedestrian crossings, barriers |

**Do not build these from scratch.** Use permissively licensed open-source assets (see `TECH_STACK.md` §26 and `ASSETS.md` requirement). Candidate sources identified: Kenney Car Kit (CC0), Kenney City Kit: Roads (CC0), Kenney Prototype Kit (CC0), RGS Free Low Poly Vehicles Pack (CC0). **Every asset license must be verified and logged before use — no assumptions from Google/Sketchfab downloads.**

## 16. Visual Style

Target: **clean smart-city strategy simulation**, low-poly. Explicitly not GTA-style, not a racing game, not photorealistic, not neon cyberpunk. Full direction in `DESIGN_GUIDELINES.md`.

## 17. Camera

| Mode | Purpose |
|---|---|
| Strategic (primary) | Elevated/isometric, ~45–60°, sees J1→J2→J3 simultaneously |
| Free | Inspect incidents manually |
| Incident Focus | Auto-moves to accident/congestion/emergency |
| Emergency Follow | Temporarily follows ambulance/fire truck/police |

## 18. Game UI (Summary — full spec in `DESIGN_GUIDELINES.md`)

```text
┌──────────────────────────────────────────────┐
│ TIME        TRAFFIC       SCORE       LEVEL  │
│                                              │
│                3D CITY                       │
│                                              │
│ AI ALERT                 ACTIONS             │
│ J2: 87%                  [SIMULATE]          │
└──────────────────────────────────────────────┘
```
Never cover the central road network with UI.

## 19. Game Levels

| Level | Name | Goal |
|---|---|---|
| 1 | Learn | Simple congestion, two choices — reduce queue |
| 2 | Rush Hour | Multiple junctions — maintain network efficiency |
| 3 | Accident | Accident at J2 — prevent spillback |
| 4 | Emergency | Ambulance needs J3 — reach hospital within time limit |
| 5 | AI Trust | Uncertain recommendation — decide whether to trust, test, or reject |
| 6 | Network Crisis | Multiple simultaneous events — balance efficiency + safety + emergency response |

## 20. MVP — Hackathon Minimum (Round 2 Target)

| Layer | Minimum required |
|---|---|
| World | J1/J2/J3, 3D roads, cars, buses, bikes, ambulance, traffic lights |
| Gameplay | One accident, one congestion event, one emergency event |
| AI | Congestion prediction, recommendation generation |
| Digital Twin | 3–4 strategies, counterfactual simulation |
| Player | Choose strategy, simulate, approve/reject |
| Score | Delay, queue, emergency safety, final score |

This is the same minimum floor already established in `10_SCOPE_AND_NON_SCOPE.md` — the game does not expand backend scope, it wraps it.

## 21. Platform Strategy

| Priority | Platform | Rationale |
|---|---|---|
| 1 | Windows standalone | Safest hackathon build — Unity + Python + SUMO run entirely locally, no network dependency |
| 2 | Unity Web build | Best judge/demo sharing — requires a running backend server (browser cannot host SUMO) |
| 3 | Android APK | Backup distribution only — architecture must stay platform-independent so this can be added later without rework |

**Decision:** Build for Windows first (offline-safe), Web second (shareable demo), APK last (stretch). Full protocol/architecture detail in `TECH_STACK.md`.

## 22. Performance Requirements

| Target | Desktop | Browser |
|---|---|---|
| Frame rate goal | 60 FPS | 30–60 FPS |
| Minimum acceptable | 30 FPS | — |
| Visible vehicles (MVP) | 100–300 | Same |

Backend SUMO can simulate substantially more vehicles independently of the rendering layer — rendering count is a Unity-side budget, not a simulation limit.

## 23. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Game shall display a 3D traffic network. |
| FR-02 | Vehicles shall move dynamically. |
| FR-03 | Traffic signals shall change according to simulation state. |
| FR-04 | Game shall generate traffic incidents. |
| FR-05 | AI shall predict congestion risk. |
| FR-06 | Game shall display AI recommendations. |
| FR-07 | Player shall select an intervention. |
| FR-08 | Digital Twin shall simulate alternatives. |
| FR-09 | Game shall compare outcomes. |
| FR-10 | Game shall explain the selected recommendation. |
| FR-11 | Player shall approve/reject the recommendation. |
| FR-12 | Game shall calculate a score. |
| FR-13 | Game shall advance to another scenario. |

## 24. Non-Functional Requirements

- **Reliability**: game continues functioning (degraded) if the AI service temporarily fails.
- **Explainability**: every recommendation must have an associated, evidence-linked reason.
- **Reproducibility**: same seed + same scenario should produce comparable results.
- **Performance**: rendering must not block the AI backend.
- **Modularity**: game, AI, SUMO, and agents remain separate modules (enforced by the architecture in `TECH_STACK.md`).
- **Safety**: no recommendation is ever presented as guaranteed real-world safe — see language rules in `DESIGN_GUIDELINES.md` §49.

## 25. High-Level System Architecture

```text
UNITY (3D world, vehicles, UI, player input)
        │  HTTP / WebSocket
        ▼
GAME SERVER — PYTHON (FastAPI)
        │
   ┌────┼────────────┐
   ▼    ▼             ▼
XGBOOST STRATEGY   EXPLAINER
        ENGINE
   └────┼────────────┘
        ▼
   SUMO DIGITAL TWIN
        │ TraCI
        ▼
TRAFFIC STATE (queue / speed / delay)
```

Full technical decisions (versions, protocol, packages) are frozen in `TECH_STACK.md` — this PRD intentionally does not restate them to avoid drift between documents.

## 26. Phase Roadmap

| Phase | Content | Status |
|---|---|---|
| 1 — Foundation | SUMO, 3 junctions, TraCI, metrics, baseline controllers | Existing |
| 2 — AI | Feature engineering, XGBoost congestion prediction, strategy generation | Existing |
| 3 — Digital Twin | Snapshot, multiple futures, strategy comparison, explanation | Existing |
| 4 — Game | Unity 3D city, vehicles, player controls, incidents, score | Next |
| 5 — Game + AI Integration | Unity ↔ Python API ↔ XGBoost ↔ SUMO ↔ Recommendation ↔ Unity | Next |
| 6 — Multi-Agent | Perception/Prediction/Strategy/Simulation/Safety/Explanation agents | Later |
| 7 — Hardware | Camera → Edge → Traffic Metadata → NexusTwin → Decision → ESP32 → LED Signal | Later |

## 27. Success Criteria (Hackathon MVP)

**Gameplay**: player completes ≥1 scenario; makes meaningful decisions; traffic visibly responds; score changes based on decisions.
**AI**: prediction is actually connected to gameplay; recommendation generated dynamically; explanation corresponds to real simulation results.
**Digital Twin**: ≥3 alternative strategies simulated; results measurable.
**Responsible AI**: AI does not make the final decision; recommendation has evidence; player can reject AI; player can test alternatives.
**Demonstration**: a judge understands the complete loop in under 3 minutes.

## 28. The 3-Minute Judge Demo

```text
0:00–0:20   Show 3D city. "You are the traffic operator."
0:20–0:45   Accident occurs; traffic begins building.
0:45–1:00   AI: "87% congestion probability at J2."
1:00–1:30   Player reviews Extend Green / Divert / Dynamic Lane / Emergency Priority; selects one.
1:30–2:00   Digital Twin simulates futures:
              A -18% delay   B -31% delay ★ BEST   C -12% delay   D +4% delay
2:00–2:20   AI explains: "Strategy B minimizes network-wide delay while
              preserving the emergency route."
2:20–2:40   Player approves. Traffic changes. Ambulance gets through.
2:40–3:00   Final: NETWORK SCORE 93 / QUEUE -28% / DELAY -31% / EMERGENCY ROUTE SAFE
```
Close with: *"The AI did not decide. It showed the player what could happen before the player decided."* — this line is the NexusTwin identity statement and should close every pitch.

## 29. Product Positioning

Not: *"a traffic simulation game."*
Instead: **"An AI-powered decision game built on a live Digital Twin, where players learn to evaluate — not blindly trust — AI recommendations."**

Three layers: **Game** (playable) → **AI** (intelligent) → **Digital Twin** (verifiable). Multi-agent orchestration later makes the intelligence distributed and extensible without changing this positioning.

## 30. Definition of Done (MVP)

```text
PLAYER → 3D CITY → INCIDENT → AI PREDICTION → RECOMMENDATIONS →
PLAYER CHOICE → SUMO COUNTERFACTUAL SIMULATION → COMPARE →
EXPLANATION → APPROVE/REJECT → 3D TRAFFIC RESPONSE → SCORE
```
The PRD is complete when this exact loop runs, end to end, playably.

## Cross-References
- Backend engine specification: `docs/phase-2-architecture/`, `docs/phase-3-digital-twin/`, `docs/phase-4-ai-intelligence/`
- Frozen technical decisions: `TECH_STACK.md` (this folder)
- Visual/UX direction: `DESIGN_GUIDELINES.md` (this folder)
- Scope discipline: `docs/phase-1-research/10_SCOPE_AND_NON_SCOPE.md`
- Ethics/oversight principles: `docs/phase-2-architecture/20_SECURITY_ETHICS.md`

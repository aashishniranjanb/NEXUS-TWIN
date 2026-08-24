# NEXUS-TWIN Team Work Split
# Hackathon deadline: August 29, 2026

---

## THE RULE

No one modifies another member's owned files without communication.
Unity scenes are owned by Aashish. Only Aashish merges into `main`.

---

## MEMBER 1 — Aashish
**Role: Game Director / Unity Lead / Release Owner**
**Branch: `feature/unity-polish`**

### Primary File Ownership
```
game/unity/Assets/_NexusTwin/
├── Scenes/             ← AASHISH ONLY. Do not touch.
├── UI/                 ← Aashish primary
├── Materials/          ← Aashish primary
├── Art/                ← Aashish primary
├── Prefabs/            ← Aashish primary
├── Audio/              ← Aashish primary
├── Scripts/Core/       ← Aashish primary (GameManager, SceneBootstrapper, EventBus)
├── Scripts/UI/         ← Aashish primary
├── Scripts/Camera/     ← Aashish primary
├── Scripts/Vehicles/   ← Aashish primary
├── Scripts/Traffic/    ← Aashish primary
└── Scripts/Audio/      ← Aashish primary
```

### Responsibilities
- Unity visual polish (vehicles, environment, lighting, roads)
- UI/UX polish (all panels, transitions, typography)
- Camera system and transitions
- Ambulance presentation and siren
- Mission 01 gameplay feel
- Audio and SoundManager
- Final Windows standalone build (.exe)
- Release packaging
- Final integration (merges friend PRs into main)
- Hackathon demo script
- 60–90s backup video recording

### Priority Stack (Aug 25–29)
```
P0 — Visual: Vehicles, ambulance, roads, lighting
P1 — UI:     Panels, cards, Digital Twin display, XAI
P2 — Feel:   Camera cuts, signal feedback, siren
P3 — Build:  NEXUS-TWIN_Mission01_Windows.zip
P4 — Demo:   Script + backup video
```

### Do NOT modify (without explicit coordination)
- `intelligence/`
- `simulation/`
- `backend/`
- `web/`
- `experiments/`
- `tests/`

---

## MEMBER 2 — Web Platform Lead
**Role: Browser Demo / Command Center**
**Branch: `feature/web-platform`**

### Primary File Ownership
```
web/
├── index.html
├── style.css
├── app.js
├── components/
└── public/
```

### Responsibilities
- NEXUS-TWIN Web Command Center (browser demo)
- Live traffic map visualization (J1, J2, J3)
- Congestion risk display
- AI recommendation display
- 4-future Digital Twin comparison panel
- XAI explanation panel
- Human decision input (approve/override)
- API consumption from FastAPI backend
- WebGL or web deployment

### API Contract (READ ONLY — do not change backend)
Use only these endpoints:
```
GET  /health
GET  /api/status
GET  /traffic/state
GET  /traffic/prediction?junction_id=J2
POST /strategy/evaluate
POST /strategy/apply
```

Expected payload for displaying futures:
```json
{
  "junction": "J2",
  "congestion_probability": 0.87,
  "recommended_strategy": "diversion",
  "confidence": 0.82,
  "strategies": [
    { "name": "extend_green",      "delay_change_pct": -12.4, "emergency_eta_change_sec": 4 },
    { "name": "divert_traffic",    "delay_change_pct": -37.6, "emergency_eta_change_sec": -24 },
    { "name": "emergency_priority","delay_change_pct": +8.0,  "emergency_eta_change_sec": -31 },
    { "name": "do_nothing",        "delay_change_pct": +45.0, "emergency_eta_change_sec": +24 }
  ]
}
```

### Success Criteria
Someone opens a browser and sees:
```
NEXUS-TWIN COMMAND CENTER
         │
   Traffic Map (J1/J2/J3)
         │
   Congestion Risk: 87%
         │
   AI Recommendation: DIVERT
         │
   [Simulate 4 Futures]
         │
   Compare → Explain → Decide
```

### Do NOT modify (without explicit coordination)
- `game/unity/`
- `intelligence/`
- `simulation/`
- `backend/api/main.py`  (read contract only)

---

## MEMBER 3 — AI & Simulation Lead
**Role: XGBoost / SUMO / Game Mechanics / Multi-Agent**
**Branch: `feature/ai-gameplay`**

### Primary File Ownership
```
intelligence/
simulation/
backend/
experiments/
tests/
game/unity/Assets/_NexusTwin/Scripts/Features/   ← new scripts only here
```

### Responsibilities
- AI prediction improvements (XGBoost confidence, multi-junction)
- SUMO simulation robustness
- Mission scoring system improvements
- Traffic event system (Accident, Closure, Surge, Signal Failure)
- Emergency ETA system (real measurement)
- Strategy consequence system (make choices actually differ)
- Multi-agent architecture groundwork (after above stable):
  - TrafficAgent, EmergencyAgent, SafetyAgent, StrategyAgent
- pytest suite maintenance (keep all tests passing)

### New Unity scripts: Features ONLY
Any new scripts must go into:
```
game/unity/Assets/_NexusTwin/Scripts/Features/
```
Examples of acceptable new scripts:
```
EmergencyETASystem.cs
TrafficSurgeEvent.cs
MultiAgentOrchestrator.cs
Mission02Controller.cs
MultiIncidentManager.cs
```

### Do NOT modify (without explicit coordination)
- `game/unity/Assets/_NexusTwin/Scenes/`  ← Aashish only
- `game/unity/Assets/_NexusTwin/Scripts/Core/GameManager.cs`
- `game/unity/Assets/_NexusTwin/Scripts/Core/SceneBootstrapper.cs`
- `game/unity/Assets/_NexusTwin/Scripts/UI/HUDController.cs`
- `game/unity/Assets/_NexusTwin/Scripts/UI/MainMenuPanel.cs`
- Any visual or material files

### API Contract: new endpoints must be agreed with web lead first

---

## GIT WORKFLOW

### Daily start
```powershell
git checkout main
git pull origin main
git checkout feature/<your-branch>
git merge main   # stay up-to-date
```

### During work
```powershell
git add .
git commit -m "feat: [short description]"
git push origin feature/<your-branch>
```

### Integration (Aashish only merges to main)
```
feature/web-platform ─────► PR ─► Aashish reviews ─► merge to main
feature/ai-gameplay  ─────► PR ─► Aashish reviews ─► merge to main
feature/unity-polish ─────► Aashish merges directly after testing
```

### Integration order
```
AI feature (Friend 2) → pytest → merge → Aashish integrates Unity → test
Web feature (Friend 1) → review → merge → full system test → release
```

---

## LOCKED FILES (nobody touches without Aashish approval)

```
game/unity/Assets/_NexusTwin/Scenes/Gameplay_J1J2J3.unity
game/unity/Assets/_NexusTwin/Scripts/Core/SceneBootstrapper.cs
game/unity/Assets/_NexusTwin/Scripts/Core/GameManager.cs
game/unity/Assets/_NexusTwin/Scripts/Core/EventBus.cs
game/unity/Assets/_NexusTwin/Scripts/UI/HUDController.cs
```

---

## RELEASE VERSIONS

| Version | Owner | Target | Use |
|---------|-------|--------|-----|
| Version A | Aashish | Unity Editor + Mock | Dev testing |
| Version B | Aashish | `.exe` (Windows standalone) | **Primary hackathon demo** |
| Version C | Friend 1 | Web browser | Round 1 / sharing / backup |
| Version D | All | Unity + FastAPI + XGBoost + SUMO | Technical live demo |

### Version B is the priority
```
NEXUS-TWIN_Mission01_Windows.zip
├── NEXUS-TWIN.exe
├── NEXUS-TWIN_Data/
└── README.txt
```
No Python. No internet. Double-click → game starts.

---

## 48-HOUR PARALLEL MILESTONES

| Member | 48h goal | Deliverable |
|--------|----------|-------------|
| Aashish | Unity Mission 01 polished | Playable, visually strong build |
| Friend 1 | Web Command Center live | Browser demo URL |
| Friend 2 | Improved simulation + events | Better AI mechanics + pytest green |

---

## DO NOT BUILD

```
❌ Mission 03
❌ Multiplayer
❌ LLM chatbot
❌ RAG / Vector DB
❌ Voice assistant
❌ Mobile APK (before .exe is done)
❌ Blockchain
❌ Open world
❌ Five-agent system before single-agent is stable
❌ GTA city scale
```

---

## THE PITCH

> NEXUS-TWIN is a playable Responsible AI traffic command game.
> AI predicts congestion. A Digital Twin simulates competing interventions.
> The human operator decides what the city actually does.

**AI recommends. The Digital Twin tests. The human decides.**

---

## DEMO FLOW (3–5 minutes)

```
0:00–0:20  Hook       Night city, hacker alert, emergency
0:20–1:00  Crisis     J2 congestion, ambulance dispatched
1:00–1:40  AI         87% risk, Recommendation: DIVERT
1:40–2:20  Override   Player selects EMERGENCY PRIORITY → AI Disagrees
2:20–3:00  Twin       4 counterfactual futures visualized
3:00–3:30  Approve    Player commits → real city changes
3:30–4:00  Outcome    Ambulance passes → Mission success
4:00–4:30  Score      Network health, safety, AI alignment
```

---
*Last updated: 2026-08-25*
*Integration Owner: Aashish*

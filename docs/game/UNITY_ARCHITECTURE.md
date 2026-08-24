# UNITY_ARCHITECTURE.md — NEXUS-TWIN
## Unity Client Architecture Specification v1.0

**Purpose**: define how the Unity game is internally constructed — managers, hierarchy, script dependencies, and data flow. This document does not repeat the PRD's gameplay rationale or the Design Guidelines' visual rules; it tells a Unity developer exactly what to build and how the pieces connect.

**Governing principle (repeat from every prior document, because it drives every decision here):**
> Unity = visualization + gameplay + player. Python = intelligence + decision support. SUMO = traffic physics / authoritative simulation. **Unity never becomes the traffic simulation authority.**

---

## 1. Purpose
Provide the concrete internal software architecture of the Unity client: managers, GameObject hierarchy, state machine, script dependency rules, and the seams where Stage A (scripted/stub) data is replaced by Stage B (live backend) data, per `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md`.

## 2. Unity Version & Rendering

| Setting | Value |
|---|---|
| Engine | Unity 6 |
| Render pipeline | URP |
| Scripting backend | IL2CPP (Windows standalone); Mono acceptable for Editor/dev iteration speed |
| Color space | Linear |
| Target resolution | 1920×1080 (desktop primary) |

No HDRP, no custom render pipeline — see `TECH_STACK.md` §3.

## 3. Project Folder Architecture

Matches `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md` §2 exactly — restated here as the authoritative reference for import paths used throughout this document:

```text
Assets/_NexusTwin/Scripts/
├── Core/          # GameManager, ScenarioDirector, GameState
├── Traffic/       # Junction, TrafficLightController, IncidentTrigger
├── Vehicles/      # VehicleAgent, VehicleManager, VehicleStateReceiver
├── UI/            # HUDController, AIAlertPanel, StrategyPanel,
│                  # CounterfactualCardPanel, ExplanationPanel, DecisionButtons
├── DigitalTwin/   # DigitalTwinSimulationView
├── Scoring/       # ScoreController, TrustScoreTracker
├── Camera/        # StrategicCameraController
├── Network/       # ApiClient, WebSocketClient, DTOs
└── Data/          # SharedIds (generated from shared_config, see DATA_CONTRACT.md)
```

## 4. Scene Architecture

| Scene | Loaded managers | Notes |
|---|---|---|
| `Boot.unity` | `GameManager` (persists via `DontDestroyOnLoad`), `ApiClient`, `WebSocketClient` | Establishes backend connection (or falls back to stub mode — §21) before any gameplay scene loads |
| `MainMenu.unity` | UI only | Loads `Gameplay_J1J2J3` on Play |
| `Training.unity` | Reduced `ScenarioDirector` timeline | Optional; can be cut under time pressure |
| `Gameplay_J1J2J3.unity` | Full stack: Traffic, Vehicles, UI, DigitalTwin, Scoring | The core scene — this is where 95% of implementation time is spent |

**Single-scene rule for MVP**: if time is tight, collapse `MainMenu` into an overlay `Canvas` inside `Gameplay_J1J2J3.unity` rather than maintaining a separate scene and load transition — matches the MVP note in the implementation plan (§3).

## 5. GameObject Hierarchy (Gameplay Scene)

```text
Gameplay_J1J2J3
├── _Managers                      (empty GameObject, holds all manager components)
│   ├── GameManager
│   ├── ScenarioDirector
│   ├── VehicleManager
│   ├── ScoreController
│   ├── TrustScoreTracker
│   ├── HUDController
│   └── DigitalTwinSimulationView
├── World
│   ├── Roads                      (static geometry, Kenney City Kit)
│   ├── Junctions
│   │   ├── J1 (Junction component)
│   │   ├── J2 (Junction component)
│   │   └── J3 (Junction component)
│   ├── Environment                (buildings, trees, props — visually secondary)
│   └── IncidentMarkers             (pooled: hazard cones, warning icons)
├── Vehicles                        (pooled VehicleAgent instances, parented here at runtime)
├── CameraRig
│   └── StrategicCameraController (Cinemachine vcams: Strategic, Free, IncidentFocus, EmergencyFollow)
├── Canvas_HUD
│   ├── TopBar
│   ├── AIAlertPanel
│   ├── StrategyPanel
│   ├── CounterfactualCardPanel
│   ├── ExplanationPanel
│   ├── DecisionButtons
│   └── BottomBar
└── Network
    ├── ApiClient
    └── WebSocketClient
```

## 6. Core Managers

### 6.1 `GameManager` (Core/)
- Singleton, persists across scene loads from `Boot.unity`.
- Owns: current connection mode (`Live` | `Stub` — see §21), global config (loaded `SharedIds`), current game session ID.
- Does **not** own gameplay logic — delegates to `ScenarioDirector`.

### 6.2 `ScenarioDirector` (Core/)
- Drives the timeline of a single playthrough: spawns Stage A traffic, fires the incident, sequences AI Alert → Strategy Panel → Simulation → Explanation → Approve/Reject → Score, per the exact beats in `PRD.md` §28.
- In **Stub mode**: timeline is time-triggered (coroutine, hardcoded seconds) — matches `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md` §16.
- In **Live mode**: timeline is event-triggered (waits on `incident_event` WebSocket messages and REST responses) rather than fixed timers — matches §17.6 swap order.
- **This is the single most important script to get right** — every other manager is called *from* here, in sequence; it is the game loop's spine.

### 6.3 `GameState` (Core/, plain data class, not MonoBehaviour)
```csharp
public enum GamePhase { Idle, Event, Analysis, Decision, Simulation, Explanation, Approval, Result, Score }
public class GameState
{
    public GamePhase CurrentPhase;
    public string ActiveScenarioId;
    public string ActiveJunctionId;
    public List<StrategyOption> AvailableStrategies;
    public StrategyOption ChosenStrategy;
}
```
Matches the nine game states frozen in `DESIGN_GUIDELINES.md` §38 — `GamePhase` enum values must map 1:1 to `STATE_01_IDLE` through `STATE_09_SCORE`. Only one phase is active at a time; UI panels subscribe to `GameState` changes and show/hide themselves accordingly rather than being manually toggled from multiple call sites.

## 7. Traffic System (Traffic/)

### 7.1 `Junction`
```csharp
public class Junction : MonoBehaviour
{
    public string junctionId;                  // must match SharedIds.Junctions
    public TrafficLightController[] lights;
    public Transform[] queueZones;
    public IncidentState currentIncident;       // None by default
}
```

### 7.2 `TrafficLightController`
- Drives one approach's light state (Red/Amber/Green) and optional countdown display (`DESIGN_GUIDELINES.md` §15).
- Stage A: cycles on a fixed local timer.
- Stage B: state is overridden by incoming `signal_state` WebSocket messages (§13 of this doc's API companion).

### 7.3 `IncidentTrigger`
- Already specified in `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md` §7.1–7.2. Restated ownership rule here: **only `ScenarioDirector` calls `IncidentTrigger.Fire()`** — no other script triggers incidents directly, to keep the single timeline authoritative.

## 8. Vehicle System (Vehicles/)

### 8.1 `VehicleAgent`
Per implementation plan §5.2. Two movement modes toggled by a single `bool useLiveState` flag — never two parallel code paths that both try to move the vehicle simultaneously.

### 8.2 `VehicleManager`
Per implementation plan §5.3. Object pool keyed by `VehicleType`. Public API:
```csharp
VehicleAgent Spawn(VehicleType type, string vehicleId, Vector3 position);
void Despawn(string vehicleId);
VehicleAgent GetById(string vehicleId); // used by VehicleStateReceiver
```

### 8.3 `VehicleStateReceiver` (Stage B only)
- Subscribes to `WebSocketClient`'s `vehicle_state` messages.
- For each vehicle in the message: `VehicleManager.GetById()` (spawn via `VehicleManager.Spawn()` if not yet present) then sets `useLiveState = true` and pushes position/speed/lane.
- **Never instantiates GameObjects directly** — always goes through `VehicleManager`'s pool, per the pooling rule in `DESIGN_GUIDELINES.md` §45.

## 9. Junction & Signal System
Covered under §7 above — kept as one system conceptually (junction + its lights + its incident state are updated together each tick) even though implemented as separate components for clarity.

## 10. Incident System
`IncidentTrigger` (§7.3) + pooled marker prefabs (hazard cone, warning icon, flashing overlay) instantiated at the affected `Junction`'s `queueZones` transform. Visual behavior per `DESIGN_GUIDELINES.md` §18.

## 11. Gameplay State Machine

```text
IDLE → EVENT → ANALYSIS → DECISION → SIMULATION → EXPLANATION → APPROVAL → RESULT → SCORE → (next EVENT or END)
```

Implemented as `GameState.CurrentPhase` transitions, driven exclusively by `ScenarioDirector`. UI panels are **reactive**, not drivers:
```csharp
gameState.OnPhaseChanged += phase => {
    aiAlertPanel.SetVisible(phase == GamePhase.Analysis);
    strategyPanel.SetVisible(phase == GamePhase.Decision);
    // etc.
};
```
This prevents the common bug class of two panels both being visible when they shouldn't be (`DESIGN_GUIDELINES.md` §38: "never mix all states simultaneously").

## 12. AI/UI Architecture

`HUDController` is the root; it does not contain gameplay logic, only layout/visibility orchestration for its four child panels (Top/Left/Right/Bottom per `DESIGN_GUIDELINES.md` §29). Each panel (`AIAlertPanel`, `StrategyPanel`, `CounterfactualCardPanel`, `ExplanationPanel`, `DecisionButtons`) is self-contained: it exposes a `Show(data)` method and events for user actions, and knows nothing about where its data came from (stub or live) — that separation is enforced by `ScenarioDirector`/`ApiClient`, not by the panels themselves. This is what makes the Stage A → Stage B swap (§17 of the implementation plan) safe: panel code never changes, only what feeds it.

## 13. Digital Twin Visualization (DigitalTwin/)

`DigitalTwinSimulationView` per implementation plan §11. Internally sequences the six-step animation from `DESIGN_GUIDELINES.md` §35 (freeze → fade → show branches → run ghost traffic → show metric deltas → return to decision) as a coroutine, driven by data passed in from `ScenarioDirector`, never fetched by itself.

## 14. Scoring System (Scoring/)

`ScoreController` + `TrustScoreTracker` per implementation plan §15. `TrustScoreTracker` specifically implements the reward rule from `DESIGN_GUIDELINES.md` §26: correctly rejecting a bad AI recommendation must increase, not decrease, the trust score. This requires `TrustScoreTracker` to know the *actual outcome* of a rejected recommendation (i.e., what would have happened) — which in Stub mode is hand-authored per scenario, and in Live mode comes from the backend having still computed the rejected candidate's `ScenarioResult` even though it wasn't applied.

## 15. Camera Architecture (Camera/)

`StrategicCameraController` wraps four Cinemachine virtual cameras (Strategic, Free, IncidentFocus, EmergencyFollow — `DESIGN_GUIDELINES.md` §8). Mode switches are driven by `ScenarioDirector` (e.g., auto-switch to `IncidentFocus` when an incident fires) and by direct player input (switch to `Free`) — both paths call the same `SetMode(CameraMode)` entry point.

## 16. Networking Layer (Network/)

| Script | Responsibility |
|---|---|
| `ApiClient` | REST calls via `UnityWebRequest`, one method per endpoint in `API_SPECIFICATION.md` |
| `WebSocketClient` | Connection lifecycle + message dispatch by `type` field |
| `DTOs` | Plain C# structs/classes mirroring backend JSON exactly (no logic) |

**Rule**: no other script in the project calls `UnityWebRequest` or opens a socket directly — all backend I/O goes through these two scripts, so the Stage A/Stage B swap and any future protocol change (e.g., MessagePack) touches exactly one place.

## 17. Data Transfer Objects
Defined in full in `API_SPECIFICATION.md` §14–20; Unity-side `DTOs.cs` mirrors those schemas field-for-field using C#-idiomatic naming (`camelCase` JSON → `PascalCase` C# properties via `[JsonProperty]` or Unity's `JsonUtility` naming convention — pick one serializer and use it everywhere, do not mix).

## 18. Backend Integration
See `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md` §17 for the swap sequence and `API_SPECIFICATION.md` for the full contract. This document's job is only to name *which Unity script* changes at each swap step (already cross-referenced inline in §7–14 above).

## 19. Script Dependency Rules

```text
ScenarioDirector  → (calls into) → VehicleManager, IncidentTrigger, HUDController,
                                    DigitalTwinSimulationView, ScoreController
GameState         ← (observed by) → all UI panels
ApiClient / WebSocketClient → (called only by) → ScenarioDirector, VehicleStateReceiver
VehicleStateReceiver → (writes to) → VehicleAgent (via VehicleManager)
UI Panels         → (never call) → ApiClient/WebSocketClient directly
```
**Hard rule**: UI panels never make network calls themselves. This keeps the entire networking surface behind two scripts (§16) and keeps UI panels reusable and testable against stub data without a running backend.

## 20. Performance & Object Pooling
- Vehicles: pooled per `VehicleType`, per `DESIGN_GUIDELINES.md` §45 and implementation plan §5.3.
- Incident markers (cones, warning icons): pooled the same way — not instantiated/destroyed per incident.
- UI panels: instantiated once at scene load, shown/hidden via `CanvasGroup.alpha`/`interactable`, never destroyed and recreated.
- Draw calls / shadows: follow the budget in `DESIGN_GUIDELINES.md` §44 — profile before assuming a change is "probably fine."

## 21. Error/Fallback Handling — Stub Mode

`GameManager` attempts a backend connection at `Boot.unity`. If it fails (or if a `--stub` launch flag / config value is set):
```csharp
public enum ConnectionMode { Live, Stub }
```
In `Stub` mode, `ApiClient`/`WebSocketClient` return hand-authored fixture data (the same fixtures used during Stage A development, per implementation plan §16) instead of making real network calls. **This is not just a development convenience — it is the explicit demo fallback** specified in implementation plan §19's Hour 7.5 rule: if live integration is unstable near the deadline, the build ships in `Stub` mode rather than risk a live failure mid-demo. This mode must therefore be kept working and tested throughout development, not treated as disposable scaffolding.

## 22. Testing
- Manual playtesting of the full `ScenarioDirector` timeline is the primary test method given the time constraints (no formal automated test suite is a hard requirement for Round 2).
- Where time allows: Unity Test Framework edit-mode tests for pure-logic classes only (`ScoreController` scoring math, `TrustScoreTracker` update rules) — not for MonoBehaviours requiring a running scene.
- Every panel should be independently playable in isolation (e.g., a debug scene that calls `StrategyPanel.ShowOptions()` with fixture data directly) so UI issues can be found without running the full timeline each time.

## 23. Definition of Done
```text
[ ] All managers listed in §6 exist and match their described responsibility exactly
[ ] GameState.CurrentPhase drives all panel visibility; no panel is shown/hidden
    from more than one call site
[ ] VehicleAgent supports both Stage A and Stage B movement behind one flag
[ ] No UI panel script contains a network call (verified by code review / grep
    for UnityWebRequest and WebSocket usage outside Network/)
[ ] Stub mode produces a fully playable scenario with zero backend running
[ ] Live mode swap (per implementation plan §17.4) has been exercised at least
    once per system before the final build is locked
```

## Cross-References
- Build sequence and milestones this architecture supports: `PHASE_4_UNITY_IMPLEMENTATION_PLAN.md`
- Backend contract every Network/ script implements: `API_SPECIFICATION.md`
- Shared identifiers referenced throughout (`junctionId`, `strategy_type`, etc.): `DATA_CONTRACT.md`
- Visual/UX rules every UI panel must follow: `DESIGN_GUIDELINES.md`
- Product loop this architecture ultimately serves: `PRD.md` §5, §28

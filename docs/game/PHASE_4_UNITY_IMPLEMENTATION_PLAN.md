# PHASE_4_UNITY_IMPLEMENTATION_PLAN.md — NEXUS-TWIN
## Unity Playable MVP — Implementation Plan v1.0

**Purpose**: turn `PRD.md` + `TECH_STACK.md` + `DESIGN_GUIDELINES.md` into concrete, buildable milestones — Unity project structure, scenes, prefabs, C# scripts, API contracts, asset list, and an hour-by-hour sequence for the Round 2 build window. This document is the thing a team member should have open while actually building, not a restatement of the other three.

**Scope reminder**: build **one spectacular 3-minute scenario** first (Ambulance + Accident at J2), not six levels. Everything below is ordered so that scenario is playable as early as possible, with levels/polish layered on only if time remains.

---

## 1. Build Order Principle (Non-Negotiable)

```text
1. Unity project scaffold
2. 3-junction 3D map (static)
3. Roads + signals (static, then scripted)
4. Vehicle assets imported
5. Vehicle movement (dummy/scripted first, SUMO-driven later)
6. Camera
7. Traffic events (scripted trigger first, backend-driven later)
8. Gameplay HUD
9. AI alert panel
10. Strategy selection UI
11. Digital Twin visualization (ghost futures)
12. Counterfactual cards
13. Explanation panel
14. Approve / Reject
15. Score
16. Complete playable scenario end-to-end

ONLY THEN:
17. Wire Unity ↔ FastAPI ↔ existing Python intelligence ↔ SUMO
```

**Rule**: steps 1–16 must work with a **stubbed/mocked backend** (hardcoded or locally-scripted responses) before step 17 begins. This guarantees a playable, demoable game exists even if the live SUMO/XGBoost integration runs into trouble late in the build — matching the same "prove the simpler thing works before adding complexity" discipline already used in `29_BASELINE_CONTROLLER.md`.

## 2. Unity Project Structure

```text
game/unity/
├── Assets/
│   ├── _NexusTwin/                     # All project-specific content (underscore = sorts first)
│   │   ├── Scenes/
│   │   │   ├── Boot.unity
│   │   │   ├── MainMenu.unity
│   │   │   ├── Training.unity
│   │   │   └── Gameplay_J1J2J3.unity   # The core 3-minute scenario scene
│   │   ├── Scripts/
│   │   │   ├── Core/
│   │   │   ├── Network/
│   │   │   ├── Traffic/
│   │   │   ├── Vehicles/
│   │   │   ├── UI/
│   │   │   ├── Camera/
│   │   │   ├── Scoring/
│   │   │   └── Data/
│   │   ├── Prefabs/
│   │   │   ├── Vehicles/
│   │   │   ├── Infrastructure/
│   │   │   └── UI/
│   │   ├── Materials/
│   │   ├── Audio/
│   │   └── ScriptableObjects/
│   ├── ThirdParty/                     # All imported open-source asset packs, untouched
│   │   ├── KenneyCarKit/
│   │   ├── KenneyCityKitRoads/
│   │   └── RGSVehiclePack/
│   ├── Packages/
│   └── ProjectSettings/
├── Packages/
│   └── manifest.json
└── README.md
```

**Rule**: never modify files under `Assets/ThirdParty/` directly — if a modification is needed, duplicate into `_NexusTwin/Prefabs/` first. This keeps license/attribution tracking (`ASSETS.md`) clean and upgrades non-destructive.

## 3. Scenes

| Scene | Purpose | Built in step |
|---|---|---|
| `Boot.unity` | Loads config, connects to backend (or stub), routes to Main Menu | Late (step 17 area) |
| `MainMenu.unity` | PLAY / TRAINING / HOW AI DECIDES / SETTINGS (`DESIGN_GUIDELINES.md` §53) | Polish pass |
| `Training.unity` | Under-one-minute tutorial loop (`DESIGN_GUIDELINES.md` §54) | Polish pass |
| `Gameplay_J1J2J3.unity` | **The core scene** — the entire 3-minute demo scenario lives here | Steps 2–16 |

**MVP note**: if time is short, `MainMenu` and `Training` can be a single static UI overlay rather than separate scenes — do not let scene-management polish delay `Gameplay_J1J2J3.unity`.

## 4. World Scaffold (Steps 2–3)

### 4.1 Static Layout
Build the J1–J2–J3 layout from `DESIGN_GUIDELINES.md` §9 directly as static geometry first (no SUMO connection yet):
```text
J1 (north) — straight road — J2 (center) — straight road — J3 (south)
```
Each junction: 4 approaches, crosswalks, one traffic-light rig per approach (from Kenney City Kit: Roads).

### 4.2 Junction GameObject Contract
```csharp
// Scripts/Traffic/Junction.cs
public class Junction : MonoBehaviour
{
    public string junctionId;              // "J1", "J2", "J3" — MUST match backend junction_id
    public TrafficLightController[] lights; // one per approach
    public Transform[] queueZones;          // used for vehicle queue visualization
}
```
**Critical**: `junctionId` strings must exactly match the `junction_id` values used in the backend `TrafficState` schema (`25_TRAFFIC_STATE_MODEL.md`) — this is the join key between the two systems and should be defined once, in one config file, not hardcoded independently in Unity and Python.

## 5. Vehicle Assets & Movement (Steps 4–5)

### 5.1 Asset Import Checklist
| Vehicle | Source pack | License to verify |
|---|---|---|
| Car (sedan/SUV) | Kenney Car Kit | CC0 |
| Bus | Kenney Car Kit / RGS pack | CC0 |
| Truck | Kenney Car Kit | CC0 |
| Motorcycle | RGS Free Low Poly Vehicles Pack | CC0 |
| Ambulance | RGS Free Low Poly Vehicles Pack | CC0 |
| Police / Fire (optional) | RGS Free Low Poly Vehicles Pack | CC0 |
| Roads / traffic lights / signage | Kenney City Kit: Roads | CC0 |

**Action for whoever does this step**: log every asset into `docs/ASSETS.md` (`asset_name, source, creator, license, URL, modification`) at the moment of import, not afterward — retroactive licensing audits are slower and error-prone under time pressure.

### 5.2 Vehicle Prefab Contract
```csharp
// Scripts/Vehicles/VehicleAgent.cs
public class VehicleAgent : MonoBehaviour
{
    public string vehicleId;         // matches SUMO vehicle id once integrated
    public VehicleType type;         // Car, Bus, Truck, Motorcycle, Ambulance, Police, Fire
    public float speed;
    public Transform target;         // next waypoint (Stage A: scripted path)

    // Stage A (steps 4-5): follows a hardcoded waypoint path at constant/random speed
    // Stage B (step 17+): position/rotation/speed driven every tick by VehicleStateReceiver
}
```

### 5.3 Vehicle Manager (Object Pooling — required per `DESIGN_GUIDELINES.md` §45)
```csharp
// Scripts/Vehicles/VehicleManager.cs
public class VehicleManager : MonoBehaviour
{
    // Pools of pre-instantiated VehicleAgent prefabs per VehicleType
    // Spawn(): pulls from pool, sets id/type/position; never Instantiate() mid-gameplay
    // Despawn(): returns to pool, does not Destroy()
}
```

### 5.4 Movement Stages
- **Stage A (MVP, steps 4–5)**: vehicles follow a scripted spline/waypoint path per lane, spawned at a fixed rate, to prove rendering + density visuals (`DESIGN_GUIDELINES.md` §13) work.
- **Stage B (step 17+)**: `VehicleStateReceiver` overrides Stage A movement, setting exact position/speed/lane from the SUMO-derived WebSocket stream (`TECH_STACK.md` §13–14).

Building Stage A first means the 3D world is playable and visually correct **before** the backend bridge exists — this directly supports the "prove the simpler thing works" rule in §1.

## 6. Camera (Step 6)

```csharp
// Scripts/Camera/StrategicCameraController.cs — Cinemachine-driven
// Modes enum: Strategic, Free, IncidentFocus, EmergencyFollow
// Default: Strategic, 45-60 deg elevation, framed on J1-J2-J3 (DESIGN_GUIDELINES.md §7-8)
```
Implement `Strategic` and `IncidentFocus` first (both needed for the 3-minute scenario). `Free` and `EmergencyFollow` are polish-pass additions.

## 7. Traffic Events (Step 7)

### 7.1 Stage A — Scripted Trigger (MVP)
```csharp
// Scripts/Traffic/IncidentTrigger.cs
public class IncidentTrigger : MonoBehaviour
{
    public IncidentType type;        // Accident, Closure, Surge, Weather, Emergency
    public string junctionId;
    public float triggerTimeSeconds; // for the scripted demo: fires at 00:20
}
```
For the core scenario, hardcode a single `IncidentTrigger` (Accident at J2, `triggerTimeSeconds = 20`) and a single emergency vehicle spawn — matching the exact 3-minute demo script in `PRD.md` §28.

### 7.2 Stage B — Backend-Driven (post step-17)
Same `IncidentType` enum, but triggered by an incoming WebSocket message from `POST /incident/trigger` (`17_API_SPECIFICATION.md`) instead of a local timer.

### 7.3 Visual Response (per `DESIGN_GUIDELINES.md` §18)
On trigger: spawn hazard cone/warning-icon prefab, disable one lane's waypoint path (Stage A) or reflect the backend's reduced-capacity state (Stage B), pulse the amber/red warning overlay.

## 8. Gameplay HUD (Step 8)

Build as one root `Canvas` with four fixed regions matching `DESIGN_GUIDELINES.md` §29:
```text
Scripts/UI/HUDController.cs
├── TopBar (Time, Traffic level, Score, Level)
├── LeftPanel (AI Alert)
├── RightPanel (Actions)
└── BottomBar (Queue / Delay / Speed bars — optional for MVP)
```
`HUDController` exposes a small public API other systems call into (`ShowAlert()`, `UpdateScore()`, `SetActionsAvailable()`) — do not let gameplay scripts reach directly into UI internals.

## 9. AI Alert Panel (Step 9)

```csharp
// Scripts/UI/AIAlertPanel.cs
public struct CongestionAlert { public string junctionId; public float probability; public int forecastMinutes; }
public class AIAlertPanel : MonoBehaviour
{
    public void Show(CongestionAlert alert); // "J2 CONGESTION RISK — 87% — Forecast: 5 min"
}
```
Stage A: fed by a hardcoded `CongestionAlert` fired alongside the scripted incident. Stage B: fed by the real `/traffic/prediction` response (`17_API_SPECIFICATION.md`).

## 10. Strategy Selection UI (Step 10)

```csharp
// Scripts/UI/StrategyPanel.cs
public enum StrategyType { GreenExtend, Diversion, DynamicLane, EmergencyPriority, DoNothing }
public struct StrategyOption { public StrategyType type; public string label; public Dictionary<string,float> parameters; }
public class StrategyPanel : MonoBehaviour
{
    public void ShowOptions(List<StrategyOption> options);
    public event Action<StrategyOption> OnStrategySelected;
    public event Action OnSimulateRequested; // maps to [SIMULATE] button
}
```
`StrategyType` values must exactly match the backend's `strategy_type` strings (`27_SCENARIO_ENGINE.md`) — again, define this enum's string mapping once in a shared config, not independently in C# and Python.

## 11. Digital Twin Visualization / Ghost Futures (Step 11)

Implements `DESIGN_GUIDELINES.md` §20 and §36.

```csharp
// Scripts/Traffic/DigitalTwinSimulationView.cs
public class DigitalTwinSimulationView : MonoBehaviour
{
    public void EnterSimulationMode();  // desaturate world, freeze current state
    public void ShowGhostFuture(StrategyOption option, GhostTrafficSnapshot snapshot);
    public void ExitSimulationMode();   // return to normal, apply chosen future
}
```

**Stage A (MVP)**: `GhostTrafficSnapshot` is a small hand-authored set of alternate vehicle positions/speeds per strategy (enough to visually sell "here's what would happen"). **Stage B**: `GhostTrafficSnapshot` is populated from the real `/strategy/evaluate` response (`17_API_SPECIFICATION.md`), rendering the Scenario Engine's actual simulated metrics as ghost vehicles.

## 12. Counterfactual Cards (Step 12)

```csharp
// Scripts/UI/CounterfactualCardPanel.cs
public struct ScenarioResultDisplay
{
    public StrategyType type;
    public string label;           // "FUTURE B — DIVERSION"
    public float delayDeltaPct;    // -31
    public bool isBest;            // drives #39E75F highlight border
}
public class CounterfactualCardPanel : MonoBehaviour
{
    public void ShowResults(List<ScenarioResultDisplay> results);
}
```
Card layout, spacing, and the "★ BEST" highlight rule come directly from `DESIGN_GUIDELINES.md` §21 — do not restyle ad hoc here.

## 13. Explanation Panel (Step 13)

```csharp
// Scripts/UI/ExplanationPanel.cs
public struct Explanation { public string action; public string reason; public Dictionary<string,string> evidence; public float confidence; }
public class ExplanationPanel : MonoBehaviour { public void Show(Explanation e); }
```
Fixed four-field template only — `ACTION / WHY / EVIDENCE / CONFIDENCE`, exactly mirroring `37_EXPLAINABLE_AI.md` and `DESIGN_GUIDELINES.md` §24. **Do not let this panel invent language beyond what the backend (or, in Stage A, the hardcoded stub) actually provides** — this is a Responsible AI product; the UI must not overstate certainty (`DESIGN_GUIDELINES.md` §49).

## 14. Approve / Reject (Step 14)

```csharp
// Scripts/UI/DecisionButtons.cs
public class DecisionButtons : MonoBehaviour
{
    public event Action OnApprove;
    public event Action OnReject;   // maps to [TRY ANOTHER]
}
```
No `[AI CONTROL]` button exists anywhere in the codebase — this is a hard design constraint from `DESIGN_GUIDELINES.md` §22, worth a code-review checklist item.

## 15. Scoring (Step 15)

```csharp
// Scripts/Scoring/ScoreController.cs
public struct ScoreBreakdown { public int trafficFlow; public int emergencySafety; public int queueControl; public int decisionQuality; public int Total => trafficFlow+emergencySafety+queueControl+decisionQuality; }
public class ScoreController : MonoBehaviour
{
    public ScoreBreakdown Current { get; private set; }
    public void ApplyDecisionOutcome(ScenarioResultDisplay chosen, bool wasAIRecommendation, bool aiWasCorrect);
    public event Action<ScoreBreakdown> OnScoreChanged;
}
```
Also tracks the **AI Trust Score** inputs (`PRD.md` §13): `recommendationsShown`, `recommendationsAccepted`, `acceptedRecommendationsThatWerePositiveOutcome` — reward correctly *rejecting* a bad recommendation, per `DESIGN_GUIDELINES.md` §26.

## 16. End-to-End Scripted Scenario (Step 16 — First Playable Milestone)

Wire steps 4–15 together into one `ScenarioDirector` that runs the exact demo script from `PRD.md` §28 using **only local/stubbed data** (no backend calls yet):

```csharp
// Scripts/Core/ScenarioDirector.cs
public class ScenarioDirector : MonoBehaviour
{
    // Coroutine-driven timeline matching PRD §28:
    // t=0    : normal traffic (Stage A vehicle spawning)
    // t=20   : IncidentTrigger fires (Accident @ J2)
    // t=40   : queue visibly builds
    // t=50   : AIAlertPanel.Show(87% risk)
    // t=60   : StrategyPanel.ShowOptions(4 strategies)
    // (on SIMULATE) : DigitalTwinSimulationView + CounterfactualCardPanel with hardcoded results
    // (on selection): ExplanationPanel.Show(...)
    // (on APPROVE)  : apply chosen ghost future to real vehicles, ambulance clears
    // t=180  : ScoreController shows final breakdown
}
```
**This is the milestone to protect above all others** — a fully playable, hardcoded-data version of the 3-minute demo. Everything after this point (backend wiring, more levels, polish) is additive risk, not a prerequisite for having something to show.

## 17. Backend Integration (Post-MVP-Playable)

Only begin once step 16 is confirmed playable and demoable standalone.

### 17.1 Networking Scripts
```text
Scripts/Network/
├── ApiClient.cs           # REST calls via UnityWebRequest (TECH_STACK.md §13)
├── WebSocketClient.cs     # realtime stream (vehicle state, alerts, incidents)
├── VehicleStateReceiver.cs# parses vehicle_state messages, drives VehicleAgent (Stage B)
└── DTOs.cs                # C# structs mirroring backend JSON exactly
```

### 17.2 API Contract (mirrors `17_API_SPECIFICATION.md` exactly — do not invent parallel endpoints)

| Unity call | Backend endpoint | Direction |
|---|---|---|
| Get current state | `GET /traffic/state` | REST |
| Get forecast | `GET /traffic/prediction` | REST |
| Request recommendation | `GET /recommendation` | REST |
| Evaluate strategies | `POST /strategy/evaluate` | REST |
| Apply chosen strategy | `POST /strategy/apply` | REST |
| Trigger incident (dev/testing) | `POST /incident/trigger` | REST |
| Live vehicle/signal stream | `vehicle_state`, `signal_state`, `incident_event` messages | WebSocket |

### 17.3 WebSocket Message Handling
```csharp
// WebSocketClient.cs routes by "type" field (TECH_STACK.md §14):
switch (message.type) {
    case "vehicle_state": vehicleStateReceiver.Apply(message); break;
    case "signal_state":  junctionRegistry.UpdateSignal(message); break;
    case "incident_event": incidentTrigger.FireFromBackend(message); break;
}
```

### 17.4 Swap Order (Stage A → Stage B, one system at a time)
```text
1. Swap vehicle movement source (VehicleAgent Stage A → Stage B) — verify visually first
2. Swap AIAlertPanel data source (hardcoded → GET /traffic/prediction)
3. Swap StrategyPanel options (hardcoded 4 → generated by backend, still 3-4 count)
4. Swap CounterfactualCardPanel data (hardcoded deltas → POST /strategy/evaluate response)
5. Swap ExplanationPanel data (hardcoded copy → backend Explanation object)
6. Swap incident trigger source (local timer → POST /incident/trigger from procedural generator)
```
**Swap one at a time and re-verify the scripted scenario still plays correctly after each swap** — do not integrate all six simultaneously, since a break in one is much harder to isolate if five other things changed at once.

## 18. Junction/Strategy ID Contract (Shared Config — Build This First, Literally Step 0)

Before any of the above, create one shared reference (duplicated deliberately in both codebases, values kept identical by convention, or generated from a single YAML/JSON if time allows):

```yaml
# shared_config/ids.yaml (reference copy; Unity and Python each read their own generated version)
junctions: [J1, J2, J3]
strategy_types: [green_extend, diversion, dynamic_lane, emergency_priority, do_nothing]
vehicle_types: [car, bus, truck, motorcycle, ambulance, police, fire]
incident_types: [accident, closure, surge, weather, emergency]
```
This single file prevents the single most likely integration bug class: a Unity-side string ("Ambulance") not matching a Python-side string ("emergency") at the exact moment a WebSocket message needs to be parsed live, mid-demo.

## 19. Hour-by-Hour Sequence (8-Hour Round 2 Build)

| Hour | Focus | Milestone |
|---|---|---|
| 0–0.5 | Shared ID config (§18), Unity project scaffold (§2), scene setup | Project opens, empty `Gameplay_J1J2J3` scene loads |
| 0.5–1.5 | Static J1-J2-J3 world (§4), asset import + `ASSETS.md` logging (§5.1) | 3D world visually complete, static |
| 1.5–2.5 | Vehicle prefabs + pooling + Stage A movement (§5.2–5.4), camera (§6) | Vehicles visibly flow through the network |
| 2.5–3.5 | Scripted incident trigger (§7.1), HUD shell (§8), AI Alert panel (§9) | Accident at J2 visibly disrupts traffic; alert appears |
| 3.5–4.5 | Strategy panel (§10), Digital Twin ghost view (§11), counterfactual cards (§12) | Player can open SIMULATE and see 4 ghost futures |
| 4.5–5.5 | Explanation panel (§13), Approve/Reject (§14), Score (§15) | Full decision loop works end-to-end on stubbed data |
| 5.5–6.5 | `ScenarioDirector` timeline (§16) — assemble and rehearse the full 3-minute script | **First fully playable milestone reached** |
| 6.5–7.5 | Backend integration (§17), swapped one system at a time | Live SUMO/XGBoost data replaces stubs, where time allows |
| 7.5–8.0 | Buffer: bug fixes, rehearse demo, fallback to Stage A stub if live integration is unstable | Demo-ready build locked, no further changes |

**Explicit fallback rule**: if Hour 7.5 arrives and live backend integration is not stable, **revert to the Stage A stubbed build from Hour 6.5 for the demo.** A polished, reliable, hardcoded-data demo beats a live-but-fragile one in front of judges — this decision should be made consciously at the 7.5-hour mark, not discovered by a crash during the presentation.

## 20. Definition of Done (Phase 4)

```text
[ ] Shared ID config exists and is used by all Unity scripts referencing
    junctions/strategies/vehicles/incidents (no hardcoded duplicate strings)
[ ] 3-junction 3D world renders at target frame rate (DESIGN_GUIDELINES.md §44)
[ ] Vehicles move, queue, and visually communicate density (§13 of design doc)
[ ] Accident incident visibly disrupts traffic at J2
[ ] AI Alert panel displays a congestion probability
[ ] Player can open strategy options and press SIMULATE
[ ] Digital Twin / ghost future visualization plays for each candidate
[ ] Counterfactual cards show comparative deltas with a highlighted best option
[ ] Explanation panel shows ACTION/WHY/EVIDENCE/CONFIDENCE
[ ] Player can APPROVE or TRY ANOTHER — no AI-auto-control path exists
[ ] Score updates and displays a final breakdown
[ ] The full PRD §28 3-minute scenario plays start to finish without manual intervention
[ ] docs/ASSETS.md is fully populated for every imported asset
```
Phase 4 is complete, and Phase 5 (full backend wiring, if not already done within the 8 hours) may proceed, only once every item above is checked.

## Cross-References
- Product loop this implements: `PRD.md` §5, §9–14, §28
- Frozen technical decisions this respects: `TECH_STACK.md` §2–15
- Visual/UX specification this follows exactly: `DESIGN_GUIDELINES.md` (all sections referenced inline above)
- Backend contract this integrates against: `docs/phase-2-architecture/17_API_SPECIFICATION.md`, `docs/phase-3-digital-twin/27_SCENARIO_ENGINE.md`, `docs/phase-4-ai-intelligence/37_EXPLAINABLE_AI.md`

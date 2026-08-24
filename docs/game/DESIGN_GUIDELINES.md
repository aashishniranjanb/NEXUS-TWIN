# DESIGN_GUIDELINES.md — NEXUS-TWIN
## Game & Visual Design Guidelines v1.0

| Field | Value |
|---|---|
| Product | NEXUS-TWIN: Traffic Crisis Simulator |
| Platform | Unity 6 / URP |
| Primary Experience | 3D strategic traffic-management game |
| Visual Direction | Smart City + Simulation + Responsible AI |
| Primary Accent | `#39E75F` |

This document must be locked **before** Unity implementation begins — it is the single source of truth for color, layout, camera, UI, animation, and language across every screen.

---

## 1. Design Vision

NEXUS-TWIN should look like a real intelligent traffic-control simulation that happens to be playable as a game. It must **not** look like: a racing game, a GTA-style open world, a futuristic cyberpunk game, a generic AI dashboard, an academic traffic simulator, or a photorealistic driving simulator.

Visual identity sits between: **smart-city command center + strategy game + Digital Twin visualization.**

The player must understand, in sequence: *Where traffic is → What is going wrong → What AI predicts → What the player can do → What will happen → Whether the decision worked.*

## 2. Reference Design Language

| Reference | Principle taken | Where it's used |
|---|---|---|
| A — Top-down traffic network | Elevated camera, visible roads, colored vehicles, traffic lights, crossings, network-level visibility | Primary gameplay perspective (§7) |
| B — Before/after optimization | Strong visual comparison, measurable improvement, obvious change after intervention | Results/explanation language (§28) |
| C — Emergency routing | Highlighted route, emergency vehicle, origin/destination, clear visual distinction | Emergency-event mechanic (§17) |

## 3. Core Visual Principle

> **"Readable before beautiful."** A judge should understand the situation within 2–3 seconds.

```text
GAMEPLAY CLARITY → TRAFFIC READABILITY → AI EXPLANATION → VISUAL POLISH
```
Never the reverse order of priority.

## 4. Overall Art Direction

**Style**: stylized low-poly 3D — simplified geometry, clean surfaces, moderate saturation, minimal textures, soft shadows, controlled lighting, clear silhouettes. This also serves performance: Unity's URP guidance recommends actively controlling rendering features, memory, draw calls, shadows, and render scale when optimizing for lower-end platforms — low-poly is a performance decision as much as an aesthetic one.

## 5. Color System

| Color | Hex | Meaning | Use for |
|---|---|---|---|
| Primary Green | `#39E75F` | GOOD / SAFE / APPROVED | Selected strategy, safe route, successful outcome, positive metric, approved decision, emergency corridor, high AI confidence |
| Deep Navy | `#0B1F33` | System / UI | Primary text, panels, navigation, labels, important outlines |
| Blue | `#1677FF` | INFORMATION / SIMULATION | Normal traffic, information, Digital Twin, neutral AI info |
| Cyan | `#22C7D6` | AI / PREDICTION | Predicted traffic, AI visualization, network connections, telemetry, Digital Twin overlays |
| Amber | `#FFB020` | CAUTION | Warnings, moderate congestion, uncertain AI recommendation, attention states |
| Red | `#EF4444` | DANGER (use rarely) | Accident, critical congestion, blocked route, safety violation, emergency failure — only |
| White | `#FFFFFF` | Neutral | Backgrounds |
| Light Gray | `#F3F5F7` | Neutral | Panel backgrounds |
| Gray | `#94A3B8` | Neutral | Secondary text/icons |
| Dark Gray | `#475569` | Neutral | Tertiary text |

**Rule**: green must not be used decoratively — it always means good/safe/approved. Red is reserved for genuine danger states and must stay rare, or its signal value collapses. **Never change these meanings between screens.**

## 6. Color Semantics (Reference Table — pin this near the Unity project)

| Color | Meaning |
|---|---|
| Green | Safe / successful |
| Blue | Normal / information |
| Cyan | AI / prediction / Digital Twin |
| Amber | Warning / uncertainty |
| Red | Critical / danger |
| White | Neutral |
| Navy | System / UI |

## 7. World Camera

Primary: **elevated 3/4 top-down strategy camera**, not fully vertical. Target angle: **45–60°**. The player must simultaneously see road layout, vehicles, signals, queues, emergency routes, and junction relationships from this single default view.

## 8. Camera Modes

| Mode | Behavior |
|---|---|
| 1 — Strategic (default) | Shows J1 → J2 → J3 |
| 2 — Incident Focus | Auto-moves toward accident/congestion/emergency |
| 3 — Simulation | Zooms slightly outward to show multiple counterfactual futures |
| 4 — Emergency Follow | Temporarily follows ambulance/fire truck/police vehicle |

## 9. World Layout

```text
             NORTH
               ↑
        ───── J1 ─────
              │
        ───── J2 ─────
              │
        ───── J3 ─────
               ↓
             SOUTH
```
Three junctions are sufficient for MVP (matches `10_SCOPE_AND_NON_SCOPE.md`). **Do not build an enormous city.**

## 10. Roads

Include: clear lane markings, sidewalks, crosswalks, traffic lights, turning lanes, lane arrows, road boundaries. Avoid excessive environmental detail — **the road network is the game board**, not scenery.

## 11. Vehicles (MVP Roster)

| Vehicle | Role |
|---|---|
| Car | Neutral everyday traffic |
| Bus | Larger vehicle, slower acceleration |
| Truck | Heavy vehicle, affects flow more per unit |
| Motorcycle | Smaller vehicle class |
| Ambulance | Highest visual priority during emergency scenarios |
| Police / Fire | Optional, advanced scenarios |

Models should be low-poly but immediately recognizable by silhouette alone.

## 12. Vehicle Color Rules

Do **not** use random rainbow colors for gameplay-critical states — the environment communicates congestion, not vehicle paint.

| Vehicle | Color |
|---|---|
| Cars | Neutral colors |
| Buses | Blue/white |
| Trucks | Gray |
| Motorcycles | Dark neutral |
| Ambulance | White/red |
| Police | White/blue |
| Fire truck | Red |

## 13. Traffic Density Visualization

| State | Visual |
|---|---|
| Normal | Vehicles spaced apart |
| Moderate | Vehicles begin clustering |
| Heavy | Vehicles form obvious queues |
| Critical | Long queues spilling into upstream junctions |

## 14. Queue Visualization

Subtle overlay, not dominant graphics:
```text
GREEN  ──────
AMBER  ████──
RED    ████████
```
Or a glowing road-edge indicator. **Avoid giant red roads** — the player should still see the actual traffic underneath.

## 15. Traffic Lights

Must be visually obvious at a distance: RED / AMBER / GREEN discs, with optional subtle glow, a state icon, and remaining time (e.g., "GREEN — 18s").

## 16. Emergency Vehicle

The ambulance is a major gameplay element: recognizable silhouette, red emergency markings, flashing lights, siren, high visual priority. On emergency trigger, show `🚑 AMBULANCE DETECTED` then highlight its route immediately.

## 17. Emergency Route

Visually distinct from normal roads: **green + subtle cyan glow**, not red.
```text
🚑
 ╲
  ╲━━━━━━━━━━► HOSPITAL
```

## 18. Accident Visualization

Show a damaged/disabled vehicle, hazard cones, a warning icon, a flashing amber/red marker, and a blocked lane. The accident must **visibly** affect traffic flow — not just appear as a decorative icon.
```text
       ⚠  ACCIDENT
🚗  🚙  🚧
────────────
```

## 19. AI Visualization

No giant floating robot. Use a compact intelligence panel:
```text
┌───────────────────────────┐
│ AI TRAFFIC ANALYSIS       │
│ J2 CONGESTION RISK        │
│         87%                │
│ Forecast: 5 min            │
└───────────────────────────┘
```

## 20. Digital Twin Visualization

On entering simulation mode: slightly desaturate the world, then show `CURRENT → DIGITAL TWIN → COUNTERFACTUAL FUTURES`. Use cyan/blue for all simulation overlays, consistently.

## 21. Counterfactual UI

```text
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ FUTURE A     │  │ FUTURE B     │  │ FUTURE C     │
│ GREEN +20s   │  │ DIVERSION    │  │ DYNAMIC LANE │
│ Delay -18%   │  │ Delay -31%   │  │ Delay -12%   │
│              │  │ ★ BEST       │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```
The best strategy always gets the `#39E75F` border/highlight — consistent with the color semantics table (§6).

## 22. Player Decision UI

The player must always feel: **"I am making the decision."**

Primary buttons: `[ SIMULATE ]` `[ APPROVE ]` `[ REJECT ]` `[ TRY ANOTHER ]`.
**Never** include a button labeled `[ AI CONTROL ]` — it undermines the human-in-the-loop concept that is the product's core positioning.

## 23. AI Recommendation Panel

```text
┌───────────────────────────────┐
│ AI RECOMMENDATION              │
│ DIVERT TRAFFIC                │
│ Confidence     84%            │
│ Queue          -28%           │
│ Delay          -31%           │
│ Spillback      LOW            │
│ Emergency      SAFE           │
│ [ APPROVE ]  [ TRY ANOTHER ] │
└───────────────────────────────┘
```

## 24. Explainability Structure

Every AI recommendation answers, in this exact order:
```text
WHAT?      Divert traffic.
WHY?       Reduces downstream queue accumulation.
EVIDENCE?  Queue: -28% · Delay: -31% · Speed: +11% · Emergency route: SAFE
CONFIDENCE? 84%
```
This mirrors the fixed four-field template already frozen in `37_EXPLAINABLE_AI.md` — do not invent a different explanation shape for the UI than the one the backend produces.

## 25. AI Confidence Indicator

```text
0% ─────────────── 100%
          ████████
             84%
```
Color banding: **0–50 → amber/red · 50–75 → amber · 75–100 → green.**

**Language rule**: confidence must never be presented as "AI is guaranteed correct." Always label it explicitly as **"Model confidence."**

## 26. Player Trust Score

```text
AI TRUST
████████░░ 82%
```
This is derived from gameplay **outcomes**, not click frequency — a player who correctly *rejects* a bad AI recommendation should be rewarded, not penalized for "not trusting the AI." Get this scoring rule right; it is the mechanical heart of the Responsible AI positioning (`PRD.md` §13).

## 27. Score Display

```text
NETWORK SCORE
       93
Breakdown:
Traffic Flow      +32
Emergency Safety  +30
Queue Control     +18
Decision Quality  +13
TOTAL              93
```
Visible but not dominant — the score is a summary, not the focal point of the screen.

## 28. Before/After Visualization

```text
BEFORE                    AFTER
QUEUE  ██████████         QUEUE  ███
DELAY  42 sec              DELAY  29 sec
SPEED  28 km/h              SPEED  39 km/h
```
Use green for improvements. This gives the judge immediate, legible proof that the player's decision mattered — it is the single highest-leverage visual in the whole product for a 3-minute demo.

## 29. Gameplay HUD (Four Zones Only)

```text
┌──────────────────────────────────────────────┐
│ TIME        TRAFFIC       SCORE       LEVEL  │
│                3D CITY                        │
│ AI ALERT                 ACTIONS             │
│ J2: 87%                  [SIMULATE]          │
└──────────────────────────────────────────────┘
```
**Never cover the central road network with UI.**

## 30. Typography

| Role | Font |
|---|---|
| Primary | Inter |
| Secondary | Roboto |
| Numbers | Inter SemiBold / Bold |

Avoid: serif fonts, handwritten fonts, futuristic/"gaming" fonts. The product should read as an engineering product, not a fantasy game.

## 31. Iconography

Simple line/filled vector icons, required set: traffic light, car, bus, truck, motorcycle, ambulance, accident, warning, AI, simulation, route, check, cross, clock, queue, speed. Maintain consistent stroke width, corner radius, and visual weight across the entire set — mixed icon styles read as unfinished.

## 32. Reusable UI Components (Unity Prefabs)

```text
UIPanel · UIButton · MetricCard · AIAlert · StrategyCard
ConfidenceBar · ScoreCard · VehicleStatus · EmergencyAlert
SimulationResult · ExplanationPanel
```
Build these once as prefabs; do not hand-design each screen independently — this is both a design-consistency rule and a build-time-efficiency rule for the 8-hour window.

## 33. Panel Design Spec

White/very light gray background, 8–16px corner radius, subtle shadow, navy text, green/blue accent border.
```text
┌──────────────────────────┐
│ AI ANALYSIS              │
│ J2 → HIGH RISK           │
│ █████████░ 87%           │
└──────────────────────────┘
```

## 34. Animation Principles

Animation communicates **state**, not decoration:

| Event | Animation |
|---|---|
| Traffic | Smooth movement |
| Congestion | Vehicles slow and accumulate |
| Accident | Warning pulse |
| AI prediction | Subtle scan/pulse |
| Simulation | Ghost/transparent vehicles |
| Successful action | Green route pulse |
| Failure | Red/amber warning pulse |

## 35. Digital Twin Mode Animation Sequence

```text
1. Freeze current state
2. Slightly fade the environment
3. Display simulation branches
4. Run ghost traffic
5. Show metric changes
6. Return to player decision
```
This sequence is what makes the Digital Twin feel like an actual game mechanic rather than a hidden backend process — it should not be skipped or shortcut even under time pressure, since it is the visual proof of the product's core novelty.

## 36. "Ghost Future" Visualization

```text
CURRENT WORLD
       ├──── FUTURE A
       ├──── FUTURE B ★
       ├──── FUTURE C
       └──── FUTURE D
```
Ghost vehicles: semi-transparent, cyan/blue, slightly desaturated. The player sees what *could* happen before committing — this is the direct visual analog of the clone-simulate-discard pattern in `13_DIGITAL_TWIN_ARCHITECTURE.md`.

## 37. Multi-Agent Visual Language (Future)

Do **not** represent agents as six giant AI characters. Represent them as small system modules with status indicators:
```text
● Perception       READY
● Prediction       87%
● Strategy         4 OPTIONS
● Simulation       COMPLETE
● Safety           PASS
● Explanation      READY
```
This preserves the engineering aesthetic even once multi-agent orchestration (Phase 2, `TECH_STACK.md` §16–21) is added.

## 38. Game States

```text
STATE_01_IDLE      STATE_02_EVENT       STATE_03_ANALYSIS
STATE_04_DECISION  STATE_05_SIMULATION  STATE_06_EXPLANATION
STATE_07_APPROVAL  STATE_08_RESULT      STATE_09_SCORE
```
Never mix all states simultaneously — one state owns the screen at a time.

## 39. State Color Logic

| State | Color |
|---|---|
| Idle | Blue/neutral |
| Warning | Amber |
| Critical | Red |
| Simulation | Cyan |
| Approved | Green |
| Failed | Red |

## 40. Lighting

Day lighting is the default hackathon demo mode; evening is an optional advanced mode. Avoid heavy bloom, fog, volumetric lighting, and reflections — **the game is about traffic intelligence, not a graphics benchmark.**

## 41. Shadows

Use lightweight shadows, prioritized on vehicles, traffic lights, and major buildings only. Unity's current URP guidance specifically recommends reducing shadow resolution/distance and limiting additional-light shadows for performance-sensitive builds — apply that guidance here rather than enabling shadows universally.

## 42. Environment

Low-poly buildings, trees, sidewalks, street lights, signs, barriers — all visually **secondary**. Enforced hierarchy:
```text
TRAFFIC → PLAYER DECISION → AI → ENVIRONMENT
```

## 43. Asset Rules

**Technical**: low-poly, correct scale, clean mesh, no unnecessary materials, no oversized textures.
**Legal**: every imported asset logged with `Asset, Creator, Source, License, URL, Modification` in `docs/ASSETS.md`. Note the SUMO2Unity precedent explicitly: its integration code is MIT-licensed, but its bundled example assets are CC-BY (attribution required) — license tracking must happen per-asset, not per-project.

## 44. Performance Budget

| Target | Desktop | Web/Mobile |
|---|---|---|
| Goal | 60 FPS | Stable frame rate prioritized over graphical quality |
| Minimum | 30 FPS | 30 FPS |

Unity's guidance is to profile CPU/GPU usage and reduce render textures, passes, draw calls, shadows, and render scale as needed — treat this as an active budget to check against, not a one-time setting.

## 45. Vehicle Rendering Strategy

Do **not** instantiate/destroy thousands of high-detail GameObjects at runtime.
```text
SUMO vehicle state → Vehicle Manager → Object Pool → Reusable vehicle prefabs
```

## 46. Traffic Rendering Strategy

SUMO remains authoritative; Unity is a visual representation only:
```text
SUMO (position, speed, lane, signal, route) → Unity (visual rendering)
```
This follows the same co-simulation approach used by SUMO2Unity (`TECH_STACK.md` §11) — position/signal sync, not physics duplication.

## 47. UI Accessibility

Never rely on color alone.

| Weak | Better |
|---|---|
| Green = safe | ✓ SAFE (icon + green) |
| (implicit warning) | ⚠ WARNING (icon + amber) |
| (implicit danger) | ✕ CRITICAL (icon + red) |

This also directly supports the Responsible AI framing — an accessible interface is part of a trustworthy one.

## 48. Text Rules

Keep UI text short.

**Good**: "87% congestion risk"
**Bad**: "The artificial intelligence model has determined that there is an 87 percent probability..."

Reserve detailed/technical explanation for an expandable panel, not the primary HUD.

## 49. AI Language Rules (Responsible AI — Non-Negotiable)

The AI must never claim certainty it does not have.

| Avoid | Use instead |
|---|---|
| "This action will eliminate congestion." | "Predicted to reduce queue length by 28%." |
| "This is definitely the safest option." | "Lowest simulated safety risk among evaluated strategies." |

This rule directly enforces the honesty principle already established in `20_SECURITY_ETHICS.md` and `37_EXPLAINABLE_AI.md` — the UI copy must not overstate what the backend actually computed.

## 50. Game Feedback

Every meaningful player action produces immediate, visible feedback:
```text
PLAYER APPROVES DIVERSION → TRAFFIC CHANGES → QUEUE ↓28% → SCORE +17
```
The player must never wonder "did my decision actually do anything?"

## 51. Failure Design

Failure is part of the game, not a dead end:
```text
⚠ DECISION RESULT
Queue spillback increased
Emergency response delayed
-18 SCORE
```
Followed immediately by a `SIMULATE ANOTHER` prompt — this encourages learning rather than pure punishment.

## 52. Learning Mechanic

```text
Predict → Question → Simulate → Compare → Decide → Observe → Learn
```
This loop is the strongest link between gameplay and Responsible AI messaging — every screen should reinforce some part of it.

## 53. Main Menu

```text
NEXUS-TWIN
TRAFFIC CRISIS

[ PLAY ]
[ TRAINING ]
[ HOW AI DECIDES ]
[ SETTINGS ]
```
No elaborate animated intro — get the player into the loop quickly.

## 54. Training Mode (Under One Minute)

```text
1. "Traffic is building at J2."
2. "AI predicts 82% congestion probability."
3. "Test two strategies."
4. "Choose the better future."
5. "Approve."
   → Finished.
```

## 55. Game Result Screen

```text
        BEFORE              AFTER
QUEUE   ██████████          ████
DELAY   48 sec              31 sec
SPEED   26 km/h             38 km/h

         + FINAL SCORE +
               91

Emergency route preserved
```

## 56. Research/Developer Mode (Hidden)

Not player-facing. Displays: Simulation Seed, Model Version, Prediction Confidence, Strategy, Scenario ID, SUMO Step, Latency, Queue MAE. Useful for experiments, the eventual paper, reproducibility, debugging, and judge Q&A — but never shown to the normal player.

## 57. Web Build Design Constraints

Reduce texture sizes, avoid heavy shaders, limit particle effects, reduce scene complexity, use compressed assets, load asynchronously, avoid a large initial download. Unity's current optimization documentation includes Web-specific profiling and performance guidance for Unity 6 — apply it before assuming the desktop build "just works" in a browser.

## 58. Android Design Constraints (Future)

Touch-first controls, larger buttons, reduced shadow quality, lower render scale where required, fewer simultaneous vehicles, simplified environment, no unnecessary post-processing. The game must remain playable without requiring a high-end phone.

## 59. Desktop Design Spec (Primary Hackathon Target)

Resolution: **1920 × 1080**.
```text
WASD / Arrow Keys → Camera    Mouse    → Select
Scroll             → Zoom     Left Click → Interact
Space              → Pause    ESC        → Menu
```

## 60. Design Don'ts

```text
✗ Neon cyberpunk city
✗ Giant AI robot
✗ Excessive particle effects
✗ Giant text everywhere
✗ Random colors
✗ Photorealistic assets mixed with low-poly assets
✗ Ten different UI styles
✗ AI automatically controlling everything
✗ UI covering the traffic network
✗ Fake metrics
✗ Decorative AI explanations not linked to real simulation results
```

## 61. Design Must-Haves

```text
✓ Top-down 3D traffic            ✓ Clear junctions
✓ Cars / buses / bikes           ✓ Ambulance
✓ Traffic lights                 ✓ Incident visualization
✓ AI prediction                  ✓ Strategy cards
✓ Counterfactual futures         ✓ Explainability
✓ Human approval                 ✓ Before/after metrics
✓ Score                          ✓ Clear failure/success states
✓ Consistent color semantics
```

## 62. Final Visual Identity Statement

```text
REAL WORLD → TRAFFIC → AI SEES → AI PREDICTS → DIGITAL TWIN TESTS
→ AI EXPLAINS → HUMAN CHOOSES → TRAFFIC CHANGES → SCORE
```
Visually: **clean smart-city simulation, not flashy gaming.**

## 63. Final Design Direction (Synthesis)

The three references merge into one experience: top-down 3D traffic world (Ref. 1) + before/after measurable optimization (Ref. 2) + emergency route/vehicle priority (Ref. 3), plus NexusTwin's unique layer (AI prediction + counterfactual Digital Twin + explainability + human decision).

> **"A playable Digital Twin where you see the consequences of an AI decision before you commit it."**

This is the design rule for every screen, asset, animation, and UI component built from this point forward — if a proposed screen or effect doesn't serve this sentence, cut it.

## Cross-References
- Product/gameplay requirements this design serves: `PRD.md` (this folder)
- Technical constraints this design must respect: `TECH_STACK.md` (this folder)
- Underlying explanation data model: `docs/phase-4-ai-intelligence/37_EXPLAINABLE_AI.md`
- Ethics/language principles this enforces: `docs/phase-2-architecture/20_SECURITY_ETHICS.md`

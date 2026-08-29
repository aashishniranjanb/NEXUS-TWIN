# PRD — NEXUS-TWIN Command Center

| Field | Value |
|---|---|
| Document | Product Requirements |
| Status | Level-1 (authoritative) |
| Owner | Laptop 3 (Frontend / Integration) |
| Depends on | `00_MASTER_PROJECT_SPEC.md` |

---

## 1. Purpose

Define exactly what NEXUS-TWIN does, panel by panel and interaction by interaction, so that three
people building in parallel produce one coherent product.

## 2. Scope

This document covers the Command Center product surface and the behaviour behind it. It does not
cover visual styling, model internals, or API payload shapes; those live in the frontend, AI, and
API documents respectively.

---

## 3. Users

| Persona | Goal | What they need from the product |
|---|---|---|
| Traffic operator (primary) | Prevent congestion spreading across the corridor | To know what is happening, what happens next, how long they have, and what the options cost |
| Traffic analyst | Understand why the system recommended something | Evidence, confidence, trade-offs, and the ability to test an alternative |
| Judge (evaluation persona) | Assess whether the AI is real | Visible dataset provenance, consistent numbers, and a decision that changes the outcome |

## 4. Core workflow

```
TRAFFIC DATA
     -> CURRENT STATE
     -> ANOMALY
     -> TRAFFIC FINGERPRINT
     -> PREDICTION
     -> DOMINO EFFECT
     -> INTERVENTION WINDOW
     -> AI STRATEGIES
     -> DIGITAL TWIN
     -> COMPARISON
     -> EXPLAINABLE RECOMMENDATION
     -> HUMAN DECISION
     -> OUTCOME
```

Each stage consumes the previous stage's output. No stage may be a decoration: if a panel cannot
be driven by the stage before it, the panel is cut.

---

## 5. Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ NEXUS-TWIN · TRAFFIC COMMAND CENTER │ LIVE │ GEOTAB · TWIN · SYSTEM  │
├───────────────────────────────────────┬──────────────────────────────┤
│                                       │  CURRENT TRAFFIC STATE       │
│                                       │  TRAFFIC FINGERPRINT         │
│         J1 — J2 — J3 MAP              │  AI FORECAST (5 MIN)         │
│         (60–65% width)                │  CONGESTION DOMINO EFFECT    │
│                                       │  INTERVENTION WINDOW         │
│                                       │  AI DECISION COPILOT         │
│                                       │  STRATEGIES / TWIN / DECISION│
├───────────────────────────────────────┴──────────────────────────────┤
│ 01 NORMAL · 02 ANOMALY · 03 FINGERPRINT · … · 09 OUTCOME             │
└──────────────────────────────────────────────────────────────────────┘
```

Header right shows three indicators: `GEOTAB DATA`, `DIGITAL TWIN`, `SYSTEM STATUS`. Each is a
real health signal, not a static badge.

---

## 6. Requirements by panel

Priority key: **M** = must have, **S** = should have, **O** = optional, **F** = future.

### 6.1 Traffic map — M

| Req | Description |
|---|---|
| MAP-1 | Render J1, J2, J3, the connecting links, and lane geometry for the corridor. |
| MAP-2 | Colour each junction by state: NORMAL green, WARNING amber, CRITICAL red. Demo baseline is J1 WARNING, J2 CRITICAL, J3 NORMAL. |
| MAP-3 | Animate vehicles continuously; density increases visibly as the scenario escalates. |
| MAP-4 | Animate traffic signal phases per junction. |
| MAP-5 | Render congestion originating at J2 and propagating along links toward J1 and J3. |
| MAP-6 (S) | Highlight the ambulance corridor when Emergency Corridor mode activates (P1). |

### 6.2 Current traffic state — M

Metrics: traffic density (%), average speed (km/h), queue length (m), waiting time (s), flow
(veh/min). Values update as the scenario progresses; static numbers across the whole demo are a
defect. Each metric shows a delta against the baseline.

### 6.3 Traffic fingerprint — M

The product does not say "anomaly detected". It classifies the abnormality.

| Field | Example |
|---|---|
| Type | `INCIDENT_LIKE` |
| Confidence | 91% |
| Supporting signals | speed deviation, waiting-time deviation, queue growth, flow anomaly, direction imbalance |

Classes: `NORMAL`, `RECURRING_CONGESTION`, `INCIDENT_LIKE`, `DEMAND_SURGE`, `SIGNAL_RELATED`,
`UNKNOWN`. The panel shows which signals fired and their magnitude — a bare label is not
acceptable.

### 6.4 AI forecast — M

Horizon: 5 minutes. Shows congestion probability, predicted queue, predicted average speed, and
model confidence. Current and predicted values must be visually distinct; a judge should never
have to ask which number is the forecast.

### 6.5 Congestion domino effect — M

The strongest visual element in the product. Shows where congestion is expected to propagate, not
merely that J2 is congested.

| Element | Requirement |
|---|---|
| Source | J2, 87% |
| Propagation | J1 73% in 4 min; J3 41% in 7 min |
| Visualisation | Animated arrows along real links, risk percentage, time-to-impact, affected-junction highlight |
| Ordering | Neighbours ranked by risk descending |

### 6.6 Intervention window — M

Converts prediction into a time constraint: status (`CRITICAL` / `WARNING` / `CLEAR`), remaining
time, expected consequence, recommended urgency. The countdown is derived from the earliest
spillover ETA minus strategy application lead time — not a decorative timer.

### 6.7 AI Decision Copilot — S (P1 for chat; M for the four-answer summary)

Answers four fixed questions: what is happening, what will happen next, what should we do, why.
The summary version is templated from real tool outputs and is a P0 requirement. Free-form chat
is P1 and may be cut without affecting the demo.

### 6.8 Strategy generation — M

Three named candidates plus a `do_nothing` baseline:

| ID | Strategy | Type |
|---|---|---|
| A | Divert traffic | `diversion` |
| B | Extend green | `green_extend` |
| C | Emergency priority | `emergency_priority` |
| — | Do nothing | `do_nothing` |

Each shows predicted queue, network delay, spillover risk, emergency ETA, and overall score. The
product never labels one option "best" without showing the numbers that make it best.

### 6.9 Digital Twin — M

Trigger: `SIMULATE STRATEGIES`. Simulates the same traffic state under each candidate and returns
comparable metrics: queue, average delay, spillover risk, emergency ETA, network score. The UI
transitions between future states rather than swapping a table silently. Results highlight best
overall, best emergency outcome, and lowest spillover — which may be three different strategies.

### 6.10 Explainable recommendation — M

Five sections: recommended action, evidence, confidence, trade-offs, safety check. Every evidence
line is a number that appears elsewhere in the UI. If the recommendation cites "J1 spillover
probability 73%", the domino panel must also read 73%.

### 6.11 Human decision — M

Three actions: `APPROVE AI PLAN`, `OVERRIDE`, `COMPARE HUMAN PLAN`.

- Approve: apply the strategy, run the outcome, show the score and before/after.
- Override: pick a different strategy, see the trade-off explained, evaluate it, and compare AI
  versus human result.

Principle: **AI recommends. The Digital Twin evaluates. The human decides.** The interface must
never imply the AI has authority it does not have.

### 6.12 Crisis timeline — M

Nine states, `01 NORMAL` through `09 OUTCOME`, advancing as the scenario progresses. The current
state is unambiguous at a glance from across a room.

### 6.13 Dataset provenance — M

A visible but non-intrusive indicator showing the source (BigQuery-Geotab Intersection Congestion
Dataset) and the pipeline stages it feeds. Expanding it shows which model consumes which columns.

---

## 7. Interaction rules

| Rule | Detail |
|---|---|
| No dead buttons | Every control produces visible feedback within 200 ms |
| No infinite loading | Every async surface has a timeout and a fallback state |
| No unexplained metrics | Every number has a unit and a tooltip naming its source |
| Determinism | The same demo run produces the same numbers after a browser refresh |
| Readability | Legible at 1920×1080 and 1366×768 |

---

## 8. Dependencies

Backend endpoints in `04_API/API_SPECIFICATION.md`; shared types in
`04_API/API_DATA_CONTRACTS.md`; model behaviour in `06_AI/`. The frontend consumes a provider
abstraction with `DEMO` and `LIVE` modes and must not know which is active.

## 9. Failure modes

| Failure | Product behaviour |
|---|---|
| Endpoint unavailable | Panel renders from the deterministic demo fixture; provenance badge switches to `DEMO` |
| Simulation partial | Show completed strategies, mark the rest `unavailable`, keep comparison usable |
| Slow response | Skeleton state for up to 3 s, then fixture |
| Contradictory data | Panels render what they received; the mismatch is a test failure, never silently smoothed |

## 10. Testing

Playwright walks all nine timeline states and asserts that fingerprint confidence, prediction
risk, domino risks, and recommendation evidence are numerically consistent across panels. Vitest
covers each panel rendering from a fixture. Contract tests assert the fixtures match the schema.

## 11. Acceptance criteria

1. All **M** requirements implemented and reachable from a single Command Center session.
2. Demo completes end to end with the backend stopped.
3. Cross-panel numeric consistency verified by an automated test.
4. Timeline reaches `09 OUTCOME` with before/after deltas populated.
5. Override path produces a measurably different outcome from approve.

## 12. Future work

Multi-corridor selection, historical replay of past incidents, operator accounts and audit
history, mobile-responsive layout, live Geotab streaming.

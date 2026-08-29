# JUDGE DEMO SCRIPT

| Field | Value |
|---|---|
| Status | Level-1 (authoritative) |
| Owner | Laptop 3 |
| Duration | 5 minutes |
| Scenario | J2 Incident — Prevent the Domino |

---

## 1. Purpose

Fix what is said, shown, and clicked, so the demo is rehearsed rather than improvised. This
document is written before the UI is finished, because the script determines what the UI must
show.

## 2. The story

```
Detect -> Understand -> Predict -> Forecast spread -> Generate strategies
      -> Simulate -> Compare -> Human decision
```

One coherent narrative. Not a feature tour. Every click advances the same story.

## 3. Setup

| Item | State |
|---|---|
| Browser | Full screen, one tab, zoom 100% |
| Mode | `LIVE` if the backend is healthy; otherwise `DEMO` — the demo is identical either way |
| Scenario | Reset to step 0 |
| Backup | Second machine with the same build, at the same state |
| Recording | A screen recording of a successful run, ready to play if the machine fails |

Reset and reload once before the judges arrive. The first render after a build is always the
slowest.

---

## 4. Script

### 0:00 — The gap

> "Traffic systems tell us where congestion is. That is useful, and it is not enough. By the time
> three intersections are red, the intervention that would have prevented two of them has already
> expired."

*Command Center visible. Corridor calm. Provenance indicator reads BigQuery-Geotab.*

### 0:20 — The claim

> "NEXUS-TWIN asks what happens next. This is a real corridor — three intersections from the
> Geotab dataset, with their real coordinates and their historical traffic baselines."

*Point at the provenance indicator. Expand it briefly.*

### 0:40 — Detection

*Advance to step 1.*

> "Something is developing at J2. Queue is growing, speed is dropping, waiting time is climbing.
> A conventional system stops here and says 'congestion detected'."

*Current State panel metrics moving, deltas against baseline visible.*

### 1:00 — Traffic fingerprint

*Advance to step 2.*

> "We classify it. This is incident-like, 91% confidence — and here is why: sharp speed drop,
> rapid queue growth concentrated on one approach, and discharge below expectation. A demand surge
> would show flow going up. This shows flow going down while the queue grows. That distinction
> decides whether we extend green or divert."

*Point at the signal bars. This is the first thing they have not seen elsewhere — let it land.*

### 1:20 — Prediction

*Advance to step 3.*

> "Five-minute forecast: 87% probability of severe congestion at J2, predicted queue 156 metres.
> Trained on Geotab features with a leakage-safe split."

*Current and predicted values side by side.*

### 1:40 — The domino effect

*Advance to step 4.*

> "Now the part conventional systems do not do. J2 is not an isolated point — it is a node. The
> queue is going to reach back into J1 in about four minutes, at 73% risk. J3 sees flow disruption
> at 41%, seven minutes out. The ETA is physical: it is how long the growing queue takes to
> consume the remaining storage on the link between them."

*Animated arrows. Pause here. This is the strongest visual in the product.*

### 2:00 — The intervention window

> "So the third question, the one nobody asks: when? Six minutes. That is how long there is to act
> before spillover reaches J1, after allowing a minute to decide and apply."

*Countdown visible, status CRITICAL.*

### 2:20 — Strategies

*Advance to step 5.*

> "Three candidate interventions plus doing nothing, drawn from a constrained catalogue. The AI
> does not invent traffic control actions — every option here is something an operator can
> actually authorise, and every option is testable."

### 2:50 — The Digital Twin

*Click SIMULATE STRATEGIES. Advance to step 6.*

> "Before recommending anything, we test it. Each strategy runs in the Digital Twin from the same
> state, same horizon, same seed. Diversion: queue down 41%, spillover risk down from 0.73 to
> 0.21. Green extension helps J2 and pushes queue into J1 — the model catches that, and it costs
> the strategy points."

*Comparison table with deltas. Note the three winner categories.*

### 3:30 — Recommendation

*Advance to step 7.*

> "The recommendation is divert, 89% confidence. Here is the evidence — and every one of these
> numbers appears elsewhere on this screen. Here is the trade-off: eight percent more delay on the
> alternate corridor. And here is the safety check: emergency access preserved, no junction made
> worse."

*Read one evidence line, then point to the same number in the panel above it.*

### 4:00 — Human override

*Click OVERRIDE, select EXTEND GREEN.*

> "The operator disagrees. The system evaluates their plan too, and shows what it costs: J2
> improves, J1 gets worse, spillover risk goes up. AI recommends. The Digital Twin evaluates. The
> human decides — and either way the decision is recorded with its evidence."

*Then return to APPROVE, or leave the override in place and let the outcome show the difference.*

### 4:30 — Outcome

*Advance to step 8.*

> "Before and after: queue down 42%, delay down 36%, spillover prevented."

### 5:00 — Close

> "Where is the problem, what happens next, when must we act, what should we do, and why. Most
> traffic systems answer the first. NEXUS-TWIN answers all five, and hands the decision to a
> human."

---

## 5. Anticipated questions

| Question | Answer |
|---|---|
| "Is the Geotab data actually used?" | Show `/api/provenance`, then offer the dependency test: delete the baselines and the anomaly confidence collapses. Offer to run it. |
| "Are these numbers hardcoded?" | Change the scenario step and show every panel change consistently. Show the mode badge. Explain that DEMO fixtures are generated from the same scenario definition the backend uses. |
| "Is this just an LLM narrating?" | The LLM computes nothing. Show the tool contracts. Every number comes from XGBoost, Isolation Forest, NetworkX, or the simulator. |
| "Is the vehicle animation real data?" | No — stated plainly. The dataset is aggregated percentiles, not a live feed. Vehicles are simulated; junctions, baselines, models, and graph are Geotab-derived. |
| "How accurate is the prediction?" | Quote the held-out F1 from `results/model_metrics.json`. Show the file. |
| "What if the backend fails?" | It already might be off. Show the mode badge. |
| "Why only three junctions?" | Deliberate scope: one corridor working completely, rather than a city partially. The graph model generalises; the timebox did not. |

Answering "no, that part is simulated" costs nothing and buys credibility for everything else. A
judge who catches an overclaim discounts the whole demo.

## 6. Failure recovery

| Failure | Action |
|---|---|
| Backend dies mid-demo | Say nothing; DEMO mode takes over automatically |
| Frontend crashes | Reload; the scenario step is in the URL |
| Machine dies | Switch to the backup machine, already at the same state |
| Both machines fail | Play the recording and narrate over it |
| A panel shows the wrong number | Acknowledge it, state the correct source, continue — do not improvise an explanation |

## 7. Timing discipline

| Segment | Budget |
|---|---|
| Setup and framing | 0:00–0:40 |
| Detect and understand | 0:40–1:20 |
| Predict and forecast spread | 1:20–2:20 |
| Strategies and simulation | 2:20–3:30 |
| Recommendation and decision | 3:30–4:30 |
| Outcome and close | 4:30–5:00 |

If running long, cut the override demonstration. Never cut the fingerprint or the domino effect —
they are the reason the project is not a dashboard.

## 8. Rehearsal

| Requirement | Count |
|---|---|
| Full runs on demo hardware | 3 minimum |
| Runs with the backend off | 1 minimum |
| Runs with an interruption at 2:00 | 1 minimum |
| Presenter and backup operator | Both rehearsed |

## 9. Acceptance criteria

1. Demo completes in five minutes without improvisation.
2. Every claim in the script is verifiable on screen.
3. Every simulated element is stated as simulated.
4. Failure recovery rehearsed at least once.
5. A `demo-ready` git tag exists for the exact build being shown.

## 10. Future work

Two-minute short version for a hallway pitch; a technical deep-dive version for judges who ask for
the models; a recorded version for submission.

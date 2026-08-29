# PROBLEM STATEMENT

| Field | Value |
|---|---|
| Status | Level-1 (authoritative) |
| Owner | Shared |
| Purpose | Map NEXUS-TWIN explicitly onto the competition requirement |

---

## 1. The competition requirement

> Provided traffic data → AI/ML processing and reasoning → meaningful traffic intelligence.

Three obligations follow, and this document exists to make each one auditable:

| Obligation | Where it is satisfied | Evidence document |
|---|---|---|
| The provided dataset is genuinely used | Geotab columns train the prediction and anomaly models and parameterise the corridor baseline | `05_DATA/DATA_PROVENANCE.md` |
| AI/ML performs real processing | XGBoost, Isolation Forest, NetworkX graph propagation, simulation-based evaluation | `03_ARCHITECTURE/AI_ARCHITECTURE.md` |
| The output is meaningful intelligence | A ranked, explained, testable intervention recommendation, not a chart | `06_AI/EXPLAINABLE_AI.md` |

**The Geotab dataset cannot be decorative.** If every model still worked with the dataset
deleted, the project has failed this requirement regardless of how the demo looks.

---

## 2. The domain problem

Urban corridors fail as networks, not as isolated points. A single blocking incident at one
intersection raises queue length upstream, which reduces discharge at the next intersection,
which raises its queue, and so on. By the time a conventional dashboard shows three red
intersections, the intervention that would have prevented two of them has already expired.

Operators therefore face three unanswered questions:

| Question | Conventional systems | Consequence |
|---|---|---|
| What kind of abnormality is this? | "Congestion detected" | Cannot choose between signal, demand, and incident responses |
| Where will it spread? | Not modelled | Interventions are applied where the problem already is, not where it is going |
| How long do I have? | Not modelled | No basis for prioritising between simultaneous events |

A recurring evening peak and a lane-blocking collision produce similar aggregate metrics and
require completely different responses. Systems that only report severity cannot distinguish them.

---

## 3. Problem statement

> Urban traffic operators receive detection without diagnosis, severity without propagation, and
> alerts without a decision window. They are asked to intervene in a network system using
> point-in-time measurements, with no way to test an action before committing to it.

## 4. What NEXUS-TWIN changes

| Capability | Question answered | Technique |
|---|---|---|
| Traffic fingerprint | What kind of abnormality is this? | Isolation Forest score + deviation-signal classification |
| 5-minute prediction | What will happen next here? | XGBoost classifier + regressor on Geotab-derived features |
| Congestion domino effect | Where will it spread, and how soon? | NetworkX corridor graph with risk propagation |
| Intervention window | How long do I have? | Earliest spillover ETA minus strategy lead time |
| Digital Twin | What happens if I do A instead of B? | Deterministic simulation of each candidate strategy |
| Explainable recommendation | Which action, and on what evidence? | Multi-objective scoring with SHAP-backed evidence |
| Human decision | Who is accountable? | Operator approves, overrides, or submits an alternative plan |

## 5. Scope of the claim

NEXUS-TWIN is a **decision-support system**, not an autonomous controller. It does not actuate
signals. It produces recommendations with stated confidence, stated trade-offs, and a safety
check, for a human to accept or reject. This limitation is deliberate and is stated to judges
rather than hidden — an AI that recommends with evidence while a human retains control is a more
defensible design than one that claims to outperform operators.

## 6. Constraints

| Constraint | Implication |
|---|---|
| Geotab data is aggregated by intersection, hour, month, direction, and weekend flag | The system reasons about typical conditions per context, not individual vehicles |
| The dataset has no incident labels | Fingerprint classes are derived from deviation against the learned contextual baseline, not supervised incident labels |
| The dataset is historical, not streaming | "Live" state is a replay or a simulation seeded with Geotab-derived distributions; this is stated in the UI, not implied away |
| Hackathon timebox | Three junctions, one corridor, one demo scenario, executed completely |

## 7. Non-goals

- Predicting individual vehicle trajectories.
- Replacing SCATS/SCOOT-class signal control.
- Claiming statistical superiority over human operators.
- City-scale deployment within the hackathon.

## 8. Success criteria

1. A judge can trace any displayed number backwards to a Geotab column or a documented model.
2. Removing the Geotab dataset visibly breaks the system — demonstrable on request.
3. The system distinguishes at least two fingerprint classes on real data, not just in the script.
4. The recommendation changes when the traffic state changes.

## 9. Failure modes of the argument

| Risk | Mitigation |
|---|---|
| "Your dataset is only in the loading screen" | Provenance document maps every model input to specific Geotab columns |
| "Your numbers are hardcoded" | Deterministic fixtures are labelled `DEMO`; live mode is switchable in front of the judge |
| "This is a dashboard with AI branding" | Fingerprint, domino, and Digital Twin all produce outputs no dashboard produces |
| "Your AI is a language model narrating fake data" | The LLM is confined to explanation; all metrics come from deterministic tools (`04_API/AGENT_TOOL_CONTRACTS.md`) |

## 10. Future work

Incident-labelled ground truth for supervised fingerprinting; live telematics ingestion;
validation of predicted spillover against observed downstream congestion.

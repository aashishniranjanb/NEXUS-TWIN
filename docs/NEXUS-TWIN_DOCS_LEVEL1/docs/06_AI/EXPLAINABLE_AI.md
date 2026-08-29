# EXPLAINABLE AI

| Field | Value |
|---|---|
| Status | Level-1 (authoritative) |
| Priority | P0 — MUST |
| Owner | Laptop 2, with Laptop 1 for SHAP |
| Consumers | Explanation panel, Copilot, decision audit trail |

---

## 1. Purpose

Ensure every recommendation answers six questions, with numbers a judge or an operator can check
against the rest of the interface.

```
WHAT?  WHY?  EVIDENCE?  CONFIDENCE?  TRADE-OFF?  SAFETY?
```

An unexplained recommendation is not usable by an operator who is accountable for the outcome.

## 2. Scope

Assembly of structured explanations from tool results, the safety check, and confidence
calculation. Natural-language phrasing by an LLM is P1 and optional; the structured explanation is
P0 and sufficient on its own.

## 3. Inputs

| Input | Source |
|---|---|
| Traffic state and deviations | Traffic State Service |
| Prediction and feature importances | XGBoost + SHAP |
| Fingerprint and signal contributions | Fingerprint service |
| Domino forecast | Graph engine |
| Simulation results for all candidates | Digital Twin |
| Scores and deltas | Strategy Optimizer |

## 4. Output structure

```json
{
  "recommended_strategy_id": "cand_diversion_25",
  "action_label": "DIVERT TRAFFIC",
  "confidence": 0.89,
  "evidence": [
    { "label": "J2 queue growth", "value": "+34%", "source": "traffic_state" },
    { "label": "J1 spillover probability", "value": "73%", "source": "domino" },
    { "label": "Predicted queue reduction", "value": "-41%", "source": "simulation" },
    { "label": "Emergency corridor", "value": "preserved", "source": "simulation" }
  ],
  "tradeoffs": [{ "label": "Alternate corridor delay", "value": "+8%" }],
  "safety": {
    "status": "PASS",
    "checks": [
      { "name": "emergency_access", "status": "PASS", "detail": "Emergency ETA 96 s, within 120 s threshold." },
      { "name": "no_junction_worsened", "status": "PASS", "detail": "No junction exceeds baseline queue." },
      { "name": "capacity_bounds", "status": "PASS", "detail": "Diversion 25%, within 40% limit." },
      { "name": "confidence_threshold", "status": "PASS", "detail": "0.89 above 0.60 minimum." }
    ]
  },
  "rationale": "Diversion reduces predicted downstream spillover while maintaining acceptable emergency access.",
  "alternatives_considered": 4
}
```

## 5. Evidence rules

| Rule | Reason |
|---|---|
| Every evidence item carries a `source` | The operator can verify it against the panel it came from |
| Every number appears elsewhere in the UI | If the explanation says 73% and the domino panel says 68%, the system has a bug, not a wording problem |
| Between three and five items | Fewer looks thin; more is not read |
| Ordered by contribution | The strongest reason first |
| Never an uncited number | Uncited values are stripped by the assembler before the response is returned |

Cross-panel numeric consistency is enforced by an automated test, not by review.

## 6. Confidence

```
confidence = 0.35·model_confidence
           + 0.25·evidence_strength
           + 0.20·simulation_margin
           + 0.20·fingerprint_confidence
```

| Term | Definition |
|---|---|
| `model_confidence` | XGBoost predicted probability distance from 0.5, scaled |
| `evidence_strength` | Mean normalised magnitude of the evidence deviations |
| `simulation_margin` | Score gap between the best and second-best candidate, normalised |
| `fingerprint_confidence` | From the fingerprint service |

`simulation_margin` matters: when two strategies score within a few percent of each other, the
recommendation genuinely is less certain, and the number should say so. Confidence below 0.60
produces `safety.status: WARN` and a UI prompt to review alternatives before approving.

## 7. Trade-offs

Every recommendation states what it costs. A recommendation with no stated downside is either
trivial or dishonest.

| Trade-off | Derivation |
|---|---|
| Alternate corridor delay | Delay increase on links receiving diverted traffic |
| Cross-street delay | Delay increase on approaches losing green time |
| Throughput reduction | Throughput below the `do_nothing` baseline |
| Emergency ETA increase | Emergency delay above baseline |

Computed from the simulation deltas. A trade-off is reported whenever any metric worsens against
`do_nothing` by more than 5%.

## 8. Safety checks

Deterministic, run before any recommendation is presented:

| Check | Condition | Fail behaviour |
|---|---|---|
| `emergency_access` | Emergency ETA ≤ 120 s | `FAIL` — recommendation blocked |
| `no_junction_worsened` | No junction queue exceeds baseline by > 15% | `WARN` |
| `capacity_bounds` | Diversion ≤ 40%, green extension ≤ 40 s | `FAIL` |
| `confidence_threshold` | Confidence ≥ 0.60 | `WARN` |
| `spillover_not_increased` | Spillover risk ≤ baseline | `WARN` |

`FAIL` blocks the approve button and surfaces the reason. The operator can still override — a
system that cannot be overridden is not decision support — but the override is recorded with the
failed check attached.

## 9. SHAP

| Aspect | Detail |
|---|---|
| Model | XGBoost congestion classifier |
| Explainer | `TreeExplainer` |
| Use | Rank which features drove the prediction; the top two become evidence items |
| Fallback | Gain-based feature importances; the response states which method was used |
| Budget | 200 ms; on timeout, use the fallback |

The explanation always names its attribution method. "Queue growth contributed 0.31 (SHAP)" is a
checkable claim; "the AI considered queue growth important" is not.

## 10. Interfaces

| Interface | Detail |
|---|---|
| API | `POST /api/decision/evaluate` |
| Tools | `explain_recommendation`, `check_safety` |
| Contract | `Recommendation`, `SafetyCheck` |
| Persistence | `decision_runs` stores the full explanation |
| Frontend | Explanation panel with five sections |

## 11. Dependencies

Simulation results, optimizer scores, prediction, fingerprint, domino. Reuses the existing
`ExplainableAIEngine` module.

## 12. Failure modes

| Failure | Behaviour |
|---|---|
| SHAP unavailable | Gain importances, method stated |
| Simulation incomplete | Explain from available candidates; `alternatives_considered` reflects the true count |
| No candidate beats baseline | Recommend `do_nothing` with that as the explicit reason |
| Confidence below threshold | `WARN`, recommendation shown with a review prompt |
| Safety `FAIL` | Approval blocked; the failed check is displayed |
| LLM phrasing unavailable | Templated rationale from the structured explanation |

## 13. Testing

| Test | Assertion |
|---|---|
| Every evidence number matches its source panel value | Cross-panel consistency |
| Trade-offs present whenever a metric worsens > 5% | No silent downsides |
| Safety `FAIL` blocks approval | UI and API both enforce |
| Confidence within `[0,1]` | Range |
| No-improvement scenario | Recommends `do_nothing` with a stated reason |
| Determinism | Same inputs, same explanation |
| Uncited number | Stripped, run flagged |

## 14. Acceptance criteria

1. All six questions answered in every recommendation.
2. Every evidence number appears elsewhere in the UI with the same value.
3. Trade-offs shown whenever any metric worsens.
4. All five safety checks implemented, with `FAIL` blocking approval.
5. Attribution method named.
6. Full explanation persisted with the decision.

## 15. Future work

Counterfactual explanations ("if J1 risk were below 40%, green extension would win"), natural
language generation over the structured explanation, operator feedback on explanation usefulness,
per-operator verbosity settings.

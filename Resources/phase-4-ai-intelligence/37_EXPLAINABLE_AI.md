# 37 — Explainable AI

## Purpose
Implements **Contribution 4** from `07_NOVELTY_AND_CONTRIBUTIONS.md`: turning the Optimization layer's chosen candidate into a structured, human-readable justification. This is a first-class pipeline output, not a UI afterthought — directly relevant to the **Responsible & Explainable AI** track.

## Explanation Structure (Fixed Template)

Every recommendation/decision produces exactly these four fields:

```text
ACTION:            <chosen strategy, in plain language>
REASON:             <why it was chosen, referencing the comparison>
EXPECTED IMPACT:    <quantified predicted effect, from Scenario Engine metrics>
CONFIDENCE:         <derived from prediction confidence + simulation consistency>
```

## Generation Method

Template-driven, generated **directly from Scenario Engine and Optimization outputs** — not a separately trained "explanation model." This keeps the explanation strictly grounded in what was actually simulated, avoiding the risk of a fluent-sounding but ungrounded justification (see the over-trust risk noted in `20_SECURITY_ETHICS.md`).

```python
def explain(chosen: ScenarioResult, all_candidates: list[ScenarioResult]) -> Explanation:
    runner_up = second_best(all_candidates)
    return Explanation(
        action=describe(chosen.strategy_type, chosen.params),
        reason=compare(chosen, runner_up),   # e.g., "reduces network delay
                                              # by X% more than the next-best
                                              # option (<runner_up>)"
        expected_impact=format_impact(chosen),  # e.g., "-31% delay, -24%
                                                  # queue spillback, -42%
                                                  # emergency response time"
        confidence=derive_confidence(chosen, prediction_confidence),
    )
```

## Worked Example

```text
ACTION: Open alternate corridor
REASON: Current corridor predicted to reach 94% capacity in 6 minutes;
        alternate corridor has 38% available capacity.
EXPECTED IMPACT: -29% predicted queue accumulation
CONFIDENCE: 92%
```

```text
ACTION: Dynamic lane activation
REASON: Reduces network-wide delay and queue more than diversion or
        signal extension, without displacing congestion to Junction B.
EXPECTED IMPACT: -34% waiting time, -28% queue, -19% emissions,
                 -41% emergency response time
CONFIDENCE: 88%
```

## Confidence Derivation

```text
confidence = f(prediction_confidence, score_margin)
```

Where `score_margin` is how much better the chosen candidate scored versus the runner-up (a narrow margin between top two candidates should lower stated confidence, even if the prediction itself was confident) — this avoids the failure mode of expressing high confidence in a close call.

## Low-Confidence Handling

- If `confidence` falls below a defined threshold, the explanation should be flagged distinctly in the UI (`54_UI_UX_SPECIFICATION.md`) — e.g., "Low confidence — consider manual review" — rather than presented identically to a high-confidence recommendation. This directly supports the human-oversight principle in `20_SECURITY_ETHICS.md`.

## What This Explanation Deliberately Avoids

- No fabricated certainty — confidence is derived, not a fixed placeholder.
- No claims not backed by the Scenario Engine's actual simulated metrics for this specific decision point.
- No opaque "AI decided X" — REASON always references a comparison against at least one alternative that was actually simulated.

## Dependencies
- Consumes `27_SCENARIO_ENGINE.md` (`ScenarioResult` list) and `35_STRATEGY_OPTIMIZATION.md` (chosen candidate + score).
- Consumed by `17_API_SPECIFICATION.md` (`/recommendation`, `/strategy/apply` responses), `54_UI_UX_SPECIFICATION.md`, and `56_DEMO_SCRIPT.md`.

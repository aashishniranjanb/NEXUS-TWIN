# 06 — Research Gap

## What Existing Systems Do

Across fixed-time, actuated, adaptive AI/RL, and even the most recent (2026) Digital Twin + edge-cloud + forecasting systems, the shared underlying pattern is:

```text
Detect → Predict (sometimes) → Control
```

An AI model — rule-based, RL, or a learned policy from GNN/LSTM/Transformer forecasting — outputs an action, and that action is applied (directly or via the Twin's simulated policy). The **Digital Twin, where present, is mainly used as the environment the control policy is trained or run against**, and/or as a visualization layer.

## What They Don't Sufficiently Address

1. **Explicit, human-visible counterfactual comparison.** Most systems select *one* action per decision point (via a trained policy). They do not routinely simulate several distinct candidate strategies side by side and show the comparison to a human before acting.
2. **Network-level (not junction-level) framing as the explicit optimization target.** Junction- or cluster-level optimization is the default framing; explicit protection against pushing congestion into a neighboring junction (spillback) is not typically the headline framing, even though it is a known failure mode.
3. **Explainability as a first-class output.** Existing systems focus on performance metrics (waiting time, queue length); relatively few surface a structured "what/why/expected impact/confidence" explanation designed for a human operator to evaluate before trusting the recommendation.
4. **Deliberate simplicity for reproducibility and demonstrability.** The most recent state-of-the-art work (GNN + LSTM + Transformer + RL) is powerful but heavy to reproduce, especially in a time-boxed hackathon setting. There is a gap for an architecture that is explainable and network-aware without requiring that level of model complexity to demonstrate its core idea.
5. **Robustness treated as a first-class experiment, not a footnote.** At least one recent study explicitly flags that simulation assumes near-perfect sensing while real sensors have noise/latency/occlusion — but this is typically a caveat, not a structured experiment with its own results.

## Where NexusTwin Fits

NexusTwin occupies the intersection of these gaps:

```text
                 Network-level framing
                          │
        Existing AI/RL ───┼─── NexusTwin
        (junction/cluster) │   (network, explicit
                            │    spillback protection)
                          │
   ────────────────────────┼──────────────────────── 
                          │
        Existing DT+RL ───┼─── NexusTwin
        (policy trained    │   (explicit multi-strategy
         against Twin)     │    simulate-then-choose,
                          │    surfaced to the user)
```

Concretely, the gap NexusTwin targets is:

> An **explainable, network-aware decision-validation layer** that sits between prediction and control — generating multiple candidate interventions, testing each inside a synchronized Digital Twin, and selecting/recommending the one with the best *network-wide* outcome, with a structured explanation, at a level of model complexity that is reproducible within a hackathon build window.

This is what `07_NOVELTY_AND_CONTRIBUTIONS.md` formalizes into specific claimed contributions.

## What We Explicitly Do NOT Claim

To stay defensible against an informed judge or reviewer, we do not claim:

- To be the first system to use a Digital Twin for traffic.
- To be the first system to use RL for signal control.
- To be the first to combine edge AI + Digital Twin + prediction (this exists — see `04_RESEARCH_LITERATURE.md`, reference 4).
- That no existing system can predict congestion.
- That our prototype controls real, live city infrastructure.

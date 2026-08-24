# DIGITAL_TWIN_INTEGRATION.md — Digital Twin & Scenario Isolation

**Status**: [IMPLEMENTED] Core Simulation Architecture  
**Authoritative Simulator**: SUMO 1.27.1 via TraCI  
**Last Updated**: 2026-08-23

---

## 1. Architecture Overview
The Digital Twin maintains a strict separation between the **Authoritative Live World** and **Counterfactual Exploratory Futures**.

```text
AUTHORITATIVE LIVE SUMO WORLD
         │
         ▼ (Snapshot: saveState)
TEMPORARY STATE MEMORY / XML SNAPSHOT
         │
  ┌──────┴─────────────────────────┐
  ▼                                ▼
FUTURE A (Do Nothing)      FUTURE B (Apply Green Extend)
  │                                │
  ▼ (Simulate Horizon 180s)        ▼ (Simulate Horizon 180s)
Metrics A                        Metrics B
  └──────┬─────────────────────────┘
         ▼ (Restore: loadState)
AUTHORITATIVE LIVE SUMO WORLD (Unmutated State)
```

---

## 2. State Snapshot & Isolation Rules
1. **Never Mutate Authoritative Live State During Exploration**: Any counterfactual evaluation MUST call `saveState()` before modifying signals or routes.
2. **Mandatory State Restoration**: After the simulation horizon (e.g., 180s forward) completes and metrics are recorded, `loadState()` MUST restore the exact pre-evaluation snapshot.
3. **Deterministic Seeding**: Counterfactual runs MUST use identical random seeds to ensure valid comparison against baseline.

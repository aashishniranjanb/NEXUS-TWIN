# MULTI_AGENT_ARCHITECTURE.md — Multi-Agent Layer Specification

**Status**: [FUTURE] Phase 2 Architecture (DOCUMENT ONLY — NOT AN MVP DEPENDENCY)  
**Framework**: LangGraph  
**Last Updated**: 2026-08-23

> [!IMPORTANT]
> This document specifies the Phase 2 extension architecture. **Do NOT implement for MVP**. The MVP relies strictly on the deterministic Python Strategy Generator + XGBoost Predictor + Scenario Engine. Multi-agent orchestration is added later without replacing the existing stack.

---

## 1. Supervisor Architecture Pattern
```text
                       ┌─────────────────────────┐
                       │    SUPERVISOR AGENT     │
                       └────────────┬────────────┘
                                    │
    ┌──────────────┬────────────────┼────────────────┬──────────────┐
    ▼              ▼                ▼                ▼              ▼
[Perception]  [Prediction]     [Strategy]       [Simulation]    [Explanation]
   Agent         Agent            Agent            Agent           Agent
```

---

## 2. Agent Roles & Tool Contracts
- **Perception Agent**: Wraps traffic state telemetry tools.
- **Prediction Agent**: Calls XGBoost predictor model.
- **Strategy Agent**: Formulates candidate strategies.
- **Simulation Agent**: Triggers Digital Twin snapshot & counterfactual evaluation.
- **Safety Agent**: Enforces speed limits, emergency access, and gridlock safety guardrails.
- **Explanation Agent**: Translates strategy comparisons into human-understandable natural language explanations.

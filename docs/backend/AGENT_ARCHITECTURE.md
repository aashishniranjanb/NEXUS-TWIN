# Multi-Agent Decision Architecture

| Property | Value |
|---|---|
| **Orchestration** | LangGraph State Machine Architecture |
| **Reasoning Nodes** | 5 Specialized Intelligence Nodes |
| **Rule** | Deterministic tools perform all calculations; LLM serves as reasoning and explanation layer. |
| **Fallback** | 100% deterministic graceful fallback if external LLM API is unavailable. |

---

## 1. Agent Roles

| Agent Node | Role | Deterministic Tools Called |
|---|---|---|
| **`TrafficIntelligenceNode`** | Analyzes empirical telematics observations and assigns diagnostic fingerprint | `TrafficPredictor`, `HistoricalBaseline`, `AnomalyDetector`, `TrafficFingerprintEngine` |
| **`NetworkIntelligenceNode`** | Evaluates corridor topology, propagates shockwaves, and computes domino chains | `TrafficNetworkGraph`, `CongestionSpilloverModel`, `DominoEffectEngine` |
| **`StrategyGenerationNode`** | Formulates candidate intervention strategies (Green Extension, Diversion, EMS) | `StrategyGenerator` |
| **`SimulationEvaluationNode`**| Executes 900s Digital Twin kinematic simulations and computes before/after deltas | `DigitalTwinEngine` |
| **`CriticDecisionNode`** | Responsible AI Safety Critic auditing recommendations and generating explanation | `SafetyCritic`, `ExplainableAIEngine` |

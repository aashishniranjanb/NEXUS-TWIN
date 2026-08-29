# AGENT TOOL CONTRACTS

| Field | Value |
|---|---|
| Status | Level-1 (authoritative) |
| Priority | P1 for the agent layer; the tools themselves are P0 functions |
| Owner | Laptop 2 |
| Depends on | `03_ARCHITECTURE/AGENT_ARCHITECTURE.md`, `API_DATA_CONTRACTS.md` |

---

## 1. Purpose

Define every function an LLM is permitted to call, with typed inputs and outputs, so that the
language model reasons over real results and never produces a traffic number itself.

## 2. The principle

```
LLM
 -> tool call
 -> real ML / graph / simulation result
 -> LLM explanation of that result
```

The LLM's job is selection and phrasing. Computation belongs to the tools. This is the single
architectural decision that separates a defensible agent system from a chatbot that sounds
confident about numbers it invented.

## 3. Rules

1. Every tool is an ordinary Python function, independently callable and unit-testable, with no
   LangChain or LangGraph import in its module.
2. Inputs and outputs are Pydantic models matching `API_DATA_CONTRACTS.md`.
3. Tools are pure with respect to the session: same `session_id` and same step gives the same
   result.
4. Tools never raise into the agent. They return a result object with `success: false` and an
   `error` string.
5. No tool has side effects except `record_decision`.
6. Tools that would take longer than 5 s return a handle, not a blocked call.

## 4. Tool catalogue

| Tool | Agent | Side effects | Typical latency |
|---|---|---|---|
| `get_current_traffic` | Traffic Intelligence | none | < 50 ms |
| `predict_congestion` | Traffic Intelligence | none | < 150 ms |
| `detect_anomaly` | Traffic Intelligence | none | < 100 ms |
| `generate_fingerprint` | Traffic Intelligence | none | < 50 ms |
| `predict_spillover` | Network Intelligence | none | < 100 ms |
| `compute_intervention_window` | Network Intelligence | none | < 20 ms |
| `generate_strategies` | Strategy | none | < 50 ms |
| `simulate_strategy` | Simulation | none | 0.5–3 s |
| `compare_strategies` | Simulation | none | < 50 ms |
| `explain_recommendation` | Critic | none | < 100 ms |
| `check_safety` | Critic | none | < 50 ms |
| `record_decision` | Critic | writes `decision_runs` | < 100 ms |

## 5. Signatures

```python
def get_current_traffic(session_id: str, junction_id: JunctionId | None = None) -> TrafficStateResult
```
Returns the current corridor state including Geotab baselines and deviations. `junction_id`
filters to one junction.

```python
def predict_congestion(session_id: str, junction_id: JunctionId, horizon_minutes: int = 5) -> PredictionResult
```
XGBoost classifier and regressor. Returns `congestion_probability`, `predicted_queue_m`,
`confidence`, and `feature_importances`. Never returns a probability outside `[0,1]`.

```python
def detect_anomaly(session_id: str, junction_id: JunctionId) -> AnomalyResult
```
Isolation Forest over the deviation vector. Returns score, threshold, and the top contributing
deviations.

```python
def generate_fingerprint(session_id: str, junction_id: JunctionId) -> FingerprintResult
```
Classifies the abnormality. May return `UNKNOWN` with low confidence — the agent must be able to
say it does not know rather than pick the nearest label.

```python
def predict_spillover(session_id: str, source_junction: JunctionId, horizon_minutes: int = 10) -> DominoResult
```
NetworkX propagation across the corridor graph. Returns neighbours ranked by risk with ETAs and
propagation mechanism.

```python
def compute_intervention_window(session_id: str, domino: DominoResult) -> InterventionWindowResult
```
Earliest spillover ETA minus strategy lead time. Pure function of its input.

```python
def generate_strategies(session_id: str, junction_id: JunctionId, fingerprint: FingerprintResult | None = None) -> StrategyListResult
```
Returns 3–4 candidates from the constrained catalogue, always including `do_nothing`. **The agent
cannot add a strategy type.** Any type not in `ids.yaml` is rejected before it reaches simulation.

```python
def simulate_strategy(session_id: str, strategy_id: str, horizon_seconds: int = 180) -> SimulationResultModel
```
Runs the Digital Twin for one strategy. Deterministic for a fixed seed.

```python
def compare_strategies(session_id: str, simulation_id: str) -> ComparisonResult
```
Multi-objective scoring against the `do_nothing` baseline. Returns per-strategy scores and the
best strategy for each of three objectives.

```python
def explain_recommendation(session_id: str, simulation_id: str, strategy_id: str) -> ExplanationResult
```
Assembles evidence, trade-offs, and confidence from prior tool results. Returns structured
evidence items, not prose — the prose is the LLM's contribution.

```python
def check_safety(session_id: str, strategy_id: str, simulation_id: str) -> SafetyResult
```
Deterministic checks: emergency access preserved, no junction worsened beyond tolerance, diversion
within capacity bounds, confidence above threshold. Returns `PASS | WARN | FAIL` per check.

```python
def record_decision(session_id: str, strategy_id: str, decision: Literal['APPROVE','OVERRIDE'], operator_note: str = '') -> DecisionResultModel
```
The only tool with side effects. Persists the decision and computes the before/after outcome.

## 6. Result envelope

```python
class ToolResult(BaseModel):
    success: bool
    tool: str
    session_id: str
    data: dict | None = None
    error: str | None = None
    computed_at: datetime
    source: Literal['model', 'graph', 'simulation', 'fixture']
```

`source` is what lets the explanation layer state where each number came from, and what the
provenance panel reads.

## 7. Anti-fabrication enforcement

Structural, not advisory:

| Control | Mechanism |
|---|---|
| No metric-producing capability | The agent has no calculator, no code execution, no database access |
| Citation requirement | Every numeric token in a generated explanation is matched against values in `tool_calls` |
| Stripping | Unmatched numbers are removed and the run is flagged `fabrication_suspected` |
| Audit trail | Full `tool_calls` list persisted per run in `agent_runs` |
| Constrained actions | Strategy type validated against `ids.yaml` before any simulation |

A run flagged `fabrication_suspected` fails the test suite. It is treated as a defect, not a
stylistic issue.

## 8. Tool registration

```python
TOOL_REGISTRY = {
    "get_current_traffic":         (get_current_traffic, GetCurrentTrafficArgs),
    "predict_congestion":          (predict_congestion, PredictCongestionArgs),
    # …
}
```

The LangGraph layer builds its tool list from this registry. Adding a function to `ai/` does not
make it callable by an LLM; registration is an explicit, reviewed step.

## 9. Failure modes

| Failure | Tool behaviour | Agent behaviour |
|---|---|---|
| Model artifact missing | `success: true`, `source: 'fixture'`, degraded values | Proceeds, notes degradation in the explanation |
| Simulation timeout | `success: false`, `error: 'timeout'` | Critic reasons with fewer candidates |
| Unknown junction | `success: false`, `error: 'unknown_junction'` | Agent retries once with a valid ID, then stops |
| Database down (`record_decision`) | `success: false` | Decision returned to UI, persistence skipped, warning logged |
| Tool called out of order (e.g. explain before simulate) | `success: false`, `error: 'missing_prerequisite'` | Agent calls the prerequisite |

## 10. Testing

- Unit test per tool with fixed inputs and asserted outputs.
- Contract test: every tool result validates against its Pydantic model.
- Determinism test: identical inputs produce identical outputs across runs.
- Fabrication test: a full agent run's explanation contains no number absent from `tool_calls`.
- Independence test: import every tool module in an environment without LangChain installed.

## 11. Acceptance criteria

1. All twelve tools implemented, typed, and independently callable.
2. No tool module imports LangChain or LangGraph.
3. Fabrication test passes on the demo scenario.
4. `TOOL_REGISTRY` is the only path by which an LLM reaches project code.

## 12. Future work

Streaming tool results into the Copilot UI, cost and latency budgets per tool, tool-level caching,
LangSmith traces linked to `agent_runs` rows.

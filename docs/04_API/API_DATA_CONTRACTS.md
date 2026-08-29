# API DATA CONTRACTS

| Field | Value |
|---|---|
| Status | Level-1 (authoritative) |
| Owner | Shared — changes require agreement from all three members |
| Location | `shared/contracts/` (TypeScript) and `services/api/schemas/` (Pydantic) |

---

## 1. Purpose

One field name, one type, one unit, everywhere. This document is the reason integration takes
minutes instead of hours.

The failure this prevents:

```
Laptop 1 emits:  { "risk": 0.87 }
Laptop 3 expects:{ "congestion_probability": 87 }
```

Both are defensible. Together they cost an afternoon, discovered during integration, under time
pressure.

## 2. Rules

1. **Probabilities are floats in `[0,1]`.** Never percentages on the wire. The frontend multiplies
   for display.
2. **Units live in field names.** `queue_length_m`, `avg_waiting_time_s`, `avg_speed_kmh`,
   `eta_minutes`, `remaining_seconds`.
3. **Identifiers are uppercase strings** from `shared_config/ids.yaml`: `J1`, `J2`, `J3`.
4. **Enums are `SCREAMING_SNAKE_CASE`.** `INCIDENT_LIKE`, not `incident-like`.
5. **Strategy types are `lower_snake_case`**, matching the existing backend: `green_extend`,
   `diversion`, `dynamic_lane`, `emergency_priority`, `do_nothing`.
6. **Timestamps are ISO-8601 UTC strings.** Simulation clocks are float seconds named `*_s`.
7. **Optional means nullable, not absent.** Emit `null` rather than omitting a key.
8. **Additive changes only** during the hackathon. Renaming a field requires a message to both
   other members before the commit, not after.

## 3. Enumerations

```ts
export type JunctionId   = 'J1' | 'J2' | 'J3';
export type JunctionState = 'NORMAL' | 'WARNING' | 'CRITICAL';
export type FingerprintType =
  | 'NORMAL' | 'RECURRING_CONGESTION' | 'INCIDENT_LIKE'
  | 'DEMAND_SURGE' | 'SIGNAL_RELATED' | 'UNKNOWN';
export type StrategyType =
  | 'do_nothing' | 'green_extend' | 'diversion'
  | 'dynamic_lane' | 'emergency_priority';
export type IncidentType = 'accident' | 'closure' | 'surge' | 'weather' | 'emergency';
export type VehicleType  = 'car' | 'bus' | 'truck' | 'motorcycle' | 'ambulance' | 'police' | 'fire';
export type SafetyStatus = 'PASS' | 'WARN' | 'FAIL';
export type UrgencyLevel = 'MONITOR' | 'PREPARE' | 'ACT_NOW';
export type DataMode     = 'LIVE' | 'DEMO';
export type ScenarioState =
  | 'NORMAL' | 'ANOMALY' | 'FINGERPRINT' | 'PREDICTION' | 'SPILLOVER'
  | 'RECOMMENDATION' | 'SIMULATION' | 'DECISION' | 'OUTCOME';
```

Any new value requires a change in `ids.yaml`, this file, the Pydantic enum, and the TypeScript
union — in that order.

## 4. Core types

### 4.1 Envelope

```ts
export interface Envelope {
  session_id: string;
  generated_at: string;      // ISO-8601 UTC
  mode: DataMode;
  degraded: boolean;
  data_source: 'geotab' | 'simulation' | 'fixture';
}
```

### 4.2 Traffic state

```ts
export interface JunctionMetrics {
  junction_id: JunctionId;
  state: JunctionState;
  queue_length_m: number;
  avg_speed_kmh: number;
  avg_waiting_time_s: number;
  vehicle_count: number;
  flow_veh_min: number;
  density_pct: number;              // 0-100, display units by exception
  signal_phase: number;
  signal_phase_name: string;
  baseline: { queue_length_m: number; avg_waiting_time_s: number } | null;
  deviation: Record<string, number> | null;   // z-scores
}

export interface NetworkMetrics {
  active_vehicles: number;
  avg_speed_kmh: number;
  avg_waiting_time_s: number;
  mean_queue_length_m: number;
  flow_veh_min: number;
  density_pct: number;
}

export interface TrafficState extends Envelope {
  timestamp: number;                 // simulation seconds
  scenario_step: number;             // 0-8
  network: NetworkMetrics;
  junctions: Record<JunctionId, JunctionMetrics>;
}
```

`density_pct` is the one deliberate exception to the fractions rule: it is a display metric with
no probabilistic meaning, and `0-100` is how operators read it.

### 4.3 Prediction

```ts
export interface Prediction extends Envelope {
  junction_id: JunctionId;
  horizon_minutes: number;           // 5
  congestion_probability: number;    // 0-1
  predicted_queue_m: number;
  predicted_avg_speed_kmh: number;
  will_congest: boolean;
  confidence: number;                // 0-1
  model: string;
  feature_importances: Record<string, number>;
}
```

### 4.4 Anomaly and fingerprint

```ts
export interface AnomalyResult extends Envelope {
  junction_id: JunctionId;
  is_anomaly: boolean;
  anomaly_score: number;             // 0-1
  threshold: number;
  model: string;
  top_deviations: { signal: string; z_score: number }[];
}

export interface FingerprintSignal {
  name: 'speed_deviation' | 'waiting_time_deviation' | 'queue_growth'
      | 'flow_anomaly' | 'direction_imbalance';
  value: number;
  z_score: number;
  contribution: number;              // 0-1, sums to ~1
}

export interface Fingerprint extends Envelope {
  junction_id: JunctionId;
  type: FingerprintType;
  confidence: number;                // 0-1
  signals: FingerprintSignal[];
  alternatives: { type: FingerprintType; confidence: number }[];
  rationale: string;
}
```

### 4.5 Domino and intervention window

```ts
export interface SpilloverNode {
  junction_id: JunctionId;
  risk: number;                      // 0-1
  eta_minutes: number;
  path: JunctionId[];
  mechanism: 'upstream_queue_spillback' | 'downstream_flow_disruption' | 'shared_demand';
}

export interface InterventionWindow {
  status: 'CLEAR' | 'WARNING' | 'CRITICAL';
  remaining_seconds: number;
  expires_at: string;
  consequence: string;
  urgency: UrgencyLevel;
}

export interface DominoForecast extends Envelope {
  source: { junction_id: JunctionId; risk: number };
  propagation: SpilloverNode[];      // sorted by risk desc
  intervention_window: InterventionWindow;
}
```

### 4.6 Strategy and simulation

```ts
export interface Strategy {
  strategy_id: string;
  strategy_type: StrategyType;
  label: string;                     // display: 'DIVERT TRAFFIC'
  parameters: Record<string, number | string>;
  description: string;
}

export interface SimulationResult {
  strategy_id: string;
  strategy_type: StrategyType;
  predicted_queue_m: number;
  predicted_delay_s: number;
  predicted_throughput: number;
  spillover_risk: number;            // 0-1
  emergency_eta_s: number;
  per_junction_metrics: Record<JunctionId, { queue_m: number; delay_s?: number }>;
  score: number;                     // lower is better
  delta_vs_baseline: { queue_m: number; delay_s: number; spillover_risk: number };
  success: boolean;
  error_message: string | null;
}

export interface SimulationRun extends Envelope {
  simulation_id: string;
  status: 'running' | 'complete' | 'failed';
  horizon_seconds: number;
  baseline_strategy_id: string;
  results: SimulationResult[];
  best: { overall: string; lowest_spillover: string; best_emergency: string };
}
```

`SimulationResult` intentionally mirrors the existing Python `ScenarioResult` dataclass. Field
names were chosen to match it rather than to be prettier.

### 4.7 Recommendation and decision

```ts
export interface EvidenceItem {
  label: string;
  value: string;                     // pre-formatted for display
  source: 'traffic_state' | 'prediction' | 'anomaly' | 'domino' | 'simulation';
}

export interface SafetyCheck { name: string; status: SafetyStatus; detail?: string }

export interface Recommendation extends Envelope {
  recommended_strategy_id: string;
  action_label: string;
  confidence: number;
  evidence: EvidenceItem[];
  tradeoffs: { label: string; value: string }[];
  safety: { status: SafetyStatus; checks: SafetyCheck[] };
  rationale: string;
  alternatives_considered: number;
}

export interface Outcome {
  before: { queue_m: number; delay_s: number; spillover_risk: number };
  after:  { queue_m: number; delay_s: number; spillover_risk: number };
  delta:  { queue_m: number; delay_s: number; spillover_risk: number };  // fractional
  spillover_prevented: boolean;
  network_score: number;             // 0-100
}

export interface DecisionResult extends Envelope {
  decision_id: string;
  applied_strategy_id: string;
  decision: 'APPROVE' | 'OVERRIDE';
  outcome: Outcome;
  ai_vs_human: {
    ai_strategy_id: string;
    human_strategy_id: string;
    agreed: boolean;
    score_difference: number;
  } | null;
}
```

## 5. Pydantic parity

Every type above has a Pydantic counterpart with identical field names. Parity is enforced by a
test, not by discipline:

```python
def test_contract_parity():
    ts = json.load(open("apps/web/src/lib/demo/traffic_state.json"))
    TrafficStateModel.model_validate(ts)   # must not raise
```

The same committed fixtures are parsed by Zod on the frontend and by Pydantic on the backend. If
either side drifts, a test goes red before integration day.

## 6. File layout

```
shared/contracts/
├── common.ts        Envelope, enums, ids
├── traffic.ts       TrafficState, JunctionMetrics, NetworkMetrics
├── prediction.ts
├── anomaly.ts       AnomalyResult
├── fingerprint.ts
├── domino.ts        SpilloverNode, InterventionWindow, DominoForecast
├── strategy.ts
├── simulation.ts
├── decision.ts      Recommendation, Outcome, DecisionResult
├── copilot.ts       P1
└── index.ts
```

Each file exports both the TypeScript type and a Zod schema of the same name suffixed `Schema`.

## 7. Failure modes

| Failure | Handling |
|---|---|
| Response fails Zod validation | Log the issue, fall back to the fixture, surface a `DEMO` badge — never render partial garbage |
| New field appears | Ignored by older clients; additive changes are safe by design |
| Field renamed without agreement | Contract test fails in CI; the commit is reverted |
| Unit mismatch | Caught by range assertions in the parity test (probabilities must be ≤ 1) |

## 8. Testing

- Parity test per contract file.
- Range assertions: every field named `*_probability`, `risk`, `confidence`, `*_score` in `[0,1]`.
- Enum coverage: every union member appears in at least one fixture.

## 9. Acceptance criteria

1. `shared/contracts/` and `services/api/schemas/` agree field-for-field.
2. Every committed fixture validates under both Zod and Pydantic.
3. No probability field carries a value greater than 1 anywhere in the system.

## 10. Future work

Generate TypeScript types directly from the FastAPI OpenAPI schema to remove the hand-maintained
duplication.

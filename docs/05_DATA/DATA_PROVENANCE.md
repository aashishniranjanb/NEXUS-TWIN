# DATA PROVENANCE

| Field | Value |
|---|---|
| Status | Level-1 (authoritative) |
| Owner | Laptop 1, verified by Laptop 3 in the UI |
| Purpose | Evidence that the mandatory dataset materially drives the system |

---

## 1. Purpose

The competition requires meaningful use of the provided dataset. This document is not description;
it is **evidence**. It states which dataset columns produce which outputs, and it defines the test
that proves the dependency is real.

## 2. Source

```
SOURCE
  BigQuery-Geotab Intersection Congestion Dataset
  Kaggle / Google BigQuery public dataset
  Aggregated commercial-vehicle telematics, grouped by intersection,
  month, hour, direction of travel, and weekend flag
  Cities: Atlanta, Boston, Chicago, Philadelphia
```

Local path `data/raw/geotab/`. Corridor selection recorded in
`data/processed/corridor_mapping.json`.

## 3. Used for

| Purpose | Status |
|---|---|
| Corridor construction (which junctions, where, connected how) | MUST |
| Contextual baselines (expected conditions per intersection-hour-direction) | MUST |
| Congestion prediction model training | MUST |
| Anomaly detection (deviation from baseline) | MUST |
| Traffic fingerprinting (which signals deviate, and by how much) | MUST |
| Network graph topology and link lengths | MUST |
| Digital Twin demand parameterisation | MUST |
| Scenario realism (what a plausible incident looks like at this junction) | SHOULD |

## 4. Column-to-output map

| Geotab column(s) | Derived feature | Consumed by | Visible in UI as |
|---|---|---|---|
| `IntersectionId` | Junction identity | Corridor mapping, baselines | J1 / J2 / J3 labels and the provenance panel |
| `Latitude`, `Longitude` | Node coordinates, link lengths | NetworkX graph, MapLibre | Map placement, domino ETAs |
| `EntryStreetName`, `ExitStreetName` | Edge identity | Graph construction | Link labels |
| `EntryHeading`, `ExitHeading` | `heading_angle`, `turn_angle`, direction imbalance | Fingerprint, prediction | `direction_imbalance` signal |
| `Hour`, `Weekend`, `Month` | `hour_sin`, `hour_cos`, `is_weekend`, `month_*` | Baselines, prediction | Baseline comparison in Current State |
| `TotalTimeStopped_p20/50/80` | `baseline_stopped_*`, waiting-time deviation | Baselines, anomaly, prediction | Waiting time, `waiting_time_deviation` signal |
| `DistanceToFirstStop_p20/50/80` | Queue-length proxy, `baseline_distance_*` | Baselines, anomaly, prediction | Queue length, `queue_growth` signal |
| `TimeFromFirstStop_p50` | Discharge-rate proxy | Digital Twin | Simulation delay outputs |
| `City` | Corridor scope | Selection, one-hot feature | Provenance panel |

Every row in this table is checkable. If a judge asks "where does the 91% fingerprint confidence
come from?", the chain is: `DistanceToFirstStop_p50` and `TotalTimeStopped_p50` → contextual
baseline → z-scored deviation → signal contributions → classification confidence.

## 5. Pipeline surface

```
Provided Traffic Data
      -> Feature Engineering
      -> AI Intelligence
      -> Prediction
      -> Simulation
      -> Decision
```

The `GET /api/provenance` endpoint returns the dataset name, city, the three `IntersectionId`
values, rows used, and the per-model input list. The Command Center renders this as a compact
header indicator that expands into the full map. Visible, but not shouting.

## 6. Honest boundaries

Claiming more than the data supports is a larger risk than claiming less. These statements are
made in the UI and in the demo narration:

| Output | Geotab-derived? | Statement |
|---|---|---|
| Junction identity and geometry | Yes | Real intersections from the dataset |
| Contextual baselines | Yes | Learned from historical percentiles |
| Prediction model | Yes (features and training) | Trained on Geotab-derived features |
| Anomaly and fingerprint | Yes (baseline reference) | Deviation measured against Geotab baselines |
| Live second-by-second vehicle positions | **No** | Simulated; the dataset is aggregated, not streaming |
| Signal phase and timing | **No** | Simulated; not present in the dataset |
| Incident labels | **No** | Fingerprint classes are deviation-derived, not supervised |

The distinction is stated plainly rather than blurred. A judge who discovers an overclaim
discounts everything else; a team that states its boundaries first is believed on the rest.

## 7. The dependency test

The claim "the dataset meaningfully influences the system" is verified by removing it:

```bash
pytest tests/test_provenance_dependency.py
```

| Action | Required observable effect |
|---|---|
| Delete `baselines.parquet` | Anomaly and fingerprint endpoints return `degraded: true`; confidence drops below 0.5 |
| Shuffle Geotab context columns and retrain | Classification F1 drops by more than 0.15 |
| Remove `corridor_mapping.json` | Corridor graph cannot be built; domino endpoint degrades |
| Remove `DistanceToFirstStop` features | Queue regressor MAE increases by more than 25% |

If any of these produces no effect, the dataset is decorative in that path and that path must be
fixed. This test is the strongest possible answer to the most likely challenge from a judge, and
it can be run in front of them.

## 8. Audit trail

Every API response carries `data_source` (`geotab`, `simulation`, or `fixture`). Simulation runs
and decisions persist the corridor mapping version and model artifact hashes, so any recorded
decision can be traced to the exact data and models that produced it.

## 9. Failure modes

| Failure | Behaviour |
|---|---|
| Raw dataset absent on demo machine | DEMO mode from `data/samples/`; provenance panel shows `SAMPLE` and the demo continues |
| Baselines stale relative to mapping | Startup version check logs a warning and flags `degraded` |
| Provenance endpoint unavailable | Panel shows the static dataset name; never shows a false green state |

## 10. Testing

- `test_provenance_dependency.py` — section 7.
- `test_provenance_endpoint.py` — returned intersection IDs match `corridor_mapping.json`.
- UI test — the provenance indicator renders and expands in both LIVE and DEMO.

## 11. Acceptance criteria

1. Every model input traces to a column in section 4.
2. The dependency test passes.
3. The provenance indicator is visible in the Command Center at all times.
4. No UI element claims Geotab origin for a simulated quantity.

## 12. Future work

Per-response provenance (which baseline cell and sample count produced this number), dataset
version pinning by checksum, live telematics ingestion.

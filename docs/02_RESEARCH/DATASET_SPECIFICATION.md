# DATASET SPECIFICATION

| Field | Value |
|---|---|
| Dataset | BigQuery-Geotab Intersection Congestion Dataset |
| Origin | Kaggle / Google BigQuery public dataset, 2019 |
| Status | Level-1 (authoritative) |
| Owner | Laptop 1 (AI / Data) |
| Local path | `data/raw/geotab/` |

---

## 1. Purpose

Define what the mandatory dataset contains, what it does not contain, and exactly how each column
is used. Every downstream document that claims "derived from Geotab" must be reconcilable with
this file.

## 2. Provenance

Geotab partnered with Kaggle and BigQuery to host the BigQuery-Geotab Intersection Congestion competition, providing aggregated trip-logging metrics from commercial vehicle telematics devices, grouped by intersection, month, hour of day, direction driven through the intersection, and whether the day was a weekend. Participants predicted the distribution of wait times and stop distances at each intersection. The data covers four cities — Atlanta, Boston, Chicago and Philadelphia — spanning over 4,500 intersections, roughly 2,000 in Chicago, 1,250 in Philadelphia, 1,000 in Boston and around 400 in Atlanta.

This matters for our design: the data is **aggregated percentile statistics per movement**, not a
vehicle-level or second-by-second feed.

## 3. Schema

### 3.1 Identity and location

| Column | Type | Use in NEXUS-TWIN |
|---|---|---|
| `RowId` | int | Row key only |
| `IntersectionId` | int | Junction identity; basis for mapping to J1/J2/J3 |
| `Latitude`, `Longitude` | float | Map placement, corridor construction, neighbour distance |
| `City` | categorical | Corridor selection; one-hot feature |

### 3.2 Movement geometry

| Column | Type | Use |
|---|---|---|
| `EntryStreetName`, `ExitStreetName` | string | Link identity for the corridor graph |
| `EntryHeading`, `ExitHeading` | categorical (N, NE, E, …) | Turning-movement feature; direction imbalance signal |
| `Path` | string | Concatenated entry/exit descriptor; movement grouping key |

Headings are encoded as `θ/π` with north = 0 measured clockwise (N = 0, E = 0.5, W = 1.5), and the
turn angle is derived as exit direction minus entry direction. This yields a continuous encoding
rather than an arbitrary categorical index.

### 3.3 Temporal context

| Column | Type | Use |
|---|---|---|
| `Hour` | 0–23 | Contextual baseline key; cyclical sin/cos features |
| `Weekend` | 0/1 | Contextual baseline key |
| `Month` | 1–12 | Seasonal feature |

### 3.4 Targets and congestion measures

| Column group | Percentiles | Meaning |
|---|---|---|
| `TotalTimeStopped_p20/40/50/60/80` | 20th–80th | Seconds stopped at the intersection |
| `TimeFromFirstStop_p20/40/50/60/80` | 20th–80th | Seconds from first stop to clearing |
| `DistanceToFirstStop_p20/40/50/60/80` | 20th–80th | Distance from the intersection to the first stop — a direct queue-length proxy |

The original competition scored six targets: `TotalTimeStopped_p20`, `p50`, `p80` and `DistanceToFirstStop_p20`, `p50`, `p80`. We use the same six as primary signals.

Only `p20/p50/p80` are present in the test split; `p40/p60` exist in training only. **Do not build
features that depend on `p40` or `p60`** unless the model is training-only.

## 4. How each capability uses the dataset

| Capability | Geotab inputs | Derived quantity |
|---|---|---|
| Contextual baseline | `IntersectionId`, `Hour`, `Weekend`, `Month`, `EntryHeading`, all target percentiles | Expected stopped time and stop distance per intersection-hour-direction |
| Current state | `TotalTimeStopped_p50`, `DistanceToFirstStop_p50` | Waiting time (s), queue proxy (m) |
| Prediction | Baseline + lag features + context | 5-minute congestion probability and predicted queue |
| Anomaly detection | Deviation of observed from contextual baseline | Isolation Forest anomaly score |
| Traffic fingerprint | Per-signal deviations including direction imbalance from `EntryHeading` distribution | Fingerprint class + supporting signals |
| Corridor graph | `Latitude`, `Longitude`, `EntryStreetName`, `ExitStreetName` | Nodes, edges, link lengths, travel-time weights |
| Domino effect | Graph + per-node risk | Neighbour spillover risk and ETA |
| Digital Twin | Baseline demand per movement | Simulation arrival rates |

The queue proxy uses `DistanceToFirstStop` because the distance from the intersection to a
vehicle's first stop is physically the back of the standing queue on that approach.

## 5. Mapping the dataset onto J1–J2–J3

The demo corridor is three consecutive real intersections from one city, selected once and frozen.

Selection procedure:

1. Filter to one `City`.
2. Group by `IntersectionId` and compute mean `TotalTimeStopped_p80` across peak hours.
3. Find chains of three intersections that share street names (`ExitStreetName` of one equals
   `EntryStreetName` of the next) and are within 400 m of each other.
4. Choose the chain with the highest combined peak congestion.
5. Record the chosen `IntersectionId` values in `shared_config/ids.yaml` alongside `J1`, `J2`, `J3`.

The mapping is written to `data/processed/corridor_mapping.json` and is displayed in the
provenance panel. The corridor is real, named, and reproducible — not invented geometry.

## 6. Limitations

| Limitation | Consequence | Handling |
|---|---|---|
| Aggregated, not streaming | No true real-time feed | "Live" mode replays or simulates from Geotab-derived distributions; the UI labels the mode |
| No incident labels | Fingerprint cannot be supervised on incidents | Deviation-based classification with documented thresholds |
| No signal timing data | Signal phase is not observed | Signal state comes from the simulation layer, never claimed as Geotab-derived |
| Percentiles, not time series | No within-hour dynamics | Within-hour dynamics come from the simulation engine, seeded by Geotab baselines |
| Commercial vehicle bias | Sample is not all traffic | Stated in provenance; treated as a proxy, not ground truth |
| 2019 vintage | Not current conditions | Stated; the system is a method demonstration |

**Rule:** anything the dataset cannot support must be labelled as simulated in both the UI and the
demo narration. Overclaiming is a larger risk to the project than a modest claim.

## 7. Storage and processing

```
data/
├── raw/geotab/            train.csv, test.csv — never modified
├── processed/
│   ├── corridor_mapping.json
│   ├── baselines.parquet          per intersection-hour-weekend-heading
│   └── features.parquet           model-ready matrix
└── samples/
    └── corridor_sample.csv        small committed sample for tests and demo mode
```

`data/raw/` is git-ignored. `data/samples/corridor_sample.csv` is committed so tests and DEMO mode
run without the full download.

## 8. Validation gates

| Check | Rule | On failure |
|---|---|---|
| Required columns present | All identity, context, and `p20/p50/p80` target columns | Abort ingestion |
| Row count | Non-empty after corridor filter | Abort |
| Coordinates | Latitude/longitude within city bounds | Drop row, log |
| Percentile monotonicity | `p20 ≤ p50 ≤ p80` | Drop row, log |
| Null rate | ≤ 5% per used column | Warn; impute by intersection-hour median |
| Heading validity | In the 8-point compass set | Drop row, log |

## 9. Testing

- Schema test against `data/samples/corridor_sample.csv`.
- Baseline reproducibility: same input produces byte-identical `baselines.parquet`.
- Corridor mapping test: the three chosen intersections are connected and within distance bounds.
- Leakage test: no target percentile column appears in the feature matrix.

## 10. Acceptance criteria

1. `corridor_mapping.json` names three real, adjacent intersections with coordinates.
2. `baselines.parquet` is regenerable from raw data by a single documented command.
3. Every feature in the model input traces to a column in section 3.
4. The provenance panel displays the dataset name, city, and the three `IntersectionId` values.

## 11. Future work

Join with OpenStreetMap link geometry for accurate lane counts; extend to all four cities; use
`TimeFromFirstStop` percentiles as a discharge-rate feature for the simulation layer.

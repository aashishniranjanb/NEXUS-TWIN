# Data Quality Report — BigQuery-Geotab Dataset

| Metric | Value |
|---|---|
| **Total Rows** | 856,387 |
| **Total Columns** | 28 |
| **Exact Duplicate Rows** | 0 |
| **Duplicate RowIds** | 0 |
| **Duplicate Context Keys** | 14,786 |

---

## 1. Schema and Missing Value Profile

| Column | Dtype | Null Count | Null % | Cardinality | Sample Values |
|---|---|---|---|---|---|
| `RowId` | `int64` | 0 | 0.0% | 856,387 | `1921357, 1921358` |
| `IntersectionId` | `int64` | 0 | 0.0% | 2,559 | `0, 0` |
| `Latitude` | `float64` | 0 | 0.0% | 4,799 | `33.791658500000004, 33.791658500000004` |
| `Longitude` | `float64` | 0 | 0.0% | 4,804 | `-84.4300325, -84.4300325` |
| `EntryStreetName` | `object` | 8148 | 0.951% | 1,723 | `Marietta Boulevard Northwest, Marietta Boulevard Northwest` |
| `ExitStreetName` | `object` | 6287 | 0.734% | 1,703 | `Marietta Boulevard Northwest, Marietta Boulevard Northwest` |
| `EntryHeading` | `object` | 0 | 0.0% | 8 | `NW, SE` |
| `ExitHeading` | `object` | 0 | 0.0% | 8 | `NW, SE` |
| `Hour` | `int64` | 0 | 0.0% | 24 | `0, 0` |
| `Weekend` | `int64` | 0 | 0.0% | 2 | `0, 0` |
| `Month` | `int64` | 0 | 0.0% | 9 | `6, 6` |
| `Path` | `object` | 0 | 0.0% | 15,075 | `Marietta Boulevard Northwest_NW_Marietta Boulevard Northwest_NW, Marietta Boulevard Northwest_SE_Marietta Boulevard Northwest_SE` |
| `TotalTimeStopped_p20` | `float64` | 0 | 0.0% | 171 | `0.0, 0.0` |
| `TotalTimeStopped_p40` | `float64` | 0 | 0.0% | 238 | `0.0, 0.0` |
| `TotalTimeStopped_p50` | `float64` | 0 | 0.0% | 262 | `0.0, 0.0` |
| `TotalTimeStopped_p60` | `float64` | 0 | 0.0% | 306 | `0.0, 0.0` |
| `TotalTimeStopped_p80` | `float64` | 0 | 0.0% | 403 | `0.0, 0.0` |
| `TimeFromFirstStop_p20` | `float64` | 0 | 0.0% | 244 | `0.0, 0.0` |
| `TimeFromFirstStop_p40` | `float64` | 0 | 0.0% | 316 | `0.0, 0.0` |
| `TimeFromFirstStop_p50` | `float64` | 0 | 0.0% | 336 | `0.0, 0.0` |
| `TimeFromFirstStop_p60` | `float64` | 0 | 0.0% | 353 | `0.0, 0.0` |
| `TimeFromFirstStop_p80` | `float64` | 0 | 0.0% | 355 | `0.0, 0.0` |
| `DistanceToFirstStop_p20` | `float64` | 0 | 0.0% | 3,631 | `0.0, 0.0` |
| `DistanceToFirstStop_p40` | `float64` | 0 | 0.0% | 6,415 | `0.0, 0.0` |
| `DistanceToFirstStop_p50` | `float64` | 0 | 0.0% | 7,751 | `0.0, 0.0` |
| `DistanceToFirstStop_p60` | `float64` | 0 | 0.0% | 9,826 | `0.0, 0.0` |
| `DistanceToFirstStop_p80` | `float64` | 0 | 0.0% | 13,689 | `0.0, 0.0` |
| `City` | `object` | 0 | 0.0% | 4 | `Atlanta, Atlanta` |

---

## 2. City & Spatial Distributions

| City | Rows Count | Intersections | Latitude Range | Longitude Range |
|---|---|---|---|---|
| **Atlanta** | 156,484 | 377 | [33.64997, 33.83488] | [-84.53519, -84.291] |
| **Boston** | 178,617 | 975 | [42.23723, 42.38178] | [-71.17265, -71.02555] |
| **Chicago** | 131,049 | 2,135 | [41.64672, 41.97331] | [-87.86229, -87.52641] |
| **Philadelphia** | 390,237 | 1,318 | [39.8837, 40.04503] | [-75.27228, -75.02186] |

---

## 3. Percentile Monotonicity & Behavioral Integrity

- **Negative Values**: TotalTimeStopped: 0, TimeFromFirstStop: 0, DistanceToFirstStop: 0
- **Monotonic Violations** ($p20 \le p40 \le p50 \le p60 \le p80$):
  - `TotalTimeStopped`: 0 violations
  - `TimeFromFirstStop`: 0 violations
  - `DistanceToFirstStop`: 0 violations

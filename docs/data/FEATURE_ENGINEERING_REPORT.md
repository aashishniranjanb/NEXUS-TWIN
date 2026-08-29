# Feature Engineering Report — BigQuery-Geotab Dataset

| Metric | Value |
|---|---|
| **Rows** | 856,387 |
| **Total Columns** | 46 |
| **Safe Context Features** | 21 |
| **Behavioral Targets** | 15 |
| **Matrix Size** | 19.32 MB (Parquet) |

---

## 1. Safe Context Features (Inference-Time Legitimate)
These 21 features contain **zero target leakage** and represent conditions observable prior to measuring vehicle queues/delays:

| Feature Name | Type | Description |
|---|---|---|
| `IntersectionId` | `int32` | Physical intersection identifier |
| `Latitude` | `float32` | Geographic latitude |
| `Longitude` | `float32` | Geographic longitude |
| `entry_heading_deg` | `float32` | Compass bearing for entry direction ($0^\circ - 315^\circ$) |
| `exit_heading_deg` | `float32` | Compass bearing for exit direction ($0^\circ - 315^\circ$) |
| `heading_delta` | `float32` | Angular change in travel direction ($0^\circ - 360^\circ$) |
| `turn_type_encoded` | `int8` | 0: Straight, 1: Right, 2: Left, 3: U-Turn |
| `is_same_street` | `int8` | Binary flag (1 if entry street == exit street) |
| `entry_street_missing` | `int8` | Binary missingness indicator |
| `exit_street_missing` | `int8` | Binary missingness indicator |
| `Hour` | `int8` | Clock hour ($0 - 23$) |
| `hour_sin` | `float32` | $\sin(2\pi \cdot \text{Hour} / 24)$ |
| `hour_cos` | `float32` | $\cos(2\pi \cdot \text{Hour} / 24)$ |
| `month_sin` | `float32` | $\sin(2\pi \cdot \text{Month} / 12)$ |
| `month_cos` | `float32` | $\cos(2\pi \cdot \text{Month} / 12)$ |
| `is_peak_hour` | `int8` | Rush hour flag (7-9 AM, 4-6 PM) |
| `is_night` | `int8` | Night hours flag (10 PM - 5 AM) |
| `is_weekend` | `int8` | Binary weekend flag (0: Weekday, 1: Weekend) |
| `city_encoded` | `int8` | 0: Atlanta, 1: Boston, 2: Chicago, 3: Philadelphia |
| `intersection_log_freq`| `float32` | $\log(1 + \text{intersection count})$ |
| `path_log_freq` | `float32` | $\log(1 + \text{path count})$ |

---

## 2. Turn Type Distribution
- **Straight**: 597,681 (69.8%)
- **Left**: 130,703 (15.3%)
- **Right**: 127,360 (14.9%)
- **U-Turn**: 643 (0.1%)

---

## 3. Anti-Leakage Boundary
All 15 target percentiles (`TotalTimeStopped_p20/40/50/60/80`, `TimeFromFirstStop_p20/40/50/60/80`, `DistanceToFirstStop_p20/40/50/60/80`) are strictly isolated from the safe context feature matrix.

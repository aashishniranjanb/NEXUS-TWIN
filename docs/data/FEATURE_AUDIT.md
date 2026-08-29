# Feature Engineering Audit

| Feature Name | Type | Mathematical Definition | Status | Risk / Audit Note |
|---|---|---|---|---|
| `IntersectionId` | `int32` | Raw spatial junction identifier | **PASS** | Categorical ID, low leakage risk |
| `Latitude` | `float32` | Bounded floating point ($33.6^\circ$ to $42.4^\circ$) | **PASS** | Valid geographic coordinate |
| `Longitude` | `float32` | Bounded floating point ($-87.9^\circ$ to $-71.0^\circ$) | **PASS** | Valid geographic coordinate |
| `entry_heading_deg` | `float32` | Compass bearing map: $\text{N}\to 0^\circ, \text{NE}\to 45^\circ, \dots$ | **PASS** | Continuous geometric feature |
| `exit_heading_deg` | `float32` | Compass bearing map: $\text{N}\to 0^\circ, \text{NE}\to 45^\circ, \dots$ | **PASS** | Continuous geometric feature |
| `heading_delta` | `float32` | $(\theta_{\text{exit}} - \theta_{\text{entry}}) \pmod{360}$ | **PASS** | Exact turning angle magnitude |
| `turn_type_encoded` | `int8` | Straight (0), Right (1), Left (2), U-Turn (3) | **PASS** | Top predictive feature (22.8% importance) |
| `is_same_street` | `int8` | $\mathbb{I}(\text{EntryStreetName} == \text{ExitStreetName})$ | **PASS** | Key through-traffic indicator (9.4% importance) |
| `entry_street_missing` | `int8` | $\mathbb{I}(\text{EntryStreetName} == \text{"UNKNOWN"})$ | **PASS** | Missingness indicator, preserves information |
| `exit_street_missing` | `int8` | $\mathbb{I}(\text{ExitStreetName} == \text{"UNKNOWN"})$ | **PASS** | Missingness indicator, preserves information |
| `Hour` | `int8` | Discrete clock hour ($0 - 23$) | **PASS** | Temporal context |
| `hour_sin` | `float32` | $\sin(2\pi \cdot \text{Hour} / 24)$ | **PASS** | Seamless circular 24h cycle |
| `hour_cos` | `float32` | $\cos(2\pi \cdot \text{Hour} / 24)$ | **PASS** | Seamless circular 24h cycle |
| `month_sin` | `float32` | $\sin(2\pi \cdot \text{Month} / 12)$ | **PASS** | Seasonal cycle |
| `month_cos` | `float32` | $\cos(2\pi \cdot \text{Month} / 12)$ | **PASS** | Seasonal cycle |
| `is_peak_hour` | `int8` | $\mathbb{I}(\text{Hour} \in \{7,8,9,16,17,18\})$ | **PASS** | Empirically verified rush hour windows |
| `is_night` | `int8` | $\mathbb{I}(\text{Hour} \in \{22,23,0,1,2,3,4,5\})$ | **PASS** | Free-flow low traffic window |
| `is_weekend` | `int8` | $\mathbb{I}(\text{Weekend} == 1)$ | **PASS** | Distinct commute vs leisure pattern |
| `city_encoded` | `int8` | Atlanta (0), Boston (1), Chicago (2), Philadelphia (3) | **PASS** | Metropolitan area encoding |
| `intersection_log_freq` | `float32` | $\log(1 + \text{count}_{\text{train}}(\text{IntersectionId}))$ | **REMEDIATED** | Refactored to fit strictly on training split |
| `path_log_freq` | `float32` | $\log(1 + \text{count}_{\text{train}}(\text{Path}))$ | **REMEDIATED** | Refactored to fit strictly on training split |

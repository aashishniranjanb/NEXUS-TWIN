# Prediction Target Definition & Model Design

## 1. Primary Target Selection
- **Target**: `TotalTimeStopped_p50` (Continuous float $\ge 0.0$, measured in seconds).
- **Physical Interpretation**: The 50th percentile (median) total vehicle stopping duration at a specific intersection, approach heading, turn movement, and hour of the day.
- **Secondary Quantile Targets**: `TotalTimeStopped_p20`, `TotalTimeStopped_p80`, and `DistanceToFirstStop_p50`.

## 2. Leakage Gate & Feature Policy
To prevent data leakage, **only safe contextual features** known at inference time are used:
1. `IntersectionId` (Spatial Identity)
2. `Latitude`, `Longitude` (Physical Geography)
3. `entry_heading_deg`, `exit_heading_deg`, `heading_delta`, `turn_type_encoded` (Movement Geometry)
4. `is_same_street`, `entry_street_missing`, `exit_street_missing` (Roadway Attributes)
5. `Hour`, `hour_sin`, `hour_cos`, `month_sin`, `month_cos`, `is_peak_hour`, `is_night`, `is_weekend` (Temporal Cycles)
6. `city_encoded`, `intersection_log_freq`, `path_log_freq` (Context Density)

## 3. Disallowed Features (Target Family)
The following columns are **STRICTLY EXCLUDED** from model training:
- `TotalTimeStopped_p20`, `p40`, `p60`, `p80`
- `TimeFromFirstStop_p20`, `p40`, `p50`, `p60`, `p80`
- `DistanceToFirstStop_p20`, `p40`, `p50`, `p60`, `p80`
- `RowId`

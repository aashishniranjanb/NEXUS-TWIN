# Leakage Audit & Feature Availability Gate

## 1. Contextual Features (Legitimate at Inference Time)
These features describe the external physical and temporal context available prior to observing traffic behavior:
- `IntersectionId`, `Latitude`, `Longitude`
- `EntryStreetName`, `ExitStreetName` (with `UNKNOWN` imputation)
- `EntryHeading`, `ExitHeading`
- `Hour`, `Weekend`, `Month`
- `City`, `Path`
- **Engineered cyclical / spatial / heading features**

## 2. Behavioral Measurement Family (Contemporaneous Targets)
These features represent measurements taken during the aggregated time window:
- `TotalTimeStopped_p20`, `p40`, `p50`, `p60`, `p80`
- `TimeFromFirstStop_p20`, `p40`, `p50`, `p60`, `p80`
- `DistanceToFirstStop_p20`, `p40`, `p50`, `p60`, `p80`

## 3. The Strict Leakage Gate Rule
> **LEAKAGE GATE ENFORCEMENT**: When predicting `TotalTimeStopped_p50` (or any single percentile target), **NO OTHER BEHAVIORAL PERCENTILE** from the same row may be fed into the model. Feeding contemporaneous `p20`, `p40`, or `DistanceToFirstStop` yields artificial accuracy that cannot exist in real-world deployment where those sensor percentiles are not yet observed.

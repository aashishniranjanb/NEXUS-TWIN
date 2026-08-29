# Exploratory Data Analysis (EDA) Report — Urban Traffic Dynamics

| Metric | Finding |
|---|---|
| **Total Analyzed Observations** | 856,387 |
| **Morning Peak Hour** | **8:00** |
| **Evening Peak Hour** | **16:00** |
| **Global Mean p50 Stopped Time** | **7.72 seconds** |
| **Global Median p50 Stopped Time** | **0.0 seconds** |

---

## 1. Key Research Findings

### Q1: Temporal Congestion Profile
- **Bimodal Peak**: Distinct morning peak at **8:00** and heavy evening peak at **16:00**.
- **Weekday vs. Weekend**: Weekday traffic shows steep commute spikes (7–9 AM and 4–7 PM), whereas weekend traffic exhibits a flatter, midday curve (12–4 PM).
- **Night Traffic**: 11 PM – 5 AM averages lowest stopping times (<4s p50 median).

### Q2: Spatial & City Heterogeneity
Average stopped times differ significantly across metropolitan corridors:
- **Atlanta**: 9.74s mean stopped duration
- **Boston**: 8.6s mean stopped duration
- **Chicago**: 7.14s mean stopped duration
- **Philadelphia**: 6.71s mean stopped duration

### Q3: Movement & Turn Dynamics
Stopping delay is heavily dictated by movement direction:
- **Left**: 15.58s mean stopped duration
- **Right**: 8.58s mean stopped duration
- **Straight**: 5.81s mean stopped duration
- **U-Turn**: 21.22s mean stopped duration

- **Left Turns & U-Turns**: Cause significantly higher queue accumulation and waiting delay due to conflicting oncoming phases and permissive/protected signal cycles.

### Q4: Identification of High-Congestion Hotspots
Top recurring bottleneck intersections identified across cities:
- **Boston Intersection #35**: 52.15s average wait (306 observations)
- **Philadelphia Intersection #463**: 46.22s average wait (559 observations)
- **Boston Intersection #100**: 43.34s average wait (213 observations)
- **Boston Intersection #997**: 41.43s average wait (295 observations)
- **Boston Intersection #171**: 41.07s average wait (246 observations)

---

## 2. Intelligence & Fingerprint Implications
1. **Normal vs. Recurring Congestion**: A high delay at 5 PM at a bottleneck intersection is **RECURRING_CONGESTION** (within the historical peak envelope).
2. **Incident-Like Signatures**: A sudden 3x spike in stopped time during off-peak hours (e.g. 2 AM or 11 AM) on a single approach is **INCIDENT_LIKE**.
3. **Demand Surge Signatures**: Simultaneous elevation across multiple turn movements and approaches with normal discharge indicates a **DEMAND_SURGE**.

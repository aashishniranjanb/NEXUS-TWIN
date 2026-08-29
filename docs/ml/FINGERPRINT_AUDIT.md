# Traffic Fingerprint Audit & Grounding Verification

| Diagnostic Class | Nature of Logic | Source Variables Used | Grounding Verification |
|---|---|---|---|
| **`NORMAL`** | Statistical Envelope Rule | `observed_wait_s`, `base_stats['median_wait_s']`, `waiting_time_z`, `anom_score` | **PASS** — Grounded in historical percentile envelope. |
| **`RECURRING_CONGESTION`** | Temporal Peak + Envelope Rule | `is_peak`, `Hour`, `observed_wait_s`, `base_stats['p80_wait_s']` | **PASS** — Grounded in rush-hour commute periods where wait is elevated but within historical peak envelope. |
| **`INCIDENT_LIKE`** | Outlier Deviation Rule | `waiting_time_z > 2.0`, `observed_wait_s > p80_wait`, `speed_drop_ratio > 0.5`, `dir_imbalance >= 1.0` | **PASS** — Grounded in severe abnormal multi-sigma delay spikes. |
| **`DEMAND_SURGE`** | Symmetrical Volume Surge Rule | `observed_wait_s > p80_wait`, `dir_imbalance < 1.2`, multi-heading presence | **PASS** — Grounded in broad multi-directional elevation. |
| **`SIGNAL_RELATED`** | Discharge Efficiency Fallback | Delay deviation without localized blockage signature | **PASS** — Grounded in non-directional discharge delay. |

---

## 1. Prohibited Unsupported Claims (Audited & Blocked)
1. **Accident Detection**: The word "ACCIDENT" or "COLLISION" must **never** be output as a fact. The pipeline outputs `INCIDENT_LIKE` as a behavioral anomaly pattern with an explicit disclaimer.
2. **Signal Hardware Failure**: The pipeline outputs `SIGNAL_RELATED` to indicate discharge inefficiency, not a claim of physical bulb/controller hardware damage.
3. **Continuous Traffic Volume**: Aggregate telematics counts represent observed sample vehicles, not 100% census volume.

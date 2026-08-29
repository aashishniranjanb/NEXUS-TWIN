# Traffic Fingerprint Semantic Diagnostics

| Field | Value |
|---|---|
| **Status** | Level-1 Active |
| **Owner** | Traffic Fingerprint Engineer (A9) |

---

## 1. The 5 Diagnostic Classes

| Class | Semantic Meaning | Discriminator Signals |
|---|---|---|
| **`NORMAL`** | Traffic within expected historical bounds | Low anomaly score (<0.45), wait time $\le$ historical p80. |
| **`RECURRING_CONGESTION`** | Expected peak commute congestion | High wait time occurring during rush hours (7–9 AM, 4–7 PM) with balanced directional flow. |
| **`INCIDENT_LIKE`** | Severe unexpected localized disruption | Sharp off-peak wait spike ($z > 2.0$), severe speed drop ($>60\%$), high directional concentration ($z > 1.0$). |
| **`DEMAND_SURGE`** | Broad network volume surge | High wait time simultaneously elevated across multiple headings with low directional imbalance. |
| **`SIGNAL_RELATED`** | Signal cycle or phase inefficiency | Delay deviates from baseline across symmetrical movements without localized blockage signatures. |

## 2. Responsible AI & Causal Disclaimer
> **MANDATORY POLICY**: Telematics data alone cannot verify physical accidents or broken signals. The system classifies **statistical behavioral signatures** (`INCIDENT_LIKE`, `SIGNAL_RELATED`) and includes an explicit limitation disclaimer in every response.

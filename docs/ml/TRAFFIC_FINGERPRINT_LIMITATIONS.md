# Traffic Fingerprint Limitations & Responsible AI Notice

| Limitation | Impact | Mitigation Strategy |
|---|---|---|
| **No Video / Vision Feeds** | Cannot confirm physical collision or vehicle breakdown | Classify as `INCIDENT_LIKE` pattern; present contributing deviation signals to human operator. |
| **No Direct Signal Phase Data** | Signal timing is inferred from aggregate discharge delay | Classify as `SIGNAL_RELATED` pattern; do not claim electrical or controller hardware faults. |
| **Sample Fleet Penetration** | Geotab telematics represents commercial fleet vehicles (trucks, vans) | Calibrate queues as relative index proxies rather than absolute census traffic volume. |
| **Aggregated Time Windows** | Metrics represent aggregated periods | Dynamic second-by-second changes are simulated via the Digital Twin scenario engine. |

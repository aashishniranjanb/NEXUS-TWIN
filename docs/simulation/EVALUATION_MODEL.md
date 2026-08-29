# Simulation Evaluation & Strategy Ranking Model

| Metric | Dimension | Formula / Source |
|---|---|---|
| **Total Vehicular Delay** | Vehicle-Hours (veh-hrs) | $\int \text{Queue}(t) \, dt$ over 900s horizon |
| **Average Stopped Time** | Seconds (s) | Webster's uniform + incremental delay formula |
| **Max Queue Accumulation** | Meters (m) | Peak residual vehicles $\times 7.5\text{m/veh}$ |
| **Corridor Throughput** | Veh / Hour | Cumulative completed corridor transits |
| **Spillover Risk Score** | $[0.0, 1.0]$ | $\min\left(1.0, \frac{Q_{\text{max}}}{250.0} \cdot \frac{V}{C}\right)$ |
| **Composite Score** | $0 - 100$ | $100 - 0.6 \cdot \text{Wait} - 0.1 \cdot \text{Queue} + 0.02 \cdot \text{Throughput}$ |

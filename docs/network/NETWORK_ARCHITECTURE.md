# Traffic Network Architecture & Graph Topology

| Component | Technology | Specification |
|---|---|---|
| **Graph Model** | NetworkX Directed Graph (`DiGraph`) | Nodes = Intersections ($J_i$), Edges = Directional Arterial Links |
| **Data Provenance** | BigQuery-Geotab Dataset | Real spatial coordinates, road names, and empirical traffic volumes |
| **Node State** | `NodeTrafficState` | Congestion score ($[0,1]$), predicted stopped time (s), queue (m), bottleneck status |
| **Edge State** | `EdgeTrafficState` | Distance (m), free-flow travel time, current travel time, capacity, flow |

---

## 1. Network Topology Construction
Intersections are identified from empirical Geotab coordinates and clustered into cohesive urban arterial corridors (e.g. Market St, Broad St, Chestnut St). Directional edges link adjacent intersections within urban block thresholds ($180\text{m} - 1200\text{m}$), establishing the physical substrate for congestion propagation analysis.

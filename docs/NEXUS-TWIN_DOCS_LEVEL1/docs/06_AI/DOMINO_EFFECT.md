# CONGESTION DOMINO EFFECT

| Field | Value |
|---|---|
| Status | Level-1 (authoritative) |
| Priority | P0 — MUST |
| Owner | Laptop 2 |
| Consumers | Domino panel, map overlay, Intervention Window, Strategy Engine |

---

## 1. Purpose

Answer where congestion will spread and how soon, instead of reporting that one junction is
congested. This is the capability that distinguishes NEXUS-TWIN from a dashboard: dashboards
report nodes, corridors fail as networks.

## 2. Scope

Risk propagation across the J1–J2–J3 corridor graph from a source junction, producing per-neighbour
risk and time-to-impact, plus the derived intervention window. Route assignment and traffic
reassignment modelling are out of scope.

## 3. Inputs

| Input | Source |
|---|---|
| Source junction and its congestion probability | XGBoost prediction |
| Corridor graph (nodes, directed edges, lengths, capacities) | `corridor_graph.json` from Geotab coordinates and street names |
| Current per-junction state | Traffic State Service |
| Baseline capacity and discharge per link | Geotab-derived baselines |
| Fingerprint class | Fingerprint service (modulates propagation speed) |

## 4. Graph

```
J1 <---> J2 <---> J3
```

| Element | Attributes |
|---|---|
| Node | `junction_id`, current queue, capacity, saturation |
| Edge | `from`, `to`, `length_m`, `free_flow_speed_kmh`, `capacity_veh_h`, `storage_veh` |

Built with NetworkX as a directed graph; each physical street becomes two directed edges, since
spillback travels upstream while flow disruption travels downstream and the two behave differently.

## 5. Propagation model

Two distinct mechanisms, not one generic "spread":

| Mechanism | Direction | Physical meaning |
|---|---|---|
| `upstream_queue_spillback` | Against traffic flow | The queue physically reaches back into the upstream junction and blocks it |
| `downstream_flow_disruption` | With traffic flow | Platoons arrive irregularly, degrading downstream progression |
| `shared_demand` | Either | Both junctions serve the same corridor demand |

### Risk

For a neighbour `n` at graph distance `d` from source `s`:

```
risk(n) = risk(s) · attenuation(d) · saturation_factor(n) · mechanism_weight(m)
```

| Term | Definition |
|---|---|
| `attenuation(d)` | `exp(-λ·d)` with λ = 0.35 per hop, from `configs/domino_params.json` |
| `saturation_factor(n)` | `min(1.4, 0.6 + current_queue(n)/capacity(n))` — an already-loaded junction absorbs less |
| `mechanism_weight` | 1.0 upstream spillback, 0.6 downstream disruption, 0.4 shared demand |

Risk is clamped to `[0,1]`. Upstream is weighted higher because a queue that physically reaches
the upstream stop line blocks it outright, whereas downstream effects degrade progression more
gradually.

### Time to impact

```
eta_minutes = (available_storage_m(edge) / queue_growth_rate_m_per_min) + free_flow_travel_time_min
```

| Term | Source |
|---|---|
| `available_storage_m` | `edge.length_m − current_queue_m` on the connecting link |
| `queue_growth_rate_m_per_min` | Observed growth at the source over the recent window |
| `free_flow_travel_time_min` | `length_m / free_flow_speed` |

The ETA is physical, not a fitted constant: it is the time for the growing queue to consume the
remaining storage on the link between the two junctions. That is why it changes when growth rate
changes, and why a judge can be shown the arithmetic.

Growth rate below 1 m/min returns `eta_minutes: null` and `risk` reduced by half — a queue that is
not growing is not going to spill over.

## 6. Intervention window

```
remaining_seconds = min(eta_minutes over neighbours with risk ≥ 0.5) · 60 − strategy_lead_time_s
```

`strategy_lead_time_s` defaults to 60 s: the time to simulate, decide, and apply.

| Status | Condition |
|---|---|
| `CRITICAL` | ≤ 5 minutes remaining |
| `WARNING` | 5–10 minutes |
| `CLEAR` | > 10 minutes, or no neighbour above the risk floor |

| Urgency | Condition |
|---|---|
| `ACT_NOW` | `CRITICAL` |
| `PREPARE` | `WARNING` |
| `MONITOR` | `CLEAR` |

This is the answer to the third question most traffic systems never ask: not just where and what,
but *when*.

## 7. Output

```json
{
  "source": { "junction_id": "J2", "risk": 0.87 },
  "propagation": [
    { "junction_id": "J1", "risk": 0.73, "eta_minutes": 4, "path": ["J2","J1"], "mechanism": "upstream_queue_spillback" },
    { "junction_id": "J3", "risk": 0.41, "eta_minutes": 7, "path": ["J2","J3"], "mechanism": "downstream_flow_disruption" }
  ],
  "intervention_window": {
    "status": "CRITICAL",
    "remaining_seconds": 360,
    "expires_at": "2026-08-29T10:20:03Z",
    "consequence": "Predicted spillover reaches J1.",
    "urgency": "ACT_NOW"
  }
}
```

Sorted by risk descending. Neighbours below `risk_floor` (0.15) are omitted rather than listed as
noise.

## 8. Visualisation requirements

This must be the strongest visual element in the product.

| Element | Requirement |
|---|---|
| Arrows | Animated along real link geometry, source to neighbour, direction matching the mechanism |
| Arrow weight | Proportional to risk |
| Arrow speed | Inversely proportional to ETA — nearer impacts visibly move faster |
| Labels | `73% · 4 min` adjacent to each arrow |
| Junction highlight | Pulsing ring on at-risk junctions, intensity by risk |
| Countdown | Intervention window timer, colour-coded by status |
| Ordering | Highest risk animates first |

The visual encodes both risk and urgency simultaneously, which is what makes it read as a command
centre rather than a chart.

## 9. Interfaces

| Interface | Detail |
|---|---|
| API | `POST /api/domino/predict` |
| Tools | `predict_spillover`, `compute_intervention_window` |
| Contract | `DominoForecast` in `shared/contracts/domino.ts` |
| Persistence | `domino_predictions` |
| Frontend | Domino panel, map overlay, Intervention Window banner |

## 10. Dependencies

NetworkX, `corridor_graph.json`, current state, prediction output. No LLM involvement.

## 11. Failure modes

| Failure | Behaviour |
|---|---|
| Graph missing | Fall back to a hardcoded three-node chain from `ids.yaml`, flagged `degraded` |
| Prediction unavailable | Use current saturation as source risk, lower confidence |
| Growth rate zero or negative | `eta_minutes: null`, risk halved, status `CLEAR` |
| Neighbour already saturated | Risk capped at 1.0 with `already_congested: true` |
| Disconnected graph | Return the source only, with an empty `propagation` |

## 12. Testing

| Test | Assertion |
|---|---|
| Known state, known growth | ETA matches the hand-computed storage/growth value within 10% |
| Ordering | Upstream neighbour ranks above downstream at equal distance |
| Attenuation | Risk decreases monotonically with hop distance |
| Zero growth | `eta_minutes` is null and status is `CLEAR` |
| Clamping | No risk outside `[0,1]`, no negative ETA |
| Simulation agreement | Predicted spillover order matches simulated order in ≥ 80% of runs |
| Determinism | Same input, same output |

## 13. Acceptance criteria

1. Two mechanisms distinguished and labelled in the output.
2. ETA derived from link storage and growth rate, not a constant.
3. Intervention window derived from the earliest qualifying ETA.
4. Map animation reflects both risk and time-to-impact.
5. Predicted ordering validated against the Digital Twin.

## 14. Future work

Multi-hop propagation across a larger network, learned propagation via a graph neural network,
probabilistic ETAs with confidence intervals, feedback loops where downstream congestion worsens
the source.

# Frontend Integration Contract: NEXUS-TWIN Backend API

| Field | Value |
|---|---|
| **Base URL** | `http://localhost:8000` |
| **API Version** | `1.0.0` |
| **Protocol** | REST JSON + Server-Sent Events (SSE) |
| **CORS** | Enabled for all origins (`*`) |

---

## 1. Primary Endpoint: Unified Decision Analysis

### `POST /api/v1/demo/analyze`
Executes the full 10-stage intelligence pipeline in a single synchronous call.

#### Request Payload
```json
{
  "city": "Philadelphia",
  "intersection_id": 0,
  "scenario": "INCIDENT_LIKE_DISRUPTION",
  "emergency_mode": false,
  "hour": 17,
  "weekend": 0,
  "seed": 42
}
```

#### Response Payload (`200 OK`)
```json
{
  "traffic_state": {
    "intersection_id": 0,
    "city": "Philadelphia",
    "name": "Junction #0 (NW->SE)",
    "latitude": 39.9526,
    "longitude": -75.1652,
    "turn_type": "Straight",
    "predicted_stopped_time_s": 64.3,
    "historical_baseline_median_s": 5.0,
    "historical_baseline_p80_s": 15.0,
    "congestion_score": 1.0,
    "severity": "CRITICAL",
    "estimated_queue_m": 87.9,
    "evidence": [
      "Predicted median stopped time is 64.3s for Straight movement (NW->SE).",
      "Wait time is 328.7% above historical 80th percentile baseline (15.0s)."
    ]
  },
  "prediction": {
    "target": "TotalTimeStopped_p50",
    "predicted_value_s": 64.3,
    "prediction_type": "Contextual Stopping Delay Expectation",
    "model": "XGBoost Regressor v1.0 (Histogram Method)",
    "confidence": 0.893
  },
  "anomaly": {
    "anomaly_score": 0.567,
    "anomaly_detected": true,
    "severity": "MODERATE",
    "top_contributing_signals": [
      "waiting_time_z (z=+9.39)",
      "directional_imbalance (z=+4.70)"
    ],
    "feature_deviations": {
      "waiting_time_z": 9.39,
      "distance_z": 0.14,
      "speed_drop_ratio": 0.87,
      "directional_imbalance": 4.70
    },
    "method": "IsolationForest + Multi-ZScore"
  },
  "fingerprint": {
    "classification": "INCIDENT_LIKE",
    "confidence": 0.842,
    "severity": "MODERATE",
    "evidence": [
      "Sudden abnormal stopping time spike (64.3s > p80 15.0s, z=+9.39) with severe speed drop (87%).",
      "Delay is concentrated along specific entry heading (NW) inconsistent with ambient traffic."
    ],
    "contributing_signals": [
      "waiting_time_z (z=+9.39)",
      "directional_imbalance (z=+4.70)"
    ],
    "historical_comparison": {
      "observed_wait_s": 64.3,
      "baseline_mean_wait_s": 8.0,
      "baseline_median_wait_s": 5.0,
      "baseline_p80_wait_s": 15.0,
      "waiting_time_z_score": 9.387
    },
    "limitation_disclaimer": "INCIDENT_LIKE / SIGNAL_RELATED fingerprint indicates statistical pattern deviation and does not verify physical collision or hardware fault without secondary ground-truth."
  },
  "network": {
    "total_nodes": 8,
    "total_edges": 16,
    "affected_nodes_count": 1,
    "overall_spillover_risk": 0.302,
    "domino_sequence": ["J24", "J1672"],
    "domino_steps": [
      {
        "step_index": 1,
        "from_node": 24,
        "from_name": "Junction #24",
        "to_node": 1672,
        "to_name": "Junction #1672",
        "transit_distance_m": 720.0,
        "cumulative_delay_s": 105.4,
        "estimated_time_to_impact_min": 2.9,
        "impact_severity": "MODERATE"
      }
    ],
    "network_exposure_index": 0.520,
    "containment_status": "ACTIVE_CONGESTION_LOCALIZED",
    "nodes_summary": [
      { "id": 0, "name": "Market & 15th", "congestion_score": 1.0, "queue_m": 87.9, "is_bottleneck": true }
    ],
    "edges_summary": [
      { "source": 0, "target": 1, "street": "Market St", "distance_m": 350.0, "congestion_ratio": 3.5 }
    ]
  },
  "strategies": [
    {
      "strategy_id": "STRAT_DIVERT_TRAFFIC",
      "strategy_type": "DIVERT_TRAFFIC",
      "name": "Upstream Dynamic Diversion (25%)",
      "rank": 1,
      "delay_reduction_pct": 28.5,
      "queue_reduction_pct": 66.8,
      "throughput_gain_pct": 5.2,
      "emergency_speedup_pct": null,
      "composite_score": 38.6,
      "description": "Activate Variable Message Signs 500m upstream to reroute 25% of inflow to parallel corridors.",
      "trade_offs": "Eliminates bottleneck shockwave; increases travel distance on secondary network by 400m.",
      "evidence": [
        "Reduces average stopping delay by 28.5%.",
        "Cuts maximum vehicle queue accumulation by 66.8%."
      ]
    }
  ],
  "recommendation": {
    "strategy_id": "STRAT_DIVERT_TRAFFIC",
    "strategy_type": "DIVERT_TRAFFIC",
    "name": "Upstream Dynamic Diversion (25%)",
    "rank": 1,
    "delay_reduction_pct": 28.5,
    "queue_reduction_pct": 66.8,
    "throughput_gain_pct": 5.2,
    "emergency_speedup_pct": null,
    "composite_score": 38.6,
    "reason": "Achieves highest network recovery score (38.6/100) and eliminates 66.8% of vehicular queues.",
    "evidence": [
      "Reduces average stopping delay by 28.5%.",
      "Cuts maximum vehicle queue accumulation by 66.8%."
    ],
    "trade_offs": "Eliminates bottleneck shockwave; increases travel distance on secondary network by 400m."
  },
  "responsible_ai": {
    "safety_status": "CONDITIONAL_APPROVAL",
    "critic_score": 78.0,
    "risk_level": "MODERATE",
    "verified_evidence_checks": [
      "Digital Twin quantitative simulation evidence verified (900s kinematic model)."
    ],
    "identified_hazards": [],
    "human_override_required": true,
    "reasoning": "Approved with operational warnings: minor volume diversion to secondary network."
  },
  "explainability": {
    "action": "AI Decision Copilot recommends 'Upstream Dynamic Diversion (25%)' to mitigate incident like disruption at Junction #0 (Philadelphia).",
    "why": "Selected because it delivers the highest composite network recovery score (38.6/100), clearing 66.8% of vehicular queues.",
    "evidence": [
      "Baseline: 140.0s delay, 264.4m queue.",
      "Upstream Dynamic Diversion (25%): 100.1s delay (-28.5%), 87.9m queue (-66.8%)."
    ],
    "trade_off_analysis": "Eliminates bottleneck shockwave; increases travel distance on secondary network by 400m.",
    "confidence_statement": "Confidence is 92% based on deterministic kinematic flow convergence over 900 simulation seconds.",
    "limitations": "Observational telematics cannot verify physical collision or hardware faults without secondary confirmation."
  },
  "metadata": {
    "pipeline_version": "1.0.0",
    "dataset": "BigQuery-Geotab Empirical Telematics (856k rows)",
    "timestamp": "2026-08-29T09:14:35Z",
    "seed": 42,
    "execution_time_ms": 5170.3
  }
}
```

---

## 2. Progressive Streaming Endpoint (SSE)

### `GET /api/v1/decision/stream?city=Philadelphia&intersection_id=0&scenario=INCIDENT_LIKE_DISRUPTION`
Server-Sent Events connection streaming 12 progressive lifecycle stages for real-time UI animation.

#### Event Stream Sequence
```
event: traffic_state_received
data: {"stage": 1, "message": "Empirical Geotab observation loaded.", "city": "Philadelphia", "intersection_id": 0}

event: prediction_complete
data: {"stage": 2, "message": "XGBoost contextual delay prediction evaluated.", "target": "TotalTimeStopped_p50"}

event: anomaly_complete
data: {"stage": 3, "message": "Multi-dimensional standardized deviation space computed."}

event: fingerprint_complete
data: {"stage": 4, "message": "Diagnostic pattern classified."}

event: network_analysis_complete
data: {"stage": 5, "message": "NetworkX corridor shockwave and domino cascade chain computed."}

event: strategies_generated
data: {"stage": 6, "message": "4 candidate intervention strategies formulated."}

event: simulation_started
data: {"stage": 7, "message": "Starting 900s Digital Twin kinematic simulation horizon..."}

event: simulation_complete
data: {"stage": 8, "message": "Multi-strategy comparison complete.", "best_strategy": "Upstream Dynamic Diversion (25%)", "delay_reduction_pct": 28.5}

event: critic_complete
data: {"stage": 9, "message": "Responsible AI Safety Critic audit finished.", "safety_status": "CONDITIONAL_APPROVAL", "score": 78.0}

event: recommendation_ready
data: {"stage": 10, "message": "AI recommendation and explainability package generated.", "recommendation": {...}}

event: human_approval_required
data: {"stage": 11, "message": "Awaiting operator decision (APPROVE / OVERRIDE / REJECT).", "human_override_required": true}

event: pipeline_complete
data: {"stage": 12, "message": "Full pipeline execution complete.", "payload": {...}}
```

---

## 3. Human Decision & Field Actuation Endpoint

### `POST /api/v1/decision/human-action`
Records operator approval, manual override, or rejection.

#### Request Payload
```json
{
  "event_id": "EVT_PHILADELPHIA_0_1724922875",
  "action": "APPROVE",
  "selected_strategy_id": "STRAT_DIVERT_TRAFFIC",
  "operator_notes": "Supervisor approved diversion to secondary corridor."
}
```

#### Response Payload (`200 OK`)
```json
{
  "event_id": "EVT_PHILADELPHIA_0_1724922875",
  "decision_id": "DEC_1724922890",
  "action": "APPROVE",
  "applied_strategy_id": "STRAT_DIVERT_TRAFFIC",
  "status": "DISPATCHED_TO_FIELD_SIGNALS",
  "projected_network_gain": "Immediate field actuation initiated: Expected 38.4% queue reduction along corridor.",
  "timestamp": "2026-08-29T09:14:50Z",
  "audit_trail": [
    "Event ID EVT_PHILADELPHIA_0_1724922875 processed by supervisor at 2026-08-29 14:44:50.",
    "Action 'APPROVE' recorded with strategy 'STRAT_DIVERT_TRAFFIC'.",
    "Field controller status: DISPATCHED_TO_FIELD_SIGNALS."
  ]
}
```

---

## 4. System Status Probe

### `GET /api/v1/system/status`
Returns live subsystem availability.

```json
{
  "backend_status": "OPERATIONAL",
  "service_version": "1.0.0",
  "ml_model_loaded": true,
  "isolation_forest_loaded": true,
  "network_intelligence_available": true,
  "digital_twin_engine_available": true,
  "agent_orchestrator_available": true,
  "dataset_connected": "BigQuery-Geotab Empirical Telematics (856,387 records)",
  "supported_cities": ["Philadelphia", "Boston", "Atlanta", "Chicago"],
  "timestamp": "2026-08-29T09:14:35Z"
}
```

---

## 5. AI Dynamic Route & Spillover Optimizer

### `POST /api/v1/routing/optimize`
Finds optimal routes and dynamic alternatives using travel times, congestion rates, shockwave spillover risk, and emergency corridor clearance flags.

#### Request Payload
```json
{
  "origin": 889,
  "destination": 463,
  "mode": "emergency",
  "city": "Philadelphia",
  "hour": 17,
  "weekend": 0
}
```

#### Response Payload (`200 OK`)
```json
{
  "origin": 889,
  "destination": 463,
  "mode": "emergency",
  "recommended_route": {
    "nodes": [889, 1422, 463],
    "edges": [
      {
        "source": 889,
        "target": 1422,
        "street": "Market St",
        "distance_m": 350.0,
        "congestion_ratio": 1.15
      },
      {
        "source": 1422,
        "target": 463,
        "street": "15th St",
        "distance_m": 410.0,
        "congestion_ratio": 1.05
      }
    ],
    "predicted_eta_s": 62.4,
    "congestion_risk": 0.1,
    "spillover_risk": 0.03
  },
  "alternatives": [
    {
      "nodes": [889, 902, 463],
      "edges": [...],
      "predicted_eta_s": 84.1,
      "congestion_risk": 0.45,
      "spillover_risk": 0.15
    }
  ],
  "comparison": {
    "baseline_eta_s": 92.6,
    "optimized_eta_s": 62.4,
    "eta_improvement_pct": 32.6
  },
  "reasoning": {
    "why": "Emergency corridor route preemption active. Avoided bottleneck at Junction #889 via dynamic secondary routing.",
    "evidence": [
      "Reduces emergency vehicle ETA by 30.2s (-32.6%).",
      "Corridor clearance active along path: 889 -> 1422 -> 463."
    ],
    "tradeoffs": [
      "Increases transit speed for ambulance; minor temporary signal pauses on cross-streets."
    ]
  },
  "metadata": {
    "version": "1.0.0",
    "city": "Philadelphia",
    "hour": 17,
    "seed": 42,
    "timestamp": "2026-08-29T09:47:12Z",
    "execution_time_ms": 12.5
  }
}
```

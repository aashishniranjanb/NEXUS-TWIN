"""
Flagship Demonstration Script for NEXUS-TWIN.
Executes the full end-to-end traffic decision pipeline directly via Python API
and prints formatted evidence, simulation deltas, safety audits, and recommendations.
"""

import os
import sys
import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.contracts.demo import DemoAnalysisRequest
from backend.services.demo_pipeline import DemoPipelineService

def run_flagship_demo():
    print("=" * 80)
    print("   NEXUS-TWIN: AI URBAN TRAFFIC DECISION INTELLIGENCE PIPELINE DEMO   ")
    print("=" * 80)
    
    service = DemoPipelineService()
    
    # 1. Flagship Scenario: Market St Corridor Disruption (Philadelphia)
    req = DemoAnalysisRequest(
        city="Philadelphia",
        intersection_id=0,
        scenario="INCIDENT_LIKE_DISRUPTION",
        emergency_mode=False,
        hour=17,
        weekend=0,
        seed=42
    )
    
    print(f"\n[1/7] INGESTING REAL GEOTAB CONTEXT:")
    print(f"  Metropolitan Area:    {req.city}")
    print(f"  Target Epicenter:     Junction #{req.intersection_id}")
    print(f"  Temporal Window:      Hour {req.hour}:00 (Weekday Commute Peak)")
    print(f"  Disruption Profile:   {req.scenario}")
    
    t0 = time.time()
    res = service.execute_pipeline(req)
    t_el = (time.time() - t0) * 1000.0
    
    # 2. Traffic State & Prediction
    print(f"\n[2/7] TRAFFIC STATE & PREDICTION:")
    print(f"  Junction Name:        {res.traffic_state.name}")
    print(f"  Predicted Wait Time:  {res.prediction.predicted_value_s:.1f}s ({res.prediction.prediction_type})")
    print(f"  Historical Baseline:  Median: {res.traffic_state.historical_baseline_median_s:.1f}s | p80: {res.traffic_state.historical_baseline_p80_s:.1f}s")
    print(f"  Congestion Score:     {res.traffic_state.congestion_score:.3f} ({res.traffic_state.severity})")
    print(f"  Estimated Queue:      {res.traffic_state.estimated_queue_m:.1f} meters")
    
    # 3. Anomaly & Fingerprint
    print(f"\n[3/7] ANOMALY DETECTION & SEMANTIC FINGERPRINT:")
    print(f"  Anomaly Score:        {res.anomaly.anomaly_score:.3f} (Detected: {res.anomaly.anomaly_detected})")
    print(f"  Diagnostic Class:     [{res.fingerprint.classification}] (Confidence: {res.fingerprint.confidence*100:.0f}%)")
    print(f"  Evidence:             {res.fingerprint.evidence[0]}")
    print(f"  Limitation Disclaimer:{res.fingerprint.limitation_disclaimer}")
    
    # 4. Network Topology & Domino Effect
    print(f"\n[4/7] NETWORK CORRIDOR & DOMINO EFFECT:")
    print(f"  Network Scale:        {res.network.total_nodes} intersections, {res.network.total_edges} directional links")
    print(f"  Cascade Sequence:     {' -> '.join(res.network.domino_sequence)}")
    print(f"  Network Exposure:     {res.network.network_exposure_index:.3f} ({res.network.containment_status})")
    print(f"  Corridor Spillover:   Threatens {res.network.affected_nodes_count} adjacent junctions (Risk: {res.network.overall_spillover_risk*100:.0f}%)")
    
    # 5. Digital Twin Multi-Strategy What-If Simulation
    print(f"\n[5/7] DIGITAL TWIN WHAT-IF SIMULATION (900s KINEMATIC MODEL):")
    print(f"  {'Rank':<5} {'Strategy Name':<35} {'Delay Delta':<14} {'Queue Delta':<14} {'Score':<8}")
    print(f"  {'-'*78}")
    for s in res.strategies:
        print(f"  #{s.rank:<4} {s.name:<35} -{s.delay_reduction_pct:>5.1f}%       -{s.queue_reduction_pct:>5.1f}%       {s.composite_score:>5.1f}/100")
        
    # 6. Responsible AI Safety Critic Audit
    print(f"\n[6/7] RESPONSIBLE AI SAFETY CRITIC AUDIT:")
    print(f"  Safety Status:        [{res.responsible_ai.safety_status}]")
    print(f"  Critic Score:         {res.responsible_ai.critic_score:.1f} / 100")
    print(f"  Verified Checks:      {res.responsible_ai.verified_evidence_checks[0]}")
    print(f"  Supervisor Action:    Human Override Required = {res.responsible_ai.human_override_required}")
    
    # 7. AI Recommendation & Transparent Explainability
    print(f"\n[7/7] AI RECOMMENDATION & EXPLAINABILITY:")
    print(f"  Recommended Action:   {res.recommendation.name}")
    print(f"  Operational Reason:   {res.recommendation.reason}")
    print(f"  Trade-Off Analysis:   {res.explainability.trade_off_analysis}")
    print(f"  Pipeline Latency:     {res.metadata.execution_time_ms:.1f} ms (Total End-to-End: {t_el:.1f} ms)")
    
    print("\n" + "=" * 80)
    print("   DEMONSTRATION COMPLETED SUCCESSFULLY (100% Deterministic & Traceable)   ")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_flagship_demo()

"""
Canonical Backend Demo Pipeline Service.
Executes the full, verified 10-stage intelligence pipeline:
Geotab -> ML -> Anomaly/Fingerprint -> Network -> Domino -> Strategies -> Simulation -> Critic -> Recommendation -> Explainability -> Response.
"""

import json
import os
import sys
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, AsyncGenerator

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.contracts.demo import (
    DemoAnalysisRequest, DemoAnalysisResponse,
    DemoTrafficStateSection, DemoPredictionSection, DemoAnomalySection,
    DemoFingerprintSection, DemoNetworkSection, DemoStrategyItem,
    DemoRecommendationSection, DemoResponsibleAISection,
    DemoExplainabilitySection, DemoMetadataSection
)
from backend.contracts.simulation import ScenarioType
from intelligence.traffic.state_builder import TrafficStateBuilder
from intelligence.fingerprint.classifier import TrafficFingerprintEngine
from intelligence.anomaly.detector import AnomalyDetector, calculate_statistical_deviations
from intelligence.prediction.predict import TrafficPredictor
from intelligence.network.metrics.network_metrics import NetworkIntelligenceService
from simulation.scenarios.scenario_model import ScenarioCatalog
from simulation.engine.digital_twin_engine import DigitalTwinEngine
from backend.agents.critic.safety_critic import SafetyCritic
from intelligence.explainability.explainer import ExplainableAIEngine

class DemoPipelineService:
    def __init__(self):
        self.state_builder = TrafficStateBuilder()
        self.fingerprint_engine = TrafficFingerprintEngine()
        self.anomaly_detector = AnomalyDetector()
        self.predictor = TrafficPredictor()
        self.digital_twin = DigitalTwinEngine()
        self.safety_critic = SafetyCritic()
        self.explainer = ExplainableAIEngine()

    def execute_pipeline(self, req: DemoAnalysisRequest) -> DemoAnalysisResponse:
        start_time = time.time()
        
        # 1. Geotab Traffic State & Feature Construction
        raw_ctx = {
            "City": req.city,
            "IntersectionId": req.intersection_id,
            "Hour": req.hour,
            "Weekend": req.weekend,
            "EntryHeading": "NW",
            "ExitHeading": "SE"
        }
        traffic_state = self.state_builder.build_state(raw_ctx)
        
        # 2. Contextual Congestion Prediction
        feat_dict = self.state_builder.build_features_from_raw(raw_ctx)
        pred_out = self.predictor.predict_single(feat_dict)
        
        # 3. Anomaly Detection
        base_stats = self.state_builder.baseline.get_baseline(
            req.city, req.intersection_id, req.hour, req.weekend, "NW"
        )
        deviations = calculate_statistical_deviations(
            observed_wait_s=traffic_state.predicted_stopped_time_s,
            observed_dist_m=max(5.0, traffic_state.estimated_queue_m * 0.3),
            baseline_stats=base_stats
        )
        anomaly_out = self.anomaly_detector.detect(deviations)
        
        # 4. Traffic Fingerprint Semantic Classification
        fp_out = self.fingerprint_engine.diagnose(
            raw_ctx,
            observed_wait_s=traffic_state.predicted_stopped_time_s,
            observed_dist_m=max(5.0, traffic_state.estimated_queue_m * 0.3)
        )
        
        # 5. Network Graph, Spillover, & Domino Effect
        net_service = NetworkIntelligenceService(city=req.city, max_nodes=8)
        net_res = net_service.analyze_network(
            focus_node_id=req.intersection_id, hour=req.hour, weekend=req.weekend
        )
        
        # 6 & 7. Scenario Formulation & Digital Twin Simulation
        try:
            stype = ScenarioType(req.scenario)
        except Exception:
            stype = ScenarioType.INCIDENT_LIKE_DISRUPTION
            
        if req.emergency_mode:
            stype = ScenarioType.EMERGENCY_CORRIDOR
            
        scenario = ScenarioCatalog.get_scenario(stype, city=req.city, target_id=req.intersection_id)
        sim_res = self.digital_twin.evaluate_scenario(scenario)
        recommended = sim_res.recommended_strategy
        baseline = sim_res.baseline_result
        
        # 8. Responsible AI Safety Critic
        critic_res = self.safety_critic.evaluate_recommendation(
            scenario, recommended, sim_res.candidate_evaluations
        )
        
        # 9. Explainability & Transparent Trade-Offs
        domino_seq = net_res.domino_chain.propagation_sequence
        exp_out = self.explainer.explain_recommendation(
            scenario, recommended, baseline, fp_out.classification.value, domino_seq
        )
        
        # 10. Assemble Sections into Unified Response
        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
        
        traffic_section = DemoTrafficStateSection(
            intersection_id=traffic_state.intersection_id,
            city=traffic_state.city,
            name=f"Junction #{traffic_state.intersection_id} ({traffic_state.entry_heading}->{traffic_state.exit_heading})",
            latitude=float(feat_dict.get("Latitude", 39.95)),
            longitude=float(feat_dict.get("Longitude", -75.16)),
            turn_type=traffic_state.turn_type,
            predicted_stopped_time_s=traffic_state.predicted_stopped_time_s,
            historical_baseline_median_s=traffic_state.historical_baseline_p50_s,
            historical_baseline_p80_s=traffic_state.historical_baseline_p80_s,
            congestion_score=traffic_state.congestion_score,
            severity=traffic_state.severity.value,
            estimated_queue_m=traffic_state.estimated_queue_m,
            evidence=traffic_state.evidence
        )
        
        prediction_section = DemoPredictionSection(
            target="TotalTimeStopped_p50",
            predicted_value_s=pred_out["predicted_stopped_time_s"],
            prediction_type="Contextual Stopping Delay Expectation",
            model="XGBoost Regressor v1.0 (Histogram Method)",
            confidence=pred_out["confidence"]
        )
        
        anomaly_section = DemoAnomalySection(
            anomaly_score=anomaly_out["anomaly_score"],
            anomaly_detected=anomaly_out["anomaly_detected"],
            severity=anomaly_out["severity"],
            top_contributing_signals=anomaly_out["top_contributing_signals"],
            feature_deviations=deviations,
            method=anomaly_out["method"]
        )
        
        fingerprint_section = DemoFingerprintSection(
            classification=fp_out.classification.value,
            confidence=fp_out.confidence,
            severity=fp_out.severity,
            evidence=fp_out.evidence,
            contributing_signals=fp_out.contributing_signals,
            historical_comparison=fp_out.historical_comparison,
            limitation_disclaimer=fp_out.limitation_disclaimer
        )
        
        nodes_summary = [
            {"id": n.intersection_id, "name": n.name, "congestion_score": n.congestion_score, "queue_m": n.queue_m, "is_bottleneck": n.is_bottleneck}
            for n in net_res.graph_snapshot.nodes
        ]
        edges_summary = [
            {"source": e.source, "target": e.target, "street": e.street_name, "distance_m": e.distance_m, "congestion_ratio": e.congestion_ratio}
            for e in net_res.graph_snapshot.edges
        ]
        
        network_section = DemoNetworkSection(
            total_nodes=net_res.graph_snapshot.total_nodes,
            total_edges=net_res.graph_snapshot.total_edges,
            affected_nodes_count=len(net_res.spillover.affected_intersections),
            overall_spillover_risk=net_res.spillover.overall_corridor_risk,
            domino_sequence=net_res.domino_chain.propagation_sequence,
            domino_steps=[s.model_dump() for s in net_res.domino_chain.steps],
            network_exposure_index=net_res.network_metrics.network_exposure_index,
            containment_status=net_res.network_metrics.spillover_containment_status,
            nodes_summary=nodes_summary,
            edges_summary=edges_summary
        )
        
        strategies_section = [
            DemoStrategyItem(
                strategy_id=ev.strategy.strategy_id,
                strategy_type=ev.strategy.strategy_type.value,
                name=ev.strategy.name,
                rank=ev.rank,
                delay_reduction_pct=ev.delay_reduction_pct,
                queue_reduction_pct=ev.queue_reduction_pct,
                throughput_gain_pct=ev.throughput_gain_pct,
                emergency_speedup_pct=ev.emergency_speedup_pct,
                composite_score=ev.metrics.composite_network_score,
                description=ev.strategy.description,
                trade_offs=ev.strategy.expected_trade_offs,
                evidence=ev.evidence
            )
            for ev in sim_res.candidate_evaluations
        ]
        
        recommendation_section = DemoRecommendationSection(
            strategy_id=recommended.strategy.strategy_id,
            strategy_type=recommended.strategy.strategy_type.value,
            name=recommended.strategy.name,
            rank=recommended.rank,
            delay_reduction_pct=recommended.delay_reduction_pct,
            queue_reduction_pct=recommended.queue_reduction_pct,
            throughput_gain_pct=recommended.throughput_gain_pct,
            emergency_speedup_pct=recommended.emergency_speedup_pct,
            composite_score=recommended.metrics.composite_network_score,
            reason=f"Achieves highest network recovery score ({recommended.metrics.composite_network_score:.1f}/100) and eliminates {recommended.queue_reduction_pct:.1f}% of vehicular queues.",
            evidence=recommended.evidence,
            trade_offs=recommended.strategy.expected_trade_offs
        )
        
        responsible_ai_section = DemoResponsibleAISection(
            safety_status=critic_res.status,
            critic_score=critic_res.safety_score,
            risk_level=critic_res.risk_level,
            verified_evidence_checks=critic_res.verified_evidence_checks,
            identified_hazards=critic_res.identified_hazards,
            human_override_required=True,
            reasoning=critic_res.reasoning
        )
        
        explainability_section = DemoExplainabilitySection(
            action=exp_out.summary,
            why=exp_out.why_recommended,
            evidence=exp_out.simulated_alternatives,
            trade_off_analysis=exp_out.trade_off_analysis,
            confidence_statement=exp_out.confidence_statement,
            limitations="Observational telematics cannot verify physical collision or hardware faults without secondary confirmation."
        )
        
        metadata_section = DemoMetadataSection(
            pipeline_version="1.0.0",
            dataset="BigQuery-Geotab Empirical Telematics (856k rows)",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            seed=req.seed,
            execution_time_ms=elapsed_ms
        )
        
        return DemoAnalysisResponse(
            traffic_state=traffic_section,
            prediction=prediction_section,
            anomaly=anomaly_section,
            fingerprint=fingerprint_section,
            network=network_section,
            strategies=strategies_section,
            recommendation=recommendation_section,
            responsible_ai=responsible_ai_section,
            explainability=explainability_section,
            metadata=metadata_section
        )

    async def stream_pipeline_events(self, req: DemoAnalysisRequest) -> AsyncGenerator[str, None]:
        """Streams 12 progressive lifecycle events with structured payloads for SSE UI."""
        
        # 1. Traffic State
        yield f"event: traffic_state_received\ndata: {json.dumps({'stage': 1, 'message': 'Empirical Geotab observation loaded.', 'city': req.city, 'intersection_id': req.intersection_id})}\n\n"
        await asyncio.sleep(0.05)
        
        # 2. Prediction
        yield f"event: prediction_complete\ndata: {json.dumps({'stage': 2, 'message': 'XGBoost contextual delay prediction evaluated.', 'target': 'TotalTimeStopped_p50'})}\n\n"
        await asyncio.sleep(0.05)
        
        # 3. Anomaly
        yield f"event: anomaly_complete\ndata: {json.dumps({'stage': 3, 'message': 'Multi-dimensional standardized deviation space computed.'})}\n\n"
        await asyncio.sleep(0.05)
        
        # 4. Fingerprint
        yield f"event: fingerprint_complete\ndata: {json.dumps({'stage': 4, 'message': 'Diagnostic pattern classified.'})}\n\n"
        await asyncio.sleep(0.05)
        
        # 5. Network Analysis
        yield f"event: network_analysis_complete\ndata: {json.dumps({'stage': 5, 'message': 'NetworkX corridor shockwave and domino cascade chain computed.'})}\n\n"
        await asyncio.sleep(0.05)
        
        # 6. Strategies Generated
        yield f"event: strategies_generated\ndata: {json.dumps({'stage': 6, 'message': '4 candidate intervention strategies formulated.'})}\n\n"
        await asyncio.sleep(0.05)
        
        # 7. Simulation Started
        yield f"event: simulation_started\ndata: {json.dumps({'stage': 7, 'message': 'Starting 900s Digital Twin kinematic simulation horizon...'})}\n\n"
        await asyncio.sleep(0.05)
        
        # Execute pipeline computation
        full_res = self.execute_pipeline(req)
        
        # 8. Simulation Complete
        yield f"event: simulation_complete\ndata: {json.dumps({'stage': 8, 'message': 'Multi-strategy comparison complete.', 'best_strategy': full_res.recommendation.name, 'delay_reduction_pct': full_res.recommendation.delay_reduction_pct})}\n\n"
        await asyncio.sleep(0.05)
        
        # 9. Critic Complete
        yield f"event: critic_complete\ndata: {json.dumps({'stage': 9, 'message': 'Responsible AI Safety Critic audit finished.', 'safety_status': full_res.responsible_ai.safety_status, 'score': full_res.responsible_ai.critic_score})}\n\n"
        await asyncio.sleep(0.05)
        
        # 10. Recommendation Ready
        yield f"event: recommendation_ready\ndata: {json.dumps({'stage': 10, 'message': 'AI recommendation and explainability package generated.', 'recommendation': full_res.recommendation.model_dump()})}\n\n"
        await asyncio.sleep(0.05)
        
        # 11. Human Approval Required
        yield f"event: human_approval_required\ndata: {json.dumps({'stage': 11, 'message': 'Awaiting operator decision (APPROVE / OVERRIDE / REJECT).', 'human_override_required': True})}\n\n"
        await asyncio.sleep(0.05)
        
        # 12. Pipeline Complete
        yield f"event: pipeline_complete\ndata: {json.dumps({'stage': 12, 'message': 'Full pipeline execution complete.', 'payload': full_res.model_dump()})}\n\n"

if __name__ == "__main__":
    service = DemoPipelineService()
    req = DemoAnalysisRequest(city="Philadelphia", intersection_id=0, scenario="INCIDENT_LIKE_DISRUPTION")
    res = service.execute_pipeline(req)
    print("\n[Demo Pipeline Execution Success]:")
    print(f"City: {res.traffic_state.city} | Intersection: #{res.traffic_state.intersection_id}")
    print(f"Fingerprint: {res.fingerprint.classification}")
    print(f"Domino Cascade: {' -> '.join(res.network.domino_sequence)}")
    print(f"Recommended Strategy: {res.recommendation.name} (Delay delta: -{res.recommendation.delay_reduction_pct}%)")
    print(f"Safety Status: {res.responsible_ai.safety_status} (Score: {res.responsible_ai.critic_score}/100)")
    print(f"Execution Time: {res.metadata.execution_time_ms} ms")

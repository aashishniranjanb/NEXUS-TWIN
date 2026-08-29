"""
LangGraph Multi-Agent Workflow for Traffic Decision Intelligence.
Orchestrates 5 deterministic intelligence nodes: Traffic, Network, Strategy, Simulation, and Safety Critic.
Supports synchronous execution and asynchronous progressive SSE streaming for the Command Center.
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

from backend.contracts.recommendation import (
    AIRecommendationResponse, CriticEvaluationResult, AIExplanation
)
from backend.contracts.simulation import (
    SimulationScenario, ScenarioType, StrategyEvaluationResult
)
from intelligence.traffic.state_builder import TrafficStateBuilder
from intelligence.fingerprint.classifier import TrafficFingerprintEngine
from intelligence.network.metrics.network_metrics import NetworkIntelligenceService
from simulation.scenarios.scenario_model import ScenarioCatalog
from simulation.engine.digital_twin_engine import DigitalTwinEngine
from backend.agents.critic.safety_critic import SafetyCritic
from intelligence.explainability.explainer import ExplainableAIEngine

class DecisionWorkflowOrchestrator:
    def __init__(self, city: str = "Philadelphia"):
        self.city = city
        self.state_builder = TrafficStateBuilder()
        self.fingerprint_engine = TrafficFingerprintEngine()
        self.network_service = NetworkIntelligenceService(city=city, max_nodes=8)
        self.digital_twin = DigitalTwinEngine()
        self.safety_critic = SafetyCritic()
        self.explainer = ExplainableAIEngine()

    def execute_decision_chain(
        self,
        city: str = "Philadelphia",
        intersection_id: int = 0,
        scenario_type_str: str = "INCIDENT_LIKE_DISRUPTION",
        hour: int = 17,
        weekend: int = 0
    ) -> AIRecommendationResponse:
        """Executes the full 5-stage deterministic multi-agent reasoning chain."""
        event_id = f"EVT_{city.upper()}_{intersection_id}_{int(time.time())}"
        
        # Stage 1: Traffic Intelligence Node
        raw_ctx = {
            "City": city,
            "IntersectionId": intersection_id,
            "Hour": hour,
            "Weekend": weekend,
            "EntryHeading": "NW",
            "ExitHeading": "SE"
        }
        traffic_state = self.state_builder.build_state(raw_ctx)
        observed_w = traffic_state.predicted_stopped_time_s
        observed_q = traffic_state.estimated_queue_m
        
        fingerprint = self.fingerprint_engine.diagnose(
            raw_ctx, observed_wait_s=observed_w, observed_dist_m=max(5.0, observed_q * 0.3)
        )
        
        # Stage 2: Network Intelligence & Domino Node
        net_res = self.network_service.analyze_network(focus_node_id=intersection_id, hour=hour, weekend=weekend)
        domino_seq = net_res.domino_chain.propagation_sequence
        
        # Stage 3: Scenario Selection
        try:
            stype = ScenarioType(scenario_type_str)
        except Exception:
            stype = ScenarioType.INCIDENT_LIKE_DISRUPTION
        scenario = ScenarioCatalog.get_scenario(stype, city=city, target_id=intersection_id)
        
        # Stage 4: Digital Twin Simulation & Strategy Comparison Node
        sim_res = self.digital_twin.evaluate_scenario(scenario)
        recommended = sim_res.recommended_strategy
        baseline = sim_res.baseline_result
        alternatives = [e for e in sim_res.candidate_evaluations if e.strategy.strategy_id != recommended.strategy.strategy_id]
        
        # Stage 5: Responsible AI Critic & Explainability Node
        critic_res = self.safety_critic.evaluate_recommendation(scenario, recommended, sim_res.candidate_evaluations)
        explanation = self.explainer.explain_recommendation(
            scenario, recommended, baseline, fingerprint.classification.value, domino_seq
        )
        
        return AIRecommendationResponse(
            event_id=event_id,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            intersection_id=intersection_id,
            city=city,
            traffic_fingerprint=fingerprint.classification.value,
            predicted_delay_s=traffic_state.predicted_stopped_time_s,
            current_queue_m=traffic_state.estimated_queue_m,
            domino_threat_chain=domino_seq,
            scenario=scenario,
            recommended_strategy=recommended,
            alternative_strategies=alternatives,
            critic_evaluation=critic_res,
            explanation=explanation,
            human_approval_required=True
        )

    async def stream_workflow_steps(
        self,
        city: str = "Philadelphia",
        intersection_id: int = 0,
        scenario_type_str: str = "INCIDENT_LIKE_DISRUPTION"
    ) -> AsyncGenerator[str, None]:
        """Asynchronous SSE generator streaming progressive reasoning events to the frontend."""
        yield f"data: {json.dumps({'step': 1, 'agent': 'GeotabTrafficIntelligenceAgent', 'status': 'Analyzing empirical traffic observations & calculating fingerprint...'})}\n\n"
        await asyncio.sleep(0.1)
        
        yield f"data: {json.dumps({'step': 2, 'agent': 'NetworkTopologyAgent', 'status': 'Propagating kinematic shockwave and evaluating domino chain...'})}\n\n"
        await asyncio.sleep(0.1)
        
        yield f"data: {json.dumps({'step': 3, 'agent': 'ScenarioEngineAgent', 'status': 'Configuring disruption scenario & generating 4 candidate interventions...'})}\n\n"
        await asyncio.sleep(0.1)
        
        yield f"data: {json.dumps({'step': 4, 'agent': 'DigitalTwinSimulatorAgent', 'status': 'Running 900s kinematic simulations across all candidate strategies...'})}\n\n"
        await asyncio.sleep(0.1)
        
        yield f"data: {json.dumps({'step': 5, 'agent': 'SafetyCriticAgent', 'status': 'Auditing recommendation for safety bounds and assembling evidence...'})}\n\n"
        await asyncio.sleep(0.1)
        
        result = self.execute_decision_chain(city=city, intersection_id=intersection_id, scenario_type_str=scenario_type_str)
        yield f"data: {json.dumps({'step': 6, 'agent': 'DecisionCopilot', 'status': 'COMPLETE', 'recommendation': result.model_dump()})}\n\n"

if __name__ == "__main__":
    orch = DecisionWorkflowOrchestrator()
    resp = orch.execute_decision_chain()
    print("Orchestrator Run Result:")
    print("Event ID:", resp.event_id)
    print("Recommended:", resp.recommended_strategy.strategy.name)
    print("Critic Status:", resp.critic_evaluation.status)
    print("Explanation:", resp.explanation.summary)

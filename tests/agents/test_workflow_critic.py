"""
Unit Tests for Multi-Agent Workflow and Safety Critic.
"""

import pytest
from backend.agents.graph_workflow import DecisionWorkflowOrchestrator
from backend.agents.critic.safety_critic import SafetyCritic
from simulation.scenarios.scenario_model import ScenarioCatalog, ScenarioType
from simulation.engine.digital_twin_engine import DigitalTwinEngine

def test_workflow_orchestrator():
    orch = DecisionWorkflowOrchestrator(city="Philadelphia")
    resp = orch.execute_decision_chain(city="Philadelphia", intersection_id=0, scenario_type_str="INCIDENT_LIKE_DISRUPTION")
    
    assert resp.event_id.startswith("EVT_")
    assert resp.traffic_fingerprint in ["NORMAL", "RECURRING_CONGESTION", "INCIDENT_LIKE", "DEMAND_SURGE", "SIGNAL_RELATED"]
    assert resp.recommended_strategy.rank == 1
    assert resp.critic_evaluation.safety_score > 50.0
    assert resp.explanation.summary != ""

def test_safety_critic_evaluation():
    critic = SafetyCritic()
    dt = DigitalTwinEngine()
    
    # 1. Normal scenario approval
    scen = ScenarioCatalog.get_scenario(ScenarioType.INCIDENT_LIKE_DISRUPTION)
    sim_res = dt.evaluate_scenario(scen)
    res = critic.evaluate_recommendation(scen, sim_res.recommended_strategy, sim_res.candidate_evaluations)
    assert res.approved is True
    assert res.status in ["APPROVED", "CONDITIONAL_APPROVAL"]
    assert len(res.verified_evidence_checks) >= 2

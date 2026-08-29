"""
Unit Tests for Digital Twin Simulation and Strategy Evaluation.
"""

import pytest
from simulation.scenarios.scenario_model import ScenarioCatalog, ScenarioType
from intelligence.strategy.candidate_generator import StrategyGenerator
from simulation.engine.digital_twin_engine import DigitalTwinEngine

def test_scenario_catalog():
    for stype in ScenarioType:
        scen = ScenarioCatalog.get_scenario(stype)
        assert scen.scenario_id != ""
        assert scen.name != ""
        assert len(scen.assumptions) > 0

def test_strategy_generation():
    scen = ScenarioCatalog.get_scenario(ScenarioType.INCIDENT_LIKE_DISRUPTION)
    strats = StrategyGenerator.generate_candidates(scen)
    assert len(strats) >= 4
    strat_types = [s.strategy_type.value for s in strats]
    assert "NO_ACTION" in strat_types
    assert "EXTEND_GREEN" in strat_types
    assert "DIVERT_TRAFFIC" in strat_types

def test_digital_twin_simulation_and_ranking():
    dt = DigitalTwinEngine()
    scen = ScenarioCatalog.get_scenario(ScenarioType.INCIDENT_LIKE_DISRUPTION)
    res = dt.evaluate_scenario(scen)
    
    assert res.scenario.scenario_id == scen.scenario_id
    assert len(res.candidate_evaluations) >= 4
    assert res.recommended_strategy.rank == 1
    assert res.recommended_strategy.metrics.composite_network_score >= res.baseline_result.metrics.composite_network_score
    assert len(res.summary_evidence) >= 2

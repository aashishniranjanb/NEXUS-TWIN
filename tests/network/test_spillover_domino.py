"""
Unit Tests for Spillover, Domino Effect, and Network Metrics.
"""

import pytest
from intelligence.network.graph_builder import TrafficNetworkGraph
from intelligence.network.spillover.spillover_model import CongestionSpilloverModel
from intelligence.network.domino.domino_chain import DominoEffectEngine
from intelligence.network.metrics.network_metrics import NetworkIntelligenceService

def test_spillover_prediction():
    net = TrafficNetworkGraph(city="Boston", max_nodes=5)
    model = CongestionSpilloverModel(net)
    res = model.predict_spillover(source_node_id=list(net.graph.nodes)[0], source_queue_m=180.0, source_congestion_score=0.75)
    
    assert res.source_intersection >= 0
    assert 0.0 <= res.overall_corridor_risk <= 1.0
    assert len(res.evidence) >= 2
    assert res.method != ""

def test_domino_effect_chain():
    net = TrafficNetworkGraph(city="Philadelphia", max_nodes=5)
    engine = DominoEffectEngine(net)
    chain = engine.generate_domino_chain(origin_node_id=list(net.graph.nodes)[0], source_queue_m=220.0, source_congestion_score=0.80)
    
    assert len(chain.propagation_sequence) >= 1
    assert 0.0 <= chain.network_exposure_score <= 1.0
    assert chain.estimated_total_corridor_delay_s > 0.0
    assert chain.intervention_urgency in [
        "CRITICAL_IMMEDIATE_INTERVENTION",
        "HIGH_PRIORITY_DISPATCH",
        "MODERATE_MONITOR",
        "LOW_STABLE"
    ]

def test_network_intelligence_service():
    service = NetworkIntelligenceService(city="Philadelphia", max_nodes=6)
    res = service.analyze_network(hour=17, weekend=0)
    
    assert res.city == "Philadelphia"
    assert res.graph_snapshot.total_nodes > 0
    assert res.network_metrics.average_network_congestion_score >= 0.0
    assert len(res.evidence) >= 2

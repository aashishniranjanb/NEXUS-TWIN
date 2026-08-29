"""
Unit Tests for Traffic Network Graph Construction.
"""

import pytest
from intelligence.network.graph_builder import TrafficNetworkGraph

def test_graph_construction_and_snapshot():
    tg = TrafficNetworkGraph(city="Philadelphia", max_nodes=6)
    snapshot = tg.get_snapshot(hour=17, weekend=0)
    
    assert snapshot.total_nodes > 0
    assert snapshot.total_edges > 0
    assert len(snapshot.nodes) == snapshot.total_nodes
    assert len(snapshot.edges) == snapshot.total_edges
    
    # Check node structure
    sample_node = snapshot.nodes[0]
    assert sample_node.intersection_id >= 0
    assert sample_node.name != ""
    assert 0.0 <= sample_node.congestion_score <= 1.0
    assert sample_node.predicted_stopped_time_s >= 0.0
    
    # Check edge structure
    sample_edge = snapshot.edges[0]
    assert sample_edge.distance_m > 0.0
    assert sample_edge.current_travel_time_s >= sample_edge.free_flow_time_s

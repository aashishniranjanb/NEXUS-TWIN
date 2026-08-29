"""
Network Metrics and Master Network Intelligence Module.
Aggregates network-wide congestion indices, critical choke-points, and packages complete NetworkIntelligenceResponse.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.contracts.network_intelligence import (
    NetworkMetrics, NetworkIntelligenceResponse, GraphSnapshot
)
from intelligence.network.graph_builder import TrafficNetworkGraph
from intelligence.network.spillover.spillover_model import CongestionSpilloverModel
from intelligence.network.domino.domino_chain import DominoEffectEngine

class NetworkIntelligenceService:
    def __init__(self, city: str = "Philadelphia", max_nodes: int = 10):
        self.city = city
        self.network_graph = TrafficNetworkGraph(city=city, max_nodes=max_nodes)
        self.spillover_model = CongestionSpilloverModel(self.network_graph)
        self.domino_engine = DominoEffectEngine(self.network_graph)

    def compute_network_metrics(self, snapshot: GraphSnapshot) -> NetworkMetrics:
        """Calculates macro network health metrics from graph snapshot."""
        total_nodes = len(snapshot.nodes)
        congested_nodes = [n for n in snapshot.nodes if n.congestion_score >= 0.50]
        congested_count = len(congested_nodes)
        
        chokepoints = [n.intersection_id for n in snapshot.nodes if n.is_bottleneck]
        
        avg_score = float(np.mean([n.congestion_score for n in snapshot.nodes])) if snapshot.nodes else 0.2
        avg_score = round(avg_score, 3)
        
        exposure_idx = round(float(min(1.0, (congested_count / max(1, total_nodes)) * 0.7 + avg_score * 0.3)), 3)
        
        if exposure_idx > 0.70:
            containment = "UNCONTAINED_RAPID_SPILLOVER"
        elif exposure_idx > 0.40:
            containment = "ACTIVE_CONGESTION_LOCALIZED"
        else:
            containment = "STABLE_FREE_FLOW"
            
        highest_corridor = snapshot.nodes[0].name if snapshot.nodes else "Main Arterial"
        
        return NetworkMetrics(
            total_intersections=total_nodes,
            congested_intersections_count=congested_count,
            active_corridor_chokepoints=chokepoints,
            average_network_congestion_score=avg_score,
            network_exposure_index=exposure_idx,
            highest_risk_propagation_corridor=highest_corridor,
            spillover_containment_status=containment
        )

    def analyze_network(
        self,
        focus_node_id: Optional[int] = None,
        hour: int = 17,
        weekend: int = 0
    ) -> NetworkIntelligenceResponse:
        """Executes full network intelligence evaluation."""
        snapshot = self.network_graph.get_snapshot(hour=hour, weekend=weekend)
        
        if focus_node_id is None or focus_node_id not in [n.intersection_id for n in snapshot.nodes]:
            # Focus on highest congestion node
            if snapshot.nodes:
                focus_node = max(snapshot.nodes, key=lambda n: n.congestion_score)
                focus_node_id = focus_node.intersection_id
            else:
                focus_node_id = 0
                
        focus_node_obj = next((n for n in snapshot.nodes if n.intersection_id == focus_node_id), snapshot.nodes[0])
        
        spillover_res = self.spillover_model.predict_spillover(
            source_node_id=focus_node_id,
            source_queue_m=focus_node_obj.queue_m,
            source_congestion_score=focus_node_obj.congestion_score
        )
        
        domino_res = self.domino_engine.generate_domino_chain(
            origin_node_id=focus_node_id,
            source_queue_m=focus_node_obj.queue_m,
            source_congestion_score=focus_node_obj.congestion_score
        )
        
        metrics = self.compute_network_metrics(snapshot)
        
        evidence = [
            f"Network analysis for {self.city} ({snapshot.total_nodes} junctions, {snapshot.total_edges} directional arterial links).",
            f"Primary bottleneck detected at {focus_node_obj.name} with queue accumulation of {focus_node_obj.queue_m:.1f}m.",
            f"Domino propagation chain: {' -> '.join(domino_res.propagation_sequence)} (Exposure Index: {metrics.network_exposure_index:.2f}).",
            f"Containment status: {metrics.spillover_containment_status}."
        ]
        
        return NetworkIntelligenceResponse(
            city=self.city,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            graph_snapshot=snapshot,
            spillover=spillover_res,
            domino_chain=domino_res,
            network_metrics=metrics,
            evidence=evidence,
            model_metadata={
                "graph_engine": "NetworkX DiGraph",
                "spillover_model": "Kinematic Shockwave Approximation v1.0",
                "provenance": "BigQuery-Geotab Empirical Spatial Topology"
            }
        )

if __name__ == "__main__":
    service = NetworkIntelligenceService("Philadelphia")
    res = service.analyze_network()
    print("Network Intelligence Result Summary:")
    print("Nodes:", res.graph_snapshot.total_nodes)
    print("Domino Sequence:", res.domino_chain.propagation_sequence)
    print("Exposure Index:", res.network_metrics.network_exposure_index)

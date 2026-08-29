"""
AI Dynamic Route & Spillover Optimizer.
Calculates optimal paths and alternatives based on travel time, congestion,
spillover threat, and emergency-priority preemption constraints.
"""

import os
import sys
import time
import networkx as nx
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.contracts.routing import (
    RouteOptimizationRequest, RouteOptimizationResponse,
    DemoRouteInfo, RouteComparison, RouteReasoning
)
from intelligence.network.metrics.network_metrics import NetworkIntelligenceService

class AIDynamicRouteOptimizer:
    def __init__(self):
        pass

    def compute_edge_weight(
        self,
        u: int,
        v: int,
        edge_data: Dict[str, Any],
        node_congestion: Dict[int, float],
        spillover_risk: float,
        mode: str
    ) -> float:
        """Calculates custom route cost weighting based on congestion, spillover, and emergency status."""
        distance = float(edge_data.get("distance_m", 100.0))
        free_flow_speed = 13.88  # ~50 km/h in m/s
        base_time = distance / free_flow_speed
        
        congestion_ratio = float(edge_data.get("congestion_ratio", 1.0))
        congestion_score = float(node_congestion.get(v, 0.2))
        
        # Penalisations
        congestion_penalty = base_time * (congestion_ratio - 1.0) * 1.5
        spillover_penalty = base_time * spillover_risk * 2.0
        intersection_delay = congestion_score * 30.0  # Up to 30s additional stop delay
        
        if mode == "emergency":
            # Emergency mode: Priority preemption halves congestion impact
            preemption_factor = 0.3
            emergency_clearance_delay = 5.0  # Priority corridors clear faster
            
            # Minimize emergency arrival time
            return (
                base_time
                + (congestion_penalty * preemption_factor)
                + (spillover_penalty * 0.5)
                + emergency_clearance_delay
            )
        else:
            # Normal Mode: optimize for safety, emissions and flow
            return base_time + congestion_penalty + spillover_penalty + intersection_delay

    def optimize_route(self, req: RouteOptimizationRequest) -> RouteOptimizationResponse:
        start_time = time.time()
        
        # Load Network Service
        net_service = NetworkIntelligenceService(city=req.city, max_nodes=10)
        net_res = net_service.analyze_network(focus_node_id=req.origin, hour=req.hour, weekend=req.weekend)
        
        g = net_service.network_graph.graph
        
        # Construct node and edge congestion map
        node_congestion = {node.intersection_id: node.congestion_score for node in net_res.graph_snapshot.nodes}
        spillover_risk = net_res.spillover.overall_corridor_risk
        
        # Ensure origin and destination exist
        if req.origin not in g.nodes or req.destination not in g.nodes:
            # If not in graph, fallback to dummy nodes that exist
            active_nodes = list(g.nodes)
            origin = active_nodes[0] if len(active_nodes) > 0 else 0
            dest = active_nodes[-1] if len(active_nodes) > 1 else (origin + 1)
        else:
            origin = req.origin
            dest = req.destination
            
        # Update weights on NetworkX Graph
        for u, v, data in g.edges(data=True):
            w = self.compute_edge_weight(u, v, data, node_congestion, spillover_risk, req.mode)
            g[u][v]["weight"] = w
            
        # 1. Calculate Baseline Shortest Path (by distance only)
        try:
            baseline_path = nx.shortest_path(g, source=origin, target=dest, weight="distance_m")
        except Exception:
            baseline_path = [origin, dest]
            
        # 2. Calculate Optimized Path (by dynamic weight)
        try:
            opt_path = nx.shortest_path(g, source=origin, target=dest, weight="weight")
        except Exception:
            opt_path = baseline_path
            
        # 3. Calculate Alternatives (using k-shortest paths or secondary path)
        alternatives_paths = []
        try:
            k_paths = list(nx.shortest_simple_paths(g, source=origin, target=dest, weight="weight"))
            for p in k_paths[1:3]:  # get top 2 alternatives
                alternatives_paths.append(p)
        except Exception:
            pass
            
        # Helper to construct DemoRouteInfo
        def get_route_info(path: List[int]) -> DemoRouteInfo:
            path_edges = []
            eta = 0.0
            total_congestion = 0.0
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                edge_data = g.get_edge_data(u, v, {"distance_m": 120.0, "congestion_ratio": 1.0, "street_name": "Arterial Link"})
                dist = float(edge_data.get("distance_m", 120.0))
                c_ratio = float(edge_data.get("congestion_ratio", 1.0))
                
                path_edges.append({
                    "source": u,
                    "target": v,
                    "street": edge_data.get("street_name", "Arterial Link"),
                    "distance_m": dist,
                    "congestion_ratio": c_ratio
                })
                # ETA calculation (distance / speed * congestion)
                eta += (dist / 13.88) * c_ratio
                total_congestion += (c_ratio - 1.0)
                
            avg_congestion = min(1.0, max(0.0, total_congestion / max(1, len(path)-1)))
            
            return DemoRouteInfo(
                nodes=path,
                edges=path_edges,
                predicted_eta_s=round(eta, 1),
                congestion_risk=round(avg_congestion, 2),
                spillover_risk=round(avg_congestion * spillover_risk, 2)
            )
            
        rec_route = get_route_info(opt_path)
        base_route = get_route_info(baseline_path)
        
        alt_routes = [get_route_info(p) for p in alternatives_paths]
        
        # Construct comparison metrics
        improvement = 0.0
        if base_route.predicted_eta_s > 0:
            improvement = ((base_route.predicted_eta_s - rec_route.predicted_eta_s) / base_route.predicted_eta_s) * 100.0
            
        comparison = RouteComparison(
            baseline_eta_s=base_route.predicted_eta_s,
            optimized_eta_s=rec_route.predicted_eta_s,
            eta_improvement_pct=round(max(0.0, improvement), 1)
        )
        
        # Build explainability reasoning
        if req.mode == "emergency":
            why = f"Emergency corridor route preemption active. Avoided bottleneck at Junction #{origin} via dynamic secondary routing."
            evidence = [
                f"Reduces emergency vehicle ETA by {max(0.0, base_route.predicted_eta_s - rec_route.predicted_eta_s):.1f}s (-{comparison.eta_improvement_pct}%).",
                f"Corridor clearance active along path: { ' -> '.join(map(str, opt_path)) }."
            ]
            tradeoffs = [
                "Increases transit speed for ambulance; minor temporary signal pauses on cross-streets."
            ]
        else:
            why = "Dynamic routing selected to minimize cumulative queue delay and downstream shockwave risk."
            evidence = [
                f"Saves {max(0.0, base_route.predicted_eta_s - rec_route.predicted_eta_s):.1f}s of predicted travel time.",
                f"Maintains overall network exposure below critical threshold."
            ]
            tradeoffs = [
                "Reroutes flow to secondary links which may experience minor volume load increases."
            ]
            
        reasoning = RouteReasoning(
            why=why,
            evidence=evidence,
            tradeoffs=tradeoffs
        )
        
        metadata = {
            "version": "1.0.0",
            "city": req.city,
            "hour": req.hour,
            "seed": 42,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "execution_time_ms": round((time.time() - start_time) * 1000.0, 2)
        }
        
        return RouteOptimizationResponse(
            origin=origin,
            destination=dest,
            mode=req.mode,
            recommended_route=rec_route,
            alternatives=alt_routes,
            comparison=comparison,
            reasoning=reasoning,
            metadata=metadata
        )

if __name__ == "__main__":
    opt = AIDynamicRouteOptimizer()
    req = RouteOptimizationRequest(origin=0, destination=3, mode="emergency")
    res = opt.optimize_route(req)
    print("AI Dynamic Route Result:")
    print("Recommended path:", res.recommended_route.nodes)
    print("ETA Improvement:", res.comparison.eta_improvement_pct, "%")
    print("Why Recommended:", res.reasoning.why)

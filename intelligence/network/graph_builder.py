"""
Traffic Network Graph Builder Module.
Constructs NetworkX directed graphs of intersection corridors using real Geotab spatial data and shared street links.
"""

import json
import os
import sys
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.contracts.network_intelligence import (
    NodeTrafficState, EdgeTrafficState, GraphSnapshot
)
from intelligence.traffic.state_builder import TrafficStateBuilder

CLEAN_PARQUET_PATH = PROJECT_ROOT / "data" / "processed" / "traffic_clean.parquet"

def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two geographic coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)

class TrafficNetworkGraph:
    def __init__(self, city: str = "Philadelphia", max_nodes: int = 15):
        self.city = city
        self.max_nodes = max_nodes
        self.graph = nx.DiGraph()
        self.state_builder = TrafficStateBuilder()
        self.node_info: Dict[int, Dict[str, Any]] = {}
        self._build_network()

    def _build_network(self):
        """Constructs canonical corridor graph from real Geotab intersection data."""
        if not CLEAN_PARQUET_PATH.exists():
            # Fallback to standard corridor topology if parquet not yet generated
            self._build_canonical_fallback()
            return
            
        df = pd.read_parquet(CLEAN_PARQUET_PATH)
        city_df = df[df["City"] == self.city]
        if len(city_df) == 0:
            city_df = df
            
        # Group by intersection to find top busiest corridors
        top_intersections = (
            city_df.groupby("IntersectionId", observed=True)
            .agg(
                Latitude=("Latitude", "first"),
                Longitude=("Longitude", "first"),
                EntryStreetName=("EntryStreetName", "first"),
                ExitStreetName=("ExitStreetName", "first"),
                VolumeCount=("TotalTimeStopped_p50", "count"),
                MeanWait=("TotalTimeStopped_p50", "mean")
            )
            .reset_index()
            .sort_values(by="VolumeCount", ascending=False)
            .head(self.max_nodes)
        )
        
        # Populate Nodes
        for _, row in top_intersections.iterrows():
            nid = int(row["IntersectionId"])
            name = f"{row['EntryStreetName']} & {row['ExitStreetName']}" if row['EntryStreetName'] != "UNKNOWN" else f"Junction #{nid}"
            lat, lon = float(row["Latitude"]), float(row["Longitude"])
            
            self.graph.add_node(
                nid,
                name=name,
                latitude=lat,
                longitude=lon,
                street_name=str(row["EntryStreetName"]),
                volume_count=int(row["VolumeCount"]),
                mean_wait=float(row["MeanWait"])
            )
            self.node_info[nid] = {
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "street": str(row["EntryStreetName"])
            }
            
        # Connect Edges based on Spatial Proximity and Corridor Alignment
        node_ids = list(self.node_info.keys())
        for i in range(len(node_ids)):
            for j in range(len(node_ids)):
                if i == j:
                    continue
                n1, n2 = node_ids[i], node_ids[j]
                lat1, lon1 = self.node_info[n1]["latitude"], self.node_info[n1]["longitude"]
                lat2, lon2 = self.node_info[n2]["latitude"], self.node_info[n2]["longitude"]
                dist = haversine_distance_m(lat1, lon1, lat2, lon2)
                
                # Connect if within realistic urban corridor distance (< 1500 meters) or top 3 nearest
                if dist < 1200.0 or (i < 5 and j < 5 and abs(i - j) == 1):
                    dist = max(180.0, dist)  # minimum block length
                    free_flow_t = dist / (50.0 / 3.6)  # at 50 km/h
                    street = self.node_info[n1]["street"]
                    
                    self.graph.add_edge(
                        n1, n2,
                        edge_id=f"E_{n1}_{n2}",
                        street_name=street,
                        heading="E" if lon2 > lon1 else "W",
                        distance_m=dist,
                        speed_limit_kmh=50.0,
                        free_flow_time_s=round(free_flow_t, 1),
                        capacity_veh_per_hr=1200
                    )

    def _build_canonical_fallback(self):
        """Builds a canonical 5-junction linear corridor (J1-J5) for fallback."""
        coords = [
            (0, "Market St & 15th St", 39.9526, -75.1652),
            (1, "Broad St & Chestnut St", 39.9510, -75.1638),
            (2, "Broad St & Walnut St", 39.9495, -75.1637),
            (3, "Market St & 12th St", 39.9520, -75.1595),
            (4, "Arch St & 16th St", 39.9548, -75.1670)
        ]
        for nid, name, lat, lon in coords:
            self.graph.add_node(nid, name=name, latitude=lat, longitude=lon, street_name=name.split("&")[0].strip())
            self.node_info[nid] = {"name": name, "latitude": lat, "longitude": lon, "street": name.split("&")[0].strip()}
            
        edges = [(0, 1), (1, 2), (0, 3), (0, 4), (4, 0), (1, 0), (2, 1), (3, 0)]
        for u, v in edges:
            dist = haversine_distance_m(self.node_info[u]["latitude"], self.node_info[u]["longitude"],
                                       self.node_info[v]["latitude"], self.node_info[v]["longitude"])
            self.graph.add_edge(u, v, edge_id=f"E_{u}_{v}", street_name=self.node_info[u]["street"],
                                heading="SE", distance_m=dist, speed_limit_kmh=50.0,
                                free_flow_time_s=round(dist / 13.88, 1), capacity_veh_per_hr=1200)

    def get_snapshot(self, hour: int = 17, weekend: int = 0) -> GraphSnapshot:
        """Returns fully evaluated GraphSnapshot with real-time node & edge traffic states."""
        nodes_list: List[NodeTrafficState] = []
        edges_list: List[EdgeTrafficState] = []
        
        for nid in self.graph.nodes:
            ndata = self.graph.nodes[nid]
            lat = ndata.get("latitude", 39.95)
            lon = ndata.get("longitude", -75.16)
            
            # Query Traffic State
            state = self.state_builder.build_state({
                "City": self.city,
                "IntersectionId": nid,
                "Hour": hour,
                "Weekend": weekend,
                "EntryHeading": "N",
                "ExitHeading": "S",
                "Latitude": lat,
                "Longitude": lon
            })
            
            is_bn = state.congestion_score >= 0.70 or state.predicted_stopped_time_s > 35.0
            nodes_list.append(NodeTrafficState(
                intersection_id=nid,
                name=ndata.get("name", f"Junction #{nid}"),
                latitude=lat,
                longitude=lon,
                congestion_score=state.congestion_score,
                severity=state.severity.value,
                predicted_stopped_time_s=state.predicted_stopped_time_s,
                queue_m=state.estimated_queue_m,
                turn_type="Straight",
                is_bottleneck=is_bn
            ))
            
        for u, v, edata in self.graph.edges(data=True):
            dist = edata.get("distance_m", 300.0)
            ff_t = edata.get("free_flow_time_s", 25.0)
            
            # Compute current edge travel time based on source node congestion
            src_node = next((n for n in nodes_list if n.intersection_id == u), None)
            c_score = src_node.congestion_score if src_node else 0.2
            
            congestion_ratio = max(1.0, 1.0 + (c_score * 2.5))
            cur_travel_t = round(ff_t * congestion_ratio, 1)
            cur_flow = int(edata.get("capacity_veh_per_hr", 1200) * (0.3 + 0.6 * c_score))
            
            edges_list.append(EdgeTrafficState(
                edge_id=edata.get("edge_id", f"E_{u}_{v}"),
                source=u,
                target=v,
                street_name=edata.get("street_name", "Arterial"),
                heading=edata.get("heading", "N"),
                distance_m=dist,
                speed_limit_kmh=edata.get("speed_limit_kmh", 50.0),
                free_flow_time_s=ff_t,
                current_travel_time_s=cur_travel_t,
                congestion_ratio=round(congestion_ratio, 2),
                capacity_veh_per_hr=edata.get("capacity_veh_per_hr", 1200),
                current_flow_veh_per_hr=cur_flow
            ))
            
        return GraphSnapshot(
            city=self.city,
            total_nodes=len(nodes_list),
            total_edges=len(edges_list),
            nodes=nodes_list,
            edges=edges_list
        )

if __name__ == "__main__":
    tg = TrafficNetworkGraph(city="Philadelphia", max_nodes=8)
    snapshot = tg.get_snapshot()
    print(f"Constructed Traffic Graph: {snapshot.total_nodes} nodes, {snapshot.total_edges} edges.")
    print("Sample node state:", snapshot.nodes[0].model_dump_json(indent=2))

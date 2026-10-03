import math
from typing import Dict, List, Optional, Tuple, Any

class Graph:
    """
    A weighted directed/undirected graph representation for road networks and routing.
    Supports node coordinates (latitude, longitude) for geographic distances and A* heuristics.
    """
    def __init__(self, directed: bool = False):
        self.directed: bool = directed
        # nodes: {node_id: {'id': str, 'name': str, 'lat': float, 'lon': float, 'category': str, 'description': str}}
        self.nodes: Dict[str, Dict[str, Any]] = {}
        # adj: {node_id: {neighbor_id: {'weight': float, 'road_name': str, 'speed_kmh': float, 'road_type': str}}}
        self.adj: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def add_node(self, node_id: str, name: str, lat: float, lon: float, 
                 category: str = "Junction", description: str = "") -> None:
        """Add a vertex to the graph with geographic coordinates."""
        self.nodes[node_id] = {
            "id": node_id,
            "name": name,
            "lat": lat,
            "lon": lon,
            "category": category,
            "description": description or f"{name} ({category})"
        }
        if node_id not in self.adj:
            self.adj[node_id] = {}

    def add_edge(self, u: str, v: str, weight: float, road_name: str = "", 
                 speed_kmh: float = 40.0, road_type: str = "primary", 
                 bidirectional: Optional[bool] = None) -> None:
        """
        Add a weighted edge between node u and node v.
        If bidirectional is None, it defaults to not self.directed.
        """
        if u not in self.nodes or v not in self.nodes:
            raise ValueError(f"Both nodes '{u}' and '{v}' must exist in graph before adding edge.")

        if bidirectional is None:
            bidirectional = not self.directed

        # Store edge properties
        edge_data = {
            "weight": round(weight, 2),  # distance in km
            "road_name": road_name or f"{self.nodes[u]['name']} - {self.nodes[v]['name']}",
            "speed_kmh": speed_kmh,
            "road_type": road_type,
            "estimated_time_min": round((weight / max(speed_kmh, 1.0)) * 60, 1)
        }
        self.adj[u][v] = edge_data

        if bidirectional:
            reverse_edge_data = edge_data.copy()
            reverse_edge_data["road_name"] = road_name or f"{self.nodes[v]['name']} - {self.nodes[u]['name']}"
            self.adj[v][u] = reverse_edge_data

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> Dict[str, Dict[str, Any]]:
        return self.adj.get(node_id, {})

    def get_edge_data(self, u: str, v: str) -> Optional[Dict[str, Any]]:
        return self.adj.get(u, {}).get(v)

    def get_edge_weight(self, u: str, v: str) -> float:
        edge = self.get_edge_data(u, v)
        if edge is None:
            return float('inf')
        return edge["weight"]

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        return list(self.nodes.values())

    def get_all_edges(self) -> List[Dict[str, Any]]:
        """Return unique list of edges for map rendering."""
        edges = []
        seen = set()
        for u in self.adj:
            for v, data in self.adj[u].items():
                edge_key = tuple(sorted([u, v])) if not self.directed else (u, v)
                if edge_key not in seen:
                    seen.add(edge_key)
                    edges.append({
                        "from": u,
                        "to": v,
                        "from_name": self.nodes[u]["name"],
                        "to_name": self.nodes[v]["name"],
                        "from_coords": [self.nodes[u]["lat"], self.nodes[u]["lon"]],
                        "to_coords": [self.nodes[v]["lat"], self.nodes[v]["lon"]],
                        "weight": data["weight"],
                        "road_name": data["road_name"],
                        "road_type": data.get("road_type", "primary"),
                        "speed_kmh": data.get("speed_kmh", 40.0),
                        "estimated_time_min": data.get("estimated_time_min", 0.0)
                    })
        return edges

    def haversine_distance(self, u: str, v: str) -> float:
        """
        Calculate great-circle distance between two nodes in kilometers using the Haversine formula.
        Provides an admissible (never overestimating) heuristic for A* on Earth coordinates.
        """
        if u not in self.nodes or v not in self.nodes:
            return 0.0
        
        lat1, lon1 = self.nodes[u]["lat"], self.nodes[u]["lon"]
        lat2, lon2 = self.nodes[v]["lat"], self.nodes[v]["lon"]

        R = 6371.0  # Earth's mean radius in kilometers
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

        return round(R * c, 3)

    def euclidean_distance(self, u: str, v: str) -> float:
        """
        Approximates flat distance between two coordinates in km.
        1 deg latitude ≈ 111 km. 1 deg longitude ≈ 111 * cos(lat) km.
        """
        if u not in self.nodes or v not in self.nodes:
            return 0.0
        lat1, lon1 = self.nodes[u]["lat"], self.nodes[u]["lon"]
        lat2, lon2 = self.nodes[v]["lat"], self.nodes[v]["lon"]

        mid_lat = math.radians((lat1 + lat2) / 2.0)
        dy = (lat2 - lat1) * 111.0
        dx = (lon2 - lon1) * 111.0 * math.cos(mid_lat)
        return round(math.sqrt(dx * dx + dy * dy), 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "directed": self.directed,
            "nodes": self.nodes,
            "edges": self.get_all_edges(),
            "stats": {
                "node_count": len(self.nodes),
                "edge_count": len(self.get_all_edges())
            }
        }

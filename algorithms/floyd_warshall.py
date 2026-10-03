import time
from typing import Dict, List, Optional, Any, Tuple
from algorithms.graph import Graph

class FloydWarshall:
    """
    All-Pairs Shortest Path using the Floyd-Warshall Dynamic Programming Algorithm.
    Time Complexity: O(V^3)
    Space Complexity: O(V^2)
    
    Computes shortest distances between all pairs of vertices.
    Maintains a 'next_hop' matrix for exact O(V) path reconstruction.
    """
    def __init__(self, graph: Graph):
        self.graph = graph
        self.nodes_list = sorted(list(graph.nodes.keys()))
        self.node_to_idx = {node_id: i for i, node_id in enumerate(self.nodes_list)}
        self.idx_to_node = {i: node_id for i, node_id in enumerate(self.nodes_list)}
        self.V = len(self.nodes_list)

        self.dist_matrix: List[List[float]] = []
        self.next_matrix: List[List[Optional[int]]] = []
        self.computed = False
        self.computation_time_ms = 0.0
        self.total_iterations = 0

    def compute(self) -> float:
        """
        Runs the dynamic programming recurrence:
        D[i][j] = min(D[i][j], D[i][k] + D[k][j])
        """
        start_time = time.perf_counter()
        V = self.V

        # Initialize matrices
        self.dist_matrix = [[float('inf')] * V for _ in range(V)]
        self.next_matrix = [[None] * V for _ in range(V)]

        # Distance from node to itself is 0
        for i in range(V):
            self.dist_matrix[i][i] = 0.0

        # Initialize with graph edge weights
        for u in self.graph.adj:
            u_idx = self.node_to_idx[u]
            for v, data in self.graph.adj[u].items():
                v_idx = self.node_to_idx[v]
                w = data["weight"]
                if w < self.dist_matrix[u_idx][v_idx]:
                    self.dist_matrix[u_idx][v_idx] = w
                    self.next_matrix[u_idx][v_idx] = v_idx

        # Floyd-Warshall 3 nested loops
        self.total_iterations = 0
        for k in range(V):
            for i in range(V):
                if self.dist_matrix[i][k] == float('inf'):
                    continue
                for j in range(V):
                    self.total_iterations += 1
                    via_k = self.dist_matrix[i][k] + self.dist_matrix[k][j]
                    if via_k < self.dist_matrix[i][j]:
                        self.dist_matrix[i][j] = round(via_k, 3)
                        self.next_matrix[i][j] = self.next_matrix[i][k]

        self.computation_time_ms = (time.perf_counter() - start_time) * 1000.0
        self.computed = True
        return self.computation_time_ms

    def reconstruct_path(self, u_id: str, v_id: str) -> List[str]:
        """Reconstruct shortest path using next_matrix pointers."""
        if not self.computed:
            self.compute()

        if u_id not in self.node_to_idx or v_id not in self.node_to_idx:
            return []

        u_idx = self.node_to_idx[u_id]
        v_idx = self.node_to_idx[v_id]

        if self.dist_matrix[u_idx][v_idx] == float('inf'):
            return []

        path_indices = [u_idx]
        curr = u_idx
        while curr != v_idx:
            next_hop = self.next_matrix[curr][v_idx]
            if next_hop is None:
                return []
            path_indices.append(next_hop)
            curr = next_hop
            if len(path_indices) > self.V:
                return []

        return [self.idx_to_node[idx] for idx in path_indices]

    def get_distance(self, u_id: str, v_id: str) -> float:
        if not self.computed:
            self.compute()
        if u_id not in self.node_to_idx or v_id not in self.node_to_idx:
            return float('inf')
        return self.dist_matrix[self.node_to_idx[u_id]][self.node_to_idx[v_id]]

    def get_serializable_matrix(self) -> Dict[str, Any]:
        """Returns distance matrix formatted for frontend table display."""
        if not self.computed:
            self.compute()

        formatted_matrix = []
        for i in range(self.V):
            row = []
            for j in range(self.V):
                val = self.dist_matrix[i][j]
                row.append(round(val, 1) if val != float('inf') else "∞")
            formatted_matrix.append(row)

        node_headers = [
            {"id": nid, "name": self.graph.nodes[nid]["name"]} 
            for nid in self.nodes_list
        ]

        return {
            "node_headers": node_headers,
            "matrix": formatted_matrix
        }

    def has_negative_cycle(self) -> bool:
        if not self.computed:
            self.compute()
        for i in range(self.V):
            if self.dist_matrix[i][i] < 0:
                return True
        return False


def floyd_warshall(graph: Graph, source: str, target: str) -> Dict[str, Any]:
    """
    Standard function wrapper to solve single-pair path using Floyd-Warshall.
    Returns path, distance, computation metrics, distance matrix, and step breakdown.
    """
    if source not in graph.nodes:
        raise ValueError(f"Source node '{source}' not found in graph.")
    if target not in graph.nodes:
        raise ValueError(f"Target node '{target}' not found in graph.")

    fw = FloydWarshall(graph)
    total_compute_time = fw.compute()

    lookup_start = time.perf_counter()
    path = fw.reconstruct_path(source, target)
    cost = fw.get_distance(source, target)
    lookup_time_ms = (time.perf_counter() - lookup_start) * 1000.0

    # Build turn-by-turn edge details
    path_details: List[Dict[str, Any]] = []
    found = len(path) > 0 and path[-1] == target

    if found:
        for i in range(len(path) - 1):
            u_node = path[i]
            v_node = path[i + 1]
            edge_info = graph.get_edge_data(u_node, v_node) or {}
            w = edge_info.get("weight", graph.get_edge_weight(u_node, v_node))
            path_details.append({
                "step": i + 1,
                "from_id": u_node,
                "from_name": graph.nodes[u_node]["name"],
                "to_id": v_node,
                "to_name": graph.nodes[v_node]["name"],
                "road_name": edge_info.get("road_name", f"{u_node} -> {v_node}"),
                "road_type": edge_info.get("road_type", "primary"),
                "segment_cost_km": w,
                "speed_kmh": edge_info.get("speed_kmh", 40.0),
                "estimated_time_min": edge_info.get("estimated_time_min", round((w / 40.0) * 60, 1))
            })

    total_time_min = sum(step["estimated_time_min"] for step in path_details)
    matrix_data = fw.get_serializable_matrix()

    source_idx = fw.node_to_idx.get(source, 0)
    target_idx = fw.node_to_idx.get(target, 0)

    shortest_path_info = (
        f"DP Subproblem D[{source}][{target}] evaluated across all {fw.V} intermediate vertices. "
        f"Minimum global cost = {cost} km via {len(path)} junctions."
    )

    return {
        "algorithm": "Floyd-Warshall Algorithm",
        "algorithm_key": "floyd_warshall",
        "source": source,
        "target": target,
        "source_idx": source_idx,
        "target_idx": target_idx,
        "found": found,
        "path": path,
        "path_names": [graph.nodes[nid]["name"] for nid in path] if path else [],
        "cost": round(cost, 2) if cost < float('inf') else None,
        "total_time_min": round(total_time_min, 1),
        "path_details": path_details,
        "visited_order": list(graph.nodes.keys()),
        "visited_count": len(graph.nodes),
        "execution_time_ms": round(total_compute_time, 4),
        "lookup_time_ms": round(lookup_time_ms, 4),
        "total_iterations": fw.total_iterations,
        "matrix_size": f"{fw.V}x{fw.V}",
        "distance_matrix": matrix_data["matrix"],
        "matrix_headers": matrix_data["node_headers"],
        "shortest_path_info": shortest_path_info,
        "time_complexity": "Θ(V³)",
        "space_complexity": "Θ(V²)",
        "optimality_guarantee": "Dynamic programming optimal substructure guarantees exact shortest path for all pairs."
    }

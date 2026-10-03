import heapq
import time
from typing import Dict, List, Optional, Any, Tuple
from algorithms.graph import Graph

def dijkstra(graph: Graph, source: str, target: str) -> Dict[str, Any]:
    """
    Computes the shortest path from source to target using Dijkstra's Algorithm.
    Uses a min-heap priority queue for optimal time complexity O((V + E) log V).
    
    Tracks visited node sequence, relaxation steps, and precise execution time
    for DAA analysis and visualization.
    """
    if source not in graph.nodes:
        raise ValueError(f"Source node '{source}' not found in graph.")
    if target not in graph.nodes:
        raise ValueError(f"Target node '{target}' not found in graph.")

    start_time = time.perf_counter()

    # Distances map: initial infinity for all
    distances: Dict[str, float] = {node_id: float('inf') for node_id in graph.nodes}
    distances[source] = 0.0

    # Predecessor map for path reconstruction
    predecessors: Dict[str, Optional[str]] = {node_id: None for node_id in graph.nodes}

    # Priority queue storing tuples: (current_distance, node_id)
    pq: List[Tuple[float, str]] = []
    heapq.heappush(pq, (0.0, source))

    visited_order: List[str] = []
    visited_nodes_details: List[Dict[str, Any]] = []
    visited_set = set()
    heap_operations = 1  # 1 push
    relaxations_count = 0
    found = False

    while pq:
        current_dist, u = heapq.heappop(pq)
        heap_operations += 1

        # If we already settled u with a strictly smaller distance, skip
        if current_dist > distances[u]:
            continue

        if u not in visited_set:
            visited_set.add(u)
            visited_order.append(u)
            parent_name = graph.nodes[predecessors[u]]["name"] if predecessors[u] else "Origin (Start)"
            visited_nodes_details.append({
                "step": len(visited_order),
                "node_id": u,
                "node_name": graph.nodes[u]["name"],
                "settled_distance": round(current_dist, 2),
                "parent": parent_name
            })

        # Early termination once target is popped (greedy property guarantees optimality)
        if u == target:
            found = True
            break

        # Edge relaxation for each outgoing neighbor
        for v, edge_data in graph.get_neighbors(u).items():
            weight = edge_data["weight"]
            new_dist = current_dist + weight

            # Relaxation condition
            if new_dist < distances[v]:
                distances[v] = round(new_dist, 3)
                predecessors[v] = u
                heapq.heappush(pq, (distances[v], v))
                heap_operations += 1
                relaxations_count += 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    # Reconstruct path if reachable
    path: List[str] = []
    path_details: List[Dict[str, Any]] = []
    total_cost: Optional[float] = None

    if found or (distances[target] < float('inf') and distances[target] >= 0):
        curr: Optional[str] = target
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
        path.reverse()

        total_cost = round(distances[target], 2)

        # Build turn-by-turn edge details
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
    is_found = found or (len(path) > 0 and path[-1] == target)

    return {
        "algorithm": "Dijkstra's Algorithm",
        "algorithm_key": "dijkstra",
        "source": source,
        "target": target,
        "found": is_found,
        "path": path,
        "path_names": [graph.nodes[nid]["name"] for nid in path] if path else [],
        "cost": total_cost if is_found else None,  # total distance in km (None if unreachable)
        "total_time_min": round(total_time_min, 1),
        "path_details": path_details,
        "visited_order": visited_order,
        "visited_count": len(visited_order),
        "visited_nodes_details": visited_nodes_details,
        "heap_operations": heap_operations,
        "relaxations_count": relaxations_count,
        "execution_time_ms": round(elapsed_ms, 4),
        "time_complexity": "O((V + E) log V)",
        "space_complexity": "O(V)",
        "optimality_guarantee": "Guaranteed globally optimal for non-negative edge weights (Greedy choice property)."
    }

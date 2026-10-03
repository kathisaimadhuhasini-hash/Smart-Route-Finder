import heapq
import time
from typing import Dict, List, Optional, Any, Tuple
from algorithms.graph import Graph

def astar(graph: Graph, source: str, target: str, heuristic: str = "haversine") -> Dict[str, Any]:
    """
    Computes the shortest path from source to target using the A* Search Algorithm.
    
    Uses evaluation function f(n) = g(n) + h(n):
    - g(n): exact cost from start to n
    - h(n): admissible heuristic from n to target (Haversine straight-line distance)
    
    Because Haversine distance satisfies the triangle inequality on the sphere,
    h(n) <= d*(n, target) (Admissible) and h(u) <= c(u, v) + h(v) (Consistent/Monotone).
    This guarantees A* finds an optimal path while expanding fewer nodes than Dijkstra.
    """
    if source not in graph.nodes:
        raise ValueError(f"Source node '{source}' not found in graph.")
    if target not in graph.nodes:
        raise ValueError(f"Target node '{target}' not found in graph.")

    start_time = time.perf_counter()

    # Heuristic function selector
    def calc_h(node_id: str) -> float:
        if heuristic == "euclidean":
            return graph.euclidean_distance(node_id, target)
        return graph.haversine_distance(node_id, target)

    # g_score: exact distance from start to node
    g_score: Dict[str, float] = {node_id: float('inf') for node_id in graph.nodes}
    g_score[source] = 0.0

    # f_score: g_score + h_score
    f_score: Dict[str, float] = {node_id: float('inf') for node_id in graph.nodes}
    initial_h = calc_h(source)
    f_score[source] = initial_h

    # Track heuristics computed for analysis
    h_cache: Dict[str, float] = {source: initial_h}

    # Predecessors for path reconstruction
    predecessors: Dict[str, Optional[str]] = {node_id: None for node_id in graph.nodes}

    # Priority queue storing tuples: (f_score, tie_breaker_counter, node_id)
    counter = 0
    open_heap: List[Tuple[float, int, str]] = []
    heapq.heappush(open_heap, (f_score[source], counter, source))

    visited_order: List[str] = []
    explored_states: List[Dict[str, Any]] = []
    closed_set = set()
    open_set_operations = 1
    evaluations_count = 0
    found = False

    while open_heap:
        current_f, _, u = heapq.heappop(open_heap)
        open_set_operations += 1

        if u in closed_set:
            continue

        closed_set.add(u)
        visited_order.append(u)

        h_val = h_cache.get(u, calc_h(u))
        g_val = g_score[u]
        f_val = g_val + h_val

        parent_name = graph.nodes[predecessors[u]]["name"] if predecessors[u] else "Origin (Start)"
        explored_states.append({
            "step": len(visited_order),
            "node_id": u,
            "node_name": graph.nodes[u]["name"],
            "g": round(g_val, 2),
            "h": round(h_val, 2),
            "f": round(f_val, 2),
            "parent": parent_name
        })

        # Goal reached
        if u == target:
            found = True
            break

        # Explore neighbors
        for v, edge_data in graph.get_neighbors(u).items():
            if v in closed_set:
                continue

            weight = edge_data["weight"]
            tentative_g = g_score[u] + weight

            if tentative_g < g_score[v]:
                predecessors[v] = u
                g_score[v] = round(tentative_g, 3)

                if v not in h_cache:
                    h_cache[v] = calc_h(v)
                
                f_score[v] = round(g_score[v] + h_cache[v], 3)
                counter += 1
                heapq.heappush(open_heap, (f_score[v], counter, v))
                open_set_operations += 1
                evaluations_count += 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    # Reconstruct path
    path: List[str] = []
    path_details: List[Dict[str, Any]] = []
    total_cost: Optional[float] = None

    if found or (g_score[target] < float('inf') and g_score[target] >= 0):
        curr: Optional[str] = target
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
        path.reverse()

        total_cost = round(g_score[target], 2)

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
        "algorithm": "A* Search Algorithm",
        "algorithm_key": "astar",
        "source": source,
        "target": target,
        "found": is_found,
        "path": path,
        "path_names": [graph.nodes[nid]["name"] for nid in path] if path else [],
        "cost": total_cost if is_found else None,
        "total_time_min": round(total_time_min, 1),
        "path_details": path_details,
        "visited_order": visited_order,
        "visited_count": len(visited_order),
        "explored_states": explored_states,
        "heap_operations": open_set_operations,
        "evaluations_count": evaluations_count,
        "execution_time_ms": round(elapsed_ms, 4),
        "heuristic_used": f"{heuristic.capitalize()} Distance (km)",
        "admissibility_proof": "h(n) <= d*(n, goal) because straight-line distance is geodesic lower bound.",
        "time_complexity": "O(E) best/average case with good heuristic, O((V + E) log V) worst case",
        "space_complexity": "O(V)",
        "optimality_guarantee": "Guaranteed optimal because heuristic is strictly admissible and consistent."
    }

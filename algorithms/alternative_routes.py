import copy
from typing import Dict, List, Any
from algorithms.graph import Graph
from algorithms.dijkstra import dijkstra

def find_alternative_routes(graph: Graph, source: str, target: str, 
                            optimal_path: List[str], max_alternatives: int = 2) -> List[Dict[str, Any]]:
    """
    Finds realistic alternative paths between source and target using edge-penalty and deviation routing.
    Compares each alternative route against the optimal path, providing distance differences,
    time differences, and divergence descriptions.
    """
    if not optimal_path or len(optimal_path) < 2:
        return []

    alternatives: List[Dict[str, Any]] = []
    seen_paths = {tuple(optimal_path)}
    base_cost = dijkstra(graph, source, target)["cost"]

    # Strategy 1: Edge Penalty Routing
    # Increase the weight of edges in the primary path by 50% to find a parallel corridor
    penalized_graph = copy.deepcopy(graph)
    for i in range(len(optimal_path) - 1):
        u, v = optimal_path[i], optimal_path[i + 1]
        if u in penalized_graph.adj and v in penalized_graph.adj[u]:
            penalized_graph.adj[u][v]["weight"] *= 1.6
        if v in penalized_graph.adj and u in penalized_graph.adj[v]:
            penalized_graph.adj[v][u]["weight"] *= 1.6

    alt1_res = dijkstra(penalized_graph, source, target)
    if alt1_res["found"] and tuple(alt1_res["path"]) not in seen_paths:
        # Calculate real cost on the original graph
        real_cost = 0.0
        path = alt1_res["path"]
        valid = True
        for i in range(len(path) - 1):
            w = graph.get_edge_weight(path[i], path[i + 1])
            if w == float('inf'):
                valid = False
                break
            real_cost += w

        if valid and real_cost >= base_cost:
            seen_paths.add(tuple(path))
            delta_cost = round(real_cost - base_cost, 2)
            pct_slower = round((delta_cost / max(base_cost, 0.001)) * 100, 1)

            # Find key detour node
            detour_nodes = [nid for nid in path if nid not in optimal_path]
            detour_label = graph.nodes[detour_nodes[0]]["name"] if detour_nodes else "Alternative corridor"

            alternatives.append({
                "id": "alt_1",
                "label": f"Alternative 1 (via {detour_label})",
                "path": path,
                "path_names": [graph.nodes[nid]["name"] for nid in path],
                "cost": round(real_cost, 2),
                "delta_km": delta_cost,
                "delta_pct": pct_slower,
                "detour_via": detour_label,
                "reason_suboptimal": f"Adds +{delta_cost} km (+{pct_slower}%) due to routing through {detour_label}."
            })

    # Strategy 2: Remove primary corridor intermediate edge to find second alternative
    if len(optimal_path) >= 3 and len(alternatives) < max_alternatives:
        # Pick the middle edge of the optimal path
        mid_idx = len(optimal_path) // 2
        u_mid, v_mid = optimal_path[mid_idx - 1], optimal_path[mid_idx]

        bypassed_graph = copy.deepcopy(graph)
        if u_mid in bypassed_graph.adj and v_mid in bypassed_graph.adj[u_mid]:
            del bypassed_graph.adj[u_mid][v_mid]
        if v_mid in bypassed_graph.adj and u_mid in bypassed_graph.adj[v_mid]:
            del bypassed_graph.adj[v_mid][u_mid]

        alt2_res = dijkstra(bypassed_graph, source, target)
        if alt2_res["found"] and tuple(alt2_res["path"]) not in seen_paths:
            path2 = alt2_res["path"]
            real_cost2 = 0.0
            valid2 = True
            for i in range(len(path2) - 1):
                w = graph.get_edge_weight(path2[i], path2[i + 1])
                if w == float('inf'):
                    valid2 = False
                    break
                real_cost2 += w

            if valid2 and real_cost2 >= base_cost:
                seen_paths.add(tuple(path2))
                delta_cost2 = round(real_cost2 - base_cost, 2)
                pct_slower2 = round((delta_cost2 / max(base_cost, 0.001)) * 100, 1)
                detour_nodes2 = [nid for nid in path2 if nid not in optimal_path]
                detour_label2 = graph.nodes[detour_nodes2[0]]["name"] if detour_nodes2 else "Secondary bypass"

                alternatives.append({
                    "id": "alt_2",
                    "label": f"Alternative 2 (via {detour_label2})",
                    "path": path2,
                    "path_names": [graph.nodes[nid]["name"] for nid in path2],
                    "cost": round(real_cost2, 2),
                    "delta_km": delta_cost2,
                    "delta_pct": pct_slower2,
                    "detour_via": detour_label2,
                    "reason_suboptimal": f"Bypasses the main expressway, incurring +{delta_cost2} km (+{pct_slower2}%) extra transit."
                })

    return alternatives

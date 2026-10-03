from typing import Dict, List, Any
from algorithms.graph import Graph

def generate_route_explanation(graph: Graph, algorithm_name: str, optimal_result: Dict[str, Any], 
                               alternatives: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generates a comprehensive DAA-grade explanation of why the selected route is mathematically
    and physically optimal compared to alternatives.
    """
    path = optimal_result.get("path", [])
    path_names = optimal_result.get("path_names", [])
    cost = optimal_result.get("cost", 0.0)
    source_name = path_names[0] if path_names else ""
    target_name = path_names[-1] if path_names else ""

    # Mathematical justification based on chosen algorithm
    algo_key = optimal_result.get("algorithm_key", "dijkstra")
    if algo_key == "astar":
        proof_summary = (
            "A* Search guarantees optimality using an admissible and consistent heuristic: "
            "h(n) = Haversine straight-line distance <= d*(n, target). "
            "Because physical road distances cannot be shorter than the straight-line geodesic distance "
            "(triangle inequality in metric space), the heuristic never overestimates. "
            "Consequently, the first time the destination is popped from the open set, its path is guaranteed optimal."
        )
        daa_principle = "Heuristic Guided Search & Branch-and-Bound Pruning"
    elif algo_key == "floyd_warshall":
        proof_summary = (
            "Floyd-Warshall guarantees global optimality via the Dynamic Programming Principle of Optimality: "
            "D^(k)[i][j] = min( D^(k-1)[i][j], D^(k-1)[i][k] + D^(k-1)[k][j] ). "
            "By exhaustively evaluating all intermediate vertex sets {1...|V|}, it proves that no intermediate "
            "combination can yield a lower total path weight."
        )
        daa_principle = "Dynamic Programming & All-Pairs Optimal Substructure"
    else:
        proof_summary = (
            "Dijkstra's Algorithm guarantees optimality via the Greedy Choice Property on graphs with non-negative weights (w >= 0). "
            "At each step, the unsettled vertex with minimum distance is extracted. "
            "Since all edge weights are positive, adding any future path cannot decrease this distance. "
            "By mathematical induction, every extracted vertex has achieved its final shortest distance."
        )
        daa_principle = "Greedy Choice Property & Edge Relaxation"

    # Step-by-step edge analysis
    edge_breakdown = []
    for step in optimal_result.get("path_details", []):
        edge_breakdown.append(
            f"Segment {step['step']}: {step['from_name']} -> {step['to_name']} "
            f"via {step['road_name']} ({step['segment_cost_km']} km, ~{step['estimated_time_min']} mins at {step['speed_kmh']} km/h)"
        )

    # Comparison against alternatives
    alt_comparisons = []
    if alternatives:
        for alt in alternatives:
            if alt["delta_km"] == 0:
                explanation_text = (
                    f"Equal Cost Alternative: Route through {alt['detour_via']} offers an identical travel cost of "
                    f"{alt['cost']} km as a viable parallel corridor."
                )
            else:
                explanation_text = (
                    f"Suboptimal: Route through {alt['detour_via']} requires {alt['cost']} km "
                    f"(+{alt['delta_km']} km / +{alt['delta_pct']}% longer) due to additional arterial segments."
                )

            alt_comparisons.append({
                "label": alt["label"],
                "cost": alt["cost"],
                "delta_km": alt["delta_km"],
                "delta_pct": alt["delta_pct"],
                "explanation": explanation_text
            })
    else:
        alt_comparisons.append({
            "label": "Direct / Single Viable Corridor",
            "cost": cost,
            "delta_km": 0.0,
            "delta_pct": 0.0,
            "explanation": "No distinct viable alternative corridor exists for this pair with reasonable detour bounds."
        })

    if len(path) <= 1:
        key_takeaway = f"Source and destination are identical ({source_name}); path cost is trivially 0.0 km."
        optimality_verdict = "Trivially Optimal (Zero Distance)."
    elif alternatives and alternatives[0]["delta_km"] > 0:
        key_takeaway = (
            f"The selected route between {source_name} and {target_name} via {len(path)} junctions "
            f"achieves the minimum possible travel cost of {cost} km. "
            f"It saves {alternatives[0]['delta_km']} km compared to {alternatives[0]['label']}."
        )
        optimality_verdict = f"Strictly Optimal ({cost} km is the theoretical global minimum on this graph)."
    elif alternatives and alternatives[0]["delta_km"] == 0:
        key_takeaway = (
            f"The selected route between {source_name} and {target_name} via {len(path)} junctions "
            f"achieves the minimum travel cost of {cost} km, tying with parallel corridor {alternatives[0]['label']}."
        )
        optimality_verdict = f"Optimal (Tied at {cost} km with parallel corridor)."
    else:
        key_takeaway = (
            f"The selected route between {source_name} and {target_name} via {len(path)} junctions "
            f"achieves the minimum possible travel cost of {cost} km."
        )
        optimality_verdict = f"Strictly Optimal ({cost} km is the theoretical global minimum on this graph)."

    return {
        "daa_principle": daa_principle,
        "proof_summary": proof_summary,
        "key_takeaway": key_takeaway,
        "edge_breakdown": edge_breakdown,
        "alternatives_comparison": alt_comparisons,
        "optimality_verdict": optimality_verdict
    }

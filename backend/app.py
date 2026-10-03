import os
import sys
from flask import Flask, jsonify, request, render_template

# Add parent directory to sys.path to resolve 'algorithms' and 'backend'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algorithms.graph import Graph
from algorithms.dijkstra import dijkstra
from algorithms.astar import astar
from algorithms.floyd_warshall import floyd_warshall, FloydWarshall
from algorithms.alternative_routes import find_alternative_routes
from algorithms.explainer import generate_route_explanation
from backend.database import load_graph_from_db, log_route_query, get_recent_queries, init_db

# Configure template and static folders inside frontend/
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
templates_dir = os.path.join(frontend_dir, "templates")
static_dir = os.path.join(frontend_dir, "static")

app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)

# Initialize database and load graph
init_db()
graph: Graph = load_graph_from_db()
# Pre-initialize Floyd-Warshall cache for instant all-pairs matrix lookups if needed
fw_manager = FloydWarshall(graph)
fw_manager.compute()

@app.route("/")
def index():
    """Renders the main single-page UI for Smart Route Finder."""
    return render_template("index.html")

@app.route("/api/graph", methods=["GET"])
def get_graph():
    """Returns the graph nodes and edges for Leaflet map visualization."""
    return jsonify({
        "success": True,
        "nodes": graph.get_all_nodes(),
        "edges": graph.get_all_edges(),
        "total_nodes": len(graph.nodes),
        "total_edges": len(graph.get_all_edges()),
        "bounds": {
            "min_lat": min(n["lat"] for n in graph.nodes.values()),
            "max_lat": max(n["lat"] for n in graph.nodes.values()),
            "min_lon": min(n["lon"] for n in graph.nodes.values()),
            "max_lon": max(n["lon"] for n in graph.nodes.values())
        }
    })

@app.route("/api/route", methods=["POST"])
def compute_route():
    """
    Finds the shortest route using the specified algorithm (dijkstra, astar, floyd_warshall).
    Computes alternative paths and provides a DAA optimality explanation.
    """
    data = request.get_json() or {}
    source = data.get("source")
    target = data.get("target")
    algorithm = (data.get("algorithm") or "dijkstra").lower()

    if not source or not target:
        return jsonify({"success": False, "error": "Both 'source' and 'target' are required."}), 400

    if source not in graph.nodes or target not in graph.nodes:
        return jsonify({"success": False, "error": f"Invalid source or target ID. Available nodes: {list(graph.nodes.keys())}"}), 400

    # Execute the requested algorithm dynamically
    try:
        if algorithm == "astar":
            result = astar(graph, source, target)
        elif algorithm in ["floyd_warshall", "floyd", "fw"]:
            result = floyd_warshall(graph, source, target)
        else:
            result = dijkstra(graph, source, target)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

    if not result.get("found"):
        return jsonify({"success": False, "error": f"No valid route found between {source} and {target}."}), 404

    # Calculate real alternative routes
    optimal_path = result.get("path", [])
    alternatives = find_alternative_routes(graph, source, target, optimal_path, max_alternatives=2)

    # Generate DAA optimality explanation
    explanation = generate_route_explanation(graph, result["algorithm"], result, alternatives)

    # Log to SQLite
    log_route_query(
        source=source,
        target=target,
        algorithm=result["algorithm"],
        cost=result.get("cost", 0.0) or 0.0,
        visited_count=result.get("visited_count", 0),
        execution_time_ms=result.get("execution_time_ms", 0.0)
    )

    return jsonify({
        "success": True,
        "optimal_route": result,
        "alternatives": alternatives,
        "explanation": explanation
    })

@app.route("/api/compare", methods=["POST"])
def compare_algorithms():
    """
    Executes Dijkstra, A*, and Floyd-Warshall on the same input.
    Returns side-by-side performance benchmarks and theoretical metrics.
    """
    data = request.get_json() or {}
    source = data.get("source")
    target = data.get("target")

    if not source or not target:
        return jsonify({"success": False, "error": "Both 'source' and 'target' are required."}), 400

    if source not in graph.nodes or target not in graph.nodes:
        return jsonify({"success": False, "error": "Invalid source or target ID."}), 400

    # 1. Dijkstra
    res_dijkstra = dijkstra(graph, source, target)

    # 2. A* Search
    res_astar = astar(graph, source, target)

    # 3. Floyd-Warshall
    res_fw = floyd_warshall(graph, source, target)

    # Verify optimality consistency (all 3 should discover the exact same minimal cost)
    all_found = res_dijkstra["found"] and res_astar["found"] and res_fw["found"]
    all_unreachable = (not res_dijkstra["found"]) and (not res_astar["found"]) and (not res_fw["found"])

    if all_found:
        costs = [res_dijkstra["cost"], res_astar["cost"], res_fw["cost"]]
        optimality_consistent = (abs(costs[0] - costs[1]) < 1e-3) and (abs(costs[0] - costs[2]) < 1e-3)
        optimal_cost_km = res_dijkstra["cost"]
    elif all_unreachable:
        optimality_consistent = True
        optimal_cost_km = None
    else:
        optimality_consistent = False
        optimal_cost_km = None

    comparison_summary = {
        "source": source,
        "source_name": graph.nodes[source]["name"],
        "target": target,
        "target_name": graph.nodes[target]["name"],
        "optimality_consistent": optimality_consistent,
        "optimal_cost_km": optimal_cost_km,
        "algorithms": {
            "dijkstra": {
                "name": "Dijkstra's Algorithm",
                "cost_km": res_dijkstra["cost"],
                "execution_time_ms": res_dijkstra["execution_time_ms"],
                "nodes_visited": res_dijkstra["visited_count"],
                "operations": res_dijkstra["heap_operations"],
                "time_complexity": res_dijkstra["time_complexity"],
                "space_complexity": res_dijkstra["space_complexity"],
                "approach": "Greedy (Uninformed Uniform-Cost)",
                "strengths": "Reliable, exact, optimal for single-source all-destinations with w >= 0.",
                "weaknesses": "Explores radially in all directions without destination awareness."
            },
            "astar": {
                "name": "A* Search",
                "cost_km": res_astar["cost"],
                "execution_time_ms": res_astar["execution_time_ms"],
                "nodes_visited": res_astar["visited_count"],
                "operations": res_astar["heap_operations"],
                "time_complexity": res_astar["time_complexity"],
                "space_complexity": res_astar["space_complexity"],
                "approach": "Informed Heuristic Search (f = g + h)",
                "strengths": f"Heuristic pruning directs search towards goal; expanded {res_astar['visited_count']} nodes vs Dijkstra's {res_dijkstra['visited_count']}.",
                "weaknesses": "Depends on heuristic quality; extra computation per node for distance calculations."
            },
            "floyd_warshall": {
                "name": "Floyd-Warshall",
                "cost_km": res_fw["cost"],
                "execution_time_ms": res_fw["execution_time_ms"],
                "lookup_time_ms": res_fw.get("lookup_time_ms", 0.0),
                "nodes_visited": res_fw["visited_count"],
                "operations": res_fw["total_iterations"],
                "time_complexity": res_fw["time_complexity"],
                "space_complexity": res_fw["space_complexity"],
                "approach": "Dynamic Programming (All-Pairs)",
                "strengths": "Solves all-pairs simultaneously. Once matrix is computed, any pair query is O(1) distance / O(V) path.",
                "weaknesses": "O(V^3) computation overhead makes it prohibitive for massive real-time road networks."
            }
        },
        "efficiency_analysis": (
            f"A* searched {res_astar['visited_count']} nodes compared to Dijkstra's {res_dijkstra['visited_count']} nodes "
            f"({round((1 - res_astar['visited_count'] / max(res_dijkstra['visited_count'], 1)) * 100, 1)}% node pruning) "
            f"while guaranteeing the identical optimal cost of {res_dijkstra['cost']} km. "
            f"Floyd-Warshall evaluated {res_fw['total_iterations']} subproblem transitions across all {len(graph.nodes)} vertices."
        )
    }

    return jsonify({
        "success": True,
        "comparison": comparison_summary,
        "results": {
            "dijkstra": res_dijkstra,
            "astar": res_astar,
            "floyd_warshall": res_fw
        }
    })

@app.route("/api/history", methods=["GET"])
def get_history():
    """Returns recent queries from the SQLite database."""
    return jsonify({
        "success": True,
        "history": get_recent_queries(limit=10)
    })

@app.route("/api/reset-graph", methods=["POST"])
def reset_graph():
    """Resets graph to default sample data."""
    global graph, fw_manager
    init_db(force_reseed=True)
    graph = load_graph_from_db()
    fw_manager = FloydWarshall(graph)
    fw_manager.compute()
    return jsonify({"success": True, "message": "Graph reset to default sample network."})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

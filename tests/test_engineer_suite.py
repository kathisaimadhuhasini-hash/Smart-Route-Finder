import unittest
import json
import random
import math
from algorithms.graph import Graph
from algorithms.dijkstra import dijkstra
from algorithms.astar import astar
from algorithms.floyd_warshall import floyd_warshall, FloydWarshall
from algorithms.alternative_routes import find_alternative_routes
from algorithms.explainer import generate_route_explanation
from backend.sample_data import build_sample_graph
from backend.app import app

class DAAEngineerComprehensiveTestSuite(unittest.TestCase):
    """
    Exhaustive DAA Testing & Debugging Suite covering:
    - Normal routes
    - Multiple routes
    - Source = Destination
    - Unreachable destinations
    - Invalid locations
    - Equal-cost routes
    - Different edge weights (varied, decimal, large)
    - Small graphs (triangle, chain, diamond)
    - Larger graphs (grid / synthetic networks)
    - Verification of Dijkstra, A*, Floyd-Warshall, path reconstruction, comparison, and API.
    """

    def setUp(self):
        self.sample_graph = build_sample_graph()
        self.client = app.test_client()
        self.client.testing = True

    # -------------------------------------------------------------
    # 1. NORMAL ROUTES
    # -------------------------------------------------------------
    def test_normal_route_dijkstra(self):
        res = dijkstra(self.sample_graph, "CYBER_TOWERS", "FINANCIAL_DISTRICT")
        self.assertTrue(res["found"])
        self.assertAlmostEqual(res["cost"], 7.1, places=1)
        self.assertEqual(res["path"][0], "CYBER_TOWERS")
        self.assertEqual(res["path"][-1], "FINANCIAL_DISTRICT")
        self.assertGreater(len(res["path_details"]), 0)

    def test_normal_route_astar(self):
        res = astar(self.sample_graph, "CYBER_TOWERS", "FINANCIAL_DISTRICT")
        self.assertTrue(res["found"])
        self.assertAlmostEqual(res["cost"], 7.1, places=1)
        self.assertIn("explored_states", res)
        self.assertGreater(len(res["explored_states"]), 0)

    def test_normal_route_floyd_warshall(self):
        res = floyd_warshall(self.sample_graph, "CYBER_TOWERS", "FINANCIAL_DISTRICT")
        self.assertTrue(res["found"])
        self.assertAlmostEqual(res["cost"], 7.1, places=1)
        self.assertIn("distance_matrix", res)

    # -------------------------------------------------------------
    # 2. MULTIPLE ROUTES & ALTERNATIVES
    # -------------------------------------------------------------
    def test_multiple_routes_alternatives(self):
        res = dijkstra(self.sample_graph, "CYBER_TOWERS", "FINANCIAL_DISTRICT")
        alts = find_alternative_routes(self.sample_graph, "CYBER_TOWERS", "FINANCIAL_DISTRICT", res["path"])
        self.assertGreater(len(alts), 0)
        for alt in alts:
            self.assertGreaterEqual(alt["cost"], res["cost"])
            self.assertNotEqual(alt["path"], res["path"])
            # Verify alternative path continuity
            for i in range(len(alt["path"]) - 1):
                w = self.sample_graph.get_edge_weight(alt["path"][i], alt["path"][i + 1])
                self.assertLess(w, float('inf'))

    # -------------------------------------------------------------
    # 3. SOURCE = DESTINATION (IDENTITY CASE)
    # -------------------------------------------------------------
    def test_source_equals_destination_dijkstra(self):
        res = dijkstra(self.sample_graph, "CYBER_TOWERS", "CYBER_TOWERS")
        self.assertTrue(res["found"])
        self.assertEqual(res["path"], ["CYBER_TOWERS"])
        self.assertEqual(res["cost"], 0.0)

    def test_source_equals_destination_astar(self):
        res = astar(self.sample_graph, "CYBER_TOWERS", "CYBER_TOWERS")
        self.assertTrue(res["found"])
        self.assertEqual(res["path"], ["CYBER_TOWERS"])
        self.assertEqual(res["cost"], 0.0)
        self.assertEqual(res["explored_states"][0]["g"], 0.0)
        self.assertEqual(res["explored_states"][0]["h"], 0.0)

    def test_source_equals_destination_floyd(self):
        res = floyd_warshall(self.sample_graph, "CYBER_TOWERS", "CYBER_TOWERS")
        self.assertTrue(res["found"])
        self.assertEqual(res["path"], ["CYBER_TOWERS"])
        self.assertEqual(res["cost"], 0.0)

    def test_source_equals_destination_api(self):
        payload = {"source": "CYBER_TOWERS", "target": "CYBER_TOWERS", "algorithm": "astar"}
        response = self.client.post("/api/route", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["optimal_route"]["cost"], 0.0)
        self.assertEqual(data["optimal_route"]["path"], ["CYBER_TOWERS"])

    # -------------------------------------------------------------
    # 4. UNREACHABLE DESTINATION (DISCONNECTED GRAPH)
    # -------------------------------------------------------------
    def test_unreachable_destination(self):
        g = Graph(directed=True)
        g.add_node("S", "Start", 17.0, 78.0)
        g.add_node("A", "Node A", 17.1, 78.1)
        g.add_node("ISO", "Isolated Island", 17.5, 78.5)
        g.add_edge("S", "A", 2.0)

        # Dijkstra on unreachable
        d_res = dijkstra(g, "S", "ISO")
        self.assertFalse(d_res["found"])
        self.assertIsNone(d_res["cost"])
        self.assertEqual(d_res["path"], [])

        # A* on unreachable
        a_res = astar(g, "S", "ISO")
        self.assertFalse(a_res["found"])
        self.assertIsNone(a_res["cost"])
        self.assertEqual(a_res["path"], [])

        # Floyd-Warshall on unreachable
        fw_res = floyd_warshall(g, "S", "ISO")
        self.assertFalse(fw_res["found"])
        self.assertIsNone(fw_res["cost"])
        self.assertEqual(fw_res["path"], [])

    # -------------------------------------------------------------
    # 5. INVALID LOCATIONS & ERROR HANDLING
    # -------------------------------------------------------------
    def test_invalid_location_dijkstra_raises(self):
        with self.assertRaises(ValueError):
            dijkstra(self.sample_graph, "NON_EXISTENT", "CYBER_TOWERS")
        with self.assertRaises(ValueError):
            dijkstra(self.sample_graph, "CYBER_TOWERS", "NON_EXISTENT")

    def test_invalid_location_api(self):
        # Missing source
        res = self.client.post("/api/route", data=json.dumps({"target": "CYBER_TOWERS"}), content_type="application/json")
        self.assertEqual(res.status_code, 400)

        # Non-existent node
        res2 = self.client.post("/api/route", data=json.dumps({"source": "FAKE_SRC", "target": "CYBER_TOWERS"}), content_type="application/json")
        self.assertEqual(res2.status_code, 400)

    # -------------------------------------------------------------
    # 6. EQUAL-COST ROUTES (TIE-BREAKING & DIVERGENCE)
    # -------------------------------------------------------------
    def test_equal_cost_routes(self):
        """Two parallel paths of equal length: S -> A -> T (cost 5) vs S -> B -> T (cost 5)."""
        g = Graph(directed=False)
        g.add_node("S", "Source", 17.0, 78.0)
        g.add_node("A", "Route North", 17.1, 78.0)
        g.add_node("B", "Route South", 16.9, 78.0)
        g.add_node("T", "Target", 17.0, 78.2)

        g.add_edge("S", "A", 2.5)
        g.add_edge("A", "T", 2.5)
        g.add_edge("S", "B", 2.5)
        g.add_edge("B", "T", 2.5)

        d_res = dijkstra(g, "S", "T")
        a_res = astar(g, "S", "T")
        fw_res = floyd_warshall(g, "S", "T")

        self.assertAlmostEqual(d_res["cost"], 5.0)
        self.assertAlmostEqual(a_res["cost"], 5.0)
        self.assertAlmostEqual(fw_res["cost"], 5.0)

        # Alternative routes should find the other parallel equal-cost corridor
        alts = find_alternative_routes(g, "S", "T", d_res["path"])
        self.assertGreater(len(alts), 0)
        self.assertAlmostEqual(alts[0]["cost"], 5.0)
        self.assertAlmostEqual(alts[0]["delta_km"], 0.0)

        # Explainer should note the equal-cost alternative cleanly
        exp = generate_route_explanation(g, "dijkstra", d_res, alts)
        self.assertIn("Equal Cost Alternative", exp["alternatives_comparison"][0]["explanation"])

    # -------------------------------------------------------------
    # 7. DIFFERENT EDGE WEIGHTS (VARIED, DECIMAL, LARGE)
    # -------------------------------------------------------------
    def test_varied_edge_weights(self):
        g = Graph(directed=False)
        g.add_node("N1", "N1", 17.0, 78.0)
        g.add_node("N2", "N2", 17.01, 78.01)
        g.add_node("N3", "N3", 17.05, 78.05)
        g.add_node("N4", "N4", 17.10, 78.10)

        # Micro decimal edge vs massive edge
        g.add_edge("N1", "N2", 0.042)
        g.add_edge("N2", "N3", 0.158)
        g.add_edge("N3", "N4", 125.75)
        g.add_edge("N1", "N4", 126.0)

        d_res = dijkstra(g, "N1", "N4")
        # Direct edge: 126.0 vs Via N2,N3: 0.042 + 0.158 + 125.75 = 125.95
        self.assertAlmostEqual(d_res["cost"], 125.95, places=2)
        self.assertEqual(d_res["path"], ["N1", "N2", "N3", "N4"])

    # -------------------------------------------------------------
    # 8. SMALL GRAPH (3-4 NODES: TRIANGLE, DIAMOND, CHAIN)
    # -------------------------------------------------------------
    def test_small_chain_graph(self):
        g = Graph(directed=False)
        for i in range(4):
            g.add_node(f"V{i}", f"Node {i}", 17.0 + i * 0.01, 78.0 + i * 0.01)
            if i > 0:
                g.add_edge(f"V{i-1}", f"V{i}", 1.5)

        res = dijkstra(g, "V0", "V3")
        self.assertEqual(res["path"], ["V0", "V1", "V2", "V3"])
        self.assertAlmostEqual(res["cost"], 4.5)

    def test_small_diamond_shortcut(self):
        g = Graph(directed=False)
        g.add_node("S", "S", 17.0, 78.0)
        g.add_node("A", "A", 17.1, 78.0)
        g.add_node("B", "B", 17.0, 78.1)
        g.add_node("T", "T", 17.1, 78.1)

        g.add_edge("S", "A", 10.0)
        g.add_edge("A", "T", 10.0)
        g.add_edge("S", "B", 1.0)
        g.add_edge("B", "T", 2.0)

        res = dijkstra(g, "S", "T")
        self.assertEqual(res["path"], ["S", "B", "T"])
        self.assertAlmostEqual(res["cost"], 3.0)

    # -------------------------------------------------------------
    # 9. LARGER GRAPH (36-NODE GRID MESH NETWORK)
    # -------------------------------------------------------------
    def test_larger_grid_graph(self):
        """Construct a 6x6 grid mesh (36 vertices, 60 bidirectional edges)."""
        grid_graph = Graph(directed=False)
        rows, cols = 6, 6

        for r in range(rows):
            for c in range(cols):
                nid = f"R{r}C{c}"
                lat = 17.40 + r * 0.02
                lon = 78.30 + c * 0.02
                grid_graph.add_node(nid, f"Junction {r},{c}", lat, lon)

        for r in range(rows):
            for c in range(cols):
                u = f"R{r}C{c}"
                if c + 1 < cols:
                    grid_graph.add_edge(u, f"R{r}C{c+1}", 2.0)
                if r + 1 < rows:
                    grid_graph.add_edge(u, f"R{r+1}C{c}", 2.0)

        src = "R0C0"
        tgt = f"R{rows-1}C{cols-1}"  # R5C5 (Manhattan distance = (5+5)*2.0 = 20.0 km)

        d_res = dijkstra(grid_graph, src, tgt)
        a_res = astar(grid_graph, src, tgt)
        fw = FloydWarshall(grid_graph)
        fw.compute()

        # 1. Dijkstra cost check
        self.assertAlmostEqual(d_res["cost"], 20.0)
        # 2. A* cost check (must match Dijkstra)
        self.assertAlmostEqual(a_res["cost"], 20.0)
        # 3. Floyd-Warshall cost check
        self.assertAlmostEqual(fw.get_distance(src, tgt), 20.0)
        # 4. Search pruning check: A* expands fewer nodes than Dijkstra on large grid
        self.assertLessEqual(a_res["visited_count"], d_res["visited_count"])
        # 5. Path length check
        self.assertEqual(len(d_res["path"]), 11)  # 10 hops = 11 nodes

    # -------------------------------------------------------------
    # 10. PATH RECONSTRUCTION INTEGRITY
    # -------------------------------------------------------------
    def test_path_reconstruction_integrity(self):
        """Verify that every edge in reconstructed path is an actual edge in the graph."""
        nodes = list(self.sample_graph.nodes.keys())
        for _ in range(5):
            u, v = random.sample(nodes, 2)
            for algo_func in [dijkstra, astar, floyd_warshall]:
                res = algo_func(self.sample_graph, u, v)
                if res["found"]:
                    path = res["path"]
                    self.assertEqual(path[0], u)
                    self.assertEqual(path[-1], v)
                    calc_cost = 0.0
                    for i in range(len(path) - 1):
                        self.assertIn(path[i + 1], self.sample_graph.adj[path[i]])
                        calc_cost += self.sample_graph.get_edge_weight(path[i], path[i + 1])
                    self.assertAlmostEqual(calc_cost, res["cost"], places=2)

    # -------------------------------------------------------------
    # 11. ROUTE COMPARISON INTEGRITY (ALL 3 AGREE)
    # -------------------------------------------------------------
    def test_compare_all_three_algorithms(self):
        pairs = [
            ("CYBER_TOWERS", "FINANCIAL_DISTRICT"),
            ("HCU_UNIVERSITY", "JUBILEE_HILLS"),
            ("GACHIBOWLI_STADIUM", "INORBIT_MALL")
        ]
        for src, tgt in pairs:
            payload = {"source": src, "target": tgt}
            response = self.client.post("/api/compare", data=json.dumps(payload), content_type="application/json")
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            cmp = data["comparison"]
            self.assertTrue(cmp["optimality_consistent"])
            d_cost = cmp["algorithms"]["dijkstra"]["cost_km"]
            a_cost = cmp["algorithms"]["astar"]["cost_km"]
            fw_cost = cmp["algorithms"]["floyd_warshall"]["cost_km"]
            self.assertAlmostEqual(d_cost, a_cost, places=2)
            self.assertAlmostEqual(d_cost, fw_cost, places=2)

    # -------------------------------------------------------------
    # 12. NO RESULTS ARE HARDCODED (RANDOMIZED GRAPH TEST)
    # -------------------------------------------------------------
    def test_no_results_hardcoded_random_weights(self):
        """Generate a random topology with arbitrary random weights and verify exact algorithmic resolution."""
        g = Graph(directed=False)
        for i in range(8):
            g.add_node(f"RND_{i}", f"Random {i}", 17.0 + i * 0.05, 78.0 + (i % 3) * 0.05)

        # Randomly connect with unique float weights
        random.seed(42)
        for i in range(8):
            for j in range(i + 1, 8):
                if random.random() < 0.4:
                    w = round(random.uniform(1.23, 19.87), 3)
                    g.add_edge(f"RND_{i}", f"RND_{j}", w)

        # Run Dijkstra, A*, and Floyd-Warshall
        d_res = dijkstra(g, "RND_0", "RND_7")
        a_res = astar(g, "RND_0", "RND_7")
        fw_res = floyd_warshall(g, "RND_0", "RND_7")

        if d_res["found"]:
            self.assertTrue(a_res["found"])
            self.assertTrue(fw_res["found"])
            self.assertAlmostEqual(d_res["cost"], a_res["cost"], places=2)
            self.assertAlmostEqual(d_res["cost"], fw_res["cost"], places=2)

if __name__ == "__main__":
    unittest.main()

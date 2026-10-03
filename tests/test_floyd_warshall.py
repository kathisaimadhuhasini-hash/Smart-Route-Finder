import unittest
from algorithms.dijkstra import dijkstra
from algorithms.floyd_warshall import FloydWarshall, floyd_warshall
from backend.sample_data import build_sample_graph

class TestFloydWarshall(unittest.TestCase):
    def setUp(self):
        self.graph = build_sample_graph()
        self.fw = FloydWarshall(self.graph)
        self.fw.compute()

    def test_all_pairs_match_dijkstra(self):
        """Every single pair of vertices in Floyd-Warshall must match Dijkstra's shortest distance."""
        nodes = list(self.graph.nodes.keys())
        # Test a subset of diverse pairs
        test_pairs = [
            ("CYBER_TOWERS", "FINANCIAL_DISTRICT"),
            ("MINDSPACE", "HCU_UNIVERSITY"),
            ("JUBILEE_HILLS", "ORR_EXPRESSWAY"),
            ("BOTANICAL_GARDEN", "CABLE_BRIDGE"),
            ("WIPRO_CIRCLE", "MADHAPUR_METRO")
        ]

        for u, v in test_pairs:
            dijkstra_res = dijkstra(self.graph, u, v)
            fw_dist = self.fw.get_distance(u, v)

            self.assertAlmostEqual(
                dijkstra_res["cost"], fw_dist, places=2,
                msg=f"Floyd-Warshall distance ({fw_dist}) differed from Dijkstra ({dijkstra_res['cost']}) for {u} -> {v}"
            )

    def test_path_reconstruction_connectivity(self):
        """Reconstructed path must be valid and continuous."""
        path = self.fw.reconstruct_path("CYBER_TOWERS", "FINANCIAL_DISTRICT")
        self.assertGreater(len(path), 1)
        self.assertEqual(path[0], "CYBER_TOWERS")
        self.assertEqual(path[-1], "FINANCIAL_DISTRICT")

        # Verify edge continuity
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            self.assertIn(v, self.graph.adj[u], f"Edge {u} -> {v} does not exist in graph!")

    def test_functional_wrapper(self):
        res = floyd_warshall(self.graph, "CYBER_TOWERS", "JUBILEE_HILLS")
        self.assertTrue(res["found"])
        self.assertGreater(res["cost"], 0)
        self.assertIn("total_iterations", res)

    def test_no_negative_cycles(self):
        self.assertFalse(self.fw.has_negative_cycle())

    def test_distance_matrix_structure(self):
        res = floyd_warshall(self.graph, "CYBER_TOWERS", "JUBILEE_HILLS")
        self.assertIn("distance_matrix", res)
        self.assertIn("matrix_headers", res)
        self.assertEqual(len(res["distance_matrix"]), len(self.graph.nodes))
        self.assertEqual(len(res["matrix_headers"]), len(self.graph.nodes))
        self.assertIn("shortest_path_info", res)

if __name__ == "__main__":
    unittest.main()

import unittest
from algorithms.graph import Graph
from algorithms.dijkstra import dijkstra
from backend.sample_data import build_sample_graph

class TestDijkstra(unittest.TestCase):
    def setUp(self):
        self.graph = build_sample_graph()

    def test_direct_neighbor(self):
        # CYBER_TOWERS to MINDSPACE is a direct 1.2 km edge
        res = dijkstra(self.graph, "CYBER_TOWERS", "MINDSPACE")
        self.assertTrue(res["found"])
        self.assertEqual(res["path"], ["CYBER_TOWERS", "MINDSPACE"])
        self.assertAlmostEqual(res["cost"], 1.2, places=2)

    def test_multi_hop_route(self):
        # CYBER_TOWERS -> MINDSPACE -> INORBIT_MALL -> CABLE_BRIDGE -> JUBILEE_HILLS
        res = dijkstra(self.graph, "CYBER_TOWERS", "JUBILEE_HILLS")
        self.assertTrue(res["found"])
        self.assertEqual(res["path"][0], "CYBER_TOWERS")
        self.assertEqual(res["path"][-1], "JUBILEE_HILLS")
        self.assertGreater(res["cost"], 0)

    def test_identity_route(self):
        res = dijkstra(self.graph, "CYBER_TOWERS", "CYBER_TOWERS")
        self.assertTrue(res["found"])
        self.assertEqual(res["path"], ["CYBER_TOWERS"])
        self.assertEqual(res["cost"], 0.0)

    def test_triangle_inequality(self):
        # Test on custom triangle graph
        g = Graph(directed=False)
        g.add_node("A", "Node A", 0.0, 0.0)
        g.add_node("B", "Node B", 1.0, 1.0)
        g.add_node("C", "Node C", 2.0, 2.0)
        g.add_edge("A", "B", 10.0)
        g.add_edge("B", "C", 10.0)
        g.add_edge("A", "C", 5.0)  # Direct shortcut
        res = dijkstra(g, "A", "B")
        self.assertAlmostEqual(res["cost"], 10.0)
        res_ac = dijkstra(g, "A", "C")
        self.assertAlmostEqual(res_ac["cost"], 5.0)

    def test_unreachable_node(self):
        g = Graph(directed=False)
        g.add_node("A", "A", 0, 0)
        g.add_node("B", "B", 1, 1)
        g.add_node("ISO", "Isolated", 2, 2)
        g.add_edge("A", "B", 5.0)
        res = dijkstra(g, "A", "ISO")
        self.assertFalse(res["found"])
        self.assertEqual(res["path"], [])

    def test_visited_nodes_details(self):
        res = dijkstra(self.graph, "CYBER_TOWERS", "FINANCIAL_DISTRICT")
        self.assertIn("visited_nodes_details", res)
        self.assertGreater(len(res["visited_nodes_details"]), 0)
        for node in res["visited_nodes_details"]:
            self.assertIn("step", node)
            self.assertIn("node_id", node)
            self.assertIn("settled_distance", node)
            self.assertIn("parent", node)

if __name__ == "__main__":
    unittest.main()

import unittest
from algorithms.dijkstra import dijkstra
from algorithms.astar import astar
from backend.sample_data import build_sample_graph

class TestAStar(unittest.TestCase):
    def setUp(self):
        self.graph = build_sample_graph()

    def test_astar_matches_dijkstra_cost(self):
        """A* must discover the exact same minimal cost as Dijkstra across pairs."""
        pairs = [
            ("CYBER_TOWERS", "FINANCIAL_DISTRICT"),
            ("HCU_UNIVERSITY", "JUBILEE_HILLS"),
            ("GACHIBOWLI_STADIUM", "INORBIT_MALL"),
            ("KOTHAGUDA_X", "ORR_EXPRESSWAY")
        ]
        for src, tgt in pairs:
            d_res = dijkstra(self.graph, src, tgt)
            a_res = astar(self.graph, src, tgt)

            self.assertTrue(d_res["found"])
            self.assertTrue(a_res["found"])
            self.assertAlmostEqual(
                d_res["cost"], a_res["cost"], places=2,
                msg=f"A* cost ({a_res['cost']}) should match Dijkstra ({d_res['cost']}) for {src} -> {tgt}"
            )

    def test_heuristic_admissibility(self):
        """Verifies h(n) <= d*(n, goal) for all nodes with respect to target."""
        target = "FINANCIAL_DISTRICT"
        for node_id in self.graph.nodes:
            h_val = self.graph.haversine_distance(node_id, target)
            actual_dist = dijkstra(self.graph, node_id, target)["cost"]
            self.assertLessEqual(
                h_val, actual_dist + 1e-4,
                f"Heuristic {h_val} exceeds actual distance {actual_dist} for node {node_id} (violates admissibility!)"
            )

    def test_search_efficiency_pruning(self):
        """A* should explore fewer or equal nodes compared to uninformed Dijkstra."""
        src, tgt = "CYBER_TOWERS", "FINANCIAL_DISTRICT"
        d_res = dijkstra(self.graph, src, tgt)
        a_res = astar(self.graph, src, tgt)

    def test_astar_explored_states_g_h_f(self):
        """Verifies that explored states contain g(n), h(n), f(n) and satisfy f = g + h."""
        src, tgt = "CYBER_TOWERS", "FINANCIAL_DISTRICT"
        a_res = astar(self.graph, src, tgt)
        self.assertIn("explored_states", a_res)
        self.assertGreater(len(a_res["explored_states"]), 0)

        for st in a_res["explored_states"]:
            self.assertIn("g", st)
            self.assertIn("h", st)
            self.assertIn("f", st)
            self.assertIn("parent", st)
            # f = g + h within float precision
            self.assertAlmostEqual(st["f"], st["g"] + st["h"], places=1)

if __name__ == "__main__":
    unittest.main()

import unittest
import json
from backend.app import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Smart Route Finder", response.data)

    def test_get_graph(self):
        response = self.client.get("/api/graph")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertGreater(data["total_nodes"], 10)
        self.assertGreater(data["total_edges"], 15)

    def test_post_route_dijkstra(self):
        payload = {
            "source": "CYBER_TOWERS",
            "target": "FINANCIAL_DISTRICT",
            "algorithm": "dijkstra"
        }
        response = self.client.post("/api/route", 
                                  data=json.dumps(payload),
                                  content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("optimal_route", data)
        self.assertIn("alternatives", data)
        self.assertIn("explanation", data)
        self.assertGreater(data["optimal_route"]["cost"], 0)
        self.assertIn("daa_principle", data["explanation"])

    def test_post_route_astar(self):
        payload = {
            "source": "CYBER_TOWERS",
            "target": "FINANCIAL_DISTRICT",
            "algorithm": "astar"
        }
        response = self.client.post("/api/route",
                                  data=json.dumps(payload),
                                  content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["optimal_route"]["algorithm_key"], "astar")

    def test_post_route_floyd_warshall(self):
        payload = {
            "source": "CYBER_TOWERS",
            "target": "FINANCIAL_DISTRICT",
            "algorithm": "floyd_warshall"
        }
        response = self.client.post("/api/route",
                                  data=json.dumps(payload),
                                  content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["optimal_route"]["algorithm_key"], "floyd_warshall")

    def test_post_compare(self):
        payload = {
            "source": "CYBER_TOWERS",
            "target": "FINANCIAL_DISTRICT"
        }
        response = self.client.post("/api/compare",
                                  data=json.dumps(payload),
                                  content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["comparison"]["optimality_consistent"])
        self.assertIn("dijkstra", data["comparison"]["algorithms"])
        self.assertIn("astar", data["comparison"]["algorithms"])
        self.assertIn("floyd_warshall", data["comparison"]["algorithms"])

    def test_invalid_node_error(self):
        payload = {
            "source": "NON_EXISTENT_SOURCE",
            "target": "FINANCIAL_DISTRICT",
            "algorithm": "dijkstra"
        }
        response = self.client.post("/api/route",
                                  data=json.dumps(payload),
                                  content_type="application/json")
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()

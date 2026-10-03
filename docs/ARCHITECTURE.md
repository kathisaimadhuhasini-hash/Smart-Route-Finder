# System Architecture & Technical Specification

## Project Overview

Smart Route Finder is structured into five distinct, decoupled layers:

```
smart route finder/
├── algorithms/                 # Core reusable algorithmic implementations
│   ├── __init__.py             # Algorithms package exports
│   ├── graph.py                # Graph data structure & geographic utilities
│   ├── dijkstra.py             # Dijkstra's shortest path algorithm
│   ├── astar.py                # A* search with Haversine heuristic
│   ├── floyd_warshall.py       # All-pairs dynamic programming & reconstruction
│   ├── alternative_routes.py   # Multi-path edge-penalty & bypass routing
│   └── explainer.py            # DAA optimality justification engine
├── backend/                    # Flask REST API & persistence
│   ├── app.py                  # Flask application & routing endpoints
│   ├── database.py             # SQLite persistence & query logger
│   └── sample_data.py          # Weighted realistic road network graph
├── frontend/                   # Interactive Single Page Application
│   ├── templates/
│   │   └── index.html          # Semantic HTML5 UI layout
│   └── static/
│       ├── css/
│       │   └── style.css       # Responsive dark-theme styling
│       └── js/
│           └── app.js          # Leaflet map rendering & REST client
├── tests/                      # Comprehensive unit & integration tests
│   ├── test_dijkstra.py        # Dijkstra correctness & edge cases
│   ├── test_astar.py           # A* heuristic admissibility & pruning
│   ├── test_floyd_warshall.py  # Floyd-Warshall DP all-pairs vs Dijkstra
│   └── test_api.py             # Flask endpoint integration tests
├── docs/                       # Project documentation
│   ├── DAA_PROJECT_REPORT.md   # Academic report, complexity analysis, proofs
│   └── ARCHITECTURE.md         # This architectural specification
├── requirements.txt            # Python dependencies
└── run.py                      # Main entry point to launch the web server
```

---

## Component Diagram & Data Flow

```
+--------------------------------------------------------------------+
|                         CLIENT BROWSER                             |
|  - Leaflet Map (Visualizes Nodes, Edges, Optimal & Alt Polylines)  |
|  - Controls (Origin, Destination, Algorithm Selector, Presets)    |
|  - Analytics (Metrics Cards, DAA Explainer, Head-to-Head Modal)   |
+---------------------------------+----------------------------------+
                                  |
                   HTTP GET / POST (JSON API)
                                  |
                                  v
+---------------------------------+----------------------------------+
|                         FLASK BACKEND                              |
|  Endpoints:                                                        |
|  - GET  /api/graph              -> Returns vertices, edges, bounds|
|  - POST /api/route              -> Computes route, alts, explainer |
|  - POST /api/compare            -> Head-to-head 3-algo benchmark   |
|  - GET  /api/history            -> Audit trail from SQLite         |
+--------+--------------------------------------------------+--------+
         |                                                  |
         v                                                  v
+---------------------+                            +-----------------+
|  ALGORITHMS ENGINE  |                            | SQLITE DATABASE |
|  - Dijkstra         |                            | - nodes         |
|  - A* Search        |                            | - edges         |
|  - Floyd-Warshall   |                            | - route_queries |
|  - Alternative Gen  |                            +-----------------+
|  - DAA Explainer    |
+---------------------+
```

---

## API Endpoints Specification

### 1. `GET /api/graph`
Returns all graph vertices and edges for map initialization.
- **Response:**
  ```json
  {
    "success": true,
    "nodes": [{"id": "CYBER_TOWERS", "name": "Cyber Towers", "lat": 17.4504, "lon": 78.3809, ...}],
    "edges": [{"from": "CYBER_TOWERS", "to": "MINDSPACE", "weight": 1.2, "road_name": "...", ...}],
    "total_nodes": 15,
    "total_edges": 21,
    "bounds": { "min_lat": 17.412, "max_lat": 17.461, ... }
  }
  ```

### 2. `POST /api/route`
Computes the optimal path using the chosen algorithm, derives secondary alternative routes, and constructs the DAA explanation.
- **Request:**
  ```json
  {
    "source": "CYBER_TOWERS",
    "target": "FINANCIAL_DISTRICT",
    "algorithm": "astar"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "optimal_route": {
      "algorithm": "A* Search Algorithm",
      "path": ["CYBER_TOWERS", "MINDSPACE", "RAIDURG_METRO", "BIODIVERSITY_JN", "WIPRO_CIRCLE", "FINANCIAL_DISTRICT"],
      "cost": 7.1,
      "total_time_min": 8.7,
      "visited_count": 6,
      "execution_time_ms": 0.09,
      "path_details": [...]
    },
    "alternatives": [
      {
        "id": "alt_1",
        "label": "Alternative 1 (via Botanical Garden)",
        "cost": 7.9,
        "delta_km": 0.8,
        "delta_pct": 11.3,
        "reason_suboptimal": "Adds +0.8 km (+11.3%) due to routing through Botanical Garden."
      }
    ],
    "explanation": {
      "daa_principle": "Heuristic Guided Search & Branch-and-Bound Pruning",
      "proof_summary": "A* Search guarantees optimality using an admissible heuristic...",
      "key_takeaway": "The selected route achieves the minimum possible travel cost of 7.1 km..."
    }
  }
  ```

### 3. `POST /api/compare`
Executes Dijkstra, A*, and Floyd-Warshall on the identical source and destination, measuring runtime, nodes expanded, heap operations, and verifying consistent optimality.
- **Request:**
  ```json
  {
    "source": "CYBER_TOWERS",
    "target": "FINANCIAL_DISTRICT"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "comparison": {
      "optimality_consistent": true,
      "optimal_cost_km": 7.1,
      "algorithms": {
        "dijkstra": { "cost_km": 7.1, "execution_time_ms": 0.08, "nodes_visited": 10, ... },
        "astar": { "cost_km": 7.1, "execution_time_ms": 0.09, "nodes_visited": 6, ... },
        "floyd_warshall": { "cost_km": 7.1, "execution_time_ms": 2.45, "lookup_time_ms": 0.01, ... }
      },
      "efficiency_analysis": "A* searched 6 nodes compared to Dijkstra's 10 nodes (40% node pruning)..."
    }
  }
  ```

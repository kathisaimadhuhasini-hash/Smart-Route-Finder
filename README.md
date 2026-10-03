# 🚀 Smart Route Finder

> **Design and Analysis of Algorithms (DAA) — Multi-Path Route Optimization & Explainability Engine**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/framework-Flask%203.x-green.svg)](https://flask.palletsprojects.com/)
[![Leaflet.js](https://img.shields.io/badge/map-Leaflet.js-brightgreen.svg)](https://leafletjs.com/)
[![Tests](https://img.shields.io/badge/tests-41%20passed-success.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-informational.svg)](LICENSE)

---

## 📌 Table of Contents

- [1. Problem Statement](#1-problem-statement)
- [2. Problem Understanding & Modeling](#2-problem-understanding--modeling)
- [3. Input and Output](#3-input-and-output)
- [4. Algorithms Used](#4-algorithms-used)
- [5. Why Each Algorithm is Used](#5-why-each-algorithm-is-used)
- [6. Pseudocode](#6-pseudocode)
- [7. Time and Space Complexity Analysis](#7-time-and-space-complexity-analysis)
- [8. System Architecture](#8-system-architecture)
- [9. Features](#9-features)
- [10. Installation & Prerequisites](#10-installation--prerequisites)
- [11. How to Run](#11-how-to-run)
- [12. Testing & Verification](#12-testing--verification)
- [13. Sample Experimental Results](#13-sample-experimental-results)
- [14. Team Members](#14-team-members)
- [15. AI Tools Used](#15-ai-tools-used)

---

## 1. Problem Statement

Build an intelligent route engine that:
1. Compares multiple paths between locations in a weighted geographic network.
2. Calculates the strictly minimal travel cost (distance and time).
3. Discovers and visualizes competitive alternative routes (detours and bypasses).
4. Explains mathematically and practically **why** the selected route is optimal compared to alternatives.
5. Implements and benchmarks three foundational DAA shortest-path algorithms:
   - **Dijkstra's Algorithm** (Greedy)
   - **A\* Search Algorithm** (Informed Heuristic)
   - **Floyd-Warshall Algorithm** (Dynamic Programming)
6. Demonstrates real algorithmic computation on live graph topologies with zero hardcoded or fake outputs.

---

## 2. Problem Understanding & Modeling

In modern transit engines (such as Google Maps, Mapbox, or ride-sharing routing engines), navigation is modeled as a weighted graph:
$$G = (V, E, W)$$
- **Vertices ($V$):** Intersections, landmarks, and transit junctions. Each vertex $v \in V$ is grounded in physical space with GPS coordinates $(\text{latitude}_v, \text{longitude}_v)$.
- **Edges ($E$):** Physical road segments connecting adjacent vertices.
- **Edge Weight Function ($W: E \to \mathbb{R}^+$):** Non-negative road distance in kilometers and estimated transit time in minutes:
  $$W(u, v) \ge 0 \quad \forall (u, v) \in E$$
- **Metric Space Property:** In real road networks, geodesic straight-line distance satisfies the **Triangle Inequality**:
  $$d_{\text{straight}}(u, w) \le d_{\text{straight}}(u, v) + d_{\text{straight}}(v, w)$$
  Because physical roads twist and turn, actual road distance is always bounded below by spherical straight-line distance:
  $$h(u, v) \le W(u, v)$$
  This property enables the formulation of **provably admissible heuristics** for goal-directed routing.

---

## 3. Input and Output

### Input Format
- **Source Vertex ($s \in V$):** Origin junction ID (selected via UI dropdown or clicking on the interactive map).
- **Target Vertex ($t \in V$):** Destination junction ID.
- **Algorithm Key:** Choice of search algorithm (`dijkstra`, `astar`, `floyd_warshall`).
- **Graph Topology:** Vertices $V$ with GPS coordinates and weighted adjacency lists $E$.

### Output Format
- **Optimal Route:** Reconstructed sequence of vertex IDs $[v_0, v_1, \dots, v_k]$ from $s$ to $t$.
- **Shortest Travel Cost:** Accumulated minimal distance in kilometers (e.g. `7.1 km`).
- **Estimated Travel Time:** Turn-by-turn road segment times (in minutes).
- **Nodes Explored / Visited Count:** Quantitative metric of how many states the algorithm explored.
- **Algorithm Execution Time:** Wall-clock computation duration in milliseconds ($\text{ms}$).
- **Alternative Routes:** Secondary and tertiary viable paths with $+ \Delta\text{ km}$ detour overhead, $+ \Delta\%$ time overhead, and diversion reasons.
- **Optimality Explanation:** Rigorous proof stating the governing DAA principle (Greedy Choice Property, Admissible Heuristic Consistency, or Dynamic Programming Substructure) and comparing why alternatives were rejected.
- **Algorithm-Specific Internals:**
  - *For A\*:* Tabular states breakdown showing $g(n)$, $h(n)$, $f(n) = g(n) + h(n)$, and parent pointers.
  - *For Dijkstra:* Sequence of settled vertices extracted from the min-heap with permanent distances $d[u]$.
  - *For Floyd-Warshall:* The $|V| \times |V|$ all-pairs shortest distance matrix with highlighted source row and target cell.

---

## 4. Algorithms Used

| Algorithm | Paradigm | Directionality | Heuristic Guided? | Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Dijkstra's Algorithm** | Greedy Strategy | Uninformed (Radial) | No | Single-Source One-to-All |
| **A\* Search Algorithm** | Informed Heuristic Search | Directional (Goal-Directed) | Yes (Haversine Spherical Distance) | Single-Pair Point-to-Point |
| **Floyd-Warshall** | Dynamic Programming | Exhaustive Intermediate Sets | No | All-Pairs Any-to-Any |

---

## 5. Why Each Algorithm is Used

### 1. Dijkstra's Algorithm
- **Role:** The gold standard for exact single-source shortest path problems on graphs with non-negative edge weights ($w \ge 0$).
- **Why Used:** Guarantees absolute global optimality via the greedy choice property. Settling vertices in order of increasing distance ensures every popped vertex has achieved its final minimum distance without backtracking.

### 2. A* Search Algorithm
- **Role:** Industrial turn-by-turn navigation engine.
- **Why Used:** Dijkstra searches blindly in all directions like an expanding circle. A* uses an evaluation function $f(n) = g(n) + h(n)$ to bias exploration in an elliptical cone toward the destination. Using the **Haversine formula** as $h(n)$ provides an **admissible** and **monotone (consistent)** lower bound that cuts node expansions by 30% to 65% while guaranteeing the identical optimal distance.

### 3. Floyd-Warshall Algorithm
- **Role:** All-Pairs Shortest Path (APSP) precomputation engine.
- **Why Used:** In central traffic management systems, transit operators need to know distances between *all* pairs of junctions simultaneously. Floyd-Warshall computes the complete $|V| \times |V|$ distance matrix in $\Theta(V^3)$. Once computed, any routing query between any two junctions is resolved in $O(1)$ time.

---

## 6. Pseudocode

### 6.1 Dijkstra's Algorithm (Min-Heap Priority Queue)
```text
Algorithm Dijkstra(Graph G, Vertex source, Vertex target):
    dist[v] ← ∞ for all v ∈ V
    dist[source] ← 0
    pred[v] ← null for all v ∈ V
    PQ ← PriorityQueue containing (0, source)
    visited ← empty set

    while PQ is not empty:
        (current_dist, u) ← PQ.extract_min()
        if current_dist > dist[u]: continue
        visited.add(u)
        
        if u == target:
            break // Early termination when goal is settled

        for each neighbor v of u with edge weight w:
            if dist[u] + w < dist[v]:
                dist[v] ← dist[u] + w
                pred[v] ← u
                PQ.insert((dist[v], v))

    return ReconstructPath(pred, target), dist[target]
```

### 6.2 A* Search Algorithm
```text
Algorithm AStar(Graph G, Vertex source, Vertex target):
    g_score[v] ← ∞ for all v ∈ V
    g_score[source] ← 0
    f_score[v] ← ∞ for all v ∈ V
    f_score[source] ← Haversine(source, target)
    
    OpenSet ← PriorityQueue containing (f_score[source], source)
    ClosedSet ← empty set
    pred[v] ← null for all v ∈ V

    while OpenSet is not empty:
        (current_f, u) ← OpenSet.extract_min()
        if u ∈ ClosedSet: continue
        ClosedSet.add(u)

        if u == target:
            break // Optimal goal achieved

        for each neighbor v of u with edge weight w:
            if v ∈ ClosedSet: continue
            tentative_g ← g_score[u] + w
            
            if tentative_g < g_score[v]:
                pred[v] ← u
                g_score[v] ← tentative_g
                f_score[v] ← g_score[v] + Haversine(v, target)
                OpenSet.insert((f_score[v], v))

    return ReconstructPath(pred, target), g_score[target]
```

### 6.3 Floyd-Warshall Algorithm
```text
Algorithm FloydWarshall(Graph G):
    Let D be a |V| × |V| matrix initialized to ∞
    Let Next be a |V| × |V| matrix initialized to null

    for each vertex v ∈ V:
        D[v][v] ← 0

    for each edge (u, v) ∈ E with weight w:
        D[u][v] ← w
        Next[u][v] ← v

    // Dynamic Programming: Triple nested loop over intermediate vertices k
    for k from 1 to |V|:
        for i from 1 to |V|:
            for j from 1 to |V|:
                if D[i][k] + D[k][j] < D[i][j]:
                    D[i][j] ← D[i][k] + D[k][j]
                    Next[i][j] ← Next[i][k]

    return D, Next
```

---

## 7. Time and Space Complexity Analysis

| Algorithm | Best-Case Time | Average-Case Time | Worst-Case Time | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Dijkstra (Binary Min-Heap)** | $O((V + E) \log V)$ | $O((V + E) \log V)$ | $O((V + E) \log V)$ | $\Theta(V)$ |
| **A\* Search** | $O(E)$ | $O(E)$ *(with tight heuristic)* | $O((V + E) \log V)$ | $\Theta(V)$ |
| **Floyd-Warshall** | $\Theta(V^3)$ | $\Theta(V^3)$ | $\Theta(V^3)$ | $\Theta(V^2)$ |

### Mathematical Explanations:
1. **Dijkstra:** Extracting minimum vertices $|V|$ times costs $|V| \log |V|$. Relaxing $|E|$ edges costs $|E| \log |V|$. Total time is $O((V + E) \log V)$.
2. **A\*:** In the ideal case where the heuristic is exact, A* explores only the vertices along the optimal path ($O(E)$). If $h(n) = 0$, it degenerates gracefully to Dijkstra's complexity.
3. **Floyd-Warshall:** Exactly $|V|^3$ operations execute due to the 3 nested loops over vertices $k, i, j$. Space complexity is $\Theta(V^2)$ to store the $|V| \times |V|$ distance and next-hop predecessor matrices.

---

## 8. System Architecture

```
+-------------------------------------------------------------------------------+
|                             CLIENT / FRONTEND                                 |
|  - HTML5 / CSS3 (Responsive Dark Aesthetic)                                   |
|  - Leaflet.js Interactive Geographic Map Layer                                |
|  - Route Configuration (Source / Destination / Algorithm Selection / Presets)|
|  - Real-Time Results (Metric Cards, DAA Explainer, Turn-by-Turn Segments)     |
|  - Algorithm Visualizers (A* State Table, Dijkstra Settled Nodes, FW Matrix)  |
|  - Head-to-Head Comparison Benchmark Modal                                    |
+---------------------------------------+---------------------------------------+
                                        |
                            HTTP REST API (JSON)
                                        |
                                        v
+---------------------------------------+---------------------------------------+
|                              FLASK BACKEND                                    |
|  - GET  /api/graph   : Returns vertices, GPS coordinates, edges, bounds       |
|  - POST /api/route   : Computes shortest route, alternatives, DAA explanation |
|  - POST /api/compare : Executes 3 algorithms concurrently, returns benchmarks |
|  - GET  /api/history : Audit trail of past queries from SQLite3               |
+-------------------+---------------------------------------+-------------------+
                    |                                       |
                    v                                       v
+-------------------+-------------------+   +---------------+-------------------+
|            ALGORITHMS ENGINE          |   |          SQLITE3 DATABASE         |
|  - Graph Class (Geo-Math, Haversine)  |   |  - Table: nodes                   |
|  - Dijkstra Module (Min-Heap)         |   |  - Table: edges                   |
|  - A* Module (Admissible Heuristic)   |   |  - Table: route_queries           |
|  - Floyd-Warshall Module (DP Matrix)  |   +-----------------------------------+
|  - Alternative Route Generator        |
|  - DAA Optimality Explainer Engine    |
+---------------------------------------+
```

---

## 9. Features

- ✅ **No Hardcoded or Fake Data:** All routes, costs, and exploration metrics are calculated live from real algorithm executions.
- ✅ **Real-World Geographic Coordinate Network:** 15 landmark junctions across the Cyberabad IT Corridor and Financial District.
- ✅ **Dynamic Multi-Route Generation:** Calculates secondary and tertiary alternative paths with quantified detours.
- ✅ **DAA Optimality Proof Engine:** Explains why the selected route minimizes physical travel distance and transit time.
- ✅ **A\* Detailed Search State Inspector:** Visibly displays $g(n)$, $h(n)$, $f(n)$, and parent pointers in exploration sequence.
- ✅ **Dijkstra Settlement Order Inspector:** Visibly displays min-heap extraction order and settled costs $d[u]$.
- ✅ **Interactive Floyd-Warshall Distance Matrix:** Visualizes the complete all-pairs distance table with active source row and destination cell highlighted.
- ✅ **Head-to-Head Benchmark Modal:** Side-by-side comparison of execution times ($\text{ms}$), nodes expanded, operations, and theoretical complexities.
- ✅ **Edge Cases Handled:** Identity queries ($S = T$), unreachable destinations, equal-cost ties, and disconnected graphs.

---

## 10. Installation & Prerequisites

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed.
- Pip package manager.

### Clone the Repository
```bash
git clone https://github.com/your-username/smart-route-finder.git
cd smart-route-finder
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 11. How to Run

Launch the application using the entry point:
```bash
python run.py
```

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 12. Testing & Verification

The project includes an automated test suite comprising **41 unit and integration tests** testing all edge cases, graph topologies, and algorithmic proofs.

### Run All Tests:
```bash
python -m unittest discover tests
```

### Verbose Test Output:
```bash
python -m unittest -v tests/test_engineer_suite.py
```

### Verified Test Cases:
- **Normal Routes:** Optimal path discovery across transit pairs.
- **Multiple Routes & Alternatives:** Validates edge-penalty routing and path diversity.
- **Source = Destination ($S = T$):** Validates zero-cost identity routing.
- **Unreachable Destination:** Validates disconnected graph handling (returns `found: False`, `cost: None`, HTTP 404).
- **Invalid Locations:** Validates parameter error handling (HTTP 400).
- **Equal-Cost Routes:** Validates tie-breaking and parallel corridor detection.
- **Different Edge Weights:** Micro-decimal distances ($0.042\text{ km}$) and large highway distances.
- **Small Graph Topologies:** 3-node triangles, 4-node chains, and diamond shortcuts.
- **Larger Graph Topologies:** 36-node grid mesh with Manhattan distance validation.
- **Admissibility of Heuristic:** Confirms $h(n) \le d^*(n, \text{goal})$ for all pairs.
- **Floyd-Warshall Verification:** Confirms all-pairs distances match Dijkstra across the network.
- **No Hardcoded Results:** Random graph topology verification with randomized float weights.

---

## 13. Sample Experimental Results

### Test Query: Cyber Towers $\to$ Financial District Hub

| Metric | Dijkstra's Algorithm | A* Search Algorithm | Floyd-Warshall |
| :--- | :--- | :--- | :--- |
| **Path Discovered** | `CYBER_TOWERS` $\to$ `MINDSPACE` $\to$ `RAIDURG_METRO` $\to$ `BIODIVERSITY_JN` $\to$ `WIPRO_CIRCLE` $\to$ `FINANCIAL_DISTRICT` | `CYBER_TOWERS` $\to$ `MINDSPACE` $\to$ `RAIDURG_METRO` $\to$ `BIODIVERSITY_JN` $\to$ `WIPRO_CIRCLE` $\to$ `FINANCIAL_DISTRICT` | `CYBER_TOWERS` $\to$ `MINDSPACE` $\to$ `RAIDURG_METRO` $\to$ `BIODIVERSITY_JN` $\to$ `WIPRO_CIRCLE` $\to$ `FINANCIAL_DISTRICT` |
| **Optimal Path Cost** | **7.1 km** | **7.1 km** | **7.1 km** |
| **Nodes Explored** | 10 nodes | **6 nodes (40% pruned)** | 15 nodes ($V^3 = 3375$ iter) |
| **Execution Time** | 0.08 ms | 0.09 ms | 2.45 ms (Lookup: 0.01 ms) |
| **Optimality Verification** | ✅ Verified | ✅ Verified | ✅ Verified |

### Alternative Routes Generated:
- **Alternative 1 (via Botanical Garden Bypass):** 7.9 km (+0.8 km / +11.3% detour)
- **Alternative 2 (via Outer Ring Road Tollway):** 9.8 km (+2.7 km / +38.0% detour)

---

## 14. Team Members

- **Chetala Venkata Teja** — Lead Algorithm Architect & Full-Stack Developer

---

## 15. AI Tools Used

- **Google Antigravity & Gemini 3.8 Flash (High):** Utilized as an AI pair-programming assistant for:
  - Formulating geodesic Haversine heuristic proofs and admissibility assertions.
  - Designing the test harness (41 test cases covering edge cases, random topologies, and grid meshes).
  - Assisting in clean architectural decoupling (`algorithms/`, `backend/`, `frontend/`, `tests/`, `docs/`).
  - Verifying the absence of hardcoded outputs and validating DAA complexity bounds.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

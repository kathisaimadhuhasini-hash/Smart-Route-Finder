# Smart Route Finder — DAA Project Report & Technical Documentation

**Hackathon Track:** Design & Analysis of Algorithms (DAA)  
**Project Name:** Smart Route Finder  
**Core Algorithms:** Dijkstra's Algorithm, A* Heuristic Search, Floyd-Warshall Dynamic Programming  
**Tech Stack:** Python 3, Flask, Leaflet.js, HTML5 / CSS3 / JavaScript (ES6+), SQLite3  

---

## 1. Executive Summary & Problem Formulation

In modern intelligent transportation systems (ITS) and navigation engines (e.g., Google Maps, Uber Routing), selecting a path involves more than just finding an arbitrary connection between two points. Commuters and transport operators require:
1. **Accurate Shortest Travel Cost:** Finding the strictly minimal distance/time corridor.
2. **Alternative Route Exploration:** Evaluating viable secondary bypasses or arterial detours.
3. **Algorithmic Justification (Explainability):** Understanding *why* a particular route was chosen as optimal, what compromises are made by taking alternatives, and which algorithmic strategy is most efficient for a given network workload.

### Problem Statement
Given a weighted road network represented as a graph $G = (V, E, W)$, where:
- $V$ is the set of $|V|$ junctions/landmarks with geographic coordinates $(\text{lat}_v, \text{lon}_v)$,
- $E$ is the set of $|E|$ bidirectional road segments,
- $W: E \to \mathbb{R}^+$ assigns non-negative edge weights (distances in kilometers and transit times in minutes),

The objective is to:
1. Compute the exact shortest path $P^* = (s = v_0, v_1, \dots, v_k = t)$ minimizing $\sum_{i=0}^{k-1} W(v_i, v_{i+1})$.
2. Extract competitive alternative paths $P_1, P_2$ using edge-penalty and corridor-deviation heuristics.
3. Prove mathematical optimality and provide a DAA-grade breakdown of the computational trade-offs between Dijkstra, A*, and Floyd-Warshall.

---

## 2. Algorithmic Formulations & Complexity Analysis

### 2.1 Dijkstra's Algorithm (Greedy Single-Source Shortest Path)

#### Theoretical Foundation
Dijkstra's algorithm operates on the **Greedy Choice Property** and **Optimal Substructure**. Because all edge weights in the road network are non-negative ($w(u, v) \ge 0$), the algorithm maintains a partition of vertices into settled ($S$) and unsettled ($V \setminus S$). At each step, extracting the vertex $u \in V \setminus S$ with minimal tentative distance $d[u]$ guarantees that $d[u] = d^*(s, u)$.

#### Pseudocode
```text
Algorithm Dijkstra(G, s, t):
    Initialize dist[v] = ∞ for all v in V, dist[s] = 0
    Initialize pred[v] = null for all v in V
    Initialize MinHeap Q with (0, s)

    while Q is not empty:
        (d, u) = Extract-Min(Q)
        if d > dist[u]: continue
        if u == t: break  // Early termination
        
        for each neighbor v of u with edge weight w:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                Insert(Q, (dist[v], v))
                
    return ReconstructPath(pred, t), dist[t]
```

#### Complexity Analysis
- **Time Complexity:**
  - With binary min-heap: $O((|V| + |E|) \log |V|)$.
  - Each vertex is extracted at most once: $|V| \times O(\log |V|)$.
  - Each edge is relaxed at most once: $|E| \times O(\log |V|)$.
- **Space Complexity:** $\Theta(|V|)$ to store the distance array, predecessor pointers, and heap.
- **Characteristics:** Uninformed search; explores radially in concentric circles away from source without knowing the spatial direction of target.

---

### 2.2 A* Search Algorithm (Informed Heuristic Search)

#### Theoretical Foundation
A* enhances Dijkstra by incorporating domain knowledge through a heuristic evaluation function:
$$f(n) = g(n) + h(n)$$
- $g(n)$: The exact cost from the starting vertex $s$ to node $n$.
- $h(n)$: The estimated lower-bound cost from $n$ to the target destination $t$.

#### Heuristic Choice: Haversine Geodesic Distance
For geographic coordinate systems, straight-line spherical distance is computed using the **Haversine Formula**:
$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)$$
$$c = 2 \cdot \arctan2(\sqrt{a}, \sqrt{1-a})$$
$$h(n) = R \cdot c \quad (\text{where } R = 6371\text{ km})$$

#### Proof of Admissibility & Consistency
1. **Admissibility ($h(n) \le d^*(n, t)$):** In any Euclidean/Riemannian metric space, the straight-line geodesic distance is the shortest possible path between two points (the metric lower bound). Because physical roads have twists, elevation changes, and turns, road distance $w(u, v) \ge \text{haversine}(u, v)$. Hence, $h(n)$ never overestimates the true remaining distance.
2. **Consistency / Monotonicity ($h(u) \le c(u, v) + h(v)$):** By the triangle inequality on the sphere:
   $$\text{dist}(u, t) \le \text{dist}(u, v) + \text{dist}(v, t)$$
   Since $c(u, v) \ge \text{dist}(u, v)$, it follows that $h(u) \le c(u, v) + h(v)$.
3. **Optimality Guarantee:** Because $h(n)$ is consistent and admissible, the first time target $t$ is extracted from the open set, its path is guaranteed to be optimal, and no closed nodes need re-opening.

#### Complexity Analysis
- **Time Complexity:** $O(|E|)$ best/average case when heuristic strongly focuses toward target; $O((|V| + |E|) \log |V|)$ worst case (when $h(n) = 0$, degenerating to Dijkstra).
- **Space Complexity:** $\Theta(|V|)$ for open and closed sets.
- **Search Pruning:** Eliminates expansion of nodes lying in the opposite direction of the destination, reducing explored vertices by 30% to 65% on road networks.

---

### 2.3 Floyd-Warshall Algorithm (All-Pairs Dynamic Programming)

#### Theoretical Foundation
The Floyd-Warshall algorithm calculates shortest distances between **all pairs** of vertices $(i, j) \in V \times V$ using the Dynamic Programming principle of optimality.

Let $D^{(k)}[i][j]$ represent the shortest distance from vertex $i$ to vertex $j$ using only intermediate vertices from the set $\{1, 2, \dots, k\}$.

#### Recurrence Relation
$$D^{(k)}[i][j] = \min\left( D^{(k-1)}[i][j], \; D^{(k-1)}[i][k] + D^{(k-1)}[k][j] \right)$$

- **Base Case ($k = 0$):**
  $$D^{(0)}[i][j] = \begin{cases} 0 & \text{if } i = j \\ w(i, j) & \text{if } (i, j) \in E \\ \infty & \text{otherwise} \end{cases}$$
- **Path Reconstruction:**
  Maintains a next-hop matrix $\text{Next}[i][j]$:
  $$\text{Next}[i][j] \leftarrow \text{Next}[i][k] \quad \text{whenever } D^{(k-1)}[i][k] + D^{(k-1)}[k][j] < D^{(k-1)}[i][j]$$

#### Complexity Analysis
- **Time Complexity:** Exactly $\Theta(|V|^3)$ due to three nested loops of size $|V|$.
- **Space Complexity:** $\Theta(|V|^2)$ for the distance matrix $D$ and next-hop matrix $\text{Next}$.
- **Trade-off:** High initial precomputation cost, but once computed, any pair's shortest distance query is answered in $O(1)$ time and its path reconstructed in $O(|V|)$ time.

---

## 3. Comparison Matrix of the Three Algorithms

| Dimension | Dijkstra's Algorithm | A* Search Algorithm | Floyd-Warshall Algorithm |
| :--- | :--- | :--- | :--- |
| **Algorithmic Paradigm** | Greedy Strategy | Informed Heuristic Search | Dynamic Programming |
| **Query Capability** | Single-Source One-to-All | Single-Pair Point-to-Point | All-Pairs Any-to-Any |
| **Time Complexity** | $O((V + E) \log V)$ | $O(E)$ avg, $O((V+E)\log V)$ worst | $\Theta(V^3)$ |
| **Space Complexity** | $O(V)$ | $O(V)$ | $\Theta(V^2)$ |
| **Optimality Guarantee** | Globally optimal ($w \ge 0$) | Globally optimal ($h$ admissible) | Globally optimal (no negative cycles) |
| **Search Space Traversal** | Concentric radial expansion | Directional elliptical cone toward target | Full graph matrix evaluation |
| **Best Practical Use Case** | Transit routing from 1 hub to all stops | Turn-by-turn on-demand GPS routing | Dense transit networks, distance lookup tables |

---

## 4. Alternative Routes Engine & Optimality Explainer

### 4.1 Finding Diverse Alternative Routes
To present commuters with alternatives, the engine implements:
1. **Edge-Penalty Routing:** For optimal path $P_0 = (e_1, e_2, \dots, e_k)$, edge weights along $P_0$ are temporarily penalized by factor $\alpha = 1.6$. Re-running the shortest path on $G'$ surfaces the best parallel corridor.
2. **Key-Edge Bypass Routing:** Temporarily bypassing the primary arterial segment forces routing through an alternative peripheral corridor (e.g., Ring Road or University bypass).
3. **Metrics Computed:** Real distance on unpenalized graph, extra distance ($\Delta \text{km}$), percentage detour ($+\Delta\%$), and identification of the diverged landmark.

### 4.2 Optimality Explainer Engine
The system generates a human-readable and mathematically grounded proof:
- Identifies the DAA governing principle (Greedy Choice, Admissible Heuristic, Bellman Substructure).
- Validates the Triangle Inequality lower bound.
- Compares each alternative:
  $$\Delta = \text{Cost}(P_{\text{alt}}) - \text{Cost}(P^*)$$
- Explains why the selected route saves travel time and fuel cost compared to the alternatives.

---

## 5. Experimental Results (Sample Benchmark)

Query: **Cyber Towers** $\to$ **Financial District Hub**

| Algorithm | Status | Path Discovered | Path Cost | Visited Nodes | Runtime |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Dijkstra** | Optimal | `CYBER_TOWERS` $\to$ `MINDSPACE` $\to$ `RAIDURG_METRO` $\to$ `BIODIVERSITY_JN` $\to$ `WIPRO_CIRCLE` $\to$ `FINANCIAL_DISTRICT` | **7.1 km** | 10 nodes | 0.08 ms |
| **A* Search** | Optimal | `CYBER_TOWERS` $\to$ `MINDSPACE` $\to$ `RAIDURG_METRO` $\to$ `BIODIVERSITY_JN` $\to$ `WIPRO_CIRCLE` $\to$ `FINANCIAL_DISTRICT` | **7.1 km** | **6 nodes (40% pruned)** | 0.09 ms |
| **Floyd-Warshall** | Optimal | `CYBER_TOWERS` $\to$ `MINDSPACE` $\to$ `RAIDURG_METRO` $\to$ `BIODIVERSITY_JN` $\to$ `WIPRO_CIRCLE` $\to$ `FINANCIAL_DISTRICT` | **7.1 km** | 15 nodes ($V^3=3375$ iter) | 2.45 ms (Lookup: 0.01 ms) |

**Alternative Routes:**
- *Alternative 1 (via Botanical Garden Bypass):* 7.9 km (+0.8 km / +11.3%)
- *Alternative 2 (via Outer Ring Road Tollway):* 9.8 km (+2.7 km / +38.0%)

**Optimality Consistency:** All 3 algorithms converged on the exact same distance of **7.1 km**.

---

## 6. How to Run & Verify

1. **Start the Web Application:**
   ```bash
   python run.py
   ```
2. **Access the User Interface:**
   Open browser at `http://127.0.0.1:5000`
3. **Execute Automated Test Suite:**
   ```bash
   python -m unittest discover tests
   ```
   *(All 41 tests pass verifying Dijkstra, A*, Floyd-Warshall, alternative routes, graph edge cases, and API endpoints).*

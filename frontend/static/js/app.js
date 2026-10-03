/**
 * Smart Route Finder - Frontend Application
 * Interacts with Flask API and renders network on Leaflet Map
 */

// Global State
let map;
let graphData = { nodes: {}, edges: [], bounds: null };
let nodeMarkers = {};
let baseEdgeLayers = [];
let routeLayers = {
  optimal: null,
  alt_1: null,
  alt_2: null
};
let currentRouteResult = null;

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  loadGraphData();
  bindEventListeners();
});

/**
 * Initializes Leaflet Map with free public OpenStreetMap tiles.
 * Completely free, no API key, token, or account required.
 */
function initMap() {
  // Default center at Cyberabad IT Corridor (17.44, 78.37)
  map = L.map("map", {
    zoomControl: true,
    attributionControl: true
  }).setView([17.44, 78.37], 13);

  // Free public OpenStreetMap tile layer (no API key required)
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);
}

/**
 * Loads graph network from Flask API and renders nodes and edges.
 */
async function loadGraphData() {
  try {
    const res = await fetch("/api/graph");
    const data = await res.json();

    if (!data.success) {
      console.error("Failed to load graph data:", data);
      return;
    }

    // Index nodes by ID
    graphData.nodes = {};
    data.nodes.forEach(n => {
      graphData.nodes[n.id] = n;
    });
    graphData.edges = data.edges;
    graphData.bounds = data.bounds;

    populateDropdowns(data.nodes);
    renderGraphOnMap();

    // Default select initial origin and destination
    const selectSource = document.getElementById("select-source");
    const selectTarget = document.getElementById("select-target");
    if (selectSource.querySelector('option[value="CYBER_TOWERS"]')) {
      selectSource.value = "CYBER_TOWERS";
    } else if (selectSource.options.length > 1) {
      selectSource.selectedIndex = 1;
    }

    if (selectTarget.querySelector('option[value="FINANCIAL_DISTRICT"]')) {
      selectTarget.value = "FINANCIAL_DISTRICT";
    } else if (selectTarget.options.length > 2) {
      selectTarget.selectedIndex = 2;
    }

    updateMarkerStyles();
    fitMapToBounds();
  } catch (err) {
    console.error("Error loading graph:", err);
  }
}

/**
 * Populates source and target select dropdowns with available nodes.
 */
function populateDropdowns(nodes) {
  const selectSource = document.getElementById("select-source");
  const selectTarget = document.getElementById("select-target");

  selectSource.innerHTML = '<option value="" disabled selected>Select origin junction...</option>';
  selectTarget.innerHTML = '<option value="" disabled selected>Select destination junction...</option>';

  // Sort nodes alphabetically by name
  const sortedNodes = [...nodes].sort((a, b) => a.name.localeCompare(b.name));

  sortedNodes.forEach(n => {
    const opt1 = document.createElement("option");
    opt1.value = n.id;
    opt1.textContent = `${n.name} (${n.category})`;
    selectSource.appendChild(opt1);

    const opt2 = document.createElement("option");
    opt2.value = n.id;
    opt2.textContent = `${n.name} (${n.category})`;
    selectTarget.appendChild(opt2);
  });
}

/**
 * Renders graph vertices and road segments onto the Leaflet map.
 */
function renderGraphOnMap() {
  // Clear previous base edges
  baseEdgeLayers.forEach(layer => map.removeLayer(layer));
  baseEdgeLayers = [];

  // Draw background graph edges (subtle road lines)
  graphData.edges.forEach(edge => {
    const polyline = L.polyline([edge.from_coords, edge.to_coords], {
      color: "#475569",
      weight: 3.5,
      opacity: 0.6,
      dashArray: "4, 6"
    }).addTo(map);

    polyline.bindTooltip(
      `<strong>${edge.road_name}</strong><br/>Distance: ${edge.weight} km • Speed: ${edge.speed_kmh} km/h`,
      { sticky: true, className: "edge-tooltip" }
    );

    baseEdgeLayers.push(polyline);
  });

  // Draw graph nodes as interactive markers
  Object.values(graphData.nodes).forEach(node => {
    const customIcon = L.divIcon({
      className: "custom-node-icon",
      html: `<span>${node.name.substring(0, 2).toUpperCase()}</span>`,
      iconSize: [26, 26],
      iconAnchor: [13, 13]
    });

    const marker = L.marker([node.lat, node.lon], { icon: customIcon }).addTo(map);

    const popupContent = `
      <div class="popup-node-title">${node.name}</div>
      <div class="popup-node-category">${node.category}</div>
      <p style="font-size:0.75rem; margin-bottom:8px; color:#cbd5e1;">${node.description}</p>
      <div>
        <button class="popup-btn-select" onclick="setAsSource('${node.id}')">Set as Origin</button>
        <button class="popup-btn-select" style="background:#e11d48;" onclick="setAsTarget('${node.id}')">Set as Target</button>
      </div>
    `;

    marker.bindPopup(popupContent);
    marker.bindTooltip(`<strong>${node.name}</strong><br/><span style="color:#94a3b8">${node.category}</span>`, {
      direction: "top",
      offset: [0, -12]
    });

    nodeMarkers[node.id] = marker;
  });
}

/**
 * Sets node as source from map popup.
 */
window.setAsSource = function(nodeId) {
  document.getElementById("select-source").value = nodeId;
  map.closePopup();
  updateMarkerStyles();
};

/**
 * Sets node as target from map popup.
 */
window.setAsTarget = function(nodeId) {
  document.getElementById("select-target").value = nodeId;
  map.closePopup();
  updateMarkerStyles();
};

/**
 * Updates marker classes based on selected source/target and path.
 */
function updateMarkerStyles(pathNodes = []) {
  const src = document.getElementById("select-source").value;
  const tgt = document.getElementById("select-target").value;

  Object.entries(nodeMarkers).forEach(([id, marker]) => {
    const el = marker.getElement();
    if (!el) return;

    el.classList.remove("source-node", "target-node", "path-node");

    if (id === src) {
      el.classList.add("source-node");
    } else if (id === tgt) {
      el.classList.add("target-node");
    } else if (pathNodes.includes(id)) {
      el.classList.add("path-node");
    }
  });
}

/**
 * Smoothly fits the map view to contain the graph or active route.
 */
function fitMapToBounds(latLngs = null) {
  if (latLngs && latLngs.length > 0) {
    map.fitBounds(L.latLngBounds(latLngs), { padding: [60, 60], maxZoom: 15 });
  } else if (graphData.bounds) {
    const b = graphData.bounds;
    map.fitBounds([[b.min_lat, b.min_lon], [b.max_lat, b.max_lon]], { padding: [40, 40] });
  }
}

/**
 * Attaches UI event listeners for buttons and form inputs.
 */
function bindEventListeners() {
  document.getElementById("btn-find-route").addEventListener("click", handleFindRoute);
  document.getElementById("btn-compare-all").addEventListener("click", handleCompareAll);
  document.getElementById("btn-quick-compare").addEventListener("click", handleCompareAll);

  // Swap button
  document.getElementById("btn-swap-nodes").addEventListener("click", () => {
    const src = document.getElementById("select-source");
    const tgt = document.getElementById("select-target");
    const temp = src.value;
    src.value = tgt.value;
    tgt.value = temp;
    updateMarkerStyles();
  });

  // Fit bounds button
  document.getElementById("btn-fit-bounds").addEventListener("click", () => {
    fitMapToBounds();
  });

  // Preset pills
  document.querySelectorAll(".preset-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      const src = pill.getAttribute("data-src");
      const tgt = pill.getAttribute("data-tgt");
      document.getElementById("select-source").value = src;
      document.getElementById("select-target").value = tgt;
      updateMarkerStyles();
      handleFindRoute();
    });
  });

  // Route View Toggles (Optimal vs Alt 1 vs Alt 2)
  document.querySelectorAll("#route-view-toggles .layer-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const targetRouteKey = btn.getAttribute("data-route");
      setActiveRouteView(targetRouteKey);
    });
  });

  // Modal close buttons
  document.getElementById("btn-close-modal").addEventListener("click", closeModal);
  document.getElementById("btn-modal-close-bottom").addEventListener("click", closeModal);
  document.getElementById("compare-modal").addEventListener("click", (e) => {
    if (e.target.id === "compare-modal") closeModal();
  });

  // Selection change
  document.getElementById("select-source").addEventListener("change", () => updateMarkerStyles());
  document.getElementById("select-target").addEventListener("change", () => updateMarkerStyles());
}

/**
 * Executes route calculation by calling the backend API.
 */
async function handleFindRoute() {
  const source = document.getElementById("select-source").value;
  const target = document.getElementById("select-target").value;
  const algorithm = document.querySelector('input[name="algorithm"]:checked')?.value || "dijkstra";

  if (!source || !target) {
    alert("Please select both a starting origin and a destination junction.");
    return;
  }

  const btn = document.getElementById("btn-find-route");
  const origText = btn.innerHTML;
  btn.innerHTML = `<span>Calculating...</span>`;
  btn.disabled = true;

  try {
    const res = await fetch("/api/route", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source, target, algorithm })
    });

    const data = await res.json();
    if (!data.success) {
      alert("Error: " + (data.error || "Failed to find route."));
      return;
    }

    currentRouteResult = data;
    displayRouteResults(data);
    drawRoutesOnMap(data);
  } catch (err) {
    console.error("API error:", err);
    alert("Network error while connecting to route engine.");
  } finally {
    btn.innerHTML = origText;
    btn.disabled = false;
  }
}

/**
 * Updates sidebar with metrics, DAA proof explanation, and turn-by-turn steps.
 */
function displayRouteResults(data) {
  const { optimal_route, alternatives, explanation } = data;
  const resultsCard = document.getElementById("results-card");
  resultsCard.classList.remove("hidden");

  // Header info
  document.getElementById("res-algo-badge").textContent = optimal_route.algorithm;
  document.getElementById("res-hops-count").textContent = `${optimal_route.path.length} junctions (${optimal_route.path_details.length} road legs)`;

  // Metrics
  document.getElementById("metric-distance").textContent = `${optimal_route.cost} km`;
  document.getElementById("metric-time").textContent = `${optimal_route.total_time_min} min`;
  document.getElementById("metric-nodes").textContent = `${optimal_route.visited_count} nodes`;
  document.getElementById("metric-runtime").textContent = `${optimal_route.execution_time_ms} ms`;

  // Explainer Card
  document.getElementById("exp-principle").textContent = explanation.daa_principle;
  document.getElementById("exp-summary").textContent = explanation.proof_summary;

  // Alternatives comparison inside explainer
  const altContainer = document.getElementById("exp-alternatives-container");
  altContainer.innerHTML = "";

  if (alternatives && alternatives.length > 0) {
    alternatives.forEach((alt, idx) => {
      const row = document.createElement("div");
      row.className = `alt-row-item ${idx === 1 ? 'alt-2-border' : ''}`;
      row.innerHTML = `
        <div class="alt-title">
          <span>${alt.label}</span>
          <span class="alt-delta">+${alt.delta_km} km (+${alt.delta_pct}%)</span>
        </div>
        <div class="alt-reason">${alt.reason_suboptimal}</div>
      `;
      altContainer.appendChild(row);
    });
  } else {
    altContainer.innerHTML = `<div class="alt-reason" style="color:#94a3b8;">Single viable corridor on this network topology.</div>`;
  }

  // Turn-by-Turn steps
  const stepsList = document.getElementById("steps-list");
  stepsList.innerHTML = "";
  document.getElementById("steps-count").textContent = optimal_route.path_details.length;

  optimal_route.path_details.forEach(step => {
    const item = document.createElement("div");
    item.className = "step-item";
    item.innerHTML = `
      <div class="step-desc">
        <strong>${step.step}. ${step.from_name} ➔ ${step.to_name}</strong>
        <div style="font-size:0.7rem; color:#94a3b8;">via ${step.road_name} (${step.road_type})</div>
      </div>
      <div class="step-meta">
        ${step.segment_cost_km} km<br/>~${step.estimated_time_min}m
      </div>
    `;
    stepsList.appendChild(item);
  });

  // Layer toggle buttons visibility
  const btnAlt1 = document.getElementById("btn-toggle-alt1");
  const btnAlt2 = document.getElementById("btn-toggle-alt2");
  
  if (alternatives && alternatives[0]) {
    btnAlt1.style.display = "inline-flex";
    btnAlt1.innerHTML = `<span class="route-color-indicator alt1"></span> Alt 1 (${alternatives[0].cost} km)`;
  } else {
    btnAlt1.style.display = "none";
  }

  if (alternatives && alternatives[1]) {
    btnAlt2.style.display = "inline-flex";
    btnAlt2.innerHTML = `<span class="route-color-indicator alt2"></span> Alt 2 (${alternatives[1].cost} km)`;
  } else {
    btnAlt2.style.display = "none";
  }

  // Reset layer active state to optimal
  document.querySelectorAll("#route-view-toggles .layer-btn").forEach(b => b.classList.remove("active"));
  document.querySelector('#route-view-toggles .layer-btn[data-route="optimal"]').classList.add("active");

  // Render algorithm-specific visual sections (A*, Dijkstra, Floyd-Warshall)
  renderAlgorithmSpecificDetails(optimal_route);
}

/**
 * Renders algorithm-specific exploration metrics:
 * - A*: g(n), h(n), f(n) states table
 * - Dijkstra: visited/explored nodes sequence & settled costs
 * - Floyd-Warshall: shortest path info & interactive distance matrix
 */
function renderAlgorithmSpecificDetails(route) {
  const astarSec = document.getElementById("section-astar");
  const dijkstraSec = document.getElementById("section-dijkstra");
  const floydSec = document.getElementById("section-floyd");

  astarSec.classList.add("hidden");
  dijkstraSec.classList.add("hidden");
  floydSec.classList.add("hidden");

  if (route.algorithm_key === "astar") {
    astarSec.classList.remove("hidden");
    const tbody = document.getElementById("astar-table-body");
    tbody.innerHTML = "";
    if (route.explored_states && route.explored_states.length > 0) {
      route.explored_states.forEach(st => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${st.step}</td>
          <td class="node-col">${st.node_name}</td>
          <td class="val-g">${st.g} km</td>
          <td class="val-h">${st.h} km</td>
          <td class="val-f">${st.f} km</td>
          <td>${st.parent}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  } else if (route.algorithm_key === "dijkstra") {
    dijkstraSec.classList.remove("hidden");
    const tbody = document.getElementById("dijkstra-table-body");
    tbody.innerHTML = "";
    if (route.visited_nodes_details && route.visited_nodes_details.length > 0) {
      route.visited_nodes_details.forEach(node => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${node.step}</td>
          <td class="node-col">${node.node_name}</td>
          <td class="val-f">${node.settled_distance} km</td>
          <td>${node.parent}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  } else if (route.algorithm_key === "floyd_warshall") {
    floydSec.classList.remove("hidden");
    if (route.shortest_path_info) {
      document.getElementById("fw-info-text").textContent = route.shortest_path_info;
    }
    renderFloydWarshallMatrix(route);
  }
}

/**
 * Renders the Floyd-Warshall distance matrix with the source row and source->target cell highlighted.
 */
function renderFloydWarshallMatrix(route) {
  const container = document.getElementById("matrix-container");
  if (!container || !route.distance_matrix || !route.matrix_headers) return;

  const headers = route.matrix_headers;
  const matrix = route.distance_matrix;
  const srcIdx = route.source_idx;
  const tgtIdx = route.target_idx;

  let html = `<table class="matrix-table"><thead><tr><th class="matrix-corner">From \\ To</th>`;
  headers.forEach(h => {
    const shortName = h.name.split(" ")[0];
    html += `<th title="${h.name}">${shortName}</th>`;
  });
  html += `</tr></thead><tbody>`;

  matrix.forEach((row, i) => {
    const isSourceRow = (i === srcIdx);
    html += `<tr class="${isSourceRow ? 'matrix-row-source' : ''}">`;
    html += `<th class="matrix-row-header" title="${headers[i].name}">${headers[i].name}</th>`;
    row.forEach((val, j) => {
      const isOptimalCell = (i === srcIdx && j === tgtIdx);
      const cellClass = isOptimalCell ? 'matrix-cell-optimal' : '';
      const cellTitle = `${headers[i].name} ➔ ${headers[j].name}: ${val} km`;
      html += `<td class="${cellClass}" title="${cellTitle}">${val}</td>`;
    });
    html += `</tr>`;
  });

  html += `</tbody></table>`;
  container.innerHTML = html;
}

/**
 * Draws optimal route and alternative polylines onto Leaflet map.
 */
function drawRoutesOnMap(data) {
  const { optimal_route, alternatives } = data;

  // Clear previous route polylines
  Object.keys(routeLayers).forEach(k => {
    if (routeLayers[k]) {
      map.removeLayer(routeLayers[k]);
      routeLayers[k] = null;
    }
  });

  const allRouteCoords = [];

  // 1. Draw Alternative 2 (if present)
  if (alternatives && alternatives[1]) {
    const coordsAlt2 = alternatives[1].path.map(id => [graphData.nodes[id].lat, graphData.nodes[id].lon]);
    routeLayers.alt_2 = L.polyline(coordsAlt2, {
      color: "#f43f5e",
      weight: 4,
      opacity: 0.75,
      dashArray: "6, 8"
    }).addTo(map);

    routeLayers.alt_2.bindTooltip(`<strong>${alternatives[1].label}</strong><br/>${alternatives[1].cost} km (+${alternatives[1].delta_km} km detour)`, { sticky: true });
  }

  // 2. Draw Alternative 1 (if present)
  if (alternatives && alternatives[0]) {
    const coordsAlt1 = alternatives[0].path.map(id => [graphData.nodes[id].lat, graphData.nodes[id].lon]);
    routeLayers.alt_1 = L.polyline(coordsAlt1, {
      color: "#f59e0b",
      weight: 5,
      opacity: 0.85,
      dashArray: "7, 9"
    }).addTo(map);

    routeLayers.alt_1.bindTooltip(`<strong>${alternatives[0].label}</strong><br/>${alternatives[0].cost} km (+${alternatives[0].delta_km} km detour)`, { sticky: true });
  }

  // 3. Draw Optimal Route in vibrant Emerald Green with high z-index
  const optCoords = optimal_route.path.map(id => [graphData.nodes[id].lat, graphData.nodes[id].lon]);
  optCoords.forEach(c => allRouteCoords.push(c));

  routeLayers.optimal = L.polyline(optCoords, {
    color: "#10b981",
    weight: 6.5,
    opacity: 0.95
  }).addTo(map);

  routeLayers.optimal.bindTooltip(
    `<strong>Optimal Path (${optimal_route.algorithm})</strong><br/>Total: ${optimal_route.cost} km • ${optimal_route.total_time_min} mins`,
    { sticky: true }
  );

  // Update node marker styling along the path
  updateMarkerStyles(optimal_route.path);

  // Fit map to optimal route
  fitMapToBounds(optCoords);
}

/**
 * Toggles focus between optimal route and alternatives on the map.
 */
function setActiveRouteView(routeKey) {
  document.querySelectorAll("#route-view-toggles .layer-btn").forEach(b => b.classList.remove("active"));
  const activeBtn = document.querySelector(`#route-view-toggles .layer-btn[data-route="${routeKey}"]`);
  if (activeBtn) activeBtn.classList.add("active");

  if (!currentRouteResult) return;

  const { optimal_route, alternatives } = currentRouteResult;

  if (routeKey === "optimal" && routeLayers.optimal) {
    routeLayers.optimal.bringToFront();
    const coords = optimal_route.path.map(id => [graphData.nodes[id].lat, graphData.nodes[id].lon]);
    fitMapToBounds(coords);
    updateMarkerStyles(optimal_route.path);
  } else if (routeKey === "alt_1" && alternatives && alternatives[0] && routeLayers.alt_1) {
    routeLayers.alt_1.bringToFront();
    const coords = alternatives[0].path.map(id => [graphData.nodes[id].lat, graphData.nodes[id].lon]);
    fitMapToBounds(coords);
    updateMarkerStyles(alternatives[0].path);
  } else if (routeKey === "alt_2" && alternatives && alternatives[1] && routeLayers.alt_2) {
    routeLayers.alt_2.bringToFront();
    const coords = alternatives[1].path.map(id => [graphData.nodes[id].lat, graphData.nodes[id].lon]);
    fitMapToBounds(coords);
    updateMarkerStyles(alternatives[1].path);
  }
}

/**
 * Opens comparison modal and runs Dijkstra, A*, and Floyd-Warshall side-by-side.
 */
async function handleCompareAll() {
  const source = document.getElementById("select-source").value;
  const target = document.getElementById("select-target").value;

  if (!source || !target) {
    alert("Please select both a source origin and destination first.");
    return;
  }

  // Open modal in loading state
  const modal = document.getElementById("compare-modal");
  modal.classList.remove("hidden");
  document.getElementById("modal-route-label").textContent = 
    `Benchmark between ${graphData.nodes[source]?.name || source} ➔ ${graphData.nodes[target]?.name || target}`;

  try {
    const res = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source, target })
    });

    const data = await res.json();
    if (!data.success) {
      alert("Comparison error: " + (data.error || "Failed to compare."));
      closeModal();
      return;
    }

    populateComparisonModal(data);
  } catch (err) {
    console.error("Comparison API error:", err);
    alert("Network error comparing algorithms.");
    closeModal();
  }
}

/**
 * Fills out comparison modal with head-to-head metrics and DAA analysis.
 */
function populateComparisonModal(data) {
  const cmp = data.comparison;
  const algos = cmp.algorithms;
  const results = data.results;

  // Banner
  const banner = document.getElementById("modal-verdict-banner");
  if (cmp.optimality_consistent) {
    banner.className = "verdict-banner banner-success";
    document.getElementById("banner-title").textContent = "✓ Optimality Mathematically Verified";
    document.getElementById("banner-desc").textContent = 
      `All 3 algorithms independently discovered the exact identical shortest cost of ${cmp.optimal_cost_km} km.`;
  } else {
    banner.className = "verdict-banner";
    banner.style.background = "rgba(239, 68, 68, 0.15)";
    document.getElementById("banner-title").textContent = "Discrepancy Detected";
  }

  // Dijkstra Card
  document.getElementById("cmp-dijkstra-cost").textContent = algos.dijkstra.cost_km;
  document.getElementById("cmp-dijkstra-time").textContent = `${algos.dijkstra.execution_time_ms} ms`;
  document.getElementById("cmp-dijkstra-nodes").textContent = algos.dijkstra.nodes_visited;
  document.getElementById("cmp-dijkstra-ops").textContent = algos.dijkstra.operations;

  // A* Card
  document.getElementById("cmp-astar-cost").textContent = algos.astar.cost_km;
  document.getElementById("cmp-astar-time").textContent = `${algos.astar.execution_time_ms} ms`;
  document.getElementById("cmp-astar-nodes").textContent = `${algos.astar.nodes_visited} (Pruned ${(100 - (algos.astar.nodes_visited / Math.max(algos.dijkstra.nodes_visited, 1) * 100)).toFixed(0)}%)`;
  document.getElementById("cmp-astar-ops").textContent = algos.astar.operations;

  // Floyd-Warshall Card
  document.getElementById("cmp-fw-cost").textContent = algos.floyd_warshall.cost_km;
  document.getElementById("cmp-fw-time").textContent = `${algos.floyd_warshall.execution_time_ms} ms`;
  document.getElementById("cmp-fw-lookup").textContent = `${algos.floyd_warshall.lookup_time_ms} ms`;
  document.getElementById("cmp-fw-iterations").textContent = algos.floyd_warshall.operations;

  // Efficiency Analysis Narrative
  document.getElementById("cmp-analysis-text").textContent = cmp.efficiency_analysis;
}

/**
 * Closes the comparison modal.
 */
function closeModal() {
  document.getElementById("compare-modal").classList.add("hidden");
}

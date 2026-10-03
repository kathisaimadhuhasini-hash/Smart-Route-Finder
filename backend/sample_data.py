from typing import List, Dict, Any
from algorithms.graph import Graph

# 15 Key Tech Corridor Landmark Locations with real GPS coordinates (Cyber City Metro Hub)
SAMPLE_NODES: List[Dict[str, Any]] = [
    {
        "id": "CYBER_TOWERS",
        "name": "Cyber Towers",
        "lat": 17.4504,
        "lon": 78.3809,
        "category": "Tech Hub",
        "description": "Central IT landmark and primary metro transit hub."
    },
    {
        "id": "MINDSPACE",
        "name": "Mindspace IT Park",
        "lat": 17.4418,
        "lon": 78.3792,
        "category": "Commercial",
        "description": "Major software park with campus corridors."
    },
    {
        "id": "INORBIT_MALL",
        "name": "Inorbit Mall",
        "lat": 17.4343,
        "lon": 78.3867,
        "category": "Retail & Transit",
        "description": "Lakeside commercial junction near Durgam Cheruvu."
    },
    {
        "id": "CABLE_BRIDGE",
        "name": "Durgam Cheruvu Cable Bridge",
        "lat": 17.4320,
        "lon": 78.3965,
        "category": "Scenic Expressway",
        "description": "Architectural suspension bridge connecting IT corridor to Jubilee Hills."
    },
    {
        "id": "JUBILEE_HILLS",
        "name": "Jubilee Hills Checkpost",
        "lat": 17.4300,
        "lon": 78.4110,
        "category": "Urban Center",
        "description": "High-density residential and commercial center."
    },
    {
        "id": "RAIDURG_METRO",
        "name": "Raidurg Metro Terminal",
        "lat": 17.4390,
        "lon": 78.3760,
        "category": "Transit Hub",
        "description": "Terminal metro station connecting suburban lines."
    },
    {
        "id": "BIODIVERSITY_JN",
        "name": "Bio-Diversity Junction",
        "lat": 17.4312,
        "lon": 78.3688,
        "category": "Highway Junction",
        "description": "Multi-level flyover linking Gachibowli and Mehdipatnam."
    },
    {
        "id": "GACHIBOWLI_STADIUM",
        "name": "Gachibowli Stadium",
        "lat": 17.4468,
        "lon": 78.3512,
        "category": "Sports Complex",
        "description": "International sports arena and expressway link."
    },
    {
        "id": "FINANCIAL_DISTRICT",
        "name": "Financial District Hub",
        "lat": 17.4172,
        "lon": 78.3435,
        "category": "Banking & FinTech",
        "description": "Concentration of multinational investment banks and tech giants."
    },
    {
        "id": "WIPRO_CIRCLE",
        "name": "Wipro Circle",
        "lat": 17.4265,
        "lon": 78.3498,
        "category": "Roundabout",
        "description": "High-traffic crossroads connecting Gachibowli and Financial District."
    },
    {
        "id": "KOTHAGUDA_X",
        "name": "Kothaguda Crossroads",
        "lat": 17.4610,
        "lon": 78.3695,
        "category": "Junction",
        "description": "Flyover connecting Kondapur and Botanical Gardens."
    },
    {
        "id": "BOTANICAL_GARDEN",
        "name": "Botanical Garden Junction",
        "lat": 17.4565,
        "lon": 78.3620,
        "category": "Eco Corridor",
        "description": "Green corridor arterial road with moderate traffic."
    },
    {
        "id": "HCU_UNIVERSITY",
        "name": "Central University Campus",
        "lat": 17.4590,
        "lon": 78.3340,
        "category": "University",
        "description": "Sprawling educational university campus."
    },
    {
        "id": "ORR_EXPRESSWAY",
        "name": "Outer Ring Road (ORR) Tollway",
        "lat": 17.4120,
        "lon": 78.3300,
        "category": "Expressway",
        "description": "High-speed 8-lane expressway bypassing inner city traffic."
    },
    {
        "id": "MADHAPUR_METRO",
        "name": "Madhapur Central",
        "lat": 17.4460,
        "lon": 78.3910,
        "category": "Commercial Hub",
        "description": "Dense restaurant and startup corridor."
    }
]

# Multiple interconnected weighted routes (distance in km, speed in km/h)
SAMPLE_EDGES: List[Dict[str, Any]] = [
    # Cyber Towers Connections
    {"from": "CYBER_TOWERS", "to": "MINDSPACE", "weight": 1.2, "road_name": "HITEC Main Road", "speed_kmh": 45, "road_type": "arterial"},
    {"from": "CYBER_TOWERS", "to": "MADHAPUR_METRO", "weight": 1.4, "road_name": "Cyber Hills Road", "speed_kmh": 35, "road_type": "urban"},
    {"from": "CYBER_TOWERS", "to": "KOTHAGUDA_X", "weight": 2.1, "road_name": "Kondapur Flyover Way", "speed_kmh": 50, "road_type": "arterial"},

    # Mindspace & Inorbit Corridor
    {"from": "MINDSPACE", "to": "RAIDURG_METRO", "weight": 0.8, "road_name": "Mindspace Loop Road", "speed_kmh": 40, "road_type": "urban"},
    {"from": "MINDSPACE", "to": "INORBIT_MALL", "weight": 1.5, "road_name": "Lake View Parkway", "speed_kmh": 40, "road_type": "arterial"},

    # Lake & Cable Bridge to Jubilee Hills
    {"from": "INORBIT_MALL", "to": "CABLE_BRIDGE", "weight": 1.1, "road_name": "Suspension Bridge Approach", "speed_kmh": 55, "road_type": "expressway"},
    {"from": "CABLE_BRIDGE", "to": "JUBILEE_HILLS", "weight": 1.8, "road_name": "Jubilee Hills Road No. 45", "speed_kmh": 50, "road_type": "arterial"},
    {"from": "MADHAPUR_METRO", "to": "JUBILEE_HILLS", "weight": 2.6, "road_name": "Old Jubilee Hills Road", "speed_kmh": 30, "road_type": "urban"},
    {"from": "MADHAPUR_METRO", "to": "INORBIT_MALL", "weight": 1.7, "road_name": "Durgam Cheruvu North Road", "speed_kmh": 35, "road_type": "urban"},

    # Raidurg & Bio-Diversity to Gachibowli / Financial District
    {"from": "RAIDURG_METRO", "to": "BIODIVERSITY_JN", "weight": 1.3, "road_name": "Old Mumbai Highway Link", "speed_kmh": 50, "road_type": "arterial"},
    {"from": "BIODIVERSITY_JN", "to": "WIPRO_CIRCLE", "weight": 2.2, "road_name": "Gachibowli Flyover Avenue", "speed_kmh": 60, "road_type": "expressway"},
    {"from": "BIODIVERSITY_JN", "to": "GACHIBOWLI_STADIUM", "weight": 2.5, "road_name": "Stadium Link Road", "speed_kmh": 45, "road_type": "arterial"},

    # Wipro Circle & Financial District
    {"from": "WIPRO_CIRCLE", "to": "FINANCIAL_DISTRICT", "weight": 1.6, "road_name": "ISB Road", "speed_kmh": 55, "road_type": "arterial"},
    {"from": "FINANCIAL_DISTRICT", "to": "ORR_EXPRESSWAY", "weight": 1.8, "road_name": "Financial District ORR Toll Ramp", "speed_kmh": 80, "road_type": "expressway"},

    # Gachibowli Stadium & Botanical Garden & University
    {"from": "GACHIBOWLI_STADIUM", "to": "BOTANICAL_GARDEN", "weight": 1.8, "road_name": "Botanical Garden Road", "speed_kmh": 45, "road_type": "arterial"},
    {"from": "GACHIBOWLI_STADIUM", "to": "HCU_UNIVERSITY", "weight": 2.3, "road_name": "University Campus Blvd", "speed_kmh": 40, "road_type": "campus"},
    {"from": "BOTANICAL_GARDEN", "to": "KOTHAGUDA_X", "weight": 1.2, "road_name": "Kothaguda Bypass", "speed_kmh": 45, "road_type": "urban"},
    {"from": "BOTANICAL_GARDEN", "to": "HCU_UNIVERSITY", "weight": 3.1, "road_name": "Lingampally Link Road", "speed_kmh": 45, "road_type": "arterial"},

    # Outer Ring Road High-Speed Bypass Network
    {"from": "HCU_UNIVERSITY", "to": "ORR_EXPRESSWAY", "weight": 5.4, "road_name": "Gopanpally ORR Connector", "speed_kmh": 70, "road_type": "highway"},
    {"from": "GACHIBOWLI_STADIUM", "to": "WIPRO_CIRCLE", "weight": 2.4, "road_name": "IIIT-Hyderabad Junction Way", "speed_kmh": 50, "road_type": "arterial"},
    {"from": "KOTHAGUDA_X", "to": "GACHIBOWLI_STADIUM", "weight": 2.8, "road_name": "Hafeezpet - Gachibowli Road", "speed_kmh": 40, "road_type": "urban"}
]

def build_sample_graph() -> Graph:
    """Builds and returns the weighted Graph populated with the sample tech network."""
    g = Graph(directed=False)

    for node in SAMPLE_NODES:
        g.add_node(
            node_id=node["id"],
            name=node["name"],
            lat=node["lat"],
            lon=node["lon"],
            category=node.get("category", "Junction"),
            description=node.get("description", "")
        )

    for edge in SAMPLE_EDGES:
        g.add_edge(
            u=edge["from"],
            v=edge["to"],
            weight=edge["weight"],
            road_name=edge.get("road_name", ""),
            speed_kmh=edge.get("speed_kmh", 45.0),
            road_type=edge.get("road_type", "primary"),
            bidirectional=True
        )

    return g

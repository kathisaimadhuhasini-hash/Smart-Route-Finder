import sqlite3
import os
from typing import List, Dict, Any, Optional
from algorithms.graph import Graph
from backend.sample_data import SAMPLE_NODES, SAMPLE_EDGES

DB_PATH = os.path.join(os.path.dirname(__file__), "smart_route.db")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force_reseed: bool = False) -> None:
    """Initialize SQLite tables and seed initial graph data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        category TEXT,
        description TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS edges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_node TEXT NOT NULL,
        to_node TEXT NOT NULL,
        weight REAL NOT NULL,
        road_name TEXT,
        speed_kmh REAL DEFAULT 45.0,
        road_type TEXT DEFAULT 'arterial',
        bidirectional INTEGER DEFAULT 1,
        FOREIGN KEY (from_node) REFERENCES nodes(id),
        FOREIGN KEY (to_node) REFERENCES nodes(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS route_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        algorithm TEXT NOT NULL,
        cost REAL,
        visited_count INTEGER,
        execution_time_ms REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    # Check if nodes exist
    cursor.execute("SELECT COUNT(*) FROM nodes")
    count = cursor.fetchone()[0]

    if count == 0 or force_reseed:
        if force_reseed:
            cursor.execute("DELETE FROM edges")
            cursor.execute("DELETE FROM nodes")

        for n in SAMPLE_NODES:
            cursor.execute("""
            INSERT OR REPLACE INTO nodes (id, name, lat, lon, category, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (n["id"], n["name"], n["lat"], n["lon"], n["category"], n["description"]))

        for e in SAMPLE_EDGES:
            cursor.execute("""
            INSERT INTO edges (from_node, to_node, weight, road_name, speed_kmh, road_type, bidirectional)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (e["from"], e["to"], e["weight"], e["road_name"], e.get("speed_kmh", 45.0), e.get("road_type", "arterial")))

        conn.commit()

    conn.close()

def load_graph_from_db() -> Graph:
    """Loads and reconstructs the Graph object from SQLite."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    g = Graph(directed=False)

    cursor.execute("SELECT * FROM nodes")
    for row in cursor.fetchall():
        g.add_node(
            node_id=row["id"],
            name=row["name"],
            lat=row["lat"],
            lon=row["lon"],
            category=row["category"],
            description=row["description"]
        )

    cursor.execute("SELECT * FROM edges")
    for row in cursor.fetchall():
        g.add_edge(
            u=row["from_node"],
            v=row["to_node"],
            weight=row["weight"],
            road_name=row["road_name"],
            speed_kmh=row["speed_kmh"],
            road_type=row["road_type"],
            bidirectional=bool(row["bidirectional"])
        )

    conn.close()
    return g

def log_route_query(source: str, target: str, algorithm: str, cost: float, 
                    visited_count: int, execution_time_ms: float) -> None:
    """Log search query performance for analysis and history tracking."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO route_queries (source_id, target_id, algorithm, cost, visited_count, execution_time_ms)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (source, target, algorithm, cost, visited_count, execution_time_ms))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to log route query: {e}")

def get_recent_queries(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve recent queries for analytics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT q.*, n1.name as source_name, n2.name as target_name 
        FROM route_queries q
        JOIN nodes n1 ON q.source_id = n1.id
        JOIN nodes n2 ON q.target_id = n2.id
        ORDER BY q.id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
        conn.close()
        return results
    except Exception:
        return []

import os
import sys

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import app

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Smart Route Finder - DAA Hackathon Project")
    print("📍 Route Engine: Dijkstra | A* Search | Floyd-Warshall")
    print("🌐 Web Server starting at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)

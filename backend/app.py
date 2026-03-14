from fastapi import FastAPI
from core.graph import build_graph
from core.dijkstra import find_cheapest_route
import os

app = FastAPI(title="AirCrazyScarello API")

# Caminhos para os arquivos de dados
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AIRPORTS_FILE = os.path.join(BASE_DIR, "data", "airports.csv")
FLIGHTS_FILE = os.path.join(BASE_DIR, "data", "flights.csv")

# Instancia o grafo
G = build_graph(AIRPORTS_FILE, FLIGHTS_FILE)

@app.get("/")
def home():
    return {"message": "Welcome to AirCrazyScarello API", "available_airports": list(G.nodes)}

@app.get("/search")
def search_route(origin: str, destination: str):
    result = find_cheapest_route(G, origin.upper(), destination.upper())
    if result:
        return result
    return {"error": "No route found"}

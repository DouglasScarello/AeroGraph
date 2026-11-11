import pandas as pd
import networkx as nx
from typing import Dict, Any, Optional

def build_graph(airports_file: str, flights_file: str) -> nx.DiGraph:
    """
    Carrega aeroportos e voos dos arquivos CSV e constrói um grafo direcionado ponderado com coordenadas.
    """
    airports = pd.read_csv(airports_file)
    flights = pd.read_csv(flights_file)
    
    G = nx.DiGraph()
    
    # Adiciona nós (aeroportos com coordenadas geográficas)
    has_lat = 'Lat' in airports.columns and 'Lon' in airports.columns
    for _, row in airports.iterrows():
        iata = str(row['IATA']).strip().upper()
        lat = float(row['Lat']) if has_lat and pd.notnull(row['Lat']) else 0.0
        lon = float(row['Lon']) if has_lat and pd.notnull(row['Lon']) else 0.0
        G.add_node(
            iata,
            city=str(row['City']).strip(),
            country=str(row['Country']).strip(),
            lat=lat,
            lon=lon
        )
    
    # Adiciona arestas (voos direcionados)
    for _, row in flights.iterrows():
        G.add_edge(
            str(row['Origin']).strip().upper(),
            str(row['Destination']).strip().upper(),
            price=int(row['Price']),
            duration=int(row['Duration'])
        )
    
    return G

def get_airport_info(G: nx.DiGraph, iata: str) -> Optional[Dict[str, Any]]:
    """
    Retorna os metadados de um aeroporto presente no grafo incluindo coordenadas.
    """
    iata = iata.upper()
    if iata in G.nodes:
        data = G.nodes[iata]
        return {
            "iata": iata,
            "city": data.get("city", ""),
            "country": data.get("country", ""),
            "lat": data.get("lat", 0.0),
            "lon": data.get("lon", 0.0)
        }
    return None

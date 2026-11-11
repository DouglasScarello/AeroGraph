import pandas as pd
import networkx as nx
from typing import Dict, Any, Optional

def build_graph(airports_file: str, flights_file: str) -> nx.DiGraph:
    """
    Carrega aeroportos e voos dos arquivos CSV e constrói um grafo direcionado ponderado.
    """
    airports = pd.read_csv(airports_file)
    flights = pd.read_csv(flights_file)
    
    G = nx.DiGraph()
    
    # Adiciona nós (aeroportos)
    for _, row in airports.iterrows():
        G.add_node(
            str(row['IATA']).strip().upper(),
            city=str(row['City']).strip(),
            country=str(row['Country']).strip()
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
    Retorna os metadados de um aeroporto presente no grafo.
    """
    iata = iata.upper()
    if iata in G.nodes:
        data = G.nodes[iata]
        return {
            "iata": iata,
            "city": data.get("city", ""),
            "country": data.get("country", "")
        }
    return None

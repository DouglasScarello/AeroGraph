import networkx as nx
from typing import Dict, Any, Literal
from core.exceptions import AirportNotFoundError, NoRouteFoundError

def find_best_route(
    G: nx.DiGraph,
    origin: str,
    destination: str,
    criteria: Literal["price", "duration"] = "price"
) -> Dict[str, Any]:
    """
    Calcula o caminho ótimo entre dois aeroportos usando o algoritmo de Dijkstra.
    
    :param G: Grafo direcionado com os voos
    :param origin: Código IATA de origem
    :param destination: Código IATA de destino
    :param criteria: 'price' para menor custo ou 'duration' para menor tempo
    :return: Dicionário com detalhes da rota, segmentos e totais
    """
    origin = origin.upper()
    destination = destination.upper()

    if origin not in G.nodes:
        raise AirportNotFoundError(origin)
    if destination not in G.nodes:
        raise AirportNotFoundError(destination)

    if origin == destination:
        return {
            "origin": origin,
            "destination": destination,
            "criteria": criteria,
            "path": [origin],
            "segments": [],
            "total_price": 0,
            "total_duration": 0,
            "stops": 0
        }

    weight_field = "duration" if criteria == "duration" else "price"

    try:
        path = nx.dijkstra_path(G, origin, destination, weight=weight_field)
    except nx.NetworkXNoPath:
        raise NoRouteFoundError(origin, destination)

    segments = []
    total_price = 0
    total_duration = 0

    for u, v in zip(path[:-1], path[1:]):
        edge_data = G[u][v]
        p = edge_data["price"]
        d = edge_data["duration"]
        total_price += p
        total_duration += d
        segments.append({
            "from_airport": u,
            "to_airport": v,
            "price": p,
            "duration": d
        })

    return {
        "origin": origin,
        "destination": destination,
        "criteria": criteria,
        "path": path,
        "segments": segments,
        "total_price": total_price,
        "total_duration": total_duration,
        "stops": max(0, len(path) - 2)
    }

# Compatibilidade retroativa
def find_cheapest_route(G, origin, destination):
    try:
        return find_best_route(G, origin, destination, criteria="price")
    except (AirportNotFoundError, NoRouteFoundError):
        return None

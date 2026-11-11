import networkx as nx
from typing import Dict, Any, List, Literal
from core.exceptions import AirportNotFoundError, NoRouteFoundError

def _build_route_dict(G: nx.DiGraph, path: List[str], rank: int, label: str) -> Dict[str, Any]:
    segments = []
    total_price = 0
    total_duration = 0

    for u, v in zip(path[:-1], path[1:]):
        edge_data = G[u][v]
        p = edge_data["price"]
        d = edge_data["duration"]
        total_price += p
        total_duration += d

        u_data = G.nodes[u]
        v_data = G.nodes[v]

        segments.append({
            "from_airport": u,
            "to_airport": v,
            "price": p,
            "duration": d,
            "from_lat": u_data.get("lat", 0.0),
            "from_lon": u_data.get("lon", 0.0),
            "to_lat": v_data.get("lat", 0.0),
            "to_lon": v_data.get("lon", 0.0)
        })

    return {
        "rank": rank,
        "label": label,
        "path": path,
        "segments": segments,
        "total_price": total_price,
        "total_duration": total_duration,
        "stops": max(0, len(path) - 2)
    }

def find_best_routes(
    G: nx.DiGraph,
    origin: str,
    destination: str,
    criteria: Literal["price", "duration"] = "price",
    k: int = 3
) -> Dict[str, Any]:
    """
    Calcula as Top K melhores rotas entre dois aeroportos usando o Algoritmo de Yen (K-Shortest Paths).
    """
    origin = origin.upper()
    destination = destination.upper()

    if origin not in G.nodes:
        raise AirportNotFoundError(origin)
    if destination not in G.nodes:
        raise AirportNotFoundError(destination)

    if origin == destination:
        route = {
            "rank": 1,
            "label": "Origem e Destino Iguais",
            "path": [origin],
            "segments": [],
            "total_price": 0,
            "total_duration": 0,
            "stops": 0
        }
        return {
            "origin": origin,
            "destination": destination,
            "criteria": criteria,
            "total_found": 1,
            "routes": [route]
        }

    weight_field = "duration" if criteria == "duration" else "price"

    try:
        paths_generator = nx.shortest_simple_paths(G, origin, destination, weight=weight_field)
    except nx.NetworkXNoPath:
        raise NoRouteFoundError(origin, destination)

    routes = []
    labels = ["Melhor Escolha", "Alternativa 2", "Alternativa 3", "Alternativa 4", "Alternativa 5"]

    try:
        for idx, path in enumerate(paths_generator):
            if idx >= k:
                break
            label = labels[idx] if idx < len(labels) else f"Alternativa {idx + 1}"
            routes.append(_build_route_dict(G, path, rank=idx + 1, label=label))
    except (nx.NetworkXNoPath, StopIteration):
        pass

    if not routes:
        raise NoRouteFoundError(origin, destination)

    return {
        "origin": origin,
        "destination": destination,
        "criteria": criteria,
        "total_found": len(routes),
        "routes": routes
    }

def find_best_route(G: nx.DiGraph, origin: str, destination: str, criteria: str = "price"):
    """Compatibilidade com chamada singular"""
    res = find_best_routes(G, origin, destination, criteria=criteria, k=1)
    r = res["routes"][0]
    return {
        "origin": origin.upper(),
        "destination": destination.upper(),
        "criteria": criteria,
        "path": r["path"],
        "segments": r["segments"],
        "total_price": r["total_price"],
        "total_duration": r["total_duration"],
        "stops": r["stops"]
    }

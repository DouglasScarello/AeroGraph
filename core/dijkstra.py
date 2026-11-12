import networkx as nx
from typing import Dict, Any, List, Literal
from core.exceptions import AirportNotFoundError, NoRouteFoundError

# Penalidade realista de conexão em solo (layover / tempo de espera e imigração)
LAYOVER_HOURS_PER_STOP = 2

def _build_route_dict(G: nx.DiGraph, path: List[str], rank: int, label: str) -> Dict[str, Any]:
    segments = []
    flight_price = 0
    flight_duration = 0

    for u, v in zip(path[:-1], path[1:]):
        edge_data = G[u][v]
        p = edge_data["price"]
        d = edge_data["duration"]
        flight_price += p
        flight_duration += d

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

    stops = max(0, len(path) - 2)
    # Trade-off explícito: conexões adicionam tempo de espera em solo no total da viagem
    total_duration = flight_duration + (stops * LAYOVER_HOURS_PER_STOP)

    return {
        "rank": rank,
        "label": label,
        "path": path,
        "segments": segments,
        "total_price": flight_price,
        "total_duration": total_duration,
        "flight_duration": flight_duration,
        "layover_hours": stops * LAYOVER_HOURS_PER_STOP,
        "stops": stops
    }

def find_best_route(
    G: nx.DiGraph,
    origin: str,
    destination: str,
    criteria: Literal["price", "duration"] = "price"
) -> Dict[str, Any]:
    """
    Calcula a rota ótima utilizando a implementação otimizada de Dijkstra do NetworkX.
    """
    origin = origin.upper().strip()
    destination = destination.upper().strip()

    if origin not in G.nodes:
        raise AirportNotFoundError(origin)
    if destination not in G.nodes:
        raise AirportNotFoundError(destination)

    if origin == destination:
        return _build_route_dict(G, [origin], rank=1, label="Mesmo Aeroporto")

    weight_field = "duration" if criteria == "duration" else "price"

    try:
        path = nx.dijkstra_path(G, origin, destination, weight=weight_field)
    except nx.NetworkXNoPath:
        raise NoRouteFoundError(origin, destination)

    return _build_route_dict(G, path, rank=1, label="Rota Ótima")

def find_smart_routes(
    G: nx.DiGraph,
    origin: str,
    destination: str
) -> Dict[str, Any]:
    """
    Gera as 3 rotas comparativas:
    1. Mais Barata: Dijkstra com peso 'price'
    2. Mais Rápida: Dijkstra com peso 'duration'
    3. Alternativa / Custo-Benefício: Desvio via Yen (nx.shortest_simple_paths)
    """
    origin = origin.upper().strip()
    destination = destination.upper().strip()

    if origin not in G.nodes:
        raise AirportNotFoundError(origin)
    if destination not in G.nodes:
        raise AirportNotFoundError(destination)

    if origin == destination:
        r = _build_route_dict(G, [origin], rank=1, label="Mesmo Aeroporto")
        r["badge"] = "Local"
        return {
            "origin": origin,
            "destination": destination,
            "total_found": 1,
            "routes": [r]
        }

    # 1. Rota mais econômica via Dijkstra (menor preço de passagens)
    try:
        cheapest_path = nx.dijkstra_path(G, origin, destination, weight="price")
    except nx.NetworkXNoPath:
        raise NoRouteFoundError(origin, destination)

    # 2. Rota mais rápida via Dijkstra (menor tempo de voo)
    try:
        fastest_path = nx.dijkstra_path(G, origin, destination, weight="duration")
    except nx.NetworkXNoPath:
        fastest_path = cheapest_path

    collected_routes = []
    seen_paths = set()

    # Rota 1: Menor Preço
    seen_paths.add(tuple(cheapest_path))
    r1 = _build_route_dict(G, cheapest_path, rank=1, label="Mais Econômica")
    r1["badge"] = "💰 Mais Barata"
    collected_routes.append(r1)

    # Rota 2: Menor Duração (se for diferente)
    if tuple(fastest_path) not in seen_paths:
        seen_paths.add(tuple(fastest_path))
        r2 = _build_route_dict(G, fastest_path, rank=2, label="Mais Rápida")
        r2["badge"] = "⚡ Mais Rápida"
        collected_routes.append(r2)

    # 3. K-Shortest Paths via Yen para achar alternativas não exploradas
    try:
        yen_gen = nx.shortest_simple_paths(G, origin, destination, weight="price")
        for p in yen_gen:
            if tuple(p) not in seen_paths:
                seen_paths.add(tuple(p))
                r_alt = _build_route_dict(G, p, rank=len(collected_routes) + 1, label="Alternativa Viável")
                r_alt["badge"] = "⚖ Alternativa"
                collected_routes.append(r_alt)
                if len(collected_routes) >= 3:
                    break
    except (nx.NetworkXNoPath, StopIteration):
        pass

    return {
        "origin": origin,
        "destination": destination,
        "total_found": len(collected_routes),
        "routes": collected_routes
    }

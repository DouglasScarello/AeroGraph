import networkx as nx
from typing import Dict, Any, List, Optional
from core.exceptions import AirportNotFoundError, NoRouteFoundError
from core.haversine import haversine_distance

# Penalidade de conexão em solo (layover / tempo médio de espera e imigração)
LAYOVER_HOURS_PER_STOP = 2

def _build_route_dict(
    G: nx.DiGraph,
    path: List[str],
    rank: int,
    label: str,
    origin: str,
    destination: str,
    criteria: str = "price"
) -> Dict[str, Any]:
    segments = []
    flight_price = 0
    flight_duration = 0

    for u, v in zip(path[:-1], path[1:]):
        edge_data = G[u][v]
        p = int(edge_data.get("price", 0))
        d = int(edge_data.get("duration", 0))
        flight_price += p
        flight_duration += d

        u_data = G.nodes[u]
        v_data = G.nodes[v]

        u_lat = float(u_data.get("lat", 0.0))
        u_lon = float(u_data.get("lon", 0.0))
        v_lat = float(v_data.get("lat", 0.0))
        v_lon = float(v_data.get("lon", 0.0))

        dist_km = haversine_distance(u_lat, u_lon, v_lat, v_lon) if (u_lat or u_lon) and (v_lat or v_lon) else 0.0

        segments.append({
            "from_airport": u,
            "to_airport": v,
            "price": p,
            "duration": d,
            "from_lat": u_lat,
            "from_lon": u_lon,
            "to_lat": v_lat,
            "to_lon": v_lon,
            "distance_km": round(dist_km, 1)
        })

    stops = max(0, len(path) - 2)
    total_duration = flight_duration + (stops * LAYOVER_HOURS_PER_STOP)

    return {
        "rank": rank,
        "label": label,
        "badge": label,
        "origin": origin,
        "destination": destination,
        "criteria": criteria,
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
    criteria: str = "price"
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
        r = _build_route_dict(G, [origin], rank=1, label="Mesmo Aeroporto", origin=origin, destination=destination, criteria=criteria)
        r["badge"] = "Local"
        return r

    weight_func = (lambda u, v, d: d.get("duration", 0) + LAYOVER_HOURS_PER_STOP) if criteria == "duration" else "price"

    try:
        path = nx.dijkstra_path(G, origin, destination, weight=weight_func)
    except nx.NetworkXNoPath:
        raise NoRouteFoundError(origin, destination)

    return _build_route_dict(G, path, rank=1, label="Rota Ótima", origin=origin, destination=destination, criteria=criteria)

def find_smart_routes(
    G: nx.DiGraph,
    origin: str,
    destination: str,
    criteria: Optional[str] = "smart"
) -> Dict[str, Any]:
    """
    Gera as rotas comparativas:
    1. Mais Barata: Dijkstra com peso 'price'
    2. Mais Rápida: Dijkstra considerando tempo de voo + penalidade de escala em solo por trecho
    3. Alternativas Viáveis: K-caminhos simples via Yen (nx.shortest_simple_paths)
    """
    origin = origin.upper().strip()
    destination = destination.upper().strip()

    if origin not in G.nodes:
        raise AirportNotFoundError(origin)
    if destination not in G.nodes:
        raise AirportNotFoundError(destination)

    if origin == destination:
        r = _build_route_dict(G, [origin], rank=1, label="Mesmo Aeroporto", origin=origin, destination=destination, criteria=criteria or "smart")
        r["badge"] = "Local"
        return {
            "origin": origin,
            "destination": destination,
            "criteria": criteria or "smart",
            "total_found": 1,
            "routes": [r]
        }

    # 1. Rota mais econômica via Dijkstra
    try:
        cheapest_path = nx.dijkstra_path(G, origin, destination, weight="price")
    except nx.NetworkXNoPath:
        raise NoRouteFoundError(origin, destination)

    # 2. Rota mais rápida via Dijkstra com penalidade de escala por conexão incorporada na busca
    # Como todo caminho de n trechos tem n-1 escalas, somar LAYOVER_HOURS_PER_STOP em cada aresta penaliza
    # rotas com conexões diretamente durante a exploração do Min-Heap.
    try:
        fastest_path = nx.dijkstra_path(
            G, origin, destination,
            weight=lambda u, v, d: d.get("duration", 0) + LAYOVER_HOURS_PER_STOP
        )
    except nx.NetworkXNoPath:
        fastest_path = cheapest_path

    collected_routes = []
    seen_paths = set()

    # Rota 1: Menor Preço
    seen_paths.add(tuple(cheapest_path))
    r1 = _build_route_dict(G, cheapest_path, rank=1, label="Mais Econômica", origin=origin, destination=destination, criteria=criteria or "price")
    r1["badge"] = "💰 Mais Barata"
    collected_routes.append(r1)

    # Rota 2: Menor Duração (se for diferente)
    if tuple(fastest_path) not in seen_paths:
        seen_paths.add(tuple(fastest_path))
        r2 = _build_route_dict(G, fastest_path, rank=2, label="Mais Rápida", origin=origin, destination=destination, criteria=criteria or "duration")
        r2["badge"] = "⚡ Mais Rápida"
        collected_routes.append(r2)

    # 3. K-Shortest Paths via Yen para alternativas viáveis
    try:
        yen_gen = nx.shortest_simple_paths(G, origin, destination, weight="price")
        for p in yen_gen:
            if tuple(p) not in seen_paths:
                seen_paths.add(tuple(p))
                r_alt = _build_route_dict(G, p, rank=len(collected_routes) + 1, label="Alternativa Viável", origin=origin, destination=destination, criteria=criteria or "smart")
                r_alt["badge"] = "⚖ Alternativa"
                collected_routes.append(r_alt)
                if len(collected_routes) >= 3:
                    break
    except (nx.NetworkXNoPath, StopIteration):
        pass

    return {
        "origin": origin,
        "destination": destination,
        "criteria": criteria or "smart",
        "total_found": len(collected_routes),
        "routes": collected_routes
    }

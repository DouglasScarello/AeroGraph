import networkx as nx

def find_cheapest_route(G, origin, destination):
    # Menor custo por preço
    try:
        path = nx.dijkstra_path(G, origin, destination, weight='price')
        total_price = sum(G[u][v]['price'] for u, v in zip(path[:-1], path[1:]))
        total_duration = sum(G[u][v]['duration'] for u, v in zip(path[:-1], path[1:]))
        return {'path': path, 'total_price': total_price, 'total_duration': total_duration}
    except nx.NetworkXNoPath:
        return None
    except Exception as e:
        return {"error": str(e)}

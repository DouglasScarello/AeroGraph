"""
Script de Benchmark e Validação de Performance do AeroGraph
Executa medições empíricas com aquecimento (warmup) e múltiplas iterações (N=10).
"""
import time
import statistics
from core.graph import build_graph
from core.dijkstra import find_smart_routes, find_best_route

def run_benchmark():
    print("=" * 65)
    print("✈️  AEROGRAPH — BENCHMARK DE PERFORMANCE (N=10 + Warmup)")
    print("=" * 65)

    t0 = time.perf_counter()
    G = build_graph("data/airports.csv", "data/flights.csv")
    load_time = (time.perf_counter() - t0) * 1000
    print(f"📦 Carga do Grafo em RAM: {load_time:.2f} ms ({len(G.nodes)} nós, {len(G.edges)} arestas)\n")

    test_routes = [
        ("FLN", "GIG", "Doméstico Curto (Brasil)"),
        ("GRU", "LHR", "Transatlântico Direto"),
        ("FLN", "NRT", "Transpacífico Múltiplas Escalas"),
        ("JFK", "SYD", "América do Norte ➔ Oceania"),
        ("CDG", "HND", "Europa ➔ Ásia"),
        ("FLN", "ALH", "Intercontinental Hemisfério Sul")
    ]

    # Aquecimento (Warmup) para caches de CPU e interpretador
    for orig, dest, _ in test_routes:
        find_best_route(G, orig, dest, criteria="price")

    print("1. Dijkstra Simples (Rota Ótima - Média de 10 execuções):")
    all_single = []
    for orig, dest, desc in test_routes:
        times = []
        for _ in range(10):
            t_start = time.perf_counter()
            res = find_best_route(G, orig, dest, criteria="price")
            t_end = time.perf_counter()
            times.append((t_end - t_start) * 1000)
        
        avg_ms = statistics.mean(times)
        std_ms = statistics.stdev(times)
        all_single.append(avg_ms)
        print(f"   • {orig} ➔ {dest} ({desc}): {avg_ms:.2f} ms (±{std_ms:.2f} ms) [Escalas: {res['stops']}]")

    print(f"\n   ⏱️ Média Geral Dijkstra Único: {statistics.mean(all_single):.2f} ms\n")

    print("2. Algoritmo de Yen (K-Shortest Paths - Média de 5 execuções):")
    all_multi = []
    for orig, dest, desc in test_routes:
        times = []
        for _ in range(5):
            t_start = time.perf_counter()
            res = find_smart_routes(G, orig, dest)
            t_end = time.perf_counter()
            times.append((t_end - t_start) * 1000)
        
        avg_ms = statistics.mean(times)
        std_ms = statistics.stdev(times)
        all_multi.append(avg_ms)
        print(f"   • {orig} ➔ {dest} ({desc}): {avg_ms:.2f} ms (±{std_ms:.2f} ms) [{res['total_found']} rotas]")

    print(f"\n   ⏱️ Média Geral Yen K-Paths: {statistics.mean(all_multi):.2f} ms")
    print("=" * 65)

if __name__ == "__main__":
    run_benchmark()

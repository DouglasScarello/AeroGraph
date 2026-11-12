"""
Script de Benchmark e Validação de Performance do AeroGraph
Executa medições reais de latência do algoritmo sobre a malha de 3.224 aeroportos e 36.826 arestas.
"""
import time
import statistics
from core.graph import build_graph
from core.dijkstra import find_smart_routes, find_best_route

def run_benchmark():
    print("=" * 60)
    print("✈️  AEROGRAPH — BENCHMARK OFICIAL DE PERFORMANCE")
    print("=" * 60)

    t0 = time.perf_counter()
    G = build_graph("data/airports.csv", "data/flights.csv")
    load_time = (time.perf_counter() - t0) * 1000
    print(f"📦 Carga do Grafo em RAM: {load_time:.2f} ms ({len(G.nodes)} nós, {len(G.edges)} arestas)\n")

    test_routes = [
        ("FLN", "GIG", "Doméstico Curto (Brasil)"),
        ("GRU", "LHR", "Transatlântico Direto"),
        ("FLN", "NRT", "Transpacífico com Múltiplas Escalas"),
        ("JFK", "SYD", "América do Norte ➔ Oceania"),
        ("CDG", "HND", "Europa ➔ Ásia"),
        ("FLN", "ALH", "Intercontinental Hemisfério Sul")
    ]

    print("1. Dijkstra Simples (Menor Preço - Rota Ótima Única):")
    single_times = []
    for orig, dest, desc in test_routes:
        t_start = time.perf_counter()
        res = find_best_route(G, orig, dest, criteria="price")
        t_end = time.perf_counter()
        ms = (t_end - t_start) * 1000
        single_times.append(ms)
        print(f"   • {orig} ➔ {dest} ({desc}): {ms:.2f} ms [Path: {' ➔ '.join(res['path'])}]")

    print(f"\n   ⏱️ Média Dijkstra Único: {statistics.mean(single_times):.2f} ms")
    print(f"   ⏱️ Mínimo: {min(single_times):.2f} ms | Máximo: {max(single_times):.2f} ms\n")

    print("2. K-Shortest Paths (Algoritmo de Yen - 3 Alternativas Simultâneas):")
    multi_times = []
    for orig, dest, desc in test_routes:
        t_start = time.perf_counter()
        res = find_smart_routes(G, orig, dest)
        t_end = time.perf_counter()
        ms = (t_end - t_start) * 1000
        multi_times.append(ms)
        print(f"   • {orig} ➔ {dest} ({desc}): {ms:.2f} ms ({res['total_found']} rotas encontradas)")

    print(f"\n   ⏱️ Média Yen Multi-Rotas: {statistics.mean(multi_times):.2f} ms")
    print(f"   ⏱️ Mínimo: {min(multi_times):.2f} ms | Máximo: {max(multi_times):.2f} ms")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmark()

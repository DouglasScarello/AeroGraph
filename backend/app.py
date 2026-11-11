import os
from typing import List, Literal
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from core.graph import build_graph, get_airport_info
from core.dijkstra import find_best_route
from core.exceptions import AirportNotFoundError, NoRouteFoundError
from backend.schemas import AirportSchema, RouteResponse, ErrorResponse

app = FastAPI(
    title="AirCrazyScarello API",
    description="API de alta performance para roteamento inteligente de voos com Algoritmo de Dijkstra e Grafos Direcionados.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caminhos dos datasets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AIRPORTS_FILE = os.path.join(BASE_DIR, "data", "airports.csv")
FLIGHTS_FILE = os.path.join(BASE_DIR, "data", "flights.csv")

# Inicialização do grafo em memória
G = build_graph(AIRPORTS_FILE, FLIGHTS_FILE)


@app.get(
    "/",
    summary="Status da API",
    description="Retorna status e resumo dos aeroportos carregados no sistema."
)
def home():
    return {
        "status": "online",
        "message": "Welcome to AirCrazyScarello Route Engine",
        "total_airports": len(G.nodes),
        "total_flights": len(G.edges),
        "available_airports": sorted(list(G.nodes))
    }


@app.get(
    "/airports",
    response_model=List[AirportSchema],
    summary="Listar aeroportos",
    description="Retorna a lista completa de todos os aeroportos cadastrados na malha aérea."
)
def list_airports():
    airports = []
    for code in sorted(G.nodes):
        info = get_airport_info(G, code)
        if info:
            airports.append(info)
    return airports


@app.get(
    "/airports/{iata}",
    response_model=AirportSchema,
    responses={404: {"model": ErrorResponse}},
    summary="Consultar aeroporto específico",
    description="Busca os detalhes de um aeroporto a partir do seu código IATA."
)
def get_airport(iata: str):
    code = iata.strip().upper()
    info = get_airport_info(G, code)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aeroporto '{code}' não encontrado na base de dados."
        )
    return info


@app.get(
    "/search",
    response_model=RouteResponse,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse}
    },
    summary="Calcular melhor rota de voo",
    description="Calcula a rota ótima entre origem e destino utilizando o algoritmo de Dijkstra com critério por menor preço ou menor tempo de voo."
)
def search_route(
    origin: str = Query(..., description="Código IATA de origem (ex: GRU)", min_length=3, max_length=3),
    destination: str = Query(..., description="Código IATA de destino (ex: LHR)", min_length=3, max_length=3),
    criteria: Literal["price", "duration"] = Query("price", description="Critério de otimização: 'price' para menor custo ou 'duration' para menor tempo")
):
    try:
        route = find_best_route(G, origin, destination, criteria=criteria)
        return route
    except AirportNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except NoRouteFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no cálculo da rota: {str(e)}"
        )

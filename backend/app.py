import os
from typing import List, Optional, Literal
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from core.graph import build_graph, get_airport_info
from core.dijkstra import find_smart_routes, find_best_route
from core.exceptions import AirportNotFoundError, NoRouteFoundError
from core.live_flights import fetch_real_flight_price
from backend.schemas import AirportSchema, MultiRouteResponse, RouteOption, ErrorResponse

app = FastAPI(
    title="AeroGraph API",
    description="Engine de aviação global com K-Shortest Paths (Yen) e Dijkstra em memória.",
    version="1.0.0"
)

# CORS configurado segundo RFC (sem allow_credentials com wildcard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AIRPORTS_FILE = os.path.join(BASE_DIR, "data", "airports.csv")
FLIGHTS_FILE = os.path.join(BASE_DIR, "data", "flights.csv")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

G = build_graph(AIRPORTS_FILE, FLIGHTS_FILE)


@app.get("/", summary="Interface Web Fullscreen ou Status")
def serve_ui():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "online", "message": "AeroGraph Engine Online"}


@app.get("/api/status", summary="Status da API em JSON")
def api_status():
    return {
        "status": "online",
        "message": "AeroGraph Engine Online",
        "total_airports": len(G.nodes),
        "total_flights": len(G.edges),
        "available_airports": sorted(list(G.nodes))
    }


@app.get("/airports", response_model=List[AirportSchema], summary="Listar aeroportos mundiais")
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
    summary="Consultar aeroporto por IATA"
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
    response_model=MultiRouteResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="Calcular rotas no Grafo"
)
def search_route(
    origin: str = Query(..., description="IATA de origem", min_length=3, max_length=3),
    destination: str = Query(..., description="IATA de destino", min_length=3, max_length=3),
    criteria: Optional[str] = Query("smart", description="Critério de otimização ('smart', 'price', 'duration')")
):
    try:
        routes_data = find_smart_routes(G, origin, destination, criteria=criteria)
        return routes_data
    except AirportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NoRouteFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro no cálculo: {str(e)}")


@app.get(
    "/live-quote",
    responses={404: {"model": ErrorResponse}},
    summary="Consultar Cotação Real no Google Flights (PoC experimental)"
)
def live_quote(
    origin: str = Query(..., description="IATA de origem", min_length=3, max_length=3),
    destination: str = Query(..., description="IATA de destino", min_length=3, max_length=3),
    currency: str = Query("BRL", description="Moeda (BRL, USD, EUR, GBP)")
):
    data = fetch_real_flight_price(origin, destination, currency=currency)
    if not data or "error" in data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=data.get("error") if data else "Nenhum voo retornado pelo Google Flights para a data."
        )
    return data

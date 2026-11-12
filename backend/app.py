import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from core.graph import build_graph, get_airport_info
from core.dijkstra import find_smart_routes
from core.exceptions import AirportNotFoundError, NoRouteFoundError
from core.live_flights import fetch_real_flight_price
from backend.schemas import AirportSchema, MultiRouteResponse, ErrorResponse

app = FastAPI(
    title="AeroGraph API",
    description="Engine inteligente de aviação global com Dijkstra + Cotação Real no Google Flights sem cadastro.",
    version="3.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AIRPORTS_FILE = os.path.join(BASE_DIR, "data", "airports.csv")
FLIGHTS_FILE = os.path.join(BASE_DIR, "data", "flights.csv")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Inicialização do grafo em memória
G = build_graph(AIRPORTS_FILE, FLIGHTS_FILE)


@app.get("/", summary="Interface Web Fullscreen")
def serve_ui():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "online", "message": "AeroGraph Engine Online"}


@app.get("/airports", response_model=List[AirportSchema], summary="Listar aeroportos mundiais")
def list_airports():
    airports = []
    for code in sorted(G.nodes):
        info = get_airport_info(G, code)
        if info:
            airports.append(info)
    return airports


@app.get("/search", response_model=MultiRouteResponse, summary="Calcular rotas inteligentes no Grafo")
def search_route(
    origin: str = Query(..., description="IATA de origem", min_length=3, max_length=3),
    destination: str = Query(..., description="IATA de destino", min_length=3, max_length=3)
):
    try:
        routes_data = find_smart_routes(G, origin, destination)
        return routes_data
    except AirportNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NoRouteFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro no cálculo: {str(e)}")


@app.get("/live-quote", summary="Consultar Cotação Real no Google Flights (Sem Chave/Sem Cadastro)")
def live_quote(
    origin: str = Query(..., description="IATA de origem", min_length=3, max_length=3),
    destination: str = Query(..., description="IATA de destino", min_length=3, max_length=3),
    currency: str = Query("BRL", description="Moeda (BRL, USD, EUR, GBP)")
):
    data = fetch_real_flight_price(origin, destination, currency=currency)
    if not data or "error" in data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=data.get("error") if data else "Nenhum voo comercial direto ou com conexões retornado pelo Google Flights para a data."
        )
    return data

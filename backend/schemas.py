from pydantic import BaseModel, Field
from typing import List, Optional

class AirportSchema(BaseModel):
    iata: str = Field(..., description="Código IATA de 3 letras do aeroporto", example="GRU")
    city: str = Field(..., description="Cidade onde o aeroporto está localizado", example="Sao Paulo")
    country: str = Field(..., description="País do aeroporto", example="Brazil")
    lat: float = Field(0.0, description="Latitude geográfica", example=-23.4356)
    lon: float = Field(0.0, description="Longitude geográfica", example=-46.4731)

class SegmentSchema(BaseModel):
    from_airport: str = Field(..., example="GRU")
    to_airport: str = Field(..., example="MIA")
    price: int = Field(..., description="Preço do trecho em USD", example=650)
    duration: int = Field(..., description="Duração estimada do voo em horas", example=9)
    from_lat: float = Field(0.0, example=-23.4356)
    from_lon: float = Field(0.0, example=-46.4731)
    to_lat: float = Field(0.0, example=25.7959)
    to_lon: float = Field(0.0, example=-80.2870)

class RouteOption(BaseModel):
    rank: int = Field(..., description="Posição no ranking", example=1)
    label: str = Field(..., description="Rótulo da rota", example="Mais Econômica")
    badge: Optional[str] = Field("Opção", description="Selo inteligente", example="💰 Mais Barata")
    path: List[str] = Field(..., description="Sequência ordenada de aeroportos", example=["GRU", "LHR"])
    segments: List[SegmentSchema] = Field(..., description="Detalhamento individual de cada voo")
    total_price: int = Field(..., description="Valor total da rota em USD", example=887)
    total_duration: int = Field(..., description="Tempo total de voo em horas", example=12)
    stops: int = Field(..., description="Quantidade de escalas", example=0)
    flight_duration: Optional[int] = Field(0, description="Tempo de voo no ar")
    layover_hours: Optional[int] = Field(0, description="Tempo de espera em conexões")

class MultiRouteResponse(BaseModel):
    origin: str = Field(..., example="GRU")
    destination: str = Field(..., example="LHR")
    criteria: Optional[str] = Field("smart", description="Critério de otimização selecionado")
    total_found: int = Field(..., description="Quantidade de alternativas calculadas", example=3)
    routes: List[RouteOption] = Field(..., description="As rotas ordenadas pelo critério")

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Aeroporto 'XXX' não encontrado na base de dados.")

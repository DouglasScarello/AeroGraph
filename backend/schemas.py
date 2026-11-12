from pydantic import BaseModel, Field
from typing import List, Optional

class AirportSchema(BaseModel):
    iata: str = Field(..., description="Código IATA de 3 letras do aeroporto")
    city: str = Field(..., description="Cidade onde o aeroporto está localizado")
    country: str = Field(..., description="País do aeroporto")
    lat: float = Field(0.0, description="Latitude geográfica")
    lon: float = Field(0.0, description="Longitude geográfica")

class SegmentSchema(BaseModel):
    from_airport: str = Field(...)
    to_airport: str = Field(...)
    price: int = Field(..., description="Preço do trecho em USD")
    duration: int = Field(..., description="Duração estimada do voo em horas")
    from_lat: float = Field(0.0)
    from_lon: float = Field(0.0)
    to_lat: float = Field(0.0)
    to_lon: float = Field(0.0)
    distance_km: float = Field(0.0, description="Distância real ortodrômica em km (Haversine)")

class RouteOption(BaseModel):
    rank: int = Field(..., description="Posição no ranking")
    label: str = Field(..., description="Rótulo da rota")
    badge: Optional[str] = Field("Opção", description="Selo inteligente")
    path: List[str] = Field(..., description="Sequência ordenada de aeroportos")
    segments: List[SegmentSchema] = Field(..., description="Detalhamento individual de cada voo")
    total_price: int = Field(..., description="Valor total da rota em USD")
    total_duration: int = Field(..., description="Tempo total de viagem em horas incluindo conexões")
    flight_duration: Optional[int] = Field(0, description="Tempo real de voo no ar")
    layover_hours: Optional[int] = Field(0, description="Tempo de espera em conexões")
    stops: int = Field(..., description="Quantidade de escalas")

class MultiRouteResponse(BaseModel):
    origin: str = Field(...)
    destination: str = Field(...)
    criteria: Optional[str] = Field("smart", description="Critério de otimização selecionado")
    total_found: int = Field(..., description="Quantidade de alternativas calculadas")
    routes: List[RouteOption] = Field(..., description="As rotas ordenadas pelo critério")

class ErrorResponse(BaseModel):
    detail: str = Field(...)

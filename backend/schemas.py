from pydantic import BaseModel, Field
from typing import List, Literal

class AirportSchema(BaseModel):
    iata: str = Field(..., description="Código IATA de 3 letras do aeroporto", example="GRU")
    city: str = Field(..., description="Cidade onde o aeroporto está localizado", example="Sao Paulo")
    country: str = Field(..., description="País do aeroporto", example="Brazil")

class SegmentSchema(BaseModel):
    from_airport: str = Field(..., example="GRU")
    to_airport: str = Field(..., example="MIA")
    price: int = Field(..., description="Preço do trecho em USD", example=650)
    duration: int = Field(..., description="Duração estimada do voo em horas", example=9)

class RouteResponse(BaseModel):
    origin: str = Field(..., example="GRU")
    destination: str = Field(..., example="LHR")
    criteria: Literal["price", "duration"] = Field("price", description="Critério de otimização selecionado")
    path: List[str] = Field(..., description="Sequência ordenada de aeroportos da rota", example=["GRU", "MIA", "JFK", "LHR"])
    segments: List[SegmentSchema] = Field(..., description="Detalhamento individual de cada voo da conexão")
    total_price: int = Field(..., description="Valor total da rota em USD", example=1350)
    total_duration: int = Field(..., description="Tempo total de voo em horas", example=19)
    stops: int = Field(..., description="Quantidade de escalas na rota", example=2)

class ErrorResponse(BaseModel):
    detail: str = Field(..., example="Aeroporto 'XXX' não encontrado na base de dados.")

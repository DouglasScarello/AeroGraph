class AirportNotFoundError(Exception):
    """Levantada quando um código IATA não existe no grafo."""

    def __init__(self, airport_code: str):
        self.airport_code = airport_code
        super().__init__(f"Aeroporto '{airport_code}' não encontrado na base de dados.")


class NoRouteFoundError(Exception):
    """Levantada quando não existe caminho entre dois aeroportos."""

    def __init__(self, origin: str, destination: str):
        self.origin = origin
        self.destination = destination
        super().__init__(
            f"Não existe rota disponível de '{origin}' para '{destination}'."
        )

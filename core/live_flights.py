from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fast_flights import FlightQuery, Passengers, create_query, get_flights

def fetch_real_flight_price(origin: str, destination: str, currency: str = "BRL") -> Optional[Dict[str, Any]]:
    """
    Consulta o Google Flights em tempo real via engenharia reversa de Protobuf (fast-flights).
    Zero necessidade de chave de API ou cadastro de cartão.
    """
    origin = origin.upper().strip()
    destination = destination.upper().strip()

    # Data padrão: 20 dias a partir de hoje
    target_date = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")

    try:
        query = create_query(
            flights=[FlightQuery(date=target_date, from_airport=origin, to_airport=destination)],
            seat="economy",
            trip="one-way",
            passengers=Passengers(adults=1),
            currency=currency
        )
        res = get_flights(query)

        if not res or len(res) == 0:
            return None

        best = res[0]
        airline_name = best.airlines[0] if best.airlines else "Companhia Aérea"

        return {
            "source": "Google Flights (Live)",
            "date": target_date,
            "origin": origin,
            "destination": destination,
            "currency": currency,
            "price": best.price,
            "airline": airline_name,
            "stops": len(best.flights) - 1 if best.flights else 0,
            "total_options_found": len(res)
        }
    except Exception as e:
        return {"error": str(e)}

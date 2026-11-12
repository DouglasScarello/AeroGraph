import pytest
from core.dijkstra import find_best_route, find_smart_routes
from core.graph import build_graph
from core.exceptions import AirportNotFoundError, NoRouteFoundError

@pytest.fixture(scope="module")
def graph():
    return build_graph("data/airports.csv", "data/flights.csv")

def test_find_route_cheapest_by_price(graph):
    result = find_best_route(graph, "GRU", "LHR", criteria="price")
    assert result["origin"] == "GRU"
    assert result["destination"] == "LHR"
    assert result["criteria"] == "price"
    assert result["path"][0] == "GRU"
    assert result["path"][-1] == "LHR"
    assert result["total_price"] > 0
    assert result["total_duration"] > 0
    assert len(result["segments"]) == len(result["path"]) - 1
    assert "distance_km" in result["segments"][0]

def test_find_route_by_duration(graph):
    result_price = find_best_route(graph, "FLN", "NRT", criteria="price")
    result_duration = find_best_route(graph, "FLN", "NRT", criteria="duration")
    assert result_duration["flight_duration"] <= result_price["flight_duration"]

def test_same_origin_and_destination(graph):
    result = find_best_route(graph, "GRU", "GRU")
    assert result["path"] == ["GRU"]
    assert result["total_price"] == 0
    assert result["total_duration"] == 0
    assert result["stops"] == 0

def test_find_smart_routes_multi(graph):
    res = find_smart_routes(graph, "FLN", "GIG")
    assert res["origin"] == "FLN"
    assert res["destination"] == "GIG"
    assert res["total_found"] >= 1
    assert len(res["routes"]) >= 1
    assert res["routes"][0]["total_price"] > 0

def test_invalid_origin_raises_error(graph):
    with pytest.raises(AirportNotFoundError):
        find_best_route(graph, "INVALID", "LHR")

def test_invalid_destination_raises_error(graph):
    with pytest.raises(AirportNotFoundError):
        find_best_route(graph, "GRU", "INVALID")

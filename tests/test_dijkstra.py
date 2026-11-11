import pytest
import networkx as nx
from core.dijkstra import find_best_route
from core.graph import build_graph
from core.exceptions import AirportNotFoundError, NoRouteFoundError

@pytest.fixture
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

def test_find_route_by_duration(graph):
    result_price = find_best_route(graph, "GRU", "FRA", criteria="price")
    result_duration = find_best_route(graph, "GRU", "FRA", criteria="duration")
    
    # As durações devem ser coerentes e otimizadas
    assert result_duration["total_duration"] <= result_price["total_duration"]

def test_same_origin_and_destination(graph):
    result = find_best_route(graph, "GRU", "GRU")
    assert result["path"] == ["GRU"]
    assert result["total_price"] == 0
    assert result["total_duration"] == 0
    assert result["stops"] == 0

def test_invalid_origin_raises_error(graph):
    with pytest.raises(AirportNotFoundError):
        find_best_route(graph, "INVALID", "LHR")

def test_invalid_destination_raises_error(graph):
    with pytest.raises(AirportNotFoundError):
        find_best_route(graph, "GRU", "INVALID")

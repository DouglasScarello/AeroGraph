import pytest
from fastapi.testclient import TestClient
import sys
import os

# Adiciona caminhos para importação
sys.path.insert(0, os.path.abspath("."))
from backend.app import app

client = TestClient(app)

def test_home_status():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["total_airports"] >= 10
    assert "GRU" in data["available_airports"]

def test_list_airports():
    response = client.get("/airports")
    assert response.status_code == 200
    airports = response.json()
    assert len(airports) >= 10
    assert any(a["iata"] == "GRU" for a in airports)

def test_get_valid_airport():
    response = client.get("/airports/GRU")
    assert response.status_code == 200
    data = response.json()
    assert data["iata"] == "GRU"
    assert data["city"] == "Sao Paulo"
    assert data["country"] == "Brazil"

def test_get_invalid_airport_404():
    response = client.get("/airports/XYZ")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]

def test_search_valid_route_price():
    response = client.get("/search?origin=GRU&destination=LHR&criteria=price")
    assert response.status_code == 200
    data = response.json()
    assert data["origin"] == "GRU"
    assert data["destination"] == "LHR"
    assert data["criteria"] == "price"
    assert len(data["path"]) >= 2
    assert len(data["segments"]) > 0

def test_search_valid_route_duration():
    response = client.get("/search?origin=GRU&destination=LHR&criteria=duration")
    assert response.status_code == 200
    data = response.json()
    assert data["criteria"] == "duration"

def test_search_invalid_airport_404():
    response = client.get("/search?origin=GRU&destination=XYZ")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]

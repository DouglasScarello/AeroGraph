import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath("."))
from backend.app import app

client = TestClient(app)

def test_home_status_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

def test_api_status_json():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["total_airports"] >= 3000
    assert "GRU" in data["available_airports"]

def test_list_airports():
    response = client.get("/airports")
    assert response.status_code == 200
    airports = response.json()
    assert len(airports) >= 3000
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

def test_search_valid_route_multi():
    response = client.get("/search?origin=FLN&destination=GIG&criteria=price")
    assert response.status_code == 200
    data = response.json()
    assert data["origin"] == "FLN"
    assert data["destination"] == "GIG"
    assert data["total_found"] >= 1
    assert len(data["routes"]) >= 1
    first = data["routes"][0]
    assert len(first["path"]) >= 2
    assert len(first["segments"]) > 0

def test_search_invalid_airport_404():
    response = client.get("/search?origin=FLN&destination=XYZ")
    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]

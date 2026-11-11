# ✈️ AirCrazyScarello — Flight Route Optimization Engine

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![NetworkX](https://img.shields.io/badge/NetworkX-Graphs-blue?style=for-the-badge)](https://networkx.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-V2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Pytest](https://img.shields.io/badge/Pytest-Tests_Passing-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

Uma API REST de alta performance desenvolvida em **FastAPI** e **NetworkX**, projetada para resolver o problema clássico de roteamento de menor caminho (**Shortest Path Problem**) em malhas aéreas internacionais utilizando o **Algoritmo de Dijkstra**.

A engine permite calcular trajetos multitrecho otimizados dinamicamente por **menor custo financeiro (preço)** ou **menor tempo de deslocamento (duração)**, retornando conexões detalhadas, paradas intermediárias e métricas completas da viagem.

---

## 🏛️ Teoria da Computação & Arquitetura

O sistema modela a malha de aviação como um **Grafo Direcionado Ponderado (Weighted DiGraph)**:
- **Vértices / Nós ($V$)**: Aeroportos identificados pelo código IATA (ex: `GRU`, `JFK`, `LHR`, `CDG`, `DXB`).
- **Arestas Direcionadas ($E$)**: Trechos de voos comerciais conectando dois aeroportos com pesos independentes:
  - $w_{price}$: Tarifa do trecho em USD ($).
  - $w_{duration}$: Duração estimada do voo em horas ($h$).

```mermaid
flowchart LR
    GRU((GRU - SP)) -->|"$650 / 9h"| MIA((MIA - Miami))
    GRU -->|"$800 / 10h"| JFK((JFK - NY))
    GRU -->|"$850 / 11h"| CDG((CDG - Paris))
    GRU -->|"$250 / 3h"| EZE((EZE - Buenos Aires))
    
    MIA -->|"$180 / 3h"| JFK
    JFK -->|"$500 / 7h"| LHR((LHR - Londres))
    JFK -->|"$600 / 8h"| FRA((FRA - Frankfurt))
    
    CDG -->|"$130 / 1h"| LHR
    CDG -->|"$100 / 1h"| FRA
    CDG -->|"$1200 / 22h"| SYD((SYD - Sydney))
    
    FRA -->|"$450 / 6h"| DXB((DXB - Dubai))
    DXB -->|"$550 / 9h"| NRT((NRT - Tóquio))
    DXB -->|"$900 / 14h"| SYD
    NRT -->|"$700 / 10h"| SYD
```

### 🧠 Como Funciona o Algoritmo de Dijkstra

Dado um aeroporto de origem $s \in V$ e um destino $t \in V$, o algoritmo mantém uma estimativa de menor distância para cada nó e expande iterativamente o vértice de menor peso acumulado ainda não visitado (usando uma fila de prioridade / heap):

$$\operatorname{dist}[v] = \min(\operatorname{dist}[v], \operatorname{dist}[u] + w(u, v))$$

* Ao selecionar o critério `price`, a função custo minimiza $\sum w_{price}$.
* Ao selecionar o critério `duration`, a função custo minimiza $\sum w_{duration}$.

---

## 🔄 Fluxo de Execução da API

```mermaid
sequenceDiagram
    autonumber
    actor Client as Cliente / Frontend
    participant API as FastAPI Gateway (/search)
    participant Validator as Pydantic Schemas
    participant Engine as Dijkstra Engine (core.dijkstra)
    participant Graph as NetworkX DiGraph

    Client->>API: GET /search?origin=GRU&destination=LHR&criteria=price
    API->>Validator: Valida query params (IATA 3 letras)
    Validator-->>API: Parâmetros validados
    API->>Engine: find_best_route(G, origin="GRU", destination="LHR", criteria="price")
    Engine->>Graph: nx.dijkstra_path(G, weight="price")
    Graph-->>Engine: Path ótimo: ['GRU', 'CDG', 'LHR']
    Engine->>Graph: Extrai pesos de cada aresta (preço + duração)
    Engine-->>API: Retorna payload consolidado com segmentos
    API-->>Client: 200 OK + RouteResponse JSON
```

---

## ⚡ Exemplos de Uso

### 1. Consultar a melhor rota (GRU ➔ LHR por menor preço)
```bash
curl -X GET "http://127.0.0.1:8000/search?origin=GRU&destination=LHR&criteria=price"
```

**Resposta JSON (200 OK):**
```json
{
  "origin": "GRU",
  "destination": "LHR",
  "criteria": "price",
  "path": ["GRU", "CDG", "LHR"],
  "segments": [
    {
      "from_airport": "GRU",
      "to_airport": "CDG",
      "price": 850,
      "duration": 11
    },
    {
      "from_airport": "CDG",
      "to_airport": "LHR",
      "price": 130,
      "duration": 1
    }
  ],
  "total_price": 980,
  "total_duration": 12,
  "stops": 1
}
```

### 2. Consultar detalhes de um aeroporto
```bash
curl -X GET "http://127.0.0.1:8000/airports/GRU"
```
```json
{
  "iata": "GRU",
  "city": "Sao Paulo",
  "country": "Brazil"
}
```

---

## 🚀 Como Executar Localmente

### Pré-requisitos
* Python 3.10+
* Git

### 1. Clonar o repositório:
```bash
git clone https://github.com/DouglasScarello/AirCrazyScarello.git
cd AirCrazyScarello
```

### 2. Criar e ativar o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

### 3. Instalar dependências:
```bash
pip install -r requirements.txt
```

### 4. Iniciar a API:
```bash
uvicorn backend.app:app --reload
```
* **Swagger interativo (OpenAPI):** http://127.0.0.1:8000/docs
* **ReDoc alternativo:** http://127.0.0.1:8000/redoc

---

## 🧪 Executando os Testes Automatizados

O projeto conta com testes unitários do algoritmo e testes de integração de todos os endpoints HTTP:

```bash
pytest -v
```

---

## 📁 Estrutura do Repositório

```text
AirCrazyScarello/
├── backend/
│   ├── __init__.py           # Package marker
│   ├── app.py                # Rotas da API, middleware CORS e tratamento de exceções
│   └── schemas.py            # Modelos de dados e validação estrita com Pydantic V2
├── core/
│   ├── __init__.py           # Package marker
│   ├── dijkstra.py           # Algoritmo de Dijkstra com suporte a múltiplos critérios
│   ├── exceptions.py         # Exceções customizadas de domínio (404, NoRouteFound)
│   └── graph.py              # Parser de CSVs e construtor do DiGraph com NetworkX
├── data/
│   ├── airports.csv          # Base cadastral de aeroportos (IATA, Cidade, País)
│   └── flights.csv           # Malha de voos com custos e tempos de voo
├── tests/
│   ├── __init__.py
│   ├── test_api.py           # Testes de integração dos endpoints FastAPI
│   └── test_dijkstra.py      # Testes unitários do cálculo de menor caminho
├── .gitignore                # Arquivos ignorados pelo Git
├── requirements.txt          # Dependências do projeto
└── README.md                 # Documentação completa
```

---

## ⚖️ Licença

Distribuído sob a licença **MIT**.

Desenvolvido por **[Douglas Scarello](https://github.com/DouglasScarello)** 🚀

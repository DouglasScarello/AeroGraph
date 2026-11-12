# 🌐 AeroGraph — Global Flight Navigation Engine & Tactical Radar

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![NetworkX](https://img.shields.io/badge/NetworkX-In--Memory_Graph-blue?style=for-the-badge)](https://networkx.org/)
[![Dijkstra & Yen](https://img.shields.io/badge/Algorithm-Dijkstra_%2B_Yen_K--Paths-orange?style=for-the-badge)](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
[![Leaflet](https://img.shields.io/badge/Leaflet-Geodesic_Dark_Radar-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

O **AeroGraph** é uma aplicação prática de **Teoria dos Grafos** e **Algoritmos de Roteamento** construída sobre uma malha histórica de aviação comercial global.

O sistema compila **3.224 aeroportos** e **36.826 rotas** em um **Grafo Direcionado Ponderado (`DiGraph`) em memória RAM**, calculando trajetórias de menor custo via **Algoritmo de Dijkstra** e rotas alternativas via **Algoritmo de Yen ($K$-Shortest Paths)** através da biblioteca **NetworkX**. O projeto conta com uma interface cartográfica fullscreen com **Leaflet**, traçado de arcos geodésicos, conversão multi-moeda no frontend e integração experimental de cotação ao vivo via Google Flights.

---

## 💡 Sobre o Nome e Conceito

> **AeroGraph** une **Aeronáutica** e **Teoria dos Grafos** (*Graph Theory*). 
> O propósito do projeto é acadêmico e de engenharia de software: demonstrar na prática a modelagem de malhas de transporte como grafos ponderados, a exploração de múltiplos caminhos mínimos e a construção de uma camada de API e visualização geoespacial responsiva.

---

## 🏛️ Modelagem Matemática e Algoritmos

### 1. Grafo Direcionado Ponderado $G = (V, E)$
* **Vértices ($V$):** $3.224$ aeroportos com código IATA, cidade, país e coordenadas geográficas $(\phi, \lambda)$.
* **Arestas Direcionadas ($E$):** $36.826$ conexões de voo registradas entre pares de aeroportos.
* **Pesos Não-Negativos:** Cada aresta possui pesos estritamente positivos ($w(u, v) > 0$): `price` (USD) e `duration` (horas).
  * *Rigor Teórico:* A ausência de **arestas negativas** é a precondição matemática para o **Algoritmo de Dijkstra**. Como o algoritmo marca os vértices como visitados de forma gulosa ao retirá-los do Min-Heap, uma aresta negativa invalidaria a garantia de otimalidade por indução. (Grafos com arestas negativas exigiriam Bellman-Ford ou Johnson).

### 2. Algoritmo de Dijkstra & Complexidade
Calcula o caminho de custo mínimo entre a origem $s$ e o destino $t$:
$$\operatorname{dist}[v] = \min(\operatorname{dist}[v], \operatorname{dist}[u] + w(u, v))$$
* **Implementação:** Utiliza `nx.dijkstra_path` do NetworkX, implementado em Python sobre a estrutura `heapq` (Min-Heap binário).
* **Complexidade Assintótica de Tempo:** $O((|V| + |E|) \log |V|)$ com listas de adjacência e fila de prioridade binária.
* **Complexidade de Espaço:** $O(|V| + |E|)$ em memória RAM.

### 3. $K$-Caminhos Mínimos sem Loops (Algoritmo de Yen / NetworkX)
Para fornecer trajetos alternativos, o sistema utiliza `nx.shortest_simple_paths` do NetworkX, que implementa uma variante otimizada do **Algoritmo de Yen (1971)** com busca de caminhos simples sem repetição de ciclos:
* A primeira rota $A_1$ é o caminho ótimo retornado pelo Dijkstra.
* Para cada rota subsequente $A_k$, o algoritmo itera sobre cada vértice do caminho anterior $A_{k-1}$ atuando como **nó de espora (*spur node*)**:
  1. Fixa a raiz (*root path*) da origem até o nó de espora.
  2. Remove temporariamente as arestas já percorridas que partem do nó de espora para impedir caminhos duplicados.
  3. Executa um novo Dijkstra a partir do nó de espora até o destino (*spur path*).
  4. Adiciona o candidato concatenado a uma fila de prioridade.
* **Custo Computacional:** Como executa múltiplos Dijkstras a cada nó de espora avaliado, o custo é na ordem de $O(K \cdot |V| \cdot (|E| + |V| \log |V|))$, o que explica o tempo de execução superior ao de uma busca direta.

### 4. Distâncias Geodésicas e Pós-Processamento (Fórmula de Haversine)
A distância ortodrômica real sobre a esfera terrestre ($R = 6.371\text{ km}$) é implementada em Python puro no módulo [`core/haversine.py`](core/haversine.py):
$$\Delta\sigma = 2 \arcsin \sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}, \quad d = R \cdot \Delta\sigma$$

* **Transparência de Uso:** O Haversine **não é o peso do grafo em tempo de execução**, mas sim uma função de **pós-processamento**. Quando o Dijkstra encontra a rota, o AeroGraph calcula a quilometragem geodésica exata de cada segmento (`distance_km`) para enriquecer os metadados da API e orientar a curvatura dos arcos no mapa.

---

## 📊 Benchmark Real de Performance

Medições empíricas reais obtidas diretamente na máquina local via script [`benchmark.py`](benchmark.py), com **aquecimento de cache (*warmup*)** e **múltiplas iterações** (10 execuções para Dijkstra simples, 5 para o Yen $K=3$):

| Rota | Tipo de Trajeto | Dijkstra Único (Média ± Desv. Padrão) | Yen K=3 (Média ± Desv. Padrão) |
| :--- | :--- | :---: | :---: |
| **FLN ➔ GIG** | Doméstico Curto (Brasil) | **0.09 ms** (±0.03 ms) | **1.23 ms** (±0.37 ms) |
| **GRU ➔ LHR** | Transatlântico Direto | **4.04 ms** (±0.54 ms) | **46.83 ms** (±2.98 ms) |
| **FLN ➔ NRT** | Transpacífico Múltiplas Escalas | **13.68 ms** (±0.75 ms) | **107.50 ms** (±3.86 ms) |
| **JFK ➔ SYD** | América do Norte ➔ Oceania | **15.43 ms** (±2.40 ms) | **92.82 ms** (±2.44 ms) |
| **CDG ➔ HND** | Europa ➔ Ásia | **14.24 ms** (±11.28 ms) | **82.25 ms** (±1.27 ms) |
| **FLN ➔ ALH** | Intercontinental Hemisfério Sul | **12.10 ms** (±0.55 ms) | **102.99 ms** (±0.90 ms) |

* **Tempo de Carga do Grafo na Memória:** ~1.2 segundos na inicialização (3.224 nós e 36.826 arestas indexados).
* **Média Global Dijkstra Único:** **~9.9 ms** (rotas curtas diretas respondem em frações de milissegundo).
* **Média Global Yen (3 alternativas):** **~72.3 ms** (refletindo o custo de rodar múltiplos Dijkstras por nó de espora).

---

## 📑 Transparência de Dados, Heurísticas e Limitações

1. **Origem dos Dados Geográficos e Malha:**
   * Aeroportos e rotas foram obtidos da base pública da **[OpenFlights](https://openflights.org/data.html)** (dados históricos compilados até meados de 2014, sob licença *Open Database License - ODbL*).
   * As rotas representam conexões existentes na época do dataset.
2. **Modelagem dos Pesos no Arquivo `flights.csv`:**
   * A OpenFlights fornece a topologia (quais aeroportos se conectam), mas não tarifas dinâmicas de companhias aéreas. Os valores de `price` e `duration` em `data/flights.csv` foram sintetizados através de uma **heurística paramétrica determinística baseada na distância**:
     $$\text{Duração Estimada (h)} \approx \max\left(1, \operatorname{round}\left(\frac{d_{\text{km}}}{800} + 0.5\right)\right)$$
     $$\text{Tarifa Paramétrica (USD)} \approx 55 + (d_{\text{km}} \times 0.088)$$
   * **Limitação Estrutural (Colinearidade):** Como tanto preço quanto duração foram derivados da distância $d_{\text{km}}$, as duas métricas são fortemente colineares no arquivo estático. Por isso, para cerca de 80% das rotas diretas, a rota "Mais Barata" calculada pelo Dijkstra é numericamente idêntica à "Mais Rápida".
   * **Penalidade de Conexão em Solo:** Para aproximar o tempo total da realidade de voos com escalas, adicionamos em código uma penalidade de tempo de conexão (`LAYOVER_HOURS_PER_STOP = 2` horas por parada) no cálculo do tempo total de viagem.
3. **Módulo Experimental de Cotação ao Vivo (`core/live_flights.py`):**
   * Utiliza a biblioteca open-source `fast-flights` para consultar tarifas comerciais reais no Google Flights via engenharia reversa de payloads Protobuf.
   * *Aviso de Engenharia:* Trata-se de uma Prova de Conceito (PoC) dependente de chamadas não oficiais do Google Flights, sujeita a instabilidade ou alterações de contrato por parte do provedor.
4. **Conversão de Moedas no Frontend:**
   * As taxas de câmbio disponíveis no radar (BRL, USD, EUR, GBP) utilizam multiplicadores fixos no JavaScript (`index.html`) para conversão cosmética imediata na interface, sem requisições a APIs externas de cotação cambial em tempo real.

---

## 🗺️ Interface Cartográfica (Frontend)

* **Biblioteca:** Leaflet.js com clusterização via `leaflet.markercluster` (capaz de renderizar os 3.224 aeroportos simultaneamente sem travar o navegador).
* **Estilização Visual:** Tiles oficiais do OpenStreetMap com filtro CSS de alto contraste (*Dark Mode* / estética tática).
* **Arcos Geodésicos:** Curvas quadráticas de Bézier (`L.curve`) com correção de continuidade no **antimeridiano** (meridiano 180° / -180°), impedindo que trajetos transpacíficos cortem o mapa na contramão.
* **Telemetria e Controle de Concorrência:**
  * Uso de `AbortController` nativo para cancelar requisições pendentes se o usuário alterar a busca rapidamente.
  * Medição de latência real de ida e volta da requisição via `performance.now()`, exibida dinamicamente no rodapé do painel.

---

## 🚀 Como Executar Localmente

### Pré-requisitos
* **Python 3.10+**
* **Git**

### Passo a Passo

1. **Clonar o repositório:**
   ```bash
   git clone https://github.com/DouglasScarello/AeroGraph.git
   cd AeroGraph
   ```

2. **Criar e ativar o ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate   # Windows
   ```

3. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar o benchmark oficial:**
   ```bash
   python benchmark.py
   ```

5. **Iniciar o servidor:**
   ```bash
   uvicorn backend.app:app --host 0.0.0.0 --port 8008 --reload
   ```

6. **Acessar no navegador:**
   * **Radar Tático Fullscreen:** [http://127.0.0.1:8008/](http://127.0.0.1:8008/)
   * **Documentação Interativa Swagger:** [http://127.0.0.1:8008/docs](http://127.0.0.1:8008/docs)

---

## 🧪 Testes Automatizados

A suíte de testes cobre regras de domínio, contratos da API FastAPI e cenários de borda (mesma origem e destino, nós desconhecidos, rotas diretas e com conexões):

```bash
pytest -v
```

---

## 📁 Estrutura do Repositório

```text
AeroGraph/
├── backend/
│   ├── app.py                # Rotas REST e inicialização da API FastAPI
│   └── schemas.py            # Validação e serialização com Pydantic V2
├── core/
│   ├── dijkstra.py           # Algoritmos de Dijkstra e Yen (K-Shortest Paths via NetworkX)
│   ├── exceptions.py         # Exceções de domínio (AirportNotFoundError, NoRouteFoundError)
│   ├── graph.py              # Construtor do Grafo em memória com NetworkX
│   ├── haversine.py          # Cálculo de distância ortodrômica em Python puro
│   └── live_flights.py       # Extração experimental de tarifas (Google Flights Protobuf)
├── data/
│   ├── airports.csv          # 3.224 aeroportos com coordenadas geográficas (ODbL / OpenFlights)
│   └── flights.csv           # 36.826 rotas com pesos paramétricos
├── frontend/
│   └── index.html            # Interface fullscreen com Leaflet Dark, telemetria real e autocomplete
├── tests/
│   ├── test_api.py           # Testes de integração dos endpoints FastAPI
│   └── test_dijkstra.py      # Testes unitários do cálculo de menor caminho
├── benchmark.py              # Medição empírica de latência (N=10 + Warmup)
├── requirements.txt          # Dependências do projeto
├── LICENSE                   # Licença MIT
└── README.md                 # Documentação técnica e acadêmica do projeto
```

---

## ⚖️ Licenças e Atribuição

* O código-fonte deste projeto é distribuído sob a licença **MIT** ([LICENSE](LICENSE)).
* A malha de aeroportos e rotas contida no diretório `data/` é derivada da base de dados pública **[OpenFlights](https://openflights.org/data.html)**, disponibilizada sob a licença **Open Database License (ODbL)**.
* Map tiles fornecidos por **[OpenStreetMap](https://www.openstreetmap.org/copyright)** sob licença CC-BY-SA.

Desenvolvido por **[Douglas Scarello](https://github.com/DouglasScarello)** 🚀

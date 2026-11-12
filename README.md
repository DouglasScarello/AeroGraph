# 🌐 AeroGraph — Global Flight Navigation Engine & Tactical Radar

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![NetworkX](https://img.shields.io/badge/NetworkX-In--Memory_Graph-blue?style=for-the-badge)](https://networkx.org/)
[![Dijkstra & Yen](https://img.shields.io/badge/Algorithm-Dijkstra_%2B_Yen_K--Paths-orange?style=for-the-badge)](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
[![Leaflet](https://img.shields.io/badge/Leaflet-Geodesic_Dark_Radar-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

O **AeroGraph** é uma aplicação prática de **Teoria dos Grafos** e **Algoritmos de Roteamento** aplicada a uma malha histórica de aviação comercial global.

O sistema compila **3.224 aeroportos** e **36.826 rotas** em um **Grafo Direcionado Ponderado (`DiGraph`) em memória RAM**, calculando trajetórias de menor custo via **Algoritmo de Dijkstra** e rotas alternativas via **Algoritmo de Yen ($K$-Shortest Paths)**. O projeto inclui um **Radar Cartográfico Geodésico Fullscreen** (Leaflet Dark / GTA Style) com traçado de arcos de grande círculo, suporte a múltiplas moedas e um módulo experimental para consulta sob demanda no Google Flights.

---

## 💡 Sobre o Nome e Conceito

> **AeroGraph** surge da união entre **Aeronáutica** e **Teoria dos Grafos** (*Graph Theory*). 
> O objetivo do projeto é demonstrar como problemas de logística aérea podem ser modelados e resolvidos de forma determinística utilizando estruturas de dados em memória e algoritmos clássicos de menor caminho, servindo como base de estudo e portfólio de engenharia de software.

---

## 🏛️ Modelagem Matemática e Algoritmos

### 1. Grafo Direcionado Ponderado $G = (V, E)$
* **Vértices ($V$):** $3.224$ aeroportos com código IATA e coordenadas geográficas $(\phi, \lambda)$.
* **Arestas Direcionadas ($E$):** $36.826$ conexões de voo entre pares de aeroportos.
* **Precondição de Não-Negatividade:** Todos os pesos atribuídos às arestas são estritamente positivos ($w(u, v) > 0$).
  * *Rigor Teórico:* A ausência de **arestas negativas** é a precondição essencial para a corretude do **Algoritmo de Dijkstra**. Como o algoritmo marca os nós como visitados de maneira gulosa assim que são desempilhados do Min-Heap, uma aresta negativa poderia reduzir o custo acumulado de um caminho já finalizado, o que invalidaria a prova por indução de Dijkstra. (Para grafos com pesos negativos, seriam necessários algoritmos como Bellman-Ford ou Johnson).

### 2. Algoritmo de Dijkstra & Complexidade
Dado o vértice de origem $s \in V$, o algoritmo mantém a estimativa de menor distância com Min-Heap:
$$\operatorname{dist}[v] = \min(\operatorname{dist}[v], \operatorname{dist}[u] + w(u, v))$$
* **Complexidade Assintótica de Tempo:** $O((|V| + |E|) \log |V|)$ com representação de lista de adjacências e fila de prioridade binária.
* **Complexidade de Espaço:** $O(|V| + |E|)$ em memória RAM.

### 3. K-Caminhos Mínimos sem Loops (Algoritmo de Yen)
O sistema utiliza a implementação do NetworkX (`nx.shortest_simple_paths`), baseada no **Algoritmo de Yen (1971)**:
* A primeira rota $A_1$ é a rota ótima computada pelo Dijkstra.
* Para cada rota subsequente $A_k$, o algoritmo itera sobre cada vértice do caminho anterior $A_{k-1}$ atuando como **nó de espora (*spur node*)**:
  1. O trecho da origem até o nó de espora é fixado como caminho raiz (*root path*).
  2. As arestas já utilizadas em rotas anteriores que saem do nó de espora são temporariamente removidas do grafo para evitar repetição.
  3. Roda-se um novo Dijkstra a partir do nó de espora até o destino para encontrar o caminho de desvio (*spur path*).
  4. O candidato resultante (raiz + desvio) é armazenado em uma fila de prioridade de potenciais rotas.
* **Custo Computacional:** O Yen custa substancialmente mais que um Dijkstra único porque executa múltiplos Dijkstras (na ordem de $O(K \cdot |V| \cdot (|E| + |V| \log |V|))$) para explorar as ramificações sem criar ciclos.

### 4. Distâncias Geodésicas e Pós-Processamento (Fórmula de Haversine)
A distância ortodrômica real entre dois aeroportos $(\phi_1, \lambda_1)$ e $(\phi_2, \lambda_2)$ sobre a esfera terrestre ($R = 6.371\text{ km}$) é computada pelo módulo [`core/haversine.py`](core/haversine.py) durante a montagem do itinerário (`distance_km` por trecho):
$$\Delta\sigma = 2 \arcsin \sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}, \quad d = R \cdot \Delta\sigma$$

*Observação de Modelagem:* No grafo estático atual, as arestas armazenam os pesos discretos `price` e `duration` (derivados da distância geodésica). O cálculo de Haversine em tempo de execução complementa os metadados de cada voo com a quilometragem exata para renderização no mapa e apresentação ao usuário.

---

## 📊 Benchmark Real de Performance

Medições empíricas realizadas via script [`benchmark.py`](benchmark.py) com **fase de aquecimento (*warmup*)** e **múltiplas iterações** (10 execuções para Dijkstra simples, 5 para o Yen):

| Rota | Tipo de Trajeto | Dijkstra Único (Média ± Desv. Padrão) | Yen K=3 (Média ± Desv. Padrão) |
| :--- | :--- | :---: | :---: |
| **FLN ➔ GIG** | Doméstico Curto (Brasil) | **0.09 ms** (±0.03 ms) | **1.23 ms** (±0.37 ms) |
| **GRU ➔ LHR** | Transatlântico Direto | **4.04 ms** (±0.54 ms) | **46.83 ms** (±2.98 ms) |
| **FLN ➔ NRT** | Transpacífico Múltiplas Escalas | **13.68 ms** (±0.75 ms) | **107.50 ms** (±3.86 ms) |
| **JFK ➔ SYD** | América do Norte ➔ Oceania | **15.43 ms** (±2.40 ms) | **92.82 ms** (±2.44 ms) |
| **CDG ➔ HND** | Europa ➔ Ásia | **14.24 ms** (±11.28 ms) | **82.25 ms** (±1.27 ms) |
| **FLN ➔ ALH** | Intercontinental Hemisfério Sul | **12.10 ms** (±0.55 ms) | **102.99 ms** (±0.90 ms) |

* **Tempo de Carga do Grafo em RAM:** ~1.2 segundos na inicialização (3.224 nós e 36.826 arestas).
* **Média Global Dijkstra Único:** **~9.9 ms** (rotas curtas diretas respondem em fração de milissegundo).
* **Média Global Yen (3 alternativas):** **~72.3 ms** (refletindo o custo de rodar múltiplos Dijkstras por nó de espora).

---

## 📑 Transparência de Dados e Heurísticas

1. **Origem dos Dados Geográficos e Malha:**
   * Aeroportos e rotas foram obtidos do banco de dados público da **[OpenFlights](https://openflights.org/data.html)** (dados históricos compilados até cerca de 2014, sob licença *Open Database License - ODbL*).
   * As rotas representam conexões existentes na época do dataset.
2. **Definição dos Pesos (Heurística Paramétrica Simples):**
   * Como a OpenFlights fornece apenas a topologia da malha (quais cidades se conectam) e não tarifas comerciais dinâmicas, os pesos de `data/flights.csv` foram gerados através de uma **heurística determinística simplificada** baseada na distância de Haversine ($d_{\text{km}}$):
     $$\text{Duração Estimada (h)} \approx \max\left(1, \operatorname{round}\left(\frac{d_{\text{km}}}{800} + 0.5\right)\right)$$
     $$\text{Tarifa Paramétrica (USD)} \approx 55 + (d_{\text{km}} \times 0.088)$$
   * **Limitação dessa modelagem:** Por serem derivadas da mesma variável física ($d_{\text{km}}$), preço e duração no grafo estático são fortemente correlacionados. O valor fixo de $55 representa uma taxa base hipotética de manuseio e decolagem. Se o $55 for removido, o preço torna-se estritamente proporcional à distância ($0.088 \cdot d$), tornando os pesos de tempo e preço quase colineares.
3. **Módulo Experimental `live_flights.py`:**
   * Utiliza a biblioteca open-source `fast-flights` para consultar tarifas reais do Google Flights sob demanda decodificando parâmetros Protobuf.
   * *Aviso Acadêmico:* Trata-se de uma Prova de Conceito (PoC) baseada em engenharia reversa de chamadas internas, não garantida para produção e sujeita a quebras caso o Google altere seus payloads.

---

## 💱 Suporte Multimoedas na Interface

Conversão dinâmica dos valores calculados na interface visual via taxas de referência pré-definidas (sem sobrecarga de reprocessamento do grafo):
* 🇧🇷 **Real Brasileiro (`BRL R$`)**
* 🇺🇸 **Dólar Americano (`USD $`)**
* 🇪🇺 **Euro (`EUR €`)**
* 🇬🇧 **Libra Esterlina (`GBP £`)**

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
   * **Swagger OpenAPI:** [http://127.0.0.1:8008/docs](http://127.0.0.1:8008/docs)

---

## 🧪 Testes Automatizados

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
│   ├── dijkstra.py           # Algoritmos de Dijkstra e Yen (K-Shortest Paths)
│   ├── exceptions.py         # Exceções de domínio (AirportNotFoundError, NoRouteFound)
│   ├── graph.py              # Construtor do Grafo em memória com NetworkX
│   └── live_flights.py       # Extração experimental de tarifas (Google Flights Protobuf)
├── data/
│   ├── airports.csv          # 3.224 aeroportos com coordenadas geográficas (ODbL / OpenFlights)
│   └── flights.csv           # 36.826 rotas com pesos paramétricos
├── frontend/
│   └── index.html            # Interface fullscreen com Leaflet Dark e Autocomplete
├── tests/
│   ├── test_api.py           # Testes de integração dos endpoints FastAPI
│   └── test_dijkstra.py      # Testes unitários do cálculo de menor caminho
├── benchmark.py              # Medição empírica de latência (N=10 + Warmup)
├── requirements.txt          # Dependências do projeto
├── LICENSE                   # Licença MIT
└── README.md                 # Documentação técnica completa
```

---

## ⚖️ Licenças e Atribuição

* O código-fonte deste projeto é distribuído sob a licença **MIT** ([LICENSE](LICENSE)).
* A malha topológica de aeroportos e rotas contida no diretório `data/` é derivada da base de dados aberta **[OpenFlights](https://openflights.org/data.html)**, disponibilizada sob a licença **Open Database License (ODbL)**.

Desenvolvido por **[Douglas Scarello](https://github.com/DouglasScarello)** 🚀

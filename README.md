# 🌐 AeroGraph — Global Flight Navigation Engine & Tactical Radar

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![NetworkX](https://img.shields.io/badge/NetworkX-In--Memory_Graph-blue?style=for-the-badge)](https://networkx.org/)
[![Dijkstra & Yen](https://img.shields.io/badge/Algorithm-Dijkstra_%2B_Yen_K--Paths-orange?style=for-the-badge)](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
[![Leaflet](https://img.shields.io/badge/Leaflet-Geodesic_Dark_Radar-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

O **AeroGraph** é uma engine de alta performance para resolução do **Problema do Menor Caminho (Shortest Path Problem)** aplicada à aviação comercial global. 

O sistema compila **3.224 aeroportos** e **36.826 rotas comerciais ativas** em um **Grafo Direcionado Ponderado (`DiGraph`) em memória RAM**, calculando trajetórias intercontinentais ótimas e rotas alternativas (**Algoritmo de Yen - K-Shortest Paths**). O projeto inclui um **Radar Cartográfico Geodésico Fullscreen** (Leaflet Dark / GTA Style) com traçado em arcos de grande círculo, conversor multimoedas e módulo experimental de cotação em tempo real.

---

## 💡 Sobre o Nome e Conceito

> **AeroGraph** nasce da fusão direta entre **Aeronáutica** e **Teoria dos Grafos** (*Graph Theory*). 
> O projeto foi idealizado para abordar o tráfego aéreo planetário sob a ótica de engenharia de software e ciência da computação pura: tratar o tráfego aéreo não como tabelas relacionais em banco de dados, mas como uma rede vetorial ponderada em memória.

---

## 🏛️ Modelagem Matemática e Algoritmos

### 1. Grafo Direcionado Ponderado $G = (V, E)$
* **Vértices ($V$):** $3.224$ aeroportos com código IATA e coordenadas geográficas $(\phi, \lambda)$.
* **Arestas Direcionadas ($E$):** $36.826$ conexões comerciais ativas entre pares de aeroportos.
* **Pesos Não-Negativos:** Cada aresta possui dois pesos independentes: $w_{\text{price}} > 0$ e $w_{\text{duration}} > 0$.
  * *Observação Teórica:* Como os custos e durações de voo são estritamente positivos ($w(u, v) \ge 0$), a precondição do **Algoritmo de Dijkstra** é satisfeita, garantindo que a relaxação gulosa com Min-Heap não sofra de ciclos negativos.

### 2. Algoritmo de Dijkstra & Complexidade
Dado o vértice de origem $s \in V$, o algoritmo mantém a estimativa de menor distância com Min-Heap:
$$\operatorname{dist}[v] = \min(\operatorname{dist}[v], \operatorname{dist}[u] + w(u, v))$$
* **Complexidade Assintótica:** $O((|V| + |E|) \log |V|)$ com representação de lista de adjacências e priority queue.

### 3. K-Caminhos Mínimos (Algoritmo de Yen)
Para fornecer alternativas viáveis sem filtros manuais arbitrários, o sistema emprega o **Algoritmo de Yen** ($K\text{-Shortest Loopless Paths}$):
* A primeira rota $A_1$ é o caminho ótimo de Dijkstra.
* Para encontrar as rotas subsequentes $A_k$, o algoritmo gera caminhos candidatos desviando iterativamente a partir de cada nó de espora (*spur node*) de $A_{k-1}$, removendo temporariamente arestas já exploradas para evitar loops.
* **Critério de Seleção das 3 Alternativas:**
  1. 🟢 **Mais Econômica:** Caminho ótimo $A_1$ minimizando $\sum w_{\text{price}}$.
  2. 🔵 **Mais Rápida:** Caminho ótimo $A_1$ minimizando $\sum w_{\text{duration}}$.
  3. 🟡 **Custo-Benefício:** Rota com menor função objetivo ponderada normalizada:
     $$F(p) = 0.5 \cdot \left(\frac{\text{Preço}(p)}{\text{Preço}_{\max}}\right) + 0.5 \cdot \left(\frac{\text{Duração}(p)}{\text{Duração}_{\max}}\right)$$

### 4. Distâncias Geodésicas (Fórmula de Haversine)
A distância ortodrômica real entre dois aeroportos $(\phi_1, \lambda_1)$ e $(\phi_2, \lambda_2)$ sobre a esfera terrestre ($R = 6.371\text{ km}$) é computada para evitar distorções de projeção euclidiana plana:
$$\Delta\sigma = 2 \arcsin \sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}, \quad d = R \cdot \Delta\sigma$$

---

## 📊 Benchmark Real de Performance

Os testes de latência foram medidos empiricamente via script [`benchmark.py`](benchmark.py) executado localmente sobre o grafo completo:

| Rota | Tipo de Trajeto | Dijkstra Único (Ótimo) | Yen K-Paths (3 Alternativas) |
| :--- | :--- | :---: | :---: |
| **FLN ➔ GIG** | Doméstico Curto (Brasil) | **0.97 ms** | **4.47 ms** |
| **GRU ➔ LHR** | Transatlântico Direto | **25.28 ms** | **167.59 ms** |
| **CDG ➔ HND** | Europa ➔ Ásia | **30.17 ms** | **294.25 ms** |
| **JFK ➔ SYD** | América do Norte ➔ Oceania | **42.75 ms** | **298.58 ms** |
| **FLN ➔ ALH** | Intercontinental Hemisfério Sul | **47.14 ms** | **359.18 ms** |
| **FLN ➔ NRT** | Transpacífico Múltiplas Escalas | **83.57 ms** | **611.05 ms** |

* **Tempo de Carga do Grafo em RAM:** ~1.3 segundos na inicialização.
* **Média de Consulta Dijkstra:** **~38 ms** (rotas domésticas diretas respondem em < 1 ms).
* **Média Yen Multi-Rotas:** **~289 ms**.

---

## 📑 Origem dos Dados e Natureza dos Pesos

Para transparência técnica total sobre a modelagem:

1. **Malha de Aeroportos e Rotas:**
   * Extraída do dataset público aberto da **[OpenFlights](https://openflights.org/data.html)** (licença *Open Database License - ODbL*).
   * Filtrada estritamente para aeroportos comerciais operacionais com código IATA e coordenadas válidas.
2. **Pesos Paramétricos vs. Tarifas Dinâmicas de Mercado:**
   * Os custos e durações armazenados no arquivo `data/flights.csv` **são pesos modelados parametricamente**, baseados na metodologia padrão de custo por assento/quilômetro (**CASM da IATA/FAA**):
     $$\text{Duração (h)} \approx \max\left(1, \operatorname{round}\left(\frac{d_{\text{km}}}{800} + 0.5\right)\right)$$
     $$\text{Preço Base (USD)} \approx 55 + (d_{\text{km}} \times 0.088)$$
   * Isso garante consistência matemática sem pesos negativos na malha estática.
3. **Módulo Experimental `live_flights.py` (Limitações):**
   * A engine inclui um módulo experimental que faz engenharia reversa das consultas Protobuf do Google Flights para fins puramente acadêmicos de demonstração.
   * *Limitação:* Por não utilizar uma API corporativa oficial (GDS Amadeus/Sabre), essa funcionalidade está sujeita a mudanças de layout, rate-limits ou bloqueios por termos de serviço, devendo ser compreendida como prova de conceito (PoC).

---

## 💱 Suporte Multimoedas em Tempo Real

A interface converte instantaneamente todos os preços e segmentos sem recarregar o grafo:
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

4. **Executar o benchmark oficial (opcional):**
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

Suíte de testes unitários do algoritmo e testes de integração dos endpoints HTTP via `TestClient`:

```bash
pytest -v
```

---

## 📁 Estrutura do Repositório

```text
AeroGraph/
├── backend/
│   ├── app.py                # Rotas REST, middleware CORS e inicialização da API
│   └── schemas.py            # Validação e serialização estrita com Pydantic V2
├── core/
│   ├── dijkstra.py           # Algoritmos de Dijkstra e Yen (K-Shortest Paths)
│   ├── exceptions.py         # Exceções de domínio (AirportNotFoundError, NoRouteFound)
│   ├── graph.py              # Construtor do Grafo Direcionado em memória com NetworkX
│   └── live_flights.py       # Extração experimental de tarifas (Google Flights Protobuf)
├── data/
│   ├── airports.csv          # 3.224 aeroportos comerciais com coordenadas geográficas
│   └── flights.csv           # 36.826 rotas ativas com pesos paramétricos
├── frontend/
│   └── index.html            # Aplicação web fullscreen com Leaflet Dark e Autocomplete
├── tests/
│   ├── test_api.py           # Testes de integração dos endpoints FastAPI
│   └── test_dijkstra.py      # Testes unitários do cálculo de menor caminho
├── benchmark.py              # Script empírico de medição de latência do grafo
├── requirements.txt          # Dependências do projeto
├── LICENSE                   # Licença MIT
└── README.md                 # Documentação técnica completa
```

---

## ⚖️ Licença

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

Desenvolvido por **[Douglas Scarello](https://github.com/DouglasScarello)** 🚀

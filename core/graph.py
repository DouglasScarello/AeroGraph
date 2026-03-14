import pandas as pd
import networkx as nx

def build_graph(airports_file, flights_file):
    airports = pd.read_csv(airports_file)
    flights = pd.read_csv(flights_file)
    
    G = nx.DiGraph()
    
    # Adiciona aeroportos
    for _, row in airports.iterrows():
        G.add_node(row['IATA'], city=row['City'], country=row['Country'])
    
    # Adiciona voos
    for _, row in flights.iterrows():
        G.add_edge(row['Origin'], row['Destination'], price=row['Price'], duration=row['Duration'])
    
    return G

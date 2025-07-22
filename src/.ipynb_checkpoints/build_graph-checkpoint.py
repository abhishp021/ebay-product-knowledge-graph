import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import json
from pathlib import Path

def load_data(input_path):
    if input_path.endswith(".csv"):
        df = pd.read_csv(input_path)
        df["normalized_entities"] = df["normalized_entities"].apply(eval)
        return df

    elif input_path.endswith(".json"):
        with open(input_path, "r", encoding="utf-8") as f:
            records = json.load(f)
        return pd.DataFrame(records)

    else:
        raise ValueError("Unsupported file format. Use .csv or .json")

def build_knowledge_graph(input_path):
    df = load_data(input_path)
    G = nx.Graph()

    for _, row in df.iterrows():
        product_id = f"product_{row['id']}"
        G.add_node(product_id, type="product", title=row["title"])

        for entity in row["normalized_entities"]:
            entity_node = f"entity_{entity.lower()}"
            G.add_node(entity_node, type="entity", label=entity)
            G.add_edge(product_id, entity_node)

    return G

def draw_graph(G, limit=50):
    plt.figure(figsize=(12, 10))

    node_colors = []
    labels = {}

    for node in G.nodes(data=True):
        if node[1]['type'] == 'product':
            node_colors.append('lightblue')
            labels[node[0]] = node[1].get('title', '')
        else:
            node_colors.append('orange')
            labels[node[0]] = node[1].get('label', '')

    pos = nx.spring_layout(G, k=0.5, iterations=50)
    nx.draw(G, pos, with_labels=True, labels=labels, node_color=node_colors, node_size=700, font_size=7)

    Path("outputs/graphs").mkdir(parents=True, exist_ok=True)
    nx.write_gml(G, "outputs/graphs/product_knowledge_graph.gml")
    plt.title("Product Knowledge Graph")
    plt.show()

def compute_centrality_measures(G: nx.Graph):
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=500)

    centrality_data = []

    for node in G.nodes(data=True):
        node_id = node[0]
        node_type = node[1]['type']
        node_label = node[1].get('title') or node[1].get('label') or node_id

        centrality_data.append({
            "node_id": node_id,
            "type": node_type,
            "label": node_label,
            "degree_centrality": degree_centrality.get(node_id, 0),
            "betweenness_centrality": betweenness_centrality.get(node_id, 0),
            "eigenvector_centrality": eigenvector_centrality.get(node_id, 0)
        })

    df = pd.DataFrame(centrality_data)
    df.sort_values(by="degree_centrality", ascending=False, inplace=True)

    output_dir = Path("outputs/analytics")
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_dir / "centrality_analysis.csv", index=False)

    print("✅ Centrality analysis complete. Results saved to outputs/analytics/centrality_analysis.csv")

    return df

if __name__ == "__main__":
    graph = build_knowledge_graph("data/processed/normalized_entities.json")
    centrality_df = compute_centrality_measures(graph)
    print(centrality_df.head(10))  # top 10 most central nodes
    draw_graph(graph)

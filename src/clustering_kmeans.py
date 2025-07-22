import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# Loading saved Word2Vec entity embeddings
def load_entity_embeddings(path):
    with open(path, "r") as f:
        data = json.load(f)
    product_ids = []
    vectors = []
    titles = []

    for row in data:
        product_ids.append(row["product_id"])
        titles.append(row["title"])
        vectors.append(row["embedding"])

    return product_ids, titles, np.array(vectors)

# KMeans clustering
def cluster_embeddings(vectors, num_clusters=5):
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(vectors)
    return labels, kmeans

# Visualizing in 2D using PCA
def visualize_clusters(vectors, labels, titles):
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(vectors)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=reduced[:, 0], y=reduced[:, 1], hue=labels, palette="Set2", s=100)

    for i, title in enumerate(titles):
        plt.text(reduced[i, 0], reduced[i, 1], title, fontsize=9)

    plt.title("Product Clusters (PCA of Word2Vec Embeddings)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    path_to_embeddings = "data/processed/product_embeddings_word2vec.json"
    product_ids, titles, vectors = load_entity_embeddings(path_to_embeddings)

    num_clusters = 2  
    labels, kmeans = cluster_embeddings(vectors, num_clusters)

    for pid, title, label in zip(product_ids, titles, labels):
        print(f"Cluster {label}: {title}")

    visualize_clusters(vectors, labels, titles)

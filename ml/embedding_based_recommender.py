import pandas as pd
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_entities_text(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = []
    texts = []

    for row in data:
        products.append({
            "id": row["id"],
            "title": row["title"]
        })
        # Joining entities into a single string
        texts.append(" ".join(row["normalized_entities"]).lower())

    return products, texts

def generate_tfidf_embeddings(texts):
    vectorizer = TfidfVectorizer()
    embeddings = vectorizer.fit_transform(texts)
    return embeddings, vectorizer

def get_top_similar_products(query_index, embeddings, products, top_k=5):
    similarity_scores = cosine_similarity(embeddings[query_index], embeddings).flatten()
    top_indices = np.argsort(similarity_scores)[::-1][1:top_k+1]  # exclude self

    results = []
    for idx in top_indices:
        results.append({
            "product_id": products[idx]["id"],
            "title": products[idx]["title"],
            "similarity": round(similarity_scores[idx] * 100, 2)
        })
    return results

def search_and_recommend(product_name_query, products, texts, embeddings):
    query_index = next(
        (i for i, p in enumerate(products) if product_name_query.lower() in p["title"].lower()),
        None
    )
    if query_index is None:
        return {"error": "Product not found"}

    matched_product = products[query_index]
    recommendations = get_top_similar_products(query_index, embeddings, products)

    return {
        "query": product_name_query,
        "matched_product": matched_product,
        "recommendations": recommendations
    }

if __name__ == "__main__":
    json_path = "data/processed/normalized_entities.json"
    products, texts = load_entities_text(json_path)
    embeddings, vectorizer = generate_tfidf_embeddings(texts)

    query = "iPhone 13 Pro Max"
    result = search_and_recommend(query, products, texts, embeddings)
    print(json.dumps(result, indent=2))
from gensim.models import Word2Vec
import numpy as np
import json

def load_entity_tokens(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = []
    token_lists = []

    for row in data:
        products.append({
            "id": row["id"],
            "title": row["title"]
        })
        # Splitting entities into tokens
        token_lists.append([entity.lower() for entity in row["normalized_entities"]])

    return products, token_lists

def train_word2vec_model(token_lists, vector_size=100, window=5, min_count=1, workers=4):
    model = Word2Vec(sentences=token_lists, vector_size=vector_size, window=window,
                     min_count=min_count, workers=workers)
    return model

def generate_product_embeddings(products, token_lists, w2v_model):
    product_embeddings = []
    for i, tokens in enumerate(token_lists):
        vectors = []
        for token in tokens:
            if token in w2v_model.wv:
                vectors.append(w2v_model.wv[token])
        if vectors:
            product_vector = np.mean(vectors, axis=0)
        else:
            product_vector = np.zeros(w2v_model.vector_size)
        product_embeddings.append({
            "product_id": products[i]["id"],
            "title": products[i]["title"],
            "embedding": product_vector.tolist()
        })
    return product_embeddings

if __name__ == "__main__":
    json_path = "data/processed/normalized_entities.json"
    products, token_lists = load_entity_tokens(json_path)
    w2v_model = train_word2vec_model(token_lists)

    product_embeddings = generate_product_embeddings(products, token_lists, w2v_model)

    # Saving to disk for later clustering or classification
    with open("data/processed/product_embeddings_word2vec.json", "w") as f:
        json.dump(product_embeddings, f, indent=2)

    print(f"Generated embeddings for {len(product_embeddings)} products.")

from fastapi import FastAPI, UploadFile, File, Query
import networkx as nx
import pandas as pd
import shutil
import subprocess
import uuid
from typing import List
from fuzzywuzzy import fuzz
from statistics import mean

from src.build_graph import build_knowledge_graph
from src import extract_entities, normalize_entities

app = FastAPI(
    title="eBay Product Knowledge Graph API",
    description="Query products and entities from the graph",
    version="1.0.0"
)

# Loading graph
GRAPH_PATH = "data/processed/normalized_entities.json"
G = build_knowledge_graph(GRAPH_PATH)

@app.get("/")
def root():
    return {"message": "eBay Product Knowledge API is live!"}

@app.get("/products/by-entity/")
def get_products_by_entity(entity: str):
    entity_node = f"entity_{entity.lower()}"
    if entity_node not in G:
        return {"error": "Entity not found"}

    neighbors = G.neighbors(entity_node)
    products = [G.nodes[n]["title"] for n in neighbors if G.nodes[n]["type"] == "product"]
    return {"entity": entity, "products": products}

@app.get("/entities/by-product/")
def get_entities_by_product(product_id: int):
    product_node = f"product_{product_id}"
    if product_node not in G:
        return {"error": "Product not found"}

    neighbors = G.neighbors(product_node)
    entities = [G.nodes[n]["label"] for n in neighbors if G.nodes[n]["type"] == "entity"]
    return {"product_id": product_id, "entities": entities}

@app.get("/entities/")
def list_entities(limit: int = 20):
    entities = [
        G.nodes[n]["label"] for n in G.nodes
        if G.nodes[n]["type"] == "entity"
    ]
    return {"entities": sorted(entities)[:limit]}

@app.get("/products/")
def list_products(limit: int = 20):
    products = [
        {"id": int(n.replace("product_", "")), "title": G.nodes[n]["title"]}
        for n in G.nodes if G.nodes[n]["type"] == "product"
    ]
    return {"products": products[:limit]}

@app.get("/relations")
def get_relations(entity: str):
    if entity not in G:
        raise HTTPException(status_code=404, detail="Entity not found")
    return [{"target": t, "relation": G[entity][t]} for t in G[entity]]

@app.post("/upload/")
def upload_file(file: UploadFile = File(...)):
    raw_path = f"data/raw/{uuid.uuid4().hex[:8]}.csv"
    with open(raw_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 1: Extracting entities
    entities_path = "data/processed/entities.csv"
    extract_entities.process_listings(csv_path=raw_path, output_path=entities_path)

    # Step 2: Normalizing
    norm_path = "data/processed/normalized_entities.json"
    normalize_entities.normalize_entities_csv(input_csv=entities_path, output_json=norm_path)

    # Step 3: Rebuilding graph globally
    global G
    G = build_knowledge_graph(norm_path)

    return {
        "message": "Graph updated from uploaded file.",
        "raw_csv": raw_path,
        "normalized_json": norm_path
    }

@app.get("/products/search/")
def search_products(q: str):
    results = [
        {"id": int(n.replace("product_", "")), "title": G.nodes[n]["title"]}
        for n in G.nodes
        if G.nodes[n]["type"] == "product" and q.lower() in G.nodes[n]["title"].lower()
    ]
    return {"query": q, "results": results}

@app.get("/graph/stats/")
def graph_stats():
    entity_count = sum(1 for n in G.nodes if G.nodes[n]["type"] == "entity")
    product_count = sum(1 for n in G.nodes if G.nodes[n]["type"] == "product")
    edge_count = G.number_of_edges()

    return {
        "products": product_count,
        "entities": entity_count,
        "edges": edge_count
    }

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= threshold

@app.get("/search_by_feature")
def search_by_feature(feature: str, limit: int = 10):
    matches = []
    for node_id, data in G.nodes(data=True):
        if data["type"] == "entity":
            score = fuzz.partial_ratio(feature.lower(), data["label"].lower())
            if score > 80:
                matches.append((node_id, data["label"], score))

    product_scores = {}
    for entity_node, label, score in matches:
        connected_products = [
            (neighbor, G.nodes[neighbor]["title"])
            for neighbor in G.neighbors(entity_node)
            if G.nodes[neighbor]["type"] == "product"
        ]
        for pid, title in connected_products:
            if pid not in product_scores:
                product_scores[pid] = {
                    "product_id": pid,
                    "product_title": title,
                    "matched_entities": [],
                    "raw_scores": []
                }
            product_scores[pid]["matched_entities"].append(label)
            product_scores[pid]["raw_scores"].append(score)

    # Compute average of top 5 scores for each product (but keep all matched_entities)
    for data in product_scores.values():
        top_scores = sorted(data["raw_scores"], reverse=True)[:5]
        data["avg_score"] = round(mean(top_scores), 2)

    # Sort by average score
    sorted_results = sorted(product_scores.values(), key=lambda x: x["avg_score"], reverse=True)

    return {
        "query": feature,
        "matches": sorted_results[:limit],
        "count": len(sorted_results)
    }

@app.get("/recommend")
def recommend_by_query(query: str, top_k: int = 5):
    # Step 1: Finding best-matching product
    product_nodes = [n for n, attr in G.nodes(data=True) if attr["type"] == "product"]
    
    best_match = None
    highest_score = 0

    for node in product_nodes:
        title = G.nodes[node]["title"]
        score = fuzz.partial_ratio(query.lower(), title.lower())
        if score > highest_score:
            highest_score = score
            best_match = node

    if not best_match:
        raise HTTPException(status_code=404, detail="No matching product found")

    # Step 2: Finding similar products by shared entities
    product_entities = {nbr for nbr in G.neighbors(best_match) if G.nodes[nbr]['type'] == 'entity'}
    
    scores = {}
    print("Entities of matched product:", product_entities)

    for entity in product_entities:
        print("Entity:", entity)
        print("Connected products:")
        for neighbor in G.neighbors(entity):
            if G.nodes[neighbor]["type"] == "product":
                print(" ->", neighbor, G.nodes[neighbor]["title"])
    
    for entity in product_entities:
        for neighbor in G.neighbors(entity):
            if neighbor.startswith("product_") and neighbor != best_match:
                scores[neighbor] = scores.get(neighbor, 0) + 1

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

    recommendations = [
        {
            "product_id": pid,
            "title": G.nodes[pid]["title"],
            "shared_entity_count": score
        }
        for pid, score in ranked
    ]

    return {
        "query": query,
        "matched_product": {
            "product_id": best_match,
            "title": G.nodes[best_match]["title"],
            "match_score": highest_score
        },
        "recommendations": recommendations
    }

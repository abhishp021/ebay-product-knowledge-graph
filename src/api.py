from fastapi import FastAPI, UploadFile, File
import networkx as nx
import pandas as pd
import shutil
import subprocess
import uuid

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

# 🧠 Product Knowledge Graph API

This project builds a **Knowledge Graph** from eBay product listings using **Natural Language Processing (NLP)** and exposes it via a **FastAPI** interface.

---

## 🚀 Features

- 📤 Upload product listing CSVs
- 🧠 Extract product-related entities (brand, model, specs) using spaCy
- 🔧 Normalize entities to standardize formats
- 🕸️ Build an interactive knowledge graph with NetworkX
- 🐳 Fully Dockerized for easy deployment

---

## 📁 Project Structure

```

.
├── src/
│   ├── api.py                     # FastAPI API endpoints
│   ├── extract_entities.py        # Extracts entities using spaCy
│   ├── normalize_entities.py      # Normalizes extracted entities
│   ├── build_graph.py             # Builds the product knowledge graph
│   ├── test_graph.py             
├── data/
│   ├── raw/                       # Uploaded raw CSV files
│   └── processed/                 # Intermediate and final outputs (CSV/JSON)
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker image definition
└── README.md                     # Project documentation

````

---

## 🛠️ Project Pipeline
CSV → Extract Entities → Normalize → Build Graph → Query via API
---

## 📦 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload/` | Upload a CSV file of listings |
| `GET`  | `/nodes/`  | List all entity nodes |
| `GET`  | `/edges/`  | List co-occurrence edges |
| `GET`  | `/stats/`  | Get graph stats (node count, edge count) |

---

## 📦 Installation

### 🔧 Local Setup

```bash
git clone https://github.com/abhishp021/ebay-product-knowledge-graph.git
cd ebay-product-knowledge-graph
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn src.api:app --reload
````

---

### 🐳 Docker

```bash
docker build -t product-kg-api .
docker run -p 8000:8000 product-kg-api
```

---

## 📤 API Usage

### 🔍 Feature-Based Search & Recommendations

#### `/search_by_feature?feature=<query>`

Performs a fuzzy search over normalized product features (entities) and returns matching products.

#### ✅ Input:

* `feature`: A search string (e.g., `iphone`, `13`, `128`)

##### 📦 Output:

```json
{
  "query": "13",
  "matches": [
    {
      "product_id": "product_1",
      "product_title": "Apple iPhone 13 Pro Max",
      "matched_entities": ["13", "Iphone 13"],
      "raw_scores": [100, 100],
      "avg_score": 100
    },
    {
      "product_id": "product_5",
      "product_title": "Dell XPS 13 Laptop",
      "matched_entities": ["Dell Xps 13 Laptop", "Dell Xps 13"],
      "raw_scores": [100, 100],
      "avg_score": 100
    }
  ],
  "count": 2
}
```

* Matches are ranked by **average fuzzy score of top-5 entity matches**.
* Repeats from same product are grouped.

---

### 🤝 Recommendation Endpoint

#### `/recommend?query=<search_string>`

Given a product search query, returns similar products **based on shared entities (features)**.

##### ✅ Input:

* `query`: Search string matching a product (e.g., `"iphone"` or `"dell"`)

##### 📦 Output:

```json
{
  "query": "13",
  "matched_product": {
    "product_id": "product_1",
    "title": "Apple iPhone 13 Pro Max",
    "match_score": 100
  },
  "recommendations": [
    {
      "product_id": "product_5",
      "title": "Dell XPS 13 Laptop",
      "shared_entities": ["13"],
      "score": 1
    }
  ]
}
```

* Returns products connected via **shared entities** in the knowledge graph.
* Scoring is based on number of shared entities.
* If no similar products exist, `recommendations` will be empty.

---

### Upload a CSV

**Endpoint:** `POST /upload/`
**Form Field:** `file` (CSV)

```bash
curl -X POST "http://localhost:8000/upload/" \
  -F "file=@examples/products.csv"
```

**Response:**

```json
{
  "message": "Graph updated from uploaded file.",
  "raw_csv": "data/raw/1a2b3c4d.csv",
  "normalized_json": "data/processed/normalized_entities.json"
}
```

---

## 📄 Sample Input CSV

```csv
title,description
"Apple iPhone 14","Latest model with A15 chip and advanced camera"
"Samsung Galaxy S22","Android flagship with AMOLED display and Snapdragon processor"
"OnePlus 10 Pro","Fast performance, Hasselblad camera, and 80W charging"
```

---

## 🧠 Sample Extracted Entities

```json
[
  {"text": "Apple", "label": "ORG"},
  {"text": "iPhone 14", "label": "PRODUCT"},
  {"text": "Snapdragon", "label": "PRODUCT"},
  {"text": "OnePlus", "label": "ORG"},
  {"text": "Galaxy S22", "label": "PRODUCT"}
]
```

---

## 🕸️ Knowledge Graph

* **Nodes**: Brands, products, chipsets, features
* **Edges**: Implied connections based on co-occurrence or relations
* Built using [`NetworkX`](https://networkx.org)

---

## 🧪 Example Workflow

1. Upload CSV → `POST /upload/`
2. Entities extracted → `data/processed/entities.csv`
3. Normalization applied → `data/processed/normalized_entities.json`
4. Knowledge graph rebuilt in memory (`G` in `api.py`)

---

## ✅ TODO / Future Enhancements

* [ ] API endpoint to return extracted entities directly
* [ ] API to export graph in GraphML or Neo4j-compatible format
* [ ] Frontend for visualizing the graph (D3.js or PyVis)
* [ ] Sentence-transformers for semantic entity grouping
* [ ] Product recommendation based on graph traversal

---

## ⚙️ Tech Stack

| Layer        | Tool / Library           |
| ------------ | ------------------------ |
| API Server   | FastAPI                  |
| NLP Engine   | spaCy (`en_core_web_sm`) |
| Graph Engine | NetworkX                 |
| Container    | Docker                   |
| Formats      | CSV, JSON                |

---

## 👨‍💻 Author

**Abhishek Pandey**
Machine Learning Engineer    
[LinkedIn](https://linkedin.com/in/abhishp021)    
[GitHub](https://github.com/abhishp021)    

---

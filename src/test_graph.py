from build_graph import build_knowledge_graph

def test_entity_connections():
    G = build_knowledge_graph("data/processed/normalized_entities.csv")
    assert any(n.startswith("entity_apple") for n in G.nodes), "Apple entity missing"
    print("✅ Entity 'apple' exists in graph")

if __name__ == "__main__":
    test_entity_connections()

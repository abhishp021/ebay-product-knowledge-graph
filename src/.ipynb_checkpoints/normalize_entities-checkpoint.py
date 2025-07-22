import pandas as pd
import re
import json
from pathlib import Path

def normalize_entity(entity):
    text, label = entity
    text = text.lower().strip()

    text = re.sub(r"[^\w\s]", "", text)

    if label in ["ORG", "PRODUCT"]:
        text = text.title()

    if label in ['ORG', 'PRODUCT', 'QUANTITY', 'GPE', 'CARDINAL']:
        return text
        
    return None

def normalize_entities_csv(input_csv, output_csv, json_output_path):
    df = pd.read_csv(input_csv)
    df["normalized_entities"] = df["entities"].apply(eval).apply(lambda ents: list(set(filter(None, [normalize_entity(e) for e in ents]))))

    df[["id", "title", "normalized_entities"]].to_csv(output_csv, index=False)

    print(f"Normalized entities saved to {output_csv}")

    # Save JSON
    records = df[["id", "title", "normalized_entities"]].to_dict(orient="records")
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON saved to {json_output_path}")

if __name__ == "__main__":
    input_csv = "data/processed/entities.csv"
    output_csv = "data/processed/normalized_entities.csv"
    json_output_path = "data/processed/normalized_entities.json"
    
    # Create output directory if not exists
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)

    normalize_entities_csv(input_csv, output_csv, json_output_path)
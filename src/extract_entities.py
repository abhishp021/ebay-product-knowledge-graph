import spacy
import pandas as pd
from tqdm import tqdm

nlp = spacy.load("en_core_web_sm")

def extract_named_entities(text: str):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def process_listings(csv_path: str, output_path: str):
    df = pd.read_csv(csv_path)
    tqdm.pandas()

    df["full_text"] = df["title"].fillna("") + ". " + df["description"].fillna("")
    df["entities"] = df["full_text"].progress_apply(extract_named_entities)

    df[["id", "title", "entities"]].to_csv(output_path, index=False)
    print(f"✅ Saved extracted entities to {output_path}")

if __name__ == "__main__":
    process_listings(
        csv_path="data/raw/ebay_listings_sample.csv",
        output_path="data/processed/entities.csv"
    )
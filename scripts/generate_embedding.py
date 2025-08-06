import os
import json
import pandas as pd
import numpy as np
import faiss

from embeddings.visual_model import DummyVisualModel
from embeddings.chessbert_model import ChessBERTEmbedder
from embeddings.theme_encoder import ThemeEncoder
from embeddings.fusion import fuse_embeddings
from utils.fen_to_image import fen_to_image

SAVE_DIR = "db"
os.makedirs(SAVE_DIR, exist_ok=True)

# Load models
visual_encoder = DummyVisualModel()
chess_encoder = ChessBERTEmbedder("your/chessbert-model")  # Replace with actual ChessBERT path
theme_encoder = ThemeEncoder()

dim_total = visual_encoder.dim + 768 + theme_encoder.model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(dim_total)
metadata = []

# Load puzzles
df = pd.read_parquet("./data/puzzles_filtered.parquet")

for _, row in df.iterrows():
    fen = row["fen"]
    moves = row["moves"].split() if isinstance(row["moves"], str) else []
    themes = row["themes"].split(",") if isinstance(row["themes"], str) else []
    pid = row["id"]

    try:
        image = fen_to_image(fen)
        visual_emb = visual_encoder.encode_image(image)
        chess_emb = chess_encoder.encode(" ".join(moves))
        theme_emb = theme_encoder.encode(themes)

        final_vector = fuse_embeddings(visual_emb, chess_emb, theme_emb)
        index.add(np.array([final_vector]))

        metadata.append({
            "id": pid,
            "fen": fen,
            "moves": moves,
            "theme": themes
        })

    except Exception as e:
        print(f"Skipping puzzle {pid} due to error: {e}")

# Save index and metadata
faiss.write_index(index, os.path.join(SAVE_DIR, "index.faiss"))
with open(os.path.join(SAVE_DIR, "metadata.json"), "w") as f:
    json.dump(metadata, f, indent=2)

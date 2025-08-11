import os
import json
import pandas as pd
import numpy as np
import torch

from embeddings import SigLIPVisualEncoder, ThemeEncoder, fuse_embeddings
from utils.fen_to_image import fen_to_image

os.environ["TOKENIZERS_PARALLELISM"] = "false"

SAVE_DIR = "db"
os.makedirs(SAVE_DIR, exist_ok=True)

# Load models
visual_encoder = SigLIPVisualEncoder()
theme_encoder = ThemeEncoder()

dim_total = visual_encoder.dim + 768 + theme_encoder.model.get_sentence_embedding_dimension()

# Load puzzles in chunks
df = pd.read_parquet("./data/puzzles_filtered.parquet")

print(torch.cuda.is_available())

BATCH_SIZE = 10000  # Adjust this if you run into memory issues
vectors_path = os.path.join(SAVE_DIR, "vectors.npy")
metadata_path = os.path.join(SAVE_DIR, "metadata.jsonl")

# If files already exist, remove them
if os.path.exists(vectors_path):
    os.remove(vectors_path)
if os.path.exists(metadata_path):
    os.remove(metadata_path)

all_vectors = []

for idx, row in df.iterrows():
    fen = row["fen"]
    moves = row["moves"]
    themes = row["themes"]
    pid = row["id"]

    try:
        image = fen_to_image(fen)
        visual_emb = visual_encoder.encode_image(image)
        theme_emb = theme_encoder.encode(themes)

        final_vector = fuse_embeddings(visual_emb, theme_emb)
        all_vectors.append(final_vector)

        with open(metadata_path, "a") as f:
            json.dump({
                "id": pid,
                "fen": fen,
                "moves": moves,
                "theme": themes
            }, f)
            f.write("\n")

    except Exception as e:
        print(f"Skipping puzzle {pid} due to error: {e}")

    if (idx + 1) % 10000 == 0:
        print(f"Processed {idx + 1}/{len(df)} puzzles...", flush=True)

    # Save every BATCH_SIZE vectors to disk and clear memory
    if len(all_vectors) >= BATCH_SIZE:
        arr = np.array(all_vectors)
        if os.path.exists(vectors_path):
            with open(vectors_path, "ab") as f:
                np.save(f, arr)
        else:
            np.save(vectors_path, arr)
        all_vectors = []

# Save any remaining vectors
if all_vectors:
    arr = np.array(all_vectors)
    with open(vectors_path, "ab") as f:
        np.save(f, arr)

print("Embedding generation complete.")

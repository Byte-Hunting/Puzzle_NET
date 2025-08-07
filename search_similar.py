import os
import json
import numpy as np
import faiss

from embeddings import SigLIPVisualEncoder, ChessBERTEmbedder, ThemeEncoder, fuse_embeddings
from utils.fen_to_image import fen_to_image

SAVE_DIR = "db"

# Load FAISS index and metadata
index = faiss.read_index(os.path.join(SAVE_DIR, "index.faiss"))
with open(os.path.join(SAVE_DIR, "metadata.json")) as f:
    metadata = json.load(f)

# Load encoders
visual_encoder = SigLIPVisualEncoder()
chess_encoder = ChessBERTEmbedder()
theme_encoder = ThemeEncoder()

def search_similar(fen, moves, themes, top_k=5):
    image = fen_to_image(fen)
    visual_emb = visual_encoder.encode_image(image)
    chess_emb = chess_encoder.encode(" ".join(moves))
    theme_emb = theme_encoder.encode(themes)

    query_vector = fuse_embeddings(visual_emb, chess_emb, theme_emb).astype('float32')
    D, I = index.search(np.array([query_vector]), k=top_k)

    results = []
    for dist, idx in zip(D[0], I[0]):
        result = metadata[idx]
        result["distance"] = float(dist)
        results.append(result)

    return results

# Example usage
if __name__ == "__main__":
    # Replace this with your test puzzle
    sample_fen = "r1bqkbnr/pppppppp/n7/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 2 2"
    sample_moves = ["Nf3", "Nc6"]
    sample_themes = ["opening", "development"]

    similar = search_similar(sample_fen, sample_moves, sample_themes)
    for item in similar:
        print(item)

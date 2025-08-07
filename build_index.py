import os
import json
import numpy as np
import faiss

SAVE_DIR = "db"

# Load embeddings and metadata
vectors = np.load(os.path.join(SAVE_DIR, "vectors.npy"))
with open(os.path.join(SAVE_DIR, "metadata.json")) as f:
    metadata = json.load(f)

dim_total = vectors.shape[1]
index = faiss.IndexFlatL2(dim_total)

index.add(vectors)

# Save FAISS index and metadata again (redundantly for completeness)
faiss.write_index(index, os.path.join(SAVE_DIR, "index.faiss"))
with open(os.path.join(SAVE_DIR, "metadata.json"), "w") as f:
    json.dump(metadata, f, indent=2)

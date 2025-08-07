import os
import json
import numpy as np
import faiss

SAVE_DIR = "db"
VECTORS_PATH = os.path.join(SAVE_DIR, "vectors.npy")
METADATA_PATH = os.path.join(SAVE_DIR, "metadata.jsonl")

# Load all chunks of vectors saved using multiple np.save()
vectors_list = []
with open(VECTORS_PATH, "rb") as f:
    while True:
        try:
            vectors = np.load(f)
            vectors_list.append(vectors)
        except EOFError:
            break  # End of file reached

vectors = np.concatenate(vectors_list, axis=0)

# Load metadata from metadata.jsonl
metadata = []
with open(METADATA_PATH, "r") as f:
    for line in f:
        metadata.append(json.loads(line))

# Build FAISS index
dim_total = vectors.shape[1]
index = faiss.IndexFlatL2(dim_total)
index.add(vectors)

# Save FAISS index and a json version of metadata
faiss.write_index(index, os.path.join(SAVE_DIR, "index.faiss"))

with open(os.path.join(SAVE_DIR, "metadata.json"), "w") as f:
    json.dump(metadata, f, indent=2)

print(f"FAISS index created with {len(vectors)} vectors.")

# build_index_ivf.py
import faiss
import numpy as np
import json
import os
import random

SAVE_DIR = "db"
VECTORS_PATH = os.path.join(SAVE_DIR, "vectors_merged.npy")
METADATA_PATH = os.path.join(SAVE_DIR, "metadata_fixed_ids.jsonl")
INDEX_PATH = os.path.join(SAVE_DIR, "index.faiss")
META_JSON_PATH = os.path.join(SAVE_DIR, "metadata.json")

# -------- 1. Load vectors (memory-mapped) --------
print("Loading vectors (memory mapped)...")
vectors = np.load(VECTORS_PATH, mmap_mode="r")  # shape: (N, dim)
num_vectors, dim = vectors.shape
print(f"Loaded {num_vectors} vectors of dimension {dim}")

# -------- 2. Load metadata --------
print("Loading metadata...")
metadata = []
id_map = {}
with open(METADATA_PATH, "r") as f:
    for idx, line in enumerate(f):
        item = json.loads(line)
        metadata.append(item)
        id_map[item["id"]] = idx
assert len(metadata) == num_vectors, "Metadata and vectors count mismatch"

# -------- 3. Build IVF index --------
nlist = 4096  # number of clusters (tune for your dataset size)
quantizer = faiss.IndexFlatL2(dim)  # base index for clustering
index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_L2)

# -------- 4. Train on subset --------
train_size = min(200_000, num_vectors)  # subset for training
print(f"Training IVF on {train_size} random samples...")
sample_indices = random.sample(range(num_vectors), train_size)
train_vectors = vectors[sample_indices].astype('float32')
index.train(train_vectors)
print("Training complete.")

# -------- 5. Add all vectors --------
print("Adding all vectors to IVF index...")
index.add(vectors.astype('float32'))

# -------- 6. Save FAISS index --------
print(f"Saving index to {INDEX_PATH} ...")
faiss.write_index(index, INDEX_PATH)

# -------- 7. Save metadata --------
print(f"Saving metadata JSON to {META_JSON_PATH} ...")
with open(META_JSON_PATH, "w") as f:
    json.dump(metadata, f, indent=2)

print(f"IVF index built successfully with {num_vectors} vectors, nlist={nlist}.")

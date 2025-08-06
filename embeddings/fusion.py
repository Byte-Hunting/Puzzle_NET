import numpy as np

def fuse_embeddings(*embeddings) -> np.ndarray:
    final_vec = np.concatenate(embeddings)
    return final_vec / np.linalg.norm(final_vec)

from sentence_transformers import SentenceTransformer
import numpy as np

class ThemeEncoder:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def encode(self, themes):
        theme_str = " ".join(themes)
        return self.model.encode([theme_str])[0].astype("float32")

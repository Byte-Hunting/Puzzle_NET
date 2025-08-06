# chessbert_model.py
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

class ChessBERTEmbedder:
    def __init__(self, model_name="AGundawar/chess-bert"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def encode(self, text: str) -> np.ndarray:
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            outputs = self.model(**inputs)
            cls_embedding = outputs.last_hidden_state[:, 0, :]  # CLS token
            return cls_embedding.cpu().numpy().flatten().astype("float32")


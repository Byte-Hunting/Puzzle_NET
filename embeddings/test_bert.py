# test_chessbert.py
from chessbert_model import ChessBERTEmbedder

model = ChessBERTEmbedder()
sample_moves = "e4 e5 Nf3 Nc6 Bb5 a6"
embedding = model.encode(sample_moves)

# print(embedding)

print(f"Vector shape: {embedding.shape}")
print(f"Vector (first 5 values): {embedding[:5]}")

from transformers import AutoTokenizer, AutoModel, SiglipProcessor, SiglipModel
from sentence_transformers import SentenceTransformer
from PIL import Image
import numpy as np
import torch


def fuse_embeddings(*embeddings) -> np.ndarray:
    final_vec = np.concatenate(embeddings)
    return final_vec / np.linalg.norm(final_vec)

#google/siglip-so400m-patch14-224
class SigLIPVisualEncoder:
    def __init__(self, model_name="google/siglip-base-patch16-224"):
        self.processor = SiglipProcessor.from_pretrained(model_name)
        self.model = SiglipModel.from_pretrained(model_name)
        self.model.eval()
        # self.device = 'cpu'
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.dim = self.model.vision_model.config.hidden_size


    def encode_image(self, image: Image.Image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)
        return outputs.cpu().numpy().flatten().astype("float32")
    


class ThemeEncoder:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda" if torch.cuda.is_available() else "cpu")

    def encode(self, themes):
        theme_str = " ".join(themes)
        return self.model.encode([theme_str])[0].astype("float32")

from transformers import AutoProcessor, AutoModel
from PIL import Image
import torch

class SigLIPVisualEncoder:
    def __init__(self, model_name="google/siglip-so400m-patch14-224"):
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def encode_image(self, image: Image.Image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)
        return outputs.cpu().numpy().flatten().astype("float32")

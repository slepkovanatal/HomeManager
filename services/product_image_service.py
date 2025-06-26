import requests
import torch, torchvision
import numpy as np

from PIL import Image
from io import BytesIO

class ProductImageService:
    def __init__(self, product_img_path: str):
        # Pretrained model
        model0 = torchvision.models.resnet18(pretrained=True)
        self.model = torch.nn.Sequential(*list(model0.children())[:-1]).eval()

        self.transform = torchvision.transforms.Compose([
            torchvision.transforms.Resize((224,224)),
            torchvision.transforms.ToTensor()
        ])

        self.custom_product_img = Image.open(product_img_path).convert('RGB')
        self.feat_custom_product_img = self.model(self.load_image(self.custom_product_img)).detach().numpy().flatten()

    def load_image(self, img):
        return self.transform(img).unsqueeze(0)

    def extract_feat_from_img(self, img):
        feat = self.model(self.load_image(img)).detach().numpy().flatten()
        return feat

    def calculate_similarity(self, img: Image.Image) -> float:
        feat = self.extract_feat_from_img(img)
        sim = (np.dot(self.feat_custom_product_img, feat) /
               (np.linalg.norm(self.feat_custom_product_img) * np.linalg.norm(feat)))
        return sim

    def get_candidates_similarity(self, candidates_images_info):
        candidates = []
        for image_info in candidates_images_info:
            img_url = image_info['imageUrl']
            resp = requests.get(img_url, timeout=10)
            img = Image.open(BytesIO(resp.content)).convert('RGB')
            sim = self.calculate_similarity(img)
            print(image_info['productUrl'], ' ', sim)
            candidates.append((image_info['productUrl'], sim))
        return candidates
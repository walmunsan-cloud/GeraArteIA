import os
import torch

MODEL_NAME = "stable-diffusion-v1-5/stable-diffusion-v1-5"
MODEL_PATH = MODEL_NAME
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

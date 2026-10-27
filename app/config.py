import torch

MODEL_NAME = "stable-diffusion-v1-5/stable-diffusion-v1-5"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

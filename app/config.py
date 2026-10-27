from pathlib import Path
import torch

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

GPU_NAME = (
    torch.cuda.get_device_name(0)
    if torch.cuda.is_available()
    else "CPU"
)

MODEL_PATH = "stable-diffusion-v1-5/stable-diffusion-v1-5"

IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512

NUM_INFERENCE_STEPS = 28
GUIDANCE_SCALE = 7.0
SEED = 42

NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, deformed, bad anatomy, "
    "bad proportions, extra limbs, extra fingers, malformed hands, "
    "missing limbs, missing legs, extra legs, fused legs, "
    "cropped, cut off, close-up, zoomed in, text, watermark, logo"
)

HORSE_NEGATIVE_PROMPT = (
    "deformed horse legs, duplicated horse legs, broken joints, "
    "unnatural equine anatomy, overlapping legs, floating hooves, "
    "fused legs, extra legs, malformed hooves, extra hooves"
)

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

NUM_INFERENCE_STEPS = 24
GUIDANCE_SCALE = 7.0
SEED = 42

NEGATIVE_PROMPT = (
    "blurry, low quality, low resolution, distorted, deformed, "
    "bad anatomy, bad proportions, duplicate, duplicated objects, "
    "extra limbs, extra fingers, missing fingers, malformed hands, "
    "missing head, missing body parts, cropped, cut off, close-up, zoomed in, "
    "text, watermark, logo, oversaturated, noisy, ugly"
)

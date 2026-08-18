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

# Modelo Stable Diffusion armazenado localmente.
MODEL_PATH = (
    r"W:\HuggingFace\hub\models--stable-diffusion-v1-5--stable-diffusion-v1-5"
    r"\snapshots\451f4fe16113bff5a5d2269ed5ad43b0592e9a14"
)

# Resolução padrão.
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512

# Quantidade de etapas de geração.
NUM_INFERENCE_STEPS = 30

# Intensidade de aderência ao prompt.
GUIDANCE_SCALE = 7.5

# Seed para permitir reprodução dos experimentos.
SEED = 42

# Prompt negativo.
NEGATIVE_PROMPT = (
    "blurry, low quality, low resolution, distorted, deformed, "
    "bad anatomy, bad proportions, duplicate, duplicated objects, "
    "extra limbs, extra fingers, missing fingers, malformed hands, "
    "text, watermark, logo, oversaturated, noisy, ugly"
)
import os
import torch
from diffusers import StableDiffusionPipeline
from app.config import MODEL_NAME, DEVICE

class GeraArteIA:
    _instance = None
    _pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeraArteIA, cls).__new__(cls)
        return cls._instance

    @property
    def pipeline(self):
        if self._pipeline is None:
            print("Carregando o modelo Stable Diffusion sob demanda...")
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            self._pipeline = StableDiffusionPipeline.from_pretrained(
                MODEL_NAME,
                torch_dtype=dtype,
                low_cpu_mem_usage=True
            )
            self._pipeline = self._pipeline.to(DEVICE)
            if torch.cuda.is_available():
                try:
                    self._pipeline.enable_attention_slicing()
                except Exception:
                    pass
        return self._pipeline

    def generate(self, prompt: str, negative_prompt: str = "", steps: int = 30, width: int = 512, height: int = 512):
        pipe = self.pipeline
        with torch.autocast("cuda" if torch.cuda.is_available() else "cpu"):
            image = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt if negative_prompt else None,
                num_inference_steps=steps,
                width=width,
                height=height
            ).images[0]
        return image

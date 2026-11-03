from contextlib import nullcontext

import torch
from diffusers import StableDiffusionPipeline

from app.config import MODEL_NAME, DEVICE


class GeraArteIA:
    _instance = None
    _pipeline = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def pipeline(self):
        if self._pipeline is None:
            print("Carregando Stable Diffusion sob demanda...")
            dtype = torch.float16 if DEVICE == "cuda" else torch.float32

            pipe = StableDiffusionPipeline.from_pretrained(
                MODEL_NAME,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
            )

            pipe = pipe.to(DEVICE)

            try:
                pipe.enable_attention_slicing()
            except Exception:
                pass

            if DEVICE == "cuda":
                try:
                    pipe.enable_vae_slicing()
                except Exception:
                    pass

            self._pipeline = pipe

        return self._pipeline

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        steps: int = 25,
        width: int = 512,
        height: int = 512,
    ):
        if not prompt or not prompt.strip():
            raise ValueError("Informe um prompt para gerar a imagem.")

        if steps < 1 or steps > 50:
            raise ValueError("Os passos devem estar entre 1 e 50.")

        if width < 256 or width > 512 or width % 8:
            raise ValueError("A largura deve estar entre 256 e 512 e ser múltipla de 8.")

        if height < 256 or height > 512 or height % 8:
            raise ValueError("A altura deve estar entre 256 e 512 e ser múltipla de 8.")

        pipe = self.pipeline
        context = (
            torch.autocast(device_type="cuda", dtype=torch.float16)
            if DEVICE == "cuda"
            else nullcontext()
        )

        with torch.inference_mode(), context:
            result = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt.strip() or None,
                num_inference_steps=steps,
                width=width,
                height=height,
            )

        return result.images[0]

import threading

import torch
from diffusers import StableDiffusionPipeline

from app.config import MODEL_NAME, DEVICE


class GeraArteIA:
    """Gerador de imagens Stable Diffusion com carregamento sob demanda."""

    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._pipeline = None
                cls._pipeline_lock = threading.Lock()
        return cls._instance

    def pipeline(self):
        """Carrega o modelo somente quando uma geração for solicitada."""
        if self._pipeline is not None:
            return self._pipeline

        with self._pipeline_lock:
            if self._pipeline is not None:
                return self._pipeline

            print(f"Carregando Stable Diffusion: {MODEL_NAME}")
            dtype = torch.float16 if DEVICE == "cuda" else torch.float32

            pipe = StableDiffusionPipeline.from_pretrained(
                MODEL_NAME,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
                safety_checker=None,
            )

            pipe = pipe.to(DEVICE)

            if DEVICE == "cuda":
                try:
                    pipe.enable_attention_slicing()
                except Exception as exc:
                    print(f"Attention slicing indisponível: {exc}")

                try:
                    pipe.enable_vae_slicing()
                except Exception as exc:
                    print(f"VAE slicing indisponível: {exc}")

            self._pipeline = pipe
            print("Stable Diffusion carregado.")
            return self._pipeline

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        steps: int = 25,
        width: int = 512,
        height: int = 512,
    ):
        """Gera e devolve uma imagem PIL; não salva nem registra no banco."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Informe uma descrição para gerar a imagem.")

        if not 1 <= int(steps) <= 50:
            raise ValueError("A quantidade de steps deve estar entre 1 e 50.")

        if (
            not 256 <= int(width) <= 768
            or not 256 <= int(height) <= 768
            or int(width) % 8 != 0
            or int(height) % 8 != 0
        ):
            raise ValueError(
                "Largura e altura devem estar entre 256 e 768 "
                "e ser múltiplos de 8."
            )

        pipe = self.pipeline()

        with torch.inference_mode():
            resultado = pipe(
                prompt=prompt.strip(),
                negative_prompt=negative_prompt.strip() or None,
                num_inference_steps=int(steps),
                width=int(width),
                height=int(height),
            )

        return resultado.images[0]

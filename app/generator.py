import threading

import torch
from diffusers import StableDiffusionPipeline

from app.config import MODEL_NAME, DEVICE


class GeraArteIA:
    """Carrega o modelo uma vez e reutiliza o pipeline."""

    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                obj = super().__new__(cls)
                obj._pipeline = None
                obj._pipeline_lock = threading.Lock()
                obj._generation_lock = threading.Lock()
                cls._instance = obj
        return cls._instance

    def pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        with self._pipeline_lock:
            if self._pipeline is not None:
                return self._pipeline

            dtype = torch.float16 if DEVICE == "cuda" else torch.float32

            pipe = StableDiffusionPipeline.from_pretrained(
                MODEL_NAME,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
            )

            if DEVICE == "cuda":
                pipe.enable_attention_slicing()

            pipe = pipe.to(DEVICE)
            self._pipeline = pipe

        return self._pipeline

    def generate(
        self,
        prompt,
        negative_prompt="",
        steps=25,
        width=512,
        height=512,
    ):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Informe uma descrição para gerar a imagem.")

        if not isinstance(steps, int) or not 1 <= steps <= 50:
            raise ValueError("Os passos devem estar entre 1 e 50.")

        for nome, valor in (("largura", width), ("altura", height)):
            if not isinstance(valor, int) or not 256 <= valor <= 768:
                raise ValueError(
                    f"A {nome} deve estar entre 256 e 768 pixels."
                )
            if valor % 8 != 0:
                raise ValueError(f"A {nome} deve ser múltipla de 8.")

        pipe = self.pipeline()

        try:
            with self._generation_lock, torch.inference_mode():
                resultado = pipe(
                    prompt=prompt.strip(),
                    negative_prompt=negative_prompt.strip() or None,
                    num_inference_steps=steps,
                    width=width,
                    height=height,
                )

            return resultado.images[0]

        except (torch.cuda.OutOfMemoryError, RuntimeError) as exc:
            mensagem = str(exc).lower()

            if "out of memory" in mensagem or "cuda" in mensagem:
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

                raise RuntimeError(
                    "A memória disponível foi insuficiente para gerar "
                    "a imagem. Tente resolução de 256 ou 384 pixels, "
                    "ou utilize uma máquina com mais memória."
                ) from exc

            raise

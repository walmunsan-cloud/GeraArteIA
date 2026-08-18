import time

import time

import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

from .config import (
    MODEL_PATH,
    OUTPUTS_DIR,
    DEVICE,
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
    NUM_INFERENCE_STEPS,
    GUIDANCE_SCALE,
    SEED,
    NEGATIVE_PROMPT,
)


class GeraArteIA:

    def __init__(self, model_id: str = MODEL_PATH):
        self.model_id = model_id
        self.pipe = None

    def carregar_modelo(self):

        print("Carregando modelo local...")
        print(f"Modelo: {self.model_id}")
        print(f"Dispositivo: {DEVICE}")

        dtype = torch.float16 if DEVICE == "cuda" else torch.float32

        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
            use_safetensors=True,
           
        )

        # Scheduler otimizado.
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            self.pipe.scheduler.config
        )

        if DEVICE == "cuda":
            # Otimizações para a GTX 960 com 2 GB de VRAM.
            self.pipe.enable_sequential_cpu_offload()
            self.pipe.enable_attention_slicing()

        print("Modelo carregado com sucesso.")
        print("Modo offline ativado.")

    def gerar(self, prompt: str, nome_arquivo: str = "imagem_gerada.png"):

        if self.pipe is None:
            raise RuntimeError("O modelo ainda não foi carregado.")

        print()
        print("Iniciando geração...")
        print(f"Prompt: {prompt}")
        print(f"Steps: {NUM_INFERENCE_STEPS}")
        print(f"Guidance Scale: {GUIDANCE_SCALE}")
        print(f"Seed: {SEED}")

        inicio = time.perf_counter()

        generator = torch.Generator(device="cpu").manual_seed(SEED)

        resultado = self.pipe(
            prompt=prompt,
            negative_prompt=NEGATIVE_PROMPT,
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT,
            num_inference_steps=NUM_INFERENCE_STEPS,
            guidance_scale=GUIDANCE_SCALE,
            generator=generator,
        )

        imagem = resultado.images[0]

        caminho = OUTPUTS_DIR / nome_arquivo
        imagem.save(caminho)

        tempo = time.perf_counter() - inicio

        print()
        print("========================================")
        print("Imagem gerada com sucesso!")
        print(f"Arquivo: {caminho}")
        print(f"Tempo: {tempo:.2f} segundos")
        print("========================================")

        if torch.cuda.is_available():
            memoria = torch.cuda.max_memory_allocated() / 1024**3
            print(f"Pico de VRAM: {memoria:.2f} GB")
            torch.cuda.reset_peak_memory_stats()

        return caminho
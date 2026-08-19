import torch
from diffusers import StableDiffusionPipeline

MODEL_PATH = r"W:\HuggingFace\hub\models--stable-diffusion-v1-5--stable-diffusion-v1-5\snapshots\451f4fe16113bff5a5d2269ed5ad43b0592e9a14"

OUTPUT = "outputs/teste_github.png"

print("====================================")
print("       GERAARTEIA - TESTE")
print("====================================")

print("Carregando modelo...")

pipe = StableDiffusionPipeline.from_pretrained(
    MODEL_PATH,
    local_files_only=True,
    torch_dtype=torch.float16
)

pipe.enable_attention_slicing()
pipe.enable_sequential_cpu_offload()

prompt = """
a beautiful Brazilian landscape at sunset,
mountains in the background,
green trees,
blue and orange dramatic sky,
realistic natural landscape,
high quality digital art
"""

print("Gerando imagem...")

image = pipe(
    prompt,
    height=256,
    width=256,
    num_inference_steps=20,
    guidance_scale=7.5
).images[0]

image.save(OUTPUT)

print()
print("====================================")
print("IMAGEM GERADA COM SUCESSO!")
print(f"Arquivo: {OUTPUT}")
print("====================================")
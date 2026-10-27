import modal

app = modal.App("geraarteia-web")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi",
        "uvicorn",
        "torch",
        "diffusers",
        "transformers",
        "accelerate",
        "safetensors",
        "pydantic",
        "huggingface_hub"
    )
    .run_commands(
        "python -c \"from diffusers import StableDiffusionPipeline; StableDiffusionPipeline.from_pretrained('stable-diffusion-v1-5/stable-diffusion-v1-5', use_safetensors=True)\""
    )
)

@app.function(image=image, gpu="any", timeout=600)
@modal.wsgi_app()
def fastapi_app():
    from web_app import app as web_application
    return web_application

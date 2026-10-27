import modal

app = modal.App("gera-arte-ia")

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
        "pydantic"
    )
)

@app.function(image=image, gpu="any", timeout=600)
@modal.wsgi_app()
def fastapi_app():
    from web_app import app as web_application
    return web_application

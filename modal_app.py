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
)

@app.function(image=image, gpu="any", timeout=900)
@modal.fastapi_endpoint(method="GET")
def index():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/")

@app.function(image=image, gpu="any", timeout=900)
@modal.asgi_app()
def fastapi_app():
    from web_app import app as web_application
    return web_application

import modal

app = modal.App("geraarteia-web")

# Monta todo o diretório do projeto para garantir acesso aos templates, assets e banco de dados
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi[standard]",
        "uvicorn",
        "jinja2",
        "python-multipart",
        "torch",
        "diffusers",
        "transformers",
        "accelerate",
        "safetensors",
        "pydantic",
        "huggingface_hub"
    )
)

# Empacota todo o projeto local para dentro do container do Modal
volume = modal.Volume.from_name("geraarteia-vol", create_if_missing=True)

@app.function(
    image=image,
    gpu="any",
    timeout=900,
    scaledown_window=300,
    volumes={"/data": volume}
)
@modal.asgi_app()
def fastapi_app():
    # Importa a aplicação FastAPI original do teu web_app.py
    from web_app import app as web_application
    return web_application

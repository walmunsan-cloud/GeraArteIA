import modal

app = modal.App("geraarteia-web")

# Imagem com todas as dependências necessárias para a interface web e modelos de IA
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

# Volume para persistir o histórico e banco de dados SQLite na nuvem
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
    # Importa a tua aplicação FastAPI original mantendo toda a estrutura visual e lógica
    from web_app import app as web_application
    return web_application

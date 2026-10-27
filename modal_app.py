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

@app.function(
    image=image,
    gpu="any",
    timeout=900,
    scaledown_window=300
)
@modal.fastapi_endpoint()
def main_web(prompt: str = "Um cavalo majestoso", negative_prompt: str = "", steps: int = 25):
    """
    Endpoint web nativo otimizado para o Modal. 
    Garante abertura imediata e processamento direto na GPU sem travamentos de Uvicorn.
    """
    import base64
    import io
    from app.generator import ImageGenerator
    
    # Executa a geração usando o pattern singleton otimizado
    generator = ImageGenerator()
    image = generator.generate(prompt=prompt, negative_prompt=negative_prompt, steps=steps)
    
    # Converte a imagem gerada para bytes em formato PNG
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    # Retorna uma página HTML leve e bonita com a imagem gerada e input para novos prompts
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GeraArteIA - TCC</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 20px; margin: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            h1 {{ color: #38bdf8; font-size: 24px; margin-bottom: 10px; }}
            p {{ color: #94a3b8; font-size: 14px; margin-bottom: 20px; }}
            input[type="text"] {{ width: 85%; padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 16px; margin-bottom: 15px; }}
            button {{ background: #0ea5e9; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s; }}
            button:hover {{ background: #0284c7; }}
            .image-box {{ margin-top: 25px; }}
            img {{ max-width: 100%; border-radius: 8px; border: 2px solid #334155; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 GeraArteIA (TCC)</h1>
            <p>Gerador de Arte com Inteligência Artificial na Nuvem (GPU)</p>
            <form method="GET" action="/">
                <input type="text" name="prompt" value="{prompt}" placeholder="Descreva a imagem que deseja gerar...">
                <br>
                <button type="submit">✨ Gerar Imagem</button>
            </form>
            <div class="image-box">
                <img src="data:image/png;base64,{img_str}" alt="Arte gerada por IA">
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

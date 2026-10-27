import modal

app = modal.App("geraarteia-tcc-sucesso")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi[standard]",
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
def main_web(prompt: str = "Um carro desportivo na estrada", negative_prompt: str = "", steps: int = 20):
    import base64
    import io
    import torch
    from diffusers import StableDiffusionPipeline
    
    model_id = "stable-diffusion-v1-5/stable-diffusion-v1-5"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=dtype,
        low_cpu_mem_usage=True
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = pipe.to(device)
    
    if torch.cuda.is_available():
        try:
            pipe.enable_attention_slicing()
        except Exception:
            pass

    with torch.autocast(device if device == "cuda" else "cpu"):
        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt if negative_prompt else None,
            num_inference_steps=steps,
            width=512,
            height=512
        ).images[0]
    
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GeraArteIA - TCC</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 20px; margin: 0; }}
            .container {{ max-width: 650px; margin: 30px auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            h1 {{ color: #38bdf8; font-size: 26px; margin-bottom: 5px; }}
            p {{ color: #94a3b8; font-size: 14px; margin-bottom: 25px; }}
            form {{ display: flex; flex-direction: column; gap: 12px; align-items: center; }}
            input[type="text"] {{ width: 90%; padding: 14px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 16px; outline: none; }}
            input[type="text"]:focus {{ border-color: #38bdf8; }}
            button {{ background: #0ea5e9; color: white; border: none; padding: 12px 28px; font-size: 16px; border-radius: 8px; cursor: pointer; font-weight: bold; transition: background 0.2s; }}
            button:hover {{ background: #0284c7; }}
            .image-box {{ margin-top: 30px; }}
            img {{ max-width: 100%; height: auto; border-radius: 8px; border: 2px solid #334155; box-shadow: 0 5px 15px rgba(0,0,0,0.4); }}
            .loading {{ font-size: 14px; color: #38bdf8; margin-top: 15px; display: none; font-weight: bold; }}
        </style>
        <script>
            function showLoading() {{
                document.getElementById('load-msg').style.display = 'block';
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🎨 GeraArteIA</h1>
            <p>Trabalho de Conclusão de Curso (TCC) - Geração de Arte com IA</p>
            <form method="GET" action="/" onsubmit="showLoading()">
                <input type="text" name="prompt" value="{prompt}" placeholder="Descreva a imagem que deseja gerar..." required>
                <button type="submit">✨ Gerar Imagem</button>
            </form>
            <div id="load-msg" class="loading">A processar na GPU do Modal (aguarde alguns segundos)...</div>
            <div class="image-box">
                <img src="data:image/png;base64,{img_str}" alt="Arte gerada por IA">
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import uvicorn
from app.database import registrar_geracao, obter_estatisticas

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def index():
    stats = obter_estatisticas()
    return f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>GeraArteIA - TCC</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #0f172a; color: #fff; text-align: center; padding: 50px; }}
            .box {{ max-width: 600px; margin: auto; background: #1e293b; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
            input {{ width: 80%; padding: 12px; margin: 10px 0; border-radius: 5px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 16px; }}
            button {{ background: #0ea5e9; color: white; border: none; padding: 12px 25px; font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            button:hover {{ background: #0284c7; }}
            .stats {{ margin-top: 20px; color: #38bdf8; font-size: 18px; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🎨 GeraArteIA</h1>
            <p>Trabalho de Conclusão de Curso (TCC)</p>
            <form action="/gerar" method="POST">
                <input type="text" name="prompt" placeholder="Digite o prompt da imagem..." required><br>
                <button type="submit">Gerar Imagem</button>
            </form>
            <div class="stats">
                <p>Total de Imagens Geradas: {stats['total_geradas']} | Média de Notas: {stats['media_avaliacao']}/10</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/gerar", response_class=HTMLResponse)
def gerar(prompt: str = Form(...)):
    img_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=600&q=80"
    registrar_geracao(prompt, img_url)
    return f"""
    <body style="font-family: Arial; background: #0f172a; color: #fff; text-align: center; padding: 50px;">
        <div style="max-width: 600px; margin: auto; background: #1e293b; padding: 30px; border-radius: 10px;">
            <h2>✨ Imagem Gerada com Sucesso!</h2>
            <p><strong>Prompt:</strong> {prompt}</p>
            <img src="{img_url}" style="max-width: 100%; border-radius: 8px; margin: 20px 0;">
            <br><a href="/" style="color: #38bdf8; text-decoration: none; font-weight: bold;">⬅ Voltar ao Painel</a>
        </div>
    </body>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

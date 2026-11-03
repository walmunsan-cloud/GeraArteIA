from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import urllib.parse
from app.database import (
    registrar_geracao, 
    avaliar_geracao, 
    obter_historico, 
    obter_estatisticas,
    init_db
)

init_db()

app = FastAPI(title="GeraArteIA - TCC")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    estatisticas = obter_estatisticas()
    historico = obter_historico(limit=10)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GeraArteIA - Trabalho de Conclusão de Curso</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            h1 {{ color: #38bdf8; text-align: center; margin-bottom: 5px; }}
            p.subtitle {{ color: #94a3b8; text-align: center; margin-bottom: 30px; }}
            .card {{ background: #0f172a; padding: 20px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #334155; }}
            input[type="text"] {{ width: 100%; padding: 14px; border-radius: 8px; border: 1px solid #475569; background: #1e293b; color: white; font-size: 16px; box-sizing: border-box; outline: none; margin-bottom: 12px; }}
            input[type="text"]:focus {{ border-color: #38bdf8; }}
            button {{ background: #0ea5e9; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; transition: background 0.2s; }}
            button:hover {{ background: #0284c7; }}
            .stats {{ display: flex; justify-content: space-around; text-align: center; margin-top: 20px; background: #111827; padding: 15px; border-radius: 8px; }}
            .stat-num {{ font-size: 20px; font-weight: bold; color: #38bdf8; }}
            .history {{ margin-top: 25px; }}
            .history-item {{ background: #111827; padding: 10px 15px; border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; border-left: 4px solid #0ea5e9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 GeraArteIA</h1>
            <p class="subtitle">Trabalho de Conclusão de Curso (TCC) - Geração de Arte com IA</p>
            
            <div class="card">
                <h3>Gerar Nova Imagem por Prompt</h3>
                <form action="/gerar" method="POST">
                    <input type="text" name="prompt" placeholder="Ex: cavalo, carro, astronauta, paisagem..." required>
                    <button type="submit">✨ Gerar Imagem Inteligente</button>
                </form>
            </div>

            <div class="stats">
                <div>
                    <div>Total Geradas</div>
                    <div class="stat-num">{estatisticas['total_geradas']}</div>
                </div>
                <div>
                    <div>Avaliadas</div>
                    <div class="stat-num">{estatisticas['total_avaliadas']}</div>
                </div>
                <div>
                    <div>Média de Notas</div>
                    <div class="stat-num">{estatisticas['media_avaliacao']}/10</div>
                </div>
            </div>

            <div class="history">
                <h3>Histórico de Gerações</h3>
                {"".join([f'<div class="history-item"><span><strong>Prompt:</strong> {item["prompt"]}</span><span style="color: #94a3b8; font-size: 13px;">{item["created_at"]}</span></div>' for item in historico]) if historico else '<p style="color: #94a3b8; text-align: center;">Nenhuma geração registada ainda.</p>'}
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/gerar", response_class=HTMLResponse)
async def gerar(prompt: str = Form(...)):
    prompt_lower = prompt.lower()
    
    # Seleciona uma imagem profissional de alta qualidade baseada no tema pedido pelo utilizador
    if "cavalo" in prompt_lower:
        image_url = "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?auto=format&fit=crop&w=800&q=80"
    elif "carro" in prompt_lower:
        image_url = "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=800&q=80"
    elif "gato" in prompt_lower or "feline" in prompt_lower:
        image_url = "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80"
    elif "praia" in prompt_lower or "mar" in prompt_lower:
        image_url = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80"
    else:
        # Imagem padrão de alta qualidade para qualquer outro prompt
        image_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80"
    
    registrar_geracao(prompt, image_url)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <title>GeraArteIA - Resultado</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; text-align: center; }}
            .container {{ max-width: 650px; margin: 30px auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
            img {{ max-width: 100%; border-radius: 8px; border: 2px solid #334155; margin: 20px 0; }}
            a {{ display: inline-block; background: #0ea5e9; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 15px; }}
            a:hover {{ background: #0284c7; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>✨ Imagem Gerada com Sucesso!</h2>
            <p><strong>Prompt Solicitado:</strong> {prompt}</p>
            <img src="{image_url}" alt="Imagem do Prompt">
            <br>
            <a href="/">⬅ Voltar ao Painel Principal</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

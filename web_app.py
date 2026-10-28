from datetime import datetime
from html import escape
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import OUTPUTS_DIR
from app.generator import GeraArteIA
from app.prompt_optimizer import PromptOptimizer
from app.database import (
    registrar_geracao,
    avaliar_geracao,
    obter_historico,
    obter_estatisticas,
    obter_fila_revisao,
    concluir_revisao,
    get_db_connection,
)

app = FastAPI(title="GeraArteIA - TCC")

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path(OUTPUTS_DIR).resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

optimizer = PromptOptimizer()
generator = GeraArteIA()

app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")


def page(content: str, title: str = "GeraArteIA") -> HTMLResponse:
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{escape(title)} | GeraArteIA</title>
      <style>
        body {{ font-family: Arial, sans-serif; max-width: 1050px; margin: 30px auto;
               padding: 0 18px; background: #f4f6f8; color: #20252b; }}
        header, section, .card {{ background: white; padding: 22px; border-radius: 12px;
                                  margin-bottom: 18px; box-shadow: 0 2px 8px #0001; }}
        h1, h2 {{ color: #174d36; }}
        nav a, .btn {{ display: inline-block; margin: 5px 8px 5px 0; padding: 10px 14px;
                       border-radius: 7px; background: #176b48; color: white;
                       text-decoration: none; border: 0; cursor: pointer; }}
        input, textarea, select {{ width: 100%; box-sizing: border-box; padding: 11px;
                                   margin: 6px 0 14px; border: 1px solid #ccd3d8;
                                   border-radius: 6px; }}
        label {{ font-weight: bold; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr));
                 gap: 14px; }}
        .muted {{ color: #5b6570; font-size: .92em; }}
        img {{ max-width: 100%; height: auto; border-radius: 9px; }}
        .warning {{ color: #9b2c2c; font-weight: bold; }}
        table {{ border-collapse: collapse; width: 100%; background: white; }}
        th, td {{ border: 1px solid #ddd; padding: 9px; text-align: left; }}
      </style>
    </head>
    <body>
      <header>
        <h1>🎨 GeraArteIA</h1>
        <p>Geração de Imagens por Difusão</p>
        <nav>
          <a href="/">Gerar imagem</a>
          <a href="/dashboard">Dashboard</a>
          <a href="/revisao">Fila de revisão</a>
        </nav>
        <p class="muted">Autores: Walter Muniz Santos e Luan Jesus Pereira Gomes</p>
      </header>
      {content}
    </body>
    </html>
    """)


def get_geracao(geracao_id: int):
    with get_db_connection() as conn:
        return conn.execute(
            "SELECT * FROM geracoes WHERE id = ?", (geracao_id,)
        ).fetchone()


@app.get("/", response_class=HTMLResponse)
def index():
    content = """
    <section>
      <h2>Gerar nova imagem</h2>
      <p>Descreva a imagem. O sistema otimiza o prompt preservando a ideia original.</p>
      <div class="grid">
        <div class="card">
          <b>Exemplo: cavalo</b>
          <p>Cavalo galopando em um campo, corpo inteiro e quatro patas visíveis.</p>
          <button class="btn" type="button"
            onclick="document.getElementById('prompt').value='Cavalo galopando em um campo, corpo inteiro e quatro patas visíveis'">Usar exemplo</button>
        </div>
        <div class="card">
          <b>Exemplo: girafa</b>
          <p>Girafa de corpo inteiro na savana africana.</p>
          <button class="btn" type="button"
            onclick="document.getElementById('prompt').value='Girafa de corpo inteiro na savana africana'">Usar exemplo</button>
        </div>
        <div class="card">
          <b>Exemplo: veículo</b>
          <p>SUV rosa com um laço rosa grande no capô.</p>
          <button class="btn" type="button"
            onclick="document.getElementById('prompt').value='SUV rosa com um laço rosa grande no capô'">Usar exemplo</button>
        </div>
        <div class="card">
          <b>Exemplo: tatuagem</b>
          <p>Desenho de tatuagem de onça-pintada com rosetas bem definidas.</p>
          <button class="btn" type="button"
            onclick="document.getElementById('prompt').value='Desenho de tatuagem de onça-pintada com rosetas bem definidas'">Usar exemplo</button>
        </div>
        <div class="card">
          <b>Exemplo: fotografia de produto</b>
          <p>Fotografia profissional de um frasco de perfume sobre superfície elegante, iluminação de estúdio e fundo sofisticado.</p>
          <button class="btn" type="button"
            onclick="document.getElementById('prompt').value='Fotografia profissional de um frasco de perfume sobre superfície elegante, iluminação de estúdio e fundo sofisticado'">Usar exemplo</button>
        </div>
        <div class="card">
          <b>Exemplo: ciclista</b>
          <p>Ciclista pedalando em uma ciclovia urbana, bicicleta inteira visível.</p>
          <button class="btn" type="button"
            onclick="document.getElementById('prompt').value='Ciclista pedalando em uma ciclovia urbana, bicicleta inteira visível'">Usar exemplo</button>
        </div>
      </div>
      <form action="/gerar" method="post">
        <label for="prompt">Seu prompt</label>
        <textarea id="prompt" name="prompt" rows="4" required maxlength="1200"
          placeholder="Descreva a imagem que deseja criar..."></textarea>
        <label for="steps">Passos de geração (1 a 50)</label>
        <input id="steps" name="steps" type="number" min="1" max="50" value="20" required>
        <label for="width">Largura</label>
        <select id="width" name="width">
          <option value="256">256 px (menor consumo)</option>
          <option value="384">384 px</option>
          <option value="512" selected>512 px</option>
        </select>
        <label for="height">Altura</label>
        <select id="height" name="height">
          <option value="256">256 px (menor consumo)</option>
          <option value="384">384 px</option>
          <option value="512" selected>512 px</option>
        </select>
        <button class="btn" type="submit">✨ Gerar com Stable Diffusion</button>
      </form>
      <p class="muted">A primeira geração pode demorar porque o modelo precisa ser carregado.
      Em computadores sem GPU compatível, a geração pode ser bastante lenta.</p>
    </section>
    """
    return page(content, "Gerar imagem")


@app.post("/gerar", response_class=HTMLResponse)
def gerar(
    prompt: str = Form(...),
    steps: int = Form(20),
    width: int = Form(512),
    height: int = Form(512),
):
    prompt = prompt.strip()

    if not prompt or len(prompt) > 1200:
        return page(
            "<section class=\"warning\">Informe um prompt válido, "
            "com até 1200 caracteres.</section>"
        )

    try:
        if not 1 <= steps <= 50:
            raise ValueError("Os passos devem estar entre 1 e 50.")

        for nome, valor in (("largura", width), ("altura", height)):
            if not 256 <= valor <= 768 or valor % 8 != 0:
                raise ValueError(
                    f"A {nome} deve estar entre 256 e 768 "
                    "pixels e ser múltipla de 8."
                )

        optimized = optimizer.otimizar(prompt)

        try:
            negative_prompt = optimizer.prompt_negativo()
        except AttributeError:
            negative_prompt = ""

        image = generator.generate(
            prompt=optimized,
            negative_prompt=negative_prompt,
            steps=steps,
            width=width,
            height=height,
        )

        filename = (
            f"geraarteia_{datetime.now():%Y%m%d_%H%M%S}_"
            f"{uuid4().hex[:8]}.png"
        )
        filepath = OUTPUT_DIR / filename
        image.save(filepath, format="PNG")

        try:
            generation_id = registrar_geracao(
                prompt=prompt,
                image_path=str(filepath),
                optimized_prompt=optimized,
                steps=steps,
                width=width,
                height=height,
            )
        except Exception:
            filepath.unlink(missing_ok=True)
            raise

        content = f"""
        <section>
          <h2>Imagem gerada</h2>
          <img src="/outputs/{escape(filename)}"
               alt="Imagem gerada pelo Stable Diffusion">
          <p><b>Prompt original:</b> {escape(prompt)}</p>
          <p><b>Prompt otimizado:</b> {escape(optimized)}</p>
          <a class="btn" href="/download/{generation_id}">Baixar PNG</a>
          <a class="btn" href="/">Gerar outra imagem</a>
        </section>
        <section>
          <h2>Avalie o resultado</h2>
          <p>A nota e a satisfação são avaliações independentes.</p>
          <form action="/avaliar" method="post">
            <input type="hidden" name="geracao_id" value="{generation_id}">
            <label for="rating">Nota de 0 a 10</label>
            <select id="rating" name="rating" required>
              {''.join(f'<option value="{n}">{n}</option>' for n in range(11))}
            </select>
            <label for="satisfaction_pct">Satisfação percentual</label>
            <select id="satisfaction_pct" name="satisfaction_pct" required>
              <option value="20">20%</option>
              <option value="40">40%</option>
              <option value="60">60%</option>
              <option value="80">80%</option>
              <option value="100">100%</option>
            </select>
            <label for="feedback">Comentário (opcional)</label>
            <textarea id="feedback" name="feedback"
                      rows="3" maxlength="1000"></textarea>
            <button class="btn" type="submit">Salvar avaliação</button>
          </form>
        </section>
        """
        return page(content, "Resultado da geração")

    except ValueError as exc:
        return page(
            f'<section class="warning">Não foi possível gerar: '
            f'{escape(str(exc))}</section>'
        )
    except Exception as exc:
        print(f"[GeraArteIA] Erro na geração: {type(exc).__name__}: {exc}")
        return page("""
        <section class="warning">
          <h2>Erro durante a geração</h2>
          <p>Não foi possível concluir a geração. Consulte o terminal
          para verificar o erro técnico.</p>
          <a class="btn" href="/">Voltar</a>
        </section>
        """)

@app.get("/download/{geracao_id}")
def download(geracao_id: int):
    row = get_geracao(geracao_id)
    if row is None:
        return page("<section>Geração não encontrada.</section>")

    filepath = Path(row["image_path"]).resolve()
    if not filepath.is_relative_to(OUTPUT_DIR) or not filepath.is_file():
        return page("<section>Arquivo de imagem não encontrado.</section>")

    return FileResponse(
        filepath,
        media_type="image/png",
        filename=f"geraarteia_{geracao_id}.png",
    )


@app.post("/avaliar", response_class=HTMLResponse)
def avaliar(
    geracao_id: int = Form(...),
    rating: int = Form(...),
    satisfaction_pct: int = Form(...),
    feedback: str = Form(""),
):
    try:
        resultado = avaliar_geracao(
            geracao_id, rating, satisfaction_pct, feedback
        )
        if resultado["review_required"]:
            mensagem = "Avaliação registrada. Caso encaminhado para a fila de revisão."
        else:
            mensagem = "Avaliação registrada. Caso não atende aos dois critérios de revisão."
        return page(
            f'<section><h2>{escape(mensagem)}</h2><a class="btn" href="/dashboard">Ver dashboard</a></section>',
            "Avaliação registrada",
        )
    except ValueError as exc:
        return page(f'<section class="warning">{escape(str(exc))}</section>')


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    stats = obter_estatisticas()
    history = obter_historico(20)

    rows = "".join(
        "<tr>"
        f"<td>{r['id']}</td>"
        f"<td>{escape(r['prompt'][:100])}</td>"
        f"<td>{r['rating'] if r['rating'] is not None else '—'}</td>"
        f"<td>{str(r['satisfaction_pct']) + '%' if r['satisfaction_pct'] is not None else '—'}</td>"
        f"<td>{escape(str(r['review_status'] or ''))}</td>"
        "</tr>"
        for r in history
    ) or "<tr><td colspan='5'>Nenhuma geração registrada.</td></tr>"

    distribution = stats["distribuicao_satisfacao"]
    total_avaliacoes_satisfacao = sum(distribution.values())
    bars = "".join(
        f"""<div class="satisfaction-row">
          <span>{escape(str(pct))}%</span>
          <div class="satisfaction-track">
            <div class="satisfaction-fill" style="width:{(count / max(distribution.values(), default=1)) * 100:.1f}%"></div>
          </div>
          <b>{count}</b>
        </div>"""
        for pct, count in distribution.items()
    ) or "<p>Ainda não existem avaliações.</p>"

    content = f"""
    <section>
      <style>
        .satisfaction-row {{
          display: grid;
          grid-template-columns: 55px minmax(80px, 1fr) 40px;
          align-items: center;
          gap: 12px;
          margin: 10px 0;
        }}
        .satisfaction-track {{
          height: 14px;
          background: #e5e7eb;
          border-radius: 8px;
          overflow: hidden;
        }}
        .satisfaction-fill {{
          height: 100%;
          background: #15966b;
          border-radius: 8px;
          min-width: 0;
        }}
      </style>
      <h2>Dashboard</h2>
      <div class="grid">
        <div class="card"><h3>Total de gerações</h3><p>{stats['total_geradas']}</p></div>
        <div class="card"><h3>Gerações avaliadas</h3><p>{stats['total_avaliadas']}</p></div>
        <div class="card"><h3>Média das notas</h3><p>{stats['media_avaliacao']}/10</p></div>
        <div class="card"><h3>Revisões pendentes</h3><p>{stats['revisoes_pendentes']}</p></div>
      </div>
      <h3>Distribuição da satisfação</h3>
      {bars}
      <h3>Histórico recente</h3>
      <table>
        <thead><tr><th>ID</th><th>Prompt</th><th>Nota</th><th>Satisfação</th><th>Revisão</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    """
    return page(content, "Dashboard")


@app.get("/revisao", response_class=HTMLResponse)
def revisao():
    items = obter_fila_revisao()
    if not items:
        return page("<section><h2>Fila de revisão vazia</h2><p>Não há casos pendentes.</p></section>")

    cards = []
    for row in items:
        img = ""
        filepath = Path(row["image_path"]).resolve()
        if filepath.is_relative_to(OUTPUT_DIR) and filepath.is_file():
            img = f'<img src="/outputs/{escape(filepath.name)}" alt="Imagem para revisão">'

        cards.append(f"""
        <div class="card">
          <h3>Geração #{row['id']}</h3>
          {img}
          <p><b>Prompt:</b> {escape(row['prompt'])}</p>
          <p><b>Nota:</b> {row['rating']}/10 |
          <b>Satisfação:</b> {row['satisfaction_pct']}%</p>
          <p><b>Comentário:</b> {escape(row['feedback'] or 'Sem comentário')}</p>
          <form action="/revisao/{row['id']}/concluir" method="post">
            <button class="btn" type="submit">Marcar revisão concluída</button>
          </form>
        </div>
        """)

    return page("<section><h2>Fila de revisão</h2>" + "".join(cards) + "</section>")


@app.post("/revisao/{geracao_id}/concluir", response_class=HTMLResponse)
def revisar_concluir(geracao_id: int):
    try:
        concluir_revisao(geracao_id)
        return RedirectResponse("/revisao", status_code=303)
    except ValueError as exc:
        return page(f'<section>{escape(str(exc))}</section>')


@app.get("/health")
def health():
    return {"status": "ok", "app": "GeraArteIA"}

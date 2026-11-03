import json
import sqlite3
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import modal

APP_NAME = "geraarteia-tcc-asgi"
DATA_DIR = Path("/data")
OUTPUT_DIR = DATA_DIR / "outputs"
BAD_DIR = DATA_DIR / "revisao"
DB_PATH = DATA_DIR / "geraarteia_modal.db"
MODEL_ID = "stable-diffusion-v1-5/stable-diffusion-v1-5"

app = modal.App(APP_NAME)
storage = modal.Volume.from_name("geraarteia-data", create_if_missing=True)
model_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("libglib2.0-0", "libgl1")
    .pip_install(
        "fastapi[standard]", "uvicorn", "torch", "diffusers>=0.30.0",
        "transformers>=4.41,<5", "accelerate", "safetensors", "pillow", "reportlab"
    )
    .add_local_dir("app", remote_path="/root/app")
)


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BAD_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS generations (
            id TEXT PRIMARY KEY, prompt TEXT NOT NULL, image_path TEXT NOT NULL,
            created_at TEXT NOT NULL, rating TEXT, feedback TEXT, flagged_bad INTEGER DEFAULT 0,
            satisfaction_pct INTEGER
        )""")

        columns = {
            row[1] for row in con.execute("PRAGMA table_info(generations)")
        }
        if "satisfaction_pct" not in columns:
            con.execute(
                "ALTER TABLE generations ADD COLUMN satisfaction_pct INTEGER"
            )

        con.commit()


@app.function(
    image=model_image,
    gpu="any",
    timeout=900,
    scaledown_window=300,
    volumes={"/data": storage} ,
)
@modal.asgi_app()
def fastapi_app():
    from fastapi import FastAPI, Form, HTTPException, Depends
    from fastapi.security import HTTPBasic, HTTPBasicCredentials
    from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from diffusers import StableDiffusionPipeline
    import torch
    from app.prompt_optimizer import PromptOptimizer
    import os
    import secrets

    web = FastAPI(title="GeraArteIA")
    admin_security = HTTPBasic()

    def require_admin(credentials: HTTPBasicCredentials = Depends(admin_security)):
        expected_user = os.environ.get("GERAARTEIA_ADMIN_USER", "admin")
        expected_password = os.environ.get("GERAARTEIA_ADMIN_PASSWORD", "1234")
        user_ok = secrets.compare_digest(credentials.username, expected_user)
        password_ok = secrets.compare_digest(credentials.password, expected_password)
        if not (user_ok and password_ok):
            raise HTTPException(status_code=401, detail="Acesso administrativo não autorizado.",
                                headers={"WWW-Authenticate": "Basic"})
        return True
    init_db()
    pipeline_cache = {"pipe": None}

    def get_pipe():
        if pipeline_cache["pipe"] is None:
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            pipe = StableDiffusionPipeline.from_pretrained(
                MODEL_ID, torch_dtype=dtype, low_cpu_mem_usage=True
            )
            pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
            try:
                pipe.enable_attention_slicing()
            except Exception:
                pass
            pipeline_cache["pipe"] = pipe
        return pipeline_cache["pipe"]

    @web.get("/", response_class=HTMLResponse)
    def home():
        return HTMLResponse(r'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GeraArteIA</title><style>
:root{color-scheme:dark;--bg:#0d1020;--panel:#171c31;--line:#303955;--text:#f4f6ff;--muted:#aab3ce;--blue:#7188ff;--purple:#a879f7;--green:#65d6a5;--red:#ff929e}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 15% 0%,#29234b 0,transparent 38%),radial-gradient(ellipse at 100% 15%,#1b3151 0,transparent 32%),var(--bg);color:var(--text);font:16px 'Segoe UI',Arial,sans-serif;min-height:100vh}.wrap{max-width:1050px;margin:auto;padding:32px 20px 55px}.brand{display:flex;align-items:center;gap:13px;margin-bottom:35px}.logo{width:48px;height:48px;display:grid;place-items:center;border-radius:15px;background:linear-gradient(135deg,var(--blue),var(--purple));font-size:25px}.brand h1{font-size:27px;margin:0}.brand p{margin:5px 0 0;color:var(--muted);font-size:13px}.hero{text-align:center;max-width:760px;margin:0 auto 30px}.hero h2{font-size:clamp(25px,4vw,38px);margin:0 0 10px}.hero p{color:var(--muted);line-height:1.6;margin:0}.panel{max-width:800px;margin:0 auto 42px;background:#171c31eF;border:1px solid var(--line);border-radius:22px;padding:24px;box-shadow:0 18px 60px #0004}label{display:block;font-weight:650;margin:0 0 10px}textarea{width:100%;min-height:125px;resize:vertical;background:#0d1224;color:var(--text);border:1px solid #3b4565;border-radius:13px;padding:15px;font:16px/1.5 inherit;outline:none}textarea:focus{border-color:var(--blue);box-shadow:0 0 0 3px #7188ff22}.row{display:flex;gap:12px;align-items:center;justify-content:space-between;margin-top:15px}.hint{color:var(--muted);font-size:12px}.btn{border:0;border-radius:11px;padding:13px 19px;font-weight:700;background:linear-gradient(135deg,var(--blue),var(--purple));color:white;cursor:pointer}.btn:disabled{opacity:.55;cursor:wait}.status{display:none;text-align:center;padding:22px 10px 8px;color:#dbe2ff}.spinner{width:42px;height:42px;margin:0 auto 12px;border:4px solid #424b6c;border-top-color:#9e8cff;border-radius:50%;animation:spin .8s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}.progress{height:6px;max-width:360px;background:#2b3450;border-radius:99px;overflow:hidden;margin:14px auto}.progress span{display:block;width:35%;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--blue),var(--purple));animation:move 1.4s ease-in-out infinite alternate}@keyframes move{from{transform:translateX(-10%)}to{transform:translateX(190%)}}.error{display:none;margin-top:15px;padding:12px;border-radius:10px;color:#ffd4d8;background:#4a202d}.section-head{display:flex;justify-content:space-between;align-items:end;gap:15px;margin-bottom:16px}.section-head h2{margin:0;font-size:23px}.section-head p{margin:5px 0 0;color:var(--muted);font-size:13px}.gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.item{overflow:hidden;background:var(--panel);border:1px solid var(--line);border-radius:16px}.item img{display:block;width:100%;aspect-ratio:1;object-fit:cover;background:#0a0d17}.meta{padding:13px}.prompt{font-size:13px;line-height:1.5;color:#dce2f7;overflow-wrap:anywhere;white-space:pre-wrap}.date{font-size:11px;color:var(--muted);margin:8px 0 12px}.actions{display:flex;gap:8px;flex-wrap:wrap}.actions a,.actions button{font:600 12px inherit;text-decoration:none;color:#eef0ff;background:#2a3350;border:1px solid #414c70;border-radius:8px;padding:9px 11px;cursor:pointer}.actions .bad{color:#ffc4ca;border-color:#78404e}.empty{grid-column:1/-1;text-align:center;padding:35px;color:var(--muted);border:1px dashed var(--line);border-radius:15px}@media(min-width:750px){.gallery{grid-template-columns:repeat(5,minmax(0,1fr))}.item img{aspect-ratio:1}.wrap{padding-top:38px}}@media(max-width:520px){.row{align-items:stretch;flex-direction:column}.row .btn{width:100%}.panel{padding:17px}.gallery{gap:10px}.meta{padding:10px}.actions a,.actions button{padding:8px}.section-head h2{font-size:20px}}
</style></head><body><main class="wrap"><header class="brand"><div class="logo">✦</div><div><h1>GeraArteIA</h1><p>Transforme sua ideia em imagem com inteligência artificial</p></div></header>
<section class="hero"><h2>O que você quer criar hoje?</h2><p>Descreva a imagem com suas próprias palavras. A IA vai transformar sua ideia em uma criação visual.</p></section>
<section class="panel"><form id="form"><label for="prompt">Descreva a imagem</label><textarea id="prompt" maxlength="1200" required placeholder="Ex.: Um cachorro golden retriever correndo em um parque ao pôr do sol, fotografia realista..."></textarea><div class="row"><span class="hint">Quanto mais detalhes, melhor a orientação para a IA.</span><button class="btn" id="generate" type="submit">✦ Gerar imagem</button></div></form>
<div class="status" id="status" role="status" aria-live="polite"><div class="spinner"></div><strong>Gerando sua imagem...</strong><div class="progress"><span></span></div><div class="hint">A IA está trabalhando. Isso pode levar alguns minutos; mantenha esta página aberta.</div></div><div class="error" id="error"></div></section>
<section><div class="section-head"><div><h2>Sua galeria</h2><p>As 10 imagens mais recentes ficam disponíveis aqui.</p></div></div><div class="gallery" id="gallery"><div class="empty">Carregando galeria...</div></div></section>
<footer style="text-align:center;margin:42px auto 0;padding:22px 12px 8px;border-top:1px solid #303955;color:#aab3ce;font-size:13px;line-height:1.8">
  <div style="font-weight:600;color:#f4f6ff">GeraArteIA</div>
  <div>Desenvolvido por Walter Muniz Santos e Luan Jesus Pereira Gomes</div>
  <div>Trabalho de Conclusão de Curso — Geração de Imagens por Difusão</div>
  <div style="margin-top:8px"><a href="/admin" style="color:#aab3ce">Administrador</a></div>
</footer>
</main>
<script>
const form=document.getElementById('form'),promptBox=document.getElementById('prompt'),button=document.getElementById('generate'),statusBox=document.getElementById('status'),errorBox=document.getElementById('error'),gallery=document.getElementById('gallery');
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function loadGallery(){try{const r=await fetch('/api/galeria');const data=await r.json();gallery.innerHTML=data.length?data.map(x=>`<article class="item"><a href="${x.url}" target="_blank" rel="noopener"><img src="${x.url}" loading="lazy" alt="Imagem gerada"></a><div class="meta"><div class="prompt">${esc(x.prompt)}</div><div class="date">${esc(x.created_at)}</div><div class="actions"><a href="${x.url}" target="_blank" rel="noopener">Abrir</a><a href="${x.url}" download>Baixar</a><button class="bad" onclick="evaluateImage('${x.id}')">★ Avaliar imagem</button></div></div></article>`).join(''):'<div class="empty">Você ainda não gerou imagens. Escreva um prompt acima para começar.</div>'}catch(e){gallery.innerHTML='<div class="empty">Não foi possível carregar a galeria agora.</div>'}}
async function evaluateImage(id){
 const raw=prompt('Dê uma nota para a imagem, de 0 a 10:');
 if(raw===null)return;
 const rating=Number(raw.trim());
 if(!Number.isInteger(rating)||rating<0||rating>10){
  alert('Digite uma nota inteira de 0 a 10.');return;
 }
 const satisfactionRaw=prompt('Qual seu nível de satisfação? Digite 20, 40, 60, 80 ou 100 (%):');
 if(satisfactionRaw===null)return;
 const satisfaction_pct=Number(satisfactionRaw.trim());
 if(![20,40,60,80,100].includes(satisfaction_pct)){
  alert('Escolha 20, 40, 60, 80 ou 100.');return;
 }
 const feedback=prompt('Comentário opcional: o que ficou bom ou precisa melhorar?')||'';
 try{
  const r=await fetch('/api/avaliar/'+encodeURIComponent(id),{
   method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({rating,satisfaction_pct,feedback})
  });
  const data=await r.json();
  if(!r.ok)throw new Error(data.detail||'Falha ao salvar avaliação');
  alert(data.saved_for_review?
   'Avaliação registrada. A imagem foi encaminhada para revisão. Obrigado!':
   'Avaliação registrada. Obrigado pelo feedback!');
  await loadGallery();
 }catch(e){alert('Não foi possível registrar a avaliação: '+e.message)}
}
form.addEventListener('submit',async e=>{e.preventDefault();const prompt=promptBox.value.trim();if(!prompt)return;button.disabled=true;button.textContent='Gerando...';statusBox.style.display='block';errorBox.style.display='none';try{const r=await fetch('/api/gerar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})});const data=await r.json();if(!r.ok)throw new Error(data.detail||'Não foi possível gerar a imagem.');await loadGallery();gallery.scrollIntoView({behavior:'smooth',block:'start'});}catch(err){errorBox.textContent=err.message||'Ocorreu um erro durante a geração.';errorBox.style.display='block'}finally{statusBox.style.display='none';button.disabled=false;button.textContent='✦ Gerar imagem'}});
loadGallery();
</script></body></html>''')

    @web.get("/api/galeria")
    def gallery():
        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            rows = con.execute("SELECT * FROM generations ORDER BY created_at DESC LIMIT 10").fetchall()
        return [{"id": r["id"], "prompt": r["prompt"], "created_at": r["created_at"],
                 "url": "/outputs/" + Path(r["image_path"]).name, "flagged_bad": bool(r["flagged_bad"])} for r in rows]

    @web.post("/api/gerar")
    def generate(payload: dict):
        prompt = str(payload.get("prompt", "")).strip()
        if not prompt:
            raise HTTPException(400, "Digite uma descrição para a imagem.")
        if len(prompt) > 1200:
            raise HTTPException(400, "O prompt deve ter até 1.200 caracteres.")
        try:
            # PROMPT_OPTIMIZER_INTEGRADO_V1
            # Usa regras centralizadas por categoria e preserva o prompt original no histórico.
            prompt_final = PromptOptimizer.otimizar(prompt)
            negativo = PromptOptimizer.prompt_negativo()
            pipe = get_pipe()
            with torch.inference_mode():
                result = pipe(
                    prompt=prompt_final,
                    negative_prompt=negativo,
                    num_inference_steps=20,
                    width=512,
                    height=512,
                )
            image = result.images[0]
            generation_id = uuid4().hex
            filename = f"{generation_id}.png"
            target = OUTPUT_DIR / filename
            image.save(target, format="PNG")
            created = datetime.now(timezone.utc).isoformat(timespec="seconds")
            with sqlite3.connect(DB_PATH) as con:
                con.execute("INSERT INTO generations(id,prompt,image_path,created_at) VALUES(?,?,?,?)",
                            (generation_id, prompt, str(target), created))
                con.commit()
            storage.commit()
            return {"id": generation_id, "url": "/outputs/" + filename}
        except Exception as exc:
            print(f"[GeraArteIA] geração falhou: {type(exc).__name__}: {exc}")
            raise HTTPException(500, "A geração falhou. Tente novamente em instantes.") from exc

    @web.post("/api/avaliar/{generation_id}")
    def rate(generation_id: str, payload: dict):
        raw_rating = payload.get("rating")
        try:
            rating = int(raw_rating)
        except (TypeError, ValueError):
            raise HTTPException(400, "A nota deve ser um número inteiro de 0 a 10.")
        if isinstance(raw_rating, bool) or str(raw_rating).strip() not in {str(rating), f"{rating}.0"} or not 0 <= rating <= 10:
            raise HTTPException(400, "A nota deve ser um número inteiro de 0 a 10.")

        feedback = str(payload.get("feedback", "") or "").strip()[:2000]

        raw_satisfaction = payload.get("satisfaction_pct")
        satisfaction_pct = None

        if raw_satisfaction is not None:
            try:
                satisfaction_pct = int(raw_satisfaction)
            except (TypeError, ValueError):
                raise HTTPException(
                    400, "A satisfação deve ser 20, 40, 60, 80 ou 100."
                )

            if (
                isinstance(raw_satisfaction, bool)
                or str(raw_satisfaction).strip() not in {
                    str(satisfaction_pct), f"{satisfaction_pct}.0"
                }
                or satisfaction_pct not in {20, 40, 60, 80, 100}
            ):
                raise HTTPException(
                    400, "A satisfação deve ser 20, 40, 60, 80 ou 100."
                )

        flagged = rating <= 4 or (
            satisfaction_pct is not None and satisfaction_pct <= 40
        )

        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT * FROM generations WHERE id=?", (generation_id,)).fetchone()
            if row is None:
                raise HTTPException(404, "Geração não encontrada.")

            source = Path(row["image_path"])
            if not source.is_file():
                raise HTTPException(404, "Arquivo de imagem não encontrado.")

            con.execute(
                """UPDATE generations
                   SET rating=?, feedback=?, flagged_bad=?, satisfaction_pct=?
                   WHERE id=?""",
                (
                    str(rating), feedback, 1 if flagged else 0,
                    satisfaction_pct, generation_id
                )
            )
            con.commit()

        BAD_DIR.mkdir(parents=True, exist_ok=True)
        bad_path = BAD_DIR / source.name
        meta_path = BAD_DIR / f"{generation_id}.json"

        if flagged:
            shutil.copy2(source, bad_path)
            metadata = {
                "id": generation_id,
                "prompt": row["prompt"],
                "created_at": row["created_at"],
                "image_file": bad_path.name,
                "rating": rating,
                "satisfaction_pct": satisfaction_pct,
                "feedback": feedback,
                "flagged_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "model": MODEL_ID,
                "review_status": "pendente"
            }
            meta_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        else:
            meta_path.unlink(missing_ok=True)
            bad_path.unlink(missing_ok=True)

        storage.commit()
        return {"ok": True, "rating": rating, "saved_for_review": flagged}

    @web.get("/outputs/{filename}")
    def output(filename: str):
        if Path(filename).name != filename or not filename.endswith(".png"):
            raise HTTPException(400, "Nome de arquivo inválido.")
        file_path = OUTPUT_DIR / filename
        if not file_path.is_file():
            raise HTTPException(404, "Imagem não encontrada.")
        return FileResponse(file_path, media_type="image/png", filename=filename)

    @web.get("/api/revisao")
    def review_queue(_admin: bool = Depends(require_admin)):
        items = []
        BAD_DIR.mkdir(parents=True, exist_ok=True)
        for meta_file in sorted(BAD_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                data = json.loads(meta_file.read_text(encoding="utf-8"))
                filename = Path(str(data.get("image_file", ""))).name
                image_path = BAD_DIR / filename
                if filename and image_path.is_file():
                    data["url"] = "/revisao/imagem/" + filename
                    items.append(data)
            except (OSError, ValueError, TypeError):
                continue
        return items

    @web.get("/revisao/imagem/{filename}")
    def review_image(filename: str, _admin: bool = Depends(require_admin)):
        if Path(filename).name != filename or not filename.lower().endswith(".png"):
            raise HTTPException(400, "Nome de arquivo inválido.")
        image_path = BAD_DIR / filename
        if not image_path.is_file():
            raise HTTPException(404, "Imagem de revisão não encontrada.")
        return FileResponse(image_path, media_type="image/png", filename=filename)

    @web.get("/revisao", response_class=HTMLResponse)
    def review_page(_admin: bool = Depends(require_admin)):
        return HTMLResponse(r"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Revisão de imagens — GeraArteIA</title>
<style>
body{margin:0;padding:24px;background:#0d1020;color:#f4f6ff;font:16px Segoe UI,Arial,sans-serif}
main{max-width:1100px;margin:auto}a{color:#b9c6ff}.top{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin-top:24px}
article{background:#171c31;border:1px solid #303955;border-radius:14px;overflow:hidden}
img{width:100%;aspect-ratio:1;object-fit:contain;background:#080b15}
.content{padding:14px}.prompt{overflow-wrap:anywhere;line-height:1.5}.date{color:#aab3ce;font-size:12px;margin:10px 0}
.empty{padding:24px;border:1px dashed #59617a;border-radius:12px;color:#c0c7dc}
</style></head><body><main>
<div class="top"><h1>Fila de revisão</h1><a href="/">← Voltar ao GeraArteIA</a></div>
<p>Imagens sinalizadas como ruins e guardadas no volume do Modal.</p>
<div id="status">Carregando imagens...</div><div id="grid" class="grid"></div>
<script>
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
(async()=>{const status=document.getElementById('status'),grid=document.getElementById('grid');
try{const r=await fetch('/api/revisao');if(!r.ok)throw Error('Falha ao consultar a fila');
const items=await r.json();status.textContent=items.length?items.length+' imagem(ns) na fila de revisão.':'Nenhuma imagem sinalizada até agora.';
grid.innerHTML=items.map(x=>`<article><a href="${x.url}" target="_blank" rel="noopener"><img src="${x.url}" loading="lazy" alt="Imagem para revisão"></a><div class="content"><div class="prompt">${esc(x.prompt)}</div><div class="date">Sinalizada em: ${esc(x.flagged_at||x.created_at||'Data não disponível')}</div><div>Nota: ${esc(x.rating??'não informada')}/10</div><div>Satisfação: ${x.satisfaction_pct==null?'Não informada':esc(x.satisfaction_pct)+'%'}</div><div>Comentário: ${esc(x.feedback||'Nenhum comentário informado')}</div><p><a href="${x.url}" download>Baixar imagem</a></p></div></article>`).join('');
}catch(e){status.textContent='Não foi possível carregar a fila. Tente novamente.'}})();
</script></main></body></html>""")


    def build_diagnostic_report():
        checks = []

        def check(name, ok, detail):
            checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})

        check("Diretório de dados", DATA_DIR.is_dir(), DATA_DIR)
        check("Diretório de imagens", OUTPUT_DIR.is_dir(), OUTPUT_DIR)
        check("Diretório de revisão", BAD_DIR.is_dir(), BAD_DIR)

        total = flagged = 0
        feedback_records = []
        try:
            with sqlite3.connect(DB_PATH) as con:
                con.row_factory = sqlite3.Row
                con.execute("SELECT 1").fetchone()
                columns = {row[1] for row in con.execute("PRAGMA table_info(generations)")}
                required_columns = {
                    "id", "prompt", "image_path", "created_at",
                    "rating", "feedback", "flagged_bad"
                }
                check("Conexão com banco", True, DB_PATH)
                check(
                    "Estrutura do banco",
                    required_columns.issubset(columns),
                    "Colunas presentes: " + ", ".join(sorted(columns))
                )
                total = con.execute("SELECT COUNT(*) FROM generations").fetchone()[0]
                flagged = con.execute(
                    "SELECT COUNT(*) FROM generations WHERE flagged_bad=1"
                ).fetchone()[0]
                check(
                    "Consulta de registros", True,
                    f"{total} geração(ões); {flagged} sinalizada(s)"
                )
                feedback_records = [
                    dict(row) for row in con.execute("""
                        SELECT id, prompt, image_path, created_at, rating, feedback
                        FROM generations
                        WHERE rating IS NOT NULL AND TRIM(CAST(rating AS TEXT)) != ''
                        ORDER BY created_at DESC
                    """).fetchall()
                ]
                check("Consulta de feedback", True,
                      f"{len(feedback_records)} avaliação(ões) encontrada(s)")
        except Exception as exc:
            check("Banco de dados", False, f"{type(exc).__name__}: {exc}")
            check("Consulta de feedback", False, f"{type(exc).__name__}: {exc}")

        ratings = []
        for item in feedback_records:
            try:
                ratings.append(int(item["rating"]))
            except (TypeError, ValueError):
                pass
        average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

        try:
            import torch
            check("PyTorch", True,
                  f"versão {torch.__version__}; CUDA disponível: {torch.cuda.is_available()}")
        except Exception as exc:
            check("PyTorch", False, f"{type(exc).__name__}: {exc}")

        try:
            import diffusers
            check("Diffusers", True, f"versão {diffusers.__version__}")
        except Exception as exc:
            check("Diffusers", False, f"{type(exc).__name__}: {exc}")

        return {
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "model": MODEL_ID,
            "total_generations": total,
            "flagged_generations": flagged,
            "feedback_records": feedback_records,
            "rated_count": len(feedback_records),
            "average_rating": average_rating,
            "checks": checks
        }

    @web.get("/admin", response_class=HTMLResponse)
    def admin_page(_admin: bool = Depends(require_admin)):
        return HTMLResponse("""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Administrador — GeraArteIA</title>
<style>
body{margin:0;padding:28px;background:#0d1020;color:#f4f6ff;font:16px Segoe UI,Arial,sans-serif}
main{max-width:850px;margin:auto}a{color:#c5ceff}.panel{background:#171c31;border:1px solid #303955;border-radius:16px;padding:20px;margin:16px 0}
button{padding:11px 15px;border:0;border-radius:9px;background:#7188ff;color:white;font-weight:700;cursor:pointer}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#090d19;padding:15px;border-radius:10px}
</style></head><body><main>
<h1>GeraArteIA — Administração</h1>
<p>Área restrita para acompanhamento e diagnóstico.</p>
<div class="panel"><h2>Feedback das imagens</h2>
<p>Consultar imagens sinalizadas para revisão, seus prompts e comentários.</p>
<p><a href="/revisao">Abrir fila de revisão</a></p></div>
<div class="panel"><h2>Painel de qualidade</h2><p>Acompanhe notas, comentarios e miniaturas das imagens avaliadas.</p><p><a href="/admin/qualidade">Abrir painel de qualidade</a></p></div><div class="panel"><h2>Teste exaustivo computacional</h2>
<p>Executa verificações técnicas de arquivos, banco de dados e dependências instaladas.</p>
<button id="run">Executar diagnóstico</button>
<p><a href="/admin/testes/relatorio.txt">Baixar relatório TXT</a> | <a href="/admin/testes/relatorio.pdf">Baixar relatório PDF</a></p>
<pre id="result">Clique em “Executar diagnóstico” para ver os resultados.</pre></div>
<p><a href="/">Voltar à página principal</a></p>
<script>
document.getElementById('run').addEventListener('click',async()=>{
 const out=document.getElementById('result');out.textContent='Executando verificações...';
 try{const r=await fetch('/admin/testes/resultado');const d=await r.json();
 if(!r.ok)throw Error(d.detail||'Falha no diagnóstico');
 out.textContent='Data UTC: '+d.created_at+'\\nModelo: '+d.model+
 '\\nGerações: '+d.total_generations+'\\nSinalizadas: '+d.flagged_generations+
 '\\n\\n'+d.checks.map(c=>(c.ok?'[OK] ':'[FALHA] ')+c.name+' — '+c.detail).join('\\n');
 }catch(e){out.textContent='Não foi possível executar o diagnóstico: '+e.message}
});
</script></main></body></html>""")


    @web.get("/admin/qualidade", response_class=HTMLResponse)
    def quality_dashboard(_admin: bool = Depends(require_admin)):
        return HTMLResponse("""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Qualidade das imagens - GeraArteIA</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:24px;background:#0d1020;color:#f4f6ff;
font:16px Segoe UI,Arial,sans-serif}
main{max-width:1100px;margin:auto}
a{color:#c5ceff}
.panel,.metric{background:#171c31;border:1px solid #303955;
border-radius:14px;padding:18px;margin:14px 0}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.value{font-size:30px;font-weight:700;margin-top:8px}
.muted{color:#b7bfd9;font-size:13px}
.reviews{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.review{background:#171c31;border:1px solid #303955;border-radius:14px;overflow:hidden}
.review img{display:block;width:100%;height:220px;object-fit:contain;background:#090d19}
.review .body{padding:14px}
.comment{white-space:pre-wrap;overflow-wrap:anywhere}
.prompt{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px;color:#c7cde0}
.bar-row{display:grid;grid-template-columns:55px 1fr 35px;gap:10px;align-items:center;margin:9px 0}
.bar-bg{height:13px;background:#090d19;border-radius:10px;overflow:hidden}
.bar{height:100%;background:#8295ff;border-radius:10px;min-width:0}
button{padding:10px 14px;border:0;border-radius:8px;background:#7188ff;color:white;cursor:pointer}
@media(max-width:600px){body{padding:12px}.review img{height:180px}}
</style>
</head>
<body><main>
<h1>Painel de qualidade das imagens</h1>
<p class="muted">Indicadores baseados nas avaliacoes salvas no banco local.</p>
<p><a href="/admin">Voltar a administracao</a> | <a href="/revisao">Fila de revisao</a></p>
<div class="metrics">
 <section class="metric"><div class="muted">Imagens geradas</div><div class="value" id="total">-</div></section>
 <section class="metric"><div class="muted">Imagens avaliadas</div><div class="value" id="rated">-</div></section>
 <section class="metric"><div class="muted">Média das notas</div><div class="value" id="average">-</div><div class="muted">de 0 a 10</div></section>
 <section class="metric"><div class="muted">Média de satisfação</div><div class="value" id="avgSatisfaction">-</div><div class="muted">percentual informado</div></section>
 <section class="metric"><div class="muted">Sinalizadas para revisão</div><div class="value" id="flagged">-</div></section>
</div>
<section class="panel">
 <h2>Distribuicao das notas</h2>
 <div id="distribution">Carregando avaliacoes...</div>
</section>
<section class="panel">
 <h2>Distribuição da satisfação</h2>
 <div id="satisfactionDistribution">Carregando percentuais...</div>
</section>
<section class="panel">
 <h2>Histórico de feedback</h2>
 <div class="muted" id="summary"></div>
 <div class="reviews" id="reviews"></div>
</section>
<script>
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function loadQuality(){
 const summary=document.getElementById('summary');
 try{
  const response=await fetch('/admin/qualidade/dados');
  const data=await response.json();
  if(!response.ok)throw new Error(data.detail||'Falha ao carregar dados');
  document.getElementById('total').textContent=data.total;
  document.getElementById('rated').textContent=data.rated_count;
  document.getElementById('average').textContent=data.average===null?'—':data.average.toFixed(2);
  document.getElementById('avgSatisfaction').textContent=data.average_satisfaction===null?'—':data.average_satisfaction.toFixed(1)+'%';
  document.getElementById('flagged').textContent=data.flagged;
  const max=Math.max(1,...data.distribution.map(x=>x.count));
  document.getElementById('distribution').innerHTML=data.distribution.map(x=>
   `<div class="bar-row"><span>Nota ${x.rating}</span><div class="bar-bg"><div class="bar" style="width:${x.count/max*100}%"></div></div><span>${x.count}</span></div>`
  ).join('');
  const maxSatisfaction=Math.max(1,...data.satisfaction_distribution.map(x=>x.count));
  document.getElementById('satisfactionDistribution').innerHTML=data.satisfaction_distribution.map(x=>
   `<div class="bar-row"><span>${x.percent}%</span><div class="bar-bg"><div class="bar" style="width:${x.count/maxSatisfaction*100}%"></div></div><span>${x.count}</span></div>`
  ).join('');
  summary.textContent=`Mostrando ${data.records.length} avaliação(ões), da mais recente para a mais antiga.`;
  document.getElementById('reviews').innerHTML=data.records.length?data.records.map(x=>
   `<article class="review"><a href="${esc(x.url)}" target="_blank" rel="noopener"><img src="${esc(x.url)}" loading="lazy" alt="Miniatura da imagem avaliada"></a><div class="body"><h3>Nota: ${esc(x.rating)}/10</h3><p><strong>Satisfação:</strong> ${x.satisfaction_pct==null?'Não informada':esc(x.satisfaction_pct)+'%'}</p><div class="muted">${esc(x.created_at)}</div><p><strong>Comentario</strong></p><div class="comment">${esc(x.feedback||'Sem comentario')}</div><p><strong>Prompt</strong></p><div class="prompt">${esc(x.prompt)}</div><p class="muted">ID: ${esc(x.id)}</p><p><a href="${esc(x.url)}" target="_blank" rel="noopener">Abrir imagem</a></p></div></article>`
  ).join(''):'<p>Nenhuma imagem avaliada ainda.</p>';
 }catch(e){summary.textContent='Nao foi possivel carregar o painel: '+e.message}
}
loadQuality();
</script>
</main></body></html>""")

    @web.get("/admin/qualidade/dados")
    def quality_dashboard_data(_admin: bool = Depends(require_admin)):
        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            total = con.execute("SELECT COUNT(*) FROM generations").fetchone()[0]
            flagged = con.execute(
                "SELECT COUNT(*) FROM generations WHERE flagged_bad=1"
            ).fetchone()[0]
            rows = con.execute("""
                SELECT id, prompt, image_path, created_at, rating, feedback, flagged_bad, satisfaction_pct
                FROM generations
                WHERE rating IS NOT NULL
                  AND TRIM(CAST(rating AS TEXT)) != ''
                ORDER BY created_at DESC
            """).fetchall()

        records = []
        ratings = []
        counts = {n: 0 for n in range(11)}
        satisfaction_values = []
        satisfaction_counts = {n: 0 for n in (20, 40, 60, 80, 100)}
        for row in rows:
            item = dict(row)
            try:
                rating = int(item["rating"])
                if 0 <= rating <= 10:
                    ratings.append(rating)
                    counts[rating] += 1
            except (TypeError, ValueError):
                continue
            value = item.get("satisfaction_pct")
            if value is not None:
                try:
                    value = int(value)
                    if value in satisfaction_counts:
                        satisfaction_values.append(value)
                        satisfaction_counts[value] += 1
                except (TypeError, ValueError):
                    pass

            item["url"] = "/outputs/" + Path(item["image_path"]).name
            records.append(item)

        return {
            "total": total,
            "rated_count": len(records),
            "flagged": flagged,
            "average": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "average_satisfaction": (
                round(sum(satisfaction_values) / len(satisfaction_values), 1)
                if satisfaction_values else None
            ),
            "satisfaction_distribution": [
                {"percent": n, "count": satisfaction_counts[n]}
                for n in (20, 40, 60, 80, 100)
            ],
            "distribution": [
                {"rating": n, "count": counts[n]} for n in range(11)
            ],
            "records": records
        }

    @web.get("/admin/testes/resultado")
    def admin_test_result(_admin: bool = Depends(require_admin)):
        return build_diagnostic_report()

    @web.get("/admin/testes/relatorio.txt")
    def admin_test_report(_admin: bool = Depends(require_admin)):
        report = build_diagnostic_report()
        average = report["average_rating"]
        lines = [
            "RELATORIO DE DIAGNOSTICO - GeraArteIA",
            "Data UTC: " + report["created_at"],
            "Modelo configurado: " + report["model"],
            "Total de geracoes: " + str(report["total_generations"]),
            "Imagens sinalizadas: " + str(report["flagged_generations"]),
            "Imagens avaliadas: " + str(report["rated_count"]),
            "Media das notas: " + (str(average) if average is not None else "Sem avaliacoes"),
            "",
            "RESULTADOS:"
        ]
        for item in report["checks"]:
            lines.append((" [OK] " if item["ok"] else " [FALHA] ") +
                         item["name"] + " - " + item["detail"])

        lines += ["", "HISTORICO DE FEEDBACK DAS IMAGENS"]
        if not report["feedback_records"]:
            lines.append("Ainda nao existem imagens avaliadas.")
        for item in report["feedback_records"]:
            lines += [
                "",
                "----------------------------------------",
                "Data: " + str(item.get("created_at") or ""),
                "ID: " + str(item.get("id") or ""),
                "Nota: " + str(item.get("rating") or ""),
                "Imagem: " + str(item.get("image_path") or ""),
                "Prompt: " + str(item.get("prompt") or ""),
                "Comentario: " + str(item.get("feedback") or "Sem comentario")
            ]

        lines += [
            "",
            "LIMITACOES:",
            "Este diagnostico verifica arquivos, banco de dados e dependencias.",
            "Nao executa geracao real de imagem nem teste de carga da GPU.",
            "Uma verificacao aprovada nao garante que todos os fluxos funcionem."
        ]
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            "\n".join(lines),
            headers={"Content-Disposition": 'attachment; filename="relatorio_geraarteia.txt"'}
        )


    @web.get("/admin/testes/relatorio.pdf")
    def admin_test_report_pdf(_admin: bool = Depends(require_admin)):
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.utils import ImageReader
        from fastapi.responses import StreamingResponse
        import textwrap

        report = build_diagnostic_report()
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        left = 42
        right = width - 42
        y = height - 48

        font_name = "Helvetica"
        font_bold = "Helvetica-Bold"
        font_path = Path("C:/Windows/Fonts/arial.ttf")
        bold_path = Path("C:/Windows/Fonts/arialbd.ttf")
        try:
            if font_path.exists():
                pdfmetrics.registerFont(TTFont("ArialLocal", str(font_path)))
                font_name = "ArialLocal"
                if bold_path.exists():
                    pdfmetrics.registerFont(TTFont("ArialLocalBold", str(bold_path)))
                    font_bold = "ArialLocalBold"
        except Exception:
            pass

        def new_page():
            nonlocal y
            pdf.showPage()
            y = height - 48

        def ensure_space(amount):
            nonlocal y
            if y - amount < 48:
                new_page()

        def line(text, leading=16, bold=False):
            nonlocal y
            font = font_bold if bold else font_name
            pdf.setFont(font, 9)
            available = 105
            chunks = textwrap.wrap(
                str(text), width=available,
                break_long_words=True, break_on_hyphens=False
            ) or [""]
            for chunk in chunks:
                ensure_space(leading)
                pdf.drawString(left, y, chunk)
                y -= leading

        line("RELATORIO DE DIAGNOSTICO - GeraArteIA", 23, True)
        line("Data UTC: " + report["created_at"])
        line("Modelo configurado: " + report["model"])
        line("Total de geracoes: " + str(report["total_generations"]))
        line("Imagens sinalizadas: " + str(report["flagged_generations"]))
        line("Imagens avaliadas: " + str(report["rated_count"]))
        average = report["average_rating"]
        line("Media das notas: " + (
            str(average) if average is not None else "Sem avaliacoes"
        ))

        line("")
        line("RESULTADOS DAS VERIFICACOES", 22, True)
        for item in report["checks"]:
            status = "[OK]" if item["ok"] else "[FALHA]"
            line(status + " " + item["name"] + " - " + item["detail"])

        line("")
        line("HISTORICO DE FEEDBACK DAS IMAGENS", 22, True)

        records = report.get("feedback_records", [])
        if not records:
            line("Ainda nao existem imagens avaliadas.")

        for item in records:
            image_path = Path(str(item.get("image_path") or ""))
            thumb_w, thumb_h = 132, 105
            text_x = left + thumb_w + 16
            text_width = 68

            # Reserva espaço para a miniatura e os dados básicos.
            ensure_space(thumb_h + 42)
            block_top = y

            pdf.setFont(font_bold, 10)
            pdf.drawString(left, y, "Nota: " + str(item.get("rating") or ""))
            y -= 15

            pdf.setFont(font_name, 8)
            satisfaction = item.get("satisfaction_pct")
            satisfaction_text = (
                str(satisfaction) + "%"
                if satisfaction is not None
                else "Nao informada"
            )
            pdf.drawString(left, y, "Satisfacao: " + satisfaction_text)
            y -= 15
            for label, value in [
                ("Data: ", item.get("created_at")),
                ("ID: ", item.get("id")),
                ("Prompt: ", item.get("prompt")),
                ("Comentario: ", item.get("feedback") or "Sem comentario"),
                ("Arquivo: ", image_path.name),
            ]:
                text = label + str(value or "")
                chunks = textwrap.wrap(
                    text, width=text_width,
                    break_long_words=True, break_on_hyphens=False
                ) or [""]
                for chunk in chunks:
                    if y < 48:
                        new_page()
                    pdf.drawString(text_x, y, chunk)
                    y -= 12

            # Coloca a imagem real à esquerda do registro.
            if image_path.is_file():
                try:
                    pdf.drawImage(
                        ImageReader(str(image_path)),
                        left, block_top - thumb_h - 4,
                        width=thumb_w, height=thumb_h,
                        preserveAspectRatio=True,
                        anchor="c",
                        mask="auto"
                    )
                except Exception as exc:
                    pdf.setFont(font_name, 8)
                    pdf.drawString(
                        left, block_top - 20,
                        "Falha ao abrir miniatura"
                    )
                    pdf.drawString(
                        left, block_top - 34,
                        type(exc).__name__
                    )
            else:
                pdf.setFont(font_name, 8)
                pdf.drawString(left, block_top - 20, "Imagem indisponivel")
                pdf.drawString(left, block_top - 34, str(image_path.name))

            y = min(y, block_top - thumb_h - 12)
            ensure_space(22)
            y -= 10
            pdf.setStrokeColorRGB(0.75, 0.75, 0.75)
            pdf.line(left, y, right, y)
            y -= 18

        line("")
        line("LIMITACOES", 22, True)
        line("O diagnostico verifica arquivos, banco de dados e dependencias.")
        line("Nao executa uma geracao real nem teste de carga da GPU.")
        line("Resultados positivos nao garantem o funcionamento de todos os fluxos.")

        pdf.save()
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="relatorio_geraarteia.pdf"'}
        )

    @web.get("/health")
    def health():
        return {"status": "ok", "app": "GeraArteIA", "storage": "modal-volume"}

    return web

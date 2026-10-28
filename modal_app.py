import json
import sqlite3
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
        "transformers>=4.41,<5", "accelerate", "safetensors", "pillow"
    )
)


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BAD_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS generations (
            id TEXT PRIMARY KEY, prompt TEXT NOT NULL, image_path TEXT NOT NULL,
            created_at TEXT NOT NULL, rating TEXT, feedback TEXT, flagged_bad INTEGER DEFAULT 0
        )""")
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
    from fastapi import FastAPI, Form, HTTPException
    from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from diffusers import StableDiffusionPipeline
    import torch

    web = FastAPI(title="GeraArteIA")
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
</footer>
</main>
<script>
const form=document.getElementById('form'),promptBox=document.getElementById('prompt'),button=document.getElementById('generate'),statusBox=document.getElementById('status'),errorBox=document.getElementById('error'),gallery=document.getElementById('gallery');
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function loadGallery(){try{const r=await fetch('/api/galeria');const data=await r.json();gallery.innerHTML=data.length?data.map(x=>`<article class="item"><a href="${x.url}" target="_blank" rel="noopener"><img src="${x.url}" loading="lazy" alt="Imagem gerada"></a><div class="meta"><div class="prompt">${esc(x.prompt)}</div><div class="date">${esc(x.created_at)}</div><div class="actions"><a href="${x.url}" target="_blank" rel="noopener">Abrir</a><a href="${x.url}" download>Baixar</a><button class="bad" onclick="flagBad('${x.id}')">⚑ Imagem ruim</button></div></div></article>`).join(''):'<div class="empty">Você ainda não gerou imagens. Escreva um prompt acima para começar.</div>'}catch(e){gallery.innerHTML='<div class="empty">Não foi possível carregar a galeria agora.</div>'}}
async function flagBad(id){if(!confirm('Sinalizar esta imagem para revisão e melhoria futura?'))return;try{const r=await fetch('/api/avaliar/'+encodeURIComponent(id),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rating:'ruim',feedback:'Sinalizada pelo usuário como imagem ruim'})});if(!r.ok)throw new Error('Falha ao salvar avaliação');alert('Imagem guardada na fila de revisão do Modal. Obrigado!');await loadGallery()}catch(e){alert('Não foi possível registrar a avaliação. Tente novamente.')}}
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
            pipe = get_pipe()
            with torch.inference_mode():
                result = pipe(prompt=prompt, num_inference_steps=20, width=512, height=512)
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
        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT * FROM generations WHERE id=?", (generation_id,)).fetchone()
            if row is None:
                raise HTTPException(404, "Geração não encontrada.")
            source = Path(row["image_path"])
            if not source.is_file():
                raise HTTPException(404, "Arquivo de imagem não encontrado.")
            bad_path = BAD_DIR / source.name
            bad_path.write_bytes(source.read_bytes())
            metadata = {"id": generation_id, "prompt": row["prompt"], "created_at": row["created_at"],
                        "image_file": bad_path.name, "rating": "ruim", "feedback": str(payload.get("feedback", "")),
                        "flagged_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "model": MODEL_ID, "review_status": "pendente"}
            (BAD_DIR / f"{generation_id}.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
            con.execute("UPDATE generations SET rating=?,feedback=?,flagged_bad=1 WHERE id=?",
                        ("ruim", metadata["feedback"], generation_id))
            con.commit()
        storage.commit()
        return {"ok": True, "saved_for_review": True}

    @web.get("/outputs/{filename}")
    def output(filename: str):
        if Path(filename).name != filename or not filename.endswith(".png"):
            raise HTTPException(400, "Nome de arquivo inválido.")
        file_path = OUTPUT_DIR / filename
        if not file_path.is_file():
            raise HTTPException(404, "Imagem não encontrada.")
        return FileResponse(file_path, media_type="image/png", filename=filename)

    @web.get("/health")
    def health():
        return {"status": "ok", "app": "GeraArteIA", "storage": "modal-volume"}

    return web

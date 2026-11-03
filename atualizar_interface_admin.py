from pathlib import Path
from datetime import datetime
import shutil
import re
import sys

root = Path.cwd()
target = root / "modal_app.py"
if not target.is_file():
    raise SystemExit("ERRO: modal_app.py não encontrado.")

source = target.read_text(encoding="utf-8")

def require_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: esperado 1 trecho, encontrado {count}. Nenhuma alteração foi gravada.")
    return text.replace(old, new, 1)

# Confere os principais pontos antes de começar.
for marker in (
    '@web.get("/", response_class=HTMLResponse)',
    '@web.post("/api/avaliar/{generation_id}")',
    '@web.get("/api/revisao")',
    '@web.get("/revisao/imagem/{filename}")',
    '@web.get("/revisao", response_class=HTMLResponse)',
    '@web.get("/health")',
):
    if source.count(marker) != 1:
        raise SystemExit(f"ERRO: estrutura inesperada: {marker}")

backup_dir = root / "backups" / ("antes_avaliacao_admin_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup_dir.mkdir(parents=True, exist_ok=False)
shutil.copy2(target, backup_dir / "modal_app.py")
print(f"Backup criado em: {backup_dir}")

updated = source

# Autenticação HTTP Basic no servidor.
updated = require_once(
    updated,
    "from fastapi import FastAPI, Form, HTTPException",
    "from fastapi import FastAPI, Form, HTTPException, Depends\n    from fastapi.security import HTTPBasic, HTTPBasicCredentials\n    import secrets",
    "Importação de segurança",
)

updated = require_once(
    updated,
    '    web = FastAPI(title="GeraArteIA")\n    init_db()',
    '''    web = FastAPI(title="GeraArteIA")
    admin_security = HTTPBasic()

    def require_admin(credentials: HTTPBasicCredentials = Depends(admin_security)):
        expected_user = "admin"
        expected_password = __import__("os").environ.get("GERAARTEIA_ADMIN_PASSWORD", "1234")
        user_ok = secrets.compare_digest(credentials.username.encode("utf-8"), expected_user.encode("utf-8"))
        password_ok = secrets.compare_digest(credentials.password.encode("utf-8"), expected_password.encode("utf-8"))
        if not (user_ok and password_ok):
            from fastapi import status
            from fastapi.responses import JSONResponse as _JSONResponse
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Acesso administrativo necessário.",
                headers={"WWW-Authenticate": "Basic"},
            )
        return True

    init_db()''',
    "Configuração da autenticação",
)

# Identidade visual e acesso administrativo na página inicial.
updated = require_once(
    updated,
    '<header class="brand"><div class="logo">?</div><div><h1>GeraArteIA</h1><p>Transforme sua ideia em imagem com inteligência artificial</p></div></header>',
    '<header class="brand"><div class="logo">✦</div><div><h1>GeraArteIA</h1><p>Transforme sua ideia em imagem com inteligência artificial</p></div><a class="admin-link" href="/admin">Área administrativa</a></header>',
    "Cabeçalho da página inicial",
)

updated = require_once(
    updated,
    '.brand{display:flex;align-items:center;gap:13px;margin-bottom:35px}',
    '.brand{display:flex;align-items:center;justify-content:center;gap:13px;margin-bottom:35px;position:relative;text-align:left}.admin-link{position:absolute;right:0;top:8px;color:#dce2ff;text-decoration:none;font-size:12px;border:1px solid #414c70;border-radius:9px;padding:9px 11px;background:#171c31}.admin-link:hover{border-color:#7188ff}',
    "Estilo do cabeçalho",
)

# Troca o antigo botão de imagem ruim por avaliação com nota e comentário.
updated = require_once(
    updated,
    '''async function flagBad(id){if(!confirm('Sinalizar esta imagem para revisão e melhoria futura?'))return;try{const r=await fetch('/api/avaliar/'+encodeURIComponent(id),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rating:'ruim',feedback:'Sinalizada pelo usuário como imagem ruim'})});if(!r.ok)throw new Error('Falha ao salvar avaliação');alert('Imagem guardada na fila de revisão do Modal. Obrigado!');await loadGallery()}catch(e){alert('Não foi possível registrar a avaliação. Tente novamente.')}}''',
    '''async function flagBad(id){
 const raw=prompt('Avalie esta imagem de 0 a 10. Digite apenas um número:');
 if(raw===null)return;
 const score=Number(raw);
 if(!Number.isInteger(score)||score<0||score>10){alert('Digite uma nota inteira entre 0 e 10.');return}
 const feedback=prompt('O que ficou bom ou precisa melhorar? (opcional)','')??'';
 try{
  const r=await fetch('/api/avaliar/'+encodeURIComponent(id),{
   method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({rating:score,feedback})
  });
  const data=await r.json().catch(()=>({}));
  if(!r.ok)throw new Error(data.detail||'Falha ao salvar avaliação');
  alert(score<=4?'Avaliação registrada e imagem encaminhada para revisão.':'Obrigado! Sua avaliação foi registrada.');
  await loadGallery();
 }catch(e){alert(e.message||'Não foi possível registrar a avaliação. Tente novamente.')}
}''',
    "Função de avaliação da galeria",
)

updated = require_once(
    updated,
    '<button class="bad" onclick="flagBad(\\'${x.id}\\')">? Imagem ruim</button>',
    '<button onclick="flagBad(\\'${x.id}\\')">★ Avaliar imagem</button>',
    "Botão de avaliação",
)

# Substitui somente a rota de avaliação, preservando as demais rotas.
start_marker = '    @web.post("/api/avaliar/{generation_id}")'
end_marker = '    @web.get("/outputs/{filename}")'
start = updated.index(start_marker)
end = updated.index(end_marker, start)

new_rate = '''    @web.post("/api/avaliar/{generation_id}")
    def rate(generation_id: str, payload: dict):
        raw_rating = payload.get("rating")
        try:
            score = int(raw_rating)
        except (TypeError, ValueError):
            raise HTTPException(400, "A nota deve ser um número inteiro de 0 a 10.")
        if score < 0 or score > 10:
            raise HTTPException(400, "A nota deve estar entre 0 e 10.")

        feedback = str(payload.get("feedback", "")).strip()[:2000]
        flagged = score <= 4

        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT * FROM generations WHERE id=?", (generation_id,)).fetchone()
            if row is None:
                raise HTTPException(404, "Geração não encontrada.")

            source = Path(row["image_path"])
            if not source.is_file():
                raise HTTPException(404, "Arquivo de imagem não encontrado.")

            if flagged:
                BAD_DIR.mkdir(parents=True, exist_ok=True)
                bad_path = BAD_DIR / source.name
                bad_path.write_bytes(source.read_bytes())
                metadata = {
                    "id": generation_id,
                    "prompt": row["prompt"],
                    "created_at": row["created_at"],
                    "image_file": bad_path.name,
                    "rating": score,
                    "feedback": feedback,
                    "flagged_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "model": MODEL_ID,
                    "review_status": "pendente",
                }
                (BAD_DIR / f"{generation_id}.json").write_text(
                    json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
                )

            con.execute(
                "UPDATE generations SET rating=?, feedback=?, flagged_bad=? WHERE id=?",
                (str(score), feedback, int(flagged), generation_id),
            )
            con.commit()

        if flagged:
            storage.commit()
        return {"ok": True, "rating": score, "saved_for_review": flagged}

'''
updated = updated[:start] + new_rate + updated[end:]

# Restringe todas as rotas que expõem a fila e as imagens de revisão.
updated = require_once(
    updated,
    '    def review_queue():',
    '    def review_queue(_admin: bool = Depends(require_admin)):',
    "Proteção da fila de revisão",
)
updated = require_once(
    updated,
    '    def review_image(filename: str):',
    '    def review_image(filename: str, _admin: bool = Depends(require_admin)):',
    "Proteção das imagens de revisão",
)
updated = require_once(
    updated,
    '    def review_page():',
    '    def review_page(_admin: bool = Depends(require_admin)):',
    "Proteção da página de revisão",
)

# Painel administrativo simples com indicadores e distribuição de notas.
admin_route = '''    @web.get("/admin", response_class=HTMLResponse)
    def admin_page(_admin: bool = Depends(require_admin)):
        with sqlite3.connect(DB_PATH) as con:
            rows = con.execute("SELECT rating, feedback, flagged_bad FROM generations").fetchall()
        scores = []
        for rating, feedback, flagged in rows:
            try:
                score = int(rating)
                if 0 <= score <= 10:
                    scores.append(score)
            except (TypeError, ValueError):
                pass
        total = len(rows)
        average = round(sum(scores) / len(scores), 2) if scores else 0
        flagged_count = sum(1 for row in rows if row[2])
        bars = []
        for score in range(11):
            count = sum(1 for value in scores if value == score)
            width = (count / max(1, len(scores))) * 100
            bars.append(
                f"<div class='barrow'><span>{score}/10</span><div class='track'><i style='width:{width:.1f}%'></i></div><b>{count}</b></div>"
            )
        bars_html = "".join(bars)
        return HTMLResponse(f"""<!doctype html>
<html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Administração — GeraArteIA</title>
<style>
body{{margin:0;background:#0d1020;color:#f4f6ff;font:16px Segoe UI,Arial,sans-serif;padding:24px}}
main{{max-width:950px;margin:auto}}a{{color:#c7d0ff}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:24px 0}}
.card{{background:#171c31;border:1px solid #303955;border-radius:16px;padding:20px}}.num{{font-size:32px;font-weight:800;margin-top:8px}}
.barrow{{display:grid;grid-template-columns:50px 1fr 30px;gap:10px;align-items:center;margin:10px 0}}
.track{{height:12px;border-radius:10px;background:#252d46;overflow:hidden}}.track i{{display:block;height:100%;background:linear-gradient(90deg,#7188ff,#a879f7)}}
.note{{color:#aab3ce;font-size:13px;line-height:1.6}}
</style><main>
<h1>✦ GeraArteIA — Administração</h1><p class="note">Painel protegido. Os indicadores refletem as avaliações registradas.</p>
<div class="cards">
<div class="card">Imagens geradas<div class="num">{total}</div></div>
<div class="card">Avaliações válidas<div class="num">{len(scores)}</div></div>
<div class="card">Nota média<div class="num">{average:.2f}/10</div></div>
<div class="card">Imagens para revisão<div class="num">{flagged_count}</div></div>
</div>
<section class="card"><h2>Distribuição das notas</h2>{bars_html}
<p class="note">Uma nota de 0 a 4 encaminha a imagem para revisão. As demais avaliações ficam registradas no histórico.</p></section>
<p style="margin-top:24px"><a href="/revisao">Abrir fila de revisão</a> · <a href="/">Voltar à página inicial</a></p>
</main></html>""")

'''
updated = require_once(
    updated,
    '    @web.get("/health")',
    admin_route + '    @web.get("/health")',
    "Inclusão do painel administrativo",
)

if updated == source:
    raise SystemExit("Nenhuma alteração foi aplicada.")

# Grava somente após todas as verificações e substituições terem funcionado.
target.write_text(updated, encoding="utf-8")
print("Atualização gravada em modal_app.py")
print("Backup original preservado:", backup_dir / "modal_app.py")

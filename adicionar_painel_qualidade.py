from pathlib import Path
from datetime import datetime
import shutil
import sys

path = Path("modal_app.py")
source = path.read_text(encoding="utf-8")

admin_marker = '    @web.get("/admin/testes/resultado")'
panel_marker = '<div class="panel"><h2>Teste exaustivo computacional</h2>'

if source.count(admin_marker) != 1:
    print("ABORTADO: rota de diagnóstico não encontrada exatamente uma vez.")
    sys.exit(1)

if source.count(panel_marker) != 1:
    print("ABORTADO: ponto de inserção na página administrativa não encontrado.")
    sys.exit(1)

if 'def quality_dashboard(' in source or 'def quality_dashboard_data(' in source:
    print("ABORTADO: as rotas do painel parecem já existir.")
    sys.exit(1)

# Adiciona o acesso ao painel na página administrativa.
source = source.replace(
    panel_marker,
    '<div class="panel"><h2>Painel de qualidade</h2>'
    '<p>Acompanhe notas, comentarios e miniaturas das imagens avaliadas.</p>'
    '<p><a href="/admin/qualidade">Abrir painel de qualidade</a></p></div>'
    + panel_marker,
    1
)

routes = r'''
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
 <section class="metric"><div class="muted">Media de satisfacao</div><div class="value" id="average">-</div><div class="muted">de 0 a 10</div></section>
 <section class="metric"><div class="muted">Sinalizadas para revisao</div><div class="value" id="flagged">-</div></section>
</div>
<section class="panel">
 <h2>Distribuicao das notas</h2>
 <div id="distribution">Carregando avaliacoes...</div>
</section>
<section class="panel">
 <h2>Historico de feedback</h2>
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
  document.getElementById('flagged').textContent=data.flagged;
  const max=Math.max(1,...data.distribution.map(x=>x.count));
  document.getElementById('distribution').innerHTML=data.distribution.map(x=>
   `<div class="bar-row"><span>Nota ${x.rating}</span><div class="bar-bg"><div class="bar" style="width:${x.count/max*100}%"></div></div><span>${x.count}</span></div>`
  ).join('');
  summary.textContent=`Mostrando ${data.records.length} avaliacao(oes), da mais recente para a mais antiga.`;
  document.getElementById('reviews').innerHTML=data.records.length?data.records.map(x=>
   `<article class="review"><a href="${esc(x.url)}" target="_blank" rel="noopener"><img src="${esc(x.url)}" loading="lazy" alt="Miniatura da imagem avaliada"></a><div class="body"><h3>Nota: ${esc(x.rating)}/10</h3><div class="muted">${esc(x.created_at)}</div><p><strong>Comentario</strong></p><div class="comment">${esc(x.feedback||'Sem comentario')}</div><p><strong>Prompt</strong></p><div class="prompt">${esc(x.prompt)}</div><p class="muted">ID: ${esc(x.id)}</p><p><a href="${esc(x.url)}" target="_blank" rel="noopener">Abrir imagem</a></p></div></article>`
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
                SELECT id, prompt, image_path, created_at, rating, feedback, flagged_bad
                FROM generations
                WHERE rating IS NOT NULL
                  AND TRIM(CAST(rating AS TEXT)) != ''
                ORDER BY created_at DESC
            """).fetchall()

        records = []
        ratings = []
        counts = {n: 0 for n in range(11)}
        for row in rows:
            item = dict(row)
            try:
                rating = int(item["rating"])
                if 0 <= rating <= 10:
                    ratings.append(rating)
                    counts[rating] += 1
            except (TypeError, ValueError):
                continue
            item["url"] = "/outputs/" + Path(item["image_path"]).name
            records.append(item)

        return {
            "total": total,
            "rated_count": len(records),
            "flagged": flagged,
            "average": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "distribution": [
                {"rating": n, "count": counts[n]} for n in range(11)
            ],
            "records": records
        }

'''

source = source.replace(admin_marker, routes + admin_marker, 1)

try:
    compile(source, str(path), "exec")
except Exception as exc:
    print("ABORTADO: o arquivo atualizado nao compilou:", exc)
    sys.exit(1)

backup = Path("modal_app_backup_painel_qualidade_" +
              datetime.now().strftime("%Y%m%d_%H%M%S") + ".py")
shutil.copy2(path, backup)
path.write_text(source, encoding="utf-8")

print("SUCESSO: painel de qualidade adicionado localmente.")
print("Backup criado:", backup)
print("Rotas adicionadas: /admin/qualidade e /admin/qualidade/dados")

from pathlib import Path

p = Path("modal_app.py")
s = p.read_text(encoding="utf-8")

marker = '    @web.get("/health")\n'
if marker not in s:
    raise SystemExit("ERRO: não encontrei o ponto de inserção. Nenhuma alteração foi feita.")

if '@web.get("/api/revisao")' in s:
    raise SystemExit("A área de revisão já existe. Nenhuma alteração foi feita.")

addition = r'''    @web.get("/api/revisao")
    def review_queue():
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
    def review_image(filename: str):
        if Path(filename).name != filename or not filename.lower().endswith(".png"):
            raise HTTPException(400, "Nome de arquivo inválido.")
        image_path = BAD_DIR / filename
        if not image_path.is_file():
            raise HTTPException(404, "Imagem de revisão não encontrada.")
        return FileResponse(image_path, media_type="image/png", filename=filename)

    @web.get("/revisao", response_class=HTMLResponse)
    def review_page():
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
grid.innerHTML=items.map(x=>`<article><a href="${x.url}" target="_blank" rel="noopener"><img src="${x.url}" loading="lazy" alt="Imagem para revisão"></a><div class="content"><div class="prompt">${esc(x.prompt)}</div><div class="date">Sinalizada em: ${esc(x.flagged_at||x.created_at||'Data não disponível')}</div><div>Motivo: ${esc(x.feedback||'Imagem sinalizada como ruim')}</div><p><a href="${x.url}" download>Baixar imagem</a></p></div></article>`).join('');
}catch(e){status.textContent='Não foi possível carregar a fila. Tente novamente.'}})();
</script></main></body></html>""")

'''
s = s.replace(marker, addition + marker, 1)
p.write_text(s, encoding="utf-8")
print("Área de revisão adicionada ao modal_app.py")

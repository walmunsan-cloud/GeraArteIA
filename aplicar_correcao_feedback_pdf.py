from pathlib import Path

p = Path("modal_app.py")
s = p.read_text(encoding="utf-8")
original = s

def replace_once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: esperado 1 trecho, encontrado {count}. Nenhuma alteração foi gravada.")
    s = s.replace(old, new, 1)
    print(f"[OK] {label}")

# 1. Adiciona a dependência usada para criar PDF no ambiente Modal.
replace_once(
    '"transformers>=4.41,<5", "accelerate", "safetensors", "pillow"',
    '"transformers>=4.41,<5", "accelerate", "safetensors", "pillow", "reportlab"',
    "Dependência reportlab"
)

# 2. Troca o botão antigo por avaliação numérica.
replace_once(
    '''<button class="bad" onclick="flagBad('${x.id}')">⚑ Imagem ruim</button>''',
    '''<button class="bad" onclick="evaluateImage('${x.id}')">★ Avaliar imagem</button>''',
    "Botão Avaliar imagem"
)

old_js = """async function flagBad(id){if(!confirm('Sinalizar esta imagem para revisão e melhoria futura?'))return;try{const r=await fetch('/api/avaliar/'+encodeURIComponent(id),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rating:'ruim',feedback:'Sinalizada pelo usuário como imagem ruim'})});if(!r.ok)throw new Error('Falha ao salvar avaliação');alert('Imagem guardada na fila de revisão do Modal. Obrigado!');await loadGallery()}catch(e){alert('Não foi possível registrar a avaliação. Tente novamente.')}}"""
new_js = """async function evaluateImage(id){const raw=prompt('Avalie esta imagem de 0 a 10:');if(raw===null)return;const rating=Number(raw.trim());if(!Number.isInteger(rating)||rating<0||rating>10){alert('Digite uma nota inteira de 0 a 10.');return}const feedback=prompt('Comentário opcional: o que ficou bom ou precisa melhorar?')||'';try{const r=await fetch('/api/avaliar/'+encodeURIComponent(id),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({rating,feedback})});const data=await r.json();if(!r.ok)throw new Error(data.detail||'Falha ao salvar avaliação');alert(data.saved_for_review?'Avaliação registrada. A imagem foi encaminhada para revisão. Obrigado!':'Avaliação registrada. Obrigado pelo feedback!');await loadGallery()}catch(e){alert('Não foi possível registrar a avaliação: '+e.message)}}"""
replace_once(old_js, new_js, "JavaScript de avaliação")

# 3. Substitui o endpoint antigo. Somente notas de 0 a 4 entram na fila.
start_marker = '    @web.post("/api/avaliar/{generation_id}")'
end_marker = '    @web.get("/outputs/{filename}")'
start = s.find(start_marker)
end = s.find(end_marker, start + len(start_marker))
if start < 0 or end < 0:
    raise RuntimeError("Não encontrei os limites do endpoint de avaliação. Nenhuma alteração foi gravada.")

new_rate = '''    @web.post("/api/avaliar/{generation_id}")
    def rate(generation_id: str, payload: dict):
        raw_rating = payload.get("rating")
        try:
            rating = int(raw_rating)
        except (TypeError, ValueError):
            raise HTTPException(400, "A nota deve ser um número inteiro de 0 a 10.")
        if isinstance(raw_rating, bool) or str(raw_rating).strip() not in {str(rating), f"{rating}.0"} or not 0 <= rating <= 10:
            raise HTTPException(400, "A nota deve ser um número inteiro de 0 a 10.")

        feedback = str(payload.get("feedback", "") or "").strip()[:2000]
        flagged = rating <= 4

        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            row = con.execute("SELECT * FROM generations WHERE id=?", (generation_id,)).fetchone()
            if row is None:
                raise HTTPException(404, "Geração não encontrada.")

            source = Path(row["image_path"])
            if not source.is_file():
                raise HTTPException(404, "Arquivo de imagem não encontrado.")

            con.execute(
                "UPDATE generations SET rating=?, feedback=?, flagged_bad=? WHERE id=?",
                (str(rating), feedback, 1 if flagged else 0, generation_id)
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

'''
s = s[:start] + new_rate + s[end:]
print("[OK] Endpoint de avaliação numérica")

# 4. Mostra a nota na fila administrativa.
replace_once(
    '''<div>Motivo: ${esc(x.feedback||'Imagem sinalizada como ruim')}</div>''',
    '''<div>Nota: ${esc(x.rating??'não informada')}/10</div><div>Comentário: ${esc(x.feedback||'Nenhum comentário informado')}</div>''',
    "Nota e comentário na fila"
)

# 5. Cria rota protegida de download PDF.
pdf_route = '''
    @web.get("/admin/testes/relatorio.pdf")
    def admin_test_report_pdf(_admin: bool = Depends(require_admin)):
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from fastapi.responses import StreamingResponse

        report = build_diagnostic_report()
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 48

        def line(text, leading=17):
            nonlocal y
            text = str(text)
            # Quebra linhas longas para caber na página.
            chunks = [text[i:i+95] for i in range(0, len(text), 95)] or [""]
            for chunk in chunks:
                if y < 55:
                    pdf.showPage()
                    y = height - 48
                pdf.drawString(42, y, chunk)
                y -= leading

        line("RELATORIO DE DIAGNOSTICO - GeraArteIA", 23)
        line("Data UTC: " + report["created_at"])
        line("Modelo configurado: " + report["model"])
        line("Total de geracoes: " + str(report["total_generations"]))
        line("Imagens sinalizadas: " + str(report["flagged_generations"]))
        line("")
        line("RESULTADOS DAS VERIFICACOES", 22)
        for item in report["checks"]:
            status = "[OK]" if item["ok"] else "[FALHA]"
            line(status + " " + item["name"] + " - " + item["detail"])

        line("")
        line("LIMITACOES", 22)
        line("O diagnostico verifica arquivos, banco de dados e dependencias.")
        line("Nao executa uma geracao real nem um teste de carga da GPU.")
        line("Resultados positivos nao garantem o funcionamento de todos os fluxos.")
        pdf.save()
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="relatorio_geraarteia.pdf"'}
        )

'''
replace_once(
    '    @web.get("/health")',
    pdf_route + '    @web.get("/health")',
    "Rota protegida de relatório PDF"
)

# 6. Adiciona o link do PDF ao painel administrativo.
replace_once(
    '<p><a href="/admin/testes/relatorio.txt">Baixar relatório TXT</a></p>',
    '<p><a href="/admin/testes/relatorio.txt">Baixar relatório TXT</a> | <a href="/admin/testes/relatorio.pdf">Baixar relatório PDF</a></p>',
    "Link para baixar PDF"
)

if s == original:
    raise RuntimeError("Nenhuma alteração foi produzida.")

p.write_text(s, encoding="utf-8")
print("\\nAlterações gravadas em modal_app.py.")

from pathlib import Path
import re
import shutil
import sys

path = Path("modal_app.py")
source = path.read_text(encoding="utf-8")

# Confirma as três funções que serão atualizadas.
required = [
    "def build_diagnostic_report():",
    "def admin_test_report(_admin: bool = Depends(require_admin)):",
    "def admin_test_report_pdf(_admin: bool = Depends(require_admin)):",
]
for marker in required:
    if source.count(marker) != 1:
        print(f"ABORTADO: estrutura inesperada: {marker}")
        sys.exit(1)

# 1. Acrescenta o histórico de avaliações ao diagnóstico.
start = source.index("    def build_diagnostic_report():")
end = source.index("    @web.get(\"/admin\", response_class=HTMLResponse)", start)

new_diagnostic = '''    def build_diagnostic_report():
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

'''
source = source[:start] + new_diagnostic + source[end:]

# 2. Atualiza o relatório TXT sem depender de textos acentuados.
start = source.index("    def admin_test_report(_admin: bool = Depends(require_admin)):")
end = source.index("    @web.get(\"/admin/testes/relatorio.pdf\")", start)

new_txt = '''    def admin_test_report(_admin: bool = Depends(require_admin)):
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
            "\\n".join(lines),
            headers={"Content-Disposition": 'attachment; filename="relatorio_geraarteia.txt"'}
        )


'''
source = source[:start] + new_txt + source[end:]

# 3. Atualiza o relatório PDF com as mesmas informações.
start = source.index("    def admin_test_report_pdf(_admin: bool = Depends(require_admin)):")
end = source.index("    @web.get(\"/health\")", start)

new_pdf = '''    def admin_test_report_pdf(_admin: bool = Depends(require_admin)):
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from fastapi.responses import StreamingResponse

        report = build_diagnostic_report()
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 48

        def line(text, leading=16):
            nonlocal y
            text = str(text)
            chunks = [text[i:i+92] for i in range(0, len(text), 92)] or [""]
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
        line("Imagens avaliadas: " + str(report["rated_count"]))
        average = report["average_rating"]
        line("Media das notas: " + (
            str(average) if average is not None else "Sem avaliacoes"
        ))
        line("")
        line("RESULTADOS DAS VERIFICACOES", 22)
        for item in report["checks"]:
            status = "[OK]" if item["ok"] else "[FALHA]"
            line(status + " " + item["name"] + " - " + item["detail"])

        line("")
        line("HISTORICO DE FEEDBACK DAS IMAGENS", 22)
        if not report["feedback_records"]:
            line("Ainda nao existem imagens avaliadas.")
        for item in report["feedback_records"]:
            line("----------------------------------------")
            line("Data: " + str(item.get("created_at") or ""))
            line("ID: " + str(item.get("id") or ""))
            line("Nota: " + str(item.get("rating") or ""))
            line("Imagem: " + str(item.get("image_path") or ""))
            line("Prompt: " + str(item.get("prompt") or ""))
            line("Comentario: " + str(item.get("feedback") or "Sem comentario"))
            line("")

        line("")
        line("LIMITACOES", 22)
        line("O diagnostico verifica arquivos, banco de dados e dependencias.")
        line("Nao executa geracao real nem teste de carga da GPU.")
        line("Resultados positivos nao garantem o funcionamento de todos os fluxos.")
        pdf.save()
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="relatorio_geraarteia.pdf"'}
        )

'''
source = source[:start] + new_pdf + source[end:]

# Só grava depois de todas as verificações estruturais passarem.
compile(source, str(path), "exec")
path.write_text(source, encoding="utf-8")
print("SUCESSO: modal_app.py atualizado localmente.")
print("Incluídos: histórico de notas, comentários, prompts, datas e caminhos das imagens.")
print("Nenhuma alteração foi enviada ao GitHub ou ao Modal.")

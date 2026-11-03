from pathlib import Path
from datetime import datetime
import shutil
import sys

path = Path("modal_app.py")
source = path.read_text(encoding="utf-8")

start_marker = '    def admin_test_report_pdf(_admin: bool = Depends(require_admin)):'
end_marker = '    @web.get("/health")'

if source.count(start_marker) != 1 or source.count(end_marker) != 1:
    print("ABORTADO: não encontrei exatamente a função PDF e seu limite.")
    sys.exit(1)

start = source.index(start_marker)
end = source.index(end_marker, start)

new_pdf = r'''    def admin_test_report_pdf(_admin: bool = Depends(require_admin)):
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

'''

updated = source[:start] + new_pdf + source[end:]
try:
    compile(updated, str(path), "exec")
except Exception as exc:
    print("ABORTADO: a nova função não compilou:", exc)
    sys.exit(1)

backup = Path(
    "modal_app_backup_miniaturas_" +
    datetime.now().strftime("%Y%m%d_%H%M%S") + ".py"
)
shutil.copy2(path, backup)
path.write_text(updated, encoding="utf-8")

print("SUCESSO: PDF atualizado para incluir miniaturas reais.")
print("Backup criado:", backup)
print("Arquivo alterado apenas localmente:", path.resolve())

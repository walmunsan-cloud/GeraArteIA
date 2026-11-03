from pathlib import Path
import shutil
import sys
from datetime import datetime

p = Path("modal_app.py")
src = p.read_text(encoding="utf-8")

# Evita aplicar a mesma alteração duas vezes.
if 'def build_diagnostic_report()' in src or 'def require_admin(' in src:
    print("ABORTADO: já existem funções administrativas no arquivo.")
    sys.exit(2)

backup = Path("backups") / ("antes_patch_admin_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / "modal_app.py")

def replace_once(old, new, label):
    global src
    count = src.count(old)
    if count != 1:
        print(f"ABORTADO: trecho '{label}' encontrado {count} vezes; esperado 1.")
        sys.exit(3)
    src = src.replace(old, new, 1)

replace_once(
    '    from fastapi import FastAPI, Form, HTTPException\n',
    '    from fastapi import FastAPI, Form, HTTPException, Depends\n'
    '    from fastapi.security import HTTPBasic, HTTPBasicCredentials\n',
    "imports FastAPI"
)

replace_once(
    '    import torch\n',
    '    import torch\n'
    '    import os\n'
    '    import secrets\n',
    "import torch"
)

replace_once(
    '    web = FastAPI(title="GeraArteIA")\n',
    '    web = FastAPI(title="GeraArteIA")\n'
    '    admin_security = HTTPBasic()\n\n'
    '    def require_admin(credentials: HTTPBasicCredentials = Depends(admin_security)):\n'
    '        expected_user = os.environ.get("GERAARTEIA_ADMIN_USER", "admin")\n'
    '        expected_password = os.environ.get("GERAARTEIA_ADMIN_PASSWORD", "1234")\n'
    '        user_ok = secrets.compare_digest(credentials.username, expected_user)\n'
    '        password_ok = secrets.compare_digest(credentials.password, expected_password)\n'
    '        if not (user_ok and password_ok):\n'
    '            raise HTTPException(status_code=401, detail="Acesso administrativo não autorizado.",\n'
    '                                headers={"WWW-Authenticate": "Basic"})\n'
    '        return True\n',
    "FastAPI initialization"
)

# Protege os três endpoints existentes da fila de revisão.
replace_once(
    '    @web.get("/api/revisao")\n    def review_queue():\n',
    '    @web.get("/api/revisao")\n'
    '    def review_queue(_admin: bool = Depends(require_admin)):\n',
    "review_queue"
)
replace_once(
    '    @web.get("/revisao/imagem/{filename}")\n    def review_image(filename: str):\n',
    '    @web.get("/revisao/imagem/{filename}")\n'
    '    def review_image(filename: str, _admin: bool = Depends(require_admin)):\n',
    "review_image"
)
replace_once(
    '    @web.get("/revisao", response_class=HTMLResponse)\n    def review_page():\n',
    '    @web.get("/revisao", response_class=HTMLResponse)\n'
    '    def review_page(_admin: bool = Depends(require_admin)):\n',
    "review_page"
)

admin_routes = r'''
    def build_diagnostic_report():
        checks = []
        def check(name, ok, detail):
            checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})

        check("Diretório de dados", DATA_DIR.is_dir(), DATA_DIR)
        check("Diretório de imagens", OUTPUT_DIR.is_dir(), OUTPUT_DIR)
        check("Diretório de revisão", BAD_DIR.is_dir(), BAD_DIR)
        try:
            with sqlite3.connect(DB_PATH) as con:
                con.execute("SELECT 1").fetchone()
                columns = {row[1] for row in con.execute("PRAGMA table_info(generations)")}
                required = {"id", "prompt", "image_path", "created_at", "rating", "feedback", "flagged_bad"}
                check("Conexão com banco", True, DB_PATH)
                check("Estrutura do banco", required.issubset(columns),
                      "Colunas presentes: " + ", ".join(sorted(columns)))
                total = con.execute("SELECT COUNT(*) FROM generations").fetchone()[0]
                flagged = con.execute("SELECT COUNT(*) FROM generations WHERE flagged_bad=1").fetchone()[0]
                check("Consulta de registros", True, f"{total} geração(ões); {flagged} sinalizada(s)")
        except Exception as exc:
            total = flagged = 0
            check("Banco de dados", False, f"{type(exc).__name__}: {exc}")

        try:
            import torch
            check("PyTorch", True, f"versão {torch.__version__}; CUDA disponível: {torch.cuda.is_available()}")
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
<div class="panel"><h2>Teste exaustivo computacional</h2>
<p>Executa verificações técnicas de arquivos, banco de dados e dependências instaladas.</p>
<button id="run">Executar diagnóstico</button>
<p><a href="/admin/testes/relatorio.txt">Baixar relatório TXT</a></p>
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

    @web.get("/admin/testes/resultado")
    def admin_test_result(_admin: bool = Depends(require_admin)):
        return build_diagnostic_report()

    @web.get("/admin/testes/relatorio.txt")
    def admin_test_report(_admin: bool = Depends(require_admin)):
        report = build_diagnostic_report()
        lines = [
            "RELATÓRIO DE DIAGNÓSTICO — GeraArteIA",
            "Data UTC: " + report["created_at"],
            "Modelo configurado: " + report["model"],
            "Total de gerações: " + str(report["total_generations"]),
            "Imagens sinalizadas: " + str(report["flagged_generations"]),
            "",
            "RESULTADOS:"
        ]
        for item in report["checks"]:
            lines.append((" [OK] " if item["ok"] else " [FALHA] ") +
                         item["name"] + " — " + item["detail"])
        lines += [
            "",
            "LIMITAÇÕES:",
            "Este diagnóstico verifica arquivos, banco de dados e dependências.",
            "Não executa geração real de imagem nem teste de carga da GPU.",
            "Uma verificação aprovada não garante que todos os fluxos da aplicação funcionem."
        ]
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            "\n".join(lines),
            headers={"Content-Disposition": 'attachment; filename="relatorio_geraarteia.txt"'}
        )

'''

replace_once(
    '    @web.get("/health")\n',
    admin_routes + '    @web.get("/health")\n',
    "health route insertion"
)

# Link discreto para o administrador no rodapé.
replace_once(
    '  <div>Trabalho de Conclusão de Curso — Geração de Imagens por Difusão</div>\n',
    '  <div>Trabalho de Conclusão de Curso — Geração de Imagens por Difusão</div>\n'
    '  <div style="margin-top:8px"><a href="/admin" style="color:#aab3ce">Administrador</a></div>\n',
    "footer admin link"
)

p.write_text(src, encoding="utf-8")
print("Patch aplicado. Backup:", backup)

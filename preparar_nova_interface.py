from pathlib import Path
import shutil
from datetime import datetime

p = Path("modal_app.py")
s = p.read_text(encoding="utf-8")

required = [
    '@web.get("/", response_class=HTMLResponse)',
    '@web.post("/api/avaliar/{generation_id}")',
    '@web.get("/api/revisao")',
    '@web.get("/revisao", response_class=HTMLResponse)',
    '@web.get("/health")',
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit("Cancelado: não encontrei os pontos: " + ", ".join(missing))

backup = Path("backups") / ("antes_painel_admin_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(p, backup / p.name)

print("Estrutura conferida.")
print("Backup adicional:", backup)
print("Nenhuma alteração foi feita ainda.")
print("Pronto para aplicar a atualização em etapas seguras.")

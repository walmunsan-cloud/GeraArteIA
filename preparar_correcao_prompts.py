from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys

root = Path.cwd()
files = [
    root / "app" / "config.py",
    root / "app" / "generator.py",
    root / "app" / "prompt_optimizer.py",
    root / "tests" / "test_generator.py",
]
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = root / "backups" / f"correcao_prompts_{stamp}"
backup.mkdir(parents=True, exist_ok=False)

for path in files:
    if path.exists():
        shutil.copy2(path, backup / path.name)

print(f"Backups criados em: {backup}")
print("\nArquivos preparados para correção:")
for path in files:
    print(f"- {path.relative_to(root)}: {'existe' if path.exists() else 'ausente'}")

optimizer = (root / "app" / "prompt_optimizer.py").read_text(encoding="utf-8")
generator = (root / "app" / "generator.py").read_text(encoding="utf-8")
config = (root / "app" / "config.py").read_text(encoding="utf-8")

checks = {
    "otimizador com método otimizar": "def otimizar(" in optimizer,
    "detecção de categoria": "def detectar_categoria(" in optimizer,
    "gerador com método gerar": "def gerar(" in generator,
    "prompt negativo configurado": "NEGATIVE_PROMPT" in config,
    "limite CLIP identificado": "max_length=77" in generator,
}

print("\nVerificações estruturais:")
for label, ok in checks.items():
    print(f"[{'OK' if ok else 'FALHOU'}] {label}")

if not all(checks.values()):
    print("\nEstrutura diferente da esperada. Nenhum arquivo de aplicação foi alterado.")
    sys.exit(2)

print("\nPreparação concluída. Nenhuma imagem foi gerada.")
print("A próxima alteração será aplicada somente após validar estes pontos.")

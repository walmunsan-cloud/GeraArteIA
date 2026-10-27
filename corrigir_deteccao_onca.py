from pathlib import Path
import ast

path = Path("app/prompt_optimizer.py")
source = path.read_text(encoding="utf-8")

old = '        onca = "onca" in texto or "jaguar" in texto'
new = '        onca = any(x in texto for x in ("onca", "onça", "jaguar"))'

if new not in source:
    if old not in source:
        raise RuntimeError("Não encontrei a linha de detecção da onça.")
    source = source.replace(old, new, 1)

ast.parse(source)
path.write_text(source, encoding="utf-8")
print("Detecção de onça atualizada.")

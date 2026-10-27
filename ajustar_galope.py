from pathlib import Path
import ast

path = Path("app/prompt_optimizer.py")
source = path.read_text(encoding="utf-8")

old = '"realistic galloping pose, clear leg separation"'
new = '"realistic galloping horse, clear leg separation"'

if new not in source:
    if old not in source:
        raise RuntimeError("Não encontrei a instrução de galope esperada.")
    source = source.replace(old, new, 1)

ast.parse(source)
path.write_text(source, encoding="utf-8")
print("Instrução de galope corrigida.")

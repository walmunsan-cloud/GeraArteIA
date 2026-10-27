from pathlib import Path
import ast

path = Path("app/prompt_optimizer.py")
source = path.read_text(encoding="utf-8")

old = '"photorealistic horse",'
new = '"photorealistic horse",\n                "anatomically plausible horse with four legs",'

if "anatomically plausible horse with four legs" not in source:
    if old not in source:
        raise RuntimeError("Não encontrei o trecho de instruções do cavalo.")
    source = source.replace(old, new, 1)

ast.parse(source)
path.write_text(source, encoding="utf-8")
print("Instrução anatômica restaurada.")

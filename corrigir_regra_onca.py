from pathlib import Path
import ast

path = Path("app/prompt_optimizer.py")
source = path.read_text(encoding="utf-8")

old = '        onca = any(x in texto for x in ("onca", "onça", "jaguar"))'
new = '        onca = any(x in texto.split() for x in ("onca", "onça", "jaguar")) or "jaguar" in texto'

if old not in source:
    print("A condição atual é:")
    for line in source.splitlines():
        if "onca =" in line:
            print(line)
    raise SystemExit("Condição esperada não encontrada; arquivo preservado.")

source = source.replace(old, new, 1)

# Garante que a detecção de tatuagem também funcione com a palavra em português.
old_tattoo = '        tatuagem = "tatuagem" in texto or "tattoo" in texto'
new_tattoo = '        tatuagem = any(x in texto for x in ("tatuagem", "tattoo"))'

if old_tattoo in source:
    source = source.replace(old_tattoo, new_tattoo, 1)

ast.parse(source)
path.write_text(source, encoding="utf-8")
print("Condições atualizadas.")

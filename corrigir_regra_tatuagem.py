from pathlib import Path
import ast

path = Path("app/prompt_optimizer.py")
source = path.read_text(encoding="utf-8")

old = '''        elif onca and tatuagem:
            extras.extend([
                "jaguar tattoo design",
                "clear jaguar illustration",
                "recognizable jaguar face and rosette spots",
                "clean tattoo linework",
                "tattoo stencil design",
            ])'''

new = '''        elif tatuagem and (
            onca
            or "onca" in texto
            or "jaguar" in texto
            or "pintada" in texto
        ):
            extras.extend([
                "jaguar tattoo design",
                "clear jaguar illustration",
                "recognizable jaguar face and rosette spots",
                "clean tattoo linework",
                "tattoo stencil design",
            ])'''

if old not in source:
    raise RuntimeError(
        "Bloco da tatuagem não encontrado. Arquivo preservado."
    )

source = source.replace(old, new, 1)
ast.parse(source)
path.write_text(source, encoding="utf-8")
print("Regra de tatuagem ajustada.")

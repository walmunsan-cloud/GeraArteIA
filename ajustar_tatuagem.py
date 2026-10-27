from pathlib import Path
import ast

path = Path("app/prompt_optimizer.py")
source = path.read_text(encoding="utf-8")

old = '''        elif onca and tatuagem:
            extras.extend([
                "jaguar tattoo design",
                "clear jaguar illustration",
                "clean tattoo linework",
                "design on skin",
            ])'''

new = '''        elif onca and tatuagem:
            extras.extend([
                "jaguar tattoo design",
                "clear jaguar illustration",
                "recognizable jaguar face and rosette spots",
                "clean tattoo linework",
                "tattoo stencil design",
            ])'''

if new not in source:
    if old not in source:
        raise RuntimeError(
            "Não encontrei o bloco esperado da regra de tatuagem. "
            "Nenhuma alteração foi feita."
        )
    source = source.replace(old, new, 1)

ast.parse(source)
path.write_text(source, encoding="utf-8")
print("Regra da tatuagem atualizada.")

from pathlib import Path
import ast

path = Path("app/prompt_optimizer.py")
source = path.read_text(encoding="utf-8")

old = '''        onca = any(x in texto.split() for x in ("onca", "onça", "jaguar")) or "jaguar" in texto'''

new = '''        onca = any(x in texto for x in (
            "onca", "onça", "jaguar"
        ))'''

if old in source:
    source = source.replace(old, new, 1)
elif '        onca = any(x in texto for x in (' not in source:
    # Compatibilidade com a versão anterior da condição.
    import re
    source, count = re.subn(
        r'(?m)^        onca = .*\\n',
        new + "\\n",
        source,
        count=1
    )
    if count != 1:
        raise RuntimeError("Não encontrei a condição de detecção da onça.")

# A regra da tatuagem deve vir antes da regra genérica de animal.
old_branch = '''        elif onca and tatuagem:
            extras.extend([
                "jaguar tattoo design",
                "clear jaguar illustration",
                "recognizable jaguar face and rosette spots",
                "clean tattoo linework",
                "tattoo stencil design",
            ])'''

if old_branch not in source:
    raise RuntimeError("Não encontrei o bloco esperado de tatuagem.")

# Normaliza hífen e espaços para reconhecer onça-pintada.
old_normalize = '        texto = self._normalizar(prompt)'
new_normalize = '''        texto = self._normalizar(prompt).replace("-", " ")'''

if old_normalize in source:
    source = source.replace(old_normalize, new_normalize, 1)

ast.parse(source)
path.write_text(source, encoding="utf-8")
print("Reconhecimento de onça-pintada atualizado.")

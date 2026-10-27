from pathlib import Path
import ast

path = Path("app/prompt_optimizer.py")
source = path.read_text(encoding="utf-8")

changes = [
    (
        '"full body animal, full body visible, head to hooves",',
        '"full body animal, complete head and face, full body visible, head to hooves",',
        "instrucao de cabeca do cavalo",
    ),
    (
        '                "entire giraffe visible",',
        '                "entire giraffe visible",\n'
        '            ])\n'
        '            if "savana" in texto:\n'
        '                extras.append("savanna landscape")\n'
        '            #',
        "instrucao de paisagem da girafa",
    ),
]

# Aplicar a primeira correção somente se ainda não existir.
old, new, label = changes[0]
if "complete head and face" not in source:
    if old not in source:
        raise RuntimeError(f"Não encontrei o trecho para: {label}")
    source = source.replace(old, new, 1)
    print(f"Aplicado: {label}")
else:
    print(f"Já presente: {label}")

# Inserir a paisagem da savana no bloco da girafa, sem duplicar.
if 'extras.append("savanna landscape")' not in source:
    marker = '                "entire giraffe visible",'
    if marker not in source:
        raise RuntimeError("Não encontrei o bloco da girafa.")
    source = source.replace(
        marker,
        marker + '\n            ])\n            if "savana" in texto:\n                extras.append("savanna landscape")\n            extras.extend([',
        1,
    )
    # Ajustar a lista aberta após a inserção, removendo o fechamento original duplicado.
    source = source.replace(
        '            extras.extend([\n                "realistic giraffe",\n'
        '                "long natural giraffe neck",\n'
        '                "four visible legs",\n'
        '                "entire giraffe visible",\n'
        '            ])\n            if "savana" in texto:\n'
        '                extras.append("savanna landscape")\n'
        '            extras.extend([',
        '            extras.extend([\n'
        '                "realistic giraffe",\n'
        '                "long natural giraffe neck",\n'
        '                "four visible legs",\n'
        '                "entire giraffe visible",\n'
        '            ])\n'
        '            if "savana" in texto:\n'
        '                extras.append("savanna landscape")',
        1,
    )
    print("Aplicado: instrucao de paisagem da girafa")
else:
    print("Já presente: instrucao de paisagem da girafa")

ast.parse(source)
path.write_text(source, encoding="utf-8")
print("Sintaxe validada.")

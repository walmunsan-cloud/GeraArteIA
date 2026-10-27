from pathlib import Path
import ast

path = Path("app/prompt_optimizer.py")
source = path.read_text(encoding="utf-8")

# Corrigir o texto do cavalo.
old_horse = '"full body animal, full body visible, head to hooves",'
new_horse = '"full body animal, complete head and face, full body visible, head to hooves",'

if "complete head and face" not in source:
    if old_horse not in source:
        raise RuntimeError("Não encontrei a instrução do cavalo.")
    source = source.replace(old_horse, new_horse, 1)

# Acrescentar a paisagem apenas quando o prompt da girafa citar savana.
old_giraffe = '''        elif girafa:
            extras.extend([
                "realistic giraffe",
                "long natural giraffe neck",
                "four visible legs",
                "entire giraffe visible",
            ])'''

new_giraffe = '''        elif girafa:
            extras.extend([
                "realistic giraffe",
                "long natural giraffe neck",
                "four visible legs",
                "entire giraffe visible",
            ])
            if "savana" in texto or "savanna" in texto:
                extras.append("savanna landscape")'''

if 'extras.append("savanna landscape")' not in source:
    if old_giraffe not in source:
        raise RuntimeError("O bloco da girafa não corresponde ao esperado.")
    source = source.replace(old_giraffe, new_giraffe, 1)

# Validar antes de gravar.
ast.parse(source)
path.write_text(source, encoding="utf-8")
print("Correções aplicadas e sintaxe validada.")

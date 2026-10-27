from pathlib import Path
from datetime import datetime
import re
import shutil
import sys

from app.prompt_optimizer import PromptOptimizer
from transformers import CLIPTokenizer
from app.config import MODEL_PATH

path = Path("app/prompt_optimizer.py")
original = path.read_text(encoding="utf-8")

# Reduz redundância: cavalos recebem as instruções específicas,
# sem acumular todas as instruções genéricas de animais.
generic_old = '        if "animal" in categoria:'
generic_new = '''        if "animal" in categoria and not any(
            x in texto for x in ("cavalo", "cavalos", "egua", "eguas", "potro", "potros")
        ):'''

if generic_old not in original:
    raise RuntimeError("Bloco genérico de animais não encontrado.")

updated = original.replace(generic_old, generic_new, 1)

# Substitui o bloco de cavalo por instruções mais compactas e prioritárias.
pattern = (
    r'        if any\(x in texto for x in '
    r'\("cavalo", "cavalos", "egua", "eguas", "potro", "potros"\)\):\n'
    r'.*?(?=        if "animal" in categoria and not any\()'
)

replacement = '''        if any(x in texto for x in ("cavalo", "cavalos", "egua", "eguas", "potro", "potros")):
            extras.extend([
                "photorealistic horse, anatomically correct",
                "four natural separate legs and realistic hooves",
                "natural horse joints and body proportions",
                "full body visible from head to hooves",
                "side view, horse at camera level",
            ])

            if any(x in texto for x in ("correndo", "galopando", "galope", "corrida")):
                extras.extend([
                    "realistic galloping pose",
                    "clear separation of all four legs",
                ])
            elif any(x in texto for x in ("parado", "pastando", "em pe")):
                extras.append("horse standing naturally on four legs")

'''

updated, count = re.subn(pattern, replacement, updated, count=1, flags=re.S)
if count != 1:
    raise RuntimeError("Bloco de cavalo não corresponde ao formato esperado.")

# Backup específico antes de salvar.
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = Path("backups") / f"prompt_optimizer_{stamp}.py"
backup.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(path, backup)

path.write_text(updated, encoding="utf-8")
print(f"Backup: {backup}")
print("Otimizador atualizado.")

# Verificar sintaxe antes de testar.
import ast
ast.parse(path.read_text(encoding="utf-8"))

tokenizer = CLIPTokenizer.from_pretrained(
    MODEL_PATH, subfolder="tokenizer", local_files_only=True
)
optimizer = PromptOptimizer()

casos = [
    ("Cavalo", "Um cavalo realista galopando em um campo"),
    ("Girafa", "Uma girafa inteira na savana africana"),
    ("SUV rosa", "Um SUV rosa com um laço rosa"),
    ("Tatuagem de onça", "Uma tatuagem realista de uma onça"),
    ("Ciclista", "Um ciclista andando de bicicleta na ciclovia da cidade"),
]

falhas = []
for nome, entrada in casos:
    prompt = optimizer.otimizar(entrada)
    ids = tokenizer(prompt, add_special_tokens=True, truncation=False)["input_ids"]
    print(f"\n{nome}: {len(ids)} tokens")
    print(prompt)

    if len(ids) > 77:
        falhas.append(f"{nome} excede 77 tokens ({len(ids)})")

if falhas:
    print("\nATENÇÃO: alguns prompts ainda excedem o limite:")
    for falha in falhas:
        print("-", falha)
    sys.exit(1)

print("\nTodos os prompts estão dentro do limite de 77 tokens.")

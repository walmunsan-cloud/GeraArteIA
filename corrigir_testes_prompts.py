from pathlib import Path
import ast

path = Path("app/prompt_optimizer.py")
source = path.read_text(encoding="utf-8")

source = source.replace(
    '"full body visible, head to hooves",',
    '"full body animal, full body visible, head to hooves",',
    1,
)

source = source.replace(
    '"long natural neck",',
    '"long natural giraffe neck",',
    1,
)

ast.parse(source)
path.write_text(source, encoding="utf-8")
print("Termos esperados pelos testes restaurados.")

from pathlib import Path
from datetime import datetime
import re
import shutil
import subprocess
import sys

root = Path.cwd()
config_path = root / "app" / "config.py"
generator_path = root / "app" / "generator.py"
optimizer_path = root / "app" / "prompt_optimizer.py"
tests_path = root / "tests" / "test_generator.py"

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = root / "backups" / f"correcao_lote_{stamp}"
backup.mkdir(parents=True)

paths = [config_path, generator_path, optimizer_path, tests_path]
for path in paths:
    shutil.copy2(path, backup / path.name)

print(f"Backup criado: {backup}")

config = config_path.read_text(encoding="utf-8")
generator = generator_path.read_text(encoding="utf-8")
optimizer = optimizer_path.read_text(encoding="utf-8")
tests = tests_path.read_text(encoding="utf-8")

# 1. Remover termos exclusivos de cavalos do prompt negativo geral.
pattern = r'NEGATIVE_PROMPT\s*=\s*\(.*?\n\)'
match = re.search(pattern, config, re.S)
if not match:
    raise RuntimeError("NEGATIVE_PROMPT não encontrado; nenhuma alteração aplicada.")

general_negative = '''NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, deformed, bad anatomy, "
    "bad proportions, extra limbs, extra fingers, malformed hands, "
    "missing limbs, missing legs, extra legs, fused legs, "
    "cropped, cut off, close-up, zoomed in, text, watermark, logo"
)

HORSE_NEGATIVE_PROMPT = (
    "deformed horse legs, duplicated horse legs, broken joints, "
    "unnatural equine anatomy, overlapping legs, floating hooves, "
    "fused legs, extra legs, malformed hooves, extra hooves"
)'''
config = config[:match.start()] + general_negative + config[match.end():]

# 2. Fazer o gerador escolher o negativo de cavalo somente para cavalos.
if "HORSE_NEGATIVE_PROMPT" not in generator:
    generator = generator.replace(
        "    NEGATIVE_PROMPT,\n)",
        "    NEGATIVE_PROMPT,\n    HORSE_NEGATIVE_PROMPT,\n)",
        1,
    )

if "HORSE_NEGATIVE_PROMPT" not in generator:
    raise RuntimeError("Não foi possível inserir a importação do prompt negativo de cavalos.")

old_call = "        resultado = self.pipe(\n            prompt=prompt_final,\n            negative_prompt=NEGATIVE_PROMPT,"
new_call = '''        texto_normalizado = self.prompt_optimizer._normalizar(prompt_original)
        palavras_cavalo = ("cavalo", "cavalos", "egua", "eguas", "potro", "potros")
        negativo_final = NEGATIVE_PROMPT
        if any(palavra in texto_normalizado for palavra in palavras_cavalo):
            negativo_final = f"{NEGATIVE_PROMPT}, {HORSE_NEGATIVE_PROMPT}"

        resultado = self.pipe(
            prompt=prompt_final,
            negative_prompt=negativo_final,'''

if old_call not in generator:
    raise RuntimeError("Trecho de chamada do modelo diferente do esperado.")

generator = generator.replace(old_call, new_call, 1)

# 3. Priorizar as instruções específicas do cavalo antes das genéricas.
start = optimizer.find('        if "animal" in categoria:')
horse_start = optimizer.find('        if any(x in texto for x in ("cavalo", "cavalos"')
girafe_start = optimizer.find('        if "girafa" in texto:')
if min(start, horse_start, girafe_start) < 0 or not start < horse_start < girafe_start:
    raise RuntimeError("Estrutura de blocos do otimizador inesperada.")

generic_block = optimizer[start:horse_start]
horse_block = optimizer[horse_start:girafe_start]
optimizer = optimizer[:start] + horse_block + generic_block + optimizer[girafe_start:]

# 4. Garantir que a regra de tatuagem reconheça onça/jaguar e produza extras.
needle = '''        if "onca" in texto or "jaguar" in texto:
            if "tatuagem" in texto or "tattoo" in texto:
                extras.extend(['''
if needle not in optimizer:
    raise RuntimeError("Bloco de tatuagem não encontrado.")

# O código existente já contém a regra; normalização de acentos é feita em _normalizar.
# Adicionar teste sem duplicá-lo.
test_name = "def test_tatuagem_onca_adiciona_instrucoes():"
if test_name not in tests:
    tests += '''

def test_tatuagem_onca_adiciona_instrucoes():
    optimizer = PromptOptimizer()
    texto = "Uma tatuagem realista de uma onça"
    prompt = optimizer.otimizar(texto)
    assert "tattoo design" in prompt
    assert "clean tattoo linework" in prompt
'''

# Assegurar que os testes tenham a importação necessária.
if "from app.prompt_optimizer import PromptOptimizer" not in tests:
    tests = "from app.prompt_optimizer import PromptOptimizer\n" + tests

# Salvar as alterações só depois de validar todos os pontos estruturais.
config_path.write_text(config, encoding="utf-8")
generator_path.write_text(generator, encoding="utf-8")
optimizer_path.write_text(optimizer, encoding="utf-8")
tests_path.write_text(tests, encoding="utf-8")

print("Arquivos atualizados.")
print("Backup preservado.")

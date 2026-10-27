from pathlib import Path
from datetime import datetime
import shutil
import subprocess
import sys
import ast

from transformers import CLIPTokenizer
from app.config import MODEL_PATH

path = Path("app/prompt_optimizer.py")
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = Path("backups") / f"prompt_optimizer_antes_reescrita_{stamp}.py"
backup.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(path, backup)
print(f"Backup preservado: {backup}")

source = r'''import re
import unicodedata


class PromptOptimizer:
    def __init__(self):
        self.animal_keywords = [
            "cavalo", "cavalos", "egua", "eguas", "potro", "potros",
            "cachorro", "cao", "caes", "gato", "gatos", "leao", "leoes",
            "onca", "oncas", "jaguar", "jaguares", "elefante", "girafa",
            "girafas", "zebra", "boi", "vaca", "touro", "urso", "lobo",
            "passaro", "animal", "animais",
        ]
        self.person_keywords = [
            "homem", "mulher", "menino", "menina", "crianca", "pessoa",
            "pessoas", "jovem", "idoso", "idosa", "rapaz", "moca", "ciclista",
        ]
        self.vehicle_keywords = [
            "carro", "automovel", "veiculo", "suv", "moto", "motocicleta",
            "caminhao", "onibus", "bicicleta", "bicicletas", "bike",
        ]
        self.landscape_keywords = [
            "paisagem", "praia", "montanha", "floresta", "campo", "cidade",
            "deserto", "lago", "rio", "cachoeira", "savana", "pastagem",
            "pasto", "ciclovia",
        ]
        self.object_keywords = [
            "mesa", "cadeira", "computador", "celular", "telefone",
            "relogio", "copo", "garrafa", "livro", "camera", "laco",
            "lacinho", "gravata", "brinco",
        ]

    @staticmethod
    def _normalizar(texto: str) -> str:
        texto = unicodedata.normalize("NFKD", texto.lower())
        texto = "".join(c for c in texto if not unicodedata.combining(c))
        return re.sub(r"\\s+", " ", texto).strip()

    def detectar_categoria(self, texto: str) -> str:
        normalizado = self._normalizar(texto)
        grupos = [
            ("animal", self.animal_keywords),
            ("pessoa", self.person_keywords),
            ("veiculo", self.vehicle_keywords),
            ("paisagem", self.landscape_keywords),
            ("objeto", self.object_keywords),
        ]
        categorias = [
            categoria for categoria, palavras in grupos
            if any(self._normalizar(p) in normalizado for p in palavras)
        ]
        if "tatuagem" in normalizado or "tattoo" in normalizado:
            categorias.append("tatuagem")
        return "+".join(dict.fromkeys(categorias)) if categorias else "geral"

    def otimizar(self, prompt: str) -> str:
        prompt = re.sub(r"\\s+", " ", prompt.strip())
        if not prompt:
            return ""

        texto = self._normalizar(prompt)
        categoria = self.detectar_categoria(prompt)
        extras = []

        cavalo = any(x in texto for x in (
            "cavalo", "cavalos", "egua", "eguas", "potro", "potros"
        ))
        girafa = "girafa" in texto
        onca = "onca" in texto or "jaguar" in texto
        tatuagem = "tatuagem" in texto or "tattoo" in texto
        bicicleta = any(x in texto for x in (
            "bicicleta", "bicicletas", "bike", "ciclista", "biciclista"
        ))

        # Instrucoes de maior prioridade primeiro; evitar redundancia.
        if cavalo:
            extras.extend([
                "photorealistic horse",
                "four anatomically correct separate legs",
                "realistic joints and hooves",
                "full body visible, head to hooves",
                "natural horse proportions",
            ])
            if any(x in texto for x in ("correndo", "galopando", "galope", "corrida")):
                extras.append("realistic galloping pose, clear leg separation")
            elif any(x in texto for x in ("parado", "pastando", "em pe")):
                extras.append("horse standing naturally on four legs")
        elif girafa:
            extras.extend([
                "realistic giraffe",
                "long natural neck",
                "four visible legs",
                "entire giraffe visible",
            ])
        elif onca and tatuagem:
            extras.extend([
                "jaguar tattoo design",
                "clear jaguar illustration",
                "clean tattoo linework",
                "design on skin",
            ])
        elif "animal" in categoria:
            extras.extend([
                "realistic animal anatomy",
                "full body visible",
                "natural body proportions",
            ])

        if "pessoa" in categoria:
            extras.extend(["natural human anatomy", "natural body proportions"])

        if "veiculo" in categoria:
            extras.extend([
                "complete vehicle visible",
                "correct vehicle proportions",
            ])

        if bicicleta:
            extras.extend([
                "complete bicycle with both wheels visible",
                "cyclist riding in a designated bike lane",
                "natural riding posture",
            ])

        if "paisagem" in categoria and not cavalo and not girafa:
            extras.append("natural perspective, coherent environment")

        if any(x in texto for x in ("laco", "lacinho")):
            extras.append("clearly visible bow accessory")

        if "rosa" in texto and "veiculo" in categoria:
            extras.append("vehicle paint is pink, preserve requested color")

        if "fotografia" in texto or "foto" in texto:
            extras.append("photorealistic")
        if "cinematografico" in texto or "cinematografica" in texto:
            extras.append("cinematic")

        resultado = [prompt]
        vistos = {self._normalizar(prompt)}
        for extra in extras:
            chave = self._normalizar(extra)
            if chave not in vistos:
                resultado.append(extra)
                vistos.add(chave)
        return ", ".join(resultado)
'''

path.write_text(source, encoding="utf-8")
ast.parse(source)
print("Otimizador reescrito e sintaxe validada.")

# Recarregar a classe do arquivo atualizado.
import importlib
import app.prompt_optimizer as modulo
importlib.invalidate_caches()
modulo = importlib.reload(modulo)
otimizador = modulo.PromptOptimizer()

tokenizer = CLIPTokenizer.from_pretrained(
    MODEL_PATH, subfolder="tokenizer", local_files_only=True
)

casos = [
    ("Cavalo", "Um cavalo realista galopando em um campo"),
    ("Girafa", "Uma girafa inteira na savana africana"),
    ("SUV rosa", "Um SUV rosa com um laço rosa"),
    ("Tatuagem de onça", "Uma tatuagem realista de uma onça"),
    ("Ciclista", "Um ciclista andando de bicicleta na ciclovia da cidade"),
]

falhas = []
for nome, entrada in casos:
    prompt = otimizador.otimizar(entrada)
    tokens = tokenizer(prompt, add_special_tokens=True, truncation=False)["input_ids"]
    print(f"\n{nome}: {len(tokens)} tokens")
    print(prompt)
    if len(tokens) > 77:
        falhas.append(f"{nome}: {len(tokens)} tokens")
    if nome == "Tatuagem de onça" and "jaguar tattoo design" not in prompt:
        falhas.append("Tatuagem de onça: regra específica ausente")
    if nome == "SUV rosa" and "vehicle paint is pink" not in prompt:
        falhas.append("SUV rosa: regra de cor ausente")
    if nome == "Ciclista" and "designated bike lane" not in prompt:
        falhas.append("Ciclista: regra de ciclovia ausente")

if falhas:
    print("\nVALIDACAO FALHOU:")
    for falha in falhas:
        print("-", falha)
    sys.exit(1)

print("\nTodos os prompts passaram na verificacao de tokens e regras.")

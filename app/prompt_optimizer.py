import re
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
        return re.sub(r"\s+", " ", texto).strip()

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
        if any(x in normalizado for x in ("tatuagem", "tattoo")):
            categorias.append("tatuagem")
        return "+".join(dict.fromkeys(categorias)) if categorias else "geral"

    def otimizar(self, prompt: str) -> str:
        prompt = re.sub(r"\s+", " ", prompt.strip())
        if not prompt:
            return ""

        texto = self._normalizar(prompt).replace("-", " ")
        categoria = self.detectar_categoria(prompt)
        extras = []

        cavalo = any(x in texto for x in (
            "cavalo", "cavalos", "egua", "eguas", "potro", "potros"
        ))
        girafa = "girafa" in texto
        onca = any(x in texto for x in ("onca", "onça", "jaguar"))
        tatuagem = any(x in texto for x in ("tatuagem", "tattoo"))
        bicicleta = any(x in texto for x in (
            "bicicleta", "bicicletas", "bike", "ciclista", "biciclista"
        ))

        if cavalo:
            extras.extend([
                "photorealistic horse",
                "anatomically plausible horse with four legs",
                "four anatomically correct separate legs",
                "realistic joints and hooves",
                "full body animal, complete head and face, full body visible, head to hooves",
                "natural horse proportions",
            ])
            if any(x in texto for x in ("correndo", "galopando", "galope", "corrida")):
                extras.append("realistic galloping horse, clear leg separation")
            elif any(x in texto for x in ("parado", "pastando", "em pe")):
                extras.append("horse standing naturally on four legs")
        elif girafa:
            extras.extend([
                "realistic giraffe",
                "long natural giraffe neck",
                "four visible legs",
                "entire giraffe visible",
            ])
            if "savana" in texto or "savanna" in texto:
                extras.append("savanna landscape")
        elif tatuagem and (onca or "onca" in texto or "jaguar" in texto or "pintada" in texto):
            extras.extend([
                "jaguar tattoo design",
                "clear jaguar illustration",
                "recognizable jaguar face and rosette spots",
                "clean tattoo linework",
                "tattoo stencil design",
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
                "natural perspective",
                "coherent environment"
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

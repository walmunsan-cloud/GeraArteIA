import re
import unicodedata


class PromptOptimizer:
    """Complementa prompts sem substituir a intenção original do usuário."""

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
        texto = "".join(
            caractere for caractere in texto
            if not unicodedata.combining(caractere)
        )
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
            categoria
            for categoria, palavras in grupos
            if any(self._normalizar(palavra) in normalizado for palavra in palavras)
        ]
        if any(termo in normalizado for termo in ("tatuagem", "tattoo")):
            categorias.append("tatuagem")
        return "+".join(dict.fromkeys(categorias)) if categorias else "geral"

    def otimizar(self, prompt: str) -> str:
        prompt = re.sub(r"\s+", " ", prompt.strip())
        if not prompt:
            return ""

        texto = self._normalizar(prompt).replace("-", " ")
        categoria = self.detectar_categoria(prompt)
        extras = []

        cavalo = any(
            termo in texto
            for termo in ("cavalo", "cavalos", "egua", "eguas", "potro", "potros")
        )
        girafa = any(termo in texto for termo in ("girafa", "girafas"))
        onca = any(termo in texto for termo in ("onca", "oncas", "jaguar"))
        tatuagem = any(termo in texto for termo in ("tatuagem", "tattoo"))
        bicicleta = any(
            termo in texto
            for termo in ("bicicleta", "bicicletas", "bike", "ciclista", "biciclista")
        )
        veiculo_rosa = (
            any(termo in texto for termo in ("rosa", "cor de rosa", "pink"))
            and "veiculo" in categoria
        )
        menciona_laco = any(termo in texto for termo in ("laco", "lacinho", "bow"))

        if cavalo:
            extras.extend([
                "photorealistic horse",
                "anatomically plausible horse with four legs",
                "four anatomically correct legs with clear separation",
                "realistic joints and hooves",
                "natural horse proportions",
                "entire horse visible from head to hooves",
                "subject centered with space around the body",
            ])
            if any(termo in texto for termo in (
                "correndo", "galopando", "galope", "corrida"
            )):
                extras.append("realistic galloping pose with anatomically plausible legs")
            elif any(termo in texto for termo in ("parado", "pastando", "em pe")):
                extras.append("horse standing naturally on four legs")

        if girafa:
            extras.extend([
                "realistic giraffe anatomy",
                "long natural giraffe neck",
                "four visible legs",
                "entire giraffe visible, including head, neck and hooves",
                "wide composition with space around the animal",
            ])
            if any(termo in texto for termo in ("savana", "savanna")):
                extras.append("African savanna landscape")

        if tatuagem and onca:
            extras.extend([
                "recognizable jaguar tattoo design",
                "clearly defined jaguar rosette spots",
                "clean tattoo linework",
                "balanced tattoo composition",
                "tattoo stencil style",
            ])

        if "animal" in categoria and not cavalo and not girafa:
            extras.extend([
                "realistic animal anatomy",
                "natural body proportions",
                "complete subject visible in frame",
            ])

        if "pessoa" in categoria:
            extras.extend([
                "natural human anatomy",
                "natural body proportions",
            ])

        if "veiculo" in categoria:
            extras.extend([
                "complete vehicle visible",
                "correct vehicle proportions",
                "wheels and body fully inside the frame",
            ])

        if bicicleta:
            extras.extend([
                "complete bicycle with both wheels visible",
                "cyclist riding in a designated urban bike lane",
                "natural riding posture",
                "realistic bicycle frame and wheel geometry",
                "coherent city environment",
            ])

        if veiculo_rosa:
            extras.append("pink vehicle paint, preserve the requested pink color")

        if menciona_laco:
            extras.append("clearly visible bow accessory")

        if "paisagem" in categoria:
            extras.extend([
                "coherent environmental perspective",
                "balanced composition",
            ])

        if any(termo in texto for termo in ("fotografia", "fotografico", "foto")):
            extras.append("photorealistic")
        if any(termo in texto for termo in ("cinematografico", "cinematografica")):
            extras.append("cinematic lighting and composition")

        resultado = [prompt]
        vistos = {self._normalizar(prompt)}
        for extra in extras:
            chave = self._normalizar(extra)
            if chave not in vistos:
                resultado.append(extra)
                vistos.add(chave)

        return ", ".join(resultado)

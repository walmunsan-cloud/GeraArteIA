import re
import unicodedata


class PromptOptimizer:
    def __init__(self):
        self.animal_keywords = [
            "cavalo", "cavalos", "egua", "eguas", "potro", "potros",
            "cachorro", "cao", "caes", "gato", "gatos", "leao", "leoes",
            "tigre", "tigres", "onca", "oncas", "jaguar", "jaguares",
            "elefante", "elefantes", "girafa", "girafas", "zebra", "zebras",
            "boi", "bois", "vaca", "vacas", "touro", "touros",
            "urso", "ursos", "lobo", "lobos", "passaro", "passaros",
            "animal", "animais",
        ]
        self.person_keywords = [
            "homem", "mulher", "menino", "menina", "crianca",
            "pessoa", "pessoas", "jovem", "idoso", "idosa",
            "rapaz", "moca", "ciclista",
        ]
        self.vehicle_keywords = [
            "carro", "carros", "automovel", "veiculo", "suv",
            "moto", "motocicleta", "caminhao", "onibus",
            "bicicleta", "bicicletas", "bike", "biciclista",
            "ciclista", "aviao", "avioes", "helicoptero", "barco", "navio",
        ]
        self.landscape_keywords = [
            "paisagem", "praia", "montanha", "floresta", "campo",
            "cidade", "deserto", "lago", "rio", "cachoeira", "savana",
            "pastagem", "pasto", "ciclovia",
        ]
        self.object_keywords = [
            "mesa", "cadeira", "computador", "celular", "telefone",
            "relogio", "copo", "garrafa", "livro", "camera",
            "laco", "lacinho", "gravata", "brinco",
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
            categoria
            for categoria, palavras in grupos
            if any(self._normalizar(p) in normalizado for p in palavras)
        ]
        if any(x in normalizado for x in ("tatuagem", "tattoo")):
            categorias.append("tatuagem")
        return "+".join(dict.fromkeys(categorias)) if categorias else "geral"

    def otimizar(self, prompt: str) -> str:
        prompt = re.sub(r"\s+", " ", prompt.strip())
        if not prompt:
            return ""

        texto = self._normalizar(prompt)
        categoria = self.detectar_categoria(prompt)
        extras = []

        if "animal" in categoria:
            extras.extend([
                "realistic animal anatomy",
                "full body animal",
                "complete head and face",
                "natural body proportions",
                "wide shot",
                "entire body visible",
                "space around the subject",
            ])

        if any(x in texto for x in ("cavalo", "cavalos", "egua", "eguas", "potro", "potros")):
            extras.extend([
                "photorealistic horse",
                "anatomically plausible horse with four legs",
                "four separate legs attached naturally to the body",
                "realistic horse joints and correctly shaped hooves",
                "clear silhouette and natural horse proportions",
                "full body horse visible, head to hooves",
                "side view, camera at horse level",
                "simple uncluttered background",
            ])

            if any(x in texto for x in ("correndo", "galopando", "galope", "corrida")):
                extras.extend([
                    "realistic galloping horse",
                    "natural coordinated leg positions",
                    "clear separation between visible legs",
                ])
            elif any(x in texto for x in ("parado", "pastando", "em pe", "em pé")):
                extras.append("horse standing naturally on four legs")

        if "girafa" in texto:
            extras.extend([
                "long natural giraffe neck",
                "four visible legs",
                "entire giraffe visible",
            ])
            if "savana" in texto:
                extras.append("savanna landscape")

        if "onca" in texto or "jaguar" in texto:
            if "tatuagem" in texto or "tattoo" in texto:
                extras.extend([
                    "tattoo design",
                    "clear jaguar illustration",
                    "clean tattoo linework",
                    "design on skin",
                ])

        if "pessoa" in categoria:
            extras.extend(["natural human anatomy", "natural body proportions"])

        if "veiculo" in categoria:
            extras.extend([
                "complete vehicle visible from front to rear",
                "correct vehicle proportions",
                "wide shot with space around the vehicle",
            ])

        if any(x in texto for x in ("bicicleta", "bike", "ciclista", "biciclista")):
            extras.extend([
                "complete bicycle with both wheels visible",
                "cyclist riding in a designated bike lane",
                "natural riding posture",
            ])

        if "paisagem" in categoria:
            extras.append("natural perspective and coherent environment")

        if any(x in texto for x in ("laco", "lacinho")):
            extras.append("clearly visible bow accessory")

        if "rosa" in texto and "veiculo" in categoria:
            extras.append("vehicle paint is pink, preserve requested color")

        if "futurista" in texto:
            extras.append("futuristic")
        if "a noite" in texto:
            extras.append("night scene")
        if "por do sol" in texto:
            extras.append("sunset")
        if "nascer do sol" in texto:
            extras.append("sunrise")
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

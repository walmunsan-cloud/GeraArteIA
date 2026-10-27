import re
import unicodedata


class PromptOptimizer:
    def __init__(self):
        self.animal_keywords = [
            "cavalo", "cavalos", "égua", "éguas", "potro", "potros",
            "cachorro", "cão", "cães", "gato", "gatos",
            "leão", "leões", "tigre", "tigres", "onça", "onças",
            "elefante", "elefantes", "girafa", "girafas",
            "zebra", "zebras", "boi", "bois", "vaca", "vacas",
            "touro", "touros", "urso", "ursos", "lobo", "lobos",
            "macaco", "macacos", "pássaro", "pássaros",
            "animal", "animais",
        ]

        self.person_keywords = [
            "homem", "mulher", "menino", "menina", "criança",
            "pessoa", "pessoas", "jovem", "idoso", "idosa",
            "rapaz", "moça", "ciclista",
        ]

        self.vehicle_keywords = [
            "carro", "carros", "automóvel", "veículo", "suv",
            "moto", "motocicleta", "caminhão", "ônibus",
            "bicicleta", "bicicletas", "bike", "biciclista",
            "avião", "aviões", "helicóptero", "barco", "navio",
        ]

        self.landscape_keywords = [
            "paisagem", "praia", "montanha", "floresta", "campo",
            "cidade", "deserto", "lago", "rio", "cachoeira",
            "savana",
        ]

        self.object_keywords = [
            "mesa", "cadeira", "computador", "celular", "telefone",
            "relógio", "copo", "garrafa", "livro", "câmera",
            "laço", "gravata", "brinco",
        ]

    @staticmethod
    def _normalizar(texto: str) -> str:
        texto = unicodedata.normalize("NFKD", texto.lower())
        return "".join(
            caractere
            for caractere in texto
            if not unicodedata.combining(caractere)
        )

    def detectar_categoria(self, texto: str) -> str:
        texto_normalizado = self._normalizar(texto)
        categorias = []

        grupos = [
            ("animal", self.animal_keywords),
            ("pessoa", self.person_keywords),
            ("veiculo", self.vehicle_keywords),
            ("paisagem", self.landscape_keywords),
            ("objeto", self.object_keywords),
        ]

        for categoria, palavras in grupos:
            if any(
                self._normalizar(palavra) in texto_normalizado
                for palavra in palavras
            ):
                categorias.append(categoria)

        return "+".join(categorias) if categorias else "geral"

    def otimizar(self, prompt: str) -> str:
        prompt = re.sub(r"\s+", " ", prompt.strip())
        if not prompt:
            return ""

        texto = self._normalizar(prompt)
        categoria = self.detectar_categoria(prompt)

        partes = [
            prompt,
            "high quality",
            "realistic",
            "natural proportions",
        ]

        if "animal" in categoria:
            partes.extend([
                "full body animal",
                "entire animal fully visible",
                "complete head and face",
                "correct animal anatomy",
                "natural body proportions",
                "all legs visible when applicable",
                "wide shot, centered composition",
            ])

            if any(termo in texto for termo in [
                "cavalo", "cavalos", "egua", "eguas", "potro", "potros"
            ]):
                partes.extend([
                    "photorealistic equine photography",
                    "full body horse",
                    "all four legs clearly visible",
                    "anatomically correct horse legs and hooves",
                    "natural equine proportions",
                    "standing or moving naturally on four legs",
                    "detailed coat and mane",
                    "wide shot, entire horse inside frame",
                ])

            if "girafa" in texto or "girafas" in texto:
                partes.extend([
                    "full body giraffe",
                    "long neck and four long legs clearly visible",
                    "distinctive giraffe coat pattern",
                    "natural giraffe anatomy",
                    "entire giraffe inside the frame",
                ])

        if "pessoa" in categoria:
            partes.extend([
                "full person",
                "correct human anatomy",
                "natural body proportions",
            ])

        if "veiculo" in categoria:
            partes.extend([
                "complete vehicle",
                "entire vehicle fully visible",
                "full vehicle from front to rear",
                "vehicle completely inside the frame",
                "wide shot",
                "medium distance camera",
                "clear space around the vehicle",
                "no part of the vehicle cropped",
                "side view or three-quarter view",
                "correct vehicle proportions",
            ])

        if "bicicleta" in texto or "bike" in texto or "ciclista" in texto:
            partes.extend([
                "cyclist riding a complete bicycle",
                "entire bicycle visible including both wheels",
                "both wheels clearly separated and correctly formed",
                "cyclist seated naturally on the bicycle",
                "hands on handlebars and feet on pedals",
                "complete cyclist and bicycle inside the frame",
                "dedicated bicycle lane clearly visible when requested",
            ])

        if "paisagem" in categoria:
            partes.extend([
                "detailed environment",
                "natural perspective",
            ])

        if "girafa" in texto or "girafas" in texto:
            partes.extend([
                "savanna landscape when requested",
                "natural wildlife photography composition",
            ])

        if "objeto" in categoria:
            partes.extend([
                "complete object",
                "correct shape",
            ])

        if any(termo in texto for termo in [
            "pista de corrida", "pista corrida", "autodromo", "circuito"
        ]):
            partes.extend([
                "professional racetrack",
                "racing circuit",
                "visible asphalt track",
                "racetrack surroundings visible",
                "wide racing scene",
                "track clearly visible in the composition",
            ])

        if any(termo in texto for termo in ["lacinho", "laço", "laco"]):
            partes.extend([
                "bow clearly visible as a separate accessory",
                "bow does not obscure or deform the main object",
            ])

        if "futurista" in texto:
            partes.append("futuristic")

        if "a noite" in texto:
            partes.append("night scene")

        if "por do sol" in texto:
            partes.append("sunset")

        if "nascer do sol" in texto:
            partes.append("sunrise")

        if "fotografia" in texto or "foto" in texto:
            partes.append("photorealistic")

        if "cinematografico" in texto or "cinematografica" in texto:
            partes.append("cinematic")

        # Remove instruções repetidas sem alterar o texto original do usuário.
        resultado = []
        vistos = set()
        for parte in partes:
            chave = self._normalizar(parte)
            if chave not in vistos:
                resultado.append(parte)
                vistos.add(chave)

        return ", ".join(resultado)

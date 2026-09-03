import re


class PromptOptimizer:

    def __init__(self):

        self.animal_keywords = [
            "cavalo", "cavalos",
            "cachorro", "cão", "cães",
            "gato", "gatos",
            "leão", "leões",
            "tigre", "tigres",
            "onça", "onças",
            "elefante", "elefantes",
            "girafa", "girafas",
            "zebra", "zebras",
            "boi", "bois",
            "vaca", "vacas",
            "touro", "touros",
            "urso", "ursos",
            "lobo", "lobos",
            "macaco", "macacos",
            "pássaro", "pássaros",
            "animal", "animais",
        ]

        self.person_keywords = [
            "homem", "mulher",
            "menino", "menina",
            "criança", "pessoa",
            "pessoas", "jovem",
            "idoso", "idosa",
            "rapaz", "moça",
        ]

        self.vehicle_keywords = [
            "carro", "carros",
            "automóvel", "veículo",
            "moto", "motocicleta",
            "caminhão", "ônibus",
            "bicicleta", "bicicletas",
            "avião", "aviões",
            "helicóptero",
            "barco", "navio",
        ]

        self.landscape_keywords = [
            "paisagem",
            "praia",
            "montanha",
            "floresta",
            "campo",
            "cidade",
            "deserto",
            "lago",
            "rio",
            "cachoeira",
        ]

        self.object_keywords = [
            "mesa", "cadeira",
            "computador", "celular",
            "telefone", "relógio",
            "copo", "garrafa",
            "livro", "câmera",
        ]

    def detectar_categoria(self, texto: str) -> str:

        texto = texto.lower()

        categorias = []

        if any(p in texto for p in self.animal_keywords):
            categorias.append("animal")

        if any(p in texto for p in self.person_keywords):
            categorias.append("pessoa")

        if any(p in texto for p in self.vehicle_keywords):
            categorias.append("veiculo")

        if any(p in texto for p in self.landscape_keywords):
            categorias.append("paisagem")

        if any(p in texto for p in self.object_keywords):
            categorias.append("objeto")

        if not categorias:
            return "geral"

        return "+".join(categorias)

    def otimizar(self, prompt: str) -> str:

        prompt = re.sub(r"\s+", " ", prompt.strip())

        texto = prompt.lower()

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
                "head clearly visible",
                "complete head and face",
                "four legs clearly visible when applicable",
                "correct animal anatomy",
                "natural body proportions",
                "centered composition",
                "wide shot",
                "medium distance camera",
                "clear space around the animal",
                "no cropping",
                "animal completely inside the frame",
            ])

        if "pessoa" in categoria:

            partes.extend([
                "full person",
                "correct anatomy",
            ])

        if "veiculo" in categoria:

            partes.extend([
                "complete vehicle",
                "entire vehicle fully visible",
                "full vehicle from front to rear",
                "vehicle completely inside the frame",
                "wide shot",
                "medium distance camera",
                "distant camera",
                "clear space around the vehicle",
                "no part of the vehicle cropped",
                "side view or three-quarter view",
                "correct vehicle proportions",
            ])

        if "paisagem" in categoria:

            partes.extend([
                "detailed environment",
                "natural perspective",
            ])

        if "objeto" in categoria:

            partes.extend([
                "complete object",
                "correct shape",
            ])

        if any(
            termo in texto
            for termo in [
                "pista de corrida",
                "pista corrida",
                "autódromo",
                "autodromo",
                "circuito",
            ]
        ):

            partes.extend([
                "professional racetrack",
                "racing circuit",
                "visible asphalt track",
                "racetrack surroundings visible",
                "wide racing scene",
                "track clearly visible in the composition",
            ])

        if "futurista" in texto:
            partes.append("futuristic")

        if "à noite" in texto or "a noite" in texto:
            partes.append("night scene")

        if "pôr do sol" in texto:
            partes.append("sunset")

        if "nascer do sol" in texto:
            partes.append("sunrise")

        if "fotografia" in texto or "foto" in texto:
            partes.append("photorealistic")

        if "cinematográfico" in texto or "cinematografica" in texto:
            partes.append("cinematic")

        return ", ".join(partes)
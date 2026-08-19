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

        # Mantém o pedido original e adiciona apenas
        # informações essenciais para o modelo.
        partes = [
            prompt,
            "high quality",
            "realistic",
            "natural proportions",
        ]

        # Animal
        if "animal" in categoria:

            partes.extend([
                "full body",
                "complete head",
                "correct anatomy",
            ])

        # Pessoa
        if "pessoa" in categoria:

            partes.extend([
                "full person",
                "correct anatomy",
            ])

        # Veículo
        if "veiculo" in categoria:

            partes.extend([
                "complete vehicle",
                "correct proportions",
            ])

        # Paisagem
        if "paisagem" in categoria:

            partes.extend([
                "detailed environment",
                "natural perspective",
            ])

        # Objeto
        if "objeto" in categoria:

            partes.extend([
                "complete object",
                "correct shape",
            ])

        # Reforços específicos de contexto
        if "futurista" in texto or "futurista" in texto:
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

        # Limita a quantidade de reforços.
        # O prompt original continua sendo prioridade.
        prompt_final = ", ".join(partes)

        return prompt_final
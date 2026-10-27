import re
import unicodedata


class PromptOptimizer:
    def __init__(self):
        self.animal_keywords = [
            "cavalo", "cavalos", "?gua", "?guas", "potro", "potros",
            "cachorro", "c?o", "c?es", "gato", "gatos", "le?o", "le?es",
            "tigre", "tigres", "on?a", "on?as", "elefante", "elefantes",
            "girafa", "girafas", "zebra", "zebras", "boi", "bois",
            "vaca", "vacas", "touro", "touros", "urso", "ursos",
            "lobo", "lobos", "macaco", "macacos", "p?ssaro", "p?ssaros",
            "animal", "animais",
        ]
        self.person_keywords = [
            "homem", "mulher", "menino", "menina", "crian?a",
            "pessoa", "pessoas", "jovem", "idoso", "idosa",
            "rapaz", "mo?a", "ciclista",
        ]
        self.vehicle_keywords = [
            "carro", "carros", "autom?vel", "ve?culo", "suv",
            "moto", "motocicleta", "caminh?o", "?nibus", "bicicleta",
            "bicicletas", "bike", "biciclista", "avi?o", "avi?es",
            "helic?ptero", "barco", "navio",
        ]
        self.landscape_keywords = [
            "paisagem", "praia", "montanha", "floresta", "campo",
            "cidade", "deserto", "lago", "rio", "cachoeira", "savana",
        ]
        self.object_keywords = [
            "mesa", "cadeira", "computador", "celular", "telefone",
            "rel?gio", "copo", "garrafa", "livro", "c?mera",
            "la?o", "lacinho", "gravata", "brinco",
        ]

    @staticmethod
    def _normalizar(texto: str) -> str:
        texto = unicodedata.normalize("NFKD", texto.lower())
        return "".join(
            c for c in texto if not unicodedata.combining(c)
        )

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
        return "+".join(categorias) if categorias else "geral"

    def otimizar(self, prompt: str) -> str:
        prompt = re.sub(r"\s+", " ", prompt.strip())
        if not prompt:
            return ""

        texto = self._normalizar(prompt)
        categoria = self.detectar_categoria(prompt)

        # Mant?m o pedido original e acrescenta apenas poucas instru??es.
        extras = []
        if "animal" in categoria:
            extras.extend(["realistic animal anatomy", "full body"])
        if any(x in texto for x in ["cavalo", "cavalos", "egua", "eguas", "potro", "potros"]):
            extras.append("four visible legs and natural hooves")
        if "girafa" in texto or "girafas" in texto:
            extras.append("long neck and four visible legs")
            if "savana" in texto:
                extras.append("savanna landscape")
        if "pessoa" in categoria:
            extras.append("natural human anatomy")
        if "veiculo" in categoria:
            extras.append("complete vehicle visible")
        if any(x in texto for x in ["bicicleta", "bicicletas", "bike", "ciclista", "biciclista"]):
            extras.append("complete bicycle with both wheels visible")
        if "paisagem" in categoria:
            extras.append("natural perspective")
        if any(x in texto for x in ["lacinho", "laco"]):
            extras.append("clearly visible separate bow accessory")
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

        # Remove complementos duplicados sem apagar a descri??o original.
        resultado = [prompt]
        vistos = {self._normalizar(prompt)}
        for extra in extras:
            chave = self._normalizar(extra)
            if chave not in vistos:
                resultado.append(extra)
                vistos.add(chave)

        # Limite conservador de palavras para reduzir risco de truncamento.
        palavras = " ".join(resultado).split()
        if len(palavras) > 45:
            palavras_originais = prompt.split()
            restantes = max(0, 45 - len(palavras_originais))
            return " ".join(palavras_originais + " ".join(resultado[1:]).split()[:restantes])

        return ", ".join(resultado)

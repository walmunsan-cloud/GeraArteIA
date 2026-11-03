"""Otimização de prompts em português e inglês para o GeraArteIA."""

import re
import unicodedata


class PromptOptimizer:
    """Melhora a descrição do usuário sem substituir o assunto solicitado."""

    @staticmethod
    def _normalizar(texto: str) -> str:
        """Remove acentos, normaliza espaços e converte o texto para minúsculas."""
        texto = unicodedata.normalize("NFD", texto.lower())
        texto = "".join(
            caractere
            for caractere in texto
            if unicodedata.category(caractere) != "Mn"
        )
        return re.sub(r"\s+", " ", texto).strip()

    @staticmethod
    def _contem(texto: str, termos) -> bool:
        """Verifica palavras e expressões sem confundir termos curtos com palavras maiores."""
        for termo in termos:
            termo = re.escape(termo)
            if re.search(r"(?<!\w)" + termo + r"(?!\w)", texto):
                return True
        return False

    @classmethod
    def detectar_categoria(cls, prompt: str) -> str:
        """Identifica a categoria principal descrita no prompt."""
        texto = cls._normalizar(prompt or "")

        if cls._contem(texto, (
            "tatuagem", "tattoo", "tattoo design"
        )):
            return "tatuagem"

        if cls._contem(texto, (
            "ciclista", "cyclist", "bicicleta", "bicycle",
            "bike", "ciclovia", "bike lane", "cycling"
        )):
            return "pessoa e bicicleta"

        if cls._contem(texto, (
            "suv", "carro", "automovel", "veiculo", "caminhao",
            "car", "vehicle", "automobile", "truck", "van",
            "pickup", "motorcycle", "motorbike"
        )):
            return "veiculo"

        if cls._contem(texto, (
            "girafa", "giraffe", "cavalo", "horse", "egua", "mare",
            "potro", "potra", "foal", "equino", "equine",
            "onca", "jaguar", "leao", "lion", "tigre", "tiger",
            "cachorro", "cao", "dog", "gato", "cat",
            "elefante", "elephant", "passaro", "bird",
            "animal", "animais", "animals", "wildlife"
        )):
            return "animal"

        if cls._contem(texto, (
            "pessoa", "homem", "mulher", "rosto", "retrato",
            "person", "people", "man", "woman", "portrait",
            "human", "face"
        )):
            return "pessoa"

        return "geral"

    @classmethod
    def otimizar(cls, prompt: str) -> str:
        """Acrescenta orientações visuais coerentes com o assunto do prompt."""
        if not isinstance(prompt, str) or not prompt.strip():
            return ""

        original = prompt.strip()
        texto = cls._normalizar(original)

        # Tatuagem: preservar a ideia original e reforçar legibilidade e desenho.
        if cls._contem(texto, ("tatuagem", "tattoo")):
            if cls._contem(texto, ("onca", "jaguar")):
                complemento = (
                    "professional jaguar tattoo design, clear silhouette, "
                    "recognizable jaguar anatomy, detailed natural rosettes, "
                    "clean linework, balanced composition, tattoo-ready artwork"
                )
            else:
                complemento = (
                    "professional tattoo design, clean linework, clear outlines, "
                    "balanced composition, readable silhouette, tattoo-ready artwork"
                )

        # Girafa: evitar pescoço curto e partes do corpo fora da imagem.
        elif cls._contem(texto, ("girafa", "giraffe")):
            complemento = (
                "complete giraffe visible from head to hooves, long natural neck, "
                "anatomically correct giraffe, four visible legs, natural proportions, "
                "African savanna landscape, realistic wildlife photography, "
                "entire animal inside the frame"
            )

        # Cavalos e equinos.
        elif cls._contem(texto, (
            "cavalo", "horse", "egua", "mare", "potro", "potra",
            "foal", "equino", "equine"
        )):
            complemento = (
                "complete horse visible from head to hooves, anatomically plausible "
                "equine proportions, four legs, four visible hooves, natural mane "
                "and tail, realistic horse posture, entire horse inside the frame, "
                "realistic animal photography"
            )

        # Onça-pintada ou jaguar.
        elif cls._contem(texto, ("onca", "jaguar")):
            complemento = (
                "anatomically accurate jaguar, complete visible body, powerful "
                "natural feline proportions, golden coat with realistic black rosettes, "
                "four visible legs, natural wildlife setting, realistic wildlife photography"
            )

        # Leões.
        elif cls._contem(texto, ("leao", "lion")):
            complemento = (
                "anatomically accurate lion, natural feline proportions, complete body "
                "visible, four legs, realistic fur and mane when appropriate, "
                "natural wildlife setting, realistic wildlife photography"
            )

        # Tigres.
        elif cls._contem(texto, ("tigre", "tiger")):
            complemento = (
                "anatomically accurate tiger, complete body visible, four legs, "
                "natural orange coat with distinct black stripes, realistic fur, "
                "natural wildlife setting, realistic wildlife photography"
            )

        # Elefantes.
        elif cls._contem(texto, ("elefante", "elephant")):
            complemento = (
                "anatomically accurate elephant, complete body visible, four legs, "
                "natural trunk and ears, realistic skin texture, natural proportions, "
                "wildlife photography, entire animal inside the frame"
            )

        # Cães.
        elif cls._contem(texto, ("cachorro", "cao", "dog")):
            complemento = (
                "anatomically plausible dog, natural canine proportions, four legs, "
                "clearly visible paws, realistic fur texture, natural posture, "
                "complete dog visible inside the frame"
            )

        # Gatos.
        elif cls._contem(texto, ("gato", "cat")):
            complemento = (
                "anatomically plausible cat, natural feline proportions, four legs, "
                "realistic fur and whiskers, natural posture, complete cat visible "
                "inside the frame"
            )

        # Pássaros.
        elif cls._contem(texto, ("passaro", "bird")):
            complemento = (
                "anatomically plausible bird, natural feather structure, correctly "
                "formed wings and beak, realistic proportions, clear subject, "
                "natural wildlife photography"
            )

        # Veículos: manter o modelo e as cores solicitadas.
        elif cls._contem(texto, (
            "suv", "carro", "automovel", "veiculo", "caminhao",
            "car", "vehicle", "automobile", "truck", "van",
            "pickup", "motorcycle", "motorbike"
        )):
            complemento = (
                "complete vehicle visible, realistic automotive proportions, "
                "coherent perspective, correctly formed wheels, detailed bodywork, "
                "realistic materials and reflections, entire vehicle inside the frame"
            )

            cor_rosa = cls._contem(texto, ("rosa", "pink"))
            tem_laco = cls._contem(texto, ("laco", "bow", "ribbon"))

            if cor_rosa:
                complemento += (
                    ", preserve the requested pink color, clearly pink vehicle paint"
                )

            if tem_laco:
                complemento += (
                    ", clearly visible decorative bow on the vehicle, realistic ribbon, "
                    "bow accessory distinct from the vehicle body"
                )

        # Ciclistas e bicicletas.
        elif cls._contem(texto, (
            "ciclista", "cyclist", "bicicleta", "bicycle",
            "bike", "ciclovia", "bike lane", "cycling"
        )):
            complemento = (
                "realistic bicycle with two visible wheels and coherent frame geometry, "
                "complete bicycle inside the frame, natural riding posture when a rider "
                "is present, anatomically plausible cyclist, hands correctly positioned "
                "on handlebars, clearly defined bike lane when requested, realistic "
                "street perspective"
            )

        # Pessoas, retratos e figuras humanas.
        elif cls._contem(texto, (
            "pessoa", "homem", "mulher", "rosto", "retrato",
            "person", "people", "man", "woman", "portrait",
            "human", "face"
        )):
            complemento = (
                "anatomically plausible human figure, natural body proportions, "
                "realistic facial features, natural pose, coherent lighting, "
                "well-composed image"
            )

        # Outros animais.
        elif cls._contem(texto, (
            "animal", "animais", "animals", "wildlife"
        )):
            complemento = (
                "anatomically plausible animal, natural proportions, clearly visible "
                "limbs, realistic surface details, natural posture, complete subject "
                "inside the frame"
            )

        # Prompt geral.
        else:
            complemento = (
                "well-composed image, clear main subject, coherent lighting, "
                "consistent perspective, detailed textures, natural proportions, "
                "high visual quality"
            )

        # Evitar acrescentar novamente um complemento já presente.
        complemento_normalizado = cls._normalizar(complemento)

        if complemento_normalizado in texto:
            return original

        return f"{original}, {complemento}"

    @staticmethod
    def prompt_negativo() -> str:
        """Retorna termos negativos para reduzir erros visuais comuns."""
        return (
            "low quality, blurry, distorted anatomy, deformed body, "
            "extra limbs, missing limbs, extra legs, missing legs, "
            "extra fingers, malformed hands, duplicate objects, "
            "cropped subject, out of frame, incorrect proportions, "
            "unrealistic perspective, malformed wheels, broken bicycle frame, "
            "distorted animal anatomy, text, watermark, logo"
        )
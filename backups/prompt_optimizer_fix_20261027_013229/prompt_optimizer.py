import re
import unicodedata


class PromptOptimizer:
    """Melhora prompts em português ou inglês sem substituir a ideia original."""

    EXTRAS = {
        "girafa": (
            "complete giraffe visible from head to hooves, "
            "natural giraffe anatomy, African savanna, coherent perspective"
        ),
        "onça": (
            "anatomically accurate jaguar, complete visible body, "
            "natural golden coat with realistic black rosette spots"
        ),
        "onca": (
            "anatomically accurate jaguar, complete visible body, "
            "natural golden coat with realistic black rosette spots"
        ),
        "cavalo": (
            "anatomically correct horse, four visible legs, "
            "natural equine proportions, complete body"
        ),
        "ciclista": (
            "cyclist riding a complete bicycle, both wheels visible, "
            "correct bicycle geometry, natural riding posture, urban bike lane"
        ),
        "bicicleta": (
            "accurate bicycle geometry, two complete wheels, "
            "correct frame, handlebars and pedals"
        ),
        "carro": (
            "complete vehicle, realistic proportions, four wheels, "
            "coherent reflections and perspective"
        ),
        "suv": (
            "complete SUV, realistic automotive proportions, "
            "four wheels, coherent paint and reflections"
        ),
        "tatuagem": (
            "tattoo-ready composition, crisp outlines, coherent design, "
            "balanced spacing, detailed and clean linework"
        ),
    }

    QUALIDADE = (
        "well-composed image, clear subject, coherent lighting, "
        "consistent perspective, detailed textures, high visual quality"
    )

    NEGATIVE = (
        "deformed anatomy, extra limbs, missing limbs, extra legs, "
        "missing legs, duplicate objects, malformed hands, distorted face, "
        "cropped subject, cut off feet, cut off head, broken geometry, "
        "floating objects, inconsistent perspective, blurry, low quality, "
        "text artifacts, watermark"
    )

    @staticmethod
    def _normalizar(texto: str) -> str:
        texto = unicodedata.normalize("NFD", texto.lower())
        return "".join(
            caractere
            for caractere in texto
            if unicodedata.category(caractere) != "Mn"
        )

    @classmethod
    def otimizar(cls, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Informe uma descrição para gerar a imagem.")

        original = re.sub(r"\s+", " ", prompt).strip()
        normalizado = cls._normalizar(original)

        complementos = []
        for palavra, complemento in cls.EXTRAS.items():
            if re.search(r"\b" + re.escape(palavra) + r"\b", normalizado):
                if complemento not in complementos:
                    complementos.append(complemento)

        partes = [original]
        partes.extend(complementos)
        partes.append(cls.QUALIDADE)

        return ", ".join(partes)

    @classmethod
    def prompt_negativo(cls) -> str:
        return cls.NEGATIVE


def otimizar_prompt(prompt: str) -> str:
    """Interface funcional para os módulos que preferem uma função."""
    return PromptOptimizer.otimizar(prompt)


def obter_prompt_negativo() -> str:
    return PromptOptimizer.prompt_negativo()

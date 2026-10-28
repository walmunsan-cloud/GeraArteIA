import re
import unicodedata


class PromptOptimizer:
    """Melhora prompts em português para orientar a geração de imagens."""

    @staticmethod
    def _normalizar(texto: str) -> str:
        texto = unicodedata.normalize("NFD", texto.lower())
        texto = "".join(
            caractere for caractere in texto
            if unicodedata.category(caractere) != "Mn"
        )
        return re.sub(r"\s+", " ", texto).strip()

    @classmethod
    def detectar_categoria(cls, prompt: str) -> str:
        """Identifica a categoria principal descrita no prompt."""
        texto = cls._normalizar(prompt or "")

        if any(p in texto for p in ("tatuagem", "tattoo")):
            return "tatuagem"
        if any(p in texto for p in (
            "ciclista", "bicicleta", "bike", "ciclovia"
        )):
            return "pessoa e bicicleta"
        if any(p in texto for p in (
            "suv", "carro", "automovel", "veiculo", "caminhao"
        )):
            return "veículo"
        if any(p in texto for p in (
            "girafa", "cavalo", "onca", "jaguar", "leao", "tigre",
            "cachorro", "cao", "gato", "elefante", "animal", "passaro"
        )):
            return "animal"
        if any(p in texto for p in (
            "pessoa", "homem", "mulher", "rosto", "retrato"
        )):
            return "pessoa"
        return "geral"

    @classmethod
    def otimizar(cls, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            return ""

        original = prompt.strip()
        texto = cls._normalizar(original)
        categoria = cls.detectar_categoria(original)

        if "tatuagem" in texto or "tattoo" in texto:
            if any(p in texto for p in ("onca", "jaguar")):
                complemento = (
                    "tattoo design, jaguar tattoo, clean tattoo linework, "
                    "clear silhouette, detailed spots, professional tattoo art"
                )
            else:
                complemento = (
                    "tattoo design, clean linework, clear outlines, "
                    "balanced composition, professional tattoo artwork"
                )

        elif "girafa" in texto:
            complemento = (
                "long natural giraffe neck, complete giraffe visible from "
                "head to hooves, anatomically correct giraffe, four legs, "
                "savanna landscape, African savanna, natural wildlife photography"
            )

        elif "cavalo" in texto:
            complemento = (
                "full body animal, complete head and face, "
                "anatomically plausible horse with four legs, "
                "anatomically correct horse, four visible legs, "
                "realistic galloping horse, natural equine proportions, complete body"
            )

        elif any(p in texto for p in ("suv", "carro", "automovel", "veiculo")):
            complemento = (
                "complete vehicle visible, realistic automotive proportions, "
                "four wheels, coherent paint and reflections, detailed vehicle"
            )
            if "rosa" in texto and any(p in texto for p in ("laco", "laço")):
                complemento += (
                    ", pink SUV, clearly visible bow accessory, vehicle paint is pink, pink bow clearly visible on the vehicle, "
                    "realistic bow, preserve requested pink color"
                )

        elif any(p in texto for p in ("ciclista", "bicicleta", "bike", "ciclovia")):
            complemento = (
                "cyclist riding a bicycle on a clearly visible bike lane, "
                "realistic bicycle frame, both wheels visible, two wheels, natural riding posture, anatomically correct "
                "rider, hands holding handlebars, complete bicycle visible"
            )

        elif any(p in texto for p in ("onca", "jaguar")):
            complemento = (
                "anatomically accurate jaguar, complete visible body, "
                "natural golden coat with realistic black rosettes, "
                "realistic wildlife photography"
            )

        elif categoria == "animal":
            complemento = (
                "full body animal, anatomically correct body, natural "
                "proportions, clearly visible limbs, realistic details"
            )

        else:
            complemento = (
                "well-composed image, clear subject, coherent lighting, "
                "consistent perspective, detailed textures, high visual quality"
            )

        if complemento.lower() in texto:
            return original

        return f"{original}, {complemento}"

    @classmethod
    def prompt_negativo(cls) -> str:
        return (
            "low quality, blurry, distorted anatomy, deformed body, "
            "extra limbs, missing limbs, extra legs, missing legs, "
            "extra fingers, malformed hands, duplicate objects, "
            "cropped subject, out of frame, incorrect proportions, "
            "unrealistic perspective, text, watermark"
        )

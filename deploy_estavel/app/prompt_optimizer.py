"""Otimizador universal de prompts do GeraArteIA."""

import re
import unicodedata


class PromptOptimizer:

    @staticmethod
    def _normalizar(texto):
        texto = unicodedata.normalize("NFD", (texto or "").lower())
        texto = "".join(
            c for c in texto
            if unicodedata.category(c) != "Mn"
        )
        return re.sub(r"\s+", " ", texto).strip()

    @classmethod
    def detectar_categoria(cls, prompt):
        texto = cls._normalizar(prompt)

        grupos = {
            "tatuagem": ("tattoo", "tatuagem"),
            "bicicleta": ("bicycle", "bike", "bicicleta", "cyclist", "ciclista"),
            "veiculo": ("car", "vehicle", "motorcycle", "motorbike",
                        "carro", "veiculo", "motocicleta", "caminhao"),
            "animal": ("dog", "cat", "animal", "giraffe", "horse",
                       "jaguar", "lion", "tiger", "elephant", "bird",
                       "cachorro", "gato", "girafa", "cavalo", "onca",
                       "leao", "tigre", "elefante", "passaro"),
            "pessoa": ("person", "people", "man", "woman", "human",
                       "portrait", "homem", "mulher", "pessoa", "retrato"),
        }

        for categoria, termos in grupos.items():
            if any(re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", texto)
                   for t in termos):
                return categoria

        return "geral"

    @classmethod
    def otimizar(cls, prompt):
        if not isinstance(prompt, str) or not prompt.strip():
            return ""

        original = re.sub(r"\s+", " ", prompt).strip()
        categoria = cls.detectar_categoria(original)

        complementos = {
            "tatuagem": "professional tattoo artwork, clean linework, clear design",
            "bicicleta": "realistic bicycle geometry, two wheels, natural riding posture",
            "veiculo": "realistic vehicle proportions, coherent perspective, detailed materials",
            "animal": "natural anatomy, realistic proportions, detailed natural textures",
            "pessoa": "natural human anatomy, realistic proportions, natural pose",
            "geral": "clear subject, coherent composition, realistic lighting, detailed textures",
        }

        return f"{original}, {complementos[categoria]}"

    @staticmethod
    def prompt_negativo():
        return (
            "blurry, low quality, deformed anatomy, extra limbs, "
            "missing limbs, malformed hands, malformed feet, "
            "distorted face, duplicate objects, fused objects, "
            "broken geometry, incorrect proportions, cropped subject, "
            "text, watermark, logo"
        )

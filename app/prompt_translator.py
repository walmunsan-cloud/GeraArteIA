"""Traducao automatica de prompts do portugues para o ingles."""

import re
import threading

import torch
from transformers import MarianMTModel, MarianTokenizer


MODEL_ID = "Helsinki-NLP/opus-mt-ROMANCE-en"


class PromptTranslator:
    _model = None
    _tokenizer = None
    _lock = threading.Lock()

    @staticmethod
    def corrigir_termos(original: str, traducao: str) -> str:
        """Corrige termos visuais conhecidos usando o texto original."""

        resultado = traducao.strip()
        origem = original.casefold()

        # Onca-pintada: o tradutor pode interpretar incorretamente a palavra.
        if re.search(r"\bonça[- ]pintada\b", origem):
            resultado = re.sub(
                r"\bpaint[- ]?once\b",
                "jaguar",
                resultado,
                flags=re.IGNORECASE,
            )
            if not re.search(r"\bjaguar\b", resultado, re.IGNORECASE):
                resultado = resultado.rstrip(" .") + ", jaguar"

        # Laco: evita a traducao incorreta como "loop".
        if re.search(r"\blaço\b", origem):
            resultado = re.sub(
                r"\bloop\b",
                "bow",
                resultado,
                flags=re.IGNORECASE,
            )
            if not re.search(r"\bbow\b", resultado, re.IGNORECASE):
                resultado = resultado.rstrip(" .") + ", bow"

        # Termos de apoio visual.
        correcoes = [
            (r"\bsavana africana\b", r"\bAfrican savannah?\b", "African savannah"),
            (r"\bgirafa\b", r"\bgiraffe\b", "giraffe"),
            (r"\bciclista\b", r"\bcyclist\b", "cyclist"),
            (r"\bbicicleta\b", r"\bbicycle\b", "bicycle"),
            (r"\btatuagem\b", r"\btattoo\b", "tattoo"),
        ]

        for termo_pt, padrao_en, termo_en in correcoes:
            if re.search(termo_pt, origem, re.IGNORECASE):
                if not re.search(padrao_en, resultado, re.IGNORECASE):
                    resultado = resultado.rstrip(" .") + ", " + termo_en

        return resultado.strip(" ,")

    @classmethod
    def traduzir(cls, texto: str) -> str:
        if not isinstance(texto, str) or not texto.strip():
            return ""

        original = texto.strip()

        with cls._lock:
            if cls._tokenizer is None or cls._model is None:
                cls._tokenizer = MarianTokenizer.from_pretrained(MODEL_ID)
                cls._model = MarianMTModel.from_pretrained(MODEL_ID)
                cls._model.to("cpu")
                cls._model.eval()

            texto_entrada = ">>pt<< " + original

            entradas = cls._tokenizer(
                [texto_entrada],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )

            with torch.inference_mode():
                resultado = cls._model.generate(
                    **entradas,
                    max_new_tokens=512,
                    num_beams=4,
                )

            traducao = cls._tokenizer.decode(
                resultado[0],
                skip_special_tokens=True,
            ).strip()

        if not traducao:
            return original

        return cls.corrigir_termos(original, traducao)



"""Traducao automatica de prompts do portugues para o ingles."""

import threading

import torch
from transformers import MarianMTModel, MarianTokenizer


MODEL_ID = "Helsinki-NLP/opus-mt-ROMANCE-en"


class PromptTranslator:
    _model = None
    _tokenizer = None
    _lock = threading.Lock()

    @classmethod
    def traduzir(cls, texto: str) -> str:
        if not isinstance(texto, str) or not texto.strip():
            return ""

        original = texto.strip()

        # Evita carregar o tradutor quando o texto ja estiver em ingles.
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

        return traducao or original


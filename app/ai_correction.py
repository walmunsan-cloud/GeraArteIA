"""
Modulo de analise assistida para autocorrecao do GeraArteIA.

Este modulo:
- Analisa prompts e avaliacoes negativas.
- Prepara propostas de correcao.
- Nao gera imagens.
- Nao modifica o banco de dados.
- Exige aprovacao humana antes da regeneracao.
"""

import json
import os
from typing import Optional


class AICorrectionError(Exception):
    """Erro controlado na analise de autocorrecao."""


class AICorrection:
    """Analise de imagens e prompts usando a API da OpenAI."""

    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = (
            model
            or os.getenv("OPENAI_MODEL", "").strip()
            or "gpt-4.1-mini"
        )

    def available(self) -> bool:
        """Informa se a integracao possui uma chave configurada."""
        return bool(self.api_key)

    def analyze(
        self,
        prompt: str,
        rating: int,
        satisfaction_pct: Optional[int] = None,
        feedback: str = "",
        image_data_url: Optional[str] = None,
        shared_memory: Optional[list] = None,
        individual_memory: Optional[list] = None,
    ) -> dict:
        """
        Analisa uma geracao e devolve uma proposta de correcao.

        A imagem e opcional. Quando fornecida, deve ser uma data URL
        valida e a analise visual sera solicitada ao modelo.
        """

        if not self.available():
            raise AICorrectionError(
                "Integracao com a IA nao configurada. "
                "Configure OPENAI_API_KEY no ambiente."
            )

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("O prompt original e obrigatorio.")

        if isinstance(rating, bool) or not isinstance(rating, int):
            raise ValueError("A avaliacao deve ser um numero inteiro.")

        if not 0 <= rating <= 10:
            raise ValueError("A avaliacao deve estar entre 0 e 10.")

        if satisfaction_pct is not None:
            if satisfaction_pct not in (20, 40, 60, 80, 100):
                raise ValueError("Percentual de satisfacao invalido.")

        if image_data_url is not None:
            if not isinstance(image_data_url, str):
                raise ValueError("A imagem fornecida e invalida.")
            if not image_data_url.startswith("data:image/"):
                raise ValueError("A imagem deve ser uma data URL.")

        feedback = str(feedback or "").strip()[:2000]

        instructions = """
Voce e um especialista em engenharia de prompts para geracao de imagens
com Stable Diffusion 1.5.

Analise o prompt original e o feedback do usuario.
Identifique problemas concretos de composicao, anatomia, proporcao,
objetos, cores, perspectiva, enquadramento ou fidelidade ao pedido.

Proponha uma correcao que preserve a ideia original do usuario.
Nao invente elementos que nao foram solicitados.
Nao afirme que uma imagem foi analisada visualmente quando ela nao
foi fornecida.

Responda exclusivamente em JSON com os campos:
problemas_identificados: lista de textos;
causa_provavel: texto;
prompt_corrigido: texto;
prompt_negativo_adicional: texto;
justificativa: texto;
alteracoes_propostas: lista de textos.

A proposta sera apresentada ao usuario para aprovacao.
Nao considere a correcao aprovada automaticamente.
"""

        user_content = [
            {
                "type": "input_text",
                "text": (
                    "PROMPT ORIGINAL:\n"
                    + prompt.strip()
                    + "\n\nNOTA: "
                    + str(rating)
                    + "/10"
                    + "\nSATISFACAO: "
                    + str(satisfaction_pct)
                    + "%"
                    + "\nFEEDBACK:\n"
                    + feedback
                    + "\n\nMEMORIA TECNICA COMPARTILHADA (anonimizada):\n"
                    + json.dumps(
                        [
                            {
                                key: item.get(key)
                                for key in (
                                    "category", "error_pattern",
                                    "correction_pattern", "confidence",
                                    "positive_count"
                                )
                                if key in item
                            }
                            for item in (shared_memory or [])[:10]
                            if isinstance(item, dict)
                        ],
                        ensure_ascii=False,
                    )
                    + "\n\nMEMORIA INDIVIDUAL DO USUARIO: \n"
                    + json.dumps(
                        [
                            {
                                key: item.get(key)
                                for key in (
                                    "category", "preference",
                                    "correction_pattern", "positive_count"
                                )
                                if key in item
                            }
                            for item in (individual_memory or [])[:10]
                            if isinstance(item, dict)
                        ],
                        ensure_ascii=False,
                    )
                ),
            }
        ]

        if image_data_url:
            user_content.append({
                "type": "input_image",
                "image_url": image_data_url,
            })

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            response = client.responses.create(
                model=self.model,
                instructions=instructions,
                input=[
                    {
                        "role": "user",
                        "content": user_content,
                    }
                ],
            )

            result_text = response.output_text

            if not result_text:
                raise AICorrectionError(
                    "A IA nao retornou uma proposta de correcao."
                )

            result = json.loads(result_text)

            required_fields = {
                "problemas_identificados",
                "causa_provavel",
                "prompt_corrigido",
                "prompt_negativo_adicional",
                "justificativa",
                "alteracoes_propostas",
            }

            if not required_fields.issubset(result):
                raise AICorrectionError(
                    "A resposta da IA esta incompleta."
                )

            if not isinstance(result["prompt_corrigido"], str):
                raise AICorrectionError(
                    "O prompt corrigido retornado e invalido."
                )

            if not result["prompt_corrigido"].strip():
                raise AICorrectionError(
                    "A IA retornou um prompt corrigido vazio."
                )

            return result

        except AICorrectionError:
            raise
        except Exception as exc:
            raise AICorrectionError(
                "Nao foi possivel concluir a analise de autocorrecao: "
                + type(exc).__name__
            ) from exc

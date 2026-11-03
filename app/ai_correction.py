"""
Modulo de analise assistida para autocorrecao do GeraArteIA.

Funciona com regras locais, sem exigir API externa.
A analise e textual: nao afirma ter examinado visualmente a imagem.
A proposta depende de aprovacao humana antes da regeneracao.
"""

import json
import os
from typing import Optional


class AICorrectionError(Exception):
    """Erro controlado na analise de autocorrecao."""


class AICorrection:
    """Analise assistida por API externa ou regras locais."""

    def __init__(self, model: Optional[str] = None):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = (
            model
            or os.getenv("OPENAI_MODEL", "").strip()
            or "gpt-4.1-mini"
        )

    def available(self) -> bool:
        """Informa se existe chave para usar a API externa."""
        return bool(self.api_key)

    def _analyze_locally(
        self,
        prompt: str,
        rating: int,
        satisfaction_pct: Optional[int] = None,
        feedback: str = "",
        shared_memory: Optional[list] = None,
        individual_memory: Optional[list] = None,
    ) -> dict:
        """Gera uma proposta de melhoria usando regras locais."""

        original = prompt.strip()
        text = (original + " " + str(feedback or "")).lower()

        problems = []
        changes = []
        additions = []

        rules = [
            (
                ("cortad", "cropped", "enquadramento", "fora do quadro"),
                "Possivel problema de enquadramento ou corte.",
                "Manter o objeto principal inteiro dentro do quadro, com margem ao redor."
            ),
            (
                ("pata", "perna", "braco", "braço", "mao", "mão",
                 "dedo", "anatom", "membro"),
                "Possivel inconsistencia anatomica ou na quantidade de membros.",
                "Anatomia natural, proporcoes corretas e quantidade exata de membros e dedos."
            ),
            (
                ("cor", "color", "rosa", "vermelh", "azul", "verde",
                 "amarelo", "preto", "branco"),
                "A fidelidade das cores precisa ser reforcada.",
                "Respeitar rigorosamente as cores especificadas no pedido original."
            ),
            (
                ("fundo", "cenario", "paisagem", "background", "ambiente"),
                "O cenario pode precisar de melhor composicao.",
                "Separar claramente o objeto principal do fundo, mantendo o ambiente solicitado."
            ),
            (
                ("texto", "letra", "palavra", "logo", "marca"),
                "Textos e logotipos podem apresentar deformacoes.",
                "Evitar textos, letras e logotipos nao solicitados."
            ),
            (
                ("rosto", "olho", "face", "pessoa", "humano"),
                "Elementos humanos podem precisar de maior consistencia.",
                "Rosto natural, olhos alinhados e proporcoes humanas coerentes."
            ),
            (
                ("carro", "veiculo", "veículo", "automovel", "automóvel",
                 "suv", "caminhonete"),
                "O veiculo pode precisar de melhor definicao estrutural.",
                "Veiculo completo, rodas proporcionais, perspectiva coerente e carroceria sem deformacoes."
            ),
            (
                ("animal", "cachorro", "cao", "cão", "gato", "onca",
                 "onça", "girafa", "jaguar", "cavalo"),
                "A representacao do animal pode precisar de maior consistencia.",
                "Animal com anatomia natural, proporcoes coerentes e quantidade correta de patas."
            ),
            (
                ("bicicleta", "bike", "ciclista", "ciclovia"),
                "A estrutura da bicicleta e a posicao do ciclista podem precisar de reforco.",
                "Bicicleta com duas rodas alinhadas, quadro completo e ciclista em postura natural."
            ),
            (
                ("nitidez", "borrad", "desfoc", "qualidade", "detalhe"),
                "A nitidez e a definicao dos detalhes podem ser aprimoradas.",
                "Detalhes nitidos, foco definido e acabamento visual de alta qualidade."
            ),
            (
                ("luz", "iluminacao", "iluminação", "sombra", "escuro"),
                "A iluminacao pode precisar de maior equilibrio.",
                "Iluminacao equilibrada, sombras naturais e boa visibilidade do objeto principal."
            ),
        ]

        for keywords, problem, improvement in rules:
            if any(word in text for word in keywords):
                problems.append(problem)
                changes.append(improvement)
                additions.append(improvement)

        if rating <= 3:
            problems.append("A nota indica insatisfacao elevada com o resultado.")
            additions.append(
                "Priorizar fidelidade ao pedido original, composicao clara e proporcoes corretas."
            )
        elif rating <= 6:
            problems.append("O resultado atende parcialmente a expectativa.")
            additions.append(
                "Aprimorar os detalhes e a fidelidade dos elementos solicitados."
            )

        if feedback.strip():
            problems.append("O feedback informado pelo usuario foi considerado.")
            changes.append(
                "Considerar as observacoes do usuario sem alterar a ideia principal."
            )

        if not problems:
            problems.append(
                "A nota e o feedback indicam necessidade de aprimorar a fidelidade ao pedido."
            )
            changes.append(
                "Reforcar o objeto principal, a composicao, as proporcoes e os detalhes descritos."
            )
            additions.append(
                "Composicao clara, objeto principal completo, proporcoes coerentes e detalhes bem definidos."
            )

        # Considera memorias tecnicas sem inventar preferencias.
        memory_notes = []
        for collection in (shared_memory or [], individual_memory or []):
            for item in collection[:10]:
                if not isinstance(item, dict):
                    continue
                correction = item.get("correction_pattern")
                if correction and isinstance(correction, str):
                    memory_notes.append(correction.strip())

        for note in memory_notes[:3]:
            if note and note.lower() not in original.lower():
                additions.append(note)

        unique_additions = list(dict.fromkeys(additions))
        corrected = original.rstrip(" .")

        if unique_additions:
            corrected += ". " + " ".join(unique_additions)

        corrected += (
            ". Alta qualidade, detalhes nitidos, "
            "iluminacao coerente e composicao equilibrada."
        )

        negative = (
            "low quality, blurry, out of focus, distorted anatomy, "
            "deformed, extra limbs, missing limbs, extra fingers, "
            "bad hands, duplicate objects, cropped, watermark, "
            "unwanted text, unwanted logo"
        )

        return {
            "problemas_identificados": list(dict.fromkeys(problems)),
            "causa_provavel": (
                "Analise textual realizada por regras locais, considerando "
                "o prompt, a avaliacao e o feedback. A imagem nao foi "
                "analisada visualmente por um modelo de IA."
            ),
            "prompt_corrigido": corrected,
            "prompt_negativo_adicional": negative,
            "justificativa": (
                "A proposta reforca os pontos identificados sem substituir "
                "a ideia original. Revise e aprove a sugestao antes de "
                "solicitar uma nova geracao."
            ),
            "alteracoes_propostas": list(dict.fromkeys(changes)),
            "metodo_analise": "regras_locais_sem_api",
        }

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
        """Analisa a geracao e devolve uma proposta de correcao."""

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

        # Sem chave, utiliza automaticamente a analise local.
        if not self.available():
            return self._analyze_locally(
                prompt=prompt,
                rating=rating,
                satisfaction_pct=satisfaction_pct,
                feedback=feedback,
                shared_memory=shared_memory,
                individual_memory=individual_memory,
            )

        instructions = """
Voce e especialista em engenharia de prompts para Stable Diffusion 1.5.
Analise o prompt e o feedback, preserve a ideia original e proponha
melhorias concretas. Nao invente elementos nao solicitados.
Responda exclusivamente em JSON com os campos:
problemas_identificados, causa_provavel, prompt_corrigido,
prompt_negativo_adicional, justificativa e alteracoes_propostas.
A proposta depende de aprovacao humana.
"""

        user_content = [
            {
                "type": "input_text",
                "text": (
                    "PROMPT ORIGINAL:\n" + prompt.strip()
                    + "\n\nNOTA: " + str(rating) + "/10"
                    + "\nSATISFACAO: " + str(satisfaction_pct) + "%"
                    + "\nFEEDBACK:\n" + feedback
                    + "\n\nMEMORIA COMPARTILHADA:\n"
                    + json.dumps(shared_memory or [], ensure_ascii=False)
                    + "\n\nMEMORIA INDIVIDUAL:\n"
                    + json.dumps(individual_memory or [], ensure_ascii=False)
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
                input=[{
                    "role": "user",
                    "content": user_content,
                }],
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

            if (
                not isinstance(result["prompt_corrigido"], str)
                or not result["prompt_corrigido"].strip()
            ):
                raise AICorrectionError(
                    "O prompt corrigido retornado e invalido."
                )

            return result

        except AICorrectionError:
            raise
        except Exception as exc:
            raise AICorrectionError(
                "Nao foi possivel concluir a analise de autocorrecao: "
                + type(exc).__name__
            ) from exc

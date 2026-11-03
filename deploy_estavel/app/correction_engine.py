"""
Motor de coordenacao da autocorrecao assistida do GeraArteIA.

Responsabilidades:
- Consultar memorias compartilhadas e individuais.
- Solicitar analise a IA.
- Preparar proposta de correcao.
- Exigir aprovacao humana antes da regeneracao.

Este modulo nao gera imagens e nao altera o banco de geracoes.
"""

from typing import Optional

from app.ai_correction import AICorrection, AICorrectionError
from app.learning_memory import LearningMemory, LearningMemoryError


class CorrectionEngineError(Exception):
    """Erro controlado do motor de autocorrecao."""


class CorrectionEngine:
    """Coordena analise, memoria e proposta de correcao."""

    def __init__(
        self,
        memory: LearningMemory,
        ai: Optional[AICorrection] = None,
    ):
        if not isinstance(memory, LearningMemory):
            raise ValueError("Uma instancia valida de LearningMemory e obrigatoria.")

        self.memory = memory
        self.ai = ai or AICorrection()

    def prepare_correction(
        self,
        prompt: str,
        rating: int,
        satisfaction_pct: Optional[int] = None,
        feedback: str = "",
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        image_data_url: Optional[str] = None,
    ) -> dict:
        """
        Prepara uma proposta de correcao para aprovacao.

        A consulta individual e opcional e depende do user_id.
        A memoria compartilhada fornece apenas referencias tecnicas.
        """

        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("O prompt original e obrigatorio.")

        category = (category or "geral").strip().lower()

        try:
            shared = self.memory.get_shared(
                category=category,
                limit=10,
            )

            individual = []

            if user_id:
                individual = self.memory.get_individual(
                    user_id=user_id,
                    category=category,
                    limit=10,
                )

            analysis = self.ai.analyze(
                prompt=prompt,
                rating=rating,
                satisfaction_pct=satisfaction_pct,
                feedback=feedback,
                image_data_url=image_data_url,
                shared_memory=shared,
                individual_memory=individual,
            )

            return {
                "status": "aguardando_aprovacao",
                "approved": False,
                "original_prompt": prompt,
                "category": category,
                "analysis": analysis,
                "shared_memory": shared,
                "individual_memory": individual,
                "proposed_prompt": analysis["prompt_corrigido"],
                "additional_negative_prompt": analysis.get(
                    "prompt_negativo_adicional", ""
                ),
                "message": (
                    "Proposta preparada. Revise e aprove antes de "
                    "solicitar uma nova geracao."
                ),
            }

        except (AICorrectionError, LearningMemoryError) as exc:
            raise CorrectionEngineError(
                "Nao foi possivel preparar a correcao: "
                + type(exc).__name__
            ) from exc

    @staticmethod
    def approve_correction(proposal: dict, edited_prompt: Optional[str] = None):
        """
        Registra a aprovacao humana na proposta em memoria.

        Nao executa a geracao da imagem.
        """

        if not isinstance(proposal, dict):
            raise ValueError("Proposta invalida.")

        if proposal.get("status") != "aguardando_aprovacao":
            raise ValueError("A proposta nao esta aguardando aprovacao.")

        final_prompt = (
            edited_prompt
            if edited_prompt is not None
            else proposal.get("proposed_prompt", "")
        )

        if not isinstance(final_prompt, str) or not final_prompt.strip():
            raise ValueError("O prompt aprovado nao pode estar vazio.")

        approved = dict(proposal)
        approved["proposed_prompt"] = final_prompt.strip()
        approved["approved"] = True
        approved["status"] = "aprovada"

        return approved

"""
Memoria de aprendizado compartilhada e individual do GeraArteIA.

- Memoria compartilhada: registra padroes tecnicos anonimizados.
- Memoria individual: registra preferencias e correcoes por usuario.
- Nao altera a tabela original de geracoes.
- Nao aplica correcoes automaticamente.
"""

import sqlite3
from pathlib import Path
from typing import Optional


class LearningMemoryError(Exception):
    """Erro controlado do modulo de memoria."""


class LearningMemory:
    """Armazena e consulta aprendizados do sistema."""

    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def _connect(self):
        connection = sqlite3.connect(str(self.db_path), timeout=15)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        """Cria somente as tabelas novas de aprendizado."""

        try:
            with self._connect() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS shared_learning_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        error_pattern TEXT NOT NULL,
                        correction_pattern TEXT NOT NULL,
                        positive_count INTEGER NOT NULL DEFAULT 0,
                        negative_count INTEGER NOT NULL DEFAULT 0,
                        confidence REAL NOT NULL DEFAULT 0,
                        active INTEGER NOT NULL DEFAULT 1,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(category, error_pattern, correction_pattern)
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_learning_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        category TEXT NOT NULL,
                        preference TEXT NOT NULL,
                        correction_pattern TEXT NOT NULL,
                        positive_count INTEGER NOT NULL DEFAULT 0,
                        negative_count INTEGER NOT NULL DEFAULT 0,
                        active INTEGER NOT NULL DEFAULT 1,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, category, preference, correction_pattern)
                    )
                """)

                conn.commit()

        except sqlite3.Error as exc:
            raise LearningMemoryError(
                "Nao foi possivel inicializar a memoria: "
                + type(exc).__name__
            ) from exc

    @staticmethod
    def _required_text(value, field):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"O campo {field} e obrigatorio.")

        value = value.strip()

        if len(value) > 2000:
            raise ValueError(f"O campo {field} excede 2000 caracteres.")

        return value

    def record_shared(
        self,
        category: str,
        error_pattern: str,
        correction_pattern: str,
        successful: bool,
    ):
        """
        Registra um padrao tecnico compartilhado.

        Nao enviar nomes, documentos, prompts privados ou imagens.
        """

        category = self._required_text(category, "category")
        error_pattern = self._required_text(
            error_pattern, "error_pattern"
        )
        correction_pattern = self._required_text(
            correction_pattern, "correction_pattern"
        )

        if not isinstance(successful, bool):
            raise ValueError("successful deve ser verdadeiro ou falso.")

        positive = 1 if successful else 0
        negative = 0 if successful else 1

        try:
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO shared_learning_memory (
                        category, error_pattern, correction_pattern,
                        positive_count, negative_count
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(category, error_pattern, correction_pattern)
                    DO UPDATE SET
                        positive_count = positive_count + excluded.positive_count,
                        negative_count = negative_count + excluded.negative_count,
                        confidence = CAST(
                            positive_count + excluded.positive_count AS REAL
                        ) / NULLIF(
                            positive_count + negative_count
                            + excluded.positive_count
                            + excluded.negative_count, 0
                        ),
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    category,
                    error_pattern,
                    correction_pattern,
                    positive,
                    negative,
                ))
                conn.commit()

        except sqlite3.Error as exc:
            raise LearningMemoryError(
                "Falha ao registrar memoria compartilhada: "
                + type(exc).__name__
            ) from exc

    def record_individual(
        self,
        user_id: str,
        category: str,
        preference: str,
        correction_pattern: str,
        successful: bool,
    ):
        """Registra uma preferencia ou aprendizado individual."""

        user_id = self._required_text(user_id, "user_id")
        category = self._required_text(category, "category")
        preference = self._required_text(preference, "preference")
        correction_pattern = self._required_text(
            correction_pattern, "correction_pattern"
        )

        if len(user_id) > 128:
            raise ValueError("user_id excede 128 caracteres.")

        if not isinstance(successful, bool):
            raise ValueError("successful deve ser verdadeiro ou falso.")

        positive = 1 if successful else 0
        negative = 0 if successful else 1

        try:
            with self._connect() as conn:
                conn.execute("""
                    INSERT INTO user_learning_memory (
                        user_id, category, preference, correction_pattern,
                        positive_count, negative_count
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(
                        user_id, category, preference, correction_pattern
                    )
                    DO UPDATE SET
                        positive_count = positive_count + excluded.positive_count,
                        negative_count = negative_count + excluded.negative_count,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    user_id,
                    category,
                    preference,
                    correction_pattern,
                    positive,
                    negative,
                ))
                conn.commit()

        except sqlite3.Error as exc:
            raise LearningMemoryError(
                "Falha ao registrar memoria individual: "
                + type(exc).__name__
            ) from exc

    def get_shared(self, category: Optional[str] = None, limit: int = 20):
        """Consulta os aprendizados compartilhados mais bem avaliados."""

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("limit deve ser um numero inteiro.")

        limit = max(1, min(limit, 100))

        try:
            with self._connect() as conn:
                if category:
                    rows = conn.execute("""
                        SELECT * FROM shared_learning_memory
                        WHERE active = 1 AND category = ?
                        ORDER BY confidence DESC, positive_count DESC
                        LIMIT ?
                    """, (category, limit)).fetchall()
                else:
                    rows = conn.execute("""
                        SELECT * FROM shared_learning_memory
                        WHERE active = 1
                        ORDER BY confidence DESC, positive_count DESC
                        LIMIT ?
                    """, (limit,)).fetchall()

                return [dict(row) for row in rows]

        except sqlite3.Error as exc:
            raise LearningMemoryError(
                "Falha ao consultar memoria compartilhada: "
                + type(exc).__name__
            ) from exc

    def get_individual(
        self,
        user_id: str,
        category: Optional[str] = None,
        limit: int = 20,
    ):
        """Consulta somente a memoria do usuario informado."""

        user_id = self._required_text(user_id, "user_id")

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise ValueError("limit deve ser um numero inteiro.")

        limit = max(1, min(limit, 100))

        try:
            with self._connect() as conn:
                if category:
                    rows = conn.execute("""
                        SELECT * FROM user_learning_memory
                        WHERE active = 1
                          AND user_id = ?
                          AND category = ?
                        ORDER BY positive_count DESC, updated_at DESC
                        LIMIT ?
                    """, (user_id, category, limit)).fetchall()
                else:
                    rows = conn.execute("""
                        SELECT * FROM user_learning_memory
                        WHERE active = 1 AND user_id = ?
                        ORDER BY positive_count DESC, updated_at DESC
                        LIMIT ?
                    """, (user_id, limit)).fetchall()

                return [dict(row) for row in rows]

        except sqlite3.Error as exc:
            raise LearningMemoryError(
                "Falha ao consultar memoria individual: "
                + type(exc).__name__
            ) from exc

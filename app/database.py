import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "geraarteia.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS geracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                image_path TEXT NOT NULL,
                rating INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        existentes = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(geracoes)").fetchall()
        }

        novas_colunas = {
            "optimized_prompt": "TEXT",
            "satisfaction_pct": "INTEGER",
            "steps": "INTEGER",
            "width": "INTEGER",
            "height": "INTEGER",
            "review_required": "INTEGER NOT NULL DEFAULT 0",
            "review_status": "TEXT NOT NULL DEFAULT 'nao_avaliada'",
            "feedback": "TEXT",
        }

        for coluna, tipo in novas_colunas.items():
            if coluna not in existentes:
                conn.execute(
                    f"ALTER TABLE geracoes ADD COLUMN {coluna} {tipo}"
                )


def registrar_geracao(
    prompt: str,
    image_path: str,
    optimized_prompt: str = "",
    steps: int = 25,
    width: int = 512,
    height: int = 512,
):
    with get_db_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO geracoes
                (prompt, image_path, optimized_prompt, steps, width, height)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            prompt, image_path, optimized_prompt, steps, width, height
        ))
        return cursor.lastrowid


def avaliar_geracao(
    geracao_id: int,
    rating: int,
    satisfaction_pct: int,
    feedback: str = "",
):
    if not 0 <= rating <= 10:
        raise ValueError("A nota deve estar entre 0 e 10.")

    if satisfaction_pct not in (20, 40, 60, 80, 100):
        raise ValueError("Percentual de satisfação inválido.")

    revisar = rating < 5 and satisfaction_pct < 60
    status = "pendente" if revisar else "nao_requerida"

    with get_db_connection() as conn:
        cursor = conn.execute("""
            UPDATE geracoes
            SET rating = ?,
                satisfaction_pct = ?,
                review_required = ?,
                review_status = ?,
                feedback = ?
            WHERE id = ?
        """, (
            rating,
            satisfaction_pct,
            int(revisar),
            status,
            feedback.strip(),
            geracao_id,
        ))

        if cursor.rowcount == 0:
            raise ValueError("Geração não encontrada.")

    return {
        "id": geracao_id,
        "review_required": revisar,
        "review_status": status,
    }


def atualizar_avaliacao(
    geracao_id: int,
    rating: int,
    satisfaction_pct: int = 100,
    feedback: str = "",
):
    return avaliar_geracao(
        geracao_id, rating, satisfaction_pct, feedback
    )


def obter_historico(limit: int = 10):
    limit = max(1, min(int(limit), 200))
    with get_db_connection() as conn:
        return conn.execute(
            "SELECT * FROM geracoes ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()


def obter_estatisticas():
    with get_db_connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM geracoes"
        ).fetchone()[0]

        avaliadas = conn.execute(
            "SELECT COUNT(*) FROM geracoes WHERE rating IS NOT NULL"
        ).fetchone()[0]

        media = conn.execute(
            "SELECT AVG(rating) FROM geracoes WHERE rating IS NOT NULL"
        ).fetchone()[0]

        revisoes = conn.execute(
            "SELECT COUNT(*) FROM geracoes WHERE review_required = 1 "
            "AND review_status = 'pendente'"
        ).fetchone()[0]

        satisfacao = conn.execute("""
            SELECT satisfaction_pct, COUNT(*) AS total
            FROM geracoes
            WHERE satisfaction_pct IS NOT NULL
            GROUP BY satisfaction_pct
            ORDER BY satisfaction_pct
        """).fetchall()

    return {
        "total_geradas": total,
        "total_avaliadas": avaliadas,
        "media_avaliacao": round(media, 1) if media is not None else 0.0,
        "revisoes_pendentes": revisoes,
        "distribuicao_satisfacao": {
            str(row["satisfaction_pct"]): row["total"]
            for row in satisfacao
        },
    }


def obter_fila_revisao(limit: int = 100):
    limit = max(1, min(int(limit), 500))
    with get_db_connection() as conn:
        return conn.execute("""
            SELECT * FROM geracoes
            WHERE review_required = 1 AND review_status = 'pendente'
            ORDER BY id DESC LIMIT ?
        """, (limit,)).fetchall()


def concluir_revisao(geracao_id: int):
    with get_db_connection() as conn:
        cursor = conn.execute("""
            UPDATE geracoes
            SET review_status = 'concluida'
            WHERE id = ? AND review_required = 1
        """, (geracao_id,))

        if cursor.rowcount == 0:
            raise ValueError("Caso de revisão pendente não encontrado.")


init_db()

import sqlite3
from pathlib import Path

from app.config import BASE_DIR

DATABASE_PATH = BASE_DIR / "geraarteia.db"


def conectar():
    conexao = sqlite3.connect(DATABASE_PATH, timeout=10)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS geracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                arquivo TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')
                ),
                nota INTEGER CHECK (nota IS NULL OR nota BETWEEN 0 AND 10)
            )
        """)
        conexao.execute("""
            CREATE INDEX IF NOT EXISTS idx_geracoes_criado_em
            ON geracoes (criado_em)
        """)


def registrar_geracao(prompt, arquivo):
    with conectar() as conexao:
        cursor = conexao.execute(
            "INSERT INTO geracoes (prompt, arquivo) VALUES (?, ?)",
            (prompt, arquivo),
        )
        return cursor.lastrowid


def avaliar_geracao(geracao_id, nota):
    if not 0 <= nota <= 10:
        raise ValueError("A nota deve estar entre 0 e 10.")

    with conectar() as conexao:
        cursor = conexao.execute(
            "UPDATE geracoes SET nota = ? WHERE id = ?",
            (nota, geracao_id),
        )
        return cursor.rowcount > 0


def obter_estatisticas():
    with conectar() as conexao:
        resumo = conexao.execute("""
            SELECT
                COUNT(*) AS total_geracoes,
                COUNT(nota) AS total_avaliacoes,
                ROUND(AVG(nota), 2) AS media_satisfacao
            FROM geracoes
        """).fetchone()

        notas = conexao.execute("""
            SELECT nota, COUNT(*) AS quantidade
            FROM geracoes
            WHERE nota IS NOT NULL
            GROUP BY nota
            ORDER BY nota
        """).fetchall()

    return {
        "total_geracoes": resumo["total_geracoes"],
        "total_avaliacoes": resumo["total_avaliacoes"],
        "media_satisfacao": resumo["media_satisfacao"],
        "avaliacoes": [
            {"nota": item["nota"], "quantidade": item["quantidade"]}
            for item in notas
        ],
    }


inicializar_banco()



def obter_historico(limite=30):
    with conectar() as conexao:
        linhas = conexao.execute(
            """
            SELECT id, prompt, arquivo, criado_em, nota
            FROM geracoes
            ORDER BY id DESC
            LIMIT ?
            """,
            (limite,),
        ).fetchall()

    return [
        {
            "id": linha["id"],
            "prompt": linha["prompt"],
            "arquivo": linha["arquivo"],
            "criado_em": linha["criado_em"],
            "nota": linha["nota"],
            "imagem": f"/api/imagem/{linha['arquivo']}",
        }
        for linha in linhas
    ]

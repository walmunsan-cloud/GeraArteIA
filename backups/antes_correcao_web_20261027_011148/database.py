import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "geraarteia.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS geracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            image_path TEXT NOT NULL,
            rating INTEGER DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def registrar_geracao(prompt: str, image_path: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO geracoes (prompt, image_path) VALUES (?, ?)",
        (prompt, image_path)
    )
    conn.commit()
    geracao_id = cursor.lastrowid
    conn.close()
    return geracao_id

def avaliar_geracao(geracao_id: int, rating: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE geracoes SET rating = ? WHERE id = ?",
        (rating, geracao_id)
    )
    conn.commit()
    conn.close()

# Mantemos também o alias caso outro módulo chame o nome antigo
def atualizar_avaliacao(geracao_id: int, rating: int):
    return avaliar_geracao(geracao_id, rating)

def obter_historico(limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM geracoes ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def obter_estatisticas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM geracoes")
    total_geradas = cursor.fetchone()["total"]
    
    cursor.execute("SELECT COUNT(*) as avaliadas FROM geracoes WHERE rating IS NOT NULL")
    total_avaliadas = cursor.fetchone()["avaliadas"]
    
    cursor.execute("SELECT AVG(rating) as media FROM geracoes WHERE rating IS NOT NULL")
    media_res = cursor.fetchone()["media"]
    media_avaliacao = round(media_res, 1) if media_res else 0.0
    
    conn.close()
    return {
        "total_geradas": total_geradas,
        "total_avaliadas": total_avaliadas,
        "media_avaliacao": media_avaliacao
    }

# Inicializa a base de dados ao importar
init_db()

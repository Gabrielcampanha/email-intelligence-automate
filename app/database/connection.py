import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Caminho do banco de dados na pasta data para facilitar persistência em Docker
DB_PATH = Path(__file__).parent.parent.parent / "data" / "emails.db"

@contextmanager
def get_connection():
    """
    Gerenciador de contexto para conexões com o banco de dados SQLite.
    Garante que a conexão seja fechada corretamente.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """
    Inicializa o banco de dados criando a tabela de e-mails se não existir.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                category TEXT NOT NULL,
                urgent BOOLEAN NOT NULL,
                summary TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

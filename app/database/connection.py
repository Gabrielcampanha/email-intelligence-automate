import sqlite3
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from pathlib import Path

# Configurações para SQLite (fallback e testes)
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "emails.db"
_sqlite_connection_pool = {}

def is_postgres():
    """Verifica se a configuração atual é para PostgreSQL."""
    db_url = os.getenv("DATABASE_URL")
    return db_url and db_url.startswith("postgres")

@contextmanager
def get_connection():
    """
    Gerenciador de contexto que suporta tanto SQLite quanto PostgreSQL.
    """
    db_url = os.getenv("DATABASE_URL")
    db_path = os.getenv("DB_PATH", str(DEFAULT_DB_PATH))

    # Caso 1: PostgreSQL (Produção)
    if is_postgres():
        conn = psycopg2.connect(db_url, sslmode="require")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # Caso 2: SQLite (Desenvolvimento/Testes)
    else:
        # Se for em memória, usamos o pool para persistir a conexão durante o teste
        if db_path == ":memory:":
            if db_path not in _sqlite_connection_pool:
                _sqlite_connection_pool[db_path] = sqlite3.connect(
                    db_path, check_same_thread=False
                )
            conn = _sqlite_connection_pool[db_path]
        else:
            conn = sqlite3.connect(db_path)

        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            if db_path != ":memory:":
                conn.close()

def init_db():
    """
    Inicializa o banco de dados criando a tabela de e-mails se não existir.
    Funciona tanto para SQLite quanto para PostgreSQL.
    """
    # Define o tipo de dado para boolean conforme o banco
    bool_type = "BOOLEAN" if is_postgres() else "BOOLEAN"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                category TEXT NOT NULL,
                urgent {bool_type} NOT NULL,
                summary TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

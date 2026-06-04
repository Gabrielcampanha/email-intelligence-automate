from typing import List, Optional, Dict, Any
from app.database.connection import get_connection, is_postgres
from app.models.email_analysis import EmailAnalysis
from app.monitoring.logger import logger

def _row_to_dict(cursor, row):
    """Converte uma linha do banco para dicionário, lidando com SQLite e Postgres."""
    if hasattr(row, 'keys'): # SQLite
        return dict(row)
    # Postgres com cursor padrão retorna tupla
    return {col[0]: val for col, val in zip(cursor.description, row)}

def save_email(email_id: str, sender: str, subject: str, analysis: EmailAnalysis) -> None:
    """
    Salva um e-mail processado e sua análise no banco de dados.
    Suporta SQLite e PostgreSQL (Upsert).
    """
    if is_postgres():
        query = """
            INSERT INTO emails 
            (id, sender, subject, category, urgent, summary, recommended_action)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
            category = EXCLUDED.category,
            urgent = EXCLUDED.urgent,
            summary = EXCLUDED.summary,
            recommended_action = EXCLUDED.recommended_action
        """
        params = (
            email_id,
            sender,
            subject,
            analysis.categoria,
            analysis.urgente,
            analysis.resumo,
            analysis.acao_recomendada
        )
    else:
        query = """
            INSERT OR REPLACE INTO emails 
            (id, sender, subject, category, urgent, summary, recommended_action)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            email_id,
            sender,
            subject,
            analysis.categoria,
            1 if analysis.urgente else 0,
            analysis.resumo,
            analysis.acao_recomendada
        )

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        logger.info("E-mail salvo no banco de dados", email_id=email_id, category=analysis.categoria)

def get_all_emails() -> List[Dict[str, Any]]:
    """
    Retorna todos os e-mails processados do banco de dados.
    """
    query = "SELECT * FROM emails ORDER BY processed_at DESC"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return [_row_to_dict(cursor, row) for row in rows]

def get_emails_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Retorna e-mails processados filtrados por categoria.
    """
    placeholder = "%s" if is_postgres() else "?"
    query = f"SELECT * FROM emails WHERE category = {placeholder} ORDER BY processed_at DESC"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (category,))
        rows = cursor.fetchall()
        return [_row_to_dict(cursor, row) for row in rows]

from typing import List, Optional, Dict, Any
from app.database.connection import get_connection
from app.models.email_analysis import EmailAnalysis
from app.monitoring.logger import logger

def save_email(email_id: str, sender: str, subject: str, analysis: EmailAnalysis) -> None:
    """
    Salva um e-mail processado e sua análise no banco de dados.
    """
    query = """
        INSERT OR REPLACE INTO emails 
        (id, sender, subject, category, urgent, summary, recommended_action)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    with get_connection() as conn:
        conn.execute(query, (
            email_id,
            sender,
            subject,
            analysis.categoria,
            1 if analysis.urgente else 0,
            analysis.resumo,
            analysis.acao_recomendada
        ))
        logger.info("E-mail salvo no banco de dados", email_id=email_id, category=analysis.categoria)

def get_all_emails() -> List[Dict[str, Any]]:
    """
    Retorna todos os e-mails processados do banco de dados.
    """
    query = "SELECT * FROM emails ORDER BY processed_at DESC"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def get_emails_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Retorna e-mails processados filtrados por categoria.
    """
    query = "SELECT * FROM emails WHERE category = ? ORDER BY processed_at DESC"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (category,))
        return [dict(row) for row in cursor.fetchall()]

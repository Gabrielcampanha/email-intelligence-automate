from prefect import task, flow, get_run_logger
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

from app.services.email_reader import get_unprocessed_emails
from app.services.imap_reader import get_real_emails
from app.services.ai_processor import extract_email_data
from app.database.connection import init_db
from app.database.repository import save_email
from app.models.email_analysis import EmailAnalysis

@task(retries=3, retry_delay_seconds=10, timeout_seconds=30)
def read_emails_task() -> List[Dict[str, Any]]:
    """
    Task para ler e-mails (prioriza reais via IMAP, fallback para mock).
    """
    logger = get_run_logger()
    
    # Tenta buscar e-mails reais primeiro
    logger.info("Tentando buscar e-mails reais via IMAP...")
    emails = get_real_emails()
    
    if emails:
        logger.info(f"{len(emails)} e-mails reais não lidos encontrados.")
        return emails
    
    # Se não encontrar reais, usa os mocks
    logger.info("Nenhum e-mail real configurado ou encontrado. Usando mocks...")
    emails = get_unprocessed_emails()
    logger.info(f"{len(emails)} e-mails mockados carregados.")
    return emails

@task(retries=2, retry_delay_seconds=5)
def process_email_task(email: Dict[str, Any]) -> EmailAnalysis:
    """
    Task para processar um único e-mail com IA.
    """
    logger = get_run_logger()
    subject = email.get("subject", "N/A")
    body = email.get("body", "N/A")
    email_id = email.get("id", "N/A")
    
    logger.info(f"Processando e-mail ID {email_id} - Assunto: {subject}")
    analysis = extract_email_data(subject, body)
    return analysis

@task
def save_email_task(email: Dict[str, Any], analysis: EmailAnalysis):
    """
    Task para persistir os dados no banco de dados.
    """
    logger = get_run_logger()
    email_id = email.get("id", "N/A")
    sender = email.get("from", "N/A")
    subject = email.get("subject", "N/A")
    
    save_email(email_id, sender, subject, analysis)
    logger.info(f"E-mail {email_id} salvo com sucesso no banco de dados.")

@flow(name="Email Processing Pipeline")
def email_processing_flow():
    """
    Fluxo principal de orquestração do pipeline de e-mails.
    """
    logger = get_run_logger()
    logger.info("Iniciando Pipeline de Automação de E-mails")
    
    # Inicializa o banco de dados
    init_db()
    
    # Executa a task de leitura
    emails = read_emails_task()
    
    if not emails:
        logger.warning("Nenhum e-mail para processar.")
        return

    # Itera sobre os e-mails e executa as tasks de processamento e persistência
    for email in emails:
        try:
            analysis = process_email_task(email)
            save_email_task(email, analysis)
        except Exception as e:
            logger.error(f"Falha ao processar e-mail {email.get('id')}: {e}")

    logger.info("Pipeline finalizado com sucesso!")

if __name__ == "__main__":
    email_processing_flow()

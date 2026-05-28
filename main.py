from typing import List, Dict, Any
from app.services.email_reader import get_unprocessed_emails
from app.services.ai_processor import extract_email_data
from app.database.connection import init_db
from app.database.repository import save_email, get_all_emails


def process_and_display_emails(emails: List[Dict[str, Any]]) -> None:
    """
    Processa os e-mails com IA, salva no banco de dados e exibe no console.
    """
    if not emails:
        print("Nenhum e-mail encontrado para processar.")
        return

    print("=" * 80)
    print("PROCESSANDO E-MAILS E SALVANDO NO BANCO DE DADOS")
    print("=" * 80)

    for email in emails:
        email_id = email.get('id', 'N/A')
        sender = email.get('from', 'N/A')
        subject = email.get('subject', 'N/A')
        body = email.get('body', 'N/A')
        
        # Extração de dados estruturados com IA
        print(f"Analisando e-mail ID {email_id}...")
        analysis = extract_email_data(subject, body)
        
        # Salvando no SQLite
        save_email(email_id, sender, subject, analysis)
        
        print(f"\nID: {email_id}")
        print(f"De: {sender}")
        print(f"Assunto: {subject}")
        print("-" * 80)
        print(f"CATEGORIA: {analysis.categoria.upper()}")
        print(f"URGENTE: {'SIM' if analysis.urgente else 'NÃO'}")
        print(f"RESUMO: {analysis.resumo}")
        print(f"AÇÃO RECOMENDADA: {analysis.acao_recomendada}")
        print("-" * 80)
        print(f"Status: Salvo com sucesso no banco de dados.")
        print("\n" + "=" * 80 + "\n")


def display_db_summary() -> None:
    """
    Exibe um resumo dos e-mails persistidos no banco.
    """
    stored_emails = get_all_emails()
    print("\n" + "!" * 80)
    print(f"RESUMO DO BANCO DE DADOS ({len(stored_emails)} e-mails totais)")
    print("!" * 80)
    
    for row in stored_emails:
        print(f"[{row['processed_at']}] {row['category'].upper()} | {row['sender']} | {row['subject']}")


def main() -> None:
    """
    Função principal do programa.
    """
    # Inicializa o banco de dados (cria tabelas se não existirem)
    init_db()
    
    # Busca e-mails mockados
    emails = get_unprocessed_emails()
    
    # Processa, salva e exibe
    process_and_display_emails(emails)
    
    # Exibe resumo do que está no banco
    display_db_summary()


if __name__ == "__main__":
    main()

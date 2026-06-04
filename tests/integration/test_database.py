import pytest
from app.database.repository import save_email, get_all_emails, get_emails_by_category
from app.models.email_analysis import EmailAnalysis

def test_save_and_get_emails(db_session):
    # Setup
    analysis = EmailAnalysis(
        categoria="financeiro",
        urgente=True,
        resumo="Teste",
        acao_recomendada="Nenhuma"
    )
    
    # Action
    save_email("id-1", "sender@test.com", "Assunto Teste", analysis)
    
    # Assert
    emails = get_all_emails()
    assert len(emails) == 1
    assert emails[0]["id"] == "id-1"
    assert emails[0]["sender"] == "sender@test.com"
    assert emails[0]["category"] == "financeiro"
    assert emails[0]["urgent"] == 1

def test_get_emails_by_category(db_session):
    # Setup
    analysis_fin = EmailAnalysis(categoria="financeiro", urgente=False, resumo="R1", acao_recomendada="A1")
    analysis_sup = EmailAnalysis(categoria="suporte", urgente=False, resumo="R2", acao_recomendada="A2")
    
    save_email("id-fin", "s1@t.com", "Sub Fin", analysis_fin)
    save_email("id-sup", "s2@t.com", "Sub Sup", analysis_sup)
    
    # Action
    fin_emails = get_emails_by_category("financeiro")
    sup_emails = get_emails_by_category("suporte")
    
    # Assert
    assert len(fin_emails) == 1
    assert fin_emails[0]["id"] == "id-fin"
    assert len(sup_emails) == 1
    assert sup_emails[0]["id"] == "id-sup"

def test_save_email_replace(db_session):
    # Test INSERT OR REPLACE
    analysis = EmailAnalysis(categoria="spam", urgente=False, resumo="R", acao_recomendada="A")
    
    save_email("id-same", "s@t.com", "Sub 1", analysis)
    
    # Update same ID
    analysis.resumo = "Resumo Novo"
    save_email("id-same", "s@t.com", "Sub 1", analysis)
    
    emails = get_all_emails()
    assert len(emails) == 1
    assert emails[0]["summary"] == "Resumo Novo"

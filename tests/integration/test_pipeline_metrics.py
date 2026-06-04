import pytest
from flows.email_pipeline import email_processing_flow
from app.monitoring.metrics import EMAILS_PROCESSED_TOTAL

def test_email_processing_flow_execution(mocker, db_session, mock_openai):
    # Mocking read_emails_task return
    mock_emails = [{
        "id": "test-1",
        "from": "test@test.com",
        "subject": "Test",
        "body": "Body"
    }]
    mocker.patch("flows.email_pipeline.read_emails_task", return_value=mock_emails)
    
    # Mocking AI result
    import json
    json_response = {
        "categoria": "suporte",
        "urgente": False,
        "resumo": "Resumo",
        "acao_recomendada": "Ação"
    }
    mock_openai.chat.completions.create.return_value.choices[0].message.content = json.dumps(json_response)
    
    # Run flow
    email_processing_flow()
    
    # Verify DB
    from app.database.repository import get_all_emails
    emails = get_all_emails()
    assert len(emails) == 1
    assert emails[0]["id"] == "test-1"

def test_metrics_increment(mocker, mock_openai):
    from app.monitoring.metrics import AI_REQUESTS_TOTAL
    
    # Get initial value
    try:
        initial = AI_REQUESTS_TOTAL.labels(model="gpt-4.1-mini", status="success")._value.get()
    except:
        initial = 0
        
    # Trigger AI call
    import json
    json_response = {"categoria": "suporte", "urgente": False, "resumo": "R", "acao_recomendada": "A"}
    mock_openai.chat.completions.create.return_value.choices[0].message.content = json.dumps(json_response)
    
    from app.services.ai_processor import extract_email_data
    extract_email_data("S", "B")
    
    # Check increment
    final = AI_REQUESTS_TOTAL.labels(model="gpt-4.1-mini", status="success")._value.get()
    # Note: AI_REQUESTS_TOTAL uses 'gpt-4.1-mini' in success path (per ai_processor.py line 118)
    assert final == initial + 1

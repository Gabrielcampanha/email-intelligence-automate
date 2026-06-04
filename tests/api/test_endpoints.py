import pytest
import json

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_process_email_endpoint(client, mock_openai, db_session):
    # Setup mock OpenAI
    json_response = {
        "categoria": "financeiro",
        "urgente": False,
        "resumo": "Boleto",
        "acao_recomendada": "Pagar"
    }
    mock_openai.chat.completions.create.return_value.choices[0].message.content = json.dumps(json_response)
    
    # Action
    payload = {
        "sender": "banco@teste.com",
        "subject": "Sua fatura chegou",
        "body": "Segue em anexo o boleto para pagamento."
    }
    response = client.post("/process-email", json=payload)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["sender"] == "banco@teste.com"
    assert data["category"] == "financeiro"
    assert "id" in data

def test_process_email_invalid_payload(client):
    # Missing subject
    payload = {
        "sender": "banco@teste.com",
        "body": "..."
    }
    response = client.post("/process-email", json=payload)
    assert response.status_code == 422 # Unprocessable Entity

def test_list_emails_endpoint(client, db_session):
    # Action
    response = client.get("/emails")
    
    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_emails_by_category_endpoint(client, db_session):
    response = client.get("/emails/category/financeiro")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text

import pytest
import json
from app.services.ai_processor import classify_email, extract_email_data
from app.models.email_analysis import EmailAnalysis

def test_classify_email_success(mock_openai):
    # Setup mock
    mock_openai.chat.completions.create.return_value.choices[0].message.content = "financeiro"
    
    result = classify_email("Fatura", "Corpo do email")
    
    assert result == "financeiro"
    mock_openai.chat.completions.create.assert_called_once()

def test_classify_email_invalid_category_fallback(mock_openai):
    # Setup mock with invalid category
    mock_openai.chat.completions.create.return_value.choices[0].message.content = "invalido"
    
    result = classify_email("Fatura", "Corpo do email")
    
    assert result == "suporte"

def test_extract_email_data_success(mock_openai):
    # Setup mock with valid JSON
    json_response = {
        "categoria": "urgente",
        "urgente": True,
        "resumo": "Problema crítico",
        "acao_recomendada": "Verificar agora"
    }
    mock_openai.chat.completions.create.return_value.choices[0].message.content = json.dumps(json_response)
    
    result = extract_email_data("Assunto", "Corpo")
    
    assert isinstance(result, EmailAnalysis)
    assert result.categoria == "urgente"
    assert result.urgente is True
    assert result.resumo == "Problema crítico"

def test_extract_email_data_invalid_json_fallback(mock_openai):
    # Setup mock with invalid JSON string
    mock_openai.chat.completions.create.return_value.choices[0].message.content = "Não é um JSON"
    
    result = extract_email_data("Assunto", "Corpo")
    
    assert result.categoria == "suporte"
    assert result.urgente is False
    assert "Não foi possível processar" in result.resumo

def test_extract_email_data_openai_error_fallback(mock_openai):
    # Setup mock to raise exception
    mock_openai.chat.completions.create.side_effect = Exception("OpenAI API Down")
    
    result = extract_email_data("Assunto", "Corpo")
    
    assert result.categoria == "suporte"
    assert result.urgente is False

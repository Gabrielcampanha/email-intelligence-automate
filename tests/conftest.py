import pytest
import sqlite3
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main_api import app
from app.database.connection import get_connection

@pytest.fixture
def mock_openai(mocker):
    """Fixture para mockar o cliente OpenAI"""
    mock = mocker.patch("app.services.ai_processor.client")
    return mock

@pytest.fixture
def db_session(mocker):
    """Fixture para banco de dados em memória para testes"""
    # Forçar o uso de :memory: via mock do DB_PATH se necessário, 
    # mas o getenv no connection.py já deve pegar do pytest.ini
    from app.database.connection import init_db, get_connection
    
    # Limpar o banco em memória antes de cada teste
    with get_connection() as conn:
        conn.execute("DROP TABLE IF EXISTS emails")
    
    init_db()
    yield

@pytest.fixture
def client():
    """Fixture para o TestClient do FastAPI"""
    return TestClient(app)

@pytest.fixture
def mock_imap(mocker):
    """Fixture para mockar o servidor IMAP"""
    return mocker.patch("app.services.imap_reader.imaplib.IMAP4_SSL")

@pytest.fixture
def sample_email_analysis():
    """Fixture com um objeto de análise de exemplo"""
    from app.models.email_analysis import EmailAnalysis
    return EmailAnalysis(
        categoria="financeiro",
        urgente=True,
        resumo="Fatura pendente",
        acao_recomendada="Pagar imediatamente"
    )

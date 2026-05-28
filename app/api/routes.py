from fastapi import APIRouter, HTTPException, Path
from typing import List
import uuid
from datetime import datetime

from app.models.api_models import EmailRequest, EmailResponse
from app.services.ai_processor import extract_email_data
from app.database.repository import save_email, get_all_emails, get_emails_by_category

router = APIRouter()

@router.post("/process-email", response_model=EmailResponse, status_code=201)
async def process_email(request: EmailRequest):
    """
    Processa um e-mail individual: classifica, extrai dados e salva no banco.
    """
    try:
        # Gerar um ID único para o e-mail via API
        email_id = str(uuid.uuid4())
        
        # Extração de dados via IA
        analysis = extract_email_data(request.subject, request.body)
        
        # Salvar no banco de dados
        save_email(email_id, request.sender, request.subject, analysis)
        
        # Retornar o objeto estruturado
        return EmailResponse(
            id=email_id,
            sender=request.sender,
            subject=request.subject,
            category=analysis.categoria,
            urgent=analysis.urgente,
            summary=analysis.resumo,
            recommended_action=analysis.acao_recomendada,
            processed_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar e-mail: {str(e)}")

@router.get("/emails", response_model=List[EmailResponse])
async def list_emails():
    """
    Retorna todos os e-mails processados e salvos no banco de dados.
    """
    try:
        emails = get_all_emails()
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar e-mails: {str(e)}")

@router.get("/emails/category/{category}", response_model=List[EmailResponse])
async def list_emails_by_category(
    category: str = Path(..., description="A categoria para filtrar (financeiro, suporte, urgente, spam)")
):
    """
    Retorna e-mails filtrados por uma categoria específica.
    """
    try:
        emails = get_emails_by_category(category.lower())
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar e-mails por categoria: {str(e)}")

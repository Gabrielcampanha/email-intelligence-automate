import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
from typing import Literal

# Carrega variáveis de ambiente
load_dotenv()

from app.models.email_analysis import EmailAnalysis
from app.monitoring.logger import logger
from app.monitoring.metrics import AI_REQUESTS_TOTAL
from app.monitoring.alerts import ia_monitor

Category = Literal["financeiro", "suporte", "urgente", "spam"]

VALID_CATEGORIES = {
    "financeiro",
    "suporte",
    "urgente",
    "spam"
}

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY não configurada.")

client = OpenAI(api_key=api_key)


def classify_email(subject: str, body: str) -> Category:
    """
    Classifica um e-mail utilizando IA.
    """

    prompt = f"""
    Classifique o e-mail abaixo em apenas uma categoria:
    financeiro, suporte, urgente ou spam.

    Responda SOMENTE com a categoria.

    Assunto: {subject}
    Corpo: {body}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um classificador de e-mails."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        category = response.choices[0].message.content.strip().lower()

        if category not in VALID_CATEGORIES:
            return "suporte"

        return category

    except Exception as e:
        AI_REQUESTS_TOTAL.labels(model="gpt-4o-mini", status="error").inc()
        print(f"Erro ao classificar e-mail: {e}")
        return "suporte"


def extract_email_data(subject: str, body: str) -> EmailAnalysis:
    """
    Extrai dados estruturados de um e-mail utilizando IA.
    """

    prompt = f"""
    Analise o e-mail abaixo e extraia as informações no formato JSON.
    O JSON deve conter exatamente as seguintes chaves:
    - "categoria": uma das seguintes (financeiro, suporte, urgente, spam)
    - "urgente": booleano indicando se o assunto requer atenção imediata
    - "resumo": um resumo de uma frase sobre o conteúdo do e-mail
    - "acao_recomendada": uma sugestão de próximo passo para tratar este e-mail

    Responda APENAS o JSON puro, sem blocos de código ou texto adicional.

    Assunto: {subject}
    Corpo: {body}
    """

    # Fallback em caso de erro
    fallback = EmailAnalysis(
        categoria="suporte",
        urgente=False,
        resumo="Não foi possível processar o resumo.",
        acao_recomendada="Revisar e-mail manualmente."
    )

    try:
        logger.info("Chamando OpenAI para extração de dados", subject=subject)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente que extrai dados de e-mails em formato JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        AI_REQUESTS_TOTAL.labels(model="gpt-4.1-mini", status="success").inc()
        ia_monitor.record_success()
        
        content = response.choices[0].message.content.strip()
        
        # Tenta carregar o JSON
        data = json.loads(content)
        
        logger.info("Extração de dados concluída com sucesso", email_id=None)
        
        # Validação básica dos campos
        return EmailAnalysis(
            categoria=data.get("categoria", "suporte") if data.get("categoria") in VALID_CATEGORIES else "suporte",
            urgente=bool(data.get("urgente", False)),
            resumo=str(data.get("resumo", "Resumo indisponível")),
            acao_recomendada=str(data.get("acao_recomendada", "Nenhuma ação recomendada"))
        )

    except (json.JSONDecodeError, Exception) as e:
        AI_REQUESTS_TOTAL.labels(model="gpt-4o-mini", status="error").inc()
        ia_monitor.record_failure(str(e))
        logger.error(f"Erro crítico na IA: {str(e)}")
        return fallback
from prometheus_client import Counter, Histogram, Summary
import time

# Métricas de Processamento
EMAILS_PROCESSED_TOTAL = Counter(
    'emails_processed_total', 
    'Total de e-mails processados',
    ['status', 'category']
)

PROCESSING_ERRORS_TOTAL = Counter(
    'processing_errors_total', 
    'Total de erros durante o processamento',
    ['error_type']
)

# Métricas de IA
AI_REQUESTS_TOTAL = Counter(
    'ai_requests_total', 
    'Total de chamadas à API da OpenAI',
    ['model', 'status']
)

# Métricas de Performance
PROCESSING_DURATION = Histogram(
    'processing_duration_seconds', 
    'Tempo de processamento do e-mail em segundos',
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf"))
)

# Métricas de API
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total', 
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status_code']
)

HTTP_REQUEST_DURATION = Summary(
    'http_request_duration_seconds', 
    'Duração das requisições HTTP'
)

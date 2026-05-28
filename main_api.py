import uvicorn
import time
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

from app.api.routes import router
from app.database.connection import init_db
from app.monitoring.logger import logger
from app.monitoring.metrics import HTTP_REQUESTS_TOTAL, HTTP_REQUEST_DURATION

app = FastAPI(
    title="Email Intelligence API",
    description="API para classificação e extração de dados de e-mails usando IA.",
    version="1.0.0"
)

# Inicializa o banco de dados ao subir a API
@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("API iniciada e banco de dados inicializado")

# Middleware para métricas e logging de requisições
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    
    # Processa a requisição
    response = await call_next(request)
    
    duration = time.time() - start_time
    status_code = response.status_code
    method = request.method
    endpoint = request.url.path
    
    # Registra métricas
    HTTP_REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    HTTP_REQUEST_DURATION.observe(duration)
    
    # Log estruturado da requisição
    logger.info(
        f"Request {method} {endpoint} finalizada",
        method=method,
        endpoint=endpoint,
        status_code=status_code,
        duration=round(duration, 4)
    )
    
    return response

# Endpoint de métricas para o Prometheus
@app.get("/metrics", tags=["Monitoring"])
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Inclui as rotas
app.include_router(router, tags=["Emails"])

@app.get("/", tags=["Health"])
def root():
    return {"status": "online", "message": "Email Intelligence API is running"}

if __name__ == "__main__":
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)

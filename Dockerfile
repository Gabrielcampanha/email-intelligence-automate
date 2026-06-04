# Usar uma imagem base leve
FROM python:3.11-slim

# Evitar que o Python gere arquivos .pyc e garantir logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Definir o diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para algumas bibliotecas Python e Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas o arquivo de requisitos primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código do projeto
COPY . .

# Criar diretório para o banco de dados e garantir permissões (se necessário)
RUN mkdir -p data

# Expor a porta que o FastAPI usará
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "8000"]

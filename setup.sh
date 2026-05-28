#!/bin/bash

# Script de inicialização automática para sistemas Unix (Linux/macOS)

echo "--- Iniciando Setup do Email Automate ---"

# Verifica se o arquivo .env existe
if [ ! -f .env ]; then
    echo "Aviso: Arquivo .env não encontrado. Criando a partir do .env.example..."
    cp .env.example .env
    echo "IMPORTANTE: Edite o arquivo .env e adicione sua OPENAI_API_KEY antes de rodar a aplicação."
fi

# Cria o ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativa o venv e instala dependências
echo "Instalando dependências..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Cria diretório de dados se não existir
mkdir -p data

echo "--- Setup concluído com sucesso! ---"
echo "Para rodar a API localmente: source venv/bin/activate && python main_api.py"
echo "Para rodar com Docker: docker-compose up -d --build"

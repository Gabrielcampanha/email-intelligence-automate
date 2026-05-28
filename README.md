# Email Automate 📧🤖

Projeto de automação inteligente de e-mails que utiliza IA para classificação, extração de dados estruturados e orquestração de pipelines.

## 🚀 Visão Geral
Este sistema permite processar fluxos de e-mails de forma automatizada, utilizando a API da OpenAI para entender o conteúdo, persistir informações em um banco de dados SQLite e monitorar a saúde da aplicação via Prometheus.

## 🏗️ Arquitetura
O projeto segue uma arquitetura modular e limpa:
- **FastAPI**: API REST para processamento sob demanda e consulta de dados.
- **OpenAI (GPT-4o-mini)**: Inteligência Artificial para análise semântica.
- **SQLite**: Persistência de dados local e eficiente.
- **Prefect**: Orquestração de pipelines de dados com retries e monitoramento.
- **Prometheus**: Coleta de métricas de performance e uso.
- **Docker**: Containerização completa do ambiente.

## 🛠️ Stack Utilizada
- Python 3.11+
- FastAPI
- OpenAI SDK
- Prefect
- Prometheus Client
- SQLite
- Docker & Docker Compose

## 📋 Funcionalidades
- **E-mails Reais**: Conexão via IMAP para processar sua caixa de entrada de verdade.
- **Classificação Inteligente**: Categoriza e-mails em `financeiro`, `suporte`, `urgente` ou `spam`.
- **Extração Estruturada**: Gera resumos e recomendações de ação automaticamente.
- **Pipeline Orquestrado**: Fluxo robusto para processamento em lote de e-mails.
- **Observabilidade**: Logs estruturados em JSON e métricas em tempo real.
- **Persistência**: Histórico completo de análises em banco de dados.

## ⚙️ Setup e Instalação

### Pré-requisitos
- Python 3.11 ou superior
- Docker & Docker Compose (opcional para rodar via container)
- Chave de API da OpenAI

### Configuração de E-mail Real (Gmail/Outlook)
Para que o sistema leia e-mails reais, você precisa configurar o IMAP:
1. **Gmail**:
   - Ative a "Verificação em duas etapas" na sua conta Google.
   - Vá em "Senhas de App" e gere uma nova senha para "E-mail".
   - Use essa senha de 16 dígitos no `.env` (campo `EMAIL_PASS`).
   - Garanta que o IMAP está ativado nas configurações do Gmail.
2. **Configuração .env**:
   ```env
   IMAP_SERVER=imap.gmail.com
   EMAIL_USER=seu-email@gmail.com
   EMAIL_PASS=sua-senha-de-app
   ```

### Configuração de Ambiente
1. Clone o repositório.
2. Copie o arquivo de exemplo e configure sua chave:
   ```bash
   cp .env.example .env
   # Edite o .env e insira sua OPENAI_API_KEY
   ```

### Instalação Local (venv)

#### Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p data
```

#### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (!(Test-Path data)) { mkdir data }
```

## 🚀 Como Executar

### Modo Local (API)
```bash
python main_api.py
```
Acesse o Swagger UI em: [http://localhost:8000/docs](http://localhost:8000/docs)

### Modo Local (Pipeline Prefect)
```bash
python flows/email_pipeline.py
```

### Modo Docker (API + Prometheus)
```bash
docker-compose up -d --build
```
- **API**: [http://localhost:8000](http://localhost:8000)
- **Prometheus**: [http://localhost:9090](http://localhost:9090)

## 📡 Endpoints Principais
- `POST /process-email`: Envia um e-mail para análise imediata pela IA.
- `GET /emails`: Lista todos os e-mails processados.
- `GET /emails/category/{category}`: Filtra e-mails por categoria.
- `GET /metrics`: Endpoint de métricas para o Prometheus.

## 📊 Observabilidade
Os logs são gerados em formato JSON no console para facilitar a integração com stacks de log (como ELK ou Loki). As métricas coletadas incluem tempo de resposta, total de requisições à IA e erros de processamento.

---
Desenvolvido como um projeto de portfólio técnico profissional.

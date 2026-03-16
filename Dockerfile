# LGPD Sentinel AI - Dockerfile
# Self-hosted gratuito com Python 3.11
# Sem necessidade de GPU - roda em qualquer máquina

FROM python:3.11-slim

# Metadados
LABEL maintainer="LGPD Sentinel AI"
LABEL description="Ferramenta open source para audits LGPD automatizados com IA"
LABEL version="0.1.0"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY . .

# Criar diretório para dados (volumes)
RUN mkdir -p /app/data /app/reports

# Expor porta da API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicialização
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

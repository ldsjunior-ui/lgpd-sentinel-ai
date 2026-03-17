#!/bin/bash
# LGPD Sentinel AI — Script de inicialização local
# Sobe Ollama, API e Frontend com um comando

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[LGPD Sentinel]${NC} $1"; }
warn() { echo -e "${YELLOW}[LGPD Sentinel]${NC} $1"; }
err()  { echo -e "${RED}[LGPD Sentinel]${NC} $1"; }

# ── Verificar .env ────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    warn ".env não encontrado — copiando .env.example"
    cp .env.example .env
fi

# ── Verificar venv ────────────────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
    log "Criando ambiente virtual..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt -q
    .venv/bin/pip install streamlit httpx -q
fi

# ── Ollama ────────────────────────────────────────────────────────────────────
if command -v ollama &>/dev/null; then
    if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
        log "Iniciando Ollama..."
        ollama serve > /tmp/lgpd-ollama.log 2>&1 &
        sleep 3
    else
        log "Ollama já está rodando."
    fi

    # Verificar modelo
    MODEL=$(grep OLLAMA_MODEL .env | cut -d= -f2 | tr -d ' ' || echo "llama3.1:8b")
    if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
        log "Baixando modelo $MODEL (pode demorar)..."
        ollama pull "$MODEL"
    else
        log "Modelo $MODEL disponível."
    fi
else
    warn "Ollama não encontrado. Endpoints de IA não funcionarão."
    warn "Instale em: https://ollama.ai"
fi

# ── API ───────────────────────────────────────────────────────────────────────
if lsof -Pi :8000 -sTCP:LISTEN -t &>/dev/null; then
    warn "Porta 8000 já em uso — API pode já estar rodando."
else
    log "Iniciando API FastAPI na porta 8000..."
    PYTHONPATH="$PROJECT_DIR" .venv/bin/uvicorn src.main:app --port 8000 \
        > /tmp/lgpd-api.log 2>&1 &
    sleep 3
fi

# ── Frontend ──────────────────────────────────────────────────────────────────
if lsof -Pi :8501 -sTCP:LISTEN -t &>/dev/null; then
    warn "Porta 8501 já em uso — Frontend pode já estar rodando."
else
    log "Iniciando Frontend Streamlit na porta 8501..."
    .venv/bin/streamlit run frontend/app.py \
        --server.port 8501 \
        --server.headless true \
        > /tmp/lgpd-frontend.log 2>&1 &
    sleep 3
fi

# ── Health check ──────────────────────────────────────────────────────────────
echo ""
log "Verificando serviços..."

API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
FE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 2>/dev/null || echo "000")

if [ "$API_STATUS" = "200" ]; then
    log "✅ API:      http://localhost:8000"
    log "✅ Swagger:  http://localhost:8000/docs"
else
    err "❌ API não respondeu (status $API_STATUS). Verifique: tail -f /tmp/lgpd-api.log"
fi

if [ "$FE_STATUS" = "200" ]; then
    log "✅ Frontend: http://localhost:8501"
else
    err "❌ Frontend não respondeu (status $FE_STATUS). Verifique: tail -f /tmp/lgpd-frontend.log"
fi

echo ""
log "Para parar os serviços: pkill -f 'uvicorn src.main' && pkill -f 'streamlit run'"
echo ""

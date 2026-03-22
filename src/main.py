# LGPD Sentinel AI - Entry Point Principal
# FastAPI app com endpoints de compliance LGPD
# 100% open source, Apache 2.0

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

from src.api.routes import billing, dpia, dsr, history, mapping, stats, usage_report
from src.core.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown da aplicação."""
    init_db()
    print("\n" + "=" * 60)
    print("🛡️  LGPD Sentinel AI v0.1.0 — Pronto para auditorias!")
    print("=" * 60)
    print("📖  Docs:        http://localhost:8000/docs")
    print("📱  Dashboard:   http://localhost:8000/dashboard")
    print("📊  Stats:       http://localhost:8000/api/v1/stats")
    print("💬  Comunidade:  https://github.com/ldsjunior-ui/lgpd-sentinel-ai/discussions")
    print("⭐  GitHub:      https://github.com/ldsjunior-ui/lgpd-sentinel-ai")
    print("=" * 60 + "\n")
    yield


# Metadados da API
app = FastAPI(
    lifespan=lifespan,
    title="LGPD Sentinel AI",
    description="""
    Ferramenta 100% open source para audits automatizados de conformidade LGPD (Lei Geral de Proteção de Dados).

    ## Features
    - 📊 **Data Mapping**: Identificação automática de dados pessoais com IA
    - 🔍 **DPIA**: Avaliação de Impacto à Proteção de Dados automatizada
    - 📝 **DSR**: Gerenciamento de solicitações de titulares de dados
    - 🛡️ **Risk Assessment**: Classificação de riscos (alto/médio/baixo)

    ## Stack
    - IA: LangChain + Ollama + Mistral (gratuito e local)
    - DB: Supabase (free tier)
    - Hosting: Self-hosted via Docker (grátis) ou managed cloud pago

    Apache 2.0 License - Zero risco jurídico
    """,
    version="0.1.0",
    contact={
        "name": "LGPD Sentinel AI",
        "url": "https://github.com/ldsjunior-ui/lgpd-sentinel-ai",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0",
    },
)

# Configurar CORS para permitir frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínio do frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["Sistema"])
async def health_check():
    """Verifica se a API está funcionando corretamente."""
    return {
        "status": "healthy",
        "service": "LGPD Sentinel AI",
        "version": "0.1.0",
        "license": "Apache 2.0",
        "github": "https://github.com/ldsjunior-ui/lgpd-sentinel-ai"
    }

# Rota raiz com info do projeto
@app.get("/", tags=["Sistema"])
async def root():
    """Informações gerais da API."""
    return {
        "name": "LGPD Sentinel AI",
        "description": "Audits LGPD automatizados com IA open source",
        "docs": "/docs",
        "health": "/health",
        "version": "0.1.0"
    }


_DASHBOARD_HTML = Path(__file__).parent.parent / "frontend" / "dashboard.html"


@app.get("/dashboard", response_class=HTMLResponse, tags=["Sistema"])
async def dashboard():
    """Dashboard mobile-friendly de uso e adoção."""
    return HTMLResponse(content=_DASHBOARD_HTML.read_text(encoding="utf-8"))


app.include_router(mapping.router, prefix="/api/v1", tags=["Data Mapping"])
app.include_router(dpia.router, prefix="/api/v1", tags=["DPIA"])
app.include_router(history.router, prefix="/api/v1", tags=["Histórico"])
app.include_router(dsr.router, prefix="/api/v1", tags=["DSR"])
app.include_router(billing.router, prefix="/api/v1", tags=["Billing / Planos"])
app.include_router(stats.router, prefix="/api/v1", tags=["Sistema"])
app.include_router(usage_report.router, prefix="/api/v1", tags=["Sistema"])

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

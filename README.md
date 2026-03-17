[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)

```
 _     _____ _____  ____     _____            _   _             _
| |   / ____| __ \|  _ \   / ____|          | | (_)           | |
| |  | |  __| |__) | | | | | (___   ___ _ __ | |_ _ _ __   ___| |
| |  | | |_ |  ___/| | | |  \___ \ / _ \ '_ \| __| | '_ \ / _ \ |
| |__| |__| | |    | |__| |  ____) |  __/ | | | |_| | | | |  __/ |
|_____\_____|_|    |_____/  |_____/ \___|_| |_|\__|_|_| |_|\___|_|

        AI para Compliance LGPD — 100% Open Source
```

# LGPD Sentinel AI

Ferramenta **100% open source** para automatizar auditorias de conformidade com a **LGPD (Lei 13.709/2018)** usando **IA local** — nenhum dado sai do seu servidor, zero custo de API.

---

## ✨ Funcionalidades

| Feature | Descrição | Artigo LGPD |
|---|---|---|
| 📊 **Data Mapping** | Classifica dados pessoais por categoria, base legal e nível de risco | Art. 5, 7, 11 |
| 🔍 **DPIA / RIPD** | Gera Relatório de Impacto completo com exportação em PDF | Art. 38 |
| 📝 **DSR** | Analisa solicitações de direitos do titular (acesso, exclusão, portabilidade...) | Art. 18 |
| 📂 **Histórico** | Salva todas as auditorias em banco local SQLite | — |
| 🌐 **Interface Web** | Frontend Streamlit com 5 abas, pronto para uso imediato | — |

---

## 🚀 Início Rápido

### Opção 1 — Docker Compose (recomendado)

```bash
git clone https://github.com/ldsjunior-ui/lgpd-sentinel-ai.git
cd lgpd-sentinel-ai
cp .env.example .env
docker compose up
```

- API: http://localhost:8000/docs
- Frontend: http://localhost:8501

### Opção 2 — Local com Ollama

**Pré-requisitos:** Python 3.11+, [Ollama](https://ollama.ai)

```bash
git clone https://github.com/ldsjunior-ui/lgpd-sentinel-ai.git
cd lgpd-sentinel-ai

# Instalar dependências
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env
# Edite .env: defina OLLAMA_MODEL=llama3.1:8b (ou mistral)

# Baixar modelo de IA
ollama pull llama3.1:8b

# Subir tudo
./start.sh
```

### Opção 3 — Script único

```bash
chmod +x start.sh && ./start.sh
```

---

## 🔌 Endpoints da API

```
GET  /health                      — Status da API
GET  /docs                        — Swagger UI interativo

POST /api/v1/map-data             — Mapeamento de dados pessoais
POST /api/v1/map-data/upload      — Upload CSV para análise

POST /api/v1/dpia/generate        — Gerar RIPD (JSON)
POST /api/v1/dpia/generate/pdf    — Gerar RIPD (PDF download)
POST /api/v1/dpia/risk-assessment — Avaliação rápida de risco

POST /api/v1/dsr/analyze          — Analisar solicitação de direito do titular
GET  /api/v1/dsr/types            — Listar tipos de direitos (Art. 18)

GET  /api/v1/history/mapping      — Histórico de auditorias de mapeamento
GET  /api/v1/history/mapping/{id} — Detalhes de uma auditoria
GET  /api/v1/history/dpia         — Histórico de DPIAs
GET  /api/v1/history/dpia/{id}    — Detalhes de um DPIA
```

---

## 🛠️ Stack

| Camada | Tecnologia | Custo |
|---|---|---|
| Backend | Python 3.11 + FastAPI | Gratuito |
| IA | LangChain + Ollama (llama3.1 / Mistral) | Gratuito |
| Frontend | Streamlit | Gratuito |
| Banco | SQLite (stdlib) | Gratuito |
| PDF | ReportLab | Gratuito |
| Deploy | Docker Compose | Gratuito |

> **Zero dependência de API externa.** Tudo roda localmente.

---

## ⚙️ Configuração (`.env`)

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b        # ou mistral, llama3:8b
LLM_TEMPERATURE=0.1
DEBUG=false
LOG_LEVEL=INFO
```

---

## 🧪 Testes

```bash
pytest tests/ -v
# 8 passed
```

---

## 🗺️ Roadmap

- [x] Core API (FastAPI + LangChain + Ollama)
- [x] Data Mapping endpoint
- [x] DPIA/RIPD com exportação PDF
- [x] DSR — Direitos do Titular (Art. 18)
- [x] Histórico de auditorias (SQLite)
- [x] Frontend Streamlit (5 abas)
- [x] Docker Compose
- [ ] Autenticação JWT (multi-tenant)
- [ ] Dashboard analytics
- [ ] Suporte a GDPR (europeu)
- [ ] Plano freemium via Stripe

---

## 🤝 Como Contribuir

Confira [CONTRIBUTING.md](./CONTRIBUTING.md). PRs são bem-vindas!

Issues e sugestões: [github.com/ldsjunior-ui/lgpd-sentinel-ai/issues](https://github.com/ldsjunior-ui/lgpd-sentinel-ai/issues)

---

## 📄 Licença

**Apache License 2.0** — use, modifique e distribua livremente.
Veja [LICENSE](./LICENSE) para detalhes.

---

<p align="center">Feito com ❤️ no Brasil 🇧🇷</p>

<div align="center">

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/tests-29%20passed-brightgreen.svg)](./tests/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Product Hunt](https://img.shields.io/badge/Product%20Hunt-Featured-orange.svg)](https://www.producthunt.com/posts/lgpd-sentinel-ai)
[![GitHub Stars](https://img.shields.io/github/stars/ldsjunior-ui/lgpd-sentinel-ai?style=social)](https://github.com/ldsjunior-ui/lgpd-sentinel-ai/stargazers)

# LGPD Sentinel AI 🛡️

> **Auditorias LGPD automatizadas com IA local — nenhum dado sai do seu servidor.**

**Se este projeto te ajuda ou te parece útil, uma ⭐ faz enorme diferença para o alcance do projeto!**
[![Star no GitHub](https://img.shields.io/badge/⭐%20Dar%20uma%20star-ldsjunior--ui%2Flgpd--sentinel--ai-yellow?style=for-the-badge&logo=github)](https://github.com/ldsjunior-ui/lgpd-sentinel-ai/stargazers)

</div>


---

## Building AI course project

This repository is my **Building AI course project** for the Elements of AI course.

## Summary

LGPD Sentinel AI helps Brazilian organizations identify personal-data risks, draft compliance documents, and handle data-subject requests. It can use local AI to reduce repetitive analysis while keeping sensitive data under the user's control.

## Background

Brazilian organizations must understand what personal data they collect, why it is processed, how it is protected, and how requests from data subjects should be handled.

For small and medium-sized organizations, this work is often manual, repetitive, expensive, and dependent on specialized legal knowledge. Incomplete data inventories and inconsistent documentation can also create compliance and security risks.

I created LGPD Sentinel AI to explore how artificial intelligence can support privacy professionals, developers, and small businesses with the operational parts of LGPD compliance. The project combines my experience in law and software development.

The problem is important because organizations process personal data every day, while mistakes can affect the privacy and rights of employees, customers, and other individuals.

## Data and AI techniques

The system works with information supplied by the organization, including:

* Categories of personal and sensitive data
* Purpose and legal basis of processing
* Retention periods and security measures
* Descriptions of internal processing activities
* Requests submitted by data subjects

The current implementation uses natural language processing with large language models orchestrated through LangChain. The self-hosted workflow can run models locally through Ollama. AI is used to classify information, identify possible risks, draft compliance documents, and analyze data-subject requests. Structured application logic handles validation, history, API access, and PDF generation.

The project does not train a model on personal data. Its results depend on the quality and completeness of the information supplied by the user. Legal knowledge should be checked against authoritative sources, especially the [Brazilian General Data Protection Law](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm) and [guidance published by the ANPD](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes).

## How is it used?

A privacy professional, lawyer, compliance analyst, consultant, or developer enters information about an organization's data-processing activities. The system can then help the user:

1. Map and classify personal data.
2. Identify possible privacy and compliance risks.
3. Draft a DPIA/RIPD document.
4. Analyze a data-subject request.
5. Export reports for review and record keeping.

The primary users are professionals responsible for privacy and compliance. The people affected also include employees, customers, and other data subjects whose information appears in the analyzed processes.

The generated results are decision-support material. A qualified human must review them before they are used in legal, compliance, or operational decisions.

## Challenges

LGPD Sentinel AI does not replace a lawyer, DPO, or privacy specialist. Large language models may produce incorrect interpretations, outdated information, or confident statements without sufficient legal support. Incomplete input can also lead to incomplete recommendations.

Sensitive organizational information must be protected against unauthorized access. A production deployment therefore needs strong access controls, encryption, audit logs, data minimization, retention rules, and clear information about whether a local or cloud model is being used.

Human review, explainable outputs, source citations, and continuous evaluation are necessary to prevent false confidence and reduce legal and privacy risks.

## What next?

Future development may include:

* Retrieval-augmented generation using a versioned collection of official LGPD and ANPD documents
* Direct citations showing the source behind each recommendation
* Evaluation datasets reviewed by privacy professionals
* Hallucination, security, and adversarial testing
* Integrations with organizational systems
* Support for other privacy frameworks, such as GDPR
* Stronger multi-tenant access controls and audit trails

## Acknowledgments

This project was developed by Leonardo Bergonzi as an open-source experiment in practical AI-assisted privacy compliance.

The project is based on the Brazilian LGPD, guidance published by the ANPD, and open-source technologies including Python, FastAPI, Streamlit, LangChain, Ollama, ReportLab, and Docker.

The course project structure follows the [Elements of AI Building AI final project instructions](https://buildingai.elementsofai.com/Conclusion/your-ai-idea).

Project repository: https://github.com/ldsjunior-ui/lgpd-sentinel-ai

Substitua dias de trabalho manual por minutos. O LGPD Sentinel AI gera **Data Mapping**, **RIPD/DPIA**, analisa **direitos dos titulares** e exporta relatórios em PDF — tudo rodando com IA 100% local via Ollama.

**Ideal para:** DPOs, jurídico, compliance, consultorias e times de desenvolvimento.

---

## 🖥️ Download — App Desktop (Novo!)

> **Baixe, instale e use. Sem terminal, sem Docker, sem complicação.**

[![Download macOS](https://img.shields.io/badge/Download-macOS%20(Apple%20Silicon)-000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/ldsjunior-ui/lgpd-sentinel-ai/releases/download/v1.0.1/LGPD.Sentinel.AI_1.0.0_aarch64.dmg)
[![Download Windows](https://img.shields.io/badge/Download-Windows%20x64-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/ldsjunior-ui/lgpd-sentinel-ai/releases/download/v1.0.1/LGPD.Sentinel.AI_1.0.0_x64-setup.exe)
[![Download Linux](https://img.shields.io/badge/Download-Linux%20AppImage-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/ldsjunior-ui/lgpd-sentinel-ai/releases/download/v1.0.1/LGPD.Sentinel.AI_1.0.0_amd64.AppImage)

**Como instalar:**
- **macOS:** Baixe o `.dmg` > arraste para Aplicativos > Ajustes > Privacidade > "Abrir Mesmo Assim"
- **Windows:** Baixe o `.exe` > execute o instalador > abra pelo Menu Iniciar
- **Linux:** Baixe o `.AppImage` > `chmod +x` > execute

**Requisitos:** macOS 10.15+ (Apple Silicon) · [Ollama](https://ollama.com) instalado · Python 3.11+

**8 análises gratuitas por dia. Sem cadastro. Sem cartão de crédito.**

---

## 📸 Screenshots

<div align="center">

| Mapeamento de Dados | DPIA / Relatório de Impacto |
|:---:|:---:|
| ![Mapeamento](docs/screenshots/01_mapping.png) | ![DPIA](docs/screenshots/02_dpia.png) |

| Direitos do Titular (DSR) | Sobre a LGPD |
|:---:|:---:|
| ![DSR](docs/screenshots/03_dsr.png) | ![Sobre](docs/screenshots/04_about.png) |

</div>

---

## ⚡ O que ele faz em 60 segundos

```bash
docker compose up        # sobe API + IA (alternativa ao app desktop)
# acesse http://localhost:8501
```

1. Cole seus dados → recebe classificação LGPD + base legal
2. Descreva um tratamento → recebe RIPD completo em PDF
3. Recebe solicitação de titular → recebe resposta pronta (Art. 18)

---

## ✨ Funcionalidades

| Feature | O que entrega | Artigo LGPD |
|---|---|---|
| 📊 **Data Mapping** | Classifica dados pessoais/sensíveis, sugere base legal, score de conformidade 0-100 | Art. 5, 7, 11 |
| 🔍 **DPIA / RIPD** | Relatório de Impacto completo com riscos, medidas de mitigação e PDF pronto para ANPD | Art. 38 |
| 📝 **DSR** | Analisa os 8 direitos do titular (acesso, exclusão, portabilidade…) e gera resposta oficial | Art. 18 |
| 📂 **Histórico** | Todas as auditorias salvas localmente com filtros, gráficos e exportação | — |
| 🌐 **Interface Web** | Dashboard Streamlit com 5 abas, pronto para uso imediato | — |
| 🔑 **API REST** | Integre no seu sistema via API com autenticação por API key | — |

---

## 💰 Planos

> **🎁 Toda nova API key inclui 7 dias de acesso Pro gratuito — sem cartão de crédito.**

| | **Free** | **Trial (7 dias)** | **Pro — R$97/mês** |
|---|---|---|---|
| Mapeamentos/mês | 5 | Ilimitado | Ilimitado |
| DPIAs/mês | 2 | Ilimitado | Ilimitado |
| DSRs/mês | 10 | Ilimitado | Ilimitado |
| Exportação PDF | ✅ | ✅ | ✅ |
| IA local (Ollama) | ✅ | ✅ | ✅ |
| Histórico completo | ✅ | ✅ | ✅ |
| Suporte prioritário | ❌ | ❌ | ✅ |

**[→ Gerar API key + trial grátis](https://github.com/ldsjunior-ui/lgpd-sentinel-ai#início-rápido)** · **[→ Upgrade Pro](https://github.com/ldsjunior-ui/lgpd-sentinel-ai)**

> A ANPD pode aplicar multas de até **R$ 50 milhões** por infração. Uma auditoria de conformidade com consultoria custa em média **R$ 8.000–R$ 30.000**. O LGPD Sentinel AI automatiza isso por R$97/mês.

---

## 🚀 Início Rápido

### Opção 1 — Docker Compose (recomendado, 3 comandos)

```bash
git clone https://github.com/ldsjunior-ui/lgpd-sentinel-ai.git
cd lgpd-sentinel-ai
cp .env.example .env
docker compose up
```

- 🌐 **Frontend:** http://localhost:8501
- 📖 **API Docs:** http://localhost:8000/docs

### Opção 2 — Local com Ollama

**Pré-requisitos:** Python 3.11+, [Ollama](https://ollama.ai)

```bash
git clone https://github.com/ldsjunior-ui/lgpd-sentinel-ai.git
cd lgpd-sentinel-ai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
ollama pull llama3.1:8b
./start.sh
```

---

## 🔌 API

Gere uma API key gratuita e integre no seu sistema:

```bash
# 1. Gerar API key
curl -X POST http://localhost:8000/api/v1/billing/keys \
  -H "Content-Type: application/json" \
  -d '{"email": "seu@email.com"}'

# 2. Usar nos endpoints
curl -X POST http://localhost:8000/api/v1/map-data \
  -H "X-API-Key: lgpd_sua_key" \
  -H "Content-Type: application/json" \
  -d '{"data": [{"key": "cpf", "value": "123.456.789-00"}]}'
```

**Endpoints principais:**

```
POST /api/v1/map-data             — Mapeamento de dados pessoais
POST /api/v1/map-data/upload      — Upload CSV/JSON para análise

POST /api/v1/dpia/generate        — Gerar RIPD completo (JSON)
POST /api/v1/dpia/generate/pdf    — Gerar RIPD (PDF download)

POST /api/v1/dsr/analyze          — Analisar solicitação de titular (Art. 18)

GET  /api/v1/billing/keys         — Gerar API key gratuita
GET  /api/v1/billing/status       — Ver uso e plano atual
POST /api/v1/billing/checkout     — Upgrade para Pro (Stripe)
```

---

## 🛠️ Stack — 100% gratuita e open source

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11 + FastAPI |
| IA | LangChain + Ollama (llama3.1:8b / Mistral) |
| Frontend | Streamlit |
| Banco | SQLite (zero configuração) |
| PDF | ReportLab |
| Pagamentos | Stripe (plano Pro) |
| Deploy | Docker Compose |

> **Zero dependência de API externa.** A IA roda localmente — seus dados nunca saem do seu servidor.

---

## 🧪 Testes

```bash
pytest tests/ -v
# 29 passed
```

---

## 🗺️ Roadmap

- [x] Core API (FastAPI + LangChain + Ollama)
- [x] Data Mapping com score de conformidade
- [x] DPIA/RIPD com exportação PDF
- [x] DSR — Direitos do Titular (Art. 18)
- [x] Histórico com gráficos e filtros
- [x] Frontend Streamlit (5 abas)
- [x] Docker Compose
- [x] Freemium com API keys + Stripe Pro (R$97/mês)
- [x] Quota enforcement por plano
- [ ] Autenticação JWT (multi-tenant)
- [ ] Notificações por email (quota, relatórios)
- [ ] Suporte a GDPR (europeu)
- [ ] Deploy one-click Railway / Render

---

## 🤝 Como Contribuir

PRs são muito bem-vindas! Veja [CONTRIBUTING.md](./CONTRIBUTING.md).

Issues e sugestões: [github.com/ldsjunior-ui/lgpd-sentinel-ai/issues](https://github.com/ldsjunior-ui/lgpd-sentinel-ai/issues)

---

## 📄 Licença

**Apache License 2.0** — use, modifique e distribua livremente, inclusive em produtos comerciais.

---

<p align="center">
  <strong>LGPD Sentinel AI — Compliance automatizado, dados protegidos, empresa segura.</strong><br/>
  Feito com ❤️ no Brasil 🇧🇷
</p>

---

<div align="center">

### Gostou do projeto? Uma ⭐ ajuda a chegar em mais DPOs e times de compliance!

[![Star no GitHub](https://img.shields.io/badge/⭐%20Dar%20uma%20star-yellow?style=for-the-badge&logo=github)](https://github.com/ldsjunior-ui/lgpd-sentinel-ai/stargazers)
[![Sponsor](https://img.shields.io/badge/💙%20Sponsor-GitHub%20Sponsors-ea4aaa?style=for-the-badge&logo=github-sponsors)](https://github.com/sponsors/ldsjunior-ui)
[![Discussions](https://img.shields.io/badge/💬%20Discussões-GitHub-blue?style=for-the-badge&logo=github)](https://github.com/ldsjunior-ui/lgpd-sentinel-ai/discussions)

</div>

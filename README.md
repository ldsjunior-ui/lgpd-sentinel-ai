[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

```
 _     _____ _____  _____     _____         _   _   _____ _     _____
| |   | __ \  __ \| __ \   / ____|       | | | | / ____| |   |_   _|
| |   | |__) | |  | | |  | | |             | | | || |    | |     | |
| |   |  ___/| |  | | |  | | |      _____  | | | || |    | |     | |
| |___| |    | |__| | |__| | |____          | |_| || |____| |___ _| |_
|_____|_|    |_____/|_____/ \_____|          \___/  \_____|______|_____|

        AI para Compliance LGPD - Open Source e Poderoso
```

# LGPD Sentinel AI

## Descrição / Description

**Português:** LGPD Sentinel AI é uma ferramenta **100% open source** para automação de audits de conformidade com a LGPD (Lei Geral de Proteção de Dados) usando IA. Inclui mapeamento de dados, DPIAs, gerenciamento de DSARs e avaliações de risco. Rode self-hosted **gratuitamente** ou use nossa versão managed cloud paga para conveniência e suporte enterprise. Licença Apache 2.0 — zero risco jurídico, comunidade-driven.

**English:** LGPD Sentinel AI is a **100% open source** tool for automating LGPD (Brazil's General Data Protection Law) compliance audits with AI. Features include data mapping, DPIAs, DSAR handling, and risk assessments. Run self-hosted for free or use our paid managed cloud for convenience and enterprise support. Apache 2.0 license — zero legal risk, community-driven.

---

## ✨ Features

- 📊 **Mapeamento de Dados Automatizado** — Identifique dados pessoais e sensíveis com IA open source (Mistral/Ollama via Hugging Face, free)
- 🔍 **DPIA e Avaliação de Riscos** — Gere relatórios de impacto e riscos conforme guidelines da ANPD
- 📝 **Gerenciamento de DSARs** — Automatize solicitações de titulares de dados (Data Subject Access Requests)
- 🛡️ **Privacidade Edge Computing** — Rode localmente para máxima privacidade, sem lock-in
- ☁️ **Opção Managed Cloud** — Hosting pago com escalabilidade, backups e suporte (fature em USD)
- 🌐 **Integrações BR-First** — Suporte nativo a APIs ANPD, Pix e sistemas fiscais brasileiros

---

## 🚀 Instalação Self-Hosted (100% Gratuito)

Pré-requisitos: [Docker](https://www.docker.com/) (free)

```bash
# 1. Clone o repositório
git clone https://github.com/ldsjunior-ui/lgpd-sentinel-ai.git
cd lgpd-sentinel-ai

# 2. Build e rode o container
docker build -t lgpd-sentinel-ai .
docker run -p 8000:8000 -v $(pwd)/data:/app/data lgpd-sentinel-ai

# 3. Acesse no browser
# http://localhost:8000
```

> **Modelos de IA:** Baixe gratuitamente do [Hugging Face](https://huggingface.co/). Recomendamos Mistral-7B para audits LGPD.

---

## 🗺️ Roadmap

- [ ] **MVP v0.1** — Core data mapping e DPIA _(em progresso)_
- [ ] **v0.2** — Integração com Supabase free DB e frontend React
- [ ] **v0.3** — Suporte a DSARs e relatórios exportáveis em PDF
- [ ] **v1.0** — Lançamento completo com marketplace de templates
- [ ] **Enterprise** — Managed cloud tiers e consultoria paga (USD)

---

## 🤝 Como Contribuir

Quer ajudar a construir essa ferramenta visionária? Confira nosso [CONTRIBUTING.md](./CONTRIBUTING.md) para guidelines e CLA simples.

Pull Requests são bem-vindos — foque em [issues abertos](https://github.com/ldsjunior-ui/lgpd-sentinel-ai/issues) para tração comunitária gratuita!

---

## 🛠️ Stack

| Camada | Tecnologia | Custo |
|---|---|---|
| Backend | Python + FastAPI | Gratuito |
| IA | LangChain + Ollama + Mistral (Hugging Face) | Gratuito |
| Banco de Dados | Supabase (PostgreSQL) | Free tier |
| Frontend | React OSS | Gratuito |
| Hosting | Vercel / Railway | Free tier |
| CDN | Cloudflare | Gratuito |
| Self-hosted | Docker + Kubernetes | Gratuito |

> Tudo 100% gratuito para desenvolvimento inicial — monetize com services pagos (managed cloud, enterprise support, consultoria).

---

## 📄 Licença

Este projeto é licenciado sob a **Apache License 2.0** — veja o arquivo [LICENSE](./LICENSE) para detalhes.

Sem riscos jurídicos: código aberto, contribuições com CLA, conformidade total com LGPD e EU regulations.

---

<p align="center">Feito com ❤️ no Brasil 🇧🇷 | Built with ❤️ in Brazil</p>

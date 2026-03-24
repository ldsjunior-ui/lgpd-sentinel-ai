# Changelog

Todas as mudanças relevantes do projeto são documentadas aqui.

## [1.0.0] — 2026-03-24

### Adicionado
- App desktop standalone via Tauri v2 (macOS .dmg, Windows .msi, Linux .AppImage)
- Auto-start do backend FastAPI e Ollama ao abrir o app
- Mapeamento de Dados com classificação por IA local (Mistral/Llama3.1)
- DPIA — Relatório de Impacto à Proteção de Dados com geração de PDF
- DSR — Análise de Solicitações de Direitos do Titular (Art. 18 LGPD)
- Histórico de análises com gráficos de evolução
- Sistema de API Keys com plano trial de 7 dias
- Disclaimer legal em todas as telas de resultado
- Botão "Limpar Dados" para governança do usuário
- Transparência sobre local de armazenamento no app
- Canal YouTube @lgpdsentinelai com 5 shorts + 3 podcasts
- Landing page em ldsjunior-ui.github.io/lgpd-sentinel-landing

### Segurança
- Backend bind restrito a 127.0.0.1 (não expõe na rede)
- CORS restrito a localhost (era wildcard "*")
- Billing e SMTP documentados como features futuras, não ativos no modo local
- Nenhum dado sai da máquina do usuário — processamento 100% local

### Limitações Conhecidas
- App macOS não é assinado com Apple Developer ID (requer bypass do Gatekeeper)
- Scores e classificações são gerados por IA e têm caráter indicativo — devem ser validados por profissional qualificado
- A ferramenta apoia análise e organização, mas NÃO substitui avaliação jurídica humana
- Velocidade de análise depende do hardware do usuário (CPU/GPU para Ollama)
- Histórico de análises é armazenado localmente em SQLite sem criptografia

### Requisitos
- macOS 10.15+ (Apple Silicon), Windows 10+, ou Linux
- Ollama instalado com modelo `mistral` ou `llama3.1`
- Python 3.11+ (instalado automaticamente pelo app no primeiro uso)

## [0.1.0] — 2026-03-15

### Adicionado
- API FastAPI com endpoints de mapeamento, DPIA e DSR
- Integração com Ollama para inferência local
- Frontend Streamlit (versão web)
- Docker Compose para deploy simplificado
- Testes automatizados com pytest
- CI/CD via GitHub Actions

"""
LGPD Sentinel AI — Interface Web (Streamlit)
Frontend visual para auditorias LGPD automatizadas
"""

import streamlit as st
import httpx
import json
from datetime import datetime

# ─── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="LGPD Sentinel AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:8000/api/v1"

# ─── Estilos ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .risk-alto    { background: #ff4b4b22; border-left: 4px solid #ff4b4b; padding: 0.5rem 1rem; border-radius: 4px; }
    .risk-medio   { background: #ffa50022; border-left: 4px solid #ffa500; padding: 0.5rem 1rem; border-radius: 4px; }
    .risk-baixo   { background: #00c85322; border-left: 4px solid #00c853; padding: 0.5rem 1rem; border-radius: 4px; }
    .metric-card  { background: #f0f2f6; border-radius: 8px; padding: 1rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🛡️ LGPD Sentinel AI</h1>
    <p>Auditorias de conformidade LGPD automatizadas com IA local • Open Source • Apache 2.0</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/LGPD-Sentinel%20AI-blue?style=for-the-badge&logo=shield")
    st.markdown("---")
    st.markdown("### ⚙️ Configuração")
    api_url = st.text_input("URL da API", value="http://localhost:8000")
    API_BASE = f"{api_url}/api/v1"

    st.markdown("---")

    # Status da API
    try:
        r = httpx.get(f"{api_url}/health", timeout=3)
        if r.status_code == 200:
            st.success("✅ API Online")
            data = r.json()
            st.caption(f"v{data.get('version', '?')}")
        else:
            st.error("❌ API com erro")
    except Exception:
        st.warning("⚠️ API offline — inicie com:\n```\nuvicorn src.main:app --reload\n```")

    st.markdown("---")
    st.markdown("### 📚 Links")
    st.markdown("[GitHub](https://github.com/ldsjunior-ui/lgpd-sentinel-ai) | [Docs](/docs)")

# ─── Abas principais ──────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Mapeamento de Dados",
    "🔍 DPIA / Avaliação de Impacto",
    "📝 Direitos do Titular (DSR)",
    "📂 Histórico",
    "📋 Sobre a LGPD"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAPEAMENTO DE DADOS
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("📊 Mapeamento de Dados Pessoais")
    st.markdown(
        "Analise quais dados pessoais sua empresa coleta, processa e armazena, "
        "identificando riscos e obrigações sob a LGPD."
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Dados para análise")
        company = st.text_input("Nome da empresa", placeholder="Acme Ltda")
        purpose = st.text_area(
            "Finalidade do tratamento",
            placeholder="Ex: Gestão de clientes, marketing, RH...",
            height=80,
        )
        st.markdown("**Itens de dados coletados**")

        # Itens dinâmicos
        if "items" not in st.session_state:
            st.session_state.items = [{"name": "", "description": "", "source": ""}]

        for i, item in enumerate(st.session_state.items):
            with st.expander(f"Item {i+1}: {item['name'] or 'Novo item'}", expanded=(i == 0)):
                c1, c2, c3 = st.columns(3)
                st.session_state.items[i]["name"] = c1.text_input(
                    "Nome do campo", value=item["name"], key=f"name_{i}",
                    placeholder="ex: email"
                )
                st.session_state.items[i]["description"] = c2.text_input(
                    "Descrição", value=item["description"], key=f"desc_{i}",
                    placeholder="ex: e-mail do cliente"
                )
                st.session_state.items[i]["source"] = c3.text_input(
                    "Origem", value=item["source"], key=f"src_{i}",
                    placeholder="ex: formulário de cadastro"
                )
                if i > 0 and st.button("🗑️ Remover", key=f"rem_{i}"):
                    st.session_state.items.pop(i)
                    st.rerun()

        if st.button("➕ Adicionar item"):
            st.session_state.items.append({"name": "", "description": "", "source": ""})
            st.rerun()

    with col2:
        st.subheader("🔎 Resultado da análise")

        if st.button("🚀 Analisar Dados", type="primary", use_container_width=True):
            items_validos = [i for i in st.session_state.items if i["name"].strip()]
            if not items_validos:
                st.error("Adicione pelo menos um item de dado.")
            else:
                payload = {
                    "company_name": company or "Empresa não informada",
                    "purpose": purpose or "Não especificada",
                    "data_items": [
                        {
                            "name": i["name"],
                            "description": i["description"],
                            "source": i["source"],
                        }
                        for i in items_validos
                    ],
                }
                with st.spinner("🤖 Analisando com IA local (Mistral)..."):
                    try:
                        resp = httpx.post(
                            f"{API_BASE}/mapping",
                            json=payload,
                            timeout=120,
                        )
                        if resp.status_code == 200:
                            result = resp.json()
                            st.session_state["mapping_result"] = result
                            st.success("✅ Análise concluída!")
                        else:
                            st.error(f"Erro {resp.status_code}: {resp.text}")
                    except httpx.ConnectError:
                        st.error("❌ Não foi possível conectar à API. Verifique se está rodando.")
                    except Exception as e:
                        st.error(f"Erro inesperado: {e}")

        # Exibir resultado
        if "mapping_result" in st.session_state:
            r = st.session_state["mapping_result"]

            # Métricas
            m1, m2, m3 = st.columns(3)
            m1.metric("📦 Itens analisados", r.get("total_items", 0))
            m2.metric("⚠️ Dados sensíveis", r.get("sensitive_count", 0))
            risk = r.get("overall_risk", "N/A").upper()
            risk_emoji = {"ALTO": "🔴", "MÉDIO": "🟡", "BAIXO": "🟢"}.get(risk, "⚪")
            m3.metric(f"{risk_emoji} Risco geral", risk)

            st.markdown("---")

            # Recomendações
            if r.get("recommendations"):
                st.markdown("### 💡 Recomendações")
                for rec in r["recommendations"]:
                    st.markdown(f"- {rec}")

            # Detalhes por item
            if r.get("items"):
                st.markdown("### 🗂️ Detalhes por item")
                for item in r["items"]:
                    risk_class = f"risk-{item.get('risk_level', 'baixo').lower()}"
                    st.markdown(
                        f'<div class="{risk_class}"><strong>{item["name"]}</strong> — '
                        f'Categoria: <em>{item.get("lgpd_category", "?")}</em> | '
                        f'Risco: <strong>{item.get("risk_level", "?").upper()}</strong></div>',
                        unsafe_allow_html=True,
                    )
                    if item.get("recommendations"):
                        for rec in item["recommendations"]:
                            st.caption(f"  → {rec}")

            # JSON raw
            with st.expander("🔧 Resposta JSON completa"):
                st.json(r)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DPIA
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("🔍 DPIA — Avaliação de Impacto à Proteção de Dados")
    st.markdown(
        "O DPIA (Data Protection Impact Assessment) é obrigatório pela LGPD para "
        "tratamentos de alto risco. Gere seu relatório automaticamente."
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Informações do processo")
        dpia_company  = st.text_input("Empresa", placeholder="Acme Ltda", key="dpia_company")
        dpia_process  = st.text_input("Nome do processo", placeholder="Ex: Sistema de RH", key="dpia_process")
        dpia_purpose  = st.text_area("Finalidade", placeholder="Ex: Gestão de folha de pagamento", height=80, key="dpia_purpose")
        dpia_data     = st.text_area(
            "Dados pessoais envolvidos",
            placeholder="Ex: nome, CPF, salário, dados bancários...",
            height=80, key="dpia_data"
        )
        dpia_measures = st.text_area(
            "Medidas de segurança existentes",
            placeholder="Ex: criptografia em repouso, acesso restrito, logs de auditoria...",
            height=80, key="dpia_measures"
        )

    with col2:
        st.subheader("📄 Relatório DPIA")

        if st.button("🚀 Gerar DPIA", type="primary", use_container_width=True):
            if not dpia_process or not dpia_purpose:
                st.error("Preencha pelo menos o processo e a finalidade.")
            else:
                payload = {
                    "company_name": dpia_company or "Empresa não informada",
                    "process_name": dpia_process,
                    "purpose": dpia_purpose,
                    "personal_data_involved": dpia_data,
                    "existing_measures": dpia_measures,
                }
                with st.spinner("🤖 Gerando DPIA com IA local (Mistral)..."):
                    try:
                        resp = httpx.post(
                            f"{API_BASE}/dpia",
                            json=payload,
                            timeout=120,
                        )
                        if resp.status_code == 200:
                            st.session_state["dpia_result"] = resp.json()
                            st.success("✅ DPIA gerado!")
                        else:
                            st.error(f"Erro {resp.status_code}: {resp.text}")
                    except httpx.ConnectError:
                        st.error("❌ Não foi possível conectar à API.")
                    except Exception as e:
                        st.error(f"Erro inesperado: {e}")

        if "dpia_result" in st.session_state:
            r = st.session_state["dpia_result"]

            risk = r.get("risk_level", "N/A").upper()
            risk_color = {"ALTO": "🔴", "MÉDIO": "🟡", "BAIXO": "🟢"}.get(risk, "⚪")
            st.metric(f"{risk_color} Nível de risco", risk)

            if r.get("risks_identified"):
                st.markdown("### ⚠️ Riscos identificados")
                for risk_item in r["risks_identified"]:
                    st.markdown(f"- {risk_item}")

            if r.get("mitigation_measures"):
                st.markdown("### 🛡️ Medidas de mitigação recomendadas")
                for measure in r["mitigation_measures"]:
                    st.markdown(f"- {measure}")

            if r.get("legal_basis"):
                st.markdown(f"**⚖️ Base legal sugerida:** {r['legal_basis']}")

            if r.get("dpo_required") is not None:
                dpo = "✅ Sim" if r["dpo_required"] else "❌ Não obrigatório"
                st.markdown(f"**👤 Encarregado (DPO) necessário:** {dpo}")

            # Download PDF button
            st.markdown("---")
            if st.button("📄 Baixar RIPD em PDF", use_container_width=True):
                with st.spinner("Gerando PDF..."):
                    try:
                        payload = {
                            "company_name": dpia_company or "Empresa não informada",
                            "treatment_description": dpia_purpose or dpia_process,
                            "data_types": [d.strip() for d in (dpia_data or "").split(",") if d.strip()],
                            "purposes": [dpia_purpose] if dpia_purpose else [],
                        }
                        pdf_resp = httpx.post(
                            f"{API_BASE}/dpia/generate/pdf",
                            json=payload,
                            timeout=120,
                        )
                        if pdf_resp.status_code == 200:
                            st.download_button(
                                label="⬇️ Clique para baixar o PDF",
                                data=pdf_resp.content,
                                file_name=f"RIPD_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                            )
                        else:
                            st.error(f"Erro ao gerar PDF: {pdf_resp.status_code}")
                    except Exception as e:
                        st.error(f"Erro: {e}")

            with st.expander("🔧 Resposta JSON completa"):
                st.json(r)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DSR (Direitos do Titular)
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("📝 Direitos do Titular — Art. 18 LGPD")
    st.markdown(
        "Analise solicitações de direitos de titulares de dados: acesso, correção, "
        "exclusão, portabilidade e outros. Gere orientações e a resposta formal ao titular."
    )

    # Buscar tipos disponíveis
    try:
        tipos_resp = httpx.get(f"{API_BASE}/dsr/types", timeout=5)
        tipos_data = tipos_resp.json() if tipos_resp.status_code == 200 else {}
        tipos_disponiveis = {d["type"]: d["descricao"] for d in tipos_data.get("direitos", [])}
    except Exception:
        tipos_disponiveis = {
            "acesso": "Confirmação e acesso aos dados tratados",
            "correcao": "Correção de dados incompletos ou inexatos",
            "exclusao": "Eliminação de dados desnecessários",
            "portabilidade": "Portabilidade dos dados",
            "oposicao": "Oposição ao tratamento",
            "revogacao_consentimento": "Revogação do consentimento",
            "restricao": "Restrição do tratamento",
            "informacao": "Informação sobre compartilhamento",
        }

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Dados da solicitação")
        dsr_company  = st.text_input("Empresa controladora", placeholder="Acme Ltda", key="dsr_company")
        dsr_titular  = st.text_input("Nome do titular (opcional)", placeholder="ex: Titular #1234", key="dsr_titular")
        dsr_type     = st.selectbox(
            "Tipo de direito solicitado",
            options=list(tipos_disponiveis.keys()),
            format_func=lambda x: f"{x.replace('_', ' ').title()} — {tipos_disponiveis.get(x, '')}",
            key="dsr_type",
        )
        dsr_desc     = st.text_area(
            "Descrição da solicitação",
            placeholder="Ex: Solicito acesso a todos os meus dados pessoais armazenados pela empresa...",
            height=100, key="dsr_desc",
        )
        dsr_context  = st.text_area(
            "Contexto dos dados (opcional)",
            placeholder="Ex: Dados cadastrais do sistema CRM, histórico de compras...",
            height=70, key="dsr_context",
        )

        st.info(f"⏱️ Prazo legal: **15 dias** (Art. 18, §5 LGPD)")

    with col2:
        st.subheader("📄 Análise e orientações")

        if st.button("🚀 Analisar Solicitação", type="primary", use_container_width=True):
            if not dsr_desc or len(dsr_desc) < 10:
                st.error("Descreva a solicitação com pelo menos 10 caracteres.")
            else:
                payload = {
                    "company_name": dsr_company or "Empresa não informada",
                    "request_type": dsr_type,
                    "request_description": dsr_desc,
                    "data_context": dsr_context or None,
                    "titular_name": dsr_titular or None,
                }
                with st.spinner("🤖 Analisando com IA local..."):
                    try:
                        resp = httpx.post(
                            f"{API_BASE}/dsr/analyze",
                            json=payload,
                            timeout=120,
                        )
                        if resp.status_code == 200:
                            st.session_state["dsr_result"] = resp.json()
                            st.success("✅ Análise concluída!")
                        else:
                            st.error(f"Erro {resp.status_code}: {resp.text}")
                    except httpx.ConnectError:
                        st.error("❌ API offline.")
                    except Exception as e:
                        st.error(f"Erro: {e}")

        if "dsr_result" in st.session_state:
            r = st.session_state["dsr_result"]

            # Status pode atender
            pode = r.get("pode_atender", True)
            if pode:
                st.success(f"✅ Solicitação pode ser **atendida**")
            else:
                st.error(f"❌ Solicitação **não pode ser atendida**")

            st.markdown(f"**Base legal:** {r.get('artigo_lgpd', 'N/A')}")
            st.markdown(f"**Justificativa:** {r.get('justificativa', '')}")
            st.markdown(f"**Prazo:** {r.get('prazo_resposta_dias', 15)} dias")

            # Flags importantes
            c1, c2 = st.columns(2)
            c1.metric("DPO necessário", "✅ Sim" if r.get("requer_dpo") else "❌ Não")
            c2.metric("Notificar ANPD", "✅ Sim" if r.get("requer_anpd") else "❌ Não")

            # Ações requeridas
            acoes = r.get("acoes_requeridas", [])
            if acoes:
                st.markdown("### 📋 Ações requeridas")
                for a in acoes:
                    prazo_label = a.get("prazo", "")
                    responsavel = a.get("responsavel", "")
                    st.markdown(
                        f"- **{a.get('acao', '')}**  \n"
                        f"  Responsável: `{responsavel}` | Prazo: `{prazo_label}`"
                    )

            # Resposta ao titular
            resposta = r.get("resposta_ao_titular", "")
            if resposta:
                st.markdown("### ✉️ Resposta ao titular")
                st.text_area(
                    "Texto pronto para envio:",
                    value=resposta,
                    height=160,
                    key="resposta_titular_text",
                )

            # Documentos necessários
            docs = r.get("documentacao_necessaria", [])
            if docs:
                st.markdown("### 🗂️ Documentação necessária")
                for d in docs:
                    st.markdown(f"- {d}")

            with st.expander("🔧 Resposta JSON completa"):
                st.json(r)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — HISTÓRICO
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.header("📂 Histórico de Auditorias")

    h_col1, h_col2 = st.columns(2)

    with h_col1:
        st.subheader("📊 Mapeamentos")
        if st.button("🔄 Atualizar", key="refresh_mapping"):
            st.session_state.pop("hist_mapping", None)

        if "hist_mapping" not in st.session_state:
            try:
                r = httpx.get(f"{API_BASE}/history/mapping", timeout=5)
                st.session_state["hist_mapping"] = r.json() if r.status_code == 200 else []
            except Exception:
                st.session_state["hist_mapping"] = []

        audits = st.session_state.get("hist_mapping", [])
        if not audits:
            st.info("Nenhuma auditoria de mapeamento encontrada.")
        else:
            for a in audits:
                with st.expander(f"#{a['id']} — {a.get('company', 'N/A')} ({a.get('created_at', '')[:10]})"):
                    st.write(f"**Contexto:** {a.get('context', 'N/A')}")
                    if st.button(f"Ver detalhes #{a['id']}", key=f"map_detail_{a['id']}"):
                        try:
                            dr = httpx.get(f"{API_BASE}/history/mapping/{a['id']}", timeout=5)
                            if dr.status_code == 200:
                                st.json(dr.json())
                        except Exception as e:
                            st.error(str(e))

    with h_col2:
        st.subheader("🔍 DPIAs")
        if st.button("🔄 Atualizar", key="refresh_dpia"):
            st.session_state.pop("hist_dpia", None)

        if "hist_dpia" not in st.session_state:
            try:
                r = httpx.get(f"{API_BASE}/history/dpia", timeout=5)
                st.session_state["hist_dpia"] = r.json() if r.status_code == 200 else []
            except Exception:
                st.session_state["hist_dpia"] = []

        dpia_audits = st.session_state.get("hist_dpia", [])
        if not dpia_audits:
            st.info("Nenhuma auditoria DPIA encontrada.")
        else:
            for a in dpia_audits:
                risk = a.get("risk_level", "N/A")
                risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk, "⚪")
                with st.expander(
                    f"#{a['id']} — {a.get('company', 'N/A')} {risk_emoji} ({a.get('created_at', '')[:10]})"
                ):
                    st.write(f"**Tratamento:** {a.get('treatment', 'N/A')}")
                    st.write(f"**Risco:** {risk.upper()} | **Conformidade:** {a.get('compliance_score', 0):.0f}/100")
                    if st.button(f"Ver detalhes #{a['id']}", key=f"dpia_detail_{a['id']}"):
                        try:
                            dr = httpx.get(f"{API_BASE}/history/dpia/{a['id']}", timeout=5)
                            if dr.status_code == 200:
                                st.json(dr.json())
                        except Exception as e:
                            st.error(str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SOBRE A LGPD
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.header("📋 Sobre a LGPD")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
### O que é a LGPD?
A **Lei Geral de Proteção de Dados (Lei 13.709/2018)** regula o tratamento de dados
pessoais no Brasil, inspirada na GDPR europeia.

### Principais obrigações
- 📌 Ter **base legal** para cada tratamento de dados
- 📌 Garantir os **direitos dos titulares** (acesso, correção, exclusão)
- 📌 Nomear um **Encarregado (DPO)** quando necessário
- 📌 Realizar **DPIA** para tratamentos de alto risco
- 📌 Notificar a **ANPD** em casos de incidentes
- 📌 Manter **registros de atividades** de tratamento
        """)

    with col2:
        st.markdown("""
### Bases legais (Art. 7º)
| Base | Descrição |
|------|-----------|
| Consentimento | Titular autorizou expressamente |
| Contrato | Necessário para executar contrato |
| Obrigação legal | Exigido por lei |
| Interesse legítimo | Uso necessário e proporcional |
| Proteção da vida | Situações de emergência |

### Dados sensíveis (Art. 11)
Origem racial, saúde, vida sexual, dados genéticos,
biometria, religião, opiniões políticas — **exigem
cuidados extras e base legal específica**.
        """)

    st.markdown("---")
    st.markdown(
        "**Disclaimer:** Esta ferramenta é open source e fornece orientações gerais. "
        "Para conformidade legal completa, consulte um advogado especializado em LGPD."
    )

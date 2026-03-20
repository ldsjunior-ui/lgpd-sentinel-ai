"""
LGPD Sentinel AI — Interface Web (Streamlit)
Frontend visual para auditorias LGPD automatizadas
"""

import streamlit as st
import streamlit.components.v1 as components
import httpx
import json
import pandas as pd
from datetime import datetime

# ─── Configuração da página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="LGPD Sentinel AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:8000/api/v1"

# ─── Matrix Rain Background ───────────────────────────────────────────────────
components.html("""
<script>
(function() {
  var parent = window.parent.document;
  if (parent.getElementById('lgpd-matrix-canvas')) return;

  var canvas = parent.createElement('canvas');
  canvas.id = 'lgpd-matrix-canvas';
  Object.assign(canvas.style, {
    position: 'fixed', top: '0', left: '0',
    width: '100%', height: '100%',
    pointerEvents: 'none', zIndex: '0', opacity: '0.13',
  });
  parent.body.appendChild(canvas);

  var ctx = canvas.getContext('2d');
  var fs = 13;
  var chars = 'アカサタナハマヤラワABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&';
  var cols, drops;

  function init() {
    canvas.width  = window.parent.innerWidth;
    canvas.height = window.parent.innerHeight;
    cols  = Math.floor(canvas.width / fs);
    drops = Array.from({length: cols}, function() { return Math.random() * -50; });
  }

  function draw() {
    ctx.fillStyle = 'rgba(0,0,0,0.04)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.font = fs + 'px monospace';
    for (var i = 0; i < drops.length; i++) {
      var c = chars[Math.floor(Math.random() * chars.length)];
      ctx.fillStyle = '#afffcf';
      ctx.fillText(c, i * fs, drops[i] * fs);
      ctx.fillStyle = '#00cc50';
      if (drops[i] * fs > canvas.height && Math.random() > 0.975) drops[i] = 0;
      drops[i] += 0.5;
    }
  }

  init();
  window.parent.addEventListener('resize', init);
  setInterval(draw, 45);
})();
</script>
""", height=0)

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

    # ── Plano & API Key ──────────────────────────────────────────────────
    st.markdown("### 🔑 Sua API Key")
    api_key_input = st.text_input(
        "API Key",
        value=st.session_state.get("api_key", ""),
        type="password",
        placeholder="lgpd_...",
        key="api_key_field",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input

    if st.button("Gerar key gratuita", use_container_width=True):
        try:
            r = httpx.post(f"{API_BASE}/billing/keys", json={}, timeout=5)
            if r.status_code == 200:
                new_key = r.json()["api_key"]
                st.session_state["api_key"] = new_key
                st.success("Key gerada!")
                st.code(new_key, language=None)
            else:
                st.error("Erro ao gerar key.")
        except Exception:
            st.error("API offline.")

    # Status do plano
    current_key = st.session_state.get("api_key", "")
    if current_key:
        try:
            status_r = httpx.get(
                f"{API_BASE}/billing/status",
                headers={"X-API-Key": current_key},
                timeout=5,
            )
            if status_r.status_code == 200:
                s = status_r.json()
                plan = s.get("plan", "free")
                usage = s.get("usage", {})
                limits = s.get("limits", {})

                if plan == "pro":
                    st.success("⭐ Plano **Pro** — uso ilimitado")
                else:
                    st.info(f"🆓 Plano **Free**")
                    def _bar(label, used, limit):
                        if isinstance(limit, int):
                            pct = min(used / limit, 1.0)
                            st.caption(f"{label}: {used}/{limit}")
                            st.progress(pct)
                    _bar("Mapeamentos", usage.get("mappings", 0), limits.get("mappings", 5))
                    _bar("DPIAs", usage.get("dpias", 0), limits.get("dpias", 2))
                    _bar("DSRs", usage.get("dsrs", 0), limits.get("dsrs", 10))

                    if s.get("stripe_configured"):
                        try:
                            checkout_r = httpx.post(
                                f"{API_BASE}/billing/checkout",
                                json={"api_key": current_key},
                                timeout=5,
                            )
                            if checkout_r.status_code == 200:
                                url = checkout_r.json().get("checkout_url", "")
                                st.markdown(f"[⭐ Upgrade para Pro]({url})", unsafe_allow_html=False)
                        except Exception:
                            pass
        except Exception:
            pass

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
                with st.spinner("🤖 Analisando com IA local (llama3.1)..."):
                    try:
                        resp = httpx.post(
                            f"{API_BASE}/map-data",
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
                with st.spinner("🤖 Gerando DPIA com IA local (llama3.1)..."):
                    try:
                        resp = httpx.post(
                            f"{API_BASE}/dpia/generate",
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

    if st.button("🔄 Atualizar histórico", key="refresh_all"):
        for k in ("hist_mapping", "hist_dpia"):
            st.session_state.pop(k, None)

    # Carregar dados
    if "hist_mapping" not in st.session_state:
        try:
            r = httpx.get(f"{API_BASE}/history/mapping", timeout=5)
            st.session_state["hist_mapping"] = r.json() if r.status_code == 200 else []
        except Exception:
            st.session_state["hist_mapping"] = []

    if "hist_dpia" not in st.session_state:
        try:
            r = httpx.get(f"{API_BASE}/history/dpia", timeout=5)
            st.session_state["hist_dpia"] = r.json() if r.status_code == 200 else []
        except Exception:
            st.session_state["hist_dpia"] = []

    mappings = st.session_state.get("hist_mapping", [])
    dpias    = st.session_state.get("hist_dpia", [])

    # ── Métricas resumo ──────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📊 Mapeamentos", len(mappings))
    m2.metric("🔍 DPIAs", len(dpias))

    if dpias:
        scores = [a.get("compliance_score", 0) for a in dpias if a.get("compliance_score") is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        m3.metric("📈 Score médio", f"{avg_score:.0f}/100")

        risk_counts = {"high": 0, "medium": 0, "low": 0}
        for a in dpias:
            risk_counts[a.get("risk_level", "low")] += 1
        dominant = max(risk_counts, key=risk_counts.get)
        risk_label = {"high": "🔴 Alto", "medium": "🟡 Médio", "low": "🟢 Baixo"}[dominant]
        m4.metric("⚠️ Risco dominante", risk_label)
    else:
        m3.metric("📈 Score médio", "—")
        m4.metric("⚠️ Risco dominante", "—")

    st.markdown("---")

    # ── Gráficos DPIA ────────────────────────────────────────────────────────
    if dpias:
        df_dpia = pd.DataFrame(dpias)
        df_dpia["created_at"] = pd.to_datetime(df_dpia["created_at"], errors="coerce")
        df_dpia["data"] = df_dpia["created_at"].dt.strftime("%d/%m/%y")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("**📉 Score de conformidade ao longo do tempo**")
            if "compliance_score" in df_dpia.columns:
                chart_df = df_dpia[["data", "compliance_score"]].rename(
                    columns={"compliance_score": "Score"}
                ).set_index("data")
                st.line_chart(chart_df)

        with chart_col2:
            st.markdown("**🎯 Distribuição de risco (DPIAs)**")
            risk_map = {"high": "Alto", "medium": "Médio", "low": "Baixo"}
            risk_df = (
                df_dpia["risk_level"]
                .map(risk_map)
                .value_counts()
                .rename_axis("Risco")
                .reset_index(name="Qtd")
                .set_index("Risco")
            )
            st.bar_chart(risk_df)

        st.markdown("---")

    # ── Tabs internas: Mapeamentos | DPIAs ───────────────────────────────────
    hist_tab1, hist_tab2 = st.tabs(["📊 Mapeamentos", "🔍 DPIAs"])

    with hist_tab1:
        if not mappings:
            st.info("Nenhuma auditoria de mapeamento encontrada.")
        else:
            df_map = pd.DataFrame(mappings)
            # Filtro por empresa
            empresas = ["Todas"] + sorted(df_map["company"].dropna().unique().tolist())
            empresa_sel = st.selectbox("Filtrar por empresa", empresas, key="filter_map_company")
            if empresa_sel != "Todas":
                df_map = df_map[df_map["company"] == empresa_sel]

            for _, a in df_map.iterrows():
                with st.expander(f"#{a['id']} — {a.get('company', 'N/A')} ({str(a.get('created_at', ''))[:10]})"):
                    st.write(f"**Contexto:** {a.get('context', 'N/A')}")
                    if st.button(f"Ver detalhes #{a['id']}", key=f"map_detail_{a['id']}"):
                        try:
                            dr = httpx.get(f"{API_BASE}/history/mapping/{a['id']}", timeout=5)
                            if dr.status_code == 200:
                                st.json(dr.json())
                        except Exception as e:
                            st.error(str(e))

    with hist_tab2:
        if not dpias:
            st.info("Nenhuma auditoria DPIA encontrada.")
        else:
            df_d = pd.DataFrame(dpias)
            # Filtros
            fc1, fc2 = st.columns(2)
            empresas_d = ["Todas"] + sorted(df_d["company"].dropna().unique().tolist())
            empresa_d  = fc1.selectbox("Filtrar por empresa", empresas_d, key="filter_dpia_company")
            riscos     = ["Todos", "high", "medium", "low"]
            risco_sel  = fc2.selectbox("Filtrar por risco", riscos, key="filter_dpia_risk",
                                       format_func=lambda x: {"Todos": "Todos", "high": "🔴 Alto",
                                                               "medium": "🟡 Médio", "low": "🟢 Baixo"}[x])
            if empresa_d != "Todas":
                df_d = df_d[df_d["company"] == empresa_d]
            if risco_sel != "Todos":
                df_d = df_d[df_d["risk_level"] == risco_sel]

            for _, a in df_d.iterrows():
                risk       = a.get("risk_level", "N/A")
                risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk, "⚪")
                score      = a.get("compliance_score", 0)
                with st.expander(
                    f"#{a['id']} {risk_emoji} — {a.get('company', 'N/A')} "
                    f"| Score: {score:.0f}/100 | ({str(a.get('created_at', ''))[:10]})"
                ):
                    st.write(f"**Tratamento:** {a.get('treatment', 'N/A')}")
                    st.progress(int(score) / 100)
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

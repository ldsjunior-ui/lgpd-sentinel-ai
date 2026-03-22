# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
LGPD-specific AI prompts in PT-BR.
All prompts are designed to elicit structured, compliance-focused responses
from local LLMs (Mistral/Llama via Ollama).
"""

try:
    from langchain.prompts import PromptTemplate
except ImportError:
    from langchain_core.prompts import PromptTemplate

# ---------------------------------------------------------------------------
# Data Mapping Prompt (Mapeamento de Dados Pessoais)
# ---------------------------------------------------------------------------

DATA_MAPPING_SYSTEM = """Voce e um especialista em privacidade de dados e conformidade com a LGPD
(Lei Geral de Protecao de Dados - Lei 13.709/2018).

Sua tarefa e analisar dados pessoais fornecidos e classificar cada campo segundo a LGPD.

Para cada campo de dado pessoal, voce deve identificar:
1. Categoria LGPD (dado_comum, dado_sensivel, dado_crianca_adolescente, dado_anonimo)
2. Base legal aplicavel (Art. 7 ou Art. 11 da LGPD)
3. Nivel de risco para o titular (baixo, medio, alto, critico)
4. Necessidade de consentimento explicito
5. Periodo de retencao recomendado
6. Medidas de seguranca recomendadas

Responda SEMPRE em formato JSON valido e estruturado.
Seja preciso e cite artigos especificos da LGPD quando relevante."""

DATA_MAPPING_TEMPLATE = PromptTemplate(
    input_variables=["data_items", "company_context"],
    template="""
{system_prompt}

CONTEXTO DA EMPRESA:
{company_context}

DADOS PESSOAIS PARA ANALISE:
{data_items}

Analise cada dado e retorne um JSON com o seguinte formato:
{{
  "mapeamento": [
    {{
      "campo": "nome_do_campo",
      "categoria_lgpd": "dado_comum|dado_sensivel|dado_crianca_adolescente|dado_anonimo",
      "base_legal": "consentimento|execucao_contrato|obrigacao_legal|interesse_legitimo|...",
      "artigo_lgpd": "Art. 7, inciso I|Art. 11, inciso II|...",
      "nivel_risco": "baixo|medio|alto|critico",
      "requer_consentimento_explicito": true|false,
      "periodo_retencao": "prazo recomendado",
      "medidas_seguranca": ["medida1", "medida2"],
      "observacoes": "observacoes adicionais sobre este dado"
    }}
  ],
  "resumo": {{
    "total_campos": 0,
    "campos_sensiveis": 0,
    "risco_geral": "baixo|medio|alto|critico",
    "recomendacoes_principais": ["rec1", "rec2"]
  }}
}}

JSON:
""".strip(),
    partial_variables={"system_prompt": DATA_MAPPING_SYSTEM},
)

# ---------------------------------------------------------------------------
# DPIA Prompt (Relatorio de Impacto a Protecao de Dados - RIPD)
# ---------------------------------------------------------------------------

DPIA_SYSTEM = """Voce e um especialista em DPIA (Data Protection Impact Assessment) e RIPD
(Relatorio de Impacto a Protecao de Dados Pessoais), conforme exigido pelo
Art. 38 da LGPD e diretrizes da ANPD (Autoridade Nacional de Protecao de Dados).

Sua tarefa e gerar um RIPD completo e estruturado para o tratamento de dados descrito.

O RIPD deve conter:
1. Descricao do tratamento de dados
2. Finalidade e base legal
3. Avaliacao de riscos aos titulares
4. Medidas de mitigacao
5. Recomendacoes de conformidade
6. Necessidade de consulta previa a ANPD

Seja tecnicamente preciso e cite a LGPD, GDPR (quando analogia util) e normas da ANPD."""

DPIA_TEMPLATE = PromptTemplate(
    input_variables=["treatment_description", "data_types", "purposes", "company_info"],
    template="""
{system_prompt}

INFORMACOES DA EMPRESA:
{company_info}

DESCRICAO DO TRATAMENTO:
{treatment_description}

TIPOS DE DADOS TRATADOS:
{data_types}

FINALIDADES DO TRATAMENTO:
{purposes}

Gere um RIPD completo em JSON:
{{
  "ripd": {{
    "identificacao": {{
      "empresa": "nome da empresa",
      "responsavel": "nome do responsavel",
      "encarregado_dpo": "nome do DPO se houver",
      "data_avaliacao": "data",
      "versao": "1.0"
    }},
    "descricao_tratamento": {{
      "finalidade": "descricao da finalidade",
      "base_legal": "base legal conforme LGPD",
      "artigos_aplicaveis": ["Art. X"],
      "categorias_dados": ["lista de categorias"],
      "volume_estimado": "numero aproximado de titulares"
    }},
    "avaliacao_riscos": [
      {{
        "risco": "descricao do risco",
        "probabilidade": "baixa|media|alta",
        "impacto": "baixo|medio|alto|severo",
        "nivel_risco": "baixo|medio|alto|critico",
        "titulares_afetados": "descricao"
      }}
    ],
    "medidas_mitigacao": [
      {{
        "medida": "descricao da medida",
        "tipo": "tecnica|organizacional|juridica",
        "prazo": "prazo para implementacao",
        "responsavel": "area responsavel"
      }}
    ],
    "conformidade": {{
      "score_conformidade": 0,
      "status": "conforme|nao_conforme|em_adequacao",
      "lacunas_identificadas": ["lacuna1"],
      "recomendacoes": ["recomendacao1"],
      "consulta_previa_anpd": false,
      "justificativa_consulta": "justificativa se necessario"
    }}
  }}
}}

RIPD JSON:
""".strip(),
    partial_variables={"system_prompt": DPIA_SYSTEM},
)

# ---------------------------------------------------------------------------
# Risk Assessment Prompt (Avaliacao de Risco LGPD)
# ---------------------------------------------------------------------------

RISK_ASSESSMENT_TEMPLATE = PromptTemplate(
    input_variables=["data_summary", "security_measures", "incidents_history"],
    template="""Voce e um auditor de privacidade especializado em LGPD.

Avalie o nivel de risco de conformidade LGPD com base nas informacoes abaixo:

RESUMO DOS DADOS TRATADOS:
{data_summary}

MEDIDAS DE SEGURANCA IMPLEMENTADAS:
{security_measures}

HISTORICO DE INCIDENTES:
{incidents_history}

Retorne uma avaliacao de risco em JSON:
{{
  "score_risco": 0.0,
  "nivel": "baixo|medio|alto|critico",
  "fatores_risco": [
    {{
      "fator": "descricao",
      "peso": 0.0,
      "justificativa": "..."
    }}
  ],
  "acoes_prioritarias": [
    {{
      "acao": "descricao",
      "urgencia": "imediata|curto_prazo|medio_prazo",
      "impacto_reducao_risco": "alto|medio|baixo"
    }}
  ],
  "proximo_review": "data recomendada para proxima avaliacao"
}}

JSON:""",
)

# ---------------------------------------------------------------------------
# DSR Prompt (Data Subject Rights / Direitos do Titular - Art. 18 LGPD)
# ---------------------------------------------------------------------------

DSR_SYSTEM = """Voce e um especialista em direitos dos titulares de dados conforme
o Art. 18 da LGPD (Lei 13.709/2018) e regulamentacoes da ANPD.

Sua tarefa e analisar uma solicitacao de direito do titular e:
1. Identificar o direito solicitado (acesso, correcao, exclusao, portabilidade, etc.)
2. Verificar se ha base legal para atender ou negar a solicitacao
3. Gerar uma resposta ao titular em linguagem clara e acessivel
4. Orientar o controlador sobre prazos e procedimentos (prazo: 15 dias conforme Art. 18 §5)
5. Indicar se e necessario acionar o DPO ou reportar a ANPD

Cite sempre os artigos aplicaveis da LGPD. Responda em JSON valido."""

DSR_TEMPLATE = PromptTemplate(
    input_variables=["request_type", "request_description", "company_name", "data_context"],
    template="""
{system_prompt}

EMPRESA/CONTROLADOR: {company_name}
TIPO DE SOLICITACAO: {request_type}
DESCRICAO DA SOLICITACAO: {request_description}
CONTEXTO DOS DADOS: {data_context}

Analise e retorne em JSON:
{{
  "dsr": {{
    "direito_identificado": "acesso|correcao|exclusao|portabilidade|oposicao|revogacao_consentimento|restricao",
    "artigo_lgpd": "Art. 18, inciso X",
    "pode_atender": true,
    "justificativa": "motivo para atender ou negar",
    "prazo_resposta_dias": 15,
    "acoes_requeridas": [
      {{
        "acao": "descricao da acao",
        "responsavel": "area/pessoa responsavel",
        "prazo": "imediato|3_dias|15_dias"
      }}
    ],
    "resposta_ao_titular": "texto da resposta formal ao titular em linguagem clara",
    "requer_dpo": false,
    "requer_anpd": false,
    "justificativa_anpd": null,
    "documentacao_necessaria": ["documento1", "documento2"]
  }}
}}

JSON:
""".strip(),
    partial_variables={"system_prompt": DSR_SYSTEM},
)

# ---------------------------------------------------------------------------
# Helper: All prompts as dict for easy access
# ---------------------------------------------------------------------------

PROMPTS = {
    "data_mapping": DATA_MAPPING_TEMPLATE,
    "dpia": DPIA_TEMPLATE,
    "risk_assessment": RISK_ASSESSMENT_TEMPLATE,
    "dsr": DSR_TEMPLATE,
}

__all__ = [
    "DATA_MAPPING_SYSTEM",
    "DATA_MAPPING_TEMPLATE",
    "DPIA_SYSTEM",
    "DPIA_TEMPLATE",
    "DSR_SYSTEM",
    "DSR_TEMPLATE",
    "RISK_ASSESSMENT_TEMPLATE",
    "PROMPTS",
]

# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
LGPD-specific AI prompts in PT-BR.
All prompts are designed to elicit structured, compliance-focused responses
from local LLMs (Mistral/Llama via Ollama).
"""

from langchain.prompts import PromptTemplate

# ---------------------------------------------------------------------------
# Data Mapping Prompt (Mapeamento de Dados Pessoais)
# ---------------------------------------------------------------------------

DATA_MAPPING_SYSTEM = """Voce e um especialista em privacidade de dados e conformidade com a LGPD
(Lei Geral de Protecao de Dados - Lei 13.709/2018).

Sua tarefa e analisar dados pessoais fornecidos e classificar cada campo segundo a LGPD.

CLASSIFICACAO OBRIGATORIA conforme Art. 5:

DADOS PESSOAIS SENSIVEIS (Art. 5, II) - inclui QUALQUER dado sobre:
- Origem racial ou etnica
- Conviccao religiosa
- Opiniao politica
- Filiacao a sindicato ou organizacao de carater religioso, filosofico ou politico
- Dados referentes a saude (diagnosticos, exames, historico medico, CID, etc.)
- Vida sexual
- Dados geneticos (DNA, sequenciamento genomico, etc.)
- Dados biometricos (facial, digital, iris, voz, etc.)

DADOS PESSOAIS COMUNS (Art. 5, I) - dados que identificam ou tornam identificavel uma pessoa:
- CPF, RG, CNH, CNPJ
- Nome, nome completo
- Email, telefone, endereco
- Endereco IP, cookies, geolocation
- Data de nascimento, idade
- Dados financeiros (salario, conta bancaria, cartao)
- Dados profissionais (cargo, empresa, matricula)

DADOS ANONIMIZADOS (Art. 12) - dados que perderam a possibilidade de associacao a um titular.

DADOS DE CRIANCA/ADOLESCENTE (Art. 14) - quaisquer dados de menores de 18 anos.

BASES LEGAIS - use SOMENTE as bases corretas para cada categoria:

Para DADOS COMUNS (Art. 7):
I - consentimento
II - obrigacao_legal_regulatoria
III - execucao_politicas_publicas
IV - pesquisa (com anonimizacao quando possivel)
V - execucao_contrato
VI - exercicio_regular_direitos
VII - protecao_vida
VIII - tutela_da_saude
IX - interesse_legitimo
X - protecao_credito

Para DADOS SENSIVEIS (Art. 11) - SOMENTE estas bases sao validas:
I - consentimento_explicito (forma destacada e para finalidades especificas)
II.a - obrigacao_legal_regulatoria
II.b - execucao_politicas_publicas
II.c - pesquisa (com anonimizacao quando possivel)
II.d - exercicio_regular_direitos (contrato ou processo)
II.e - protecao_vida
II.f - tutela_da_saude (por profissionais de saude ou autoridade sanitaria)
II.g - prevencao_fraude

IMPORTANTE: Para dados sensiveis, NAO sao validas as bases: execucao_contrato, interesse_legitimo, protecao_credito.

Para cada campo de dado pessoal, voce deve identificar:
1. Categoria LGPD (dado_comum, dado_sensivel, dado_crianca_adolescente, dado_anonimo)
2. Base legal aplicavel (Art. 7 para dados comuns, Art. 11 para dados sensiveis)
3. Artigo LGPD especifico (ex: Art. 7, inciso V ou Art. 11, inciso I)
4. Nivel de risco para o titular (baixo, medio, alto, critico)
5. Necessidade de consentimento explicito
6. Periodo de retencao recomendado
7. Medidas de seguranca recomendadas

Responda SEMPRE em formato JSON valido e estruturado.
Seja preciso e cite artigos especificos da LGPD quando relevante."""

DATA_MAPPING_TEMPLATE = PromptTemplate(
    input_variables=["data_items", "company_context"],
    template="""Classifique cada dado conforme LGPD. Dados sensiveis (Art.5,II): saude, biometria, genetica, religiao, politica, etnia, vida sexual, sindicato. Dados comuns (Art.5,I): CPF, nome, email, telefone, endereco, financeiro. Bases legais dados sensiveis SOMENTE Art.11: consentimento_explicito, obrigacao_legal, tutela_saude, prevencao_fraude. Dados comuns Art.7: consentimento, execucao_contrato, obrigacao_legal, interesse_legitimo.

Contexto: {company_context}
Dados: {data_items}

JSON (sem explicacao, so o JSON):
{{"mapeamento":[{{"campo":"x","categoria_lgpd":"dado_comum|dado_sensivel","is_sensitive":true|false,"base_legal":"base","artigo_lgpd":"Art.X","nivel_risco":"baixo|medio|alto|critico"}}],"resumo":{{"score_conformidade":0,"recomendacoes_principais":["r1"]}}}}

JSON:""",
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
    template="""Gere RIPD (LGPD Art.38). Empresa: {company_info}. Tratamento: {treatment_description}. Dados: {data_types}. Finalidade: {purposes}.

JSON (so JSON, sem explicacao):
{{"ripd":{{"descricao_tratamento":{{"base_legal":"base conforme LGPD","artigos_aplicaveis":["Art.X"]}},"avaliacao_riscos":[{{"risco":"descricao","nivel_risco":"baixo|medio|alto|critico"}}],"medidas_mitigacao":[{{"medida":"descricao","tipo":"tecnica|organizacional"}}],"conformidade":{{"score_conformidade":0,"recomendacoes":["rec"],"consulta_previa_anpd":false}}}}}}

JSON:""",
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
    template="""Analise solicitacao de direito do titular (LGPD Art.18). Prazo legal: 15 dias (Art.18 §5). Empresa: {company_name}. Tipo: {request_type}. Solicitacao: {request_description}. Contexto: {data_context}.

JSON (so JSON, sem explicacao):
{{"dsr":{{"direito_identificado":"tipo","artigo_lgpd":"Art.18,X","pode_atender":true,"justificativa":"motivo","prazo_resposta_dias":15,"acoes_requeridas":[{{"acao":"descricao","responsavel":"area","prazo":"imediato|3_dias|15_dias"}}],"resposta_ao_titular":"texto resposta formal clara","requer_dpo":false,"requer_anpd":false,"documentacao_necessaria":["doc1"]}}}}

JSON:""",
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

# LGPD Sentinel AI - Endpoint de Data Mapping
# Identifica dados pessoais usando LangChain + Ollama (gratuito e local)
# Sem APIs pagas, sem GPU obrigatória
# Apache 2.0

import json
import re
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
from io import StringIO

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from src.models.schemas import (
    DataMappingRequest,
    DataMappingResponse,
    DataItem,
    LGPDCategory,
    RiskLevel
)

# Router para o módulo de data mapping
router = APIRouter()

# URL do Ollama (local via Docker, gratuito)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "mistral"  # Modelo gratuito e eficiente

# Prompt especializado em LGPD para classificação de dados
LGPD_MAPPING_PROMPT = PromptTemplate(
    input_variables=["data_items", "context"],
    template="""Você é um especialista em LGPD (Lei Geral de Proteção de Dados do Brasil).
    
Analise os seguintes dados e classifique cada um conforme a LGPD:

DADOS PARA ANÁLISE:
{data_items}

CONTEXTO DO TRATAMENTO: {context}

Para cada item, determine:
1. Se é dado pessoal (LGPD Art. 5, I)
2. Se é dado sensível (LGPD Art. 5, II): origem racial/étnica, convicção religiosa, 
   opinião política, filiação sindical, saúde, vida sexual, genético, biométrico
3. A base legal apropriada (Art. 7 para pessoal, Art. 11 para sensível)
4. Nível de risco: baixo, medio, alto, critico

Responda em JSON com o formato:
{{
  "classificacoes": [
    {{
      "key": "nome_do_campo",
      "is_personal": true/false,
      "is_sensitive": true/false,
      "lgpd_category": "dado_pessoal|dado_sensivel|dado_anonimizado|nao_classificado",
      "risk_level": "baixo|medio|alto|critico",
      "legal_basis": "descrição da base legal"
    }}
  ],
  "compliance_score": 0-100,
  "recommendations": ["recomendação 1", "recomendação 2"]
}}

Responda APENAS com o JSON, sem texto adicional."""
)


def get_llm():
    """Inicializa o modelo Ollama local (gratuito)."""
    try:
        return Ollama(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            temperature=0.1  # Baixa temperatura para respostas mais precisas
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama não está disponível. Execute: docker exec lgpd-sentinel-ollama ollama pull {OLLAMA_MODEL}. Erro: {str(e)}"
        )


@router.post(
    "/map-data",
    response_model=DataMappingResponse,
    summary="Mapear dados pessoais conforme LGPD",
    description="""
    Analisa uma lista de dados e classifica cada item conforme a LGPD usando IA (Mistral via Ollama).
    
    - Identifica dados pessoais (Art. 5, I)
    - Identifica dados sensíveis (Art. 5, II)  
    - Sugere bases legais (Art. 7 e 11)
    - Calcula score de conformidade
    - Gera recomendações de melhoria
    
    **Gratuito**: usa Ollama local, sem chamadas a APIs externas pagas.
    """
)
async def map_data(request: DataMappingRequest):
    """
    Endpoint principal de data mapping LGPD.
    Usa LangChain + Ollama (Mistral) para análise com IA local.
    """
    # Preparar dados para o prompt
    data_items_str = "\n".join([
        f"- {item.key}: {item.value}"
        for item in request.data
    ])
    
    context = request.context or "não especificado"
    
    # Chamar LLM local (Ollama, gratuito)
    llm = get_llm()
    chain = LLMChain(llm=llm, prompt=LGPD_MAPPING_PROMPT)
    
    try:
        result = await chain.arun(
            data_items=data_items_str,
            context=context
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro na análise IA: {str(e)}"
        )
    
    # Parsear resposta JSON do LLM
    try:
        # Extrair JSON da resposta (LLM pode adicionar texto extra)
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if not json_match:
            raise ValueError("LLM não retornou JSON válido")
        
        analysis = json.loads(json_match.group())
        classificacoes = analysis.get("classificacoes", [])
        compliance_score = float(analysis.get("compliance_score", 50))
        recommendations = analysis.get("recommendations", [])
        
    except (json.JSONDecodeError, ValueError):
        # Fallback: classificação básica por regex se LLM falhar
        classificacoes = _classify_by_regex(request.data)
        compliance_score = 60.0
        recommendations = [
            "Execute o audit completo com Ollama para análise mais precisa",
            "Verifique se todos os dados têm base legal documentada"
        ]
    
    # Construir resposta
    mapped_items = []
    for item in request.data:
        classificacao = next(
            (c for c in classificacoes if c.get("key") == item.key),
            {"is_sensitive": False, "lgpd_category": "nao_classificado", "legal_basis": None}
        )
        
        mapped_items.append(DataItem(
            key=item.key,
            value=item.value,
            sensitive=classificacao.get("is_sensitive", False),
            lgpd_category=LGPDCategory(
                classificacao.get("lgpd_category", "nao_classificado")
            ),
            legal_basis=classificacao.get("legal_basis")
        ))
    
    total_personal = sum(1 for i in mapped_items if i.lgpd_category != LGPDCategory.NAO_CLASSIFICADO)
    total_sensitive = sum(1 for i in mapped_items if i.sensitive)
    
    return DataMappingResponse(
        mapped_data=mapped_items,
        compliance_score=compliance_score,
        recommendations=recommendations,
        total_personal_data=total_personal,
        total_sensitive_data=total_sensitive
    )


@router.post(
    "/map-data/upload",
    summary="Mapear dados a partir de arquivo CSV/JSON",
    description="Faz upload de arquivo CSV ou JSON e analisa os dados conforme LGPD."
)
async def map_data_from_file(file: UploadFile = File(...)):
    """
    Aceita upload de arquivo CSV ou JSON e executa o data mapping LGPD.
    """
    if not file.filename.endswith(('.csv', '.json')):
        raise HTTPException(
            status_code=400,
            detail="Formato não suportado. Use CSV ou JSON."
        )
    
    content = await file.read()
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(StringIO(content.decode('utf-8')))
            data_items = [
                DataItem(key=col, value=str(df[col].iloc[0]))
                for col in df.columns
                if not df[col].empty
            ]
        else:
            data_dict = json.loads(content.decode('utf-8'))
            if isinstance(data_dict, list):
                data_dict = data_dict[0] if data_dict else {}
            data_items = [
                DataItem(key=k, value=str(v))
                for k, v in data_dict.items()
            ]
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )
    
    request = DataMappingRequest(data=data_items)
    return await map_data(request)


def _classify_by_regex(data: list) -> list:
    """
    Classificação básica por regex (fallback quando Ollama não está disponível).
    Identifica padrões comuns de dados pessoais sem IA.
    """
    sensitive_patterns = {
        'cpf': r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}',
        'rg': r'\d{1,2}\.?\d{3}\.?\d{3}-?[\dxX]',
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'telefone': r'\(?\d{2}\)?[\s-]?\d{4,5}-?\d{4}',
        'data_nascimento': r'\d{2}/\d{2}/\d{4}',
    }
    
    sensitive_keys = ['saude', 'health', 'biometrico', 'biometric', 'racial', 
                     'religiao', 'religion', 'politico', 'political', 'sexual']
    
    result = []
    for item in data:
        is_sensitive = any(k in item.key.lower() for k in sensitive_keys)
        is_personal = any(re.search(p, item.value) for p in sensitive_patterns.values())
        
        result.append({
            "key": item.key,
            "is_personal": is_personal or is_sensitive,
            "is_sensitive": is_sensitive,
            "lgpd_category": "dado_sensivel" if is_sensitive else ("dado_pessoal" if is_personal else "nao_classificado"),
            "legal_basis": "Verificar base legal conforme LGPD Art. 7"
        })
    
    return result

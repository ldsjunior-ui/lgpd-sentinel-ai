let baseUrl: string | null = null;
let apiKey: string | null = null;

export async function getBaseUrl(): Promise<string> {
  if (baseUrl) return baseUrl;
  baseUrl = "http://localhost:8000/api/v1";
  return baseUrl;
}

export function setApiKey(key: string) {
  apiKey = key;
  localStorage.setItem("lgpd_api_key", key);
}

export function getApiKey(): string | null {
  if (apiKey) return apiKey;
  apiKey = localStorage.getItem("lgpd_api_key");
  return apiKey;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = await getBaseUrl();
  const key = getApiKey();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (key) {
    headers["X-API-Key"] = key;
  }

  const response = await fetch(`${url}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    let message = `API Error ${response.status}`;
    try {
      const parsed = JSON.parse(errorBody);
      const detail = parsed.detail || parsed.message;
      if (typeof detail === 'string') {
        message = detail;
      } else if (Array.isArray(detail)) {
        message = detail.map((d: Record<string, unknown>) => `${d.loc}: ${d.msg}`).join(', ');
      } else if (typeof detail === 'object' && detail !== null) {
        message = JSON.stringify(detail);
      }
    } catch {
      if (errorBody) message = errorBody;
    }
    throw new Error(message);
  }

  return response.json();
}

async function requestBlob(
  endpoint: string,
  options: RequestInit = {}
): Promise<Blob> {
  const url = await getBaseUrl();
  const key = getApiKey();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (key) {
    headers["X-API-Key"] = key;
  }

  const response = await fetch(`${url}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    let message = `API Error ${response.status}`;
    try {
      const parsed = JSON.parse(errorBody);
      const detail = parsed.detail || parsed.message;
      if (typeof detail === 'string') {
        message = detail;
      } else if (Array.isArray(detail)) {
        message = detail.map((d: Record<string, unknown>) => `${d.loc}: ${d.msg}`).join(', ');
      } else if (typeof detail === 'object' && detail !== null) {
        message = JSON.stringify(detail);
      }
    } catch {
      if (errorBody) message = errorBody;
    }
    throw new Error(message);
  }

  return response.blob();
}

// --- Data Types ---

export interface DataItem {
  nome: string;
  descricao: string;
  fonte: string;
}

export interface MapDataRequest {
  empresa: string;
  finalidade: string;
  dados: DataItem[];
}

export interface MappedItem {
  nome: string;
  descricao: string;
  fonte: string;
  sensivel: boolean;
  nivel_risco: string;
  base_legal_sugerida: string;
  recomendacoes: string[];
}

export interface MapDataResponse {
  empresa: string;
  total_itens: number;
  dados_sensiveis: number;
  nivel_risco_geral: string;
  score_conformidade: number;
  recomendacoes_gerais: string[];
  itens_mapeados: MappedItem[];
  timestamp: string;
}

export interface DPIARequest {
  empresa: string;
  processo: string;
  finalidade: string;
  dados_envolvidos: string;
  medidas_seguranca: string;
}

export interface DPIAResponse {
  empresa: string;
  processo: string;
  nivel_risco: string;
  score_risco: number;
  riscos_identificados: string[];
  medidas_mitigacao: string[];
  base_legal: string;
  necessita_dpo: boolean;
  recomendacoes: string[];
  timestamp: string;
}

export interface DSRRequest {
  empresa: string;
  titular: string;
  tipo_solicitacao: string;
  descricao: string;
  contexto: string;
}

export interface DSRResponse {
  empresa: string;
  titular: string;
  tipo_solicitacao: string;
  pode_atender: boolean;
  artigo_lgpd: string;
  prazo: string;
  necessita_dpo: boolean;
  necessita_anpd: boolean;
  acoes_requeridas: string[];
  resposta_ao_titular: string;
  timestamp: string;
}

export interface HistoryEntry {
  id: string;
  tipo: string;
  empresa: string;
  timestamp: string;
  nivel_risco?: string;
  score_conformidade?: number;
  resumo?: string;
}

export interface HistoryResponse {
  total: number;
  items: HistoryEntry[];
}

export interface StatusResponse {
  status: string;
  ollama_connected: boolean;
  model_loaded: boolean;
  model_name: string;
  version: string;
}

export interface PlanStatus {
  plan: string;
  requests_today: number;
  daily_limit: number;
  requests_remaining: number;
}

// --- API Functions ---

export async function mapData(data: MapDataRequest): Promise<MapDataResponse> {
  // Convert frontend format to API format
  const apiPayload = {
    data: data.dados.map((d) => ({
      key: d.nome,
      value: d.descricao || d.nome,
    })),
  };
  const raw = await request<Record<string, unknown>>("/map-data", {
    method: "POST",
    body: JSON.stringify(apiPayload),
  });
  // Normalize API response to frontend format
  const mapped = (raw.mapped_data as Array<Record<string, unknown>>) || [];
  const legalBasisMap: Record<string, string> = {
    consentimento: "Consentimento (Art. 7º, I)",
    execucao_contrato: "Execução de Contrato (Art. 7º, V)",
    obrigacao_legal: "Obrigação Legal (Art. 7º, II)",
    interesse_legitimo: "Interesse Legítimo (Art. 7º, IX)",
    protecao_vida: "Proteção da Vida (Art. 7º, VII)",
    tutela_saude: "Tutela da Saúde (Art. 7º, VIII)",
    protecao_credito: "Proteção ao Crédito (Art. 7º, X)",
  };
  const sensitiveCount = mapped.filter((m) => m.sensitive === true).length;
  return {
    empresa: data.empresa,
    total_itens: (raw.total_personal_data as number) || mapped.length,
    dados_sensiveis: (raw.total_sensitive_data as number) || sensitiveCount,
    nivel_risco_geral: (raw.compliance_score as number) < 50 ? "alto" : (raw.compliance_score as number) < 75 ? "medio" : "baixo",
    score_conformidade: (raw.compliance_score as number) || 0,
    recomendacoes_gerais: (raw.recommendations as string[]) || [],
    itens_mapeados: mapped.map((m) => {
      const basis = (m.legal_basis as string) || "";
      return {
        nome: (m.key as string) || "",
        descricao: (m.value as string) || "",
        fonte: (m.lgpd_category as string) || "",
        sensivel: (m.sensitive as boolean) || false,
        nivel_risco: (m.sensitive as boolean) ? "alto" : "baixo",
        base_legal_sugerida: legalBasisMap[basis] || basis || "Não identificada",
        recomendacoes: [],
      };
    }),
    timestamp: new Date().toISOString(),
  };
}

export async function generateDPIA(data: DPIARequest): Promise<DPIAResponse> {
  const apiPayload = {
    company_name: data.empresa,
    treatment_description: `${data.processo}: ${data.finalidade}`,
    data_types: data.dados_envolvidos.split(/[,\n]/).map(s => s.trim()).filter(Boolean),
    purposes: [data.finalidade],
    existing_measures: data.medidas_seguranca,
  };
  const raw = await request<Record<string, unknown>>("/dpia/generate", {
    method: "POST",
    body: JSON.stringify(apiPayload),
  });
  // Map risks (API returns objects with risco/descricao fields)
  const rawRisks = (raw.risks as Array<Record<string, unknown>>) || [];
  const riscos = rawRisks.map(r =>
    typeof r === 'string' ? r : (r.risco as string) || (r.descricao as string) || JSON.stringify(r)
  );
  // Map mitigation measures (API returns objects with medida field)
  const rawMedidas = (raw.mitigation_measures as Array<Record<string, unknown>>) || [];
  const medidas = rawMedidas.map(m =>
    typeof m === 'string' ? m : (m.medida as string) || (m.descricao as string) || JSON.stringify(m)
  );
  // Map recommendations (API returns objects or strings)
  const rawRecs = (raw.recommendations as Array<Record<string, unknown> | string>) || [];
  const recs = rawRecs.map(r =>
    typeof r === 'string' ? r : (r as Record<string, unknown>).recomendacao as string || JSON.stringify(r)
  );
  return {
    empresa: data.empresa,
    processo: data.processo,
    nivel_risco: (raw.risk_level as string) || "medio",
    score_risco: (raw.overall_risk_score as number) || (raw.compliance_score as number) || 50,
    riscos_identificados: riscos,
    medidas_mitigacao: medidas,
    base_legal: (raw.legal_basis as string) || "",
    necessita_dpo: (raw.requires_anpd_consultation as boolean) || false,
    recomendacoes: recs,
    timestamp: new Date().toISOString(),
  };
}

export async function generateDPIAPdf(data: DPIARequest): Promise<Blob> {
  const apiPayload = {
    company_name: data.empresa,
    treatment_description: `${data.processo}: ${data.finalidade}`,
    data_types: data.dados_envolvidos.split(/[,\n]/).map(s => s.trim()).filter(Boolean),
    purposes: [data.finalidade],
  };
  return requestBlob("/dpia/generate/pdf", {
    method: "POST",
    body: JSON.stringify(apiPayload),
  });
}

export async function analyzeDSR(data: DSRRequest): Promise<DSRResponse> {
  const apiPayload = {
    company_name: data.empresa,
    request_type: data.tipo_solicitacao,
    request_description: data.descricao,
    data_context: data.contexto || null,
    titular_name: data.titular || null,
  };
  const raw = await request<Record<string, unknown>>("/dsr/analyze", {
    method: "POST",
    body: JSON.stringify(apiPayload),
  });
  return {
    empresa: data.empresa,
    titular: data.titular,
    tipo_solicitacao: data.tipo_solicitacao,
    pode_atender: (raw.pode_atender as boolean) ?? true,
    artigo_lgpd: (raw.artigo_lgpd as string) || "",
    prazo: (raw.prazo_resposta_dias as string) || "15 dias",
    necessita_dpo: (raw.requer_dpo as boolean) || false,
    necessita_anpd: (raw.requer_anpd as boolean) || false,
    acoes_requeridas: ((raw.acoes_requeridas as Array<Record<string, string>>) || []).map(
      a => typeof a === 'string' ? a : `${a.acao || ''} (${a.responsavel || ''} - ${a.prazo || ''})`
    ),
    resposta_ao_titular: (raw.resposta_ao_titular as string) || "",
    timestamp: new Date().toISOString(),
  };
}

export async function getHistory(
  _tipo?: string,
  _empresa?: string,
  limit?: number
): Promise<HistoryResponse> {
  const limitParam = limit ? `?limit=${limit}` : "";
  const [mappings, dpias] = await Promise.all([
    request<Array<Record<string, unknown>>>(`/history/mapping${limitParam}`).catch(() => []),
    request<Array<Record<string, unknown>>>(`/history/dpia${limitParam}`).catch(() => []),
  ]);
  const items: HistoryEntry[] = [
    ...mappings.map((m) => ({
      id: String(m.id),
      tipo: "mapeamento",
      empresa: (m.company as string) || "N/A",
      timestamp: (m.created_at as string) || new Date().toISOString(),
      resumo: (m.context as string) || undefined,
    })),
    ...dpias.map((d) => ({
      id: String(d.id),
      tipo: "dpia",
      empresa: (d.company as string) || "N/A",
      timestamp: (d.created_at as string) || new Date().toISOString(),
      nivel_risco: (d.risk_level as string) || undefined,
      score_conformidade: (d.compliance_score as number) || undefined,
      resumo: (d.treatment as string) || undefined,
    })),
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  return { total: items.length, items };
}

export async function getStatus(): Promise<StatusResponse> {
  // Use the health endpoint which always exists
  const url = await getBaseUrl();
  const healthUrl = url.replace("/api/v1", "/health");
  const response = await fetch(healthUrl);
  if (!response.ok) throw new Error("API offline");
  const data = await response.json();
  return {
    status: data.status || "healthy",
    ollama_connected: true,
    model_loaded: true,
    model_name: "mistral",
    version: data.version || "1.0.0",
  };
}

export async function generateKey(): Promise<{ api_key: string }> {
  return request<{ api_key: string }>("/billing/keys", {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function getPlanStatus(): Promise<PlanStatus> {
  return request<PlanStatus>("/billing/status");
}

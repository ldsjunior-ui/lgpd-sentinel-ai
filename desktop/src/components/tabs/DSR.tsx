import { useState } from "react";
import {
  Shield,
  Loader2,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  UserCheck,
  Building2,
} from "lucide-react";
import { analyzeDSR, type DSRRequest, type DSRResponse } from "../../lib/api";

const REQUEST_TYPES = [
  { value: "acesso", label: "Acesso aos Dados" },
  { value: "correcao", label: "Correção de Dados" },
  { value: "exclusao", label: "Exclusão de Dados" },
  { value: "portabilidade", label: "Portabilidade" },
  { value: "oposicao", label: "Oposição ao Tratamento" },
  { value: "revogacao_consentimento", label: "Revogação de Consentimento" },
  { value: "restricao", label: "Restrição de Tratamento" },
  { value: "informacao", label: "Solicitação de Informação" },
];

export default function DSR() {
  const [form, setForm] = useState<DSRRequest>({
    empresa: "",
    titular: "",
    tipo_solicitacao: "acesso",
    descricao: "",
    contexto: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DSRResponse | null>(null);

  function updateField(field: keyof DSRRequest, value: string) {
    setForm({ ...form, [field]: value });
  }

  async function handleSubmit() {
    if (!form.empresa.trim() || !form.titular.trim() || !form.descricao.trim()) {
      setError("Preencha ao menos empresa, titular e descrição.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeDSR(form);
      setResult(response);
    } catch (err: any) {
      const msg = err instanceof Error ? err.message
        : typeof err === 'object' ? JSON.stringify(err)
        : String(err);
      setError(msg || "Erro ao analisar DSR.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Shield size={24} className="text-[#00cc50]" />
          Direitos do Titular (DSR)
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Analise solicitações de direitos dos titulares de dados conforme os
          Arts. 17-22 da LGPD.
        </p>
      </div>

      {/* Form */}
      <div className="card space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label-text">Nome da Empresa</label>
            <input
              type="text"
              className="input-field"
              placeholder="Ex: Minha Empresa Ltda"
              value={form.empresa}
              onChange={(e) => updateField("empresa", e.target.value)}
            />
          </div>
          <div>
            <label className="label-text">Nome do Titular</label>
            <input
              type="text"
              className="input-field"
              placeholder="Nome do titular dos dados"
              value={form.titular}
              onChange={(e) => updateField("titular", e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="label-text">Tipo de Solicitação</label>
          <select
            className="select-field"
            value={form.tipo_solicitacao}
            onChange={(e) => updateField("tipo_solicitacao", e.target.value)}
          >
            {REQUEST_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label-text">Descrição da Solicitação</label>
          <textarea
            className="input-field min-h-[100px] resize-y"
            placeholder="Descreva em detalhes a solicitação do titular..."
            value={form.descricao}
            onChange={(e) => updateField("descricao", e.target.value)}
          />
        </div>

        <div>
          <label className="label-text">Contexto Adicional</label>
          <textarea
            className="input-field min-h-[80px] resize-y"
            placeholder="Informações adicionais relevantes (relação com a empresa, dados tratados, etc.)"
            value={form.contexto}
            onChange={(e) => updateField("contexto", e.target.value)}
          />
        </div>

        {error && (
          <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 p-3 rounded-lg border border-red-500/20">
            <AlertTriangle size={16} />
            {error}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn-primary w-full justify-center text-base py-3"
        >
          {loading ? (
            <>
              <Loader2 size={20} className="spinner" />
              Analisando solicitação...
            </>
          ) : (
            <>
              <Shield size={20} />
              Analisar Solicitação
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4 fade-in">
          {/* Verdict */}
          <div
            className={`card border ${
              result.pode_atender
                ? "border-[#00cc50]/30 bg-[#00cc50]/5"
                : "border-red-500/30 bg-red-500/5"
            }`}
          >
            <div className="flex items-center gap-3 mb-3">
              {result.pode_atender ? (
                <CheckCircle size={28} className="text-[#00cc50]" />
              ) : (
                <XCircle size={28} className="text-red-500" />
              )}
              <div>
                <h3 className="text-lg font-bold text-white">
                  {result.pode_atender
                    ? "Solicitação Pode Ser Atendida"
                    : "Solicitação Não Pode Ser Atendida"}
                </h3>
                <p className="text-sm text-gray-400">
                  Tipo:{" "}
                  {REQUEST_TYPES.find(
                    (t) => t.value === result.tipo_solicitacao
                  )?.label || result.tipo_solicitacao}
                </p>
              </div>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="card">
              <div className="flex items-center gap-2 mb-2">
                <Shield size={14} className="text-[#00cc50]" />
                <span className="text-xs font-medium text-gray-400">
                  Artigo LGPD
                </span>
              </div>
              <p className="text-sm text-white">{result.artigo_lgpd}</p>
            </div>

            <div className="card">
              <div className="flex items-center gap-2 mb-2">
                <Clock size={14} className="text-[#00cc50]" />
                <span className="text-xs font-medium text-gray-400">Prazo</span>
              </div>
              <p className="text-sm text-white">{result.prazo}</p>
            </div>

            <div className="card">
              <div className="flex items-center gap-2 mb-2">
                <UserCheck size={14} className="text-yellow-500" />
                <span className="text-xs font-medium text-gray-400">
                  DPO Necessário
                </span>
              </div>
              <p
                className={`text-sm font-medium ${
                  result.necessita_dpo ? "text-yellow-500" : "text-[#00cc50]"
                }`}
              >
                {result.necessita_dpo ? "Sim" : "Não"}
              </p>
            </div>

            <div className="card">
              <div className="flex items-center gap-2 mb-2">
                <Building2 size={14} className="text-yellow-500" />
                <span className="text-xs font-medium text-gray-400">
                  Notificar ANPD
                </span>
              </div>
              <p
                className={`text-sm font-medium ${
                  result.necessita_anpd ? "text-yellow-500" : "text-[#00cc50]"
                }`}
              >
                {result.necessita_anpd ? "Sim" : "Não"}
              </p>
            </div>
          </div>

          {/* Required Actions */}
          {result.acoes_requeridas?.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-white mb-3">
                Ações Requeridas
              </h3>
              <ol className="space-y-2">
                {result.acoes_requeridas.map((acao, i) => (
                  <li
                    key={i}
                    className="text-sm text-gray-300 flex items-start gap-2"
                  >
                    <span className="text-[#00cc50] font-mono text-xs mt-0.5 shrink-0">
                      {(i + 1).toString().padStart(2, "0")}
                    </span>
                    {typeof acao === 'string' ? acao : (acao as any)?.acao || (acao as any)?.descricao || JSON.stringify(acao)}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Response to Titular */}
          {result.resposta_ao_titular && (
            <div className="card border border-[#00cc50]/20">
              <h3 className="text-sm font-semibold text-white mb-3">
                Modelo de Resposta ao Titular
              </h3>
              <div className="p-4 rounded-lg bg-[#0d1117]/80 text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                {result.resposta_ao_titular}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

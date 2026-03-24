import { useState } from "react";
import {
  FileText,
  Loader2,
  AlertTriangle,
  Download,
  ShieldCheck,
  ShieldAlert,
  UserCheck,
} from "lucide-react";
import {
  generateDPIA,
  generateDPIAPdf,
  type DPIARequest,
  type DPIAResponse,
} from "../../lib/api";

export default function DPIA() {
  const [form, setForm] = useState<DPIARequest>({
    empresa: "",
    processo: "",
    finalidade: "",
    dados_envolvidos: "",
    medidas_seguranca: "",
  });
  const [loading, setLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DPIAResponse | null>(null);

  function updateField(field: keyof DPIARequest, value: string) {
    setForm({ ...form, [field]: value });
  }

  async function handleSubmit() {
    if (!form.empresa.trim() || !form.processo.trim() || !form.finalidade.trim()) {
      setError("Preencha ao menos empresa, processo e finalidade.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await generateDPIA(form);
      setResult(response);
    } catch (err: any) {
      const msg = err instanceof Error ? err.message
        : typeof err === 'object' ? JSON.stringify(err)
        : String(err);
      setError(msg || "Erro ao gerar DPIA.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDownloadPdf() {
    setPdfLoading(true);
    try {
      const blob = await generateDPIAPdf(form);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `DPIA_${form.empresa.replace(/\s+/g, "_")}_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erro ao gerar PDF."
      );
    } finally {
      setPdfLoading(false);
    }
  }

  function riskColor(risk: string): string {
    const r = risk?.toLowerCase();
    if (r === "alto") return "text-red-500";
    if (r === "medio" || r === "médio") return "text-yellow-500";
    return "text-[#00cc50]";
  }

  function riskBadgeClass(risk: string): string {
    const r = risk?.toLowerCase();
    if (r === "alto") return "risk-badge risk-alto";
    if (r === "medio" || r === "médio") return "risk-badge risk-medio";
    return "risk-badge risk-baixo";
  }

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <FileText size={24} className="text-[#00cc50]" />
          Relatório de Impacto (DPIA)
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Gere um Relatório de Impacto à Proteção de Dados Pessoais conforme
          exigido pela LGPD (Art. 38).
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
            <label className="label-text">Processo</label>
            <input
              type="text"
              className="input-field"
              placeholder="Ex: Cadastro de clientes"
              value={form.processo}
              onChange={(e) => updateField("processo", e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="label-text">Finalidade do Tratamento</label>
          <textarea
            className="input-field min-h-[80px] resize-y"
            placeholder="Descreva a finalidade do tratamento de dados pessoais..."
            value={form.finalidade}
            onChange={(e) => updateField("finalidade", e.target.value)}
          />
        </div>

        <div>
          <label className="label-text">Dados Envolvidos</label>
          <textarea
            className="input-field min-h-[80px] resize-y"
            placeholder="Liste os tipos de dados pessoais tratados (ex: nome, CPF, endereço, dados de saúde...)"
            value={form.dados_envolvidos}
            onChange={(e) => updateField("dados_envolvidos", e.target.value)}
          />
        </div>

        <div>
          <label className="label-text">Medidas de Segurança Existentes</label>
          <textarea
            className="input-field min-h-[80px] resize-y"
            placeholder="Descreva as medidas de segurança já implementadas (ex: criptografia, controle de acesso...)"
            value={form.medidas_seguranca}
            onChange={(e) => updateField("medidas_seguranca", e.target.value)}
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
              Gerando DPIA com IA...
            </>
          ) : (
            <>
              <FileText size={20} />
              Gerar DPIA
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4 fade-in">
          {/* Risk Overview */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-semibold text-white">
                Resultado da Análise
              </h3>
              <span className={riskBadgeClass(result.nivel_risco)}>
                Risco: {result.nivel_risco}
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              <div className="text-center p-3 rounded-lg bg-[#0d1117]/60">
                <div className={`text-xl font-bold ${riskColor(result.nivel_risco)}`}>
                  {result.score_risco}
                </div>
                <div className="text-xs text-gray-400 mt-1">Score de Risco</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-[#0d1117]/60">
                <div className="text-xl font-bold text-white">
                  {result.riscos_identificados?.length || 0}
                </div>
                <div className="text-xs text-gray-400 mt-1">Riscos</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-[#0d1117]/60">
                <div className="text-xl font-bold text-white">
                  {result.medidas_mitigacao?.length || 0}
                </div>
                <div className="text-xs text-gray-400 mt-1">Mitigações</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-[#0d1117]/60">
                <div className={`text-xl font-bold ${result.necessita_dpo ? "text-yellow-500" : "text-[#00cc50]"}`}>
                  {result.necessita_dpo ? "Sim" : "Não"}
                </div>
                <div className="text-xs text-gray-400 mt-1">DPO Necessário</div>
              </div>
            </div>

            {/* Legal Basis */}
            <div className="p-3 rounded-lg bg-[#0d1117]/60 mb-3">
              <div className="flex items-center gap-2 mb-1">
                <ShieldCheck size={14} className="text-[#00cc50]" />
                <span className="text-xs font-medium text-gray-300">
                  Base Legal
                </span>
              </div>
              <p className="text-sm text-white">{result.base_legal}</p>
            </div>

            {result.necessita_dpo && (
              <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                <div className="flex items-center gap-2">
                  <UserCheck size={14} className="text-yellow-500" />
                  <span className="text-sm text-yellow-500 font-medium">
                    Este processo requer a designação de um Encarregado (DPO).
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Risks */}
          {result.riscos_identificados?.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <ShieldAlert size={16} className="text-red-400" />
                Riscos Identificados
              </h3>
              <ul className="space-y-2">
                {result.riscos_identificados.map((risk, i) => (
                  <li
                    key={i}
                    className="text-sm text-gray-300 flex items-start gap-2 p-2 rounded bg-red-500/5 border border-red-500/10"
                  >
                    <AlertTriangle
                      size={14}
                      className="text-red-400 mt-0.5 shrink-0"
                    />
                    {typeof risk === 'string' ? risk : (risk as any)?.risco || (risk as any)?.descricao || JSON.stringify(risk)}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Mitigation */}
          {result.medidas_mitigacao?.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <ShieldCheck size={16} className="text-[#00cc50]" />
                Medidas de Mitigação
              </h3>
              <ul className="space-y-2">
                {result.medidas_mitigacao.map((m, i) => (
                  <li
                    key={i}
                    className="text-sm text-gray-300 flex items-start gap-2"
                  >
                    <span className="text-[#00cc50] mt-0.5">✓</span>
                    {typeof m === 'string' ? m : (m as any)?.medida || (m as any)?.descricao || JSON.stringify(m)}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommendations */}
          {result.recomendacoes?.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-white mb-3">
                Recomendações Adicionais
              </h3>
              <ul className="space-y-2">
                {result.recomendacoes.map((rec, i) => (
                  <li
                    key={i}
                    className="text-sm text-gray-300 flex items-start gap-2"
                  >
                    <span className="text-[#00cc50]">→</span>
                    {typeof rec === 'string' ? rec : (rec as any)?.recomendacao || (rec as any)?.descricao || JSON.stringify(rec)}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Disclaimer */}
          <div className="p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/20">
            <p className="text-[0.65rem] text-gray-500 leading-relaxed">
              ⚠️ <strong className="text-gray-400">Aviso:</strong> Este RIPD é gerado por IA local e tem caráter indicativo.
              Deve ser revisado e validado por DPO ou profissional jurídico qualificado antes de uso oficial.
              Não substitui avaliação humana especializada.
            </p>
          </div>

          {/* PDF Download */}
          <button
            onClick={handleDownloadPdf}
            disabled={pdfLoading}
            className="btn-secondary w-full justify-center py-3"
          >
            {pdfLoading ? (
              <>
                <Loader2 size={18} className="spinner" />
                Gerando PDF...
              </>
            ) : (
              <>
                <Download size={18} />
                Baixar Relatório em PDF
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}

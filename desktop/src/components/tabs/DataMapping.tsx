import { useState } from "react";
import {
  Database,
  Plus,
  Trash2,
  Loader2,
  AlertTriangle,
  CheckCircle,
  ShieldAlert,
} from "lucide-react";
import {
  mapData,
  type DataItem,
  type MapDataResponse,
} from "../../lib/api";

const emptyItem = (): DataItem => ({
  nome: "",
  descricao: "",
  fonte: "",
});

export default function DataMapping() {
  const [empresa, setEmpresa] = useState("");
  const [finalidade, setFinalidade] = useState("");
  const [dados, setDados] = useState<DataItem[]>([emptyItem()]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MapDataResponse | null>(null);

  function addItem() {
    setDados([...dados, emptyItem()]);
  }

  function removeItem(index: number) {
    if (dados.length <= 1) return;
    setDados(dados.filter((_, i) => i !== index));
  }

  function updateItem(index: number, field: keyof DataItem, value: string) {
    const updated = [...dados];
    updated[index] = { ...updated[index], [field]: value };
    setDados(updated);
  }

  async function handleSubmit() {
    if (!empresa.trim() || !finalidade.trim()) {
      setError("Preencha o nome da empresa e a finalidade.");
      return;
    }
    const validItems = dados.filter((d) => d.nome.trim());
    if (validItems.length === 0) {
      setError("Adicione ao menos um item de dado com nome preenchido.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await mapData({
        empresa: empresa.trim(),
        finalidade: finalidade.trim(),
        dados: validItems,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao analisar dados.");
    } finally {
      setLoading(false);
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
          <Database size={24} className="text-[#00cc50]" />
          Mapeamento de Dados
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Mapeie os dados pessoais tratados pela sua organização e receba
          recomendações de conformidade com a LGPD.
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
              value={empresa}
              onChange={(e) => setEmpresa(e.target.value)}
            />
          </div>
          <div>
            <label className="label-text">Finalidade do Tratamento</label>
            <input
              type="text"
              className="input-field"
              placeholder="Ex: Marketing, RH, Vendas..."
              value={finalidade}
              onChange={(e) => setFinalidade(e.target.value)}
            />
          </div>
        </div>

        {/* Data Items */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="label-text mb-0">Itens de Dados</label>
            <button
              onClick={addItem}
              className="btn-secondary text-xs py-1.5 px-3"
            >
              <Plus size={14} />
              Adicionar Item
            </button>
          </div>

          <div className="space-y-3">
            {dados.map((item, i) => (
              <div
                key={i}
                className="grid grid-cols-[1fr_1fr_1fr_auto] gap-2 items-end"
              >
                <div>
                  {i === 0 && (
                    <label className="text-xs text-gray-500 mb-1 block">
                      Nome do Dado
                    </label>
                  )}
                  <input
                    type="text"
                    className="input-field text-sm"
                    placeholder="Ex: CPF"
                    value={item.nome}
                    onChange={(e) => updateItem(i, "nome", e.target.value)}
                  />
                </div>
                <div>
                  {i === 0 && (
                    <label className="text-xs text-gray-500 mb-1 block">
                      Descrição
                    </label>
                  )}
                  <input
                    type="text"
                    className="input-field text-sm"
                    placeholder="Breve descrição"
                    value={item.descricao}
                    onChange={(e) => updateItem(i, "descricao", e.target.value)}
                  />
                </div>
                <div>
                  {i === 0 && (
                    <label className="text-xs text-gray-500 mb-1 block">
                      Fonte
                    </label>
                  )}
                  <input
                    type="text"
                    className="input-field text-sm"
                    placeholder="Ex: Formulário web"
                    value={item.fonte}
                    onChange={(e) => updateItem(i, "fonte", e.target.value)}
                  />
                </div>
                <button
                  onClick={() => removeItem(i)}
                  className="btn-danger"
                  disabled={dados.length <= 1}
                  title="Remover item"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
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
              Analisando com IA...
            </>
          ) : (
            <>
              <Database size={20} />
              Analisar Dados
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4 fade-in">
          {/* Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="card text-center">
              <div className="text-2xl font-bold text-white">
                {result.total_itens}
              </div>
              <div className="text-xs text-gray-400 mt-1">Itens Mapeados</div>
            </div>
            <div className="card text-center">
              <div className="text-2xl font-bold text-yellow-500">
                {result.dados_sensiveis}
              </div>
              <div className="text-xs text-gray-400 mt-1">Dados Sensíveis</div>
            </div>
            <div className="card text-center">
              <div className={`text-2xl font-bold ${riskColor(result.nivel_risco_geral)}`}>
                {result.nivel_risco_geral}
              </div>
              <div className="text-xs text-gray-400 mt-1">Risco Geral</div>
            </div>
            <div className="card text-center">
              <div className="text-2xl font-bold text-[#00cc50]">
                {result.score_conformidade}%
              </div>
              <div className="text-xs text-gray-400 mt-1">Score Conformidade</div>
            </div>
          </div>

          {/* General Recommendations */}
          {result.recomendacoes_gerais?.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <CheckCircle size={16} className="text-[#00cc50]" />
                Recomendações Gerais
              </h3>
              <ul className="space-y-2">
                {result.recomendacoes_gerais.map((rec, i) => (
                  <li
                    key={i}
                    className="text-sm text-gray-300 flex items-start gap-2"
                  >
                    <span className="text-[#00cc50] mt-0.5">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Per-Item Details */}
          <div className="card">
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <ShieldAlert size={16} className="text-[#00cc50]" />
              Detalhes por Item
            </h3>
            <div className="space-y-3">
              {result.itens_mapeados?.map((item, i) => (
                <div
                  key={i}
                  className="p-3 rounded-lg bg-[#0d1117]/60 border border-[#0f3460]/30"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-white text-sm">
                        {item.nome}
                      </span>
                      {item.sensivel && (
                        <span className="text-[0.6rem] px-1.5 py-0.5 bg-yellow-500/15 text-yellow-500 rounded-full border border-yellow-500/30">
                          SENSÍVEL
                        </span>
                      )}
                    </div>
                    <span className={riskBadgeClass(item.nivel_risco)}>
                      {item.nivel_risco}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mb-1">
                    Categoria: <span className="text-gray-300">{item.fonte || "—"}</span> | Base Legal: <span className="text-[#00cc50]">{item.base_legal_sugerida || "Não identificada"}</span>
                  </p>
                  {item.recomendacoes?.length > 0 && (
                    <ul className="mt-2 space-y-1">
                      {item.recomendacoes.map((rec, j) => (
                        <li
                          key={j}
                          className="text-xs text-gray-400 flex items-start gap-1.5"
                        >
                          <span className="text-[#00cc50]">→</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Disclaimer */}
          <div className="p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/20">
            <p className="text-[0.65rem] text-gray-500 leading-relaxed">
              ⚠️ <strong className="text-gray-400">Aviso:</strong> Esta análise é gerada por IA local e tem caráter indicativo.
              Classificações e scores devem ser validados por profissional de compliance ou DPO qualificado.
              Não substitui análise jurídica especializada.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

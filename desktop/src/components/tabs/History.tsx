import { useEffect, useState } from "react";
import {
  History as HistoryIcon,
  Database,
  FileText,
  Shield,
  TrendingUp,
  BarChart3,
  ChevronDown,
  ChevronUp,
  Loader2,
  AlertTriangle,
  Trash2,
  FolderOpen,
  HardDrive,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { getHistory, type HistoryEntry } from "../../lib/api";

export default function History() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [subTab, setSubTab] = useState<"mappings" | "dpias">("mappings");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filterCompany, setFilterCompany] = useState("");
  const [filterRisk, setFilterRisk] = useState("");
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [clearing, setClearing] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  async function loadHistory() {
    setLoading(true);
    setError(null);
    try {
      const response = await getHistory(undefined, undefined, 200);
      setEntries(response.items || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar histórico.");
    } finally {
      setLoading(false);
    }
  }

  const mappings = entries.filter((e) => e.tipo === "mapeamento");
  const dpias = entries.filter((e) => e.tipo === "dpia");

  const totalMappings = mappings.length;
  const totalDPIAs = dpias.length;
  const avgScore =
    mappings.length > 0
      ? Math.round(
          mappings.reduce((sum, m) => sum + (m.score_conformidade || 0), 0) /
            mappings.length
        )
      : 0;

  const riskCounts: Record<string, number> = {};
  entries.forEach((e) => {
    if (e.nivel_risco) {
      const r = e.nivel_risco.toLowerCase();
      riskCounts[r] = (riskCounts[r] || 0) + 1;
    }
  });
  const dominantRisk =
    Object.entries(riskCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || "N/A";

  // Chart data
  const scoreData = mappings
    .slice(-20)
    .map((m) => ({
      date: new Date(m.timestamp).toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
      }),
      score: m.score_conformidade || 0,
    }));

  const riskChartData = Object.entries(riskCounts).map(([risk, count]) => ({
    risk: risk.charAt(0).toUpperCase() + risk.slice(1),
    count,
    fill:
      risk === "alto"
        ? "#ef4444"
        : risk === "medio" || risk === "médio"
        ? "#eab308"
        : "#00cc50",
  }));

  function filteredList() {
    const list = subTab === "mappings" ? mappings : dpias;
    return list.filter((e) => {
      if (filterCompany && !e.empresa.toLowerCase().includes(filterCompany.toLowerCase()))
        return false;
      if (filterRisk && e.nivel_risco?.toLowerCase() !== filterRisk.toLowerCase())
        return false;
      return true;
    });
  }

  function riskBadgeClass(risk: string): string {
    const r = risk?.toLowerCase();
    if (r === "alto") return "risk-badge risk-alto";
    if (r === "medio" || r === "médio") return "risk-badge risk-medio";
    return "risk-badge risk-baixo";
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 size={32} className="text-[#00cc50] spinner" />
      </div>
    );
  }

  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <HistoryIcon size={24} className="text-[#00cc50]" />
            Histórico de Análises
          </h2>
          <p className="text-sm text-gray-400 mt-1">
            Acompanhe o histórico de mapeamentos, DPIAs e a evolução da
            conformidade.
          </p>
        </div>
        <button
          onClick={() => setShowClearConfirm(true)}
          className="text-xs text-gray-500 hover:text-red-400 flex items-center gap-1 transition-colors px-3 py-1.5 rounded-lg hover:bg-red-500/10"
          title="Limpar todos os dados locais"
        >
          <Trash2 size={14} />
          Limpar Dados
        </button>
      </div>

      {/* Clear Data Confirmation */}
      {showClearConfirm && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30">
          <h3 className="text-sm font-semibold text-red-400 flex items-center gap-2 mb-2">
            <AlertTriangle size={16} />
            Confirmar Exclusão de Dados
          </h3>
          <p className="text-xs text-gray-300 mb-2">
            Isso apagará <strong>permanentemente</strong> todo o histórico de mapeamentos, DPIAs,
            DSRs e o banco de dados local. Esta ação não pode ser desfeita.
          </p>
          <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
            <HardDrive size={12} />
            <span>Dados armazenados em: <code className="text-[#00cc50]">~/Library/Application Support/LGPD Sentinel AI/</code></span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={async () => {
                setClearing(true);
                try {
                  const { getBaseUrl, getApiKey } = await import("../../lib/api");
                  const url = await getBaseUrl();
                  const key = getApiKey();
                  await fetch(`${url.replace("/api/v1", "")}/api/v1/history/clear`, {
                    method: "DELETE",
                    headers: key ? { "X-API-Key": key } : {},
                  });
                  setEntries([]);
                  setShowClearConfirm(false);
                } catch {
                  // If API endpoint doesn't exist, inform user
                  alert("Para limpar os dados manualmente, exclua o arquivo:\n~/Library/Application Support/LGPD Sentinel AI/sentinel.db");
                  setShowClearConfirm(false);
                } finally {
                  setClearing(false);
                }
              }}
              disabled={clearing}
              className="px-4 py-2 text-xs bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 border border-red-500/30 transition-colors"
            >
              {clearing ? "Apagando..." : "Sim, Apagar Tudo"}
            </button>
            <button
              onClick={() => setShowClearConfirm(false)}
              className="px-4 py-2 text-xs text-gray-400 rounded-lg hover:bg-[#0f3460]/20 transition-colors"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {/* Data Storage Info */}
      <div className="flex items-center gap-2 text-xs text-gray-600 px-1">
        <FolderOpen size={12} />
        <span>Dados armazenados localmente em <code className="text-gray-500">~/Library/Application Support/LGPD Sentinel AI/sentinel.db</code></span>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 p-3 rounded-lg border border-red-500/20">
          <AlertTriangle size={16} />
          {error}
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="card text-center">
          <Database size={18} className="text-[#00cc50] mx-auto mb-1" />
          <div className="text-2xl font-bold text-white">{totalMappings}</div>
          <div className="text-xs text-gray-400">Mapeamentos</div>
        </div>
        <div className="card text-center">
          <FileText size={18} className="text-[#00cc50] mx-auto mb-1" />
          <div className="text-2xl font-bold text-white">{totalDPIAs}</div>
          <div className="text-xs text-gray-400">DPIAs</div>
        </div>
        <div className="card text-center">
          <TrendingUp size={18} className="text-[#00cc50] mx-auto mb-1" />
          <div className="text-2xl font-bold text-[#00cc50]">{avgScore}%</div>
          <div className="text-xs text-gray-400">Score Médio</div>
        </div>
        <div className="card text-center">
          <BarChart3 size={18} className="text-[#00cc50] mx-auto mb-1" />
          <div className="text-2xl font-bold text-white capitalize">
            {dominantRisk}
          </div>
          <div className="text-xs text-gray-400">Risco Dominante</div>
        </div>
      </div>

      {/* Charts */}
      {entries.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {scoreData.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-white mb-3">
                Evolução do Score de Conformidade
              </h3>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={scoreData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1a2e" />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: "#6b7280", fontSize: 11 }}
                    stroke="#1a1a2e"
                  />
                  <YAxis
                    tick={{ fill: "#6b7280", fontSize: 11 }}
                    stroke="#1a1a2e"
                    domain={[0, 100]}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1a1a2e",
                      border: "1px solid #0f3460",
                      borderRadius: "8px",
                      color: "#e5e7eb",
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#00cc50"
                    strokeWidth={2}
                    dot={{ fill: "#00cc50", r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {riskChartData.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-white mb-3">
                Distribuição de Risco
              </h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={riskChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1a2e" />
                  <XAxis
                    dataKey="risk"
                    tick={{ fill: "#6b7280", fontSize: 11 }}
                    stroke="#1a1a2e"
                  />
                  <YAxis
                    tick={{ fill: "#6b7280", fontSize: 11 }}
                    stroke="#1a1a2e"
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#1a1a2e",
                      border: "1px solid #0f3460",
                      borderRadius: "8px",
                      color: "#e5e7eb",
                    }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {riskChartData.map((entry, index) => (
                      <Bar key={index} dataKey="count" fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {/* Sub-Tabs + Filters */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <button
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              subTab === "mappings"
                ? "bg-[#00cc50]/15 text-[#00cc50] border border-[#00cc50]/30"
                : "text-gray-400 hover:text-gray-300"
            }`}
            onClick={() => setSubTab("mappings")}
          >
            <Database size={14} className="inline mr-1.5" />
            Mapeamentos ({totalMappings})
          </button>
          <button
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              subTab === "dpias"
                ? "bg-[#00cc50]/15 text-[#00cc50] border border-[#00cc50]/30"
                : "text-gray-400 hover:text-gray-300"
            }`}
            onClick={() => setSubTab("dpias")}
          >
            <FileText size={14} className="inline mr-1.5" />
            DPIAs ({totalDPIAs})
          </button>

          <div className="ml-auto flex gap-2">
            <input
              type="text"
              placeholder="Filtrar empresa..."
              className="input-field text-xs py-1.5 w-40"
              value={filterCompany}
              onChange={(e) => setFilterCompany(e.target.value)}
            />
            <select
              className="select-field text-xs py-1.5 w-32"
              value={filterRisk}
              onChange={(e) => setFilterRisk(e.target.value)}
            >
              <option value="">Todos os riscos</option>
              <option value="alto">Alto</option>
              <option value="medio">Médio</option>
              <option value="baixo">Baixo</option>
            </select>
          </div>
        </div>

        {/* List */}
        <div className="space-y-2">
          {filteredList().length === 0 ? (
            <div className="text-center py-8 text-gray-500 text-sm">
              Nenhum registro encontrado.
            </div>
          ) : (
            filteredList().map((entry) => (
              <div
                key={entry.id}
                className="rounded-lg bg-[#0d1117]/60 border border-[#0f3460]/30 overflow-hidden"
              >
                <button
                  className="w-full flex items-center justify-between p-3 text-left hover:bg-[#0f3460]/10 transition-colors"
                  onClick={() =>
                    setExpandedId(expandedId === entry.id ? null : entry.id)
                  }
                >
                  <div className="flex items-center gap-3">
                    {entry.tipo === "mapeamento" ? (
                      <Database size={16} className="text-[#00cc50]" />
                    ) : entry.tipo === "dpia" ? (
                      <FileText size={16} className="text-[#00cc50]" />
                    ) : (
                      <Shield size={16} className="text-[#00cc50]" />
                    )}
                    <div>
                      <span className="text-sm text-white font-medium">
                        {entry.empresa}
                      </span>
                      <span className="text-xs text-gray-500 ml-2">
                        {new Date(entry.timestamp).toLocaleDateString("pt-BR")}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {entry.nivel_risco && (
                      <span className={riskBadgeClass(entry.nivel_risco)}>
                        {entry.nivel_risco}
                      </span>
                    )}
                    {entry.score_conformidade !== undefined && (
                      <span className="text-xs text-[#afffcf]">
                        {entry.score_conformidade}%
                      </span>
                    )}
                    {expandedId === entry.id ? (
                      <ChevronUp size={16} className="text-gray-500" />
                    ) : (
                      <ChevronDown size={16} className="text-gray-500" />
                    )}
                  </div>
                </button>

                {expandedId === entry.id && (
                  <div className="px-3 pb-3 border-t border-[#0f3460]/20 pt-3 fade-in">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-gray-500">Tipo:</span>{" "}
                        <span className="text-gray-300 capitalize">
                          {entry.tipo}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Data:</span>{" "}
                        <span className="text-gray-300">
                          {new Date(entry.timestamp).toLocaleString("pt-BR")}
                        </span>
                      </div>
                      {entry.resumo && (
                        <div className="col-span-2 mt-1">
                          <span className="text-gray-500">Resumo:</span>{" "}
                          <span className="text-gray-300">{entry.resumo}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

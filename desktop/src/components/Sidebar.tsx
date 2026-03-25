import { useEffect, useState } from "react";
import {
  Shield,
  Database,
  FileText,
  History,
  Info,
  Key,
  Copy,
  Check,
  ExternalLink,
  Loader2,
  Github,
  BookOpen,
} from "lucide-react";
import {
  getStatus,
  generateKey,
  setApiKey,
  getApiKey,
  getPlanStatus,
  type StatusResponse,
  type PlanStatus,
} from "../lib/api";

interface SidebarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
}

const tabs = [
  { id: "mapping", label: "Mapeamento", icon: Database },
  { id: "dpia", label: "DPIA", icon: FileText },
  { id: "dsr", label: "DSR", icon: Shield },
  { id: "history", label: "Histórico", icon: History },
  { id: "about", label: "Sobre a LGPD", icon: Info },
];

export default function Sidebar({ currentTab, onTabChange }: SidebarProps) {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [planStatus, setPlanStatus] = useState<PlanStatus | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState(getApiKey() || "");
  const [copied, setCopied] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [showKeySection, setShowKeySection] = useState(false);

  useEffect(() => {
    checkStatus();
    checkPlan();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  async function checkStatus() {
    try {
      const s = await getStatus();
      setStatus(s);
    } catch {
      setStatus(null);
    }
  }

  async function checkPlan() {
    try {
      const p = await getPlanStatus();
      setPlanStatus(p);
    } catch {
      /* ignore */
    }
  }

  async function handleGenerateKey() {
    setGenerating(true);
    try {
      const { api_key } = await generateKey();
      setApiKey(api_key);
      setApiKeyInput(api_key);
      await checkPlan();
    } catch {
      /* ignore */
    } finally {
      setGenerating(false);
    }
  }

  function handleSaveKey() {
    if (apiKeyInput.trim()) {
      setApiKey(apiKeyInput.trim());
      checkPlan();
    }
  }

  function handleCopyKey() {
    navigator.clipboard.writeText(apiKeyInput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const isOnline = status !== null;

  return (
    <aside className="w-64 min-w-64 h-full bg-[#1a1a2e]/90 border-r border-[#0f3460]/50 flex flex-col overflow-y-auto">
      {/* Logo */}
      <div className="p-5 border-b border-[#0f3460]/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00cc50] to-[#0f3460] flex items-center justify-center">
            <Shield size={22} className="text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white leading-tight">
              LGPD Sentinel
            </h1>
            <span className="text-[0.65rem] text-[#afffcf] font-medium tracking-wider uppercase">
              AI Desktop
            </span>
          </div>
        </div>
      </div>

      {/* Status */}
      <div className="px-4 py-3 border-b border-[#0f3460]/30">
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isOnline ? "bg-[#00cc50] shadow-[0_0_6px_#00cc50]" : "bg-red-500 shadow-[0_0_6px_#ef4444]"
            }`}
          />
          <span className="text-xs text-gray-400">
            API {isOnline ? "Online" : "Offline"}
          </span>
          {status?.model_loaded && (
            <span className="ml-auto text-[0.6rem] text-[#afffcf] bg-[#00cc50]/10 px-2 py-0.5 rounded-full">
              {status.model_name}
            </span>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              className={`tab-button ${currentTab === tab.id ? "active" : ""}`}
              onClick={() => onTabChange(tab.id)}
            >
              <Icon size={18} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      {/* API Key Section */}
      <div className="px-4 pb-3">
        <button
          className="flex items-center gap-2 text-xs text-gray-400 hover:text-gray-300 w-full py-2"
          onClick={() => setShowKeySection(!showKeySection)}
        >
          <Key size={14} />
          <span>API Key</span>
          <span className="ml-auto text-[0.6rem]">
            {showKeySection ? "▲" : "▼"}
          </span>
        </button>

        {showKeySection && (
          <div className="space-y-2 fade-in">
            <div className="flex gap-1">
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder="Cole sua API key..."
                className="input-field text-xs py-1.5 flex-1"
              />
              {apiKeyInput && (
                <button
                  onClick={handleCopyKey}
                  className="p-1.5 text-gray-400 hover:text-[#00cc50] transition-colors"
                  title="Copiar"
                >
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                </button>
              )}
            </div>
            <div className="flex gap-1">
              <button
                onClick={handleSaveKey}
                className="flex-1 text-xs py-1.5 bg-[#0f3460]/50 text-gray-300 rounded hover:bg-[#0f3460] transition-colors"
              >
                Salvar
              </button>
              <button
                onClick={handleGenerateKey}
                disabled={generating}
                className="flex-1 text-xs py-1.5 bg-[#00cc50]/20 text-[#00cc50] rounded hover:bg-[#00cc50]/30 transition-colors disabled:opacity-50 flex items-center justify-center gap-1"
              >
                {generating ? (
                  <Loader2 size={12} className="spinner" />
                ) : null}
                Gerar Nova
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Plan Status */}
      {planStatus && (
        <div className="px-4 pb-3">
          <div className="text-[0.65rem] text-gray-500 uppercase tracking-wider mb-1.5">
            PLANO: {planStatus.plan}
          </div>
          <div className="progress-bar">
            <div
              className="progress-bar-fill"
              style={{
                width: `${Math.min(
                  (planStatus.requests_today / planStatus.daily_limit) * 100,
                  100
                )}%`,
              }}
            />
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-[0.6rem] text-gray-500">
              {planStatus.requests_today}/{planStatus.daily_limit} análises hoje
            </span>
            <span className="text-[0.6rem] text-[#afffcf]">
              {planStatus.requests_remaining} restantes
            </span>
          </div>
        </div>
      )}

      {/* Footer Links */}
      <div className="p-4 border-t border-[#0f3460]/30 space-y-2">
        <a
          href="https://github.com/lgpd-sentinel-ai"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
        >
          <Github size={14} />
          <span>GitHub</span>
          <ExternalLink size={10} className="ml-auto" />
        </a>
        <a
          href="https://lgpd-sentinel-ai.github.io/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
        >
          <BookOpen size={14} />
          <span>Documentação</span>
          <ExternalLink size={10} className="ml-auto" />
        </a>
        <div className="text-[0.55rem] text-gray-600 mt-2">
          v{status?.version || "1.0.0"} — 100% Local & Privado
        </div>
      </div>
    </aside>
  );
}

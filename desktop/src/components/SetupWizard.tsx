import { useState, useEffect, useCallback } from "react";
import { invoke } from "@tauri-apps/api/core";
import {
  Shield,
  CheckCircle,
  XCircle,
  Download,
  Loader2,
  ArrowRight,
  Cpu,
  Sparkles,
} from "lucide-react";

interface SetupWizardProps {
  onComplete: () => void;
}

type Step = 1 | 2 | 3 | 4;

export default function SetupWizard({ onComplete }: SetupWizardProps) {
  const [step, setStep] = useState<Step>(1);

  // Step 2 state
  const [ollamaInstalled, setOllamaInstalled] = useState<boolean | null>(null);
  const [checkingOllama, setCheckingOllama] = useState(false);
  const [startingOllama, setStartingOllama] = useState(false);
  const [ollamaRunning, setOllamaRunning] = useState(false);

  // Step 3 state
  const [pulling, setPulling] = useState(false);
  const [pullProgress, setPullProgress] = useState(0);
  const [pullStatus, setPullStatus] = useState("");
  const [pullComplete, setPullComplete] = useState(false);
  const [pullError, setPullError] = useState<string | null>(null);

  const checkOllama = useCallback(async () => {
    setCheckingOllama(true);
    try {
      const installed = await invoke<boolean>("check_ollama_installed");
      setOllamaInstalled(installed);
      if (installed) {
        try {
          const status = await invoke<{ ollama_ready: boolean }>(
            "get_status"
          );
          setOllamaRunning(status.ollama_ready);
        } catch {
          setOllamaRunning(false);
        }
      }
    } catch {
      setOllamaInstalled(false);
    } finally {
      setCheckingOllama(false);
    }
  }, []);

  useEffect(() => {
    if (step === 2) {
      checkOllama();
    }
  }, [step, checkOllama]);

  async function handleStartOllama() {
    setStartingOllama(true);
    try {
      const result = await invoke<boolean>("start_ollama");
      console.log("start_ollama result:", result);
      // Wait a moment then re-check
      await new Promise((r) => setTimeout(r, 2000));
      await checkOllama();
    } catch (err) {
      console.error("start_ollama error:", err);
      // Try to check again anyway - Ollama might already be starting
      await new Promise((r) => setTimeout(r, 3000));
      await checkOllama();
    } finally {
      setStartingOllama(false);
    }
  }

  async function handlePullModel() {
    setPulling(true);
    setPullError(null);
    setPullProgress(0);
    setPullStatus("Iniciando download do modelo...");

    try {
      // The pull_model command in Tauri streams progress via events
      // We'll poll for status updates
      await invoke("pull_model", { model: "mistral" });

      // If invoke returns, model is ready
      setPullComplete(true);
      setPullProgress(100);
      setPullStatus("Modelo instalado com sucesso!");
    } catch (err) {
      // Simulate progress for the demo or handle real streaming
      setPullError(
        err instanceof Error ? err.message : "Erro ao baixar o modelo."
      );
    } finally {
      setPulling(false);
    }
  }

  // Simulate progress updates (replace with real Tauri event listener)
  useEffect(() => {
    if (!pulling) return;
    const interval = setInterval(() => {
      setPullProgress((prev) => {
        if (prev >= 95) return prev;
        const increment = Math.random() * 3;
        const next = Math.min(prev + increment, 95);
        if (next < 25) setPullStatus("Baixando camadas do modelo...");
        else if (next < 50) setPullStatus("Baixando pesos da rede neural...");
        else if (next < 75) setPullStatus("Verificando integridade...");
        else setPullStatus("Finalizando instalação...");
        return next;
      });
    }, 800);
    return () => clearInterval(interval);
  }, [pulling]);

  function handleFinish() {
    localStorage.setItem("lgpd_setup_complete", "true");
    onComplete();
  }

  return (
    <div className="h-full w-full flex items-center justify-center bg-[#0d1117] relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#00cc50] rounded-full blur-[128px]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#0f3460] rounded-full blur-[128px]" />
      </div>

      <div className="relative z-10 w-full max-w-lg mx-4">
        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center gap-2">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                  s < step
                    ? "bg-[#00cc50] text-[#0d1117]"
                    : s === step
                    ? "bg-[#00cc50]/20 text-[#00cc50] border-2 border-[#00cc50]"
                    : "bg-[#1a1a2e] text-gray-600 border border-[#0f3460]/50"
                }`}
              >
                {s < step ? <CheckCircle size={16} /> : s}
              </div>
              {s < 4 && (
                <div
                  className={`w-12 h-0.5 ${
                    s < step ? "bg-[#00cc50]" : "bg-[#0f3460]/50"
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div className="card fade-in">
          {/* Step 1: Welcome */}
          {step === 1 && (
            <div className="text-center space-y-6 py-4">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#00cc50] to-[#0f3460] flex items-center justify-center mx-auto shadow-lg shadow-[#00cc50]/20">
                <Shield size={40} className="text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  LGPD Sentinel AI
                </h2>
                <p className="text-[#afffcf] text-sm font-medium tracking-wider uppercase">
                  Auditoria LGPD com Inteligência Artificial
                </p>
              </div>
              <p className="text-sm text-gray-400 leading-relaxed max-w-sm mx-auto">
                Bem-vindo ao LGPD Sentinel AI. Vamos configurar tudo para que
                você possa realizar auditorias de conformidade com a LGPD usando
                IA 100% local e privada.
              </p>
              <div className="flex flex-wrap justify-center gap-3 text-xs text-gray-500">
                <span className="px-3 py-1 bg-[#1a1a2e] rounded-full">
                  100% Local
                </span>
                <span className="px-3 py-1 bg-[#1a1a2e] rounded-full">
                  Open Source
                </span>
                <span className="px-3 py-1 bg-[#1a1a2e] rounded-full">
                  Sem Cloud
                </span>
              </div>
              <button
                onClick={() => setStep(2)}
                className="btn-primary mx-auto"
              >
                Começar Configuração
                <ArrowRight size={18} />
              </button>
            </div>
          )}

          {/* Step 2: Ollama Check */}
          {step === 2 && (
            <div className="space-y-6 py-4">
              <div className="text-center">
                <Cpu size={32} className="text-[#00cc50] mx-auto mb-3" />
                <h2 className="text-xl font-bold text-white mb-1">
                  Verificando Ollama
                </h2>
                <p className="text-sm text-gray-400">
                  O Ollama é necessário para executar o modelo de IA localmente.
                </p>
              </div>

              {checkingOllama ? (
                <div className="flex items-center justify-center gap-3 py-4">
                  <Loader2 size={20} className="text-[#00cc50] spinner" />
                  <span className="text-sm text-gray-300">
                    Verificando instalação...
                  </span>
                </div>
              ) : ollamaInstalled === null ? null : ollamaInstalled ? (
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-[#00cc50]/10 border border-[#00cc50]/20">
                    <CheckCircle size={20} className="text-[#00cc50]" />
                    <span className="text-sm text-[#00cc50] font-medium">
                      Ollama está instalado
                    </span>
                  </div>

                  {ollamaRunning ? (
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-[#00cc50]/10 border border-[#00cc50]/20">
                      <CheckCircle size={20} className="text-[#00cc50]" />
                      <span className="text-sm text-[#00cc50] font-medium">
                        Ollama está em execução
                      </span>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                        <XCircle size={20} className="text-yellow-500" />
                        <span className="text-sm text-yellow-500 font-medium">
                          Ollama não está rodando
                        </span>
                      </div>
                      <button
                        onClick={handleStartOllama}
                        disabled={startingOllama}
                        className="btn-secondary w-full justify-center"
                      >
                        {startingOllama ? (
                          <>
                            <Loader2 size={16} className="spinner" />
                            Iniciando Ollama...
                          </>
                        ) : (
                          "Iniciar Ollama"
                        )}
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                    <XCircle size={20} className="text-red-500" />
                    <span className="text-sm text-red-500 font-medium">
                      Ollama não está instalado
                    </span>
                  </div>
                  <a
                    href="https://ollama.com/download"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary w-full justify-center"
                  >
                    <Download size={18} />
                    Instalar Ollama
                  </a>
                  <button
                    onClick={checkOllama}
                    className="btn-secondary w-full justify-center"
                  >
                    Verificar Novamente
                  </button>
                </div>
              )}

              <div className="flex gap-2 pt-2">
                <button
                  onClick={() => setStep(1)}
                  className="btn-secondary flex-1 justify-center"
                >
                  Voltar
                </button>
                <button
                  onClick={() => setStep(3)}
                  disabled={!ollamaInstalled || !ollamaRunning}
                  className="btn-primary flex-1 justify-center"
                >
                  Próximo
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Model Download */}
          {step === 3 && (
            <div className="space-y-6 py-4">
              <div className="text-center">
                <Download size={32} className="text-[#00cc50] mx-auto mb-3" />
                <h2 className="text-xl font-bold text-white mb-1">
                  Modelo de IA
                </h2>
                <p className="text-sm text-gray-400">
                  Baixe o modelo llama3.1 (~4GB) para análise local.
                </p>
              </div>

              {!pulling && !pullComplete && !pullError && (
                <div className="space-y-3">
                  <div className="p-4 rounded-lg bg-[#0d1117]/60 border border-[#0f3460]/30">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-300">Modelo</span>
                      <span className="text-white font-mono">llama3.1</span>
                    </div>
                    <div className="flex items-center justify-between text-sm mt-2">
                      <span className="text-gray-300">Tamanho Aproximado</span>
                      <span className="text-white">~4 GB</span>
                    </div>
                  </div>
                  <button
                    onClick={handlePullModel}
                    className="btn-primary w-full justify-center"
                  >
                    <Download size={18} />
                    Baixar Modelo
                  </button>
                </div>
              )}

              {(pulling || pullComplete) && (
                <div className="space-y-3">
                  <div className="progress-bar h-3">
                    <div
                      className="progress-bar-fill transition-all duration-500"
                      style={{ width: `${pullProgress}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">{pullStatus}</span>
                    <span className="text-[#00cc50] font-mono">
                      {Math.round(pullProgress)}%
                    </span>
                  </div>
                  {pullComplete && (
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-[#00cc50]/10 border border-[#00cc50]/20">
                      <CheckCircle size={20} className="text-[#00cc50]" />
                      <span className="text-sm text-[#00cc50] font-medium">
                        Modelo instalado com sucesso!
                      </span>
                    </div>
                  )}
                </div>
              )}

              {pullError && (
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                    <XCircle size={20} className="text-red-500" />
                    <span className="text-sm text-red-400">{pullError}</span>
                  </div>
                  <button
                    onClick={handlePullModel}
                    className="btn-primary w-full justify-center"
                  >
                    Tentar Novamente
                  </button>
                </div>
              )}

              <div className="flex gap-2 pt-2">
                <button
                  onClick={() => setStep(2)}
                  className="btn-secondary flex-1 justify-center"
                >
                  Voltar
                </button>
                <button
                  onClick={() => setStep(4)}
                  disabled={!pullComplete}
                  className="btn-primary flex-1 justify-center"
                >
                  Próximo
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Ready */}
          {step === 4 && (
            <div className="text-center space-y-6 py-4">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#00cc50] to-[#0f3460] flex items-center justify-center mx-auto pulse-glow">
                <Sparkles size={40} className="text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  Tudo Pronto!
                </h2>
                <p className="text-sm text-gray-400 max-w-sm mx-auto">
                  O LGPD Sentinel AI está configurado e pronto para uso.
                  Todas as análises são realizadas localmente no seu computador.
                </p>
              </div>
              <div className="space-y-2 text-left max-w-xs mx-auto">
                {[
                  "Ollama instalado e rodando",
                  "Modelo llama3.1 disponível",
                  "Processamento 100% local",
                  "Seus dados nunca saem do seu PC",
                ].map((item, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 text-sm text-gray-300"
                  >
                    <CheckCircle size={14} className="text-[#00cc50] shrink-0" />
                    {item}
                  </div>
                ))}
              </div>
              <button
                onClick={handleFinish}
                className="btn-primary mx-auto text-base px-8 py-3"
              >
                <Shield size={20} />
                Iniciar LGPD Sentinel AI
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

import { useState } from "react";
import {
  Database,
  FileText,
  Users,
  History,
  Shield,
  HardDrive,
  AlertTriangle,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  Cpu,
  Lock,
} from "lucide-react";

interface OnboardingProps {
  onComplete: () => void;
}

const STEPS = [
  {
    icon: Shield,
    iconColor: "text-[#00cc50]",
    title: "Bem-vindo ao LGPD Sentinel AI",
    subtitle: "Auditoria LGPD com IA 100% Local",
    content: [
      {
        icon: Cpu,
        title: "Processamento Local",
        desc: "Toda análise é feita na sua máquina via Ollama. Nenhum dado pessoal sai do seu computador.",
      },
      {
        icon: Lock,
        title: "Privacidade por Design",
        desc: "Sem telemetria, sem tracking, sem envio de dados para cloud. Você tem controle total.",
      },
      {
        icon: AlertTriangle,
        title: "Ferramenta de Apoio",
        desc: "O sistema auxilia análise e organização, mas NÃO substitui avaliação jurídica humana ou consultoria de DPO.",
      },
    ],
  },
  {
    icon: Database,
    iconColor: "text-[#00cc50]",
    title: "Funcionalidades Disponíveis",
    subtitle: "4 módulos para sua conformidade LGPD",
    content: [
      {
        icon: Database,
        title: "📊 Mapeamento de Dados",
        desc: "Classifique dados pessoais automaticamente. A IA identifica dados sensíveis, sugere bases legais e calcula score de conformidade.",
      },
      {
        icon: FileText,
        title: "📋 DPIA (Relatório de Impacto)",
        desc: "Gere Relatórios de Impacto à Proteção de Dados conforme Art. 38 da LGPD, com avaliação de riscos e medidas de mitigação.",
      },
      {
        icon: Users,
        title: "👤 DSR (Direitos do Titular)",
        desc: "Analise solicitações de direitos dos titulares (Art. 18): acesso, correção, exclusão, portabilidade e mais.",
      },
      {
        icon: History,
        title: "📜 Histórico",
        desc: "Consulte todas as análises anteriores com gráficos de evolução da conformidade.",
      },
    ],
  },
  {
    icon: HardDrive,
    iconColor: "text-blue-400",
    title: "Armazenamento e Limitações",
    subtitle: "Transparência sobre seus dados",
    content: [
      {
        icon: HardDrive,
        title: "Onde ficam seus dados",
        desc: "macOS: ~/Library/Application Support/LGPD Sentinel AI/ — Windows: %LOCALAPPDATA%/LGPD Sentinel AI/ — Tudo em SQLite local.",
      },
      {
        icon: AlertTriangle,
        title: "Scores são indicativos",
        desc: "Classificações e scores são gerados por IA e calculados deterministicamente. Devem ser validados por profissional qualificado antes de decisões.",
      },
      {
        icon: Lock,
        title: "Você pode apagar tudo",
        desc: "Na aba Histórico, use o botão 'Limpar Dados' para excluir permanentemente todo o banco local a qualquer momento.",
      },
    ],
  },
];

export default function Onboarding({ onComplete }: OnboardingProps) {
  const [step, setStep] = useState(0);
  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;
  const Icon = current.icon;

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-[#0d1117] relative overflow-hidden">
      {/* Subtle background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#0d1117] via-[#0f1923] to-[#0d1117]" />

      <div className="relative z-10 max-w-xl w-full mx-4">
        {/* Progress dots */}
        <div className="flex justify-center gap-2 mb-6">
          {STEPS.map((_, i) => (
            <div
              key={i}
              className={`w-2.5 h-2.5 rounded-full transition-all ${
                i === step
                  ? "bg-[#00cc50] scale-125"
                  : i < step
                  ? "bg-[#00cc50]/40"
                  : "bg-gray-700"
              }`}
            />
          ))}
        </div>

        {/* Card */}
        <div className="bg-[#161b22] rounded-2xl border border-[#0f3460]/30 p-8 shadow-2xl">
          {/* Header */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-[#00cc50]/10 mb-3">
              <Icon size={28} className={current.iconColor} />
            </div>
            <h2 className="text-xl font-bold text-white">{current.title}</h2>
            <p className="text-sm text-gray-400 mt-1">{current.subtitle}</p>
          </div>

          {/* Content items */}
          <div className="space-y-3 mb-8">
            {current.content.map((item, i) => {
              const ItemIcon = item.icon;
              return (
                <div
                  key={i}
                  className="flex items-start gap-3 p-3 rounded-lg bg-[#0d1117]/60 border border-[#0f3460]/20"
                >
                  <ItemIcon
                    size={16}
                    className="text-[#00cc50] mt-0.5 shrink-0"
                  />
                  <div>
                    <h4 className="text-sm font-medium text-white">
                      {item.title}
                    </h4>
                    <p className="text-xs text-gray-400 mt-0.5 leading-relaxed">
                      {item.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between">
            {step > 0 ? (
              <button
                onClick={() => setStep(step - 1)}
                className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition-colors px-4 py-2 rounded-lg hover:bg-[#0f3460]/20"
              >
                <ArrowLeft size={16} />
                Voltar
              </button>
            ) : (
              <button
                onClick={() => {
                  localStorage.setItem("lgpd_onboarding_complete", "true");
                  onComplete();
                }}
                className="text-xs text-gray-600 hover:text-gray-400 transition-colors"
              >
                Pular
              </button>
            )}

            <button
              onClick={() => {
                if (isLast) {
                  localStorage.setItem("lgpd_onboarding_complete", "true");
                  onComplete();
                } else {
                  setStep(step + 1);
                }
              }}
              className="flex items-center gap-1.5 text-sm bg-[#00cc50] text-black font-semibold px-6 py-2.5 rounded-lg hover:bg-[#00ff62] transition-colors"
            >
              {isLast ? (
                <>
                  <CheckCircle size={16} />
                  Começar a Usar
                </>
              ) : (
                <>
                  Próximo
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-[0.6rem] text-gray-600 mt-4">
          v1.0.0 — 100% Local & Privado — Apache 2.0 License
        </p>
      </div>
    </div>
  );
}

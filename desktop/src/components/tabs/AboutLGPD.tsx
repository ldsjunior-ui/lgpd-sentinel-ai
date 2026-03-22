import { Info, Scale, Users, Lock, AlertTriangle, BookOpen } from "lucide-react";

const LEGAL_BASES = [
  {
    base: "Consentimento",
    artigo: "Art. 7°, I",
    descricao: "Manifestação livre, informada e inequívoca do titular.",
  },
  {
    base: "Obrigação Legal",
    artigo: "Art. 7°, II",
    descricao:
      "Cumprimento de obrigação legal ou regulatória pelo controlador.",
  },
  {
    base: "Políticas Públicas",
    artigo: "Art. 7°, III",
    descricao:
      "Execução de políticas públicas pela administração pública.",
  },
  {
    base: "Estudos por Órgão de Pesquisa",
    artigo: "Art. 7°, IV",
    descricao: "Realização de estudos por órgão de pesquisa.",
  },
  {
    base: "Execução de Contrato",
    artigo: "Art. 7°, V",
    descricao:
      "Execução de contrato ou de procedimentos preliminares a pedido do titular.",
  },
  {
    base: "Exercício de Direitos",
    artigo: "Art. 7°, VI",
    descricao: "Exercício regular de direitos em processo judicial ou administrativo.",
  },
  {
    base: "Proteção da Vida",
    artigo: "Art. 7°, VII",
    descricao: "Proteção da vida ou da incolumidade física do titular ou de terceiro.",
  },
  {
    base: "Tutela da Saúde",
    artigo: "Art. 7°, VIII",
    descricao: "Tutela da saúde, exclusivamente, em procedimento realizado por profissionais de saúde.",
  },
  {
    base: "Legítimo Interesse",
    artigo: "Art. 7°, IX",
    descricao:
      "Interesses legítimos do controlador ou de terceiro, exceto quando prevalecerem direitos do titular.",
  },
  {
    base: "Proteção ao Crédito",
    artigo: "Art. 7°, X",
    descricao: "Proteção do crédito, inclusive quanto ao disposto na legislação pertinente.",
  },
];

const SENSITIVE_DATA = [
  "Origem racial ou étnica",
  "Convicção religiosa",
  "Opinião política",
  "Filiação a sindicato ou organização de caráter religioso, filosófico ou político",
  "Dados referentes à saúde ou à vida sexual",
  "Dados genéticos ou biométricos",
];

export default function AboutLGPD() {
  return (
    <div className="space-y-6 fade-in">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Info size={24} className="text-[#00cc50]" />
          Sobre a LGPD
        </h2>
        <p className="text-sm text-gray-400 mt-1">
          Informações essenciais sobre a Lei Geral de Proteção de Dados Pessoais
          (Lei n.° 13.709/2018).
        </p>
      </div>

      {/* What is LGPD */}
      <div className="card">
        <h3 className="text-base font-semibold text-white flex items-center gap-2 mb-3">
          <Scale size={18} className="text-[#00cc50]" />
          O que é a LGPD?
        </h3>
        <p className="text-sm text-gray-300 leading-relaxed">
          A Lei Geral de Proteção de Dados Pessoais (LGPD) é a legislação
          brasileira que regula o tratamento de dados pessoais por pessoas
          físicas e jurídicas, públicas ou privadas. Em vigor desde setembro de
          2020, a lei estabelece regras claras sobre coleta, armazenamento,
          tratamento e compartilhamento de dados pessoais, garantindo maior
          proteção e penalidades para o não cumprimento.
        </p>
        <p className="text-sm text-gray-300 leading-relaxed mt-2">
          Inspirada no Regulamento Geral de Proteção de Dados (GDPR) da União
          Europeia, a LGPD visa proteger os direitos fundamentais de liberdade e
          de privacidade dos cidadãos brasileiros.
        </p>
      </div>

      {/* Key Obligations */}
      <div className="card">
        <h3 className="text-base font-semibold text-white flex items-center gap-2 mb-3">
          <Users size={18} className="text-[#00cc50]" />
          Principais Obrigações
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            {
              title: "Transparência",
              desc: "Informar ao titular como, por que e por quanto tempo seus dados serão tratados.",
            },
            {
              title: "Finalidade",
              desc: "Tratar dados apenas para propósitos legítimos, específicos e informados ao titular.",
            },
            {
              title: "Necessidade",
              desc: "Limitar o tratamento ao mínimo necessário para atingir a finalidade.",
            },
            {
              title: "Segurança",
              desc: "Adotar medidas técnicas e administrativas para proteger os dados pessoais.",
            },
            {
              title: "Prevenção",
              desc: "Implementar medidas para prevenir danos ao titular dos dados.",
            },
            {
              title: "Responsabilização",
              desc: "Demonstrar eficácia das medidas de proteção de dados adotadas.",
            },
          ].map((item, i) => (
            <div
              key={i}
              className="p-3 rounded-lg bg-[#0d1117]/60 border border-[#0f3460]/30"
            >
              <h4 className="text-sm font-medium text-[#00cc50] mb-1">
                {item.title}
              </h4>
              <p className="text-xs text-gray-400">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Legal Bases Table */}
      <div className="card">
        <h3 className="text-base font-semibold text-white flex items-center gap-2 mb-3">
          <BookOpen size={18} className="text-[#00cc50]" />
          Bases Legais para Tratamento (Art. 7°)
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#0f3460]/50">
                <th className="text-left py-2 px-3 text-gray-400 font-medium text-xs">
                  Base Legal
                </th>
                <th className="text-left py-2 px-3 text-gray-400 font-medium text-xs">
                  Artigo
                </th>
                <th className="text-left py-2 px-3 text-gray-400 font-medium text-xs">
                  Descrição
                </th>
              </tr>
            </thead>
            <tbody>
              {LEGAL_BASES.map((item, i) => (
                <tr
                  key={i}
                  className="border-b border-[#0f3460]/20 hover:bg-[#0f3460]/10"
                >
                  <td className="py-2 px-3 text-[#00cc50] font-medium text-xs">
                    {item.base}
                  </td>
                  <td className="py-2 px-3 text-gray-300 text-xs font-mono">
                    {item.artigo}
                  </td>
                  <td className="py-2 px-3 text-gray-400 text-xs">
                    {item.descricao}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sensitive Data */}
      <div className="card">
        <h3 className="text-base font-semibold text-white flex items-center gap-2 mb-3">
          <Lock size={18} className="text-yellow-500" />
          Dados Sensíveis (Art. 11)
        </h3>
        <p className="text-sm text-gray-400 mb-3">
          A LGPD define categorias especiais de dados pessoais que requerem
          proteção reforçada:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {SENSITIVE_DATA.map((item, i) => (
            <div
              key={i}
              className="flex items-center gap-2 text-sm text-gray-300 p-2 rounded bg-yellow-500/5 border border-yellow-500/10"
            >
              <AlertTriangle size={12} className="text-yellow-500 shrink-0" />
              {item}
            </div>
          ))}
        </div>
      </div>

      {/* Rights of the Data Subject */}
      <div className="card">
        <h3 className="text-base font-semibold text-white flex items-center gap-2 mb-3">
          <Users size={18} className="text-[#00cc50]" />
          Direitos do Titular (Arts. 17-22)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {[
            "Confirmação da existência de tratamento",
            "Acesso aos dados",
            "Correção de dados incompletos ou desatualizados",
            "Anonimização, bloqueio ou eliminação de dados desnecessários",
            "Portabilidade dos dados",
            "Eliminação dos dados tratados com consentimento",
            "Informação sobre compartilhamento de dados",
            "Informação sobre possibilidade de não fornecer consentimento",
            "Revogação do consentimento",
            "Oposição ao tratamento",
          ].map((right, i) => (
            <div
              key={i}
              className="flex items-start gap-2 text-sm text-gray-300 p-2"
            >
              <span className="text-[#00cc50] mt-0.5">•</span>
              {right}
            </div>
          ))}
        </div>
      </div>

      {/* Penalties */}
      <div className="card border border-red-500/20">
        <h3 className="text-base font-semibold text-white flex items-center gap-2 mb-3">
          <AlertTriangle size={18} className="text-red-500" />
          Penalidades (Art. 52)
        </h3>
        <div className="space-y-2 text-sm text-gray-300">
          <p>
            A ANPD (Autoridade Nacional de Proteção de Dados) pode aplicar
            sanções administrativas que incluem:
          </p>
          <ul className="space-y-1 ml-4">
            <li className="flex items-start gap-2">
              <span className="text-red-400">•</span>
              Advertência com prazo para adoção de medidas corretivas
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400">•</span>
              Multa simples de até 2% do faturamento (limitada a R$ 50 milhões por infração)
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400">•</span>
              Multa diária
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400">•</span>
              Publicização da infração
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400">•</span>
              Bloqueio ou eliminação dos dados pessoais
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400">•</span>
              Suspensão parcial ou total do funcionamento do banco de dados
            </li>
          </ul>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="p-4 rounded-lg bg-[#0f3460]/20 border border-[#0f3460]/30">
        <p className="text-xs text-gray-500 leading-relaxed">
          <strong className="text-gray-400">Aviso Legal:</strong> As informações
          apresentadas nesta seção têm caráter informativo e educacional. O LGPD
          Sentinel AI é uma ferramenta de auxílio e não substitui a consultoria
          jurídica especializada. Para questões específicas sobre conformidade
          com a LGPD, consulte um advogado especializado em proteção de dados.
        </p>
      </div>
    </div>
  );
}

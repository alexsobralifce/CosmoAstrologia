import React, { useState } from 'react';
import { UIIcons } from './ui-icons';
import { zodiacSigns } from './zodiac-icons';
import { BirthChartWheel } from './birth-chart-wheel';
import { apiService } from '../services/api';
import { useLanguage } from '../i18n';
import { OnboardingData } from './onboarding';
import { formatGroqText } from '../utils/formatGroqText';
import { generateBirthChartPDF } from '../utils/generateBirthChartPDF';
import { formatTriadContent } from '../utils/formatTriadContent';

// ===== TIPOS =====
interface BirthChartSection {
  section: string;
  title: string;
  content: string;
  generated_by: string;
}

interface FullBirthChartProps {
  userData: OnboardingData;
  onBack: () => void;
}

// ===== COMPONENTE DE SEÇÃO INDIVIDUAL =====
const ChartSection = ({ 
  section, 
  isLoading, 
  isExpanded, 
  onToggle,
  icon: Icon,
  accentColor 
}: { 
  section: BirthChartSection | null;
  isLoading: boolean;
  isExpanded: boolean;
  onToggle: () => void;
  icon: React.ComponentType<{ size: number; className?: string }>;
  accentColor: string;
}) => {
  const { language } = useLanguage();
  
  if (!section && !isLoading) return null;
  
  // Formatar conteúdo especificamente para a tríade fundamental e power
  const formattedContent = (section?.section === 'triad' || section?.section === 'power') && section?.content
    ? section.section === 'triad' 
      ? formatTriadContent(section.content)
      : formatTriadContent(section.content) // Usar mesma formatação para power
    : section?.content || '';
  
  return (
    <div className={`birth-chart-section-card ${isExpanded ? 'expanded' : ''}`}>
      <button
        onClick={onToggle}
        className="birth-chart-section-button"
      >
        <div className="birth-chart-section-header">
          <div className={`birth-chart-section-icon-container ${accentColor}`}>
            <Icon size={24} className="text-primary-foreground" />
          </div>
          <div className="birth-chart-section-title-container">
            <h3 className="birth-chart-section-title">
              {section?.title || (language === 'pt' ? 'Carregando...' : 'Loading...')}
            </h3>
            {!isExpanded && section?.content && (
              <p className="birth-chart-section-preview">
                {section.content.substring(0, 100)}...
              </p>
            )}
          </div>
        </div>
        <div className="birth-chart-section-actions">
          {isLoading && (
            <div className="birth-chart-section-spinner"></div>
          )}
          <UIIcons.ChevronDown 
            size={24} 
            className="birth-chart-section-chevron" 
          />
        </div>
      </button>
      
      {isExpanded && (
        <div className="birth-chart-section-content">
          {isLoading ? (
            <div className="birth-chart-section-loading">
              <div className="birth-chart-section-loading-line"></div>
              <div className="birth-chart-section-loading-line w-5-6"></div>
              <div className="birth-chart-section-loading-line w-4-6"></div>
              <div className="birth-chart-section-loading-line"></div>
              <div className="birth-chart-section-loading-line w-3-4"></div>
            </div>
          ) : (
            <div className="birth-chart-section-text">
              {formatGroqText(formattedContent)}
            </div>
          )}
          
          {section?.generated_by === 'groq' && (
            <div className="birth-chart-section-footer">
              <UIIcons.Sparkles size={14} />
              <span>{language === 'pt' ? 'Interpretação gerada por IA com base em fontes astrológicas' : 'AI-generated interpretation based on astrological sources'}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ===== COMPONENTE PRINCIPAL =====
export const FullBirthChartSection = ({ userData, onBack }: FullBirthChartProps) => {
  const { language } = useLanguage();
  const [sections, setSections] = useState<Record<string, BirthChartSection | null>>({
    power: null,
    triad: null,
    personal: null,
    houses: null,
    karma: null,
    synthesis: null,
  });
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({
    power: false,
    triad: false,
    personal: false,
    houses: false,
    karma: false,
    synthesis: false,
  });
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    power: false,
    triad: false,
    personal: false,
    houses: false,
    karma: false,
    synthesis: false,
  });
  const [isGeneratingAll, setIsGeneratingAll] = useState(false);

  // Dados do usuário
  const sunSign = userData.sunSign || 'Áries';
  const moonSign = userData.moonSign || 'Touro';
  const ascendant = userData.ascendant || 'Gêmeos';
  
  // Função para gerar uma seção individual
  const generateSection = async (sectionKey: string) => {
    if (loadingStates[sectionKey] || sections[sectionKey]) return;
    
    setLoadingStates(prev => ({ ...prev, [sectionKey]: true }));
    
    try {
      // Formatar birthDate para string se for Date
      const birthDateStr = typeof userData.birthDate === 'string' 
        ? userData.birthDate 
        : userData.birthDate instanceof Date 
          ? userData.birthDate.toLocaleDateString('pt-BR')
          : '01/01/1990';
      
      const response = await apiService.generateBirthChartSection({
        name: userData.name || 'Usuário',
        birthDate: birthDateStr,
        birthTime: userData.birthTime || '12:00',
        birthPlace: userData.birthPlace || 'São Paulo, Brasil',
        sunSign,
        moonSign,
        ascendant,
        sunHouse: 1,
        moonHouse: 4,
        section: sectionKey,
        language,
        // ===== PLANETAS PESSOAIS (Nível 2) =====
        mercurySign: userData.mercurySign,
        mercuryHouse: userData.mercuryHouse,
        venusSign: userData.venusSign,
        venusHouse: userData.venusHouse,
        marsSign: userData.marsSign,
        marsHouse: userData.marsHouse,
        // ===== PLANETAS SOCIAIS (Nível 3) =====
        jupiterSign: userData.jupiterSign,
        jupiterHouse: userData.jupiterHouse,
        saturnSign: userData.saturnSign,
        saturnHouse: userData.saturnHouse,
        // ===== PLANETAS TRANSPESSOAIS (Nível 4) =====
        uranusSign: userData.uranusSign,
        uranusHouse: userData.uranusHouse,
        neptuneSign: userData.neptuneSign,
        neptuneHouse: userData.neptuneHouse,
        plutoSign: userData.plutoSign,
        plutoHouse: userData.plutoHouse,
        // ===== PONTOS KÁRMICOS (Nível 3-4) =====
        northNodeSign: userData.northNodeSign,
        northNodeHouse: userData.northNodeHouse,
        southNodeSign: userData.southNodeSign,
        southNodeHouse: userData.southNodeHouse,
        chironSign: userData.chironSign,
        chironHouse: userData.chironHouse,
        // ===== ÂNGULOS DO MAPA =====
        midheavenSign: userData.midheavenSign,
        icSign: userData.icSign,
      });
      
      setSections(prev => ({ ...prev, [sectionKey]: response }));
    } catch (error) {
      console.error(`Erro ao gerar seção ${sectionKey}:`, error);
      setSections(prev => ({
        ...prev,
        [sectionKey]: {
          section: sectionKey,
          title: sectionKey,
          content: language === 'pt' 
            ? 'Não foi possível gerar esta análise no momento. Por favor, tente novamente.'
            : 'Could not generate this analysis at the moment. Please try again.',
          generated_by: 'error'
        }
      }));
    } finally {
      setLoadingStates(prev => ({ ...prev, [sectionKey]: false }));
    }
  };

  // Função para gerar todas as seções
  const generateAllSections = async () => {
    setIsGeneratingAll(true);
    const sectionKeys = ['power', 'triad', 'personal', 'houses', 'karma', 'synthesis'];
    
    for (const key of sectionKeys) {
      if (!sections[key]) {
        await generateSection(key);
        // Pequena pausa entre requisições para não sobrecarregar
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }
    
    setIsGeneratingAll(false);
  };

  // Toggle de seção expandida
  const toggleSection = (sectionKey: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionKey]: !prev[sectionKey]
    }));
    
    // Se expandindo e não tem conteúdo, gerar
    // EXCETO para 'power' que só deve ser gerada com "Gerar Análise Completa"
    if (!expandedSections[sectionKey] && !sections[sectionKey] && sectionKey !== 'power') {
      generateSection(sectionKey);
    }
    // Para 'power', apenas expandir mas não gerar automaticamente
    // O usuário deve clicar em "Gerar Análise Completa" para gerar 'power'
  };

  // Não gerar nenhuma seção automaticamente - apenas quando solicitado
  // useEffect removido - seções só são geradas quando:
  // 1. Usuário expande manualmente uma seção
  // 2. Usuário clica em "Gerar Análise Completa"

  // Configuração das seções
  const sectionConfig = [
    {
      key: 'power',
      icon: UIIcons.Zap,
      accentColor: 'bg-gradient-to-br from-yellow-500 to-orange-500',
      titlePt: 'A Estrutura de Poder',
      titleEn: 'The Power Structure',
      descPt: 'Temperamento, motivação e regente do mapa',
      descEn: 'Temperament, motivation and chart ruler',
    },
    {
      key: 'triad',
      icon: UIIcons.Sun,
      accentColor: 'bg-gradient-to-br from-orange-500 to-amber-500',
      titlePt: 'A Tríade Fundamental',
      titleEn: 'The Fundamental Triad',
      descPt: 'Sol, Lua e Ascendente - O núcleo da personalidade',
      descEn: 'Sun, Moon and Ascendant - The core of personality',
    },
    {
      key: 'personal',
      icon: UIIcons.Star,
      accentColor: 'bg-gradient-to-br from-purple-500 to-pink-500',
      titlePt: 'Dinâmica Pessoal e Ferramentas',
      titleEn: 'Personal Dynamics and Tools',
      descPt: 'Mercúrio, Vênus e Marte como ferramentas',
      descEn: 'Mercury, Venus and Mars as tools',
    },
    {
      key: 'houses',
      icon: UIIcons.Home,
      accentColor: 'bg-gradient-to-br from-blue-500 to-indigo-500',
      titlePt: 'Análise Setorial Avançada',
      titleEn: 'Advanced Sectorial Analysis',
      descPt: 'Casas, regentes e áreas da vida prática',
      descEn: 'Houses, rulers and practical life areas',
    },
    {
      key: 'karma',
      icon: UIIcons.Compass,
      accentColor: 'bg-gradient-to-br from-purple-500 to-violet-500',
      titlePt: 'Expansão, Estrutura e Karma',
      titleEn: 'Expansion, Structure and Karma',
      descPt: 'Júpiter, Saturno, Nodos, Quíron e Lilith',
      descEn: 'Jupiter, Saturn, Nodes, Chiron and Lilith',
    },
    {
      key: 'synthesis',
      icon: UIIcons.Sparkles,
      accentColor: 'bg-gradient-to-br from-amber-500 to-orange-500',
      titlePt: 'Síntese e Orientação Estratégica',
      titleEn: 'Strategic Synthesis and Guidance',
      descPt: 'Pontos fortes, desafios e conselho final',
      descEn: 'Strengths, challenges and final counsel',
    },
  ];

  // Ícones dos signos
  const SunIcon = zodiacSigns.find(z => z.name === sunSign)?.icon || zodiacSigns[0].icon;
  const MoonIcon = zodiacSigns.find(z => z.name === moonSign)?.icon || zodiacSigns[0].icon;
  const AscIcon = zodiacSigns.find(z => z.name === ascendant)?.icon || zodiacSigns[0].icon;

  return (
    <div className="dashboard-section-container birth-chart-container">
      {/* Header */}
      <div className="birth-chart-header">
        <div className="birth-chart-header-content">
          <h2 className="birth-chart-title">
            {language === 'pt' ? 'Meu Mapa Astral Completo' : 'My Complete Birth Chart'}
          </h2>
          <p className="birth-chart-subtitle">
            {language === 'pt' 
              ? 'Uma análise profunda e personalizada da sua carta natal'
              : 'A deep and personalized analysis of your birth chart'}
          </p>
        </div>
        <div className="birth-chart-header-actions">
          <button
            onClick={generateAllSections}
            disabled={isGeneratingAll}
            className="birth-chart-generate-button"
          >
            <div className="birth-chart-generate-button-shine"></div>
            {isGeneratingAll ? (
              <>
                <div className="birth-chart-generate-button-spinner"></div>
                <span className="birth-chart-generate-button-text">
                  {language === 'pt' ? 'Gerando análise...' : 'Generating analysis...'}
                </span>
              </>
            ) : (
              <>
                <div className="birth-chart-generate-button-icon">
                  <UIIcons.Sparkles size={14} style={{ color: '#160F24' }} />
                </div>
                <span className="birth-chart-generate-button-text">
                  {language === 'pt' ? 'Gerar Análise Completa' : 'Generate Complete Analysis'}
                </span>
                <UIIcons.ChevronRight size={18} className="birth-chart-generate-button-chevron" style={{ color: '#160F24' }} />
              </>
            )}
          </button>
          <button
            onClick={onBack}
            className="birth-chart-back-button"
          >
            <UIIcons.ArrowLeft size={18} />
            {language === 'pt' ? 'Voltar' : 'Back'}
          </button>
        </div>
      </div>

      {/* Resumo do Mapa */}
      <div className="birth-chart-summary">
        <div className="birth-chart-summary-content">
          {/* Wheel Preview */}
          <div className="birth-chart-wheel-container">
            <div className="birth-chart-wheel-wrapper">
              <BirthChartWheel userData={userData} size={280} />
            </div>
          </div>
          
          {/* Info Cards */}
          <div className="birth-chart-info">
            <div className="birth-chart-user-info">
              <UIIcons.User size={16} />
              <span className="birth-chart-user-name">{userData.name}</span>
              <span>•</span>
              <span>
                {typeof userData.birthDate === 'string' 
                  ? userData.birthDate 
                  : userData.birthDate instanceof Date 
                    ? userData.birthDate.toLocaleDateString() 
                    : 'Data não informada'} {language === 'pt' ? 'às' : 'at'} {userData.birthTime || '12:00'}
              </span>
              <span>•</span>
              <span>{userData.birthPlace || 'Local não informado'}</span>
            </div>
            
            {/* Cards Sol, Lua e Ascendente - sempre lado a lado */}
            <div className="birth-chart-planets-cards">
              {/* Sol */}
              <div className="birth-chart-planet-card birth-chart-planet-card-sun">
                <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-sun">
                  <SunIcon size={28} className="text-foreground" />
                </div>
                <div>
                  <p className="birth-chart-planet-label">
                    {language === 'pt' ? 'Sol' : 'Sun'}
                  </p>
                  <p className="birth-chart-planet-sign">{sunSign}</p>
                </div>
                <p className="birth-chart-planet-desc">
                  {language === 'pt' ? 'Sua essência e identidade' : 'Your essence and identity'}
                </p>
              </div>
              
              {/* Lua */}
              <div className="birth-chart-planet-card birth-chart-planet-card-moon">
                <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-moon">
                  <MoonIcon size={28} className="text-foreground" />
                </div>
                <div>
                  <p className="birth-chart-planet-label">
                    {language === 'pt' ? 'Lua' : 'Moon'}
                  </p>
                  <p className="birth-chart-planet-sign">{moonSign}</p>
                </div>
                <p className="birth-chart-planet-desc">
                  {language === 'pt' ? 'Suas emoções e necessidades' : 'Your emotions and needs'}
                </p>
              </div>
              
              {/* Ascendente */}
              <div className="birth-chart-planet-card birth-chart-planet-card-asc">
                <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-asc">
                  <AscIcon size={28} className="text-foreground" />
                </div>
                <div>
                  <p className="birth-chart-planet-label">
                    {language === 'pt' ? 'Asc' : 'Asc'}
                  </p>
                  <p className="birth-chart-planet-sign">{ascendant}</p>
                </div>
                <p className="birth-chart-planet-desc">
                  {language === 'pt' ? 'Sua máscara social' : 'Your social mask'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Seções do Mapa */}
      <div className="birth-chart-sections">
        <h3 className="birth-chart-sections-title">
          <UIIcons.BookOpen size={24} className="text-primary" />
          {language === 'pt' ? 'Análise Completa' : 'Complete Analysis'}
        </h3>
        
        <p className="birth-chart-sections-description">
          {language === 'pt' 
            ? 'Clique em cada seção para expandir e ler a análise detalhada. Cada seção é gerada individualmente com base nos seus dados de nascimento.'
            : 'Click on each section to expand and read the detailed analysis. Each section is generated individually based on your birth data.'}
        </p>
        
        <div className="birth-chart-sections-list">
          {sectionConfig.map((config) => (
            <ChartSection
              key={config.key}
              section={sections[config.key]}
              isLoading={loadingStates[config.key]}
              isExpanded={expandedSections[config.key]}
              onToggle={() => toggleSection(config.key)}
              icon={config.icon}
              accentColor={config.accentColor}
            />
          ))}
        </div>
      </div>

      {/* Nota Final */}
      <div className="birth-chart-note">
        <div className="birth-chart-note-content">
          <div className="birth-chart-note-icon">
            <UIIcons.Info size={20} className="text-primary" />
          </div>
          <div className="birth-chart-note-text">
            <h4 className="birth-chart-note-title">
              {language === 'pt' ? 'Sobre esta análise' : 'About this analysis'}
            </h4>
            <p className="birth-chart-note-description">
              {language === 'pt' 
                ? 'Esta interpretação foi gerada usando inteligência artificial treinada em fontes astrológicas tradicionais, combinando Astrologia Psicológica (linha Junguiana) e Astrologia Evolutiva. As análises focam no potencial de crescimento e livre-arbítrio, evitando determinismos. Use estas informações como ferramenta de autoconhecimento.'
                : 'This interpretation was generated using artificial intelligence trained on traditional astrological sources, combining Psychological Astrology (Jungian approach) and Evolutionary Astrology. The analyses focus on growth potential and free will, avoiding determinism. Use this information as a self-knowledge tool.'}
            </p>
          </div>
        </div>
      </div>

      {/* Botão de Gerar PDF */}
      <div className="birth-chart-pdf-section">
        <button
          onClick={() => {
            // Verificar se há pelo menos uma seção gerada
            const hasAnySection = Object.values(sections).some(section => section !== null && section.content);
            
            if (!hasAnySection) {
              alert(language === 'pt' 
                ? 'Por favor, gere pelo menos uma seção do mapa astral antes de exportar para PDF.'
                : 'Please generate at least one section of the birth chart before exporting to PDF.');
              return;
            }
            
            generateBirthChartPDF({
              userData,
              sections,
              language
            });
          }}
          className="birth-chart-pdf-button"
        >
          <UIIcons.FileText size={20} className="birth-chart-pdf-icon" />
          <span className="birth-chart-pdf-text">
            {language === 'pt' ? 'Gerar PDF do Mapa Astral' : 'Generate Birth Chart PDF'}
          </span>
          <UIIcons.Download size={18} className="birth-chart-pdf-download-icon" />
        </button>
        <p className="birth-chart-pdf-description">
          {language === 'pt' 
            ? 'Baixe seu mapa astral completo em PDF com todas as seções, referências e informações organizadas.'
            : 'Download your complete birth chart in PDF format with all sections, references and organized information.'}
        </p>
      </div>
    </div>
  );
};

export default FullBirthChartSection;


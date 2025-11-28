import React, { useState, useEffect } from 'react';
import { UIIcons } from './ui-icons';
import { zodiacSigns } from './zodiac-icons';
import { BirthChartWheel } from './birth-chart-wheel';
import { apiService } from '../services/api';
import { useLanguage } from '../i18n';
import { OnboardingData } from './onboarding';

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
              {section?.content.split('\n\n').map((paragraph, idx) => {
                // Remover informações de suporte
                let cleaned = paragraph;
                cleaned = cleaned.replace(/##?\s*📞\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
                cleaned = cleaned.replace(/##?\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
                cleaned = cleaned.replace(/Para dúvidas sobre interpretação astrológica[\s\S]*?Consulta com astrólogo profissional[\s\S]*?(?=\n\n|$)/gi, '');
                cleaned = cleaned.replace(/Livros de astrologia na pasta.*?/gi, '');
                cleaned = cleaned.replace(/Análise com IA.*?/gi, '');
                cleaned = cleaned.replace(/Consulta com astrólogo profissional.*?/gi, '');
                cleaned = cleaned.replace(/Desenvolvido com.*?autoconhecimento profundo[\s\S]*?(?=\n\n|$)/gi, '');
                cleaned = cleaned.replace(/^[-]{3,}$/gm, '');
                
                if (!cleaned.trim()) return null;
                
                return (
                  <p key={idx} className="birth-chart-section-paragraph">
                    {cleaned}
                  </p>
                );
              })}
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
  const { t, language } = useLanguage();
  const [sections, setSections] = useState<Record<string, BirthChartSection | null>>({
    triad: null,
    roots: null,
    karma: null,
    career: null,
    love: null,
    synthesis: null,
  });
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({
    triad: false,
    roots: false,
    karma: false,
    career: false,
    love: false,
    synthesis: false,
  });
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    triad: true,
    roots: false,
    karma: false,
    career: false,
    love: false,
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
        venusSign: userData.venusSign,
        marsSign: userData.marsSign,
        // ===== PLANETAS SOCIAIS (Nível 3) =====
        jupiterSign: userData.jupiterSign,
        saturnSign: userData.saturnSign,
        // ===== PLANETAS TRANSPESSOAIS (Nível 4) =====
        uranusSign: userData.uranusSign,
        neptuneSign: userData.neptuneSign,
        plutoSign: userData.plutoSign,
        // ===== PONTOS KÁRMICOS (Nível 3-4) =====
        northNodeSign: userData.northNodeSign,
        southNodeSign: userData.southNodeSign,
        chironSign: userData.chironSign,
        // ===== ÂNGULOS DO MAPA =====
        midheavenSign: userData.midheavenSign,
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
    const sectionKeys = ['triad', 'roots', 'karma', 'career', 'love', 'synthesis'];
    
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
    if (!expandedSections[sectionKey] && !sections[sectionKey]) {
      generateSection(sectionKey);
    }
  };

  // Gerar primeira seção ao montar (com dependências corretas)
  useEffect(() => {
    // Só gerar se ainda não tiver conteúdo
    if (!sections.triad && !loadingStates.triad) {
      generateSection('triad');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Configuração das seções
  const sectionConfig = [
    {
      key: 'triad',
      icon: UIIcons.Sun,
      accentColor: 'bg-gradient-to-br from-orange-500 to-amber-500',
      titlePt: 'A Tríade da Personalidade',
      titleEn: 'The Personality Triad',
      descPt: 'Sol, Lua e Ascendente - O núcleo do seu ser',
      descEn: 'Sun, Moon and Ascendant - The core of your being',
    },
    {
      key: 'roots',
      icon: UIIcons.Home,
      accentColor: 'bg-gradient-to-br from-emerald-500 to-teal-500',
      titlePt: 'Raízes e Vida Privada',
      titleEn: 'Roots and Private Life',
      descPt: 'Sua história familiar e necessidades emocionais',
      descEn: 'Your family history and emotional needs',
    },
    {
      key: 'karma',
      icon: UIIcons.Compass,
      accentColor: 'bg-gradient-to-br from-purple-500 to-violet-500',
      titlePt: 'Carma, Desafios e Evolução',
      titleEn: 'Karma, Challenges and Evolution',
      descPt: 'Sua missão de alma e propósito de vida',
      descEn: 'Your soul mission and life purpose',
    },
    {
      key: 'career',
      icon: UIIcons.Briefcase,
      accentColor: 'bg-gradient-to-br from-blue-500 to-indigo-500',
      titlePt: 'Carreira, Vocação e Dinheiro',
      titleEn: 'Career, Vocation and Money',
      descPt: 'Seu caminho profissional e realização material',
      descEn: 'Your professional path and material fulfillment',
    },
    {
      key: 'love',
      icon: UIIcons.Heart,
      accentColor: 'bg-gradient-to-br from-pink-500 to-rose-500',
      titlePt: 'O Jeito de Amar e Relacionar',
      titleEn: 'The Way of Loving and Relating',
      descPt: 'Como você ama e o que busca nos relacionamentos',
      descEn: 'How you love and what you seek in relationships',
    },
    {
      key: 'synthesis',
      icon: UIIcons.Sparkles,
      accentColor: 'bg-gradient-to-br from-amber-500 to-orange-500',
      titlePt: 'Síntese Final e Orientações',
      titleEn: 'Final Synthesis and Guidance',
      descPt: 'Integração de todo o mapa e conselhos práticos',
      descEn: 'Integration of the entire chart and practical advice',
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
    </div>
  );
};

export default FullBirthChartSection;


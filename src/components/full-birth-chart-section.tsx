import { useState, useEffect } from 'react';
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
    <div className={`bg-card rounded-2xl border border-border overflow-hidden transition-all duration-300 ${isExpanded ? 'shadow-lg' : 'shadow'}`}>
      <button
        onClick={onToggle}
        className="w-full p-6 flex items-center justify-between hover:bg-muted/50 transition-colors"
      >
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-xl ${accentColor} flex items-center justify-center`}>
            <Icon size={24} className="text-white" />
          </div>
          <div className="text-left">
            <h3 className="font-serif text-xl font-bold text-foreground">
              {section?.title || (language === 'pt' ? 'Carregando...' : 'Loading...')}
            </h3>
            {!isExpanded && section?.content && (
              <p className="text-sm text-muted-foreground line-clamp-1 mt-1">
                {section.content.substring(0, 100)}...
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isLoading && (
            <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          )}
          <UIIcons.ChevronDown 
            size={24} 
            className={`text-muted-foreground transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} 
          />
        </div>
      </button>
      
      {isExpanded && (
        <div className="px-6 pb-6 border-t border-border">
          <div className="pt-6 prose prose-lg dark:prose-invert max-w-none">
            {isLoading ? (
              <div className="space-y-4">
                <div className="h-4 bg-muted rounded animate-pulse" />
                <div className="h-4 bg-muted rounded animate-pulse w-5/6" />
                <div className="h-4 bg-muted rounded animate-pulse w-4/6" />
                <div className="h-4 bg-muted rounded animate-pulse" />
                <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
              </div>
            ) : (
              <div className="text-foreground leading-relaxed whitespace-pre-wrap">
                {section?.content.split('\n\n').map((paragraph, idx) => (
                  <p key={idx} className="mb-4 text-base">
                    {paragraph}
                  </p>
                ))}
              </div>
            )}
          </div>
          
          {section?.generated_by === 'groq' && (
            <div className="mt-4 pt-4 border-t border-border flex items-center gap-2 text-xs text-muted-foreground">
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

  // Gerar primeira seção ao montar
  useEffect(() => {
    generateSection('triad');
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h2 className="font-serif text-3xl lg:text-4xl font-bold text-foreground">
            {language === 'pt' ? 'Meu Mapa Astral Completo' : 'My Complete Birth Chart'}
          </h2>
          <p className="text-muted-foreground mt-2 text-lg">
            {language === 'pt' 
              ? 'Uma análise profunda e personalizada da sua carta natal'
              : 'A deep and personalized analysis of your birth chart'}
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={generateAllSections}
            disabled={isGeneratingAll}
            className="group relative flex items-center gap-3 px-8 py-3.5 rounded-2xl font-semibold text-white shadow-lg shadow-primary/25 transition-all duration-300 hover:shadow-xl hover:shadow-primary/30 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed disabled:hover:scale-100 overflow-hidden"
            style={{
              background: isGeneratingAll 
                ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%)'
                : 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #ec4899 100%)'
            }}
          >
            {/* Efeito de brilho no hover */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-out" />
            
            {isGeneratingAll ? (
              <>
                <div className="relative w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span className="relative text-base">
                  {language === 'pt' ? 'Gerando análise...' : 'Generating analysis...'}
                </span>
              </>
            ) : (
              <>
                <div className="relative flex items-center justify-center w-6 h-6 rounded-full bg-white/20 group-hover:bg-white/30 transition-colors">
                  <UIIcons.Sparkles size={14} className="text-white group-hover:animate-pulse" />
                </div>
                <span className="relative text-base">
                  {language === 'pt' ? 'Gerar Análise Completa' : 'Generate Complete Analysis'}
                </span>
                <UIIcons.ChevronRight size={18} className="relative opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300" />
              </>
            )}
          </button>
          <button
            onClick={onBack}
            className="flex items-center gap-2 px-5 py-3.5 rounded-2xl bg-muted/80 hover:bg-muted text-muted-foreground hover:text-foreground font-medium transition-all duration-200 hover:shadow-md"
          >
            <UIIcons.ArrowLeft size={18} />
            {language === 'pt' ? 'Voltar' : 'Back'}
          </button>
        </div>
      </div>

      {/* Resumo do Mapa */}
      <div className="bg-gradient-to-br from-primary/10 via-accent/10 to-primary/5 rounded-2xl p-4 md:p-6 border border-primary/20">
        <div className="flex flex-col lg:flex-row gap-4 lg:gap-6">
          {/* Wheel Preview */}
          <div className="lg:w-1/3 flex justify-center">
            <div className="w-[200px] h-[200px] md:w-[250px] md:h-[250px] lg:w-[280px] lg:h-[280px]">
              <BirthChartWheel userData={userData} size={280} />
            </div>
          </div>
          
          {/* Info Cards */}
          <div className="lg:w-2/3 flex flex-col gap-3">
            <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <UIIcons.User size={16} />
              <span className="font-medium text-foreground">{userData.name}</span>
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
            <div className="flex flex-row gap-3">
              {/* Sol */}
              <div 
                className="flex-1 rounded-xl p-4 shadow-md"
                style={{
                  background: 'linear-gradient(to bottom right, rgba(245, 158, 11, 0.25), rgba(249, 115, 22, 0.1))',
                  border: '1px solid rgba(245, 158, 11, 0.5)',
                  boxShadow: '0 4px 6px -1px rgba(245, 158, 11, 0.15)'
                }}
              >
                <div className="flex flex-col items-center gap-2">
                  <div 
                    className="w-12 h-12 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: 'rgba(245, 158, 11, 0.35)' }}
                  >
                    <SunIcon size={28} style={{ color: '#d97706' }} />
                  </div>
                  <div className="text-center">
                    <p className="text-xs uppercase tracking-wider font-semibold" style={{ color: '#b45309' }}>
                      {language === 'pt' ? 'Sol' : 'Sun'}
                    </p>
                    <p className="font-bold text-lg" style={{ color: '#78350f' }}>{sunSign}</p>
                  </div>
                </div>
                <p className="text-xs text-center mt-2" style={{ color: 'rgba(146, 64, 14, 0.8)' }}>
                  {language === 'pt' ? 'Sua essência e identidade' : 'Your essence and identity'}
                </p>
              </div>
              
              {/* Lua */}
              <div 
                className="flex-1 rounded-xl p-4 shadow-md"
                style={{
                  background: 'linear-gradient(to bottom right, rgba(59, 130, 246, 0.25), rgba(99, 102, 241, 0.1))',
                  border: '1px solid rgba(59, 130, 246, 0.5)',
                  boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.15)'
                }}
              >
                <div className="flex flex-col items-center gap-2">
                  <div 
                    className="w-12 h-12 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: 'rgba(59, 130, 246, 0.35)' }}
                  >
                    <MoonIcon size={28} style={{ color: '#2563eb' }} />
                  </div>
                  <div className="text-center">
                    <p className="text-xs uppercase tracking-wider font-semibold" style={{ color: '#1d4ed8' }}>
                      {language === 'pt' ? 'Lua' : 'Moon'}
                    </p>
                    <p className="font-bold text-lg" style={{ color: '#1e3a8a' }}>{moonSign}</p>
                  </div>
                </div>
                <p className="text-xs text-center mt-2" style={{ color: 'rgba(30, 58, 138, 0.8)' }}>
                  {language === 'pt' ? 'Suas emoções e necessidades' : 'Your emotions and needs'}
                </p>
              </div>
              
              {/* Ascendente */}
              <div 
                className="flex-1 rounded-xl p-4 shadow-md"
                style={{
                  background: 'linear-gradient(to bottom right, rgba(168, 85, 247, 0.25), rgba(139, 92, 246, 0.1))',
                  border: '1px solid rgba(168, 85, 247, 0.5)',
                  boxShadow: '0 4px 6px -1px rgba(168, 85, 247, 0.15)'
                }}
              >
                <div className="flex flex-col items-center gap-2">
                  <div 
                    className="w-12 h-12 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: 'rgba(168, 85, 247, 0.35)' }}
                  >
                    <AscIcon size={28} style={{ color: '#9333ea' }} />
                  </div>
                  <div className="text-center">
                    <p className="text-xs uppercase tracking-wider font-semibold" style={{ color: '#7c3aed' }}>
                      {language === 'pt' ? 'Asc' : 'Asc'}
                    </p>
                    <p className="font-bold text-lg" style={{ color: '#581c87' }}>{ascendant}</p>
                  </div>
                </div>
                <p className="text-xs text-center mt-2" style={{ color: 'rgba(88, 28, 135, 0.8)' }}>
                  {language === 'pt' ? 'Sua máscara social' : 'Your social mask'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Seções do Mapa */}
      <div className="space-y-4">
        <h3 className="font-serif text-2xl font-bold text-foreground flex items-center gap-3">
          <UIIcons.BookOpen size={24} className="text-primary" />
          {language === 'pt' ? 'Análise Completa' : 'Complete Analysis'}
        </h3>
        
        <p className="text-muted-foreground">
          {language === 'pt' 
            ? 'Clique em cada seção para expandir e ler a análise detalhada. Cada seção é gerada individualmente com base nos seus dados de nascimento.'
            : 'Click on each section to expand and read the detailed analysis. Each section is generated individually based on your birth data.'}
        </p>
        
        <div className="space-y-3">
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
      <div className="bg-muted/50 rounded-2xl p-6 border border-border">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
            <UIIcons.Info size={20} className="text-primary" />
          </div>
          <div>
            <h4 className="font-semibold text-foreground mb-2">
              {language === 'pt' ? 'Sobre esta análise' : 'About this analysis'}
            </h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
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


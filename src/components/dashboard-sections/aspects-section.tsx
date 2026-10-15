import React, { useState } from 'react';
import { UIIcons } from '../ui-icons';
import { planets } from '../planet-icons';
import { apiService } from '../../services/api';
import { useLanguage } from '../../i18n';
import { OnboardingData } from '../onboarding';

// ===== ASPECTOS =====
interface AspectsSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

// Ícones de símbolo para cada aspecto
const AspectSymbols = {
  Conjunção: '☌',
  Conjunction: '☌',
  Trígono: '△',
  Trine: '△',
  Sextil: '✱',
  Sextile: '✱',
  Quadratura: '□',
  Square: '□',
  Oposição: '☍',
  Opposition: '☍',
};

// Dados detalhados dos tipos de aspectos
const aspectTypeInfo = {
  pt: {
    Conjunção: {
      symbol: '☌',
      nature: 'União / Fusão',
      description: 'Os planetas atuam juntos, fundindo suas energias. Pode ser harmonioso ou tenso dependendo dos planetas envolvidos.',
      keywords: ['Intensificação', 'Foco', 'Potencial'],
      color: 'blue',
    },
    Trígono: {
      symbol: '△',
      nature: 'Harmonioso / Fluido',
      description: 'Fluxo natural de energia entre os planetas. Talentos inatos e facilidades.',
      keywords: ['Talento Natural', 'Fluidez', 'Oportunidade'],
      color: 'green',
    },
    Sextil: {
      symbol: '✱',
      nature: 'Oportunidade / Cooperação',
      description: 'Aspectos que trazem oportunidades quando há esforço consciente para aproveitá-las.',
      keywords: ['Potencial', 'Cooperação', 'Desenvolvimento'],
      color: 'cyan',
    },
    Quadratura: {
      symbol: '□',
      nature: 'Desafio / Tensão',
      description: 'Tensão que exige ação. Conflitos internos que podem gerar grande crescimento quando trabalhados.',
      keywords: ['Desafio', 'Crescimento', 'Ação Necessária'],
      color: 'red',
    },
    Oposição: {
      symbol: '☍',
      nature: 'Polaridade / Equilíbrio',
      description: 'Forças opostas que pedem integração. Frequentemente se manifesta em relacionamentos externos.',
      keywords: ['Equilíbrio', 'Consciência', 'Integração'],
      color: 'orange',
    },
  },
  en: {
    Conjunction: {
      symbol: '☌',
      nature: 'Union / Fusion',
      description: 'The planets work together, merging their energies. Can be harmonious or tense depending on the planets involved.',
      keywords: ['Intensification', 'Focus', 'Potential'],
      color: 'blue',
    },
    Trine: {
      symbol: '△',
      nature: 'Harmonious / Fluid',
      description: 'Natural energy flow between planets. Innate talents and ease.',
      keywords: ['Natural Talent', 'Flow', 'Opportunity'],
      color: 'green',
    },
    Sextile: {
      symbol: '✱',
      nature: 'Opportunity / Cooperation',
      description: 'Aspects that bring opportunities when there is conscious effort to take advantage of them.',
      keywords: ['Potential', 'Cooperation', 'Development'],
      color: 'cyan',
    },
    Square: {
      symbol: '□',
      nature: 'Challenge / Tension',
      description: 'Tension that demands action. Internal conflicts that can generate great growth when worked on.',
      keywords: ['Challenge', 'Growth', 'Action Required'],
      color: 'red',
    },
    Opposition: {
      symbol: '☍',
      nature: 'Polarity / Balance',
      description: 'Opposing forces that ask for integration. Often manifests in external relationships.',
      keywords: ['Balance', 'Awareness', 'Integration'],
      color: 'orange',
    },
  },
};

// Componente para formatar a interpretação dos aspectos
const FormattedAspectInterpretation = ({ 
  text, 
  language, 
  planet1, 
  planet2, 
  aspectType 
}: { 
  text: string; 
  language: string; 
  planet1: string;
  planet2: string;
  aspectType: string;
}) => {
  const aspectInfo = language === 'pt' 
    ? aspectTypeInfo.pt[aspectType as keyof typeof aspectTypeInfo.pt]
    : aspectTypeInfo.en[aspectType as keyof typeof aspectTypeInfo.en];

  // Cores agora são aplicadas via CSS classes, não mais via Tailwind

  // Dividir o texto em seções se houver parágrafos
  const paragraphs = text.split(/\n\n+/).filter(p => p.trim());
  
  // Identificar seções do texto
  const identifySection = (paragraph: string): { type: string; content: string } => {
    const lowerP = paragraph.toLowerCase();
    if (lowerP.includes('energia') || lowerP.includes('energy') || lowerP.includes('dinâmica') || lowerP.includes('dynamic')) {
      return { type: 'energy', content: paragraph };
    }
    if (lowerP.includes('desafio') || lowerP.includes('challenge') || lowerP.includes('tensão') || lowerP.includes('tension')) {
      return { type: 'challenge', content: paragraph };
    }
    if (lowerP.includes('potencial') || lowerP.includes('potential') || lowerP.includes('oportunidade') || lowerP.includes('opportunity')) {
      return { type: 'potential', content: paragraph };
    }
    if (lowerP.includes('conselho') || lowerP.includes('advice') || lowerP.includes('orientação') || lowerP.includes('guidance')) {
      return { type: 'advice', content: paragraph };
    }
    return { type: 'general', content: paragraph };
  };

  const sectionIcons: Record<string, { icon: React.ReactNode; title: { pt: string; en: string }; color: string }> = {
    energy: {
      icon: <UIIcons.Zap size={20} />,
      title: { pt: '⚡ Energia da Conexão', en: '⚡ Connection Energy' },
      color: 'amber-500',
    },
    challenge: {
      icon: <UIIcons.AlertCircle size={20} />,
      title: { pt: '🔥 Desafios e Tensões', en: '🔥 Challenges and Tensions' },
      color: 'red-500',
    },
    potential: {
      icon: <UIIcons.Star size={20} />,
      title: { pt: '✨ Potenciais e Dons', en: '✨ Potentials and Gifts' },
      color: 'emerald-500',
    },
    advice: {
      icon: <UIIcons.Compass size={20} />,
      title: { pt: '🧭 Orientações Práticas', en: '🧭 Practical Guidance' },
      color: 'blue-500',
    },
    general: {
      icon: <UIIcons.BookOpen size={20} />,
      title: { pt: '📖 Interpretação', en: '📖 Interpretation' },
      color: 'purple-500',
    },
  };

  return (
    <div className="aspect-interpretation-container">
      {/* Header do Aspecto */}
      <div className={`aspect-interpretation-header aspect-interpretation-header-${aspectInfo?.color || 'blue'}`}>
        <div className="aspect-interpretation-header-content">
          <div className={`aspect-interpretation-icon-container aspect-interpretation-icon-container-${aspectInfo?.color || 'blue'}`}>
            <span className={`aspect-interpretation-icon aspect-interpretation-icon-${aspectInfo?.color || 'blue'}`}>
              {aspectInfo?.symbol || '☌'}
            </span>
          </div>
          <div>
            <h3 className="aspect-interpretation-title">
              {planet1} {aspectInfo?.symbol} {planet2}
            </h3>
            <p className={`aspect-interpretation-meta aspect-interpretation-meta-${aspectInfo?.color || 'blue'}`}>
              {aspectType} • {aspectInfo?.nature}
            </p>
          </div>
        </div>
        
        {/* Palavras-chave */}
        {aspectInfo?.keywords && (
          <div className="aspect-interpretation-keywords">
            {aspectInfo.keywords.map((keyword, idx) => (
              <span 
                key={idx}
                className={`aspect-interpretation-keyword aspect-interpretation-keyword-${aspectInfo.color}`}
              >
                {keyword}
              </span>
            ))}
          </div>
        )}
        
        <p className="aspect-interpretation-description">
          {aspectInfo?.description}
        </p>
      </div>

      {/* Seções da Interpretação */}
      {paragraphs.length > 0 && (
        <div className="aspect-interpretation-sections">
          <h4 className="aspect-interpretation-sections-title">
            <UIIcons.BookOpen size={20} className="aspect-interpretation-sections-icon" />
            {language === 'pt' ? 'Análise Detalhada' : 'Detailed Analysis'}
          </h4>
          
          {paragraphs.map((paragraph, index) => {
            const section = identifySection(paragraph);
            const sectionInfo = sectionIcons[section.type];
            
            return (
              <div 
                key={index}
                className="aspect-interpretation-section-card"
              >
                <div className="aspect-interpretation-section-content">
                  <div className={`aspect-interpretation-section-icon aspect-interpretation-section-icon-${sectionInfo.color.replace('text-', '')}`}>
                    {sectionInfo.icon}
                  </div>
                  <div className="aspect-interpretation-section-text">
                    {paragraphs.length > 1 && (
                      <p className={`aspect-interpretation-section-label aspect-interpretation-section-label-${sectionInfo.color.replace('text-', '')}`}>
                        {language === 'pt' ? sectionInfo.title.pt : sectionInfo.title.en}
                      </p>
                    )}
                    <p className="aspect-interpretation-section-paragraph">
                      {section.content}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export const AspectsSection = ({ userData, onBack }: AspectsSectionProps) => {
  const { language } = useLanguage();
  const [selectedAspect, setSelectedAspect] = useState<string | null>(null);
  const [selectedAspectData, setSelectedAspectData] = useState<{
    planet1: string;
    planet2: string;
    type: string;
    typeEn: string;
  } | null>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // Aspectos exemplo (seriam calculados a partir dos dados reais)
  const aspects = [
    { planet1: 'Sol', planet2: 'Lua', type: 'Trígono', typeEn: 'Trine', color: 'text-green-500', bgColor: 'bg-green-500/10', symbol: '△' },
    { planet1: 'Vênus', planet2: 'Marte', type: 'Conjunção', typeEn: 'Conjunction', color: 'text-blue-500', bgColor: 'bg-blue-500/10', symbol: '☌' },
    { planet1: 'Mercúrio', planet2: 'Júpiter', type: 'Sextil', typeEn: 'Sextile', color: 'text-cyan-500', bgColor: 'bg-cyan-500/10', symbol: '✱' },
    { planet1: 'Saturno', planet2: 'Plutão', type: 'Quadratura', typeEn: 'Square', color: 'text-red-500', bgColor: 'bg-red-500/10', symbol: '□' },
    { planet1: 'Sol', planet2: 'Saturno', type: 'Oposição', typeEn: 'Opposition', color: 'text-orange-500', bgColor: 'bg-orange-500/10', symbol: '☍' },
  ];

  // Legenda detalhada dos aspectos com significado completo e ícones SVG
  const aspectLegend = language === 'pt' ? [
    { type: 'Conjunção', symbol: '☌', icon: UIIcons.ConjunctionIcon, bgColor: '#3b82f6', textColor: 'text-blue-500', desc: 'Fusão de energias', meaning: '0° - Planetas unidos, intensificam um ao outro' },
    { type: 'Trígono', symbol: '△', icon: UIIcons.TrineIcon, bgColor: '#22c55e', textColor: 'text-green-500', desc: 'Fluxo harmonioso', meaning: '120° - Talentos naturais e facilidades' },
    { type: 'Sextil', symbol: '⚹', icon: UIIcons.SextileIcon, bgColor: '#06b6d4', textColor: 'text-cyan-500', desc: 'Oportunidades', meaning: '60° - Potencial que requer ação consciente' },
    { type: 'Quadratura', symbol: '□', icon: UIIcons.SquareAspectIcon, bgColor: '#ef4444', textColor: 'text-red-500', desc: 'Desafios', meaning: '90° - Tensão que gera crescimento' },
    { type: 'Oposição', symbol: '☍', icon: UIIcons.OppositionIcon, bgColor: '#f97316', textColor: 'text-orange-500', desc: 'Polaridades', meaning: '180° - Equilíbrio entre forças opostas' },
  ] : [
    { type: 'Conjunction', symbol: '☌', icon: UIIcons.ConjunctionIcon, bgColor: '#3b82f6', textColor: 'text-blue-500', desc: 'Energy fusion', meaning: '0° - Planets united, intensify each other' },
    { type: 'Trine', symbol: '△', icon: UIIcons.TrineIcon, bgColor: '#22c55e', textColor: 'text-green-500', desc: 'Harmonious flow', meaning: '120° - Natural talents and ease' },
    { type: 'Sextile', symbol: '⚹', icon: UIIcons.SextileIcon, bgColor: '#06b6d4', textColor: 'text-cyan-500', desc: 'Opportunities', meaning: '60° - Potential requiring conscious action' },
    { type: 'Square', symbol: '□', icon: UIIcons.SquareAspectIcon, bgColor: '#ef4444', textColor: 'text-red-500', desc: 'Challenges', meaning: '90° - Tension that generates growth' },
    { type: 'Opposition', symbol: '☍', icon: UIIcons.OppositionIcon, bgColor: '#f97316', textColor: 'text-orange-500', desc: 'Polarities', meaning: '180° - Balance between opposing forces' },
  ];

  const fetchAspectInterpretation = async (planet1: string, planet2: string, aspect: string, aspectEn: string) => {
    try {
      setIsLoading(true);
      setSelectedAspect(`${planet1}-${planet2}`);
      setSelectedAspectData({ planet1, planet2, type: aspect, typeEn: aspectEn });
      const result = await apiService.getAspectInterpretation({
        planet1,
        planet2,
        aspect,
      });
      setInterpretation(result.interpretation);
    } catch (error) {
      console.error('Erro ao buscar interpretação:', error);
      setInterpretation(
        language === 'pt'
          ? `O aspecto de ${aspect} entre ${planet1} e ${planet2} cria uma dinâmica única no seu mapa. Este aspecto influencia como essas energias planetárias interagem na sua vida, revelando padrões de comportamento e áreas de desenvolvimento pessoal.`
          : `The ${aspectEn} aspect between ${planet1} and ${planet2} creates a unique dynamic in your chart. This aspect influences how these planetary energies interact in your life, revealing behavior patterns and areas of personal development.`
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard-section-container">
      {/* Header */}
      <div className="section-header">
        <div className="section-header-content">
          <h2 className="section-title">
            {language === 'pt' ? 'Aspectos Planetários' : 'Planetary Aspects'}
          </h2>
          <p className="section-subtitle">
            {language === 'pt' ? 'As conexões entre os planetas do seu mapa' : 'The connections between planets in your chart'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="section-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Legenda Detalhada dos Aspectos */}
      <div className="aspects-legend-container">
        <h3 className="aspects-legend-title">
          <UIIcons.Info size={18} className="text-primary" />
          {language === 'pt' ? 'Tipos de Aspectos' : 'Aspect Types'}
        </h3>
        <div className="aspects-legend-grid">
          {aspectLegend.map((item) => {
            const IconComponent = item.icon;
            return (
              <div 
                key={item.type} 
                className="aspects-legend-item"
                style={{ 
                  borderColor: item.bgColor,
                  backgroundColor: `${item.bgColor}10` 
                }}
              >
                {/* Ícone SVG Grande */}
                <div className="aspects-legend-icon-container">
                  <div 
                    className="aspects-legend-icon-circle"
                    style={{ backgroundColor: item.bgColor }}
                  >
                    <IconComponent size={28} color="currentColor" />
                  </div>
                  <div className="aspects-legend-text">
                    <p className="aspects-legend-type">{item.type}</p>
                    <p className={`aspects-legend-desc ${item.textColor}`}>{item.desc}</p>
                  </div>
                </div>
                {/* Significado */}
                <p className="aspects-legend-meaning">
                  {item.meaning}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Lista de Aspectos */}
      <div className="aspects-list-container">
        <h3 className="aspects-list-title">
          <UIIcons.Sparkles size={18} className="text-primary" />
          {language === 'pt' ? 'Seus Aspectos' : 'Your Aspects'}
        </h3>
        <div className="aspects-list-grid">
          {aspects.map((aspect, index) => {
            const Planet1Icon = planets.find(p => p.name === aspect.planet1)?.icon;
            const Planet2Icon = planets.find(p => p.name === aspect.planet2)?.icon;
            const isSelected = selectedAspect === `${aspect.planet1}-${aspect.planet2}`;

            return (
              <button
                key={index}
                onClick={() => fetchAspectInterpretation(aspect.planet1, aspect.planet2, aspect.type, aspect.typeEn)}
                className={`aspect-card ${isSelected ? 'selected' : ''}`}
              >
                <div className="aspect-card-header">
                  <div className="aspect-card-planets">
                    {Planet1Icon && <Planet1Icon size={28} className={aspect.color} />}
                    <span className={`aspect-card-symbol ${aspect.color}`}>{aspect.symbol}</span>
                    {Planet2Icon && <Planet2Icon size={28} className={aspect.color} />}
                  </div>
                  <UIIcons.ChevronRight size={20} className={`aspect-card-chevron ${isSelected ? 'text-primary' : ''}`} />
                </div>
                <div className="aspect-card-body">
                  <p className="aspect-card-planet-names">
                    {aspect.planet1} {language === 'pt' ? 'e' : 'and'} {aspect.planet2}
                  </p>
                  <p className={`aspect-card-type ${aspect.color}`}>
                    {language === 'pt' ? aspect.type : aspect.typeEn}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Painel de Interpretação */}
      {selectedAspect && selectedAspectData && (
        <div className="aspect-interpretation-panel">
          {isLoading ? (
            <div className="aspect-loading-container">
              <UIIcons.Loader className="aspect-loading-spinner" />
              <p className="aspect-loading-text">
                {language === 'pt' ? 'Analisando o aspecto...' : 'Analyzing the aspect...'}
              </p>
            </div>
          ) : (
            <FormattedAspectInterpretation 
              text={interpretation} 
              language={language}
              planet1={selectedAspectData.planet1}
              planet2={selectedAspectData.planet2}
              aspectType={language === 'pt' ? selectedAspectData.type : selectedAspectData.typeEn}
            />
          )}
        </div>
      )}
    </div>
  );
};

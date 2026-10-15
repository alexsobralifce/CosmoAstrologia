import React from 'react';
import { useState } from 'react';
import { UIIcons } from '../ui-icons';
import { zodiacSigns } from '../zodiac-icons';
import { planets } from '../planet-icons';
import { apiService } from '../../services/api';
import { useLanguage } from '../../i18n';
import { OnboardingData } from '../onboarding';

// ===== PLANETAS =====
interface PlanetsSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

// Informações sobre cada planeta
const planetInfo = {
  pt: {
    Sol: { symbol: '☉', domain: 'Identidade, Ego, Propósito', element: 'Fogo', keywords: ['Essência', 'Vitalidade', 'Autoexpressão'] },
    Lua: { symbol: '☽', domain: 'Emoções, Inconsciente, Passado', element: 'Água', keywords: ['Intuição', 'Memória', 'Nutrição'] },
    Mercúrio: { symbol: '☿', domain: 'Comunicação, Mente, Aprendizado', element: 'Ar/Terra', keywords: ['Pensamento', 'Fala', 'Escrita'] },
    Vênus: { symbol: '♀', domain: 'Amor, Beleza, Valores', element: 'Terra/Ar', keywords: ['Afeto', 'Prazer', 'Harmonia'] },
    Marte: { symbol: '♂', domain: 'Ação, Energia, Coragem', element: 'Fogo', keywords: ['Impulso', 'Desejo', 'Conquista'] },
    Júpiter: { symbol: '♃', domain: 'Expansão, Sorte, Sabedoria', element: 'Fogo', keywords: ['Crescimento', 'Fé', 'Abundância'] },
    Saturno: { symbol: '♄', domain: 'Estrutura, Limites, Tempo', element: 'Terra', keywords: ['Disciplina', 'Maturidade', 'Karma'] },
    Urano: { symbol: '♅', domain: 'Inovação, Liberdade, Revolução', element: 'Ar', keywords: ['Originalidade', 'Mudança', 'Despertar'] },
    Netuno: { symbol: '♆', domain: 'Espiritualidade, Sonhos, Ilusão', element: 'Água', keywords: ['Imaginação', 'Compaixão', 'Transcendência'] },
    Plutão: { symbol: '♇', domain: 'Transformação, Poder, Renascimento', element: 'Água', keywords: ['Intensidade', 'Regeneração', 'Profundidade'] },
  },
  en: {
    Sun: { symbol: '☉', domain: 'Identity, Ego, Purpose', element: 'Fire', keywords: ['Essence', 'Vitality', 'Self-expression'] },
    Moon: { symbol: '☽', domain: 'Emotions, Unconscious, Past', element: 'Water', keywords: ['Intuition', 'Memory', 'Nurturing'] },
    Mercury: { symbol: '☿', domain: 'Communication, Mind, Learning', element: 'Air/Earth', keywords: ['Thought', 'Speech', 'Writing'] },
    Venus: { symbol: '♀', domain: 'Love, Beauty, Values', element: 'Earth/Air', keywords: ['Affection', 'Pleasure', 'Harmony'] },
    Mars: { symbol: '♂', domain: 'Action, Energy, Courage', element: 'Fire', keywords: ['Drive', 'Desire', 'Conquest'] },
    Jupiter: { symbol: '♃', domain: 'Expansion, Luck, Wisdom', element: 'Fire', keywords: ['Growth', 'Faith', 'Abundance'] },
    Saturn: { symbol: '♄', domain: 'Structure, Limits, Time', element: 'Earth', keywords: ['Discipline', 'Maturity', 'Karma'] },
    Uranus: { symbol: '♅', domain: 'Innovation, Freedom, Revolution', element: 'Air', keywords: ['Originality', 'Change', 'Awakening'] },
    Neptune: { symbol: '♆', domain: 'Spirituality, Dreams, Illusion', element: 'Water', keywords: ['Imagination', 'Compassion', 'Transcendence'] },
    Pluto: { symbol: '♇', domain: 'Transformation, Power, Rebirth', element: 'Water', keywords: ['Intensity', 'Regeneration', 'Depth'] },
  },
};

// Componente para formatar a interpretação dos planetas
const FormattedPlanetInterpretation = ({ 
  text, 
  language, 
  planetName,
  sign,
  house 
}: { 
  text: string; 
  language: string; 
  planetName: string;
  sign: string;
  house: number;
}) => {
  const planetData = language === 'pt' 
    ? planetInfo.pt[planetName as keyof typeof planetInfo.pt]
    : planetInfo.en[planetName as keyof typeof planetInfo.en];

  // Cores por tipo de planeta
  // Cores agora são aplicadas via CSS classes, não mais via Tailwind

  // Dividir o texto em parágrafos
  const paragraphs = text.split(/\n\n+/).filter(p => p.trim());

  // Agrupar por seção principal (PASSADO/KARMA, PRESENTE/ESSÊNCIA, etc.)
  interface Section {
    mainTitle: string;
    mainTitleRaw: string;
    subsections: Array<{
      subTitle: string;
      content: string;
      color: string;
    }>;
  }

  const sections: Section[] = [];
  let currentSection: Section | null = null;

  paragraphs.forEach((paragraph) => {
    const trimmed = paragraph.trim();
    
    // Verificar se é um título principal (PASSADO/KARMA, PRESENTE/ESSÊNCIA, etc.)
    const mainTitleMatch = trimmed.match(/^\*\*(PASSADO|PRESENTE|FUTURO|PAST|PRESENT|FUTURE)[\s\/]*(KARMA|ESSÊNCIA|EVOLUÇÃO|KARMA|ESSENCE|EVOLUTION)?\*\*\s*$/i);
    
    if (mainTitleMatch) {
      // Salvar seção anterior se existir
      if (currentSection && currentSection.subsections.length > 0) {
        sections.push(currentSection);
      }
      
      // Criar nova seção principal
      currentSection = {
        mainTitle: trimmed.replace(/^\*\*|\*\*$/g, ''),
        mainTitleRaw: trimmed,
        subsections: []
      };
    } else if (currentSection) {
      // Identificar tipo de subseção
      const lowerP = paragraph.toLowerCase();
      let subTitle = language === 'pt' ? 'Análise' : 'Analysis';
      let color = 'text-purple-500';
      
      if (lowerP.includes('personalidade') || lowerP.includes('personality') || lowerP.includes('essência') || lowerP.includes('essence')) {
        subTitle = language === 'pt' ? 'Personalidade' : 'Personality';
        color = 'text-blue-500';
      } else if (lowerP.includes('desafio') || lowerP.includes('challenge') || lowerP.includes('dificuldade') || lowerP.includes('difficulty')) {
        subTitle = language === 'pt' ? 'Desafios' : 'Challenges';
        color = 'text-red-500';
      } else if (lowerP.includes('potencial') || lowerP.includes('potential') || lowerP.includes('talento') || lowerP.includes('talent') || lowerP.includes('dom') || lowerP.includes('gift')) {
        subTitle = language === 'pt' ? 'Potenciais e Dons' : 'Potentials and Gifts';
        color = 'text-emerald-500';
      } else if (lowerP.includes('conselho') || lowerP.includes('advice') || lowerP.includes('orientação') || lowerP.includes('guidance') || lowerP.includes('recomend')) {
        subTitle = language === 'pt' ? 'Orientações' : 'Guidance';
        color = 'text-amber-500';
      } else if (lowerP.includes('relacionamento') || lowerP.includes('relationship') || lowerP.includes('amor') || lowerP.includes('love')) {
        subTitle = language === 'pt' ? 'Relacionamentos' : 'Relationships';
        color = 'text-pink-500';
      } else if (lowerP.includes('carreira') || lowerP.includes('career') || lowerP.includes('profissão') || lowerP.includes('profession') || lowerP.includes('trabalho') || lowerP.includes('work')) {
        subTitle = language === 'pt' ? 'Carreira' : 'Career';
        color = 'text-indigo-500';
      }
      
      currentSection.subsections.push({
        subTitle,
        content: paragraph,
        color
      });
    }
  });

  // Adicionar última seção (o TS não enxerga as atribuições feitas dentro do forEach)
  const lastSection = currentSection as Section | null;
  if (lastSection && lastSection.subsections.length > 0) {
    sections.push(lastSection);
  }

  return (
    <div className="planet-interpretation-container">
      {/* Header do Planeta */}
      <div className={`planet-interpretation-header planet-interpretation-header-${planetName.toLowerCase()}`}>
        <div className="planet-interpretation-header-content">
          <div className="planet-interpretation-icon-container">
            <span className={`planet-interpretation-icon planet-interpretation-icon-${planetName.toLowerCase()}`}>
              {planetData?.symbol || '★'}
            </span>
          </div>
          <div>
            <h3 className="planet-interpretation-title">
              {planetName} {language === 'pt' ? 'em' : 'in'} {sign}
            </h3>
            <p className={`planet-interpretation-meta planet-interpretation-meta-${planetName.toLowerCase()}`}>
              Casa {house} • {planetData?.domain}
            </p>
          </div>
        </div>
        
        {/* Palavras-chave */}
        {planetData?.keywords && (
          <div className="planet-interpretation-keywords">
            {planetData.keywords.map((keyword, idx) => (
              <span 
                key={idx}
                className={`planet-interpretation-keyword planet-interpretation-keyword-${planetName.toLowerCase()}`}
              >
                {keyword}
              </span>
            ))}
          </div>
        )}
        
        {/* Elemento */}
        <div className="planet-interpretation-element">
          <span className="planet-interpretation-element-label">{language === 'pt' ? 'Elemento:' : 'Element:'}</span>
          <span className={`planet-interpretation-element-value planet-interpretation-element-value-${planetName.toLowerCase()}`}>{planetData?.element}</span>
        </div>
      </div>

      {/* Seções da Interpretação */}
      {sections.length > 0 ? (
        <div className="planet-interpretation-sections">
          <h4 className="planet-interpretation-sections-title">
            {language === 'pt' ? 'Interpretação Completa' : 'Complete Interpretation'}
          </h4>
          
          {/* Card único com todos os tópicos */}
          <div className="planet-interpretation-sections-card">
            {sections.map((section, sectionIndex) => (
              <div key={sectionIndex} className="planet-interpretation-section">
                {/* Título Principal */}
                <h5 className="planet-interpretation-section-main-title">
                  {section.mainTitle}
                </h5>
                
                {/* Subseções */}
                <div className="planet-interpretation-subsections">
                  {section.subsections.map((subsection, subIndex) => (
                    <div key={subIndex} className="planet-interpretation-subsection">
                      {/* Subtítulo */}
                      <p className={`planet-interpretation-subsection-title planet-interpretation-subsection-title-${subsection.color.replace('text-', '')}`}>
                        {subsection.subTitle}
                      </p>
                      
                      {/* Conteúdo */}
                      <p className="planet-interpretation-subsection-content">
                        {subsection.content}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : text && text.trim() ? (
        // Fallback: se não houver seções estruturadas, exibir o texto diretamente
        <div className="planet-interpretation-sections">
          <h4 className="planet-interpretation-sections-title">
            {language === 'pt' ? 'Interpretação' : 'Interpretation'}
          </h4>
          <div className="planet-interpretation-sections-card">
            <div className="planet-interpretation-section">
              {paragraphs.map((paragraph, index) => (
                <p key={index} className="planet-interpretation-subsection-content" style={{ marginBottom: '1rem' }}>
                  {paragraph.trim()}
                </p>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export const PlanetsSection = ({ userData, onBack }: PlanetsSectionProps) => {
  const { language } = useLanguage();
  const [selectedPlanet, setSelectedPlanet] = useState<string | null>(null);
  const [selectedPlanetData, setSelectedPlanetData] = useState<{ sign: string; house: number } | null>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // Lista de planetas com signos reais do userData
  const planetData = [
    { name: 'Sol', nameEn: 'Sun', sign: userData.sunSign || 'Áries', house: userData.sunHouse || 1, color: 'text-orange-500', bgColor: 'bg-orange-500/10' },
    { name: 'Lua', nameEn: 'Moon', sign: userData.moonSign || 'Touro', house: userData.moonHouse || 4, color: 'text-purple-500', bgColor: 'bg-purple-500/10' },
    { name: 'Mercúrio', nameEn: 'Mercury', sign: userData.mercurySign || 'Gêmeos', house: userData.mercuryHouse || 3, color: 'text-cyan-500', bgColor: 'bg-cyan-500/10' },
    { name: 'Vênus', nameEn: 'Venus', sign: userData.venusSign || 'Touro', house: userData.venusHouse || 2, color: 'text-pink-500', bgColor: 'bg-pink-500/10' },
    { name: 'Marte', nameEn: 'Mars', sign: userData.marsSign || 'Áries', house: userData.marsHouse || 1, color: 'text-red-500', bgColor: 'bg-red-500/10' },
    { name: 'Júpiter', nameEn: 'Jupiter', sign: userData.jupiterSign || 'Sagitário', house: userData.jupiterHouse || 9, color: 'text-amber-500', bgColor: 'bg-amber-500/10' },
    { name: 'Saturno', nameEn: 'Saturn', sign: userData.saturnSign || 'Capricórnio', house: userData.saturnHouse || 10, color: 'text-muted-foreground', bgColor: 'bg-gray-500/10' },
    { name: 'Urano', nameEn: 'Uranus', sign: userData.uranusSign || 'Aquário', house: userData.uranusHouse || 11, color: 'text-teal-500', bgColor: 'bg-teal-500/10' },
    { name: 'Netuno', nameEn: 'Neptune', sign: userData.neptuneSign || 'Peixes', house: userData.neptuneHouse || 12, color: 'text-blue-500', bgColor: 'bg-blue-500/10' },
    { name: 'Plutão', nameEn: 'Pluto', sign: userData.plutoSign || 'Escorpião', house: userData.plutoHouse || 8, color: 'text-rose-500', bgColor: 'bg-rose-500/10' },
  ];

  // Categorias de planetas
  const planetCategories = {
    pt: [
      { name: 'Luminares', planets: ['Sol', 'Lua'], desc: 'A essência e as emoções' },
      { name: 'Pessoais', planets: ['Mercúrio', 'Vênus', 'Marte'], desc: 'Comunicação, amor e ação' },
      { name: 'Sociais', planets: ['Júpiter', 'Saturno'], desc: 'Expansão e estrutura' },
      { name: 'Transpessoais', planets: ['Urano', 'Netuno', 'Plutão'], desc: 'Transformação coletiva' },
    ],
    en: [
      { name: 'Luminaries', planets: ['Sun', 'Moon'], desc: 'Essence and emotions' },
      { name: 'Personal', planets: ['Mercury', 'Venus', 'Mars'], desc: 'Communication, love and action' },
      { name: 'Social', planets: ['Jupiter', 'Saturn'], desc: 'Expansion and structure' },
      { name: 'Transpersonal', planets: ['Uranus', 'Neptune', 'Pluto'], desc: 'Collective transformation' },
    ],
  };

  const fetchPlanetInterpretation = async (planetName: string, sign: string, house: number) => {
    try {
      setIsLoading(true);
      setSelectedPlanet(planetName);
      setSelectedPlanetData({ sign, house });
      
      // Validar dados antes de fazer a chamada
      if (!planetName) {
        throw new Error('Nome do planeta é obrigatório');
      }
      
      if (!sign) {
        throw new Error('Signo do planeta é obrigatório');
      }
      
      console.log('Buscando interpretação para:', { planet: planetName, sign, house });
      
      const result = await apiService.getPlanetInterpretation({
        planet: planetName,
        sign: sign,
        house: house && house > 0 ? house : undefined,
        sunSign: userData.sunSign,
        moonSign: userData.moonSign,
        ascendant: userData.ascendant,
        userName: userData.name,
      });
      
      console.log('Resultado recebido:', result);
      
      if (result && result.interpretation && result.interpretation.trim()) {
        setInterpretation(result.interpretation);
      } else {
        throw new Error('Interpretação não retornada ou está vazia');
      }
    } catch (error) {
      console.error('Erro ao buscar interpretação:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setInterpretation(
        language === 'pt'
          ? `Erro ao buscar interpretação para ${planetName} em ${sign}${house ? ` na Casa ${house}` : ''}. ${errorMessage}`
          : `Error fetching interpretation for ${planetName} in ${sign}${house ? ` in House ${house}` : ''}. ${errorMessage}`
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif text-3xl font-bold text-foreground">
            {language === 'pt' ? 'Planetas no Seu Mapa' : 'Planets in Your Chart'}
          </h2>
          <p className="text-muted-foreground mt-2">
            {language === 'pt' ? 'Explore as energias planetárias que compõem sua essência' : 'Explore the planetary energies that make up your essence'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Legenda de Categorias */}
      <div className="bg-card rounded-xl p-5 border border-border">
        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
          <UIIcons.Info size={18} className="text-primary" />
          {language === 'pt' ? 'Categorias Planetárias' : 'Planetary Categories'}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {(language === 'pt' ? planetCategories.pt : planetCategories.en).map((cat, idx) => (
            <div key={idx} className="p-3 rounded-lg bg-muted/50 text-center">
              <p className="font-medium text-sm text-foreground">{cat.name}</p>
              <p className="text-xs text-muted-foreground mt-1">{cat.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Planets Grid */}
      <div>
        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2">
          <UIIcons.Star size={18} className="text-primary" />
          {language === 'pt' ? 'Seus Planetas' : 'Your Planets'}
        </h3>
        <p className="text-sm text-muted-foreground mb-4">
          {language === 'pt' 
            ? 'Clique em qualquer planeta para ver sua análise completa abaixo' 
            : 'Click on any planet to see its complete analysis below'}
        </p>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {planetData.map((planet, index) => {
          const PlanetIcon = planets[index]?.icon;
          const SignIcon = zodiacSigns.find(z => z.name === planet.sign)?.icon;
          const isSelected = selectedPlanet === planet.name;
          const info = language === 'pt' 
            ? planetInfo.pt[planet.name as keyof typeof planetInfo.pt]
            : planetInfo.en[planet.nameEn as keyof typeof planetInfo.en];
          
          // Validar se o planeta tem signo antes de renderizar
          if (!planet.sign) {
            console.warn(`Planeta ${planet.name} não tem signo definido`);
            return null;
          }
          
          return (
            <button
              key={planet.name}
              onClick={() => {
                console.log('Clique no planeta:', planet.name, 'Signo:', planet.sign, 'Casa:', planet.house);
                fetchPlanetInterpretation(planet.name, planet.sign, planet.house || 0);
              }}
              className={`p-4 rounded-xl border transition-all hover:scale-105 ${
                isSelected 
                    ? `${planet.bgColor} border-current shadow-lg` 
                  : 'bg-card border-border hover:border-primary/50'
              }`}
            >
              <div className="flex flex-col items-center gap-3">
                  <div className={`w-12 h-12 rounded-full ${planet.bgColor} flex items-center justify-center`}>
                    {PlanetIcon && <PlanetIcon size={28} className={planet.color} />}
                  </div>
                <div className="text-center">
                    <p className={`font-semibold ${isSelected ? planet.color : 'text-foreground'}`}>
                      {language === 'pt' ? planet.name : planet.nameEn}
                    </p>
                    <p className="text-lg font-bold text-muted-foreground">{info?.symbol || '?'}</p>
                  <div className="flex items-center justify-center gap-1 mt-1">
                    {SignIcon && <SignIcon size={14} className="text-muted-foreground" />}
                    <p className="text-xs text-muted-foreground">{planet.sign}</p>
                  </div>
                    {planet.house && planet.house > 0 && (
                      <p className="text-xs text-muted-foreground">
                        {language === 'pt' ? 'Casa' : 'House'} {planet.house}
                      </p>
                    )}
                </div>
              </div>
            </button>
          );
        })}
        </div>
      </div>

      {/* Interpretation Panel */}
      {selectedPlanet && selectedPlanetData && (
        <div className="bg-card rounded-xl p-6 border border-border animate-fadeIn">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 gap-4">
              <UIIcons.Loader className="w-8 h-8 animate-spin text-primary" />
              <p className="text-muted-foreground">
                {language === 'pt' ? 'Analisando o planeta...' : 'Analyzing the planet...'}
              </p>
            </div>
          ) : interpretation ? (
            <FormattedPlanetInterpretation 
              text={interpretation} 
              language={language}
              planetName={selectedPlanet}
              sign={selectedPlanetData.sign}
              house={selectedPlanetData.house}
            />
          ) : (
            <div className="flex flex-col items-center justify-center py-12 gap-4">
              <UIIcons.AlertCircle className="w-8 h-8 text-muted-foreground" />
              <p className="text-muted-foreground">
                {language === 'pt' 
                  ? 'Não foi possível carregar a interpretação. Tente novamente.' 
                  : 'Could not load interpretation. Please try again.'}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

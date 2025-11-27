import { useState, useEffect } from 'react';
import { UIIcons } from './ui-icons';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';
import { BirthChartWheel } from './birth-chart-wheel';
import { ElementChart } from './element-chart';
import { FutureTransitsSection } from './future-transits-section';
import { apiService } from '../services/api';
import { useLanguage } from '../i18n';
import { OnboardingData } from './onboarding';

// ===== VISÃO GERAL =====
interface OverviewSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const OverviewSection = ({ userData, onBack }: OverviewSectionProps) => {
  const { t, language } = useLanguage();
  const [chartRulerInterpretation, setChartRulerInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  // Determinar signo e regente baseado nos dados do usuário
  const ascendantSign = userData.ascendant || 'Áries';
  const sunSign = userData.sunSign || 'Áries';
  const moonSign = userData.moonSign || 'Touro';

  // Mapeamento de regentes
  const rulerMap: Record<string, string> = {
    'Áries': 'Marte', 'Touro': 'Vênus', 'Gêmeos': 'Mercúrio', 'Câncer': 'Lua',
    'Leão': 'Sol', 'Virgem': 'Mercúrio', 'Libra': 'Vênus', 'Escorpião': 'Plutão',
    'Sagitário': 'Júpiter', 'Capricórnio': 'Saturno', 'Aquário': 'Urano', 'Peixes': 'Netuno'
  };

  const chartRuler = rulerMap[ascendantSign] || 'Sol';

  // Dados dos elementos baseados nos planetas
  const elementData = [
    { name: language === 'pt' ? 'Fogo' : 'Fire', percentage: 35, color: '#F97316' },
    { name: language === 'pt' ? 'Terra' : 'Earth', percentage: 25, color: '#22C55E' },
    { name: language === 'pt' ? 'Ar' : 'Air', percentage: 25, color: '#3B82F6' },
    { name: language === 'pt' ? 'Água' : 'Water', percentage: 15, color: '#8B5CF6' },
  ];

  useEffect(() => {
    const fetchInterpretation = async () => {
      try {
        setIsLoading(true);
        const result = await apiService.getChartRulerInterpretation({
          ascendant: ascendantSign,
          ruler: chartRuler,
          rulerSign: sunSign,
          rulerHouse: 1,
        });
        setChartRulerInterpretation(result.interpretation);
      } catch (error) {
        console.error('Erro ao buscar interpretação:', error);
        setChartRulerInterpretation(
          language === 'pt' 
            ? `Com Ascendente em ${ascendantSign}, seu planeta regente é ${chartRuler}. Este planeta guia sua jornada de vida e influencia como você se expressa no mundo.`
            : `With Ascendant in ${ascendantSign}, your ruling planet is ${chartRuler}. This planet guides your life journey and influences how you express yourself in the world.`
        );
      } finally {
        setIsLoading(false);
      }
    };
    fetchInterpretation();
  }, [ascendantSign, chartRuler, sunSign, language]);

  const AscIcon = zodiacSigns.find(z => z.name === ascendantSign)?.icon || zodiacSigns[0].icon;
  const SunIcon = zodiacSigns.find(z => z.name === sunSign)?.icon || zodiacSigns[0].icon;
  const MoonIcon = zodiacSigns.find(z => z.name === moonSign)?.icon || zodiacSigns[0].icon;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif text-3xl font-bold text-foreground">
            {language === 'pt' ? 'Visão Geral do Seu Mapa' : 'Your Chart Overview'}
          </h2>
          <p className="text-muted-foreground mt-2">
            {language === 'pt' ? 'Explore os principais elementos do seu mapa astral' : 'Explore the main elements of your birth chart'}
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

      {/* Big Three Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-orange-500/20 to-orange-500/5 rounded-xl p-6 border border-orange-500/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-lg bg-orange-500/20 flex items-center justify-center">
              <SunIcon size={28} className="text-orange-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{language === 'pt' ? 'Sol' : 'Sun'}</p>
              <p className="font-bold text-xl text-foreground">{sunSign}</p>
            </div>
          </div>
          <p className="text-sm text-foreground/70">
            {language === 'pt' ? 'Sua essência e identidade central' : 'Your essence and core identity'}
          </p>
        </div>

        <div className="bg-gradient-to-br from-purple-500/20 to-purple-500/5 rounded-xl p-6 border border-purple-500/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-lg bg-purple-500/20 flex items-center justify-center">
              <MoonIcon size={28} className="text-purple-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{language === 'pt' ? 'Lua' : 'Moon'}</p>
              <p className="font-bold text-xl text-foreground">{moonSign}</p>
            </div>
          </div>
          <p className="text-sm text-foreground/70">
            {language === 'pt' ? 'Suas emoções e mundo interior' : 'Your emotions and inner world'}
          </p>
        </div>

        <div className="bg-gradient-to-br from-blue-500/20 to-blue-500/5 rounded-xl p-6 border border-blue-500/30">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
              <AscIcon size={28} className="text-blue-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{language === 'pt' ? 'Ascendente' : 'Ascendant'}</p>
              <p className="font-bold text-xl text-foreground">{ascendantSign}</p>
            </div>
          </div>
          <p className="text-sm text-foreground/70">
            {language === 'pt' ? 'Como você se apresenta ao mundo' : 'How you present yourself to the world'}
          </p>
        </div>
      </div>

      {/* Birth Chart Wheel */}
      <div className="bg-card rounded-xl p-6 border border-border">
        <h3 className="font-serif text-xl font-bold text-foreground mb-6">
          {language === 'pt' ? 'Roda do Mapa Astral' : 'Birth Chart Wheel'}
        </h3>
        <BirthChartWheel />
      </div>

      {/* Chart Ruler & Elements Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart Ruler */}
        <div className="bg-card rounded-xl p-6 border border-border">
          <h3 className="font-serif text-xl font-bold text-foreground mb-4">
            {language === 'pt' ? 'Regente do Mapa' : 'Chart Ruler'}
          </h3>
          <div className="flex items-center gap-4 mb-4 p-4 bg-primary/10 rounded-lg">
            <div className="w-14 h-14 rounded-full bg-primary/20 flex items-center justify-center">
              {planets.find(p => p.name === chartRuler)?.icon && (
                <div className="text-primary">
                  {(() => {
                    const PlanetIcon = planets.find(p => p.name === chartRuler)?.icon;
                    return PlanetIcon ? <PlanetIcon size={32} /> : null;
                  })()}
                </div>
              )}
            </div>
            <div>
              <p className="font-bold text-lg text-foreground">{chartRuler}</p>
              <p className="text-sm text-muted-foreground">
                {language === 'pt' ? `Regente de ${ascendantSign}` : `Ruler of ${ascendantSign}`}
              </p>
            </div>
          </div>
          {isLoading ? (
            <div className="flex items-center gap-3 py-4">
              <UIIcons.Loader className="w-5 h-5 animate-spin text-primary" />
              <p className="text-muted-foreground">
                {language === 'pt' ? 'Gerando interpretação...' : 'Generating interpretation...'}
              </p>
            </div>
          ) : (
            <p className="text-foreground/80 leading-relaxed">{chartRulerInterpretation}</p>
          )}
        </div>

        {/* Elements Distribution */}
        <div className="bg-card rounded-xl p-6 border border-border">
          <h3 className="font-serif text-xl font-bold text-foreground mb-4">
            {language === 'pt' ? 'Distribuição dos Elementos' : 'Elements Distribution'}
          </h3>
          <ElementChart 
            data={elementData} 
            title="" 
          />
        </div>
      </div>
    </div>
  );
};

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
  const planetColors: Record<string, { bg: string; border: string; text: string }> = {
    Sol: { bg: 'from-orange-500/20 to-yellow-500/10', border: 'border-orange-500/30', text: 'text-orange-500' },
    Sun: { bg: 'from-orange-500/20 to-yellow-500/10', border: 'border-orange-500/30', text: 'text-orange-500' },
    Lua: { bg: 'from-purple-500/20 to-indigo-500/10', border: 'border-purple-500/30', text: 'text-purple-500' },
    Moon: { bg: 'from-purple-500/20 to-indigo-500/10', border: 'border-purple-500/30', text: 'text-purple-500' },
    Mercúrio: { bg: 'from-cyan-500/20 to-blue-500/10', border: 'border-cyan-500/30', text: 'text-cyan-500' },
    Mercury: { bg: 'from-cyan-500/20 to-blue-500/10', border: 'border-cyan-500/30', text: 'text-cyan-500' },
    Vênus: { bg: 'from-pink-500/20 to-rose-500/10', border: 'border-pink-500/30', text: 'text-pink-500' },
    Venus: { bg: 'from-pink-500/20 to-rose-500/10', border: 'border-pink-500/30', text: 'text-pink-500' },
    Marte: { bg: 'from-red-500/20 to-orange-500/10', border: 'border-red-500/30', text: 'text-red-500' },
    Mars: { bg: 'from-red-500/20 to-orange-500/10', border: 'border-red-500/30', text: 'text-red-500' },
    Júpiter: { bg: 'from-amber-500/20 to-yellow-500/10', border: 'border-amber-500/30', text: 'text-amber-500' },
    Jupiter: { bg: 'from-amber-500/20 to-yellow-500/10', border: 'border-amber-500/30', text: 'text-amber-500' },
    Saturno: { bg: 'from-gray-500/20 to-slate-500/10', border: 'border-gray-500/30', text: 'text-gray-500' },
    Saturn: { bg: 'from-gray-500/20 to-slate-500/10', border: 'border-gray-500/30', text: 'text-gray-500' },
    Urano: { bg: 'from-teal-500/20 to-cyan-500/10', border: 'border-teal-500/30', text: 'text-teal-500' },
    Uranus: { bg: 'from-teal-500/20 to-cyan-500/10', border: 'border-teal-500/30', text: 'text-teal-500' },
    Netuno: { bg: 'from-blue-500/20 to-indigo-500/10', border: 'border-blue-500/30', text: 'text-blue-500' },
    Neptune: { bg: 'from-blue-500/20 to-indigo-500/10', border: 'border-blue-500/30', text: 'text-blue-500' },
    Plutão: { bg: 'from-rose-500/20 to-red-500/10', border: 'border-rose-500/30', text: 'text-rose-500' },
    Pluto: { bg: 'from-rose-500/20 to-red-500/10', border: 'border-rose-500/30', text: 'text-rose-500' },
  };

  const colors = planetColors[planetName] || { bg: 'from-primary/20 to-primary/5', border: 'border-primary/30', text: 'text-primary' };

  // Dividir o texto em parágrafos
  const paragraphs = text.split(/\n\n+/).filter(p => p.trim());

  return (
    <div className="space-y-6">
      {/* Header do Planeta */}
      <div className={`bg-gradient-to-br ${colors.bg} rounded-xl p-5 border ${colors.border}`}>
        <div className="flex items-center gap-4 mb-4">
          <div className={`w-16 h-16 rounded-full bg-white/20 dark:bg-black/20 flex items-center justify-center`}>
            <span className={`text-4xl ${colors.text}`}>
              {planetData?.symbol || '★'}
            </span>
          </div>
          <div>
            <h3 className="font-serif text-xl font-bold text-foreground">
              {planetName} {language === 'pt' ? 'em' : 'in'} {sign}
            </h3>
            <p className={`text-sm font-medium ${colors.text}`}>
              Casa {house} • {planetData?.domain}
            </p>
          </div>
        </div>
        
        {/* Palavras-chave */}
        {planetData?.keywords && (
          <div className="flex flex-wrap gap-2 mb-4">
            {planetData.keywords.map((keyword, idx) => (
              <span 
                key={idx}
                className={`px-3 py-1 rounded-full text-xs font-medium bg-white/30 dark:bg-black/20 ${colors.text}`}
              >
                {keyword}
              </span>
            ))}
          </div>
        )}
        
        {/* Elemento */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">{language === 'pt' ? 'Elemento:' : 'Element:'}</span>
          <span className={`text-xs font-medium ${colors.text}`}>{planetData?.element}</span>
        </div>
      </div>

      {/* Seções da Interpretação */}
      {paragraphs.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-semibold text-foreground flex items-center gap-2">
            <UIIcons.BookOpen className="w-5 h-5 text-primary" />
            {language === 'pt' ? 'Interpretação Completa' : 'Complete Interpretation'}
          </h4>
          
          {paragraphs.map((paragraph, index) => {
            // Identificar tipo de seção
            const lowerP = paragraph.toLowerCase();
            let sectionType = 'general';
            let sectionIcon = <UIIcons.BookOpen className="w-5 h-5" />;
            let sectionTitle = language === 'pt' ? '📖 Análise' : '📖 Analysis';
            let sectionColor = 'text-purple-500';
            
            if (lowerP.includes('personalidade') || lowerP.includes('personality') || lowerP.includes('essência') || lowerP.includes('essence')) {
              sectionType = 'personality';
              sectionIcon = <UIIcons.User className="w-5 h-5" />;
              sectionTitle = language === 'pt' ? '👤 Personalidade' : '👤 Personality';
              sectionColor = 'text-blue-500';
            } else if (lowerP.includes('desafio') || lowerP.includes('challenge') || lowerP.includes('dificuldade') || lowerP.includes('difficulty')) {
              sectionType = 'challenge';
              sectionIcon = <UIIcons.AlertCircle className="w-5 h-5" />;
              sectionTitle = language === 'pt' ? '🔥 Desafios' : '🔥 Challenges';
              sectionColor = 'text-red-500';
            } else if (lowerP.includes('potencial') || lowerP.includes('potential') || lowerP.includes('talento') || lowerP.includes('talent') || lowerP.includes('dom') || lowerP.includes('gift')) {
              sectionType = 'potential';
              sectionIcon = <UIIcons.Star className="w-5 h-5" />;
              sectionTitle = language === 'pt' ? '✨ Potenciais e Dons' : '✨ Potentials and Gifts';
              sectionColor = 'text-emerald-500';
            } else if (lowerP.includes('conselho') || lowerP.includes('advice') || lowerP.includes('orientação') || lowerP.includes('guidance') || lowerP.includes('recomend')) {
              sectionType = 'advice';
              sectionIcon = <UIIcons.Compass className="w-5 h-5" />;
              sectionTitle = language === 'pt' ? '🧭 Orientações' : '🧭 Guidance';
              sectionColor = 'text-amber-500';
            } else if (lowerP.includes('relacionamento') || lowerP.includes('relationship') || lowerP.includes('amor') || lowerP.includes('love')) {
              sectionType = 'relationships';
              sectionIcon = <UIIcons.Heart className="w-5 h-5" />;
              sectionTitle = language === 'pt' ? '💖 Relacionamentos' : '💖 Relationships';
              sectionColor = 'text-pink-500';
            } else if (lowerP.includes('carreira') || lowerP.includes('career') || lowerP.includes('profissão') || lowerP.includes('profession') || lowerP.includes('trabalho') || lowerP.includes('work')) {
              sectionType = 'career';
              sectionIcon = <UIIcons.Briefcase className="w-5 h-5" />;
              sectionTitle = language === 'pt' ? '💼 Carreira' : '💼 Career';
              sectionColor = 'text-indigo-500';
            }
            
            return (
              <div 
                key={index}
                className="bg-muted/30 rounded-lg p-4 border border-border/50"
              >
                <div className="flex items-start gap-3">
                  <div className={`flex-shrink-0 mt-0.5 ${sectionColor}`}>
                    {sectionIcon}
                  </div>
                  <div className="flex-1">
                    {paragraphs.length > 1 && (
                      <p className={`text-sm font-medium mb-2 ${sectionColor}`}>
                        {sectionTitle}
                      </p>
                    )}
                    <p className="text-foreground leading-relaxed">
                      {paragraph}
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

export const PlanetsSection = ({ userData, onBack }: PlanetsSectionProps) => {
  const { language } = useLanguage();
  const [selectedPlanet, setSelectedPlanet] = useState<string | null>(null);
  const [selectedPlanetData, setSelectedPlanetData] = useState<{ sign: string; house: number } | null>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // Lista de planetas com signos (mock data que seria do userData)
  const planetData = [
    { name: 'Sol', nameEn: 'Sun', sign: userData.sunSign || 'Áries', house: 1, color: 'text-orange-500', bgColor: 'bg-orange-500/10' },
    { name: 'Lua', nameEn: 'Moon', sign: userData.moonSign || 'Touro', house: 4, color: 'text-purple-500', bgColor: 'bg-purple-500/10' },
    { name: 'Mercúrio', nameEn: 'Mercury', sign: 'Gêmeos', house: 3, color: 'text-cyan-500', bgColor: 'bg-cyan-500/10' },
    { name: 'Vênus', nameEn: 'Venus', sign: 'Touro', house: 2, color: 'text-pink-500', bgColor: 'bg-pink-500/10' },
    { name: 'Marte', nameEn: 'Mars', sign: 'Áries', house: 1, color: 'text-red-500', bgColor: 'bg-red-500/10' },
    { name: 'Júpiter', nameEn: 'Jupiter', sign: 'Sagitário', house: 9, color: 'text-amber-500', bgColor: 'bg-amber-500/10' },
    { name: 'Saturno', nameEn: 'Saturn', sign: 'Capricórnio', house: 10, color: 'text-gray-500', bgColor: 'bg-gray-500/10' },
    { name: 'Urano', nameEn: 'Uranus', sign: 'Aquário', house: 11, color: 'text-teal-500', bgColor: 'bg-teal-500/10' },
    { name: 'Netuno', nameEn: 'Neptune', sign: 'Peixes', house: 12, color: 'text-blue-500', bgColor: 'bg-blue-500/10' },
    { name: 'Plutão', nameEn: 'Pluto', sign: 'Escorpião', house: 8, color: 'text-rose-500', bgColor: 'bg-rose-500/10' },
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
      const result = await apiService.getPlanetInterpretation({
        planet: planetName,
        sign: sign,
        house: house,
      });
      setInterpretation(result.interpretation);
    } catch (error) {
      console.error('Erro ao buscar interpretação:', error);
      setInterpretation(
        language === 'pt'
          ? `${planetName} em ${sign} na Casa ${house} traz influências importantes para sua vida. Este posicionamento revela aspectos únicos da sua personalidade e jornada. O planeta ${planetName} governa áreas específicas da experiência humana, e sua posição no signo de ${sign} colore a forma como você expressa essas energias.`
          : `${planetName} in ${sign} in House ${house} brings important influences to your life. This placement reveals unique aspects of your personality and journey. The planet ${planetName} rules specific areas of human experience, and its position in the sign of ${sign} colors how you express these energies.`
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
        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
          <UIIcons.Star size={18} className="text-primary" />
          {language === 'pt' ? 'Seus Planetas' : 'Your Planets'}
        </h3>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {planetData.map((planet, index) => {
          const PlanetIcon = planets[index]?.icon;
          const SignIcon = zodiacSigns.find(z => z.name === planet.sign)?.icon;
          const isSelected = selectedPlanet === planet.name;
            const info = planetInfo.pt[planet.name as keyof typeof planetInfo.pt];
          
          return (
            <button
              key={planet.name}
              onClick={() => fetchPlanetInterpretation(planet.name, planet.sign, planet.house)}
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
                    <p className="text-lg font-bold text-muted-foreground">{info?.symbol}</p>
                  <div className="flex items-center justify-center gap-1 mt-1">
                    {SignIcon && <SignIcon size={14} className="text-muted-foreground" />}
                    <p className="text-xs text-muted-foreground">{planet.sign}</p>
                  </div>
                    <p className="text-xs text-muted-foreground">
                      {language === 'pt' ? 'Casa' : 'House'} {planet.house}
                    </p>
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
              ) : (
            <FormattedPlanetInterpretation 
              text={interpretation} 
              language={language}
              planetName={selectedPlanet}
              sign={selectedPlanetData.sign}
              house={selectedPlanetData.house}
            />
              )}
        </div>
      )}
    </div>
  );
};

// ===== CASAS =====
interface HousesSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const HousesSection = ({ userData, onBack }: HousesSectionProps) => {
  const { language } = useLanguage();
  const [selectedHouse, setSelectedHouse] = useState<number | null>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const houseMeanings = {
    pt: [
      { house: 1, title: 'Identidade', desc: 'Aparência, personalidade, primeira impressão' },
      { house: 2, title: 'Recursos', desc: 'Finanças, valores, posses materiais' },
      { house: 3, title: 'Comunicação', desc: 'Irmãos, vizinhos, aprendizado' },
      { house: 4, title: 'Lar', desc: 'Família, raízes, vida doméstica' },
      { house: 5, title: 'Criatividade', desc: 'Romance, filhos, hobbies' },
      { house: 6, title: 'Rotina', desc: 'Saúde, trabalho diário, serviço' },
      { house: 7, title: 'Parcerias', desc: 'Casamento, sociedades, contratos' },
      { house: 8, title: 'Transformação', desc: 'Crises, heranças, sexualidade' },
      { house: 9, title: 'Expansão', desc: 'Viagens, filosofia, ensino superior' },
      { house: 10, title: 'Carreira', desc: 'Profissão, status, reputação' },
      { house: 11, title: 'Amizades', desc: 'Grupos, sonhos, causas sociais' },
      { house: 12, title: 'Espiritualidade', desc: 'Inconsciente, karma, isolamento' },
    ],
    en: [
      { house: 1, title: 'Identity', desc: 'Appearance, personality, first impression' },
      { house: 2, title: 'Resources', desc: 'Finances, values, material possessions' },
      { house: 3, title: 'Communication', desc: 'Siblings, neighbors, learning' },
      { house: 4, title: 'Home', desc: 'Family, roots, domestic life' },
      { house: 5, title: 'Creativity', desc: 'Romance, children, hobbies' },
      { house: 6, title: 'Routine', desc: 'Health, daily work, service' },
      { house: 7, title: 'Partnerships', desc: 'Marriage, partnerships, contracts' },
      { house: 8, title: 'Transformation', desc: 'Crises, inheritance, sexuality' },
      { house: 9, title: 'Expansion', desc: 'Travel, philosophy, higher education' },
      { house: 10, title: 'Career', desc: 'Profession, status, reputation' },
      { house: 11, title: 'Friendships', desc: 'Groups, dreams, social causes' },
      { house: 12, title: 'Spirituality', desc: 'Unconscious, karma, isolation' },
    ],
  };

  const houses = houseMeanings[language === 'pt' ? 'pt' : 'en'];

  const fetchHouseInterpretation = async (house: number) => {
    try {
      setIsLoading(true);
      setSelectedHouse(house);
      const result = await apiService.getInterpretation({
        house: house,
        custom_query: `Casa ${house} no mapa astral significado interpretação áreas da vida`,
        use_groq: true,
      });
      setInterpretation(result.interpretation);
    } catch (error) {
      console.error('Erro ao buscar interpretação:', error);
      const houseData = houses.find(h => h.house === house);
      setInterpretation(
        language === 'pt'
          ? `A Casa ${house} rege ${houseData?.desc}. Esta área do mapa revela como você lida com esses temas na sua vida.`
          : `House ${house} rules ${houseData?.desc}. This area of the chart reveals how you handle these themes in your life.`
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
            {language === 'pt' ? 'As 12 Casas Astrológicas' : 'The 12 Astrological Houses'}
          </h2>
          <p className="text-muted-foreground mt-2">
            {language === 'pt' ? 'Cada casa representa uma área da sua vida' : 'Each house represents an area of your life'}
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

      {/* Houses Grid */}
      <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {houses.map((house) => {
          const isSelected = selectedHouse === house.house;
          return (
            <button
              key={house.house}
              onClick={() => fetchHouseInterpretation(house.house)}
              className={`p-4 rounded-xl border transition-all hover:scale-105 ${
                isSelected 
                  ? 'bg-primary/20 border-primary shadow-lg' 
                  : 'bg-card border-border hover:border-primary/50'
              }`}
            >
              <div className="text-center">
                <div className={`w-10 h-10 mx-auto rounded-full flex items-center justify-center mb-2 ${
                  isSelected ? 'bg-primary text-white' : 'bg-muted text-foreground'
                }`}>
                  <span className="font-bold">{house.house}</span>
                </div>
                <p className="font-medium text-sm text-foreground">{house.title}</p>
              </div>
            </button>
          );
        })}
      </div>

      {/* Interpretation Panel */}
      {selectedHouse && (
        <div className="bg-card rounded-xl p-6 border border-border animate-fadeIn">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-full bg-primary flex items-center justify-center flex-shrink-0 text-white text-xl font-bold">
              {selectedHouse}
            </div>
            <div className="flex-1">
              <h3 className="font-serif text-xl font-bold text-foreground mb-1">
                Casa {selectedHouse}: {houses.find(h => h.house === selectedHouse)?.title}
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                {houses.find(h => h.house === selectedHouse)?.desc}
              </p>
              {isLoading ? (
                <div className="flex items-center gap-3 py-4">
                  <UIIcons.Loader className="w-5 h-5 animate-spin text-primary" />
                  <p className="text-muted-foreground">
                    {language === 'pt' ? 'Buscando interpretação...' : 'Fetching interpretation...'}
                  </p>
                </div>
              ) : (
                <p className="text-foreground/80 leading-relaxed whitespace-pre-line">{interpretation}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ===== GUIA 2026 =====
interface Guide2026SectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const Guide2026Section = ({ userData, onBack }: Guide2026SectionProps) => {
  const { language } = useLanguage();

  // Destaques astrológicos de 2026
  const highlights = language === 'pt' ? [
    { icon: '♃', title: 'Júpiter em Câncer', period: 'Jun 2025 - Jul 2026', desc: 'Expansão emocional e familiar', color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { icon: '♄', title: 'Saturno em Áries', period: 'Mar 2025 - Mai 2026', desc: 'Novos começos estruturados', color: 'text-gray-500', bg: 'bg-gray-500/10' },
    { icon: '♅', title: 'Urano em Gêmeos', period: 'Jul 2025 - 2033', desc: 'Revolução na comunicação', color: 'text-teal-500', bg: 'bg-teal-500/10' },
    { icon: '♆', title: 'Netuno em Áries', period: 'Mar 2025 - 2039', desc: 'Nova era espiritual', color: 'text-blue-500', bg: 'bg-blue-500/10' },
  ] : [
    { icon: '♃', title: 'Jupiter in Cancer', period: 'Jun 2025 - Jul 2026', desc: 'Emotional and family expansion', color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { icon: '♄', title: 'Saturn in Aries', period: 'Mar 2025 - May 2026', desc: 'Structured new beginnings', color: 'text-gray-500', bg: 'bg-gray-500/10' },
    { icon: '♅', title: 'Uranus in Gemini', period: 'Jul 2025 - 2033', desc: 'Communication revolution', color: 'text-teal-500', bg: 'bg-teal-500/10' },
    { icon: '♆', title: 'Neptune in Aries', period: 'Mar 2025 - 2039', desc: 'New spiritual era', color: 'text-blue-500', bg: 'bg-blue-500/10' },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif text-3xl font-bold text-foreground">
            {language === 'pt' ? 'Guia Astrológico 2026' : '2026 Astrological Guide'}
          </h2>
          <p className="text-muted-foreground mt-2">
            {language === 'pt' ? 'Previsões e tendências para os próximos meses' : 'Predictions and trends for the coming months'}
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

      {/* Destaques do Ano */}
      <div className="bg-card rounded-xl p-5 border border-border">
        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
          <UIIcons.Star size={18} className="text-primary" />
          {language === 'pt' ? 'Destaques Astrológicos' : 'Astrological Highlights'}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {highlights.map((item, idx) => (
            <div key={idx} className={`${item.bg} rounded-lg p-4 border border-border/50`}>
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-2xl ${item.color}`}>{item.icon}</span>
                <span className="text-xs text-muted-foreground">{item.period}</span>
              </div>
              <p className={`font-semibold text-sm ${item.color}`}>{item.title}</p>
              <p className="text-xs text-foreground mt-1">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Legenda de Tipos de Trânsitos */}
      <div className="bg-card rounded-xl p-5 border border-border">
        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
          <UIIcons.Info size={18} className="text-primary" />
          {language === 'pt' ? 'Tipos de Trânsitos' : 'Transit Types'}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="flex items-center gap-2 p-2 rounded-lg bg-[#E8B95A]/10">
            <span className="text-lg">🌟</span>
            <div>
              <p className="text-sm font-medium text-foreground">{language === 'pt' ? 'Expansão' : 'Expansion'}</p>
              <p className="text-xs text-muted-foreground">{language === 'pt' ? 'Júpiter' : 'Jupiter'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 p-2 rounded-lg bg-[#8B7355]/10">
            <span className="text-lg">🏛️</span>
            <div>
              <p className="text-sm font-medium text-foreground">{language === 'pt' ? 'Estrutura' : 'Structure'}</p>
              <p className="text-xs text-muted-foreground">{language === 'pt' ? 'Saturno' : 'Saturn'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 p-2 rounded-lg bg-[#4ECDC4]/10">
            <span className="text-lg">⚡</span>
            <div>
              <p className="text-sm font-medium text-foreground">{language === 'pt' ? 'Mudança' : 'Change'}</p>
              <p className="text-xs text-muted-foreground">{language === 'pt' ? 'Urano' : 'Uranus'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 p-2 rounded-lg bg-[#9B59B6]/10">
            <span className="text-lg">🌊</span>
            <div>
              <p className="text-sm font-medium text-foreground">{language === 'pt' ? 'Espiritualidade' : 'Spirituality'}</p>
              <p className="text-xs text-muted-foreground">{language === 'pt' ? 'Netuno' : 'Neptune'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 p-2 rounded-lg bg-[#E74C3C]/10">
            <span className="text-lg">🔥</span>
            <div>
              <p className="text-sm font-medium text-foreground">{language === 'pt' ? 'Transformação' : 'Transformation'}</p>
              <p className="text-xs text-muted-foreground">{language === 'pt' ? 'Plutão' : 'Pluto'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Future Transits Component */}
      <div>
        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
          <UIIcons.Calendar size={18} className="text-primary" />
          {language === 'pt' ? 'Seus Trânsitos Pessoais' : 'Your Personal Transits'}
        </h3>
      <FutureTransitsSection />
      </div>
    </div>
  );
};

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

  const colorMap: Record<string, string> = {
    blue: 'from-blue-500/20 to-blue-500/5 border-blue-500/30',
    green: 'from-green-500/20 to-green-500/5 border-green-500/30',
    cyan: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/30',
    red: 'from-red-500/20 to-red-500/5 border-red-500/30',
    orange: 'from-orange-500/20 to-orange-500/5 border-orange-500/30',
  };

  const iconColorMap: Record<string, string> = {
    blue: 'text-blue-500',
    green: 'text-green-500',
    cyan: 'text-cyan-500',
    red: 'text-red-500',
    orange: 'text-orange-500',
  };

  const bgColorMap: Record<string, string> = {
    blue: 'bg-blue-500/20',
    green: 'bg-green-500/20',
    cyan: 'bg-cyan-500/20',
    red: 'bg-red-500/20',
    orange: 'bg-orange-500/20',
  };

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
      icon: <UIIcons.Zap className="w-5 h-5" />,
      title: { pt: '⚡ Energia da Conexão', en: '⚡ Connection Energy' },
      color: 'text-amber-500',
    },
    challenge: {
      icon: <UIIcons.AlertCircle className="w-5 h-5" />,
      title: { pt: '🔥 Desafios e Tensões', en: '🔥 Challenges and Tensions' },
      color: 'text-red-500',
    },
    potential: {
      icon: <UIIcons.Star className="w-5 h-5" />,
      title: { pt: '✨ Potenciais e Dons', en: '✨ Potentials and Gifts' },
      color: 'text-emerald-500',
    },
    advice: {
      icon: <UIIcons.Compass className="w-5 h-5" />,
      title: { pt: '🧭 Orientações Práticas', en: '🧭 Practical Guidance' },
      color: 'text-blue-500',
    },
    general: {
      icon: <UIIcons.BookOpen className="w-5 h-5" />,
      title: { pt: '📖 Interpretação', en: '📖 Interpretation' },
      color: 'text-purple-500',
    },
  };

  return (
    <div className="space-y-6">
      {/* Header do Aspecto */}
      <div className={`bg-gradient-to-br ${colorMap[aspectInfo?.color || 'blue']} rounded-xl p-5 border`}>
        <div className="flex items-center gap-4 mb-4">
          <div className={`w-14 h-14 rounded-full ${bgColorMap[aspectInfo?.color || 'blue']} flex items-center justify-center`}>
            <span className={`text-3xl ${iconColorMap[aspectInfo?.color || 'blue']}`}>
              {aspectInfo?.symbol || '☌'}
            </span>
          </div>
          <div>
            <h3 className="font-serif text-xl font-bold text-foreground">
              {planet1} {aspectInfo?.symbol} {planet2}
            </h3>
            <p className={`text-sm font-medium ${iconColorMap[aspectInfo?.color || 'blue']}`}>
              {aspectType} • {aspectInfo?.nature}
            </p>
          </div>
        </div>
        
        {/* Palavras-chave */}
        {aspectInfo?.keywords && (
          <div className="flex flex-wrap gap-2 mb-4">
            {aspectInfo.keywords.map((keyword, idx) => (
              <span 
                key={idx}
                className={`px-3 py-1 rounded-full text-xs font-medium ${bgColorMap[aspectInfo.color]} ${iconColorMap[aspectInfo.color]}`}
              >
                {keyword}
              </span>
            ))}
          </div>
        )}
        
        <p className="text-sm text-foreground/70">
          {aspectInfo?.description}
        </p>
      </div>

      {/* Seções da Interpretação */}
      {paragraphs.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-semibold text-foreground flex items-center gap-2">
            <UIIcons.BookOpen className="w-5 h-5 text-primary" />
            {language === 'pt' ? 'Análise Detalhada' : 'Detailed Analysis'}
          </h4>
          
          {paragraphs.map((paragraph, index) => {
            const section = identifySection(paragraph);
            const sectionInfo = sectionIcons[section.type];
            
            return (
              <div 
                key={index}
                className="bg-muted/30 rounded-lg p-4 border border-border/50"
              >
                <div className="flex items-start gap-3">
                  <div className={`flex-shrink-0 mt-0.5 ${sectionInfo.color}`}>
                    {sectionInfo.icon}
                  </div>
                  <div className="flex-1">
                    {paragraphs.length > 1 && (
                      <p className={`text-sm font-medium mb-2 ${sectionInfo.color}`}>
                        {language === 'pt' ? sectionInfo.title.pt : sectionInfo.title.en}
                      </p>
                    )}
                    <p className="text-foreground/80 leading-relaxed">
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif text-3xl font-bold text-foreground">
            {language === 'pt' ? 'Aspectos Planetários' : 'Planetary Aspects'}
          </h2>
          <p className="text-muted-foreground mt-2">
            {language === 'pt' ? 'As conexões entre os planetas do seu mapa' : 'The connections between planets in your chart'}
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

      {/* Legenda Detalhada dos Aspectos */}
      <div className="bg-card rounded-xl p-5 border border-border">
        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
          <UIIcons.Info size={18} className="text-primary" />
          {language === 'pt' ? 'Tipos de Aspectos' : 'Aspect Types'}
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {aspectLegend.map((item) => {
            const IconComponent = item.icon;
            return (
              <div 
                key={item.type} 
                className="flex flex-col p-4 rounded-xl border transition-all hover:scale-105"
                style={{ 
                  borderColor: item.bgColor,
                  backgroundColor: `${item.bgColor}10` 
                }}
              >
                {/* Ícone SVG Grande */}
                <div className="flex items-center gap-3 mb-3">
                  <div 
                    className="w-14 h-14 rounded-full flex items-center justify-center shadow-lg"
                    style={{ backgroundColor: item.bgColor }}
                  >
                    <IconComponent size={28} color="#ffffff" />
          </div>
                  <div>
                    <p className="font-bold text-foreground">{item.type}</p>
                    <p className={`text-xs font-medium ${item.textColor}`}>{item.desc}</p>
                  </div>
                </div>
                {/* Significado */}
                <p className="text-xs text-foreground leading-relaxed bg-muted/50 rounded-lg p-2">
                  {item.meaning}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Lista de Aspectos */}
      <div>
        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
          <UIIcons.Sparkles size={18} className="text-primary" />
          {language === 'pt' ? 'Seus Aspectos' : 'Your Aspects'}
        </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {aspects.map((aspect, index) => {
          const Planet1Icon = planets.find(p => p.name === aspect.planet1)?.icon;
          const Planet2Icon = planets.find(p => p.name === aspect.planet2)?.icon;
          const isSelected = selectedAspect === `${aspect.planet1}-${aspect.planet2}`;

          return (
            <button
              key={index}
                onClick={() => fetchAspectInterpretation(aspect.planet1, aspect.planet2, aspect.type, aspect.typeEn)}
                className={`p-5 rounded-xl border transition-all text-left hover:scale-[1.02] ${
                isSelected 
                  ? 'bg-primary/20 border-primary shadow-lg' 
                  : `${aspect.bgColor} border-border hover:border-primary/50`
              }`}
            >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                      {Planet1Icon && <Planet1Icon size={28} className={aspect.color} />}
                      <span className={`text-2xl font-bold ${aspect.color}`}>{aspect.symbol}</span>
                      {Planet2Icon && <Planet2Icon size={28} className={aspect.color} />}
                </div>
                  </div>
                  <UIIcons.ChevronRight size={20} className={`${isSelected ? 'text-primary' : 'text-muted-foreground'}`} />
                </div>
                <div className="mt-3">
                  <p className="font-semibold text-foreground">
                    {aspect.planet1} {language === 'pt' ? 'e' : 'and'} {aspect.planet2}
                  </p>
                  <p className={`text-sm ${aspect.color} font-medium`}>
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
        <div className="bg-card rounded-xl p-6 border border-border animate-fadeIn">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 gap-4">
              <UIIcons.Loader className="w-8 h-8 animate-spin text-primary" />
              <p className="text-muted-foreground">
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

// ===== NODOS LUNARES =====
interface LunarNodesSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const LunarNodesSection = ({ userData, onBack }: LunarNodesSectionProps) => {
  const { language } = useLanguage();
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  // Dados dos nodos (reais do mapa do usuário)
  const northNode = userData.northNodeSign || 'Virgem';
  const southNode = userData.southNodeSign || 'Peixes';
  const northNodeDegree = userData.northNodeDegree ? Math.floor(userData.northNodeDegree) : 0;
  const southNodeDegree = userData.southNodeDegree ? Math.floor(userData.southNodeDegree) : 0;
  
  // Saturno do usuário (importante para karma e desafios)
  const saturnSign = userData.saturnSign || 'Capricórnio';
  const saturnDegree = userData.saturnDegree ? Math.floor(userData.saturnDegree) : 0;
  
  // Quíron - a ferida do curador
  const chironSign = userData.chironSign || 'Áries';
  const chironDegree = userData.chironDegree ? Math.floor(userData.chironDegree) : 0;

  useEffect(() => {
    const fetchInterpretation = async () => {
      try {
        setIsLoading(true);
        
        // Prompt Mestre com hierarquia de corpos celestes
        const promptPt = `
**CONTEXTO DO SISTEMA:**
Você é o COSMOS ASTRAL, uma engine astrológica avançada. Sua função é gerar uma síntese coerente, não uma lista de definições.

**DIRETRIZES DE HIERARQUIA E PESO:**
- Nível 1 (Peso Máximo): Sol, Lua e Regente do Ascendente
- Nível 2 (Peso Alto): Planetas Pessoais (Mercúrio, Vênus, Marte)
- Nível 3 (Peso Médio): Nodos Lunares, Saturno, Júpiter
- Nível 4 (Peso Refinado): Quíron, Lilith, Planetas Transpessoais

**DEFINIÇÕES ESPECÍFICAS DE INTERPRETAÇÃO:**
• NODOS LUNARES: Interprete como jornada da alma - Nodo Sul (passado/zona de conforto) → Nodo Norte (futuro/desafio evolutivo)
• QUÍRON: A "ferida que vira dom". Onde a pessoa sente inadequação, mas onde se torna mestre em ajudar outros
• SATURNO: O mestre kármico que exige maturidade e onde recompensas vêm tarde, mas sólidas
• Nunca gere contradições sem explicá-las como "tensões internas de amadurecimento"

**DADOS DO NATIVO:**
- Nome: ${userData.name}
- Sol em ${userData.sunSign} (Nível 1 - Essência, Ego Consciente)
- Lua em ${userData.moonSign} (Nível 1 - Inconsciente, Emoções)
- Ascendente em ${userData.ascendant} (Nível 1 - Identidade Projetada)
- Nodo Norte em ${northNode} ${northNodeDegree}° (Nível 3 - Missão de Vida)
- Nodo Sul em ${southNode} ${southNodeDegree}° (Nível 3 - Bagagem de Vidas Passadas)
- Saturno em ${saturnSign} ${saturnDegree}° (Nível 3 - Mestre Kármico, Estrutura)
- Quíron em ${chironSign} ${chironDegree}° (Nível 4 - O Curador Ferido)

**SEÇÃO: CARMA, DESAFIOS E EVOLUÇÃO (A MISSÃO DA ALMA)**

Estruture em três blocos:

**PASSADO/KARMA:** Analise o Nodo Sul em ${southNode} como zona de conforto e padrões trazidos. Como isso se conecta com Saturno em ${saturnSign}?

**PRESENTE/ESSÊNCIA:** Como a combinação Sol em ${userData.sunSign}, Lua em ${userData.moonSign} e Ascendente em ${userData.ascendant} cria tensões ou harmonias com o eixo nodal? Onde está a ferida (Quíron em ${chironSign})?

**FUTURO/EVOLUÇÃO:** O que o Nodo Norte em ${northNode} pede como desafio evolutivo? Como transformar a ferida de Quíron em dom de cura?

**EXEMPLO DE PROFUNDIDADE:**
"Seu Nodo Sul em Libra indica que você se definiu através dos outros. Seu desafio kármico (Nodo Norte em Áries) é aprender a bancar suas vontades sozinho. Quíron em Gêmeos sugere uma ferida na comunicação - talvez você tenha sido silenciado. Mas essa mesma ferida te torna um comunicador extraordinário quando curada. Saturno em Capricórnio avisa: o reconhecimento virá tarde, mas sólido."

Escreva a análise completa para ${userData.name}, com 2-3 parágrafos por seção.
`;

        const promptEn = `
**SYSTEM CONTEXT:**
You are COSMOS ASTRAL, an advanced astrological engine. Your function is to generate a coherent synthesis, not a list of definitions.

**HIERARCHY AND WEIGHT GUIDELINES:**
- Level 1 (Maximum Weight): Sun, Moon and Ascendant Ruler
- Level 2 (High Weight): Personal Planets (Mercury, Venus, Mars)
- Level 3 (Medium Weight): Lunar Nodes, Saturn, Jupiter
- Level 4 (Refined Weight): Chiron, Lilith, Transpersonal Planets

**SPECIFIC INTERPRETATION DEFINITIONS:**
• LUNAR NODES: Interpret as soul journey - South Node (past/comfort zone) → North Node (future/evolutionary challenge)
• CHIRON: The "wound that becomes gift". Where the person feels inadequacy, but becomes a master at helping others
• SATURN: The karmic master demanding maturity, where rewards come late but solid
• Never generate contradictions without explaining them as "internal tensions of maturation"

**NATIVE'S DATA:**
- Name: ${userData.name}
- Sun in ${userData.sunSign} (Level 1 - Essence, Conscious Ego)
- Moon in ${userData.moonSign} (Level 1 - Unconscious, Emotions)
- Ascendant in ${userData.ascendant} (Level 1 - Projected Identity)
- North Node in ${northNode} ${northNodeDegree}° (Level 3 - Life Mission)
- South Node in ${southNode} ${southNodeDegree}° (Level 3 - Past Lives Baggage)
- Saturn in ${saturnSign} ${saturnDegree}° (Level 3 - Karmic Master, Structure)
- Chiron in ${chironSign} ${chironDegree}° (Level 4 - The Wounded Healer)

**SECTION: KARMA, CHALLENGES AND EVOLUTION (THE SOUL'S MISSION)**

Structure in three blocks:

**PAST/KARMA:** Analyze the South Node in ${southNode} as comfort zone and brought patterns. How does this connect with Saturn in ${saturnSign}?

**PRESENT/ESSENCE:** How does the combination Sun in ${userData.sunSign}, Moon in ${userData.moonSign} and Ascendant in ${userData.ascendant} create tensions or harmonies with the nodal axis? Where is the wound (Chiron in ${chironSign})?

**FUTURE/EVOLUTION:** What does the North Node in ${northNode} ask as evolutionary challenge? How to transform Chiron's wound into healing gift?

**DEPTH EXAMPLE:**
"Your South Node in Libra indicates you defined yourself through others. Your karmic challenge (North Node in Aries) is learning to stand by your wishes alone. Chiron in Gemini suggests a wound in communication - perhaps you were silenced. But this same wound makes you an extraordinary communicator when healed. Saturn in Capricorn warns: recognition will come late, but solid."

Write the complete analysis for ${userData.name}, with 2-3 paragraphs per section.
`;

        const result = await apiService.getInterpretation({
          custom_query: language === 'pt' ? promptPt : promptEn,
          use_groq: true,
        });
        setInterpretation(result.interpretation);
      } catch (error) {
        console.error('Erro ao buscar interpretação:', error);
        setInterpretation(
          language === 'pt'
            ? `Com o Nodo Norte em ${northNode}, seu propósito de vida está ligado ao desenvolvimento das qualidades desse signo. O Nodo Sul em ${southNode} indica padrões que você traz de experiências passadas. Saturno em ${saturnSign} mostra onde estão seus maiores desafios e lições de vida.`
            : `With the North Node in ${northNode}, your life purpose is linked to developing the qualities of that sign. The South Node in ${southNode} indicates patterns you bring from past experiences. Saturn in ${saturnSign} shows where your greatest challenges and life lessons are.`
        );
      } finally {
        setIsLoading(false);
      }
    };
    fetchInterpretation();
  }, [language, northNode, southNode, saturnSign, userData]);

  const NorthIcon = zodiacSigns.find(z => z.name === northNode)?.icon;
  const SouthIcon = zodiacSigns.find(z => z.name === southNode)?.icon;
  const SaturnIcon = zodiacSigns.find(z => z.name === saturnSign)?.icon;
  const ChironIcon = zodiacSigns.find(z => z.name === chironSign)?.icon;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif text-3xl font-bold text-foreground">
            {language === 'pt' ? 'Nodos Lunares e Saturno' : 'Lunar Nodes and Saturn'}
          </h2>
          <p className="text-muted-foreground mt-2">
            {language === 'pt' ? 'Seu propósito de vida, karma e lições a aprender' : 'Your life purpose, karma and lessons to learn'}
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

      {/* Nodes, Saturn and Chiron Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* North Node */}
        <div className="bg-gradient-to-br from-amber-500/20 to-amber-500/5 rounded-xl p-6 border border-amber-500/30">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-full bg-amber-500/20 flex items-center justify-center">
              <UIIcons.ArrowUp size={32} className="text-amber-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{language === 'pt' ? 'Nodo Norte' : 'North Node'}</p>
              <div className="flex items-center gap-2">
                {NorthIcon && <NorthIcon size={20} className="text-amber-500" />}
                <p className="font-bold text-xl text-foreground">{northNode}</p>
              </div>
              <p className="text-sm text-muted-foreground">{northNodeDegree}°</p>
            </div>
          </div>
          <p className="text-foreground/80">
            {language === 'pt' 
              ? 'O destino e o propósito que você deve buscar nesta vida' 
              : 'The destiny and purpose you should seek in this life'}
          </p>
        </div>

        {/* South Node */}
        <div className="bg-gradient-to-br from-indigo-500/20 to-indigo-500/5 rounded-xl p-6 border border-indigo-500/30">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-full bg-indigo-500/20 flex items-center justify-center">
              <UIIcons.ArrowDown size={32} className="text-indigo-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{language === 'pt' ? 'Nodo Sul' : 'South Node'}</p>
              <div className="flex items-center gap-2">
                {SouthIcon && <SouthIcon size={20} className="text-indigo-500" />}
                <p className="font-bold text-xl text-foreground">{southNode}</p>
              </div>
              <p className="text-sm text-muted-foreground">{southNodeDegree}°</p>
            </div>
          </div>
          <p className="text-foreground/80">
            {language === 'pt' 
              ? 'Padrões do passado que você traz como zona de conforto' 
              : 'Past patterns you bring as a comfort zone'}
          </p>
        </div>

        {/* Saturn */}
        <div className="bg-gradient-to-br from-gray-500/20 to-gray-500/5 rounded-xl p-6 border border-gray-500/30">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-full bg-gray-500/20 flex items-center justify-center">
              <UIIcons.AlertCircle size={32} className="text-gray-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{language === 'pt' ? 'Saturno' : 'Saturn'}</p>
              <div className="flex items-center gap-2">
                {SaturnIcon && <SaturnIcon size={20} className="text-gray-500" />}
                <p className="font-bold text-xl text-foreground">{saturnSign}</p>
              </div>
              <p className="text-sm text-muted-foreground">{saturnDegree}°</p>
            </div>
          </div>
          <p className="text-foreground/80">
            {language === 'pt' 
              ? 'Onde estão seus maiores desafios e lições de vida' 
              : 'Where your greatest challenges and life lessons are'}
          </p>
        </div>

        {/* Chiron - A ferida do curador */}
        <div className="bg-gradient-to-br from-rose-500/20 to-rose-500/5 rounded-xl p-6 border border-rose-500/30">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-full bg-rose-500/20 flex items-center justify-center">
              <UIIcons.Heart size={32} className="text-rose-500" />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{language === 'pt' ? 'Quíron' : 'Chiron'}</p>
              <div className="flex items-center gap-2">
                {ChironIcon && <ChironIcon size={20} className="text-rose-500" />}
                <p className="font-bold text-xl text-foreground">{chironSign}</p>
              </div>
              <p className="text-sm text-muted-foreground">{chironDegree}°</p>
            </div>
          </div>
          <p className="text-foreground/80">
            {language === 'pt' 
              ? 'A ferida que pode se tornar seu maior dom de cura' 
              : 'The wound that can become your greatest healing gift'}
          </p>
        </div>
      </div>

      {/* Interpretation */}
      <div className="bg-card rounded-xl p-6 border border-border">
        <h3 className="font-serif text-xl font-bold text-foreground mb-6">
          {language === 'pt' ? 'Interpretação do Eixo Nodal' : 'Nodal Axis Interpretation'}
        </h3>
        {isLoading ? (
          <div className="flex items-center gap-3 py-4">
            <UIIcons.Loader className="w-5 h-5 animate-spin text-primary" />
            <p className="text-muted-foreground">
              {language === 'pt' ? 'Gerando interpretação...' : 'Generating interpretation...'}
            </p>
          </div>
        ) : (
          <FormattedInterpretation text={interpretation} language={language} />
        )}
      </div>
    </div>
  );
};

// Componente para formatar a interpretação com ícones e estrutura
const FormattedInterpretation = ({ text, language }: { text: string; language: string }) => {
  // Função para identificar e formatar seções
  const formatText = (rawText: string) => {
    // Detectar seções comuns
    const sections: Array<{ title: string; icon: React.ReactNode; content: string; color: string }> = [];
    
    // Padrões para identificar seções
    const patterns = {
      passado: /\*?\*?(PASSADO|KARMA|Passado|Karma|passado|karma)[\/\s]*(KARMA|karma|Karma)?\*?\*?/gi,
      presente: /\*?\*?(PRESENTE|ESSÊNCIA|Presente|Essência|presente|essência)[\/\s]*(ESSÊNCIA|essência|Essência)?\*?\*?/gi,
      futuro: /\*?\*?(FUTURO|EVOLUÇÃO|Futuro|Evolução|futuro|evolução)[\/\s]*(EVOLUÇÃO|evolução|Evolução)?\*?\*?/gi,
    };

    // Dividir o texto em parágrafos
    const paragraphs = rawText.split(/\n\n+/);
    let currentSection: { title: string; icon: React.ReactNode; content: string[]; color: string } | null = null;
    const result: Array<{ title: string; icon: React.ReactNode; content: string; color: string }> = [];

    for (const paragraph of paragraphs) {
      const trimmed = paragraph.trim();
      if (!trimmed) continue;

      // Verificar se é uma nova seção
      let isNewSection = false;
      
      if (patterns.passado.test(trimmed)) {
        if (currentSection) {
          result.push({ ...currentSection, content: currentSection.content.join('\n\n') });
        }
        currentSection = {
          title: language === 'pt' ? '🌙 Passado / Karma' : '🌙 Past / Karma',
          icon: <UIIcons.Moon className="w-6 h-6 text-indigo-500" />,
          content: [],
          color: 'from-indigo-500/20 to-indigo-500/5 border-indigo-500/30'
        };
        // Remover o título do parágrafo
        const cleaned = trimmed.replace(patterns.passado, '').replace(/^\*+|\*+$/g, '').trim();
        if (cleaned) currentSection.content.push(cleaned);
        isNewSection = true;
      } else if (patterns.presente.test(trimmed)) {
        if (currentSection) {
          result.push({ ...currentSection, content: currentSection.content.join('\n\n') });
        }
        currentSection = {
          title: language === 'pt' ? '☀️ Presente / Essência' : '☀️ Present / Essence',
          icon: <UIIcons.Sun className="w-6 h-6 text-amber-500" />,
          content: [],
          color: 'from-amber-500/20 to-amber-500/5 border-amber-500/30'
        };
        const cleaned = trimmed.replace(patterns.presente, '').replace(/^\*+|\*+$/g, '').trim();
        if (cleaned) currentSection.content.push(cleaned);
        isNewSection = true;
      } else if (patterns.futuro.test(trimmed)) {
        if (currentSection) {
          result.push({ ...currentSection, content: currentSection.content.join('\n\n') });
        }
        currentSection = {
          title: language === 'pt' ? '⭐ Futuro / Evolução' : '⭐ Future / Evolution',
          icon: <UIIcons.Star className="w-6 h-6 text-emerald-500" />,
          content: [],
          color: 'from-emerald-500/20 to-emerald-500/5 border-emerald-500/30'
        };
        const cleaned = trimmed.replace(patterns.futuro, '').replace(/^\*+|\*+$/g, '').trim();
        if (cleaned) currentSection.content.push(cleaned);
        isNewSection = true;
      }

      if (!isNewSection && currentSection) {
        // Limpar asteriscos e formatar
        const cleaned = trimmed.replace(/^\*+|\*+$/g, '').trim();
        if (cleaned) currentSection.content.push(cleaned);
      } else if (!isNewSection && !currentSection) {
        // Se não há seção atual, criar uma seção de resumo
        if (!result.find(r => r.title.includes('Resumo') || r.title.includes('Summary'))) {
          currentSection = {
            title: language === 'pt' ? '📋 Resumo' : '📋 Summary',
            icon: <UIIcons.BookOpen className="w-6 h-6 text-gray-500" />,
            content: [trimmed],
            color: 'from-gray-500/20 to-gray-500/5 border-gray-500/30'
          };
        } else if (currentSection) {
          currentSection.content.push(trimmed);
        }
      }
    }

    // Adicionar última seção
    if (currentSection) {
      result.push({ ...currentSection, content: currentSection.content.join('\n\n') });
    }

    return result;
  };

  const sections = formatText(text);

  // Se não conseguiu dividir em seções, mostrar texto original formatado
  if (sections.length === 0) {
    return (
      <div className="space-y-4 text-foreground/80 leading-relaxed">
        {text.split('\n\n').map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {sections.map((section, index) => (
        <div 
          key={index} 
          className={`bg-gradient-to-br ${section.color} rounded-xl p-5 border`}
        >
          <div className="flex items-center gap-3 mb-4">
            {section.icon}
            <h4 className="font-semibold text-lg text-foreground">{section.title}</h4>
          </div>
          <div className="text-foreground/80 leading-relaxed space-y-3 pl-9">
            {section.content.split('\n\n').map((paragraph, pIndex) => {
              // Destacar termos importantes
              const formatted = paragraph
                .replace(/O Nodo Norte/g, '**O Nodo Norte**')
                .replace(/O Nodo Sul/g, '**O Nodo Sul**')
                .replace(/Saturno/g, '**Saturno**')
                .replace(/Sol em/g, '**Sol** em')
                .replace(/Lua em/g, '**Lua** em')
                .replace(/Ascendente/g, '**Ascendente**');
              
              // Renderizar com negrito
              const parts = formatted.split(/\*\*(.*?)\*\*/g);
              return (
                <p key={pIndex}>
                  {parts.map((part, partIndex) => 
                    partIndex % 2 === 1 ? (
                      <strong key={partIndex} className="text-foreground font-semibold">{part}</strong>
                    ) : (
                      <span key={partIndex}>{part}</span>
                    )
                  )}
                </p>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

// ===== BIORRITMOS =====
interface BiorhythmsSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const BiorhythmsSection = ({ userData, onBack }: BiorhythmsSectionProps) => {
  const { language } = useLanguage();
  
  // Calcular biorritmos baseados na data de nascimento
  const birthDate = userData.birthDate ? new Date(userData.birthDate) : new Date('1990-01-01');
  const today = new Date();
  const daysSinceBirth = Math.floor((today.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24));

  const physical = Math.sin((2 * Math.PI * daysSinceBirth) / 23) * 100;
  const emotional = Math.sin((2 * Math.PI * daysSinceBirth) / 28) * 100;
  const intellectual = Math.sin((2 * Math.PI * daysSinceBirth) / 33) * 100;

  const biorhythms = [
    { 
      name: language === 'pt' ? 'Físico' : 'Physical', 
      value: physical, 
      color: 'rgb(239, 68, 68)', 
      period: 23,
      desc: language === 'pt' ? 'Energia, força, coordenação' : 'Energy, strength, coordination'
    },
    { 
      name: language === 'pt' ? 'Emocional' : 'Emotional', 
      value: emotional, 
      color: 'rgb(59, 130, 246)', 
      period: 28,
      desc: language === 'pt' ? 'Humor, sensibilidade, criatividade' : 'Mood, sensitivity, creativity'
    },
    { 
      name: language === 'pt' ? 'Intelectual' : 'Intellectual', 
      value: intellectual, 
      color: 'rgb(34, 197, 94)', 
      period: 33,
      desc: language === 'pt' ? 'Raciocínio, memória, comunicação' : 'Reasoning, memory, communication'
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif text-3xl font-bold text-foreground">
            {language === 'pt' ? 'Seus Biorritmos' : 'Your Biorhythms'}
          </h2>
          <p className="text-muted-foreground mt-2">
            {language === 'pt' ? 'Ciclos naturais baseados na sua data de nascimento' : 'Natural cycles based on your birth date'}
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

      {/* Biorhythm Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {biorhythms.map((bio) => (
          <div key={bio.name} className="bg-card rounded-xl p-6 border border-border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-foreground">{bio.name}</h3>
              <span 
                className="text-2xl font-bold" 
                style={{ color: bio.color }}
              >
                {Math.round(bio.value)}%
              </span>
            </div>
            
            {/* Progress Bar */}
            <div className="relative h-4 bg-muted rounded-full overflow-hidden mb-4">
              <div 
                className="absolute left-0 top-0 h-full rounded-full transition-all duration-500"
                style={{ 
                  width: `${Math.abs(bio.value)}%`,
                  backgroundColor: bio.color,
                  marginLeft: bio.value < 0 ? `${50 - Math.abs(bio.value) / 2}%` : '50%',
                  transform: bio.value < 0 ? 'translateX(-100%)' : 'none'
                }}
              />
              <div className="absolute left-1/2 top-0 w-0.5 h-full bg-foreground/30" />
            </div>

            <p className="text-sm text-muted-foreground">{bio.desc}</p>
            <p className="text-xs text-muted-foreground mt-2">
              {language === 'pt' ? `Ciclo de ${bio.period} dias` : `${bio.period}-day cycle`}
            </p>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="bg-card rounded-xl p-6 border border-border">
        <h3 className="font-serif text-xl font-bold text-foreground mb-4">
          {language === 'pt' ? 'Resumo do Dia' : 'Daily Summary'}
        </h3>
        <p className="text-foreground/80 leading-relaxed">
          {language === 'pt' 
            ? `Hoje você está no dia ${daysSinceBirth} desde o seu nascimento. ${
                physical > 50 ? 'Sua energia física está alta, ótimo para exercícios e atividades físicas.' :
                physical < -50 ? 'Sua energia física está baixa, priorize o descanso.' :
                'Sua energia física está moderada, mantenha um ritmo equilibrado.'
              } ${
                emotional > 50 ? 'Emocionalmente você está receptivo e criativo.' :
                emotional < -50 ? 'Emocionalmente pode ser um dia mais introspectivo.' :
                'Suas emoções estão estáveis.'
              } ${
                intellectual > 50 ? 'Mentalmente é um ótimo dia para estudos e decisões importantes.' :
                intellectual < -50 ? 'Evite decisões complexas hoje, se possível.' :
                'Seu raciocínio está funcionando normalmente.'
              }`
            : `Today you are on day ${daysSinceBirth} since your birth. ${
                physical > 50 ? 'Your physical energy is high, great for exercise and physical activities.' :
                physical < -50 ? 'Your physical energy is low, prioritize rest.' :
                'Your physical energy is moderate, maintain a balanced pace.'
              } ${
                emotional > 50 ? 'Emotionally you are receptive and creative.' :
                emotional < -50 ? 'Emotionally it may be a more introspective day.' :
                'Your emotions are stable.'
              } ${
                intellectual > 50 ? 'Mentally it is a great day for studies and important decisions.' :
                intellectual < -50 ? 'Avoid complex decisions today if possible.' :
                'Your reasoning is working normally.'
              }`
          }
        </p>
      </div>
    </div>
  );
};

// ===== SINASTRIA =====
interface SynastrySectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const SynastrySection = ({ userData, onBack }: SynastrySectionProps) => {
  const { language } = useLanguage();
  const [partnerSign, setPartnerSign] = useState<string>('');
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const userSunSign = userData.sunSign || 'Áries';

  const fetchCompatibility = async () => {
    if (!partnerSign) return;
    
    try {
      setIsLoading(true);
      const result = await apiService.getInterpretation({
        custom_query: `compatibilidade sinastria ${userSunSign} com ${partnerSign} relacionamento amor`,
        use_groq: true,
      });
      setInterpretation(result.interpretation);
    } catch (error) {
      console.error('Erro ao buscar compatibilidade:', error);
      setInterpretation(
        language === 'pt'
          ? `A combinação entre ${userSunSign} e ${partnerSign} traz dinâmicas únicas para o relacionamento. Cada signo contribui com suas qualidades e desafios, criando uma conexão que pode ser tanto complementar quanto desafiadora.`
          : `The combination between ${userSunSign} and ${partnerSign} brings unique dynamics to the relationship. Each sign contributes its qualities and challenges, creating a connection that can be both complementary and challenging.`
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
            {language === 'pt' ? 'Sinastria' : 'Synastry'}
          </h2>
          <p className="text-muted-foreground mt-2">
            {language === 'pt' ? 'Análise de compatibilidade entre mapas' : 'Compatibility analysis between charts'}
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

      {/* Your Sign */}
      <div className="bg-primary/10 rounded-xl p-6 border border-primary/30">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
            {(() => {
              const SignIcon = zodiacSigns.find(z => z.name === userSunSign)?.icon;
              return SignIcon ? <SignIcon size={32} className="text-primary" /> : null;
            })()}
          </div>
          <div>
            <p className="text-sm text-muted-foreground">{language === 'pt' ? 'Seu Signo Solar' : 'Your Sun Sign'}</p>
            <p className="font-bold text-2xl text-foreground">{userSunSign}</p>
          </div>
        </div>
      </div>

      {/* Partner Sign Selection */}
      <div className="bg-card rounded-xl p-6 border border-border">
        <h3 className="font-serif text-lg font-bold text-foreground mb-4">
          {language === 'pt' ? 'Selecione o signo do parceiro(a)' : 'Select partner\'s sign'}
        </h3>
        <div className="grid grid-cols-4 md:grid-cols-6 gap-3 mb-6">
          {zodiacSigns.map((sign) => {
            const SignIcon = sign.icon;
            const isSelected = partnerSign === sign.name;
            return (
              <button
                key={sign.name}
                onClick={() => setPartnerSign(sign.name)}
                className={`p-3 rounded-xl border transition-all ${
                  isSelected 
                    ? 'bg-primary/20 border-primary' 
                    : 'bg-muted border-border hover:border-primary/50'
                }`}
              >
                <SignIcon size={24} className={isSelected ? 'text-primary mx-auto' : 'text-foreground mx-auto'} />
                <p className="text-xs text-center mt-2 text-foreground">{sign.name}</p>
              </button>
            );
          })}
        </div>
        
        {partnerSign && (
          <button
            onClick={fetchCompatibility}
            disabled={isLoading}
            className="w-full py-3 rounded-lg bg-primary text-white font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <UIIcons.Loader className="w-5 h-5 animate-spin" />
                {language === 'pt' ? 'Analisando...' : 'Analyzing...'}
              </span>
            ) : (
              language === 'pt' ? 'Analisar Compatibilidade' : 'Analyze Compatibility'
            )}
          </button>
        )}
      </div>

      {/* Interpretation */}
      {interpretation && (
        <div className="bg-card rounded-xl p-6 border border-border animate-fadeIn">
          <h3 className="font-serif text-xl font-bold text-foreground mb-4">
            {userSunSign} + {partnerSign}
          </h3>
          <p className="text-foreground/80 leading-relaxed whitespace-pre-line">{interpretation}</p>
        </div>
      )}
    </div>
  );
};


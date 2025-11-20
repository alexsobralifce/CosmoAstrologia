import { useMemo, useState, useEffect } from 'react';
import { AstroCard } from './astro-card';
import { AstroButton } from './astro-button';
import { BirthChartWheel } from './birth-chart-wheel';
import { ElementChart } from './element-chart';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';
import { UIIcons } from './ui-icons';
import { BookOpen, Eye, Activity, Heart, Calendar, Moon, Star, Home, Zap } from 'lucide-react';
import { AspectIcons, aspectData, AspectType } from './aspect-icons';
import { OnboardingData } from './onboarding';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from './ui/accordion';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';
import { Badge } from './ui/badge';
import { ThemeToggle } from './theme-toggle';
import { ChartRulerSection } from './chart-ruler-section';
import { DailyAdviceSection } from './daily-advice-section';
import { FutureTransitsSection } from './future-transits-section';
import { calculateChartBasics, getChartRuler, getMoonSignForDate, getLunarNodesInfo } from '../utils/astrology';
import { Avatar, AvatarFallback } from './ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { EditUserModal } from './edit-user-modal';
import { ThemeCustomizationModal, ThemeConfig, FontSizeConfig, TypographyConfig } from './theme-customization-modal';
import { useTheme } from './theme-provider';
import { apiService } from '../services/api';

interface AdvancedDashboardProps {
  userData: OnboardingData;
  onViewInterpretation: (topic: string) => void;
  onLogout?: () => void;
  onUserUpdate?: (data: OnboardingData) => void;
}

interface PlanetData {
  name: string;
  sign: string;
  house: number;
  degree: number;
  icon: any;
  signIcon: any;
  interpretation: {
    inSign: string;
    inHouse: string;
  };
}

interface HouseData {
  number: number;
  theme: string;
  cuspSign: string;
  planetsInHouse: string[];
  interpretation: string;
  isAngular: boolean;
}

interface AspectData {
  id: string;
  planet1: string;
  planet2: string;
  type: AspectType;
  orb: number;
  interpretation: string;
  tags: string[];
}

type RelationshipInfo = {
  partnerData?: {
    name?: string;
    sunSign?: string;
    moonSign?: string;
  };
  relationshipStatus?: 'single' | 'couple';
};

const BIORHYTHM_CYCLES = {
  physical: 23,
  emotional: 28,
  intellectual: 33,
} as const;

const BIORHYTHM_LABELS: Record<keyof typeof BIORHYTHM_CYCLES, string> = {
  physical: 'Físico',
  emotional: 'Emocional',
  intellectual: 'Intelectual',
};

const calculateBiorhythmLevels = (birthDate?: Date | null) => {
  if (!birthDate) {
    return null;
  }

  const today = new Date();
  const diffDays = Math.floor(
    (today.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24)
  );

  const computeLevel = (cycle: number) => {
    const value = Math.sin((2 * Math.PI * diffDays) / cycle);
    const percentage = Math.round(((value + 1) / 2) * 100);
    return {
      value,
      percentage,
      trend: value >= 0 ? 'ascendente' : 'descendente',
    };
  };

  return {
    physical: computeLevel(BIORHYTHM_CYCLES.physical),
    emotional: computeLevel(BIORHYTHM_CYCLES.emotional),
    intellectual: computeLevel(BIORHYTHM_CYCLES.intellectual),
  };
};

const getBiorhythmAdvice = (
  levels: ReturnType<typeof calculateBiorhythmLevels>,
  phaseName: string
) => {
  if (!levels) {
    return 'Informe sua data de nascimento para gerar os biorritmos personalizados.';
  }

  const positiveCycles = Object.values(levels).filter((level) => level.value >= 0.25).length;
  if (positiveCycles >= 2) {
    return `Momento favorável para agir: ${phaseName} amplifica sua autoconfiança e clareza. Aproveite para iniciar projetos.`;
  }
  if (positiveCycles === 1) {
    return `Semana de movimentos moderados. Honre o ciclo ativo e use o restante para planejamento introspectivo.`;
  }
  return `Energia pedindo pausa estratégica. Use ${phaseName.toLowerCase()} para revisar rotas, recuperar vitalidade e ouvir sua intuição.`;
};

const getLunarPhaseInfo = (date: Date) => {
  const synodicMonth = 29.53058867;
  const referenceNewMoon = new Date(Date.UTC(2000, 0, 6, 18, 14)); // referência conhecida
  const daysSinceReference =
    (date.getTime() - referenceNewMoon.getTime()) / (1000 * 60 * 60 * 24);
  const normalizedDays = ((daysSinceReference % synodicMonth) + synodicMonth) % synodicMonth;
  const phaseIndex = Math.floor((normalizedDays / synodicMonth) * 8);
  const phases = [
    { name: 'Lua Nova', guidance: 'Temporalidade ideal para plantar intenções e ouvir o silêncio interno.' },
    { name: 'Lua Crescente', guidance: 'Hora de ganhar tração e ajustar rotas com flexibilidade.' },
    { name: 'Quarto Crescente', guidance: 'Esforço disciplinado transforma ideias em estrutura concreta.' },
    { name: 'Lua Gibosa Crescente', guidance: 'Refine detalhes, alinhe expectativas e prepare-se para o clímax.' },
    { name: 'Lua Cheia', guidance: 'Luminosidade máxima: celebre, compartilhe e observe revelações.' },
    { name: 'Lua Gibosa Minguante', guidance: 'Solte excessos, reorganize prioridades e ofereça seus aprendizados.' },
    { name: 'Quarto Minguante', guidance: 'Recolha-se um pouco, revise compromissos e foque em conclusões.' },
    { name: 'Lua Minguante', guidance: 'Descanso profundo e limpeza emocional para renovar os ciclos.' },
  ];

  return phases[phaseIndex];
};

const PLANET_CONFIG = [
  { key: 'sun', name: 'Sol', house: 5 },
  { key: 'moon', name: 'Lua', house: 2 },
  { key: 'mercury', name: 'Mercúrio', house: 4 },
  { key: 'venus', name: 'Vênus', house: 3 },
  { key: 'mars', name: 'Marte', house: 1 },
  { key: 'jupiter', name: 'Júpiter', house: 8 },
  { key: 'saturn', name: 'Saturno', house: 10 },
  { key: 'uranus', name: 'Urano', house: 11 },
  { key: 'neptune', name: 'Netuno', house: 12 },
  { key: 'pluto', name: 'Plutão', house: 9 },
];

const SIGN_OPPOSITE: Record<string, string> = {
  Áries: 'Libra',
  Touro: 'Escorpião',
  Gêmeos: 'Sagitário',
  Câncer: 'Capricórnio',
  Leão: 'Aquário',
  Virgem: 'Peixes',
  Libra: 'Áries',
  Escorpião: 'Touro',
  Sagitário: 'Gêmeos',
  Capricórnio: 'Câncer',
  Aquário: 'Leão',
  Peixes: 'Virgem',
};

const SIGN_SQUARES: Record<string, string[]> = {
  Áries: ['Câncer', 'Capricórnio'],
  Touro: ['Leão', 'Aquário'],
  Gêmeos: ['Virgem', 'Peixes'],
  Câncer: ['Áries', 'Libra'],
  Leão: ['Touro', 'Escorpião'],
  Virgem: ['Gêmeos', 'Sagitário'],
  Libra: ['Câncer', 'Capricórnio'],
  Escorpião: ['Leão', 'Aquário'],
  Sagitário: ['Virgem', 'Peixes'],
  Capricórnio: ['Áries', 'Libra'],
  Aquário: ['Touro', 'Escorpião'],
  Peixes: ['Gêmeos', 'Sagitário'],
};

const MONTHLY_FORECASTS_2026 = [
  {
    month: 'Janeiro',
    theme: 'Estruturar antes de acelerar',
    influencers:
      'Sol, Mercúrio, Vênus e Marte juntos em Capricórnio, com Júpiter nutrindo Câncer; Saturno e Netuno fecham etapa em Peixes enquanto Plutão firma raízes em Aquário.',
    business:
      'Planeje o ano com calma, revise contratos e crie metas semanais para não carregar mais do que cabe. Há sorte em negócios ligados a casa, alimentação e serviços contínuos; evite prazos irreais só para agradar.',
    love:
      'Vênus e Marte em Capricórnio pedem cuidados práticos: ajudar na rotina vale mais do que discursos. Combine sonhos de longo prazo e não pressione quem precisa de tempo para se comprometer.',
  },
  {
    month: 'Fevereiro',
    theme: 'Ideias novas com delicadeza',
    influencers:
      'Sol e Marte seguem em Aquário, enquanto Vênus e Mercúrio amolecem o clima em Peixes; Saturno e Netuno começam vida nova em Áries.',
    business:
      'Saturno em Áries inaugura ciclo de coragem, mas entregue protótipos simples antes de grandes lançamentos. Use grupos e comunidades aquarianas para testes e mantenha contratos bem explicados para não gerar confusão.',
    love:
      'Clima romântico em Peixes convida conversas empáticas e arte. Ainda assim, combine limites para não prometer presença quando a agenda estiver cheia de novos projetos.',
  },
  {
    month: 'Março',
    theme: 'Do sonho para a ação',
    influencers:
      'Sol ainda atravessa Peixes e logo ativa Áries; Vênus estreia em Áries, Marte permanece em Peixes, Júpiter segue em Câncer e Saturno consolida passo firme em Áries.',
    business:
      'Use a primeira quinzena para revisar processos e, após o equinócio, lance ações rápidas. Cuidado com decisões tomadas apenas pela empolgação ariana; confirme dados com a equipe financeira.',
    love:
      'Vênus em Áries acende paixões, mas Marte pisciano lembra de respeitar o tempo emocional do outro. Gestos simples e sinceros valem mais do que disputas.',
  },
  {
    month: 'Abril',
    theme: 'Coragem com pés no chão',
    influencers:
      'Sol, Mercúrio e Marte em Áries estimulam iniciativa; Vênus floresce em Touro, Júpiter ainda protege Câncer e Urano se prepara para mudar de signo.',
    business:
      'Ótimo mês para lançar produtos piloto e renegociar preços com clareza. Atenção para não esgotar o time: distribua tarefas e mantenha check-ins curtos para evitar conflitos impulsivos.',
    love:
      'Vênus em Touro pede presença sensorial e rotinas gostosas. Marte em Áries acelera tudo, então alinhe desejos antes de tomar decisões sérias.',
  },
  {
    month: 'Maio',
    theme: 'Construir e experimentar',
    influencers:
      'Sol e Mercúrio permanecem em Touro, Vênus circula por Gêmeos e Urano enfim entra em Gêmeos; Marte finaliza Áries e toca Touro enquanto Júpiter conclui o passeio por Câncer.',
    business:
      'Sorte em produtos consistentes, mas abra espaço para formatos digitais rápidos sugeridos por Urano em Gêmeos. Revise estoques e logística antes de ampliar ofertas.',
    love:
      'Vênus geminiana deixa conversas leves e flertes inteligentes. Só cuide para não prometer presença em todos os encontros; priorize qualidade.',
  },
  {
    month: 'Junho',
    theme: 'Trocas inteligentes',
    influencers:
      'Sol em Gêmeos, Vênus chega a Leão, Marte se estabiliza em Touro, Mercúrio ativa Câncer e Júpiter encerra lições cancerianas.',
    business:
      'Conclua acordos iniciados no semestre e formalize documentos antes de Júpiter mudar de signo. Há sorte em networking e campanhas que eduquem o público; não deixe detalhes jurídicos para depois.',
    love:
      'Vênus em Leão pede alegria compartilhada e elogios sinceros. Marte taurino lembra de manter gestos constantes; evite ciúmes nas redes sociais.',
  },
  {
    month: 'Julho',
    theme: 'Mostrar o brilho com cuidado',
    influencers:
      'Sol e Mercúrio em Câncer dão o tom emocional, Vênus analisa em Virgem, Marte espalha ideias em Gêmeos e Júpiter inaugura permanência em Leão.',
    business:
      'Hora de contar histórias que tocam o público. Júpiter em Leão dá palco a quem assume autoralidade, mas não confunda visibilidade com gasto extra; segmente campanhas.',
    love:
      'Vênus virginiana valoriza pequenos serviços: cozinhar, organizar, ouvir. Marte em Gêmeos inspira diálogos picantes, desde que não haja ironias com quem está sensível.',
  },
  {
    month: 'Agosto',
    theme: 'Liderar com equilíbrio',
    influencers:
      'Sol e Mercúrio em Leão seguem vibrantes, Vênus em Libra busca harmonia, Marte em Câncer mexe nas emoções e Júpiter fortalece a confiança leonina.',
    business:
      'Assuma liderança com clareza e aceite parcerias estratégicas. Evite decisões movidas por orgulho; peça feedback antes de anunciar mudanças.',
    love:
      'Vênus em Libra pede cooperação e acordos justos. Marte em Câncer pode reabrir memórias, então fale sobre inseguranças antes que virem drama.',
  },
  {
    month: 'Setembro',
    theme: 'Ajustes e profundidade',
    influencers:
      'Sol atravessa Virgem, Vênus mergulha em Escorpião, Mercúrio negocia em Libra, Marte ainda percorre Câncer e Júpiter segue firme em Leão.',
    business:
      'Faça auditorias simples, ajuste preços e corte desperdícios. Há sorte em mentorias e cursos curtos; cuidado para não controlar demais o time.',
    love:
      'Vênus em Escorpião deseja intimidade verdadeira. Abra espaço para conversas profundas e defina limites saudáveis para ciúmes.',
  },
  {
    month: 'Outubro',
    theme: 'Diplomacia com ousadia',
    influencers:
      'Sol em Libra, Vênus e Mercúrio em Escorpião, Marte aquece Leão e Júpiter amplia o palco criativo.',
    business:
      'Mês excelente para negociações, parcerias e eventos. Marte leonino pede coragem para vender ideias, mas cheque números antes de prometer entrega rápida.',
    love:
      'Paixão intensa e sincera, ótima para reacender a faísca, desde que haja honestidade sobre necessidades individuais.',
  },
  {
    month: 'Novembro',
    theme: 'Transformar sem perder leveza',
    influencers:
      'Sol e Mercúrio permanecem em Escorpião, Vênus retorna a Libra, Marte segue em Leão e Júpiter se aproxima do fim do signo.',
    business:
      'Feche o ano eliminando processos pesados. Parcerias equilibradas rendem sorte, mas evite gastos impulsivos movidos por ego.',
    love:
      'Combinação de profundidade escorpiana com charme libriano facilita reconciliações. Cuidado para não dramatizar tudo que não recebe atenção imediata.',
  },
  {
    month: 'Dezembro',
    theme: 'Planejar 2027 com fé',
    influencers:
      'Sol e Mercúrio em Sagitário, Vênus continua em Escorpião, Marte organiza em Virgem, Júpiter estabiliza Leão enquanto Saturno em Áries, Urano em Gêmeos e Netuno em Áries pedem visão inovadora.',
    business:
      'Revise metas, defina investimentos criativos e alinhe expansão com disciplina saturnina. Sorte em projetos educacionais ou viagens de trabalho; atenção aos contratos digitais.',
    love:
      'Clima aventureiro favorece viagens a dois ou experiências diferentes. Marte em Virgem aconselha cuidar da saúde do relacionamento com conversas práticas e planos claros.',
  },
] as const;

const JUPITER_HOUSE_KEYWORDS: Record<
  number,
  { title: string; description: string }
> = {
  1: { title: 'identidade e coragem', description: 'Hora de se mostrar mais, atualizar estilo e tomar decisões que reflitam sua essência.' },
  2: { title: 'finanças e autoestima', description: 'Crescimento ao cuidar do dinheiro com consciência e cobrar pelo seu valor.' },
  3: { title: 'comunicação e estudos', description: 'Cursos rápidos e networking destravam oportunidades.' },
  4: { title: 'família e raízes', description: 'Aproveite para reorganizar a casa e curar histórias antigas.' },
  5: { title: 'criatividade e romance', description: 'Expresse talentos e lembre-se de brincar mais.' },
  6: { title: 'rotina e saúde', description: 'Pequenos hábitos sustentam grandes metas em 2026.' },
  7: { title: 'parcerias e contratos', description: 'Negociações honestas ampliam impacto conjunto.' },
  8: { title: 'transformação e investimentos', description: 'Mergulhe em terapias e revise acordos financeiros.' },
  9: { title: 'expansão mental e viagens', description: 'Planeje intercâmbios, cursos ou publicações.' },
 10: { title: 'carreira e reputação', description: 'Visibilidade cresce; alinhe ambição com propósito.' },
 11: { title: 'redes e projetos coletivos', description: 'Comunidades certas abrem portas inesperadas.' },
 12: { title: 'cura e bastidores', description: 'Reserve tempo para silêncio, espiritualidade e conclusão de ciclos.' },
};

const JUPITER_MANTRAS: Record<number, string> = {
  1: 'Eu lidero minha história com coragem tranquila.',
  2: 'Eu valorizo meus dons e crio segurança passo a passo.',
  3: 'Minha voz é clara e abre estradas em 2026.',
  4: 'Eu nutro minhas raízes para crescer com estabilidade.',
  5: 'Crio, amo e celebro a vida com leveza.',
  6: 'Pequenas rotinas conscientes sustentam meus sonhos.',
  7: 'Parcerias equilibradas multiplicam resultados.',
  8: 'Transformo medos em poder compartilhado.',
  9: 'Estudo, viajo e expando horizontes sem pressa.',
 10: 'Minha carreira reflete quem sou de verdade.',
 11: 'Juntos vamos mais longe, com propósito.',
 12: 'Silêncio e fé são meu combustível em 2026.',
};

const SLOW_PLANET_KEYS: Record<string, string> = {
  Plutão: 'pluto_sign',
  Urano: 'uranus_sign',
  Netuno: 'neptune_sign',
};

const ASPECT_LABELS: Record<string, string> = {
  conjunction: 'Conjunção (encontro direto)',
  opposition: 'Oposição (180°)',
  square: 'Quadratura (90°)',
};

const ASPECT_TIPS: Record<string, string> = {
  conjunction: 'Canalize a intensidade em mudanças conscientes; não deixe o passado ditar seu ritmo.',
  opposition: 'Equilíbrio é a palavra-chave. Escute o outro lado antes de reagir.',
  square: 'Use o atrito como combustível para disciplina e novos hábitos.',
};

const DEFAULT_THEME: ThemeConfig = {
  light: {
    primary: '#FDFBF7',
    secondary: '#6B7280',
    accent: '#D4A024',
    neutral: '#F0E6D2',
  },
  dark: {
    primary: '#0A0E2F',
    secondary: '#A0AEC0',
    accent: '#E8B95A',
    neutral: '#1A1F4A',
  },
};

const getTenseAspect = (slowSign?: string, targetSign?: string) => {
  if (!slowSign || !targetSign) return null;
  if (slowSign === targetSign) return 'conjunction';
  if (SIGN_OPPOSITE[targetSign] === slowSign) return 'opposition';
  if (SIGN_SQUARES[targetSign]?.includes(slowSign)) return 'square';
  return null;
};

const buildAspectInsight = (
  planetName: string,
  planetSign: string,
  targetLabel: string,
  targetSign: string,
  aspectType: string
) => {
  const label = ASPECT_LABELS[aspectType] || 'Aspecto';
  const tip = ASPECT_TIPS[aspectType] || 'Observe os sinais do corpo e ajuste o ritmo.';
  return {
    title: `${label} com seu ${targetLabel}`,
    text: `${planetName} em ${planetSign} ativa seu ${targetLabel} em ${targetSign}. ${tip}`,
  };
};

export const AdvancedDashboard = ({
  userData,
  onViewInterpretation,
  onLogout,
  onUserUpdate,
}: AdvancedDashboardProps) => {
  const [selectedHouse, setSelectedHouse] = useState<HouseData | null>(null);
  const [aspectFilter, setAspectFilter] = useState<'all' | 'harmonic' | 'dynamic' | 'neutral'>('all');
  const [activeTab, setActiveTab] = useState<string>('guide');
  const [showEditModal, setShowEditModal] = useState(false);
  const [showThemeModal, setShowThemeModal] = useState(false);
  const [currentUserData, setCurrentUserData] = useState<OnboardingData>(userData);
  const [showElementsModal, setShowElementsModal] = useState(false);
  const [elementsInterpretation, setElementsInterpretation] = useState<string>('');
  const [loadingElementsInterpretation, setLoadingElementsInterpretation] = useState(false);
  const [aspectDetailedInterpretations, setAspectDetailedInterpretations] = useState<Record<string, string>>({});
  const [loadingAspectInterpretations, setLoadingAspectInterpretations] = useState<Record<string, boolean>>({});
  const [showDetailedAspects, setShowDetailedAspects] = useState<Record<string, boolean>>({});
  const [customTheme, setCustomTheme] = useState<ThemeConfig>(() => {
    // Carregar tema do localStorage se existir
    try {
      const saved = localStorage.getItem('astro-custom-theme');
      if (saved) {
        const parsed = JSON.parse(saved) as ThemeConfig;
        // Validar estrutura
        if (parsed.light && parsed.dark) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Erro ao carregar tema do localStorage:', e);
    }
    return DEFAULT_THEME;
  });
  const [fontSize, setFontSize] = useState<FontSizeConfig>(() => {
    // Carregar tamanho de fonte do localStorage se existir
    try {
      const saved = localStorage.getItem('astro-font-size');
      if (saved) {
        const parsed = JSON.parse(saved) as FontSizeConfig;
        if (parsed.base && parsed.base >= 12 && parsed.base <= 24) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Erro ao carregar tamanho de fonte do localStorage:', e);
    }
    return { base: 16 };
  });
  const [typography, setTypography] = useState<TypographyConfig | null>(() => {
    // Carregar tipografia do localStorage se existir
    try {
      const saved = localStorage.getItem('astro-typography');
      if (saved) {
        return JSON.parse(saved) as TypographyConfig;
      }
    } catch (e) {
      console.warn('Erro ao carregar tipografia do localStorage:', e);
    }
    return null;
  });
  const { theme: currentTheme } = useTheme();
  const ensureHex = (value: string) => (value.startsWith('#') ? value : `#${value}`);
  const pickForeground = (color: string) => {
    const hex = ensureHex(color).replace('#', '');
    if (hex.length !== 6) return '#0a0e2f';
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
    return luminance > 0.6 ? '#0a0e2f' : '#fdfbf7';
  };
  useEffect(() => {
    if (!customTheme) {
      return;
    }
    const root = document.documentElement;
    // Usar as cores do tema atual (light ou dark)
    const themeColors = customTheme[currentTheme];
    const { primary, secondary, accent, neutral } = themeColors;
    const primaryFg = pickForeground(primary);
    const secondaryFg = pickForeground(secondary);
    const accentFg = pickForeground(accent);
    const neutralFg = pickForeground(neutral);

    root.style.setProperty('--custom-primary', primary);
    root.style.setProperty('--custom-secondary', secondary);
    root.style.setProperty('--custom-accent', accent);
    root.style.setProperty('--custom-neutral', neutral);

    root.style.setProperty('--background', neutral);
    root.style.setProperty('--foreground', neutralFg);
    root.style.setProperty('--card', primary);
    root.style.setProperty('--card-foreground', primaryFg);
    root.style.setProperty('--primary', primary);
    root.style.setProperty('--primary-foreground', primaryFg);
    root.style.setProperty('--secondary', secondary);
    root.style.setProperty('--secondary-foreground', secondaryFg);
    root.style.setProperty('--accent', accent);
    root.style.setProperty('--accent-foreground', accentFg);
    root.style.setProperty('--border', accent);
    root.style.setProperty('--muted', secondary);
    root.style.setProperty('--muted-foreground', secondaryFg);
  }, [customTheme, currentTheme]);

  // Aplicar tamanho de fonte globalmente
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--font-size', `${fontSize.base}px`);
  }, [fontSize]);

  // Aplicar configurações de tipografia globalmente
  useEffect(() => {
    if (!typography) return;
    
    const root = document.documentElement;
    root.style.setProperty('--font-family', typography.fontFamily);
    root.style.setProperty('--font-weight-base', typography.fontWeight === 'normal' ? '400' : typography.fontWeight === 'medium' ? '500' : typography.fontWeight === 'semibold' ? '600' : '700');
    root.style.setProperty('--font-style', typography.fontStyle);
    root.style.setProperty('--letter-spacing', typography.letterSpacing === 'tight' ? '-0.025em' : typography.letterSpacing === 'normal' ? '0' : '0.05em');
    root.style.setProperty('--line-height', typography.lineHeight === 'tight' ? '1.25' : typography.lineHeight === 'normal' ? '1.5' : '1.75');
    root.style.setProperty('--text-color-primary', typography.textColor.primary);
    root.style.setProperty('--text-color-secondary', typography.textColor.secondary);
    root.style.setProperty('--text-color-accent', typography.textColor.accent);
  }, [typography]);

  // Carregar interpretação de elementos quando o dialog for aberto
  useEffect(() => {
    if (showElementsModal && !elementsInterpretation && !loadingElementsInterpretation) {
      loadElementsInterpretation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showElementsModal]);

  const [isApplyingTheme, setIsApplyingTheme] = useState(false);
  const [backendChartData, setBackendChartData] = useState<any>(null);
  const relationshipInfo = currentUserData as OnboardingData & RelationshipInfo;
  const partnerData = relationshipInfo.partnerData;
  const relationshipStatus = relationshipInfo.relationshipStatus || (partnerData ? 'couple' : 'single');

  // Buscar dados do backend quando o componente monta ou userData muda
  useEffect(() => {
    const fetchBackendData = async () => {
      try {
        const birthChart = await apiService.getUserBirthChart();
        if (birthChart) {
          console.log('[DEBUG Dashboard] Dados do backend recebidos:', {
            sun_sign: birthChart.sun_sign,
            moon_sign: birthChart.moon_sign,
            ascendant_sign: birthChart.ascendant_sign,
            uranus_sign: birthChart.uranus_sign,
          });
          setBackendChartData(birthChart);
        }
      } catch (error) {
        console.error('[DEBUG Dashboard] Erro ao buscar dados do backend:', error);
      }
    };
    
    fetchBackendData();
  }, [userData]);

  // Sincronizar currentUserData quando userData mudar (ex: após atualização)
  useEffect(() => {
    console.log('[DEBUG Dashboard] userData mudou, atualizando currentUserData:', {
      name: userData.name,
      birthDate: userData.birthDate,
      birthTime: userData.birthTime,
      birthPlace: userData.birthPlace,
      coordinates: userData.coordinates,
    });
    // Criar novo objeto para garantir que React detecte a mudança
    const newUserData = {
      ...userData,
      birthDate: new Date(userData.birthDate), // Nova instância de Date
      coordinates: userData.coordinates ? {
        ...userData.coordinates
      } : undefined,
    };
    console.log('[DEBUG Dashboard] Atualizando currentUserData com novos dados');
    setCurrentUserData(newUserData);
  }, [
    userData.name,
    userData.birthTime,
    userData.birthPlace,
    userData.birthDate?.getTime(),
    userData.coordinates?.latitude,
    userData.coordinates?.longitude,
  ]);

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleLogout = () => {
    apiService.logout();
    if (onLogout) {
      onLogout();
    } else {
      window.location.href = '/';
    }
  };

  const handleUserUpdate = (data: OnboardingData) => {
    console.log('[DEBUG Dashboard] handleUserUpdate chamado com:', {
      name: data.name,
      birthDate: data.birthDate,
      birthTime: data.birthTime,
      coordinates: data.coordinates,
    });
    // Criar novo objeto para garantir que React detecte a mudança
    const newData = {
      ...data,
      birthDate: new Date(data.birthDate),
      coordinates: data.coordinates ? { ...data.coordinates } : undefined,
    };
    setCurrentUserData(newData);
    if (onUserUpdate) {
      console.log('[DEBUG Dashboard] Chamando onUserUpdate do App');
      onUserUpdate(newData);
    }
  };

  const chartBasics = useMemo(() => {
    console.log('[DEBUG Dashboard] Recalculando chartBasics com currentUserData:', {
      name: currentUserData.name,
      birthDate: currentUserData.birthDate,
      birthTime: currentUserData.birthTime,
      coordinates: currentUserData.coordinates,
    });
    const result = calculateChartBasics(currentUserData);
    if (!result.planets) {
      result.planets = [];
    }

    if (backendChartData) {
      const derivedPlanets =
        PLANET_CONFIG.map((planet) => {
          const sign = backendChartData?.[`${planet.key}_sign`];
          const degree = backendChartData?.[`${planet.key}_degree`];
          if (!sign) {
            return null;
          }
          return {
            name: planet.name,
            sign,
            degree: typeof degree === 'number' ? degree : Number(degree) || 0,
            house: planet.house,
          };
        }).filter(Boolean) ?? [];

      if (derivedPlanets.length > 0) {
        result.planets = derivedPlanets;
      }
    }

    console.log('[DEBUG Dashboard] Resultado do cálculo:', result);
    return result;
  }, [currentUserData, backendChartData]);
  const resolveIcon = (signName?: string) => {
    if (!signName) return zodiacSigns[0].icon;
    return zodiacSigns.find((sign) => sign.name === signName)?.icon ?? zodiacSigns[0].icon;
  };

  const bigThree = {
    sun: {
      sign: chartBasics.sun?.sign ?? 'Indefinido',
      degree: chartBasics.sun?.degree ?? 0,
      icon: resolveIcon(chartBasics.sun?.sign),
    },
    moon: {
      sign: chartBasics.moon?.sign ?? 'Indefinido',
      degree: chartBasics.moon?.degree ?? 0,
      icon: resolveIcon(chartBasics.moon?.sign),
    },
    ascendant: {
      sign: chartBasics.ascendant?.sign ?? 'Indisponível',
      degree: chartBasics.ascendant?.degree ?? 0,
      icon: resolveIcon(chartBasics.ascendant?.sign),
    },
  };

  // Calcular regente do mapa baseado no ascendente
  const chartRuler = useMemo(() => {
    // Usar dados do backend se disponíveis, senão usar dados calculados localmente
    const ascendantSign = backendChartData?.ascendant_sign || chartBasics.ascendant?.sign;
    if (!ascendantSign) {
      return null;
    }

    const ruler = getChartRuler(ascendantSign);
    
    // Mapear regente para o signo correspondente
    // Priorizar dados do backend (mais precisos), senão usar dados calculados localmente
    let rulerSign = 'Desconhecido';
    
    const rulerToSignMap: Record<string, string> = {
      'Sol': backendChartData?.sun_sign || chartBasics.sun?.sign || 'Desconhecido',
      'Lua': backendChartData?.moon_sign || chartBasics.moon?.sign || 'Desconhecido',
      'Mercúrio': backendChartData?.mercury_sign || chartBasics.mercury?.sign || chartBasics.moon?.sign || 'Desconhecido',
      'Vênus': backendChartData?.venus_sign || chartBasics.venus?.sign || chartBasics.sun?.sign || 'Desconhecido',
      'Marte': backendChartData?.mars_sign || chartBasics.mars?.sign || chartBasics.sun?.sign || 'Desconhecido',
      'Júpiter': backendChartData?.jupiter_sign || chartBasics.jupiter?.sign || chartBasics.sun?.sign || 'Desconhecido',
      'Saturno': backendChartData?.saturn_sign || chartBasics.saturn?.sign || chartBasics.sun?.sign || 'Desconhecido',
      'Urano': backendChartData?.uranus_sign || chartBasics.uranus?.sign || chartBasics.sun?.sign || 'Desconhecido',
      'Netuno': backendChartData?.neptune_sign || chartBasics.neptune?.sign || chartBasics.moon?.sign || 'Desconhecido',
      'Plutão': backendChartData?.pluto_sign || chartBasics.pluto?.sign || chartBasics.sun?.sign || 'Desconhecido',
    };
    
    rulerSign = rulerToSignMap[ruler] || 'Desconhecido';
    
    console.log('[DEBUG Dashboard] Calculando regente:', {
      ascendantSign,
      ruler,
      rulerSign,
      backendData: !!backendChartData,
    });
    
    // Casa aproximada (em uma implementação completa, calcularíamos as casas)
    // Por enquanto, vamos usar uma aproximação baseada no signo
    const rulerHouse = 3; // Aproximação - em implementação completa, calcularíamos as casas
    
    return {
      ascendant: ascendantSign,
      ruler,
      rulerSign,
      rulerHouse,
    };
  }, [chartBasics, backendChartData]);

  const midheavenInfo = useMemo(() => {
    if (!backendChartData?.midheaven_sign) {
      return null;
    }

    const mcSign = backendChartData.midheaven_sign;
    const mcDegree = backendChartData.midheaven_degree ?? 0;
    const icon = resolveIcon(mcSign);
    const planetsOnMC = backendChartData.planets_conjunct_midheaven || [];
    const uranusOnMC =
      backendChartData.uranus_on_midheaven ||
      planetsOnMC.includes('Urano');

    return {
      sign: mcSign,
      degree: mcDegree,
      icon,
      planets: planetsOnMC,
      uranusOnMC,
    };
  }, [backendChartData]);

  const lunarPhaseInfo = useMemo(() => getLunarPhaseInfo(new Date()), []);

  const moonTransitSign = useMemo(() => {
    const currentMoon = getMoonSignForDate(new Date());
    return currentMoon?.sign || 'Atualizando';
  }, []);

  const biorhythmLevels = useMemo(
    () => calculateBiorhythmLevels(currentUserData.birthDate || null),
    [currentUserData.birthDate?.getTime()]
  );

  const biorhythmAdvice = useMemo(
    () => getBiorhythmAdvice(biorhythmLevels, lunarPhaseInfo.name),
    [biorhythmLevels, lunarPhaseInfo.name]
  );

  const elementsData = [
    { name: 'Fogo', percentage: 40, color: '#E8B95A' },
    { name: 'Terra', percentage: 30, color: '#8B7355' },
    { name: 'Ar', percentage: 20, color: '#A0AEC0' },
    { name: 'Água', percentage: 10, color: '#4A90E2' },
  ];

  const modalitiesData = [
    { name: 'Cardinal', percentage: 25, color: '#E8B95A' },
    { name: 'Fixo', percentage: 50, color: '#8B7355' },
    { name: 'Mutável', percentage: 25, color: '#A0AEC0' },
  ];

  const strengths = [
    {
      title: 'Vênus em Trígono com Júpiter',
      description: 'Carisma natural e sorte nas finanças. Generosidade e otimismo atraem oportunidades.',
    },
    {
      title: 'Lua em Sextil com Mercúrio',
      description: 'Comunicação emocional equilibrada. Facilidade em expressar sentimentos de forma clara.',
    },
  ];

  const challenges = [
    {
      title: 'Sol em Quadratura com Saturno',
      description: 'Necessidade de disciplina e superação de limites. Trabalho árduo traz reconhecimento.',
    },
    {
      title: 'Marte em Oposição com Plutão',
      description: 'Tensão entre ação e poder. Cuidado com confrontos e uso da força de forma construtiva.',
    },
  ];

  // Estado para armazenar interpretações dinâmicas
  const [planetInterpretations, setPlanetInterpretations] = useState<Record<string, { inSign: string; inHouse: string }>>({});
  const [loadingInterpretations, setLoadingInterpretations] = useState<Record<string, boolean>>({});

  // Função para calcular elementos e modalidades do mapa
  const calculateUserElements = () => {
    const elementMap: Record<string, string> = {
      'Áries': 'Fogo',
      'Touro': 'Terra',
      'Gêmeos': 'Ar',
      'Câncer': 'Água',
      'Leão': 'Fogo',
      'Virgem': 'Terra',
      'Libra': 'Ar',
      'Escorpião': 'Água',
      'Sagitário': 'Fogo',
      'Capricórnio': 'Terra',
      'Aquário': 'Ar',
      'Peixes': 'Água',
    };

    const modalityMap: Record<string, string> = {
      'Áries': 'Cardinal',
      'Touro': 'Fixo',
      'Gêmeos': 'Mutável',
      'Câncer': 'Cardinal',
      'Leão': 'Fixo',
      'Virgem': 'Mutável',
      'Libra': 'Cardinal',
      'Escorpião': 'Fixo',
      'Sagitário': 'Mutável',
      'Capricórnio': 'Cardinal',
      'Aquário': 'Fixo',
      'Peixes': 'Mutável',
    };

    const elementCounts: Record<string, number> = { Fogo: 0, Terra: 0, Ar: 0, Água: 0 };
    const modalityCounts: Record<string, number> = { Cardinal: 0, Fixo: 0, Mutável: 0 };

    // Contar elementos e modalidades dos planetas
    if (chartBasics.planets && chartBasics.planets.length > 0) {
      chartBasics.planets.forEach((planet: any) => {
        const sign = planet.sign;
        if (sign && elementMap[sign]) {
          elementCounts[elementMap[sign]]++;
        }
        if (sign && modalityMap[sign]) {
          modalityCounts[modalityMap[sign]]++;
        }
      });
    }

    // Adicionar Sol, Lua e Ascendente
    if (chartBasics.sun?.sign) {
      const element = elementMap[chartBasics.sun.sign];
      const modality = modalityMap[chartBasics.sun.sign];
      if (element) elementCounts[element]++;
      if (modality) modalityCounts[modality]++;
    }
    if (chartBasics.moon?.sign) {
      const element = elementMap[chartBasics.moon.sign];
      const modality = modalityMap[chartBasics.moon.sign];
      if (element) elementCounts[element]++;
      if (modality) modalityCounts[modality]++;
    }
    if (chartBasics.ascendant?.sign) {
      const element = elementMap[chartBasics.ascendant.sign];
      const modality = modalityMap[chartBasics.ascendant.sign];
      if (element) elementCounts[element]++;
      if (modality) modalityCounts[modality]++;
    }

    // Encontrar elemento mais e menos presente
    const totalElements = Object.values(elementCounts).reduce((a, b) => a + b, 0);
    
    if (totalElements === 0) {
      // Fallback: retornar valores padrão
      return {
        elementCounts,
        elementPercentages: [],
        mostElement: 'Fogo',
        leastElement: 'Água',
        mostElementPct: 0,
        leastElementPct: 0,
      };
    }
    
    const elementPercentages = Object.entries(elementCounts).map(([name, count]) => ({
      name,
      count,
      percentage: Math.round((count / totalElements) * 100),
    }));

    const sortedByPercentage = [...elementPercentages].sort((a, b) => b.percentage - a.percentage);
    const mostElement = sortedByPercentage[0] || { name: 'Fogo', percentage: 0 };
    const leastElement = sortedByPercentage[sortedByPercentage.length - 1] || { name: 'Água', percentage: 0 };

    return {
      elementCounts,
      elementPercentages,
      mostElement: mostElement.name,
      leastElement: leastElement.name,
      mostElementPct: mostElement.percentage,
      leastElementPct: leastElement.percentage,
    };
  };

  // Função para buscar interpretação sobre elementos e modalidades
  const loadAspectDetailedInterpretation = async (
    aspectId: string,
    planet1: string,
    planet2: string,
    aspectType: AspectType
  ) => {
    // Se já está carregando ou já tem a interpretação, apenas mostrar
    if (loadingAspectInterpretations[aspectId]) {
      return;
    }

    if (aspectDetailedInterpretations[aspectId]) {
      setShowDetailedAspects(prev => ({ ...prev, [aspectId]: true }));
      return;
    }

    try {
      setLoadingAspectInterpretations(prev => ({ ...prev, [aspectId]: true }));

      // Mapear o tipo de aspecto para o formato esperado pela API
      const aspectTypeMap: Record<AspectType, string> = {
        conjunction: 'conjunction',
        trine: 'trine',
        sextile: 'sextile',
        square: 'square',
        opposition: 'opposition',
      };

      const result = await apiService.getAspectInterpretation({
        planet1,
        planet2,
        aspect: aspectTypeMap[aspectType],
      });

      if (result.interpretation) {
        // Limpar a interpretação removendo referências de fonte
        let cleanInterpretation = result.interpretation;
        cleanInterpretation = cleanInterpretation.replace(/\[Fonte:[^\]]+\]/g, '');
        cleanInterpretation = cleanInterpretation.replace(/--- Documento \d+[^-]+---/g, '');
        cleanInterpretation = cleanInterpretation.replace(/Fonte:[^\n]+/g, '');
        cleanInterpretation = cleanInterpretation.replace(/Página \d+/g, '');

        setAspectDetailedInterpretations(prev => ({
          ...prev,
          [aspectId]: cleanInterpretation,
        }));
        setShowDetailedAspects(prev => ({ ...prev, [aspectId]: true }));
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      // Log apenas se não for timeout
      if (!errorMessage.includes('Tempo de espera esgotado')) {
        console.error(`[Aspectos] Erro ao buscar interpretação para ${aspectId}:`, error);
      }
    } finally {
      setLoadingAspectInterpretations(prev => ({ ...prev, [aspectId]: false }));
    }
  };

  const loadElementsInterpretation = async () => {
    if (loadingElementsInterpretation || elementsInterpretation) {
      return;
    }

    try {
      setLoadingElementsInterpretation(true);
      
      // Calcular elementos do usuário
      const userElements = calculateUserElements();
      
      // Construir query mais específica sobre os elementos
      const query = `elemento ${userElements.mostElement} predominante no mapa astral significado características personalidade comportamento influência vida prática elemento ${userElements.leastElement} ausente falta impacto`;
      
      const result = await apiService.getInterpretation({
        custom_query: query,
        use_groq: true,
      });

      console.log('[DEBUG] Resultado da interpretação:', {
        hasInterpretation: !!result.interpretation,
        generatedBy: result.generated_by,
        interpretationLength: result.interpretation?.length,
        interpretationPreview: result.interpretation?.substring(0, 200),
      });

      if (result.interpretation) {
        // Remover informações de fonte se presentes
        let cleanInterpretation = result.interpretation;
        
        console.log('[DEBUG] Interpretação recebida (primeiros 500 chars):', cleanInterpretation.substring(0, 500));
        console.log('[DEBUG] Generated by:', result.generated_by);
        console.log('[DEBUG] Tamanho original:', cleanInterpretation.length);
        
        // Primeiro, remover apenas referências explícitas a fontes, mas preservar o conteúdo
        cleanInterpretation = cleanInterpretation.replace(/\[Fonte:[^\]]+\]/g, '');
        cleanInterpretation = cleanInterpretation.replace(/--- Documento \d+[^-]+---/g, '');
        cleanInterpretation = cleanInterpretation.replace(/Fonte:[^\n]+/g, '');
        cleanInterpretation = cleanInterpretation.replace(/Página \d+/g, '');
        
        // Remover linhas que são apenas cabeçalhos ou referências, mas manter o conteúdo
        const lines = cleanInterpretation.split('\n');
        const filteredLines = lines.filter(line => {
          const trimmed = line.trim();
          // Ignorar apenas linhas completamente vazias
          if (!trimmed) return false;
          // Ignorar linhas que são apenas referências
          if (trimmed.toLowerCase().includes('contexto da consulta:')) return false;
          if (trimmed.toLowerCase().includes('documentos de referência:')) return false;
          // Se a linha é exatamente igual à query, ignorar
          if (trimmed.toLowerCase() === query.toLowerCase()) return false;
          return true;
        });
        
        cleanInterpretation = filteredLines.join('\n').trim();
        
        console.log('[DEBUG] Tamanho após primeira limpeza:', cleanInterpretation.length);
        
        // Se após a limpeza ficou muito curto, usar a versão original com limpeza mínima
        if (cleanInterpretation.length < 100) {
          console.warn('[DEBUG] Interpretação muito curta após limpeza, usando versão com limpeza mínima');
          // Limpeza mínima: apenas remover referências explícitas a fontes
          cleanInterpretation = result.interpretation
            .replace(/\[Fonte:[^\]]+\]/g, '')
            .replace(/Fonte:[^\n]+/g, '')
            .replace(/Página \d+/g, '')
            .trim();
        }
        
        // Verificar se ainda há conteúdo válido
        if (!cleanInterpretation || cleanInterpretation.length < 50) {
          console.error('[DEBUG] Interpretação ainda muito curta após limpeza mínima:', cleanInterpretation.length);
          console.error('[DEBUG] Conteúdo original completo:', result.interpretation);
          setElementsInterpretation('Não foi possível processar a interpretação. Por favor, verifique os logs do backend ou tente novamente.');
          return;
        }
        
        // Verificar se não é apenas a query repetida (validação mais flexível)
        const queryWords = query.toLowerCase().split(/\s+/).filter(w => w.length > 3);
        if (queryWords.length > 0) {
          const interpretationWords = cleanInterpretation.toLowerCase().split(/\s+/);
          const matchingWords = queryWords.filter(qw => interpretationWords.includes(qw));
          
          // Se mais de 90% das palavras da query estão na interpretação E a interpretação é muito curta, pode ser problema
          if (matchingWords.length / queryWords.length > 0.9 && cleanInterpretation.length < 150) {
            console.warn('[DEBUG] Interpretação parece ser apenas a query repetida');
            // Mesmo assim, vamos tentar usar se tiver algum conteúdo
            if (cleanInterpretation.length < 50) {
              setElementsInterpretation('A interpretação gerada parece estar incompleta. Por favor, tente novamente.');
              return;
            }
          }
        }
        
        // Melhorar formatação da interpretação
        // Converter markdown básico para melhor legibilidade
        cleanInterpretation = cleanInterpretation
          .replace(/\*\*(.*?)\*\*/g, '$1') // Remover ** mas manter o texto em negrito
          .replace(/\n{3,}/g, '\n\n') // Reduzir múltiplas quebras de linha
          .trim();
        
        console.log('[DEBUG] Interpretação final (primeiros 200 chars):', cleanInterpretation.substring(0, 200));
        setElementsInterpretation(cleanInterpretation);
      } else {
        setElementsInterpretation('Não foi possível carregar a interpretação no momento. Tente novamente mais tarde.');
      }
    } catch (error: any) {
      console.error('Erro ao buscar interpretação de elementos:', error);
      
      // Verificar se é um erro HTTP
      if (error?.response?.status === 500) {
        console.error('[DEBUG] Erro 500 do servidor:', error?.response?.data);
        setElementsInterpretation('Erro no servidor ao gerar a interpretação. O serviço pode estar temporariamente indisponível. Por favor, tente novamente em alguns instantes.');
      } else if (error?.response?.status === 400) {
        console.error('[DEBUG] Erro 400 - Requisição inválida:', error?.response?.data);
        setElementsInterpretation('Erro na requisição. Por favor, verifique os dados e tente novamente.');
      } else if (error?.message) {
        console.error('[DEBUG] Erro na requisição:', error.message);
        setElementsInterpretation(`Erro ao carregar a interpretação: ${error.message}. Por favor, tente novamente.`);
      } else {
        setElementsInterpretation('Erro ao carregar a interpretação. Por favor, verifique sua conexão e tente novamente.');
      }
    } finally {
      setLoadingElementsInterpretation(false);
    }
  };

  // Função para buscar interpretação de um planeta
  const fetchPlanetInterpretation = async (planetName: string, sign: string, house: number) => {
    const key = `${planetName}-${sign}-${house}`;
    
    // Se já está carregando ou já tem interpretação, não buscar novamente
    if (loadingInterpretations[key] || planetInterpretations[key]) {
      return;
    }

    try {
      setLoadingInterpretations(prev => ({ ...prev, [key]: true }));
      
      // Buscar interpretação do planeta no signo
      const signResponse = await apiService.getPlanetInterpretation({
        planet: planetName,
        sign: sign,
      });
      
      // Buscar interpretação do planeta na casa
      const houseResponse = await apiService.getPlanetHouseInterpretation({
        planet: planetName,
        house: house,
      });
      
      setPlanetInterpretations(prev => ({
        ...prev,
        [key]: {
          inSign: signResponse.interpretation || 'Interpretação não disponível.',
          inHouse: houseResponse.interpretation || 'Interpretação não disponível.',
        },
      }));
    } catch (error) {
      console.error(`Erro ao buscar interpretação de ${planetName}:`, error);
      // Fallback para interpretação padrão
      setPlanetInterpretations(prev => ({
        ...prev,
        [key]: {
          inSign: `Interpretação de ${planetName} em ${sign} não disponível no momento.`,
          inHouse: `Interpretação de ${planetName} na Casa ${house} não disponível no momento.`,
        },
      }));
    } finally {
      setLoadingInterpretations(prev => ({ ...prev, [key]: false }));
    }
  };

  // Buscar interpretações quando chartBasics estiver disponível
  useEffect(() => {
    if (chartBasics && chartBasics.planets) {
      chartBasics.planets.forEach((planet: any) => {
        if (planet.sign && planet.house) {
          fetchPlanetInterpretation(planet.name, planet.sign, planet.house);
        }
      });
    }
  }, [chartBasics]);

  // Construir dados dos planetas com interpretações dinâmicas
  const planetaryData: PlanetData[] = useMemo(() => {
    if (!chartBasics?.planets) {
      return [];
    }

    return chartBasics.planets.map((planet: any) => {
      const planetIcon = planets.find(p => p.name === planet.name)?.icon || planets[0].icon;
      const signIcon = zodiacSigns.find(z => z.name === planet.sign)?.icon || zodiacSigns[0].icon;
      const key = `${planet.name}-${planet.sign}-${planet.house}`;
      const interpretation = planetInterpretations[key] || {
        inSign: loadingInterpretations[key] ? 'Carregando interpretação...' : 'Clique para carregar interpretação',
        inHouse: loadingInterpretations[key] ? 'Carregando interpretação...' : 'Clique para carregar interpretação',
      };

      return {
        name: planet.name,
        sign: planet.sign,
        house: planet.house,
        degree: planet.degree || 0,
        icon: planetIcon,
        signIcon: signIcon,
        interpretation,
      };
    });
  }, [chartBasics, planetInterpretations, loadingInterpretations]);

  const venusProfile = useMemo(
    () => planetaryData.find((planet) => planet.name === 'Vênus'),
    [planetaryData]
  );

  const marsProfile = useMemo(
    () => planetaryData.find((planet) => planet.name === 'Marte'),
    [planetaryData]
  );

  const venusIconComponent = useMemo(
    () => planets.find((planet) => planet.name === 'Vênus')?.icon ?? planets[0].icon,
    []
  );

  const marsIconComponent = useMemo(
    () => planets.find((planet) => planet.name === 'Marte')?.icon ?? planets[0].icon,
    []
  );

  const saturnProfile = useMemo(
    () => planetaryData.find((planet) => planet.name === 'Saturno'),
    [planetaryData]
  );

  const lunarNodes = useMemo(
    () => getLunarNodesInfo(currentUserData.birthDate || null),
    [currentUserData.birthDate?.getTime()]
  );

  const saturnIconComponent = useMemo(
    () => planets.find((planet) => planet.name === 'Saturno')?.icon ?? planets[0].icon,
    []
  );

  const formatNodeDescription = (sign?: string, isNorth = true) => {
    if (!sign) {
      return isNorth
        ? 'Quando soubermos o signo do Nodo Norte, traçaremos a missão de alma desta encarnação.'
        : 'Assim que identificarmos o Nodo Sul, indicaremos as zonas de conforto que precisam de desapego.';
    }
    return isNorth
      ? `Nodo Norte em ${sign} convida você a desenvolver competências ${sign === 'Aquário' ? 'visionárias e genuínas' : 'coerentes com o símbolo'} e a aceitar desafios que ampliem o propósito.`
      : `Nodo Sul em ${sign} aponta talentos herdados, mas também padrões de ${sign.toLowerCase()} que podem aprisionar se repetidos no piloto automático.`;
  };

  const futureGuide = useMemo(() => {
    const jupiterData = planetaryData.find((planet) => planet.name === 'Júpiter');
    const jupiterHouse = jupiterData?.house;
    const jupiterSign = jupiterData?.sign || backendChartData?.jupiter_sign || 'Áries';
    const jupiterFocus = jupiterHouse ? JUPITER_HOUSE_KEYWORDS[jupiterHouse] : undefined;

    const slowPlanets = ['Plutão', 'Urano', 'Netuno'].map((name) => {
      const backendKey = SLOW_PLANET_KEYS[name];
      const backendSign = backendKey ? backendChartData?.[backendKey as keyof typeof backendChartData] : undefined;
      const natalSign = planetaryData.find((planet) => planet.name === name)?.sign;
      return { name, sign: (backendSign as string) || natalSign };
    });

    const targetMarkers = [
      {
        label: 'Sol',
        sign: backendChartData?.sun_sign || bigThree.sun.sign,
      },
      {
        label: 'Ascendente',
        sign: backendChartData?.ascendant_sign || bigThree.ascendant.sign,
      },
    ];

    const challengeInsights =
      slowPlanets.flatMap((planet) => {
        if (!planet.sign) return [];
        return targetMarkers
          .map((target) => {
            if (!target.sign) return null;
            const aspectType = getTenseAspect(planet.sign, target.sign);
            if (!aspectType) return null;
            const insight = buildAspectInsight(planet.name, planet.sign, target.label, target.sign, aspectType);
            return {
              id: `${planet.name}-${target.label}`,
              aspectLabel: ASPECT_LABELS[aspectType],
              text: insight.text,
            };
          })
          .filter(Boolean) as { id: string; aspectLabel?: string; text: string }[];
      }) ?? [];

    const challenges =
      challengeInsights.length > 0
        ? challengeInsights
        : [
            {
              id: 'harmonia',
              aspectLabel: 'Céu colaborativo',
              text: 'Nenhum aspecto tenso forte foi detectado entre planetas lentos, Sol ou Ascendente. Use 2026 para consolidar aprendizados recentes.',
            },
          ];

    const mantra =
      (jupiterHouse && JUPITER_MANTRAS[jupiterHouse]) ||
      'Confie no passo a passo: 2026 será construído com constância e honestidade emocional.';

    return {
      jupiterHouse,
      jupiterSign,
      jupiterSummary: jupiterFocus
        ? `Em 2026, Júpiter ativará sua Casa ${jupiterHouse} (${jupiterFocus.title}). ${jupiterFocus.description}`
        : 'Em 2026, Júpiter segue pedindo expansão consciente. Observe onde você sente vontade de arriscar mais e prepare o terreno ainda em 2025.',
      jupiterFocus,
      challenges,
      mantra,
    };
  }, [planetaryData, backendChartData, bigThree.sun.sign, bigThree.ascendant.sign]);

  const housesData: HouseData[] = [
    {
      number: 1,
      theme: 'Identidade e Aparência',
      cuspSign: 'Gêmeos',
      planetsInHouse: ['Marte'],
      interpretation: 'A Casa 1 representa sua personalidade externa, aparência física e como você se apresenta ao mundo. Com Gêmeos no Ascendente, você é percebido como comunicativo, versátil e intelectualmente curioso. Marte aqui traz energia assertiva e presença marcante.',
      isAngular: true,
    },
    {
      number: 2,
      theme: 'Valores e Recursos',
      cuspSign: 'Câncer',
      planetsInHouse: ['Lua'],
      interpretation: 'A Casa 2 rege suas finanças, posses e valores pessoais. Sua segurança emocional está ligada à segurança material. Você pode ganhar dinheiro através de atividades relacionadas ao cuidado, alimentação ou lar.',
      isAngular: false,
    },
    {
      number: 3,
      theme: 'Comunicação e Aprendizado',
      cuspSign: 'Leão',
      planetsInHouse: ['Vênus'],
      interpretation: 'A Casa 3 rege comunicação, irmãos, vizinhança e aprendizado básico. Você se comunica de forma criativa e dramática. Relações com irmãos e vizinhos tendem a ser harmoniosas.',
      isAngular: false,
    },
    {
      number: 4,
      theme: 'Lar, Raízes e Família',
      cuspSign: 'Virgem',
      planetsInHouse: ['Mercúrio'],
      interpretation: 'A Casa 4 é seu fundamento emocional, lar e família. Você pode trabalhar de casa ou ter uma abordagem prática às questões domésticas. Há forte conexão com suas raízes.',
      isAngular: true,
    },
    {
      number: 5,
      theme: 'Criatividade e Romance',
      cuspSign: 'Libra',
      planetsInHouse: ['Sol'],
      interpretation: 'A Casa 5 rege criatividade, romance, filhos e prazer. Esta é uma área iluminada em sua vida. Você brilha através da autoexpressão criativa e encontra alegria genuína nestas atividades.',
      isAngular: false,
    },
    {
      number: 6,
      theme: 'Rotina e Saúde',
      cuspSign: 'Escorpião',
      planetsInHouse: [],
      interpretation: 'A Casa 6 rege trabalho diário, saúde e rotinas. Você pode ter uma abordagem intensa ao trabalho e pode precisar cuidar de questões de saúde relacionadas ao estresse.',
      isAngular: false,
    },
    {
      number: 7,
      theme: 'Parcerias e Relacionamentos',
      cuspSign: 'Sagitário',
      planetsInHouse: [],
      interpretation: 'A Casa 7 rege casamento, parcerias e contratos. Você busca parceiros aventureiros, filosóficos e que expandam seus horizontes. Relacionamentos são uma jornada de crescimento.',
      isAngular: true,
    },
    {
      number: 8,
      theme: 'Transformação e Recursos Compartilhados',
      cuspSign: 'Capricórnio',
      planetsInHouse: ['Júpiter'],
      interpretation: 'A Casa 8 rege transformação, intimidade e recursos compartilhados. Júpiter aqui pode trazer sorte através de heranças ou recursos de parceiros. Há crescimento através de crises.',
      isAngular: false,
    },
    {
      number: 9,
      theme: 'Filosofia e Viagens',
      cuspSign: 'Aquário',
      planetsInHouse: [],
      interpretation: 'A Casa 9 rege educação superior, filosofia e viagens longas. Você tem uma mente aberta e progressista, interessada em ideias inovadoras e humanitárias.',
      isAngular: false,
    },
    {
      number: 10,
      theme: 'Carreira e Reputação',
      cuspSign: 'Peixes',
      planetsInHouse: ['Saturno'],
      interpretation: 'A Casa 10 rege carreira, reputação e vocação. Saturno aqui indica que você pode trabalhar em áreas relacionadas a serviço, criatividade ou espiritualidade, com disciplina e responsabilidade.',
      isAngular: true,
    },
    {
      number: 11,
      theme: 'Amizades e Grupos',
      cuspSign: 'Áries',
      planetsInHouse: [],
      interpretation: 'A Casa 11 rege amizades, grupos e objetivos futuros. Você é um líder natural em grupos e seus amigos tendem a ser dinâmicos e assertivos.',
      isAngular: false,
    },
    {
      number: 12,
      theme: 'Espiritualidade e Inconsciente',
      cuspSign: 'Touro',
      planetsInHouse: [],
      interpretation: 'A Casa 12 rege o inconsciente, espiritualidade e isolamento. Você encontra paz em ambientes naturais e tranquilos. Pode ter talentos artísticos ou curativos ocultos.',
      isAngular: false,
    },
  ];

  const house5Info = housesData.find((house) => house.number === 5);
  const house7Info = housesData.find((house) => house.number === 7);

  const aspectsData: AspectData[] = [
    {
      id: '1',
      planet1: 'Vênus',
      planet2: 'Júpiter',
      type: 'trine',
      orb: 3,
      interpretation: 'Este trígono entre Vênus e Júpiter é um dos aspectos mais afortunados em astrologia. Traz carisma natural, generosidade e otimismo. Você tem facilidade em atrair oportunidades, especialmente em questões financeiras e românticas. Há uma natureza amável e socialmente agradável que atrai pessoas e situações positivas. Pode ter sorte em investimentos e uma vida amorosa satisfatória.',
      tags: ['Harmonia', 'Finanças', 'Sorte', 'Romance'],
    },
    {
      id: '2',
      planet1: 'Lua',
      planet2: 'Mercúrio',
      type: 'sextile',
      orb: 2,
      interpretation: 'O sextil entre a Lua e Mercúrio facilita a comunicação de emoções. Você consegue expressar seus sentimentos de forma clara e racional. Há uma boa integração entre mente e coração, permitindo decisões equilibradas. Pode ter talento para escrita emocional ou aconselhamento.',
      tags: ['Comunicação', 'Emoções', 'Equilíbrio'],
    },
    {
      id: '3',
      planet1: 'Sol',
      planet2: 'Saturno',
      type: 'square',
      orb: 4,
      interpretation: 'A quadratura entre Sol e Saturno indica uma necessidade de superar obstáculos para brilhar. Pode haver questões de autoestima ou sensação de que precisa trabalhar mais duro que os outros. No entanto, este aspecto também traz disciplina, responsabilidade e a capacidade de alcançar grandes realizações através da persistência. O sucesso vem com o tempo e a maturidade.',
      tags: ['Desafio', 'Disciplina', 'Crescimento', 'Carreira'],
    },
    {
      id: '4',
      planet1: 'Marte',
      planet2: 'Plutão',
      type: 'opposition',
      orb: 5,
      interpretation: 'A oposição entre Marte e Plutão cria uma tensão poderosa entre ação e transformação profunda. Você tem uma energia intensa e magnética, mas precisa aprender a usá-la construtivamente. Pode haver tendência a confrontos de poder. O desafio é canalizar esta força para transformação pessoal e realização, ao invés de conflito.',
      tags: ['Poder', 'Transformação', 'Intensidade', 'Conflito'],
    },
    {
      id: '5',
      planet1: 'Sol',
      planet2: 'Lua',
      type: 'conjunction',
      orb: 1,
      interpretation: 'A conjunção Sol-Lua indica que você nasceu próximo a uma Lua Nova. Isto traz um forte senso de propósito e unidade interna. Sua vontade consciente e suas necessidades emocionais estão alinhadas. Você é autêntico e o que você mostra externamente reflete o que sente internamente.',
      tags: ['Identidade', 'Autenticidade', 'Propósito'],
    },
  ];

  const filteredAspects = aspectsData.filter((aspect) => {
    if (aspectFilter === 'all') return true;
    return aspectData[aspect.type].type === aspectFilter;
  });

  const themeStyles = customTheme
    ? {
        '--custom-primary': customTheme[currentTheme].primary,
        '--custom-secondary': customTheme[currentTheme].secondary,
        '--custom-accent': customTheme[currentTheme].accent,
        '--custom-neutral': customTheme[currentTheme].neutral,
      }
    : undefined;

  const handleThemeSave = (theme: ThemeConfig) => {
    setIsApplyingTheme(true);
    const newTheme: ThemeConfig = {
      light: {
        primary: ensureHex(theme.light.primary),
        secondary: ensureHex(theme.light.secondary),
        accent: ensureHex(theme.light.accent),
        neutral: ensureHex(theme.light.neutral),
      },
      dark: {
        primary: ensureHex(theme.dark.primary),
        secondary: ensureHex(theme.dark.secondary),
        accent: ensureHex(theme.dark.accent),
        neutral: ensureHex(theme.dark.neutral),
      },
    };
    setCustomTheme(newTheme);
    // Salvar no localStorage
    try {
      localStorage.setItem('astro-custom-theme', JSON.stringify(newTheme));
    } catch (e) {
      console.warn('Erro ao salvar tema no localStorage:', e);
    }
    setTimeout(() => setIsApplyingTheme(false), 1200);
  };

  const handleFontSizeChange = (newFontSize: FontSizeConfig) => {
    setFontSize(newFontSize);
    // Salvar no localStorage
    try {
      localStorage.setItem('astro-font-size', JSON.stringify(newFontSize));
    } catch (e) {
      console.warn('Erro ao salvar tamanho de fonte no localStorage:', e);
    }
  };

  return (
    <div
      className="min-h-screen bg-gradient-to-b from-[color:var(--custom-neutral,_var(--background))] via-[color:var(--custom-neutral,_var(--background))] to-[#1a1f4a] dark:to-[#1a1f4a] light:to-[#F0E6D2]"
      style={themeStyles as React.CSSProperties}
    >
      {/* Header */}
      <header className="border-b border-border/30 backdrop-blur-sm sticky top-0 z-10 bg-background/80">
        <div className="max-w-[1800px] mx-auto px-4">
          {/* Top Row: Title and Actions */}
          <div className="flex items-center justify-between py-4">
            <h2 className="text-accent">Mapa Astral Completo</h2>
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <button className="p-2 rounded-lg hover:bg-accent/10 hover:scale-110 transition-all duration-200 group">
                <UIIcons.Bell size={20} className="text-secondary group-hover:text-accent transition-colors" />
              </button>
              <button
                className="p-2 rounded-lg hover:bg-accent/10 hover:scale-110 transition-all duration-200 group"
                onClick={() => setShowThemeModal(true)}
              >
                <UIIcons.Settings size={20} className="text-secondary group-hover:text-accent group-hover:rotate-90 transition-all duration-200" />
              </button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="p-2 rounded-lg hover:bg-accent/10 hover:scale-110 transition-all duration-200 cursor-pointer group">
                    <Avatar className="w-8 h-8 bg-accent/20 group-hover:bg-accent/30 transition-colors ring-2 ring-transparent group-hover:ring-accent/40">
                      <AvatarFallback className="text-accent font-medium text-sm group-hover:scale-105 transition-transform">
                        {getInitials(currentUserData.name)}
                      </AvatarFallback>
                    </Avatar>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem onClick={() => setShowEditModal(true)} className="hover:bg-accent/10 cursor-pointer group/item">
                    <UIIcons.User className="mr-2 group-hover/item:text-accent group-hover/item:scale-110 transition-all" size={16} />
                    <span className="group-hover/item:text-accent transition-colors">Editar Perfil</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} variant="destructive" className="hover:bg-destructive/10 cursor-pointer group/item">
                    <UIIcons.LogOut className="mr-2 group-hover/item:scale-110 transition-all" size={16} />
                    <span className="group-hover/item:opacity-90 transition-opacity">Sair</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
          
          {/* Bottom Row: Navigation Tabs */}
          <div className="pb-3">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="w-full justify-start bg-card/50 backdrop-blur-sm dark:bg-card/70 p-1 flex-wrap">
                <TabsTrigger value="guide" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent dark:data-[state=active]:bg-accent/30 dark:data-[state=active]:text-accent dark:text-foreground/90 dark:hover:text-accent hover:bg-accent/10 hover:scale-105 transition-all duration-200 flex items-center gap-2">
                  <BookOpen size={16} className="text-blue-500 dark:text-blue-400" />
                  Seu Guia Pessoal
                </TabsTrigger>
                <TabsTrigger value="overview" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent dark:data-[state=active]:bg-accent/30 dark:data-[state=active]:text-accent dark:text-foreground/90 dark:hover:text-accent hover:bg-accent/10 hover:scale-105 transition-all duration-200 flex items-center gap-2">
                  <Eye size={16} className="text-purple-500 dark:text-purple-400" />
                  Visão Geral
                </TabsTrigger>
                <TabsTrigger value="biorhythms" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent dark:data-[state=active]:bg-accent/30 dark:data-[state=active]:text-accent dark:text-foreground/90 dark:hover:text-accent hover:bg-accent/10 hover:scale-105 transition-all duration-200 flex items-center gap-2">
                  <Activity size={16} className="text-green-500 dark:text-green-400" />
                  Biorritmos
                </TabsTrigger>
                <TabsTrigger value="synastry" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent dark:data-[state=active]:bg-accent/30 dark:data-[state=active]:text-accent dark:text-foreground/90 dark:hover:text-accent hover:bg-accent/10 flex items-center gap-2">
                  <Heart size={16} className="text-pink-500 dark:text-pink-400" />
                  Sinastria
                </TabsTrigger>
                <TabsTrigger value="guide2026" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent dark:data-[state=active]:bg-accent/30 dark:data-[state=active]:text-accent dark:text-foreground/90 dark:hover:text-accent hover:bg-accent/10 flex items-center gap-2">
                  <Calendar size={16} className="text-orange-500 dark:text-orange-400" />
                  Guia 2026
                </TabsTrigger>
                <TabsTrigger value="lunarNodes" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent dark:data-[state=active]:bg-accent/30 dark:data-[state=active]:text-accent dark:text-foreground/90 dark:hover:text-accent hover:bg-accent/10 flex items-center gap-2">
                  <Moon size={16} className="text-indigo-500 dark:text-indigo-400" />
                  Nodos Lunares
                </TabsTrigger>
                <TabsTrigger value="planets" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent dark:data-[state=active]:bg-accent/30 dark:data-[state=active]:text-accent dark:text-foreground/90 dark:hover:text-accent hover:bg-accent/10 flex items-center gap-2">
                  <Star size={16} className="text-yellow-500 dark:text-yellow-400" />
                  Planetas
                </TabsTrigger>
                <TabsTrigger value="houses" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent dark:data-[state=active]:bg-accent/30 dark:data-[state=active]:text-accent dark:text-foreground/90 dark:hover:text-accent hover:bg-accent/10 flex items-center gap-2">
                  <Home size={16} className="text-amber-600 dark:text-amber-500" />
                  Casas
                </TabsTrigger>
                <TabsTrigger value="aspects" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent dark:data-[state=active]:bg-accent/30 dark:data-[state=active]:text-accent dark:text-foreground/90 dark:hover:text-accent hover:bg-accent/10 flex items-center gap-2">
                  <Zap size={16} className="text-cyan-500 dark:text-cyan-400" />
                  Aspectos
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </div>
      </header>

      {/* Main Layout: Fixed Left Sidebar + Tabbed Content */}
      <div className="max-w-[1800px] mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Sidebar - Fixed Chart & Big Three */}
          <aside className="lg:col-span-4 xl:col-span-3 space-y-6">
            <div className="lg:sticky lg:top-24 space-y-6">
              {/* User Info */}
              <AstroCard>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <button className="cursor-pointer hover:scale-105 transition-all duration-200 group">
                            <Avatar className="w-12 h-12 bg-accent/20 group-hover:bg-accent/30 transition-colors ring-2 ring-transparent group-hover:ring-accent/40">
                              <AvatarFallback className="text-accent font-medium group-hover:scale-105 transition-transform">
                                {getInitials(currentUserData.name)}
                              </AvatarFallback>
                            </Avatar>
                          </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-48">
                          <DropdownMenuItem onClick={() => setShowEditModal(true)} className="hover:bg-accent/10 cursor-pointer group/item">
                            <UIIcons.User className="mr-2 group-hover/item:text-accent group-hover/item:scale-110 transition-all" size={16} />
                            <span className="group-hover/item:text-accent transition-colors">Editar Perfil</span>
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem onClick={handleLogout} variant="destructive" className="hover:bg-destructive/10 cursor-pointer group/item">
                            <UIIcons.LogOut className="mr-2 group-hover/item:scale-110 transition-all" size={16} />
                            <span className="group-hover/item:opacity-90 transition-opacity">Sair</span>
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                      <div className="flex-1">
                        <h3 className="text-foreground">{currentUserData.name}</h3>
                        <p className="text-sm text-secondary">
                          {currentUserData.birthDate.toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="pt-3 border-t border-border/30 space-y-1">
                    <p className="text-sm text-secondary flex items-center gap-2">
                      <UIIcons.Clock size={14} />
                      {currentUserData.birthTime}
                    </p>
                    <p className="text-sm text-secondary flex items-center gap-2">
                      <UIIcons.MapPin size={14} />
                      {currentUserData.birthPlace}
                    </p>
                  </div>
                </div>
              </AstroCard>

              {/* Birth Chart Wheel */}
              <AstroCard>
                <div className="space-y-4">
                  <h3 className="text-foreground text-center">Mapa Natal</h3>
                  <BirthChartWheel />
                </div>
              </AstroCard>

              {/* Big Three */}
              <AstroCard>
                <h3 className="text-foreground mb-4">Seus Três Pilares</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-accent/10 hover:bg-accent/20 hover:scale-[1.02] transition-all duration-200 cursor-pointer group">
                    <bigThree.sun.icon size={32} className="text-accent group-hover:scale-110 group-hover:rotate-12 transition-all duration-200" />
                    <div>
                      <p className="text-xs text-secondary group-hover:text-foreground transition-colors">Sol</p>
                      <p className="text-foreground group-hover:text-accent transition-colors">{bigThree.sun.sign}</p>
                      {chartBasics.sun && (
                        <p className="text-xs text-secondary group-hover:text-foreground transition-colors">
                          {bigThree.sun.degree.toFixed(1)}°
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-accent/10 hover:bg-accent/20 hover:scale-[1.02] transition-all duration-200 cursor-pointer group">
                    <bigThree.moon.icon size={32} className="text-accent group-hover:scale-110 group-hover:rotate-12 transition-all duration-200" />
                    <div>
                      <p className="text-xs text-secondary group-hover:text-foreground transition-colors">Lua</p>
                      <p className="text-foreground group-hover:text-accent transition-colors">{bigThree.moon.sign}</p>
                      {chartBasics.moon && (
                        <p className="text-xs text-secondary group-hover:text-foreground transition-colors">
                          {bigThree.moon.degree.toFixed(1)}°
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-accent/10 hover:bg-accent/20 hover:scale-[1.02] transition-all duration-200 cursor-pointer group">
                    <bigThree.ascendant.icon size={32} className="text-accent group-hover:scale-110 group-hover:rotate-12 transition-all duration-200" />
                    <div>
                      <p className="text-xs text-secondary group-hover:text-foreground transition-colors">Ascendente</p>
                      <p className="text-foreground group-hover:text-accent transition-colors">{bigThree.ascendant.sign}</p>
                      {chartBasics.ascendant && (
                        <p className="text-xs text-secondary group-hover:text-foreground transition-colors">
                          {bigThree.ascendant.degree.toFixed(1)}°
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </AstroCard>
            </div>
          </aside>

          {/* Right Content Area - Tabs */}
          <main className="lg:col-span-8 xl:col-span-9">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              {/* Tab 0: Seu Guia Pessoal */}
              <TabsContent value="guide" className="space-y-8">
                {/* Seção 1: Regente do Mapa 
                    - Mostra o planeta regente baseado no Ascendente
                    - ascendant: Signo do Ascendente do usuário
                    - ruler: Planeta regente desse ascendente
                    - rulerSign: Signo onde o regente está posicionado
                    - rulerHouse: Casa onde o regente está posicionado
                */}
                {chartRuler ? (
                  <ChartRulerSection
                    ascendant={chartRuler.ascendant}
                    ruler={chartRuler.ruler}
                    rulerSign={chartRuler.rulerSign}
                    rulerHouse={chartRuler.rulerHouse}
                  />
                ) : (
                  <AstroCard>
                    <p className="text-secondary">Calculando regente do mapa...</p>
                  </AstroCard>
                )}

                {/* Seção Meio do Céu */}
                {midheavenInfo ? (
                  <AstroCard className="border border-accent/30 bg-accent/5 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <midheavenInfo.icon size={36} className="text-accent" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-foreground/70 dark:text-foreground/80 font-medium">
                            Meio do Céu
                          </p>
                          <p className="text-foreground text-lg font-semibold">
                            {midheavenInfo.sign}{' '}
                            <span className="text-foreground/70 dark:text-foreground/80 text-base font-normal">
                              {midheavenInfo.degree.toFixed(1)}°
                            </span>
                          </p>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-accent border-accent/60 bg-accent/10 dark:bg-accent/15 font-semibold">
                        MC
                      </Badge>
                    </div>

                    <div className="space-y-3">
                      {midheavenInfo.planets.length > 0 ? (
                        <>
                          <p className="text-sm text-secondary">
                            Planetas conjuntos ao MC:
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {midheavenInfo.planets.map((planet) => (
                              <span
                                key={planet}
                                className="px-3 py-1 rounded-full bg-accent/30 dark:bg-accent/25 text-accent font-medium text-sm border border-accent/40 shadow-sm"
                              >
                                {planet}
                              </span>
                            ))}
                          </div>
                        </>
                      ) : (
                        <p className="text-sm text-secondary">
                          Nenhum planeta estritamente conjunto ao Meio do Céu.
                        </p>
                      )}
                    </div>

                    {midheavenInfo.uranusOnMC ? (
                      <div className="p-4 rounded-lg bg-[#4ECDC4]/25 border-2 border-[#4ECDC4]/60 shadow-lg shadow-[#4ECDC4]/20">
                        <p className="text-sm font-semibold text-[#0A7C72] dark:text-[#2ED4C4] mb-2">
                          Urano em destaque
                        </p>
                        <p className="text-sm text-foreground leading-relaxed">
                          Urano está conjunto ao Meio do Céu, sinalizando vocação marcada
                          por inovação, autenticidade e necessidade de quebrar padrões nas
                          suas metas e carreira.
                        </p>
                      </div>
                    ) : (
                      <p className="text-sm text-secondary">
                        Use o Meio do Céu para entender sua reputação e direção profissional.
                      </p>
                    )}
                  </AstroCard>
                ) : (
                  <AstroCard>
                    <p className="text-secondary">
                      Buscando dados do Meio do Céu a partir do backend...
                    </p>
                  </AstroCard>
                )}

                {/* Seção 2: Conselhos para Hoje 
                    - Mostra trânsitos diários e conselhos práticos
                    - moonSign: Signo atual da Lua em trânsito
                    - moonHouse: Casa do mapa natal onde a Lua transita hoje
                    - isMercuryRetrograde: true se Mercúrio está retrógrado
                    - isMoonVoidOfCourse: true se Lua está fora de curso
                    - voidEndsAt: Horário que a Lua sai do void of course
                */}
                <DailyAdviceSection
                  moonSign="Câncer"
                  moonHouse={11}
                  isMercuryRetrograde={true}
                  isMoonVoidOfCourse={false}
                  voidEndsAt="16:30"
                  planetaryData={planetaryData}
                />

                {/* Seção 3: Horizontes Futuros 
                    - Mostra trânsitos de longo prazo (planetas lentos)
                    - Pode receber um array customizado de trânsitos
                    - Se não passar nada, usa dados de exemplo
                */}
                <FutureTransitsSection />
              </TabsContent>

              {/* Tab 1: Overview */}
              <TabsContent value="overview" className="space-y-6">
                {/* Cosmic Balance */}
                <AstroCard className="relative">
                  <h2 className="text-accent mb-6">Balanço de Elementos e Modalidades</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <ElementChart data={elementsData} title="Elementos" />
                    <ElementChart data={modalitiesData} title="Modalidades" />
                  </div>
                  <div className="mt-6 flex justify-start">
                    <AstroButton
                      onClick={() => {
                        setShowElementsModal(true);
                      }}
                      className="text-sm inline-flex items-center gap-2"
                    >
                      <UIIcons.BookOpen className="w-4 h-4" />
                      Leia mais
                    </AstroButton>
                  </div>
                </AstroCard>

                {/* Strengths and Challenges */}
                <AstroCard>
                  <h2 className="text-accent mb-6">Principais Padrões do Mapa</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h3 className="text-foreground flex items-center gap-2">
                        <AspectIcons.Trine size={20} className="text-green-400" />
                        Forças
                      </h3>
                      <div className="space-y-3">
                        {strengths.map((strength, i) => (
                          <div
                            key={i}
                            className="p-4 rounded-lg bg-green-400/10 border border-green-400/20"
                          >
                            <h4 className="text-foreground mb-2">{strength.title}</h4>
                            <p className="text-sm text-secondary">{strength.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h3 className="text-foreground flex items-center gap-2">
                        <AspectIcons.Square size={20} className="text-red-400" />
                        Desafios
                      </h3>
                      <div className="space-y-3">
                        {challenges.map((challenge, i) => (
                          <div
                            key={i}
                            className="p-4 rounded-lg bg-red-400/10 border border-red-400/20"
                          >
                            <h4 className="text-foreground mb-2">{challenge.title}</h4>
                            <p className="text-sm text-secondary">{challenge.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </AstroCard>
              </TabsContent>

              {/* Tab 2: Biorhythms */}
              <TabsContent value="biorhythms" className="space-y-6">
                <AstroCard className="space-y-6">
                  <div>
                    <h2 className="text-accent mb-2">Essência • Tripé Astrológico</h2>
                    <p className="text-secondary text-sm">
                      Um olhar integrado sobre Sol, Lua e Ascendente para entender onde sua vitalidade brilha, como o coração reage e de que forma o mundo percebe sua presença nesta semana.
                    </p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-lg border border-border/40 bg-card/40 space-y-2 hover:bg-card/60 hover:border-accent/40 hover:scale-[1.02] transition-all duration-200 cursor-pointer group">
                      <div className="flex items-center gap-2">
                        <bigThree.sun.icon size={28} className="text-accent group-hover:scale-110 group-hover:rotate-12 transition-all duration-200" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-secondary group-hover:text-foreground transition-colors">Sol</p>
                          <p className="text-foreground font-medium group-hover:text-accent transition-colors">{bigThree.sun.sign}</p>
                        </div>
                      </div>
                      <p className="text-sm text-secondary leading-relaxed">
                        Vitalidade focada em {bigThree.sun.sign}, convidando você a brilhar através de {bigThree.sun.sign === 'Libra' ? 'parcerias e estética equilibrada' : 'expressões autênticas'}. Onde você pode aplicar essa luz hoje?
                      </p>
                    </div>
                    <div className="p-4 rounded-lg border border-border/40 bg-card/40 space-y-2 hover:bg-card/60 hover:border-accent/40 hover:scale-[1.02] transition-all duration-200 cursor-pointer group">
                      <div className="flex items-center gap-2">
                        <bigThree.moon.icon size={28} className="text-accent group-hover:scale-110 group-hover:rotate-12 transition-all duration-200" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-secondary group-hover:text-foreground transition-colors">Lua</p>
                          <p className="text-foreground font-medium group-hover:text-accent transition-colors">{bigThree.moon.sign}</p>
                        </div>
                      </div>
                      <p className="text-sm text-secondary leading-relaxed">
                        Emoções pulsando em {bigThree.moon.sign}. Observe como sua intuição reage: precisa de aconchego, coragem ou movimento? Responda a isso antes de tomar decisões.
                      </p>
                    </div>
                    <div className="p-4 rounded-lg border border-border/40 bg-card/40 space-y-2 hover:bg-card/60 hover:border-accent/40 hover:scale-[1.02] transition-all duration-200 cursor-pointer group">
                      <div className="flex items-center gap-2">
                        <bigThree.ascendant.icon size={28} className="text-accent group-hover:scale-110 group-hover:rotate-12 transition-all duration-200" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-secondary group-hover:text-foreground transition-colors">Ascendente</p>
                          <p className="text-foreground font-medium group-hover:text-accent transition-colors">{bigThree.ascendant.sign}</p>
                        </div>
                      </div>
                      <p className="text-sm text-secondary leading-relaxed">
                        O mundo percebe você como {bigThree.ascendant.sign}. Use essa motivação inicial para escolher como quer ser visto hoje: mais ousado ou mais reservado?
                      </p>
                    </div>
                  </div>
                </AstroCard>

                <AstroCard className="space-y-5">
                  <div className="flex flex-wrap gap-4 items-start justify-between">
                    <div>
                      <h2 className="text-accent mb-1">Biorritmo Astral</h2>
                      <p className="text-sm text-secondary">
                        Lua {lunarPhaseInfo.name} em {moonTransitSign}. {lunarPhaseInfo.guidance}
                      </p>
                    </div>
                    <Badge variant="outline" className="text-accent border-accent/40">
                      Ciclos Semanais
                    </Badge>
                  </div>

                  {biorhythmLevels ? (
                    <div className="space-y-4">
                      {(Object.keys(BIORHYTHM_CYCLES) as Array<keyof typeof BIORHYTHM_CYCLES>).map((key) => {
                        const level = biorhythmLevels[key];
                        return (
                          <div key={key} className="space-y-2">
                            <div className="flex items-center justify-between text-sm text-secondary">
                              <span className="font-medium text-foreground">{BIORHYTHM_LABELS[key]}</span>
                              <span>
                                {level.percentage}% •{' '}
                                {level.trend === 'ascendente' ? 'energia crescente' : 'energia pedindo cuidado'}
                              </span>
                            </div>
                            <div className="h-2 rounded-full bg-border/40 overflow-hidden">
                              <div
                                className={`h-full transition-all ${
                                  level.value >= 0 ? 'bg-accent' : 'bg-secondary/60'
                                }`}
                                style={{ width: `${level.percentage}%` }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="text-sm text-secondary">
                      Forneça data de nascimento válida para calcular seus ciclos físico, emocional e intelectual.
                    </p>
                  )}

                  <div className="p-4 rounded-lg bg-accent/10 border border-accent/30">
                    <p className="text-sm font-medium text-accent mb-1">Agir ou recuar?</p>
                    <p className="text-sm text-foreground leading-relaxed">{biorhythmAdvice}</p>
                  </div>
                </AstroCard>
              </TabsContent>

              {/* Tab 3: Sinastria */}
              <TabsContent value="synastry" className="space-y-6">
                <AstroCard className="space-y-4">
                  <div>
                    <h2 className="text-accent mb-2">Mapa do Amor • Vênus & Marte</h2>
                    <p className="text-secondary text-sm">
                      Leia sua assinatura de atração (Vênus) e como você se move para conquistar (Marte). Use estas
                      pistas para lapidar encontros, flertes e vínculos em andamento.
                    </p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-lg border border-border/40 bg-card/40 space-y-3">
                      <div className="flex items-center gap-2">
                        <venusIconComponent size={28} className="text-accent" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-secondary">Vênus</p>
                          <p className="text-foreground font-medium">
                            {venusProfile ? `${venusProfile.sign} • Casa ${venusProfile.house}` : 'Atualizando'}
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-secondary leading-relaxed">
                        Você valoriza relações que emanam {venusProfile?.sign || 'harmonia'}, com desejo de viver
                        experiências afetivas através da Casa {venusProfile?.house || '—'}. Atração cresce quando há
                        estética e valores compartilhados.
                      </p>
                    </div>
                    <div className="p-4 rounded-lg border border-border/40 bg-card/40 space-y-3">
                      <div className="flex items-center gap-2">
                        <marsIconComponent size={28} className="text-accent" />
                        <div>
                          <p className="text-xs uppercase tracking-wide text-secondary">Marte</p>
                          <p className="text-foreground font-medium">
                            {marsProfile ? `${marsProfile.sign} • Casa ${marsProfile.house}` : 'Atualizando'}
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-secondary leading-relaxed">
                        Você conquista com a vibração de {marsProfile?.sign || 'autenticidade'} e prefere agir na Casa{' '}
                        {marsProfile?.house || '—'}. Use essa chama para iniciar conversas e demonstrar intenções.
                      </p>
                    </div>
                  </div>
                </AstroCard>

                <AstroCard className="space-y-5">
                  <div className="flex items-center justify-between flex-wrap gap-3">
                    <div>
                      <h2 className="text-accent mb-1">Dica de Relacionamento</h2>
                      <p className="text-sm text-secondary">
                        Casa 5 fala do romance espontâneo; Casa 7, dos compromissos espelhados. Use ambas para entender
                        onde investir sua energia.
                      </p>
                    </div>
                    <Badge variant="outline" className="text-accent border-accent/40">
                      Status: {relationshipStatus === 'couple' ? 'Em casal' : 'Solteiro(a)'}
                    </Badge>
                  </div>

                  {relationshipStatus === 'single' || !partnerData ? (
                    <>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 rounded-lg border border-border/40 bg-card/30 space-y-2">
                          <p className="text-xs uppercase tracking-wide text-secondary">Casa 5 • Prazeres</p>
                          <h3 className="text-foreground text-lg">
                            {house5Info?.cuspSign || 'Atualizando'} em destaque
                          </h3>
                          <p className="text-sm text-secondary">
                            Lugares criativos, hobbies, eventos artísticos e espaços ligados a {house5Info?.cuspSign ||
                              'seu estilo'} despertam conexões leves. Pessoas com planetas em{' '}
                            {house5Info?.planetsInHouse?.join(', ') || 'fogo criativo'} podem cruzar seu caminho.
                          </p>
                        </div>
                        <div className="p-4 rounded-lg border border-border/40 bg-card/30 space-y-2">
                          <p className="text-xs uppercase tracking-wide text-secondary">Casa 7 • Parcerias</p>
                          <h3 className="text-foreground text-lg">
                            {house7Info?.cuspSign || 'Atualizando'} no horizonte
                          </h3>
                          <p className="text-sm text-secondary">
                            Observe pessoas que expressem valores de {house7Info?.cuspSign || 'equilíbrio'}: elas tendem
                            a espelhar seu potencial para parcerias estáveis. Conversas profundas e acordos claros abrem
                            portas para algo duradouro.
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-secondary">
                        Dica: agende experiências que combinem lazer (Casa 5) e networking consciente (Casa 7). Sua Vênus
                        e Marte já sabem onde acender a chama.
                      </p>
                    </>
                  ) : (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 rounded-lg border border-border/40 bg-card/30 space-y-2">
                          <p className="text-xs uppercase tracking-wide text-secondary">Sóis em Diálogo</p>
                          <h3 className="text-foreground text-lg">
                            {backendChartData?.sun_sign || chartBasics.sun?.sign || 'Você'} +{' '}
                            {partnerData.sunSign || 'Parceiro(a)'}
                          </h3>
                          <p className="text-sm text-secondary">
                            Harmonia flui quando vocês reconhecem a forma diferente de brilhar. Busque atividades onde
                            cada um possa liderar em turnos, evitando disputas de ego.
                          </p>
                        </div>
                        <div className="p-4 rounded-lg border border-border/40 bg-card/30 space-y-2">
                          <p className="text-xs uppercase tracking-wide text-secondary">Luas em Sintonia</p>
                          <h3 className="text-foreground text-lg">
                            {backendChartData?.moon_sign || chartBasics.moon?.sign || 'Sua Lua'} +{' '}
                            {partnerData.moonSign || 'Lua do parceiro(a)'}
                          </h3>
                          <p className="text-sm text-secondary">
                            Observem o ritmo emocional: quando uma Lua prefere recolhimento, a outra pode oferecer
                            acolhimento. Criem rituais de cuidado mútuo.
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-secondary">
                        Pontos de fluxo aparecem quando ambos celebram semelhanças solares; travas surgem se emoções são
                        guardadas. Nomeiem necessidades e mantenham encontros conscientes.
                      </p>
                    </div>
                  )}
                </AstroCard>
              </TabsContent>

              {/* Tab 4: Guia 2026 */}
              <TabsContent value="guide2026" className="space-y-6">
                <AstroCard className="space-y-4">
                  <div className="flex items-center justify-between flex-wrap gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-wide text-secondary">Seção 4 • O Futuro</p>
                      <h2 className="text-accent text-xl">Guia 2026 em linguagem simples</h2>
                      <p className="text-sm text-secondary mt-1">
                        Trânsito = passagem de um planeta pelo céu ativando áreas do seu mapa. Use estas pistas para
                        planejar o próximo ciclo com mais clareza.
                      </p>
                    </div>
                    <Badge variant="outline" className="text-accent border-accent/40">
                      2026
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-lg border border-border/40 bg-card/40 space-y-3">
                      <p className="text-xs uppercase tracking-wide text-secondary">Trânsitos de Poder</p>
                      <h3 className="text-foreground text-lg font-medium">
                        Júpiter em {futureGuide.jupiterSign}{' '}
                        {futureGuide.jupiterHouse ? `• Casa ${futureGuide.jupiterHouse}` : ''}
                      </h3>
                      <p className="text-sm text-secondary leading-relaxed">{futureGuide.jupiterSummary}</p>
                      <p className="text-xs text-secondary/70">
                        Anote oportunidades e convites que chegarem de forma espontânea. Eles mostram onde a vida quer
                        expandir em 2026.
                      </p>
                    </div>
                    <div className="p-4 rounded-lg border border-border/40 bg-card/40 space-y-3">
                      <p className="text-xs uppercase tracking-wide text-secondary">Radar emocional</p>
                      <p className="text-sm text-secondary">
                        Expansão saudável = entusiasmo com limites. Exagero = prometer mais do que cabe no calendário.
                        Revise agendas quinzenalmente para manter o fluxo leve.
                      </p>
                      <ul className="text-sm text-secondary space-y-2">
                        <li>• Pergunte: “isso me aproxima do meu foco ou é distração?”</li>
                        <li>• Descanse o suficiente para aproveitar cada vitória.</li>
                        <li>• Compartilhe planos com alguém de confiança para ganhar apoio.</li>
                      </ul>
                    </div>
                  </div>
                </AstroCard>

                <AstroCard className="space-y-4">
                  <div>
                    <h3 className="text-accent">Desafios • Planetas lentos</h3>
                    <p className="text-sm text-secondary">
                      Aspecto tenso = conversa mais séria no céu (quadratura = 90°, oposição = 180°). Não é sentença,
                      apenas pedido de atenção e preparo.
                    </p>
                  </div>
                  <div className="space-y-3">
                    {futureGuide.challenges.map((challenge) => (
                      <div
                        key={challenge.id}
                        className="border-l-4 border-accent/60 bg-accent/5 p-3 rounded-md space-y-1"
                      >
                        <p className="text-sm font-medium text-accent">{challenge.aspectLabel}</p>
                        <p className="text-sm text-secondary leading-relaxed">{challenge.text}</p>
                      </div>
                    ))}
                  </div>
                </AstroCard>

                <AstroCard className="space-y-3">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <h3 className="text-accent">Foco do Ano</h3>
                    <Badge variant="outline" className="text-secondary border-border/50">
                      Mantra de bolso
                    </Badge>
                  </div>
                  <p className="text-lg font-serif text-foreground">
                    “{futureGuide.mantra}”
                  </p>
                  <p className="text-sm text-secondary">
                    Repita quando precisar lembrar sua prioridade. Foco simples = energia bem usada.
                  </p>
                </AstroCard>

                <AstroCard className="space-y-5">
                  <div className="flex items-start justify-between flex-wrap gap-3">
                    <div>
                      <p className="text-xs uppercase tracking-wide text-secondary">Calendário vivo</p>
                      <h3 className="text-accent text-lg">Previsões mensais 2026</h3>
                      <p className="text-sm text-secondary mt-1">
                        Resumo direto de quais astros puxam cada mês, com cuidados e oportunidades para negócios e amor.
                      </p>
                    </div>
                    <Badge variant="outline" className="text-accent border-accent/40">12 meses</Badge>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {MONTHLY_FORECASTS_2026.map((forecast) => (
                      <div
                        key={forecast.month}
                        className="p-4 rounded-lg border border-border/40 bg-card/30 space-y-3 shadow-sm"
                      >
                        <div className="space-y-2">
                          <div className="flex items-center justify-between gap-2">
                            <Badge variant="outline" className="text-accent border-accent/30">
                              {forecast.month}
                            </Badge>
                            <span className="text-xs text-secondary/80">{forecast.theme}</span>
                          </div>
                          <p className="text-sm text-secondary leading-relaxed">{forecast.influencers}</p>
                        </div>
                        <div className="space-y-3">
                          <div>
                            <p className="text-xs uppercase tracking-wide text-secondary/70">Negócios e dinheiro</p>
                            <p className="text-sm text-secondary leading-relaxed">{forecast.business}</p>
                          </div>
                          <div>
                            <p className="text-xs uppercase tracking-wide text-secondary/70">Amor e relações</p>
                            <p className="text-sm text-secondary leading-relaxed">{forecast.love}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </AstroCard>
              </TabsContent>

              {/* Tab 5: Lunar Nodes */}
              <TabsContent value="lunarNodes" className="space-y-6">
                <AstroCard className="space-y-4">
                  <div>
                    <h2 className="text-accent mb-2">O Destino • Nodos Lunares</h2>
                    <p className="text-secondary text-sm">
                      Cabeça e Cauda do Dragão revelam a bússola kármica: onde sua alma deve crescer (Nodo Norte) e quais
                      comportamentos podem ser reciclados (Nodo Sul).
                    </p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-lg border border-border/40 bg-card/30 space-y-2">
                      <p className="text-xs uppercase tracking-wide text-secondary">Missão de Alma</p>
                      <h3 className="text-foreground text-lg font-medium">
                        Nodo Norte{' '}
                        {lunarNodes
                          ? `em ${lunarNodes.north.sign} • ${lunarNodes.north.degree.toFixed(1)}°`
                          : 'em atualização'}
                      </h3>
                      <p className="text-sm text-secondary leading-relaxed">
                        {formatNodeDescription(lunarNodes?.north.sign, true)}
                      </p>
                    </div>
                    <div className="p-4 rounded-lg border border-border/40 bg-card/30 space-y-2">
                      <p className="text-xs uppercase tracking-wide text-secondary">Zona de Conforto</p>
                      <h3 className="text-foreground text-lg font-medium">
                        Nodo Sul{' '}
                        {lunarNodes
                          ? `em ${lunarNodes.south.sign} • ${lunarNodes.south.degree.toFixed(1)}°`
                          : 'em atualização'}
                      </h3>
                      <p className="text-sm text-secondary leading-relaxed">
                        {formatNodeDescription(lunarNodes?.south.sign, false)}
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-secondary">
                    Dica: anote situações em que se sente repetindo velhos padrões (Nodo Sul) e escolha uma ação ousada
                    alinhada ao Nodo Norte nesta semana.
                  </p>
                </AstroCard>

                <AstroCard className="space-y-4">
                  <div className="flex items-center justify-between flex-wrap gap-3">
                    <div>
                      <h2 className="text-accent mb-1">O Mestre do Tempo • Saturno</h2>
                      <p className="text-sm text-secondary">
                        Saturno aponta o compromisso que precisa de disciplina agora. Ele revela onde limites viram
                        maturidade.
                      </p>
                    </div>
                    <Badge variant="outline" className="text-accent border-accent/40">
                      Responsabilidade
                    </Badge>
                  </div>
                  <div className="p-4 rounded-lg border border-border/40 bg-card/40 space-y-3">
                    <div className="flex items-center gap-3">
                      <saturnIconComponent size={32} className="text-accent" />
                      <div>
                        <p className="text-xs uppercase tracking-wide text-secondary">Saturno</p>
                        <p className="text-foreground text-lg font-medium">
                          {saturnProfile
                            ? `${saturnProfile.sign} • Casa ${saturnProfile.house}`
                            : 'Aguardando cálculo'}
                        </p>
                      </div>
                    </div>
                    <p className="text-sm text-secondary leading-relaxed">
                      {saturnProfile
                        ? `Saturno em ${saturnProfile.sign} exige seriedade ao lidar com temas da Casa ${saturnProfile.house}. Comprometa-se com objetivos de longo prazo; a consistência agora se torna autoridade mais adiante.`
                        : 'Assim que a posição de Saturno estiver disponível, destacaremos a grande lição de responsabilidade deste ciclo.'}
                    </p>
                  </div>
                </AstroCard>
              </TabsContent>

              {/* Tab 2: Planets */}
              <TabsContent value="planets" className="space-y-4">
                <AstroCard>
                  <h2 className="text-accent mb-6">Posições Planetárias</h2>
                  <Accordion type="single" collapsible className="space-y-3">
                    {planetaryData.map((planet, index) => (
                      <AccordionItem
                        key={planet.name}
                        value={planet.name}
                        className="border border-border/30 rounded-lg px-4 bg-card/50 backdrop-blur-sm"
                      >
                        <AccordionTrigger className="hover:no-underline group/accordion">
                          <div className="flex items-center gap-4 w-full">
                            <planet.icon size={28} className="text-accent group-hover/accordion:scale-110 group-hover/accordion:rotate-12 transition-all duration-200" />
                            <div className="flex-1 text-left">
                              <h3 className="text-foreground group-hover/accordion:text-accent transition-colors">{planet.name}</h3>
                              <p className="text-sm text-secondary group-hover/accordion:text-foreground transition-colors">
                                em {planet.sign}, na Casa {planet.house} ({planet.degree}°)
                              </p>
                            </div>
                            <planet.signIcon size={24} className="text-accent opacity-50 group-hover/accordion:opacity-100 group-hover/accordion:scale-110 transition-all duration-200" />
                          </div>
                        </AccordionTrigger>
                        <AccordionContent className="pt-4 space-y-4">
                          <div className="space-y-3">
                            <div className="p-4 rounded-lg bg-accent/5 border border-accent/20">
                              <h4 className="text-foreground mb-2 flex items-center gap-2 group/icon">
                                <planet.signIcon size={18} className="text-accent group-hover/icon:scale-125 group-hover/icon:rotate-12 transition-all duration-200" />
                                {planet.name} em {planet.sign}
                              </h4>
                              <p className="text-secondary leading-relaxed">
                                {planet.interpretation.inSign}
                              </p>
                            </div>
                            <div className="p-4 rounded-lg bg-accent/5 border border-accent/20">
                              <h4 className="text-foreground mb-2">
                                {planet.name} na Casa {planet.house}
                              </h4>
                              <p className="text-secondary leading-relaxed">
                                {planet.interpretation.inHouse}
                              </p>
                            </div>
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                </AstroCard>
              </TabsContent>

              {/* Tab 3: Houses */}
              <TabsContent value="houses" className="space-y-4">
                <AstroCard>
                  <h2 className="text-accent mb-6">As 12 Casas Astrológicas</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {housesData.map((house) => (
                      <button
                        key={house.number}
                        onClick={() => setSelectedHouse(house)}
                        className={`p-4 rounded-lg border transition-all text-left hover:border-accent/50 ${
                          house.isAngular
                            ? 'border-accent/40 bg-accent/5'
                            : 'border-border/30 bg-card/30'
                        }`}
                      >
                        <div className="space-y-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <h3 className="text-foreground">Casa {house.number}</h3>
                              <p className="text-sm text-secondary mt-1">{house.theme}</p>
                            </div>
                            {house.isAngular && (
                              <UIIcons.Star size={16} className="text-accent" />
                            )}
                          </div>
                          <div className="pt-2 border-t border-border/30 space-y-2">
                            <p className="text-xs text-secondary">
                              Cúspide: {house.cuspSign}
                            </p>
                            {house.planetsInHouse.length > 0 && (
                              <div className="flex gap-2 flex-wrap">
                                {house.planetsInHouse.map((planetName) => {
                                  const planet = planetaryData.find(
                                    (p) => p.name === planetName
                                  );
                                  return planet ? (
                                    <div
                                      key={planetName}
                                      className="flex items-center gap-1 px-2 py-1 rounded-full bg-accent/20"
                                    >
                                      <planet.icon size={14} className="text-accent" />
                                      <span className="text-xs text-accent">
                                        {planetName}
                                      </span>
                                    </div>
                                  ) : null;
                                })}
                              </div>
                            )}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </AstroCard>
              </TabsContent>

              {/* Tab 4: Aspects */}
              <TabsContent value="aspects" className="space-y-4">
                <AstroCard>
                  <div className="space-y-6">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                      <h2 className="text-accent">Aspectos Planetários</h2>
                      <div className="flex gap-2 flex-wrap">
                        <AstroButton
                          variant={aspectFilter === 'all' ? 'primary' : 'secondary'}
                          size="sm"
                          onClick={() => setAspectFilter('all')}
                        >
                          Todos
                        </AstroButton>
                        <AstroButton
                          variant={aspectFilter === 'harmonic' ? 'primary' : 'secondary'}
                          size="sm"
                          onClick={() => setAspectFilter('harmonic')}
                        >
                          Harmônicos
                        </AstroButton>
                        <AstroButton
                          variant={aspectFilter === 'dynamic' ? 'primary' : 'secondary'}
                          size="sm"
                          onClick={() => setAspectFilter('dynamic')}
                        >
                          Dinâmicos
                        </AstroButton>
                        <AstroButton
                          variant={aspectFilter === 'neutral' ? 'primary' : 'secondary'}
                          size="sm"
                          onClick={() => setAspectFilter('neutral')}
                        >
                          Neutros
                        </AstroButton>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {filteredAspects.map((aspect) => {
                        const AspectIcon = aspectData[aspect.type].icon;
                        const aspectColor = aspectData[aspect.type].color;
                        const planet1 = planetaryData.find((p) => p.name === aspect.planet1);
                        const planet2 = planetaryData.find((p) => p.name === aspect.planet2);

                        return (
                          <Accordion
                            key={aspect.id}
                            type="single"
                            collapsible
                            className="border border-border/30 rounded-lg bg-card/50 backdrop-blur-sm"
                          >
                            <AccordionItem value={aspect.id} className="border-0 px-4">
                              <AccordionTrigger className="hover:no-underline group/aspect">
                                <div className="flex items-start gap-4 w-full">
                                  <div className="flex flex-col items-center gap-3 flex-shrink-0">
                                    <div className="flex items-center gap-2">
                                      {planet1 && (
                                        <planet1.icon size={24} className="text-accent group-hover/aspect:scale-110 group-hover/aspect:rotate-12 transition-all duration-200" />
                                      )}
                                      <AspectIcon size={20} className={`${aspectColor} group-hover/aspect:scale-110 transition-all duration-200`} />
                                      {planet2 && (
                                        <planet2.icon size={24} className="text-accent group-hover/aspect:scale-110 group-hover/aspect:-rotate-12 transition-all duration-200" />
                                      )}
                                    </div>
                                    {/* Botão Leia mais - pequeno abaixo dos símbolos */}
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        loadAspectDetailedInterpretation(aspect.id, aspect.planet1, aspect.planet2, aspect.type);
                                      }}
                                      disabled={loadingAspectInterpretations[aspect.id]}
                                      className="inline-flex items-center gap-0.5 px-1 py-0.5 text-[9px] font-medium text-accent hover:text-accent/80 bg-accent/10 hover:bg-accent/20 rounded transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                      {loadingAspectInterpretations[aspect.id] ? (
                                        <UIIcons.Loader className="w-2 h-2 animate-spin" />
                                      ) : (
                                        <>
                                          <UIIcons.BookOpen className="w-2 h-2" />
                                          <span>Leia mais</span>
                                        </>
                                      )}
                                    </button>
                                  </div>
                                  <div className="flex-1 text-left">
                                    <h3 className="text-foreground">
                                      {aspect.planet1} em {aspectData[aspect.type].name} com{' '}
                                      {aspect.planet2}
                                    </h3>
                                    <div className="flex gap-2 mt-2 flex-wrap">
                                      {aspect.tags.map((tag) => (
                                        <Badge
                                          key={tag}
                                          variant="outline"
                                          className="text-xs border-accent/30 text-accent"
                                        >
                                          {tag}
                                        </Badge>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              </AccordionTrigger>
                              <AccordionContent className="pt-4">
                                <div className="p-4 rounded-lg bg-accent/5 border border-accent/20 space-y-4">
                                  <p className="text-secondary leading-relaxed">
                                    {aspect.interpretation}
                                  </p>
                                  <p className="text-xs text-secondary/70">
                                    Orb: {aspect.orb}°
                                  </p>

                                  {/* Interpretação Detalhada */}
                                  {showDetailedAspects[aspect.id] && aspectDetailedInterpretations[aspect.id] && (
                                    <div className="mt-4 p-4 rounded-lg bg-gradient-to-br from-secondary/10 to-secondary/5 border border-secondary/20">
                                      <div className="flex items-center justify-between mb-2">
                                        <h4 className="text-secondary font-medium" style={{ fontFamily: 'var(--font-sans)' }}>
                                          Interpretação Detalhada:
                                        </h4>
                                        <button
                                          onClick={() => setShowDetailedAspects(prev => ({ ...prev, [aspect.id]: false }))}
                                          className="text-secondary/70 hover:text-secondary transition-colors"
                                        >
                                          <UIIcons.X className="w-4 h-4" />
                                        </button>
                                      </div>
                                      <p className="text-secondary leading-relaxed whitespace-pre-wrap">
                                        {aspectDetailedInterpretations[aspect.id]}
                                      </p>
                                    </div>
                                  )}
                                </div>
                              </AccordionContent>
                            </AccordionItem>
                          </Accordion>
                        );
                      })}
                    </div>
                  </div>
                </AstroCard>
              </TabsContent>
            </Tabs>
          </main>
        </div>
      </div>

      {/* House Detail Modal */}
      <Dialog open={selectedHouse !== null} onOpenChange={() => setSelectedHouse(null)}>
        <DialogContent className="max-w-2xl bg-card backdrop-blur-md border border-border">
          {selectedHouse && (
            <>
              <DialogHeader>
                <DialogTitle className="text-accent flex items-center gap-3">
                  <span>Casa {selectedHouse.number}</span>
                  {selectedHouse.isAngular && <UIIcons.Star size={20} className="text-accent" />}
                </DialogTitle>
                <DialogDescription className="text-secondary">{selectedHouse.theme}</DialogDescription>
              </DialogHeader>
              <div className="space-y-6 pt-4">
                <div className="p-4 rounded-lg bg-accent/5 border border-accent/20">
                  <h4 className="text-foreground mb-2">Signo na Cúspide</h4>
                  <p className="text-secondary">{selectedHouse.cuspSign}</p>
                </div>

                {selectedHouse.planetsInHouse.length > 0 && (
                  <div className="p-4 rounded-lg bg-accent/5 border border-accent/20">
                    <h4 className="text-foreground mb-3">Planetas nesta Casa</h4>
                    <div className="space-y-2">
                      {selectedHouse.planetsInHouse.map((planetName) => {
                        const planet = planetaryData.find((p) => p.name === planetName);
                        return planet ? (
                          <div key={planetName} className="flex items-center gap-2 hover:bg-accent/10 p-2 rounded-lg transition-all duration-200 cursor-pointer group/planet">
                            <planet.icon size={20} className="text-accent group-hover/planet:scale-125 group-hover/planet:rotate-12 transition-all duration-200" />
                            <span className="text-foreground group-hover/planet:text-accent transition-colors">{planetName}</span>
                            <span className="text-secondary group-hover/planet:text-foreground transition-colors">em {planet.sign}</span>
                          </div>
                        ) : null;
                      })}
                    </div>
                  </div>
                )}

                <div>
                  <h4 className="text-foreground mb-3">Interpretação</h4>
                  <p className="text-secondary leading-relaxed">
                    {selectedHouse.interpretation}
                  </p>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Elements and Modalities Detail Modal */}
      <Dialog open={showElementsModal} onOpenChange={setShowElementsModal}>
        <DialogContent className="max-w-3xl bg-card backdrop-blur-md border border-border max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-accent flex items-center gap-3">
              <UIIcons.Star size={20} className="text-accent" />
              <span>Elementos e Modalidades na Sua Vida</span>
            </DialogTitle>
            <DialogDescription className="text-secondary">
              Entenda como os elementos e modalidades influenciam sua personalidade e comportamento
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6 pt-4">
            {loadingElementsInterpretation ? (
              <div className="flex items-center justify-center py-8">
                <div className="flex flex-col items-center gap-3">
                  <div className="w-8 h-8 border-4 border-accent/20 border-t-accent rounded-full animate-spin"></div>
                  <p className="text-secondary">Buscando informações na base de conhecimento...</p>
                </div>
              </div>
            ) : elementsInterpretation ? (
              <div className="prose prose-invert max-w-none">
                <div className="text-secondary leading-relaxed whitespace-pre-wrap space-y-4">
                  {elementsInterpretation.split('\n\n').map((paragraph, index) => (
                    paragraph.trim() && (
                      <p key={index} className="mb-4">
                        {paragraph.trim()}
                      </p>
                    )
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-secondary">Clique em "Leia mais" para carregar a interpretação.</p>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
      <EditUserModal
        open={showEditModal}
        onOpenChange={setShowEditModal}
        userData={currentUserData}
        onUpdate={handleUserUpdate}
        onLogout={handleLogout}
      />
      <ThemeCustomizationModal
        open={showThemeModal}
        onOpenChange={setShowThemeModal}
        onSave={handleThemeSave}
        onFontSizeChange={handleFontSizeChange}
        onTypographyChange={(newTypography) => {
          setTypography(newTypography);
          localStorage.setItem('astro-typography', JSON.stringify(newTypography));
        }}
        initialValue={customTheme}
        initialFontSize={fontSize}
        initialTypography={typography}
      />
      {isApplyingTheme && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="relative w-32 h-32">
            <div className="absolute inset-0 rounded-full border-4 border-white opacity-60 animate-ping"></div>
            <div
              className="absolute inset-4 rounded-full opacity-90 animate-pulse"
              style={{ backgroundColor: customTheme[currentTheme].accent }}
            ></div>
            <div
              className="absolute inset-10 rounded-full border-4 animate-spin"
              style={{ borderColor: customTheme[currentTheme].secondary }}
            ></div>
          </div>
          <p className="mt-4 text-white font-medium tracking-wide">Atualizando cores...</p>
        </div>
      )}
    </div>
  );
};

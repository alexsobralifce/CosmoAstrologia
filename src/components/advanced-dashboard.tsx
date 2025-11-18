import { useState } from 'react';
import { AstroCard } from './astro-card';
import { AstroButton } from './astro-button';
import { BirthChartWheel } from './birth-chart-wheel';
import { ElementChart } from './element-chart';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';
import { UIIcons } from './ui-icons';
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

interface AdvancedDashboardProps {
  userData: OnboardingData;
  onViewInterpretation: (topic: string) => void;
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

export const AdvancedDashboard = ({ userData, onViewInterpretation }: AdvancedDashboardProps) => {
  const [selectedHouse, setSelectedHouse] = useState<HouseData | null>(null);
  const [aspectFilter, setAspectFilter] = useState<'all' | 'harmonic' | 'dynamic' | 'neutral'>('all');

  // Mock astrological data
  const bigThree = {
    sun: { sign: 'Leão', icon: zodiacSigns[4].icon },
    moon: { sign: 'Touro', icon: zodiacSigns[1].icon },
    ascendant: { sign: 'Gêmeos', icon: zodiacSigns[2].icon },
  };

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

  const planetaryData: PlanetData[] = [
    {
      name: 'Sol',
      sign: 'Leão',
      house: 5,
      degree: 15,
      icon: planets[0].icon,
      signIcon: zodiacSigns[4].icon,
      interpretation: {
        inSign: 'Com o Sol em Leão, você possui uma personalidade magnética e criativa. Há um forte senso de identidade e orgulho pessoal. Você brilha quando está no centro das atenções e tem um talento natural para liderança. Sua autoexpressão é dramática e generosa, e você busca reconhecimento por suas realizações. A criatividade e o romance são áreas importantes da sua vida.',
        inHouse: 'O Sol na Casa 5 amplifica sua necessidade de autoexpressão criativa. Esta é a casa da criatividade, romance, filhos e prazer. Você encontra sua identidade através das atividades que lhe trazem alegria. Pode ter talento para as artes performáticas e adora estar no centro das atenções. Os relacionamentos românticos são importantes para seu senso de vitalidade.',
      },
    },
    {
      name: 'Lua',
      sign: 'Touro',
      house: 2,
      degree: 22,
      icon: planets[1].icon,
      signIcon: zodiacSigns[1].icon,
      interpretation: {
        inSign: 'A Lua em Touro traz estabilidade emocional e necessidade de segurança material. Você se sente confortável com rotinas e ambientes familiares. Há uma forte conexão com os prazeres sensoriais - boa comida, música, natureza. Suas emoções são estáveis e confiáveis, mas pode haver resistência a mudanças. Você valoriza a lealdade e o conforto emocional.',
        inHouse: 'Na Casa 2, a Lua reforça a necessidade de segurança material e financeira para seu bem-estar emocional. Você pode ter flutuações em suas finanças relacionadas ao seu estado emocional. Há um apego emocional a posses e objetos que trazem conforto. Seus valores pessoais estão profundamente conectados ao seu senso de identidade.',
      },
    },
    {
      name: 'Mercúrio',
      sign: 'Câncer',
      house: 4,
      degree: 8,
      icon: planets[2].icon,
      signIcon: zodiacSigns[3].icon,
      interpretation: {
        inSign: 'Mercúrio em Câncer pensa com o coração. Sua mente é intuitiva e absorve informações emocionalmente. Você tem excelente memória, especialmente para experiências emocionais. A comunicação é sensível e você pode perceber as necessidades não ditas dos outros. Pode haver tendência a deixar as emoções influenciarem a lógica.',
        inHouse: 'Na Casa 4, Mercúrio indica que sua mente está focada em questões familiares e domésticas. Você pode trabalhar de casa ou ter interesse em história familiar e genealogia. Conversas profundas acontecem em ambientes privados e seguros. Há um desejo de entender suas raízes e origem.',
      },
    },
    {
      name: 'Vênus',
      sign: 'Gêmeos',
      house: 3,
      degree: 28,
      icon: planets[3].icon,
      signIcon: zodiacSigns[2].icon,
      interpretation: {
        inSign: 'Vênus em Gêmeos busca variedade no amor e nas relações. Você valoriza a comunicação e a estimulação mental nos relacionamentos. Pode ter múltiplos interesses amorosos ou gostar de flertar. A conversa é uma forma de sedução. Você aprecia parceiros inteligentes e versáteis.',
        inHouse: 'Na Casa 3, Vênus traz harmonia à comunicação e às relações com irmãos e vizinhos. Você tem uma forma agradável de se expressar e pode ter talento para escrita ou oratória. Viagens curtas podem trazer encontros românticos.',
      },
    },
    {
      name: 'Marte',
      sign: 'Áries',
      house: 1,
      degree: 12,
      icon: planets[4].icon,
      signIcon: zodiacSigns[0].icon,
      interpretation: {
        inSign: 'Marte em Áries está em seu domicílio, conferindo energia assertiva e pioneira. Você age rapidamente e com coragem. Há uma forte necessidade de independência e liderança. Pode ser impaciente e impulsivo, mas sua iniciativa é admirável. Você é competitivo e gosta de desafios.',
        inHouse: 'Na Casa 1, Marte dá energia física e presença marcante. Você é assertivo e direto em sua abordagem à vida. Pode ter aparência atlética e gostar de atividades físicas. Há uma forte necessidade de agir de acordo com sua própria vontade.',
      },
    },
    {
      name: 'Júpiter',
      sign: 'Sagitário',
      house: 9,
      degree: 5,
      icon: planets[5].icon,
      signIcon: zodiacSigns[8].icon,
      interpretation: {
        inSign: 'Júpiter em Sagitário está em seu domicílio, trazendo otimismo filosófico e amor pela aventura. Você tem fé natural e acredita em possibilidades expansivas. Há interesse por culturas estrangeiras, filosofia e busca de significado. Você é generoso com seu conhecimento.',
        inHouse: 'Na Casa 9, Júpiter expande seu horizonte através de viagens, educação superior e filosofia. Você pode ter sorte em viagens ao exterior ou com pessoas estrangeiras. Há uma mente aberta e curiosa sobre diferentes culturas e crenças.',
      },
    },
    {
      name: 'Saturno',
      sign: 'Capricórnio',
      house: 10,
      degree: 18,
      icon: planets[6].icon,
      signIcon: zodiacSigns[9].icon,
      interpretation: {
        inSign: 'Saturno em Capricórnio está em seu domicílio, conferindo ambição e disciplina naturais. Você leva responsabilidades a sério e trabalha duro por suas metas. Há respeito pela tradição e autoridade. O sucesso vem através da persistência e paciência.',
        inHouse: 'Na Casa 10, Saturno indica que sua carreira é uma área de grande responsabilidade e realização. Você pode alcançar posições de autoridade através do trabalho árduo. Há uma necessidade de ser respeitado profissionalmente.',
      },
    },
  ];

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

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-[#1a1f4a] dark:to-[#1a1f4a] light:to-[#F0E6D2]">
      {/* Header */}
      <header className="border-b border-border/30 backdrop-blur-sm sticky top-0 z-10 bg-background/80">
        <div className="max-w-[1800px] mx-auto px-4 py-4 flex items-center justify-between">
          <h2 className="text-accent">Mapa Astral Completo</h2>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <button className="p-2 rounded-lg hover:bg-accent/10 transition-colors">
              <UIIcons.Bell size={20} className="text-secondary" />
            </button>
            <button className="p-2 rounded-lg hover:bg-accent/10 transition-colors">
              <UIIcons.Settings size={20} className="text-secondary" />
            </button>
            <button className="p-2 rounded-lg hover:bg-accent/10 transition-colors">
              <UIIcons.User size={20} className="text-accent" />
            </button>
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
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center">
                      <UIIcons.User size={24} className="text-accent" />
                    </div>
                    <div>
                      <h3 className="text-foreground">{userData.name}</h3>
                      <p className="text-sm text-secondary">
                        {userData.birthDate.toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                  <div className="pt-3 border-t border-border/30 space-y-1">
                    <p className="text-sm text-secondary flex items-center gap-2">
                      <UIIcons.Clock size={14} />
                      {userData.birthTime}
                    </p>
                    <p className="text-sm text-secondary flex items-center gap-2">
                      <UIIcons.MapPin size={14} />
                      {userData.birthPlace}
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
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-accent/10">
                    <bigThree.sun.icon size={32} className="text-accent" />
                    <div>
                      <p className="text-xs text-secondary">Sol</p>
                      <p className="text-foreground">{bigThree.sun.sign}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-accent/10">
                    <bigThree.moon.icon size={32} className="text-accent" />
                    <div>
                      <p className="text-xs text-secondary">Lua</p>
                      <p className="text-foreground">{bigThree.moon.sign}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-accent/10">
                    <bigThree.ascendant.icon size={32} className="text-accent" />
                    <div>
                      <p className="text-xs text-secondary">Ascendente</p>
                      <p className="text-foreground">{bigThree.ascendant.sign}</p>
                    </div>
                  </div>
                </div>
              </AstroCard>
            </div>
          </aside>

          {/* Right Content Area - Tabs */}
          <main className="lg:col-span-8 xl:col-span-9">
            <Tabs defaultValue="guide" className="space-y-6">
              <TabsList className="w-full justify-start bg-card/50 backdrop-blur-sm p-1 flex-wrap">
                <TabsTrigger value="guide" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent">
                  Seu Guia Pessoal
                </TabsTrigger>
                <TabsTrigger value="overview" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent">
                  Visão Geral
                </TabsTrigger>
                <TabsTrigger value="planets" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent">
                  Planetas
                </TabsTrigger>
                <TabsTrigger value="houses" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent">
                  Casas
                </TabsTrigger>
                <TabsTrigger value="aspects" className="data-[state=active]:bg-accent/20 data-[state=active]:text-accent">
                  Aspectos
                </TabsTrigger>
              </TabsList>

              {/* Tab 0: Seu Guia Pessoal */}
              <TabsContent value="guide" className="space-y-8">
                {/* Seção 1: Regente do Mapa 
                    - Mostra o planeta regente baseado no Ascendente
                    - ascendant: Signo do Ascendente do usuário
                    - ruler: Planeta regente desse ascendente
                    - rulerSign: Signo onde o regente está posicionado
                    - rulerHouse: Casa onde o regente está posicionado
                */}
                <ChartRulerSection
                  ascendant="Virgem"
                  ruler="Mercúrio"
                  rulerSign="Sagitário"
                  rulerHouse={3}
                />

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
                <AstroCard>
                  <h2 className="text-accent mb-6">Balanço de Elementos e Modalidades</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <ElementChart data={elementsData} title="Elementos" />
                    <ElementChart data={modalitiesData} title="Modalidades" />
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
                        <AccordionTrigger className="hover:no-underline">
                          <div className="flex items-center gap-4 w-full">
                            <planet.icon size={28} className="text-accent" />
                            <div className="flex-1 text-left">
                              <h3 className="text-foreground">{planet.name}</h3>
                              <p className="text-sm text-secondary">
                                em {planet.sign}, na Casa {planet.house} ({planet.degree}°)
                              </p>
                            </div>
                            <planet.signIcon size={24} className="text-accent opacity-50" />
                          </div>
                        </AccordionTrigger>
                        <AccordionContent className="pt-4 space-y-4">
                          <div className="space-y-3">
                            <div className="p-4 rounded-lg bg-accent/5 border border-accent/20">
                              <h4 className="text-foreground mb-2 flex items-center gap-2">
                                <planet.signIcon size={18} className="text-accent" />
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
                              <AccordionTrigger className="hover:no-underline">
                                <div className="flex items-center gap-4 w-full">
                                  {planet1 && (
                                    <planet1.icon size={24} className="text-accent" />
                                  )}
                                  <AspectIcon size={20} className={aspectColor} />
                                  {planet2 && (
                                    <planet2.icon size={24} className="text-accent" />
                                  )}
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
                                <div className="p-4 rounded-lg bg-accent/5 border border-accent/20">
                                  <p className="text-secondary leading-relaxed">
                                    {aspect.interpretation}
                                  </p>
                                  <p className="text-xs text-secondary/70 mt-3">
                                    Orb: {aspect.orb}°
                                  </p>
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
                          <div key={planetName} className="flex items-center gap-2">
                            <planet.icon size={20} className="text-accent" />
                            <span className="text-foreground">{planetName}</span>
                            <span className="text-secondary">em {planet.sign}</span>
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
    </div>
  );
};

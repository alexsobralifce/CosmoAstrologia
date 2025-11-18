import { useState, useEffect } from 'react';
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
import { Avatar, AvatarImage, AvatarFallback } from './ui/avatar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from './ui/dropdown-menu';
import { ThemeToggle } from './theme-toggle';
import { ChartRulerSection } from './chart-ruler-section';
import { DailyAdviceSection } from './daily-advice-section';
import { FutureTransitsSection } from './future-transits-section';
import { UserProfileModal } from './user-profile-modal';
import { useChart } from '../hooks/useChart';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';

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
  const [planetaryData, setPlanetaryData] = useState<PlanetData[]>([]);
  const [aspectsData, setAspectsData] = useState<AspectData[]>([]);
  const [loadingInterpretations, setLoadingInterpretations] = useState(false);
  const [showUserProfile, setShowUserProfile] = useState(false);

  const { chart, loading, error, dailyTransits, futureTransits } = useChart(userData);
  const { user, updateUser, logout } = useAuth();

  // Get icon helpers
  const getSignIcon = (signName: string) => {
    return zodiacSigns.find(z => z.name === signName)?.icon || zodiacSigns[0].icon;
  };

  const getPlanetIcon = (planetName: string) => {
    return planets.find(p => p.name === planetName)?.icon || planets[0].icon;
  };

  // Process chart data
  const bigThree = chart ? {
    sun: { sign: chart.big_three.sun, icon: getSignIcon(chart.big_three.sun) },
    moon: { sign: chart.big_three.moon, icon: getSignIcon(chart.big_three.moon) },
    ascendant: { sign: chart.big_three.ascendant, icon: getSignIcon(chart.big_three.ascendant) },
  } : {
    sun: { sign: '', icon: planets[0].icon },
    moon: { sign: '', icon: planets[1].icon },
    ascendant: { sign: '', icon: zodiacSigns[0].icon },
  };

  const elementsData = chart?.elements || [];
  const modalitiesData = chart?.modalities || [];

  // Load and process planetary data from chart
  useEffect(() => {
    if (!chart) return;

    const loadPlanetaryData = async () => {
      setLoadingInterpretations(true);
      try {
        const planetsToLoad = ['Sol', 'Lua', 'Mercúrio', 'Vênus', 'Marte', 'Júpiter', 'Saturno'];
        const loadedPlanets: PlanetData[] = [];

        for (const planet of chart.planets) {
          if (planetsToLoad.includes(planet.planet)) {
            try {
              const interpretation = await apiService.getPlanetInterpretation(
                planet.planet,
                planet.sign,
                planet.house,
                chart
              );

              loadedPlanets.push({
                name: planet.planet,
                sign: planet.sign,
                house: planet.house,
                degree: planet.degree,
                icon: getPlanetIcon(planet.planet),
                signIcon: getSignIcon(planet.sign),
                interpretation: {
                  inSign: interpretation.in_sign,
                  inHouse: interpretation.in_house,
                },
              });
            } catch (err) {
              console.warn(`Error loading interpretation for ${planet.planet}:`, err);
              // Use fallback
              loadedPlanets.push({
                name: planet.planet,
                sign: planet.sign,
                house: planet.house,
                degree: planet.degree,
                icon: getPlanetIcon(planet.planet),
                signIcon: getSignIcon(planet.sign),
                interpretation: {
                  inSign: `${planet.planet} em ${planet.sign}`,
                  inHouse: `${planet.planet} na Casa ${planet.house}`,
                },
              });
            }
          }
        }

        setPlanetaryData(loadedPlanets);
      } catch (err) {
        console.error('Error loading planetary data:', err);
      } finally {
        setLoadingInterpretations(false);
      }
    };

    loadPlanetaryData();
  }, [chart]);

  // Process aspects data from chart
  useEffect(() => {
    if (!chart || chart.aspects.length === 0) return;

    const loadAspectsData = async () => {
      try {
        const loadedAspects: AspectData[] = [];

        for (const aspect of chart.aspects.slice(0, 10)) { // Limit to first 10 to avoid too many API calls
          try {
            const interpretation = await apiService.getAspectInterpretation(
              aspect.planet1,
              aspect.planet2,
              aspect.type,
              aspect.orb,
              chart
            );

            loadedAspects.push({
              id: `${aspect.planet1}-${aspect.planet2}-${aspect.type}`,
              planet1: aspect.planet1,
              planet2: aspect.planet2,
              type: aspect.type as AspectType,
              orb: aspect.orb,
              interpretation: interpretation.interpretation,
              tags: interpretation.tags,
            });
          } catch (err) {
            console.warn(`Error loading aspect interpretation:`, err);
          }
        }

        setAspectsData(loadedAspects);
      } catch (err) {
        console.error('Error loading aspects data:', err);
      }
    };

    loadAspectsData();
  }, [chart]);

  // Process houses data from chart
  const housesData: HouseData[] = chart
    ? chart.houses.map((house) => {
        const themes: Record<number, string> = {
          1: 'Identidade e Aparência',
          2: 'Valores e Recursos',
          3: 'Comunicação e Aprendizado',
          4: 'Lar, Raízes e Família',
          5: 'Criatividade e Romance',
          6: 'Rotina e Saúde',
          7: 'Parcerias e Relacionamentos',
          8: 'Transformação e Recursos Compartilhados',
          9: 'Filosofia e Viagens',
          10: 'Carreira e Reputação',
          11: 'Amizades e Grupos',
          12: 'Espiritualidade e Inconsciente',
        };

        return {
          number: house.number,
          theme: themes[house.number] || `Casa ${house.number}`,
          cuspSign: house.cusp_sign,
          planetsInHouse: house.planets_in_house,
          interpretation: '', // Will be loaded on demand
          isAngular: [1, 4, 7, 10].includes(house.number),
        };
      })
    : [];

  // Process strengths and challenges from aspects
  const strengths = aspectsData
    .filter((a) => a.type === 'trine' || a.type === 'sextile')
    .slice(0, 2)
    .map((a) => ({
      title: `${a.planet1} em ${aspectData[a.type]?.name || a.type} com ${a.planet2}`,
      description: a.interpretation.substring(0, 150) + '...',
    }));

  const challenges = aspectsData
    .filter((a) => a.type === 'square' || a.type === 'opposition')
    .slice(0, 2)
    .map((a) => ({
      title: `${a.planet1} em ${aspectData[a.type]?.name || a.type} com ${a.planet2}`,
      description: a.interpretation.substring(0, 150) + '...',
    }));

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background via-background to-[#1a1f4a]">
        <AstroCard>
          <div className="text-center space-y-4">
            <UIIcons.Star size={48} className="text-accent mx-auto animate-pulse" />
            <h2 className="text-accent">Calculando seu mapa astral...</h2>
            <p className="text-secondary">Isso pode levar alguns segundos</p>
          </div>
        </AstroCard>
      </div>
    );
  }

  if (error || !chart) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background via-background to-[#1a1f4a]">
        <AstroCard>
          <div className="text-center space-y-4">
            <UIIcons.AlertCircle size={48} className="text-destructive mx-auto" />
            <h2 className="text-destructive">Erro ao carregar mapa</h2>
            <p className="text-secondary">{error || 'Não foi possível calcular o mapa astral'}</p>
            <AstroButton onClick={() => window.location.reload()}>Tentar Novamente</AstroButton>
          </div>
        </AstroCard>
      </div>
    );
  }

  const filteredAspects = aspectsData.filter((aspect) => {
    if (aspectFilter === 'all') return true;
    if (aspectFilter === 'harmonic') return aspect.type === 'trine' || aspect.type === 'sextile';
    if (aspectFilter === 'dynamic') return aspect.type === 'square' || aspect.type === 'opposition';
    if (aspectFilter === 'neutral') return aspect.type === 'conjunction';
    return true;
  });

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleLogout = async () => {
    await logout();
    window.location.href = '/';
  };

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
            {user && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="p-1 rounded-full hover:ring-2 hover:ring-accent/50 transition-all focus:outline-none focus:ring-2 focus:ring-accent/50">
                    <Avatar className="w-8 h-8 cursor-pointer">
                      {user.picture ? (
                        <AvatarImage src={user.picture} alt={user.name} />
                      ) : null}
                      <AvatarFallback className="bg-accent/20 text-accent text-sm">
                        {getInitials(user.name)}
                      </AvatarFallback>
                    </Avatar>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user.name}</p>
                      <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => setShowUserProfile(true)} className="cursor-pointer">
                    <UIIcons.User className="mr-2 h-4 w-4" />
                    <span>Perfil</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="cursor-pointer">
                    <UIIcons.Settings className="mr-2 h-4 w-4" />
                    <span>Configurações</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-red-500 focus:text-red-500">
                    <UIIcons.LogOut className="mr-2 h-4 w-4" />
                    <span>Sair</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>
      </header>

      {/* User Profile Modal */}
      {user && (
        <UserProfileModal
          open={showUserProfile}
          onOpenChange={setShowUserProfile}
          user={user}
          onUpdateUser={updateUser}
          onLogout={handleLogout}
        />
      )}

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
                  <BirthChartWheel chartData={chart} />
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
                {/* Seção 1: Regente do Mapa */}
                {chart.chart_ruler && (
                  <ChartRulerSection
                    ascendant={chart.chart_ruler.ascendant}
                    ruler={chart.chart_ruler.ruler}
                    rulerSign={chart.chart_ruler.ruler_sign}
                    rulerHouse={chart.chart_ruler.ruler_house}
                  />
                )}

                {/* Seção 2: Conselhos para Hoje */}
                {dailyTransits && (
                  <DailyAdviceSection
                    moonSign={dailyTransits.moon_sign}
                    moonHouse={dailyTransits.moon_house}
                    isMercuryRetrograde={dailyTransits.is_mercury_retrograde}
                    isMoonVoidOfCourse={dailyTransits.is_moon_void_of_course}
                    voidEndsAt={dailyTransits.void_ends_at || undefined}
                  />
                )}

                {/* Seção 3: Horizontes Futuros */}
                <FutureTransitsSection transits={futureTransits} />
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
                    {(planetaryData.length > 0 ? planetaryData : chart.planets.slice(0, 7).map(p => ({
                      name: p.planet,
                      sign: p.sign,
                      house: p.house,
                      degree: p.degree,
                      icon: getPlanetIcon(p.planet),
                      signIcon: getSignIcon(p.sign),
                      interpretation: { inSign: '', inHouse: '' }
                    }))).map((planet, index) => (
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

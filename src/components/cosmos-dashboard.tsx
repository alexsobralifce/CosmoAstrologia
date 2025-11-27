import { useState, useRef, useEffect } from 'react';
import { OnboardingData } from './onboarding';
import { UIIcons } from './ui-icons';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';
import { useTheme } from './theme-provider';
import { useLanguage } from '../i18n';
import { useInactivityTimeout } from '../hooks/useInactivityTimeout';
import { InactivityWarningModal } from './inactivity-warning-modal';
import { 
  OverviewSection, 
  PlanetsSection, 
  HousesSection, 
  Guide2026Section,
  AspectsSection,
  LunarNodesSection,
  BiorhythmsSection,
  SynastrySection
} from './dashboard-sections';
import { FullBirthChartSection } from './full-birth-chart-section';

// Componente de Menu de Configurações
interface SettingsMenuProps {
  onLogout: () => void;
}

const SettingsMenu = ({ onLogout }: SettingsMenuProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { theme, toggleTheme } = useTheme();
  const { language, toggleLanguage, t } = useLanguage();

  // Fechar menu ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={menuRef}>
      {/* Botão de Engrenagem */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`p-2 rounded-lg transition-colors ${
          isOpen ? 'bg-primary/20 text-primary' : 'hover:bg-muted text-foreground'
        }`}
        title={language === 'pt' ? 'Configurações' : 'Settings'}
      >
        <UIIcons.Settings size={20} className={isOpen ? 'animate-spin-slow' : ''} />
      </button>

      {/* Menu Dropdown */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-56 bg-card border border-border rounded-xl shadow-xl overflow-hidden animate-fadeIn z-50">
          {/* Header do Menu */}
          <div className="px-4 py-3 border-b border-border bg-muted/50">
            <p className="text-sm font-semibold text-foreground">
              {language === 'pt' ? 'Configurações' : 'Settings'}
            </p>
          </div>

          {/* Opções */}
          <div className="p-2">
            {/* Toggle de Tema */}
            <button
              onClick={() => {
                toggleTheme();
              }}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-muted transition-colors text-left"
            >
              {theme === 'dark' ? (
                <UIIcons.Sun size={18} className="text-amber-500" />
              ) : (
                <UIIcons.Moon size={18} className="text-indigo-500" />
              )}
              <span className="text-sm text-foreground flex-1">
                {language === 'pt' ? 'Modo Noturno' : 'Dark Mode'}
              </span>
              <div className={`w-9 h-5 rounded-full transition-colors ${
                theme === 'dark' ? 'bg-primary' : 'bg-muted-foreground/30'
              }`}>
                <div className={`w-4 h-4 rounded-full bg-white shadow-sm transition-transform mt-0.5 ${
                  theme === 'dark' ? 'translate-x-4 ml-0.5' : 'translate-x-0.5'
                }`} />
              </div>
            </button>

            {/* Toggle de Idioma */}
            <button
              onClick={() => {
                toggleLanguage();
              }}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-muted transition-colors text-left"
            >
              <span className="text-lg">{language === 'pt' ? '🇧🇷' : '🇺🇸'}</span>
              <span className="text-sm text-foreground flex-1">
                {language === 'pt' ? 'Idioma' : 'Language'}
              </span>
              <span className="text-xs font-medium text-muted-foreground px-2 py-1 bg-muted rounded">
                {language === 'pt' ? 'PT' : 'EN'}
              </span>
            </button>

            {/* Separador */}
            <div className="my-2 border-t border-border" />

            {/* Botão Sair */}
            <button
              onClick={() => {
                setIsOpen(false);
                onLogout();
              }}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-destructive/10 transition-colors text-left group"
            >
              <UIIcons.LogOut size={18} className="text-destructive" />
              <span className="text-sm text-destructive font-medium">
                {language === 'pt' ? 'Sair' : 'Logout'}
              </span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

interface CosmosDashboardProps {
  userData: OnboardingData;
  onViewInterpretation: (topic: string) => void;
  onLogout: () => void;
  onUserUpdate?: (data: OnboardingData) => void;
}

export const CosmosDashboard = ({ userData, onViewInterpretation, onLogout }: CosmosDashboardProps) => {
  const [activeSection, setActiveSection] = useState('inicio');
  const { language, t } = useLanguage();
  
  // Estado para modal de aviso de inatividade
  const [showInactivityWarning, setShowInactivityWarning] = useState(false);
  const [warningCountdown, setWarningCountdown] = useState(120); // 2 minutos em segundos

  // Sistema de timeout de inatividade
  useInactivityTimeout({
    timeout: 30 * 60 * 1000, // 30 minutos de inatividade
    warningTime: 2 * 60 * 1000, // Avisar 2 minutos antes
    onWarning: (remainingSeconds) => {
      setWarningCountdown(remainingSeconds);
      setShowInactivityWarning(true);
    },
    onTimeout: () => {
      console.log('[CosmosDashboard] Sessão expirada por inatividade');
      setShowInactivityWarning(false);
      onLogout();
    },
    enabled: true // Sempre ativo quando o dashboard está montado
  });

  // Handler para continuar conectado
  const handleContinueSession = () => {
    setShowInactivityWarning(false);
    // O hook já reseta o timer automaticamente ao detectar atividade
  };

  // Ícone do signo do usuário baseado no signo solar
  const userSunSign = userData.sunSign || 'Áries';
  const UserZodiacIcon = zodiacSigns.find(z => z.name === userSunSign)?.icon || zodiacSigns[0].icon;

  // Menu items para sidebar com traduções
  const menuItems = [
    { id: 'inicio', label: t('menu', 'home'), icon: UIIcons.Home },
    { id: 'mapa-completo', label: t('menu', 'fullChart'), icon: UIIcons.BookOpen, badge: t('menu', 'new'), highlight: true },
    { id: 'visao-geral', label: t('menu', 'overview'), icon: UIIcons.Eye },
    { id: 'biorritmos', label: t('menu', 'biorhythms'), icon: UIIcons.Activity },
    { id: 'sinastria', label: t('menu', 'synastry'), icon: UIIcons.Heart },
    { id: 'guia-2026', label: t('menu', 'guide2026'), icon: UIIcons.Calendar },
    { id: 'nodos-lunares', label: t('menu', 'lunarNodes'), icon: UIIcons.Moon },
    { id: 'planetas', label: t('menu', 'planets'), icon: UIIcons.Star },
    { id: 'casas', label: t('menu', 'houses'), icon: UIIcons.Home },
    { id: 'aspectos', label: t('menu', 'aspects'), icon: UIIcons.Sparkles },
  ];

  // Dados mockados para previsões com traduções
  const insights = [
    {
      id: 'energia',
      title: t('insights', 'dayEnergy'),
      value: '8.5/10',
      description: t('insights', 'favorableMoment'),
      icon: UIIcons.Zap,
      color: 'orange',
      bgColor: 'bg-orange-100 dark:bg-orange-500/15',
      textColor: 'text-orange-700 dark:text-orange-300',
    },
    {
      id: 'signo',
      title: t('insights', 'daySign'),
      value: language === 'pt' ? 'Touro' : 'Taurus',
      description: t('insights', 'focusStability'),
      icon: zodiacSigns[1].icon,
      color: 'emerald',
      bgColor: 'bg-emerald-100 dark:bg-emerald-500/15',
      textColor: 'text-emerald-700 dark:text-emerald-300',
    },
    {
      id: 'fase-lunar',
      title: t('insights', 'lunarPhase'),
      value: language === 'pt' ? 'Crescente' : 'Waxing',
      description: t('insights', 'expansionGrowth'),
      icon: UIIcons.Moon,
      color: 'amber',
      bgColor: 'bg-amber-100 dark:bg-amber-500/15',
      textColor: 'text-amber-700 dark:text-amber-300',
    },
    {
      id: 'elemento',
      title: t('insights', 'element'),
      value: t('elements', 'earth'),
      description: t('insights', 'practicalityRealization'),
      icon: UIIcons.Globe,
      color: 'emerald',
      bgColor: 'bg-emerald-100 dark:bg-emerald-500/15',
      textColor: 'text-emerald-700 dark:text-emerald-300',
    },
  ];

  const areas = [
    {
      id: 'amor',
      title: t('areas', 'loveRelationships'),
      intensity: 9,
      description: t('areas', 'venusHarmony'),
      icon: UIIcons.Heart,
      color: 'bg-red-500',
      textColor: 'text-red-700 dark:text-red-300',
      bgColor: 'bg-red-100 dark:bg-red-500/15',
    },
    {
      id: 'carreira',
      title: t('areas', 'careerFinances'),
      intensity: 7,
      description: t('areas', 'jupiterOpportunities'),
      icon: UIIcons.Briefcase,
      color: 'bg-amber-500',
      textColor: 'text-amber-700 dark:text-amber-300',
      bgColor: 'bg-amber-100 dark:bg-amber-500/15',
    },
    {
      id: 'saude',
      title: t('areas', 'healthWellbeing'),
      intensity: 6,
      description: t('areas', 'marsEnergy'),
      icon: UIIcons.Activity,
      color: 'bg-emerald-500',
      textColor: 'text-emerald-700 dark:text-emerald-300',
      bgColor: 'bg-emerald-100 dark:bg-emerald-500/15',
    },
    {
      id: 'familia',
      title: t('areas', 'familyFriends'),
      intensity: 8,
      description: t('areas', 'moonRelations'),
      icon: UIIcons.Users,
      color: 'bg-purple-500',
      textColor: 'text-purple-700 dark:text-purple-300',
      bgColor: 'bg-purple-100 dark:bg-purple-500/15',
    },
  ];

  const planetaryPositions = [
    { 
      planet: t('planets', 'mercury'), 
      sign: language === 'pt' ? 'Capricórnio' : 'Capricorn', 
      status: t('planets', 'retrograde'), 
      icon: planets[2].icon, 
      statusColor: 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300' 
    },
    { 
      planet: t('planets', 'venus'), 
      sign: language === 'pt' ? 'Escorpião' : 'Scorpio', 
      status: t('planets', 'direct'), 
      icon: planets[3].icon, 
      statusColor: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300' 
    },
    { 
      planet: t('planets', 'mars'), 
      sign: language === 'pt' ? 'Leão' : 'Leo', 
      status: t('planets', 'direct'), 
      icon: planets[4].icon, 
      statusColor: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300' 
    },
    { 
      planet: t('planets', 'jupiter'), 
      sign: language === 'pt' ? 'Gêmeos' : 'Gemini', 
      status: t('planets', 'direct'), 
      icon: planets[5].icon, 
      statusColor: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300' 
    },
  ];

  const compatibility = [
    { name: 'João Pedro', sign: language === 'pt' ? 'Leão' : 'Leo', compatibility: 85, avatar: 'JP', color: 'bg-orange-500' },
    { name: 'Ana Costa', sign: 'Libra', compatibility: 92, avatar: 'AC', color: 'bg-pink-500' },
    { name: 'Carlos Mendes', sign: language === 'pt' ? 'Sagitário' : 'Sagittarius', compatibility: 78, avatar: 'CM', color: 'bg-purple-500' },
  ];

  // Dados do calendário (mini calendário novembro 2025)
  const calendarDays = [
    { day: 1, events: false },
    { day: 2, events: false },
    { day: 3, events: false },
    { day: 4, events: false },
    { day: 5, events: false },
    { day: 6, events: false },
    { day: 7, events: false },
    { day: 8, events: false },
    { day: 9, events: false },
    { day: 10, events: false },
    { day: 11, events: false },
    { day: 12, events: false },
    { day: 13, events: false },
    { day: 14, events: false },
    { day: 15, events: false },
    { day: 16, events: false },
    { day: 17, events: false },
    { day: 18, events: false },
    { day: 19, events: false },
    { day: 20, events: false },
    { day: 21, events: false },
    { day: 22, events: false },
    { day: 23, events: false },
    { day: 24, events: true, current: true },  // Dia atual
    { day: 25, events: false },
    { day: 26, events: false },
    { day: 27, events: false },
    { day: 28, events: false },
    { day: 29, events: false },
    { day: 30, events: false },
  ];

  // Dias da semana traduzidos
  const weekDays = language === 'pt' 
    ? ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'] 
    : ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

  // Textos traduzidos
  const texts = {
    moonIn: language === 'pt' ? 'Lua em' : 'Moon in',
    asc: language === 'pt' ? 'Asc.' : 'Asc.',
    november: language === 'pt' ? 'Novembro' : 'November',
    of: language === 'pt' ? 'de' : '',
    fullMoon: t('alerts', 'fullMoon'),
    mercuryDirect: t('alerts', 'mercuryDirect'),
    searchPlaceholder: t('dashboard', 'searchPlaceholder'),
    yourCelestialGuide: t('dashboard', 'yourCelestialGuide'),
    welcome: t('dashboard', 'welcome'),
    astralForecast: t('dashboard', 'astralForecast'),
    todayInsights: t('dashboard', 'todayInsights'),
    forecastByArea: t('dashboard', 'forecastByArea'),
    planetaryPositions: t('dashboard', 'planetaryPositions'),
    compatibility: t('dashboard', 'compatibility'),
    intensity: t('insights', 'intensity'),
    mercuryRetrograde: t('alerts', 'mercuryRetrograde'),
    searchPerson: t('compatibilitySection', 'searchPerson'),
    closePeople: t('compatibilitySection', 'closePeople'),
    affinity: t('compatibilitySection', 'affinity'),
    viewAll: t('compatibilitySection', 'viewAll'),
    footer: t('footer', 'copyright'),
    monday: language === 'pt' ? 'Segunda' : 'Monday',
    heroText: language === 'pt' 
      ? 'Hoje os astros alinham-se para trazer clareza aos seus caminhos. Mercúrio retrógrado em Capricórnio convida à reflexão profunda sobre suas metas e ambições.'
      : 'Today the stars align to bring clarity to your paths. Mercury retrograde in Capricorn invites deep reflection on your goals and ambitions.',
    waxingMoonIn: language === 'pt' ? 'Lua Crescente em Aquário' : 'Waxing Moon in Aquarius',
  };

  return (
    <div className="min-h-screen bg-background">
      {/* ===== SIDEBAR FIXA À ESQUERDA ===== */}
      <aside className="w-64 bg-sidebar border-r border-sidebar-border fixed left-0 top-0 h-screen overflow-y-auto flex flex-col z-50">
        {/* Perfil do Usuário - Centralizado */}
        <div className="p-6 border-b border-sidebar-border">
          <div className="flex flex-col items-center text-center">
            {/* Avatar centralizado */}
            <div className="relative mb-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center border-2 border-primary/30">
                <UIIcons.User size={40} className="text-primary" />
              </div>
              {/* Status indicator */}
              <div className="absolute bottom-0 right-0 w-5 h-5 bg-emerald-500 rounded-full border-2 border-sidebar"></div>
            </div>
            {/* Nome centralizado */}
            <h3 className="font-serif text-lg text-sidebar-foreground font-semibold">{userData.name || 'Maria Silva'}</h3>
            {/* Info do signo */}
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground mt-1">
              <UserZodiacIcon size={16} className="text-primary" />
              <span>{texts.moonIn} {userData.moonSign || 'N/A'} • {texts.asc} {userData.ascendant || 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* Navegação */}
        <nav className="flex-1 py-4 px-3">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all mb-1 ${
                activeSection === item.id
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
              }`}
            >
              <item.icon size={20} />
              <span className="text-sm font-medium">{item.label}</span>
              {item.badge && (
                <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-orange text-primary-foreground">
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </nav>

        {/* Mini Calendário */}
        <div className="p-4 border-t border-sidebar-border">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-semibold text-sidebar-foreground">
              {texts.november} {texts.of} 2025
            </h4>
            <div className="flex gap-1">
              <button className="p-1 hover:bg-sidebar-accent rounded">
                <UIIcons.ChevronLeft size={16} className="text-muted-foreground" />
              </button>
              <button className="p-1 hover:bg-sidebar-accent rounded">
                <UIIcons.ChevronRight size={16} className="text-muted-foreground" />
              </button>
            </div>
          </div>
          
          {/* Grid calendário */}
          <div className="grid grid-cols-7 gap-1 text-center text-xs">
            {weekDays.map((day, i) => (
              <div key={i} className="text-muted-foreground font-medium py-1">{day}</div>
            ))}
            {calendarDays.map((dayData, i) => (
              <div
                key={i}
                className={`py-1 rounded relative ${
                  dayData.current
                    ? 'bg-primary text-primary-foreground font-bold'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent cursor-pointer'
                }`}
              >
                {dayData.day}
                {dayData.events && !dayData.current && (
                  <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-orange rounded-full"></div>
                )}
              </div>
            ))}
          </div>

          {/* Eventos lunares */}
          <div className="mt-4 space-y-2 text-xs">
            <div className="flex items-center gap-2 text-muted-foreground">
              <UIIcons.Moon size={12} className="text-primary" />
              <span>{texts.fullMoon} (15)</span>
            </div>
            <div className="flex items-center gap-2 text-muted-foreground">
              <UIIcons.Moon size={12} className="text-destructive" />
              <span>{texts.mercuryDirect} (28)</span>
            </div>
          </div>
        </div>
      </aside>

      {/* ===== ÁREA PRINCIPAL (com margin-left para sidebar) ===== */}
      <div className="ml-64 min-h-screen">
        {/* ===== HEADER SUPERIOR ===== */}
        <header className="h-20 bg-background border-b border-border sticky top-0 z-40 backdrop-blur-sm bg-background/80">
          <div className="h-full max-w-[1800px] mx-auto px-8 flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-primary flex items-center justify-center rotate-3 shadow-lg">
                <UIIcons.Sparkles size={24} className="text-foreground" />
              </div>
              <div>
                <h1 className="font-serif text-xl font-bold text-foreground">Cosmos Astral</h1>
                <p className="text-xs text-muted-foreground">{texts.yourCelestialGuide}</p>
              </div>
            </div>

            {/* Barra de Busca */}
            <div className="flex-1 max-w-2xl mx-8">
              <div className="search-bar-header">
                <UIIcons.Search size={18} className="text-muted-foreground flex-shrink-0" />
                <input
                  type="text"
                  placeholder={texts.searchPlaceholder}
                />
              </div>
            </div>

            {/* Ações à direita */}
            <div className="flex items-center gap-2">
              {/* Notificações */}
              <button className="relative p-2 rounded-lg hover:bg-muted transition-colors">
                <UIIcons.Bell size={20} className="text-foreground" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full"></span>
              </button>

              {/* Menu de Configurações */}
              <SettingsMenu onLogout={onLogout} />
            </div>
          </div>
        </header>

        {/* ===== CONTEÚDO PRINCIPAL ===== */}
        <main className="p-8 max-w-[1800px] mx-auto">
          {/* Renderização condicional baseada na seção ativa */}
          {activeSection === 'mapa-completo' ? (
            <FullBirthChartSection userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : activeSection === 'visao-geral' ? (
            <OverviewSection userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : activeSection === 'planetas' ? (
            <PlanetsSection userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : activeSection === 'casas' ? (
            <HousesSection userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : activeSection === 'guia-2026' ? (
            <Guide2026Section userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : activeSection === 'aspectos' ? (
            <AspectsSection userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : activeSection === 'nodos-lunares' ? (
            <LunarNodesSection userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : activeSection === 'biorritmos' ? (
            <BiorhythmsSection userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : activeSection === 'sinastria' ? (
            <SynastrySection userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : (
          <>
          {/* ===== HERO SECTION ===== */}
          <div className="mb-8 bg-gradient-to-br from-[#2D324D] to-[#1F2337] rounded-3xl p-8 relative overflow-hidden shadow-xl">
            {/* Orbes de fundo */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue/20 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple/20 rounded-full blur-3xl"></div>
            
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-3">
                <UIIcons.Sparkles size={20} className="text-purple-400" />
                <span className="text-sm text-purple-300 font-medium">{texts.astralForecast}</span>
              </div>
              <h2 className="font-serif text-4xl font-bold text-white mb-4">
                {texts.welcome}
              </h2>
              <p className="text-gray-200 text-lg max-w-2xl">
                {texts.heroText}
              </p>
              <div className="flex gap-4 mt-6">
                <div className="px-4 py-2 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20">
                  <UIIcons.Calendar size={16} className="inline mr-2 text-white" />
                  <span className="text-white text-sm">{texts.monday}, 24 {texts.of} {texts.november}</span>
                </div>
                <div className="px-4 py-2 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20">
                  <UIIcons.Moon size={16} className="inline mr-2 text-amber-400" />
                  <span className="text-white text-sm">{texts.waxingMoonIn}</span>
                </div>
              </div>
            </div>
          </div>

          {/* ===== INSIGHTS DE HOJE (GRID 4 CARDS) ===== */}
          <div className="mb-8">
            <h3 className="font-serif text-2xl font-bold text-foreground mb-4">{texts.todayInsights}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {insights.map((insight) => (
                <div
                  key={insight.id}
                  className={`${insight.bgColor} rounded-xl p-6 border border-border hover:border-primary/30 transition-all cursor-pointer group`}
                >
                  <div className={`w-12 h-12 rounded-lg ${insight.bgColor} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <insight.icon size={24} className={insight.textColor} />
                  </div>
                  <h4 className="text-sm font-medium text-foreground mb-1">{insight.title}</h4>
                  <p className={`text-2xl font-bold ${insight.textColor} mb-2`}>{insight.value}</p>
                  <p className="text-xs text-foreground dark:text-gray-300">{insight.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* ===== PREVISÕES POR ÁREA ===== */}
          <div className="mb-8">
            <h3 className="font-serif text-2xl font-bold text-foreground mb-4">{texts.forecastByArea}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {areas.map((area) => (
                <div
                  key={area.id}
                  className={`${area.bgColor} rounded-xl p-6 border border-border hover:border-primary/30 transition-all cursor-pointer`}
                  onClick={() => onViewInterpretation(area.id)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg ${area.bgColor} flex items-center justify-center`}>
                        <area.icon size={20} className={area.textColor} />
                      </div>
                      <h4 className={`font-semibold ${area.textColor}`}>{area.title}</h4>
                    </div>
                    <div className="text-right">
                      <span className="text-sm text-foreground dark:text-gray-400">{texts.intensity}</span>
                      <p className={`text-xl font-bold ${area.textColor}`}>{area.intensity}/10</p>
                    </div>
                  </div>
                  <p className="text-sm text-foreground dark:text-gray-300 mb-4">{area.description}</p>
                  {/* Barra de progresso */}
                  <div className="h-1.5 bg-white/30 dark:bg-black/20 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${area.color} rounded-full transition-all duration-500`}
                      style={{ width: `${area.intensity * 10}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ===== GRID INFERIOR: POSIÇÕES PLANETÁRIAS + COMPATIBILIDADE ===== */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Posições Planetárias */}
            <div className="bg-card rounded-xl p-6 border border-border">
              <h3 className="font-serif text-xl font-bold text-foreground mb-6">{texts.planetaryPositions}</h3>
              <div className="space-y-4">
                {planetaryPositions.map((position, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <position.icon size={24} className="text-primary" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-foreground">{position.planet}</p>
                      <p className="text-sm text-muted-foreground">{t('planets', 'in')} {position.sign}</p>
                    </div>
                    <span className={`text-xs px-3 py-1 rounded-full font-medium ${position.statusColor}`}>
                      {position.status}
                    </span>
                  </div>
                ))}
              </div>

              {/* Alerta Mercúrio Retrógrado */}
              <div className="mt-6 p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
                <div className="flex items-start gap-3">
                  <UIIcons.AlertCircle size={20} className="text-amber-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {texts.mercuryRetrograde}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Compatibilidade */}
            <div className="bg-card rounded-xl p-6 border border-border">
              <h3 className="font-serif text-xl font-bold text-foreground mb-6">{texts.compatibility}</h3>
              
              {/* Barra de busca */}
              <div className="search-bar-small mb-6">
                <UIIcons.Search size={16} className="text-muted-foreground flex-shrink-0" />
                <input
                  type="text"
                  placeholder={texts.searchPerson}
                />
              </div>

              <p className="text-xs text-muted-foreground mb-4 flex items-center gap-2">
                <UIIcons.Users size={14} />
                {texts.closePeople}
              </p>

              <div className="space-y-3">
                {compatibility.map((person, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full ${person.color} flex items-center justify-center text-primary-foreground font-semibold text-sm`}>
                        {person.avatar}
                      </div>
                      <div>
                        <p className="font-medium text-foreground text-sm">{person.name}</p>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <UIIcons.Star size={12} />
                          <span>{person.sign}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-foreground">{person.compatibility}%</p>
                      <p className="text-xs text-muted-foreground">{texts.affinity}</p>
                    </div>
                  </div>
                ))}
              </div>

              <button className="w-full mt-6 py-3 rounded-lg bg-orange text-primary-foreground font-medium hover:bg-orange/90 transition-colors">
                {texts.viewAll}
              </button>
            </div>
          </div>

          {/* Footer */}
          <footer className="mt-12 text-center text-sm text-muted-foreground border-t border-border pt-6">
            <p>{texts.footer}</p>
          </footer>
          </>
          )}
        </main>
      </div>

      {/* Modal de Aviso de Inatividade */}
      <InactivityWarningModal
        isOpen={showInactivityWarning}
        remainingSeconds={warningCountdown}
        onContinue={handleContinueSession}
        onLogout={onLogout}
      />
    </div>
  );
};

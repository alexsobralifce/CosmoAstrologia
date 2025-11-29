import React, { useState, useRef, useEffect } from 'react';
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
  SynastrySection,
  SolarReturnSection
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
    <div className="dashboard-settings-menu" ref={menuRef}>
      {/* Botão de Engrenagem */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`dashboard-settings-button ${isOpen ? 'active' : ''}`}
        title={language === 'pt' ? 'Configurações' : 'Settings'}
      >
        <UIIcons.Settings size={20} className={`dashboard-settings-icon ${isOpen ? 'animate-spin-slow' : ''}`} style={{ color: 'inherit' }} />
      </button>

      {/* Menu Dropdown */}
      {isOpen && (
        <div className="dashboard-settings-dropdown">
          {/* Header do Menu */}
          <div className="dashboard-settings-header">
            <p className="dashboard-settings-header-text">
              {language === 'pt' ? 'Configurações' : 'Settings'}
            </p>
          </div>

          {/* Opções */}
          <div className="dashboard-settings-options">
            {/* Toggle de Tema */}
            <button
              onClick={() => {
                toggleTheme();
              }}
              className="dashboard-settings-option"
            >
              <span className="dashboard-settings-option-icon">
              {theme === 'dark' ? (
                <UIIcons.Sun size={18} className="text-amber-500" />
              ) : (
                <UIIcons.Moon size={18} className="text-indigo-500" />
              )}
              </span>
              <span className="dashboard-settings-option-text">
                {language === 'pt' ? 'Modo Noturno' : 'Dark Mode'}
              </span>
              <div className={`dashboard-settings-toggle ${theme === 'dark' ? 'active' : 'inactive'}`}>
                <div className="dashboard-settings-toggle-thumb" />
              </div>
            </button>

            {/* Toggle de Idioma */}
            <button
              onClick={() => {
                toggleLanguage();
              }}
              className="dashboard-settings-option"
            >
              <span className="dashboard-settings-option-icon">
                <span style={{ fontSize: '1.125rem' }}>{language === 'pt' ? '🇧🇷' : '🇺🇸'}</span>
              </span>
              <span className="dashboard-settings-option-text">
                {language === 'pt' ? 'Idioma' : 'Language'}
              </span>
              <span className="dashboard-settings-option-badge">
                {language === 'pt' ? 'PT' : 'EN'}
              </span>
            </button>

            {/* Separador */}
            <div className="dashboard-settings-separator" />

            {/* Botão Sair */}
            <button
              onClick={() => {
                setIsOpen(false);
                onLogout();
              }}
              className="dashboard-settings-option dashboard-settings-option-danger"
            >
              <span className="dashboard-settings-option-icon">
              <UIIcons.LogOut size={18} className="text-destructive" />
              </span>
              <span className="dashboard-settings-option-text" style={{ color: 'hsl(var(--destructive))', fontWeight: '500' }}>
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const { language, t } = useLanguage();
  const { theme } = useTheme(); // Adicionar acesso ao tema
  
  // Estado para calendário
  const [currentMonth, setCurrentMonth] = useState(new Date().getMonth());
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  
  // Estado para notificações
  const [showNotifications, setShowNotifications] = useState(false);
  
  // Estado para modal de aviso de inatividade
  const [showInactivityWarning, setShowInactivityWarning] = useState(false);
  const [warningCountdown, setWarningCountdown] = useState(60); // 1 minuto em segundos

  // Sistema de timeout de inatividade
  // Timeout de 10 minutos de inatividade com aviso de 1 minuto antes
  useInactivityTimeout({
    timeout: 10 * 60 * 1000, // 10 minutos de inatividade total
    warningTime: 1 * 60 * 1000, // Avisar 1 minuto antes (9 minutos de inatividade)
    onWarning: (remainingSeconds) => {
      console.log(`[CosmosDashboard] Aviso de inatividade: ${remainingSeconds} segundos restantes`);
      setWarningCountdown(remainingSeconds);
      setShowInactivityWarning(true);
    },
    onTimeout: () => {
      console.log('[CosmosDashboard] Sessão expirada por inatividade - fazendo logout');
      setShowInactivityWarning(false);
      onLogout();
    },
    enabled: true // Sempre ativo quando o dashboard está montado
  });

  // Handler para continuar conectado
  const handleContinueSession = () => {
    console.log('[CosmosDashboard] Usuário escolheu continuar conectado - resetando timer');
    setShowInactivityWarning(false);
    // O hook já reseta o timer automaticamente ao detectar atividade
    // Ao clicar no botão, o evento de click já dispara o reset do timer
  };

  // Handlers para calendário
  const handlePreviousMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const handleNextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  // Handler para notificações
  const handleNotificationsClick = () => {
    setShowNotifications(!showNotifications);
    // TODO: Implementar painel de notificações
    console.log('Notificações:', showNotifications ? 'fechando' : 'abrindo');
  };

  // Handler para ver todos (compatibilidade)
  const handleViewAllCompatibility = () => {
    // TODO: Implementar navegação para página completa de compatibilidade
    console.log('Ver todos os contatos de compatibilidade');
    // Por enquanto, apenas log. Pode ser implementado como navegação para uma seção específica
  };

  // Ícone do signo do usuário baseado no signo solar
  const userSunSign = userData.sunSign || 'Áries';
  const UserZodiacIcon = zodiacSigns.find(z => z.name === userSunSign)?.icon || zodiacSigns[0].icon;

  // Menu items para sidebar com traduções
  const menuItems = [
    { id: 'inicio', label: t('menu', 'home'), icon: UIIcons.Home },
    { id: 'mapa-completo', label: t('menu', 'fullChart'), icon: UIIcons.BookOpen, badge: t('menu', 'new'), highlight: true },
    { id: 'visao-geral', label: t('menu', 'overview'), icon: UIIcons.Eye },
    { id: 'revolucao-solar', label: t('menu', 'solarReturn'), icon: UIIcons.Sun },
    { id: 'biorritmos', label: t('menu', 'biorhythms'), icon: UIIcons.Activity },
    { id: 'sinastria', label: t('menu', 'synastry'), icon: UIIcons.Heart },
    { id: 'guia-2026', label: t('menu', 'guide2026'), icon: UIIcons.Calendar },
    { id: 'nodos-lunares', label: t('menu', 'lunarNodes'), icon: UIIcons.Moon },
    { id: 'planetas', label: t('menu', 'planets'), icon: UIIcons.Star },
    { id: 'casas', label: t('menu', 'houses'), icon: UIIcons.Home },
    { id: 'aspectos', label: t('menu', 'aspects'), icon: UIIcons.Sparkles },
  ];

  // Dados mockados para previsões com traduções
  // isDark: true = fundo escuro (texto branco), false = fundo claro (texto preto)
  const insights = [
    {
      id: 'energia',
      title: t('insights', 'dayEnergy'),
      value: '8.5/10',
      description: t('insights', 'favorableMoment'),
      icon: UIIcons.Zap,
      bgColor: 'bg-orange-50 dark:bg-orange-950/50 border-orange-200 dark:border-orange-800',
      accentColor: '#EA580C', // orange-600
      iconBg: 'bg-orange-100 dark:bg-orange-900/50',
    },
    {
      id: 'signo',
      title: t('insights', 'daySign'),
      value: language === 'pt' ? 'Touro' : 'Taurus',
      description: t('insights', 'focusStability'),
      icon: zodiacSigns[1].icon,
      bgColor: 'bg-emerald-50 dark:bg-emerald-950/50 border-emerald-200 dark:border-emerald-800',
      accentColor: '#059669', // emerald-600
      iconBg: 'bg-emerald-100 dark:bg-emerald-900/50',
    },
    {
      id: 'fase-lunar',
      title: t('insights', 'lunarPhase'),
      value: language === 'pt' ? 'Crescente' : 'Waxing',
      description: t('insights', 'expansionGrowth'),
      icon: UIIcons.Moon,
      bgColor: 'bg-indigo-50 dark:bg-indigo-950/50 border-indigo-200 dark:border-indigo-800',
      accentColor: '#4F46E5', // indigo-600
      iconBg: 'bg-indigo-100 dark:bg-indigo-900/50',
    },
    {
      id: 'elemento',
      title: t('insights', 'element'),
      value: t('elements', 'earth'),
      description: t('insights', 'practicalityRealization'),
      icon: UIIcons.Globe,
      bgColor: 'bg-teal-50 dark:bg-teal-950/50 border-teal-200 dark:border-teal-800',
      accentColor: '#0D9488', // teal-600
      iconBg: 'bg-teal-100 dark:bg-teal-900/50',
    },
  ];

  // isDark: true = fundo escuro (texto branco), false = fundo claro (texto preto)
  const areas = [
    {
      id: 'amor',
      title: t('areas', 'loveRelationships'),
      intensity: 9,
      description: t('areas', 'venusHarmony'),
      icon: UIIcons.Heart,
      color: 'bg-red-500',
      accentColor: '#DC2626', // red-600
      bgColor: 'bg-red-50 dark:bg-red-950/50 border-red-200 dark:border-red-800',
      iconBg: 'bg-red-100 dark:bg-red-900/50',
    },
    {
      id: 'carreira',
      title: t('areas', 'careerFinances'),
      intensity: 7,
      description: t('areas', 'jupiterOpportunities'),
      icon: UIIcons.Briefcase,
      color: 'bg-amber-500',
      accentColor: '#D97706', // amber-600
      bgColor: 'bg-amber-50 dark:bg-amber-950/50 border-amber-200 dark:border-amber-800',
      iconBg: 'bg-amber-100 dark:bg-amber-900/50',
    },
    {
      id: 'saude',
      title: t('areas', 'healthWellbeing'),
      intensity: 6,
      description: t('areas', 'marsEnergy'),
      icon: UIIcons.Activity,
      color: 'bg-emerald-500',
      accentColor: '#059669', // emerald-600
      bgColor: 'bg-emerald-50 dark:bg-emerald-950/50 border-emerald-200 dark:border-emerald-800',
      iconBg: 'bg-emerald-100 dark:bg-emerald-900/50',
    },
    {
      id: 'familia',
      title: t('areas', 'familyFriends'),
      intensity: 8,
      description: t('areas', 'moonRelations'),
      icon: UIIcons.Users,
      color: 'bg-purple-500',
      accentColor: '#9333EA', // purple-600
      bgColor: 'bg-purple-50 dark:bg-purple-950/50 border-purple-200 dark:border-purple-800',
      iconBg: 'bg-purple-100 dark:bg-purple-900/50',
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
    yourCelestialGuide: t('dashboard', 'yourCelestialGuide'),
    welcome: t('dashboard', 'welcome'),
    astralForecast: t('dashboard', 'astralForecast'),
    todayInsights: t('dashboard', 'todayInsights'),
    forecastByArea: t('dashboard', 'forecastByArea'),
    planetaryPositions: t('dashboard', 'planetaryPositions'),
    compatibility: t('dashboard', 'compatibility'),
    intensity: t('insights', 'intensity'),
    mercuryRetrograde: t('alerts', 'mercuryRetrograde'),
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
    <div className="dashboard-container">
      {/* ===== BOTÃO HAMBÚRGUER (MOBILE) ===== */}
      <button
        className="dashboard-mobile-menu-button"
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        aria-label="Toggle menu"
      >
        <UIIcons.Menu size={24} />
      </button>

      {/* ===== OVERLAY ESCURO (MOBILE) ===== */}
      {isSidebarOpen && (
        <div 
          className="dashboard-sidebar-overlay"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* ===== SIDEBAR FIXA À ESQUERDA ===== */}
      <aside className={`dashboard-sidebar ${isSidebarOpen ? 'open' : ''}`}>
        {/* Perfil do Usuário - Centralizado */}
        <div className="dashboard-sidebar-profile">
          <div className="dashboard-sidebar-profile-content">
            {/* Avatar centralizado */}
            <div className="dashboard-sidebar-avatar">
              <div className="dashboard-sidebar-avatar-circle">
                <UIIcons.User size={40} className="text-primary" />
              </div>
              {/* Status indicator */}
              <div className="dashboard-sidebar-status"></div>
            </div>
            {/* Nome centralizado */}
            <h3 className="dashboard-sidebar-name">{userData.name || 'Maria Silva'}</h3>
            {/* Info do signo */}
            <div className="dashboard-sidebar-info">
              <UserZodiacIcon size={16} className="text-primary" />
              <span>{texts.moonIn} {userData.moonSign || 'N/A'} • {texts.asc} {userData.ascendant || 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* Navegação */}
        <nav className="dashboard-sidebar-nav">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                setActiveSection(item.id);
                setIsSidebarOpen(false); // Fechar sidebar ao clicar em um item (mobile)
              }}
              className={`dashboard-sidebar-menu-item ${activeSection === item.id ? 'active' : ''}`}
            >
              <item.icon size={20} />
              <span className="dashboard-sidebar-menu-item-label">{item.label}</span>
              {item.badge && (
                <span className="dashboard-sidebar-menu-item-badge">
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </nav>

        {/* Mini Calendário */}
        <div className="dashboard-sidebar-calendar">
          <div className="dashboard-sidebar-calendar-header">
            <h4 className="dashboard-sidebar-calendar-title">
              {texts.november} {texts.of} 2025
            </h4>
            <div className="dashboard-sidebar-calendar-controls">
              <button 
                className="dashboard-sidebar-calendar-button"
                onClick={handlePreviousMonth}
                title={language === 'pt' ? 'Mês anterior' : 'Previous month'}
              >
                <UIIcons.ChevronLeft size={16} className="text-muted-foreground" />
              </button>
              <button 
                className="dashboard-sidebar-calendar-button"
                onClick={handleNextMonth}
                title={language === 'pt' ? 'Próximo mês' : 'Next month'}
              >
                <UIIcons.ChevronRight size={16} className="text-muted-foreground" />
              </button>
            </div>
          </div>
          
          {/* Grid calendário */}
          <div className="dashboard-sidebar-calendar-grid">
            {weekDays.map((day, i) => (
              <div key={i} className="dashboard-sidebar-calendar-day-header">{day}</div>
            ))}
            {calendarDays.map((dayData, i) => (
              <div
                key={i}
                className={`dashboard-sidebar-calendar-day ${dayData.current ? 'current' : ''}`}
              >
                {dayData.day}
                {dayData.events && !dayData.current && (
                  <div style={{
                    position: 'absolute',
                    bottom: 0,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: '4px',
                    height: '4px',
                    backgroundColor: 'hsl(var(--accent))',
                    borderRadius: '50%'
                  }}></div>
                )}
              </div>
            ))}
          </div>

          {/* Eventos lunares */}
          <div className="dashboard-sidebar-calendar-events">
            <div className="dashboard-sidebar-calendar-event">
              <UIIcons.Moon size={12} className="text-primary" />
              <span>{texts.fullMoon} (15)</span>
            </div>
            <div className="dashboard-sidebar-calendar-event">
              <UIIcons.Moon size={12} className="text-destructive" />
              <span>{texts.mercuryDirect} (28)</span>
            </div>
          </div>
        </div>
      </aside>

      {/* ===== ÁREA PRINCIPAL (com margin-left para sidebar) ===== */}
      <div className="dashboard-main">
        {/* ===== HEADER SUPERIOR ===== */}
        <header className="dashboard-header">
          <div className="dashboard-header-content">
            {/* Logo */}
            <div className="dashboard-header-logo">
              <div className="dashboard-header-logo-icon">
                <UIIcons.Sparkles size={24} className="text-foreground" />
              </div>
              <div>
                <h1 className="dashboard-header-logo-text">Cosmos Astral</h1>
                <p className="dashboard-header-logo-subtitle">{texts.yourCelestialGuide}</p>
              </div>
            </div>

            {/* Barra de Busca */}

            {/* Ações à direita */}
            <div className="dashboard-header-actions">
              {/* Notificações */}
              <button 
                className="dashboard-header-button"
                onClick={handleNotificationsClick}
                title={language === 'pt' ? 'Notificações' : 'Notifications'}
              >
                <UIIcons.Bell size={20} className="text-foreground" />
                <span className="dashboard-header-notification-badge"></span>
              </button>

              {/* Menu de Configurações */}
              <SettingsMenu onLogout={onLogout} />
            </div>
          </div>
        </header>

        {/* ===== CONTEÚDO PRINCIPAL ===== */}
        <main className="dashboard-content">
          {/* Renderização condicional baseada na seção ativa */}
          {activeSection === 'mapa-completo' ? (
            <FullBirthChartSection userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : activeSection === 'visao-geral' ? (
            <OverviewSection userData={userData} onBack={() => setActiveSection('inicio')} />
          ) : activeSection === 'revolucao-solar' ? (
            <SolarReturnSection userData={userData} onBack={() => setActiveSection('inicio')} />
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
          {/* Card sempre com fundo escuro e texto branco, independente do tema */}
          <div className="dashboard-hero">
            {/* Orbes de fundo */}
            <div className="dashboard-hero-orb dashboard-hero-orb-blue"></div>
            <div className="dashboard-hero-orb dashboard-hero-orb-purple"></div>
            
            <div className="dashboard-hero-content">
              <div className="dashboard-hero-badge">
                <UIIcons.Sparkles size={20} className="dashboard-hero-badge-icon" />
                <span className="dashboard-hero-badge-text">{texts.astralForecast}</span>
              </div>
              <h2 className="dashboard-hero-title">
                {texts.welcome}
              </h2>
              <p className="dashboard-hero-text">
                {texts.heroText}
              </p>
              <div className="dashboard-hero-tags">
                <div className="dashboard-hero-tag">
                  <UIIcons.Calendar size={16} className="dashboard-hero-tag-icon" />
                  <span className="dashboard-hero-tag-text">{texts.monday}, 24 {texts.of} {texts.november}</span>
                </div>
                <div className="dashboard-hero-tag">
                  <UIIcons.Moon size={16} className="dashboard-hero-tag-icon" />
                  <span className="dashboard-hero-tag-text dashboard-hero-tag-text-yellow">{texts.waxingMoonIn}</span>
                </div>
              </div>
            </div>
          </div>

          {/* ===== INSIGHTS DE HOJE (GRID 4 CARDS) ===== */}
          <div className="dashboard-section">
            <h3 className="dashboard-section-title">{texts.todayInsights}</h3>
            <div className="dashboard-insights-grid">
              {insights.map((insight) => (
                <div
                  key={insight.id}
                  className="dashboard-insight-card"
                >
                  {/* Ícone com fundo contrastante - mantém cor original */}
                  <div className="dashboard-insight-icon-container">
                    <insight.icon size={24} style={{ color: insight.accentColor }} />
                  </div>
                  {/* Textos usando variáveis CSS para contraste automático */}
                  <h4 className="dashboard-insight-title">
                    {insight.title}
                  </h4>
                  <p className="dashboard-insight-value">
                    {insight.value}
                  </p>
                  <p className="dashboard-insight-description">
                    {insight.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* ===== PREVISÕES POR ÁREA ===== */}
          <div className="dashboard-section">
            <h3 className="dashboard-section-title">{texts.forecastByArea}</h3>
            <div className="dashboard-areas-grid">
              {areas.map((area) => (
                <div
                  key={area.id}
                  className="dashboard-area-card"
                  onClick={() => onViewInterpretation(area.id)}
                >
                  <div className="dashboard-area-header">
                    <div className="dashboard-area-header-left">
                      {/* Ícone com fundo contrastante - mantém cor original */}
                      <div className="dashboard-area-icon-container">
                        <area.icon size={20} style={{ color: area.accentColor }} />
                      </div>
                      <h4 className="dashboard-area-title">
                        {area.title}
                      </h4>
                    </div>
                    <div className="dashboard-area-intensity">
                      <span className="dashboard-area-intensity-label">
                        {texts.intensity}
                      </span>
                      <p 
                        className="dashboard-area-intensity-value"
                        style={{ color: area.accentColor }}
                      >
                        {area.intensity}/10
                      </p>
                    </div>
                  </div>
                  <p className="dashboard-area-description">
                    {area.description}
                  </p>
                  {/* Barra de progresso melhorada */}
                  <div className="dashboard-area-progress">
                    <div
                      className={`dashboard-area-progress-bar ${area.color}`}
                      style={{ width: `${area.intensity * 10}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ===== GRID INFERIOR: POSIÇÕES PLANETÁRIAS + COMPATIBILIDADE ===== */}
          <div className="dashboard-bottom-grid">
            {/* Posições Planetárias */}
            <div className="dashboard-bottom-card">
              <h3 className="dashboard-bottom-card-title">{texts.planetaryPositions}</h3>
              <div className="dashboard-planetary-list">
                {planetaryPositions.map((position, i) => (
                  <div key={i} className="dashboard-planetary-item">
                    <div className="dashboard-planetary-icon-container">
                      <position.icon size={24} className="text-primary" />
                    </div>
                    <div className="dashboard-planetary-info">
                      <p className="dashboard-planetary-name">{position.planet}</p>
                      <p className="dashboard-planetary-sign">{t('planets', 'in')} {position.sign}</p>
                    </div>
                    <span className={`dashboard-planetary-status ${position.status === t('planets', 'retrograde') ? 'dashboard-planetary-status-retrograde' : 'dashboard-planetary-status-direct'}`}>
                      {position.status}
                    </span>
                  </div>
                ))}
              </div>

              {/* Alerta Mercúrio Retrógrado */}
              <div className="dashboard-planetary-alert">
                <UIIcons.AlertCircle size={20} className="dashboard-planetary-alert-icon" />
                <p className="dashboard-planetary-alert-text">
                      {texts.mercuryRetrograde}
                    </p>
              </div>
            </div>

            {/* Compatibilidade */}
            <div className="dashboard-bottom-card">
              <h3 className="dashboard-bottom-card-title">{texts.compatibility}</h3>
              

              <p className="dashboard-compatibility-subtitle">
                <UIIcons.Users size={14} />
                {texts.closePeople}
              </p>

              <div className="dashboard-compatibility-list">
                {compatibility.map((person, i) => (
                  <div key={i} className="dashboard-compatibility-item">
                    <div className="dashboard-compatibility-item-left">
                      <div className={`dashboard-compatibility-avatar ${person.color}`}>
                        {person.avatar}
                      </div>
                      <div className="dashboard-compatibility-info">
                        <p className="dashboard-compatibility-name">{person.name}</p>
                        <div className="dashboard-compatibility-sign">
                          <UIIcons.Star size={12} />
                          <span>{person.sign}</span>
                        </div>
                      </div>
                    </div>
                    <div className="dashboard-compatibility-item-right">
                      <p className="dashboard-compatibility-percentage">{person.compatibility}%</p>
                      <p className="dashboard-compatibility-label">{texts.affinity}</p>
                    </div>
                  </div>
                ))}
              </div>

              <button 
                className="dashboard-compatibility-button"
                onClick={handleViewAllCompatibility}
              >
                {texts.viewAll}
              </button>
            </div>
          </div>

          {/* Footer */}
          <footer className="dashboard-footer">
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

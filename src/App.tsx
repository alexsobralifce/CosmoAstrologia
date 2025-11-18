import { useState, useEffect } from 'react';
import { Onboarding, OnboardingData } from './components/onboarding';
import { AdvancedDashboard } from './components/advanced-dashboard';
import { PreChartDashboard } from './components/pre-chart-dashboard';
import { InterpretationPage } from './components/interpretation-page';
import { AstroButton } from './components/astro-button';
import { zodiacSigns } from './components/zodiac-icons';
import { planets } from './components/planet-icons';
import { UIIcons } from './components/ui-icons';
import { AstroCard } from './components/astro-card';
import { AstroInput } from './components/astro-input';
import { DatePicker } from './components/date-picker';
import { LocationAutocomplete } from './components/location-autocomplete';
import { ThemeProvider } from './components/theme-provider';
import { ThemeToggle } from './components/theme-toggle';
import { useAuth, UserWithBirthData } from './hooks/useAuth';

type AppView = 'landing' | 'onboarding' | 'dashboard' | 'interpretation' | 'style-guide';

export default function App() {
  // Always start on landing page - never auto-redirect to onboarding
  const [currentView, setCurrentView] = useState<AppView>('landing');
  const [userData, setUserData] = useState<OnboardingData | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [shouldGenerateChart, setShouldGenerateChart] = useState(false);
  const { user, loading, login, logout, isAuthenticated, hasBirthData, saveBirthData } = useAuth();

  // Check authentication and onboarding data
  useEffect(() => {
    if (loading) return;

    console.log('Auth state:', { loading, isAuthenticated, user, currentView }); // Debug

    // Check if user is returning from OAuth and should continue onboarding
    const onboardingStep = sessionStorage.getItem('onboarding_step');
    if (onboardingStep && isAuthenticated && currentView === 'landing') {
      console.log('User returning from OAuth, redirecting to onboarding');
      setCurrentView('onboarding');
      return;
    }

    // Check for birth data to save after authentication
    const birthDataToSave = sessionStorage.getItem('birth_data_to_save');
    if (birthDataToSave && isAuthenticated && saveBirthData) {
      try {
        const data = JSON.parse(birthDataToSave);
        // Save birth data to database
        saveBirthData({
          name: data.name,
          birthDate: new Date(data.birthDate),
          birthTime: data.birthTime,
          birthPlace: data.birthPlace,
        });
        sessionStorage.removeItem('birth_data_to_save');
        // After saving, redirect to dashboard
        setCurrentView('dashboard');
        return;
      } catch (error) {
        console.error('Error saving birth data:', error);
      }
    }

    // Load birth data from database when going to dashboard
    if (currentView === 'dashboard' && isAuthenticated && user && hasBirthData && !userData) {
      console.log('Loading birth data from database for dashboard');
      // Convert birth data from database to userData format
      if (user.birthData) {
        setUserData({
          name: user.birthData.name,
          birthDate: new Date(user.birthData.birth_date),
          birthTime: user.birthData.birth_time,
          birthPlace: user.birthData.birth_place,
        });
      }
      return;
    }

    // Only auto-redirect from landing page, not from other views
    if (currentView !== 'landing') return;

    // If user is authenticated and has birth data, offer to go to dashboard
    // But don't force it - let user choose
    if (isAuthenticated && user && hasBirthData) {
      console.log('User authenticated with birth data, staying on landing (can go to dashboard via button)');
      // Don't auto-redirect - let user click button
      return;
    }
    
    // If user is authenticated but no birth data, stay on landing
    // They can choose to go to onboarding or dashboard
    if (isAuthenticated && user && !hasBirthData) {
      console.log('User authenticated but no birth data, staying on landing');
      // Don't auto-redirect - let user choose
      return;
    }

    // Otherwise, stay on landing page (default state)
    console.log('Staying on landing page');
  }, [loading, isAuthenticated, user, currentView, hasBirthData, userData, saveBirthData]);

  const handleOnboardingComplete = async (data: OnboardingData) => {
    // If user is authenticated, save birth data to database
    if (isAuthenticated && saveBirthData) {
      try {
        await saveBirthData(data);
      } catch (error) {
        console.error('Failed to save birth data:', error);
      }
    }
    
    // Set userData and go to dashboard (works for both authenticated and non-authenticated users)
    setUserData(data);
    setCurrentView('dashboard');
  };

  const handleViewInterpretation = (topicId: string) => {
    setSelectedTopic(topicId);
    setCurrentView('interpretation');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
  };

  // Show loading screen while checking auth
  if (loading) {
    return (
      <ThemeProvider>
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-background via-background to-[#1a1f4a]">
          <div className="text-center space-y-4">
            <div className="animate-spin">
              <UIIcons.Star size={48} className="text-accent" />
            </div>
            <p className="text-secondary">Carregando...</p>
          </div>
        </div>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <AppContent
        currentView={currentView}
        setCurrentView={setCurrentView}
        userData={userData}
        selectedTopic={selectedTopic}
        handleOnboardingComplete={handleOnboardingComplete}
        handleViewInterpretation={handleViewInterpretation}
        handleBackToDashboard={handleBackToDashboard}
        user={user}
        login={login}
        logout={logout}
        isAuthenticated={isAuthenticated}
        hasBirthData={hasBirthData}
      />
    </ThemeProvider>
  );
}

interface LandingPageFormProps {
  onComplete: (data: OnboardingData) => void;
  onLogin: () => void;
  isAuthenticated: boolean;
  logout: () => Promise<void>;
  setCurrentView: (view: AppView) => void;
  saveBirthData?: (data: OnboardingData) => Promise<void>;
}

function LandingPageForm({
  onComplete,
  onLogin,
  isAuthenticated,
  logout,
  setCurrentView,
  saveBirthData
}: LandingPageFormProps) {
  const [step, setStep] = useState(1);
  const [birthPlace, setBirthPlace] = useState('');
  const [birthDate, setBirthDate] = useState<Date>();
  const [birthTime, setBirthTime] = useState('');
  const [dontKnowTime, setDontKnowTime] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = () => {
    if (!birthPlace || !birthDate) {
      return;
    }
    // Go to step 2 to collect name and email
    setStep(2);
  };

  const handleFinalSubmit = async () => {
    if (!name || !email || !birthPlace || !birthDate) {
      return;
    }

    // Use default time if user doesn't know
    const time = dontKnowTime ? '12:00' : birthTime || '12:00';
    
    try {
      // Register user in database
      const { apiService } = await import('./services/api');
      const response = await apiService.registerUser(
        name,
        email,
        {
          name,
          birth_date: birthDate.toISOString().split('T')[0],
          birth_time: time,
          birth_place: birthPlace
        }
      );
      
      // Complete with name and email
      onComplete({
        name,
        birthDate: birthDate,
        birthTime: time,
        birthPlace,
      });
    } catch (error) {
      console.error('Error registering user:', error);
      // Still complete even if registration fails (user can see map)
      onComplete({
        name,
        birthDate: birthDate,
        birthTime: time,
        birthPlace,
      });
    }
  };

  const handleGoogleLogin = () => {
    // Save birth data for after authentication
    if (birthPlace && birthDate) {
      const time = dontKnowTime ? '12:00' : birthTime || '12:00';
      sessionStorage.setItem('birth_data_to_save', JSON.stringify({
        name: 'Usuário',
        birthDate: birthDate.toISOString(),
        birthTime: time,
        birthPlace
      }));
    }
    // Trigger Google OAuth
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    window.location.href = `${API_BASE_URL}/api/auth/login`;
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-background via-background to-[#1a1f4a] dark:to-[#1a1f4a] light:to-[#F0E6D2] relative overflow-hidden">
      {/* Theme Toggle in Corner */}
      <div className="absolute top-4 right-4 z-50 flex gap-2">
        <ThemeToggle />
        {isAuthenticated ? (
          <AstroButton
            variant="outline"
            size="sm"
            onClick={async () => {
              await logout();
              window.location.reload();
            }}
            className="text-xs"
          >
            <UIIcons.LogOut size={14} />
            Sair
          </AstroButton>
        ) : null}
      </div>

      <div className="w-full max-w-md relative z-10">
        <AstroCard className="p-8 space-y-6">
          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center">
              <UIIcons.Star size={24} className="text-accent" />
            </div>
            <h1 className="text-2xl font-bold text-accent">Astrolink</h1>
          </div>

          {/* Step 1: Birth Data */}
          {step === 1 && (
            <>
              {/* Form Fields */}
              <div className="space-y-4">
                <LocationAutocomplete
                  label=""
                  placeholder="Em qual cidade você nasceu?"
                  value={birthPlace}
                  onChange={setBirthPlace}
                />

                <DatePicker
                  value={birthDate}
                  onChange={setBirthDate}
                  minYear={1900}
                  maxYear={new Date().getFullYear()}
                  placeholder="Qual sua data de nascimento?"
                />

                <div className="relative">
                  <AstroInput
                    type="time"
                    placeholder="Qual seu horário de nascimento?"
                    value={birthTime}
                    onChange={(e) => setBirthTime(e.target.value)}
                    disabled={dontKnowTime}
                    className="pr-10"
                  />
                  <UIIcons.Clock className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary" size={20} />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="dontKnowTime"
                    checked={dontKnowTime}
                    onChange={(e) => setDontKnowTime(e.target.checked)}
                    className="w-4 h-4 rounded border-border text-accent focus:ring-accent"
                  />
                  <label htmlFor="dontKnowTime" className="text-sm text-secondary cursor-pointer">
                    Não sei meu horário de nascimento / Informar depois?
                  </label>
                </div>
              </div>

              {/* Primary Button */}
              <AstroButton
                variant="primary"
                className="w-full"
                onClick={handleSubmit}
                disabled={!birthPlace || !birthDate}
              >
                Ver mapa astral completo
              </AstroButton>

              {/* Separator */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-card text-secondary">ou</span>
                </div>
              </div>

              {/* Social Login Buttons */}
              <div className="space-y-3">
                <AstroButton
                  variant="google"
                  className="w-full gap-3"
                  onClick={handleGoogleLogin}
                >
                  <svg width="20" height="20" viewBox="0 0 18 18">
                    <path
                      fill="#4285F4"
                      d="M16.51 8H8.98v3h4.3c-.18 1-.74 1.48-1.6 2.04v2.01h2.6a7.8 7.8 0 0 0 2.38-5.88c0-.57-.05-.66-.15-1.18z"
                    />
                    <path
                      fill="#34A853"
                      d="M8.98 17c2.16 0 3.97-.72 5.3-1.94l-2.6-2a4.8 4.8 0 0 1-7.18-2.54H1.83v2.07A8 8 0 0 0 8.98 17z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M4.5 10.52a4.8 4.8 0 0 1 0-3.04V5.41H1.83a8 8 0 0 0 0 7.18l2.67-2.07z"
                    />
                    <path
                      fill="#EA4335"
                      d="M8.98 4.18c1.17 0 2.23.4 3.06 1.2l2.3-2.3A8 8 0 0 0 1.83 5.4L4.5 7.49a4.77 4.77 0 0 1 4.48-3.3z"
                    />
                  </svg>
                  Login com Google
                </AstroButton>
              </div>

              {/* Login Link */}
              <div className="text-center pt-2">
                <span className="text-sm text-secondary">Já tem um cadastro? </span>
                <button
                  onClick={onLogin}
                  className="text-sm text-accent hover:text-accent/80 underline"
                >
                  Faça login
                </button>
              </div>
            </>
          )}

          {/* Step 2: Name and Email */}
          {step === 2 && (
            <>
              <div className="space-y-2 mb-4">
                <h2 className="text-accent text-xl">Complete seu cadastro</h2>
                <p className="text-secondary text-sm">
                  Informe seu nome e email para salvar seu mapa astral
                </p>
              </div>

              <div className="space-y-4">
                <AstroInput
                  label="Nome completo"
                  placeholder="Digite seu nome"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  autoFocus
                />

                <AstroInput
                  type="email"
                  label="Email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="flex gap-3 pt-2">
                <AstroButton
                  variant="secondary"
                  className="flex-1"
                  onClick={() => setStep(1)}
                >
                  Voltar
                </AstroButton>
                <AstroButton
                  variant="primary"
                  className="flex-1"
                  onClick={handleFinalSubmit}
                  disabled={!name || !email}
                >
                  Avançar
                </AstroButton>
              </div>
            </>
          )}
        </AstroCard>
      </div>
    </div>
  );
}

interface AppContentProps {
  currentView: AppView;
  setCurrentView: (view: AppView) => void;
  userData: OnboardingData | null;
  selectedTopic: string;
  handleOnboardingComplete: (data: OnboardingData) => void;
  handleViewInterpretation: (topicId: string) => void;
  handleBackToDashboard: () => void;
  user: UserWithBirthData | null;
  login: () => void;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  hasBirthData: boolean;
}

function AppContent({
  currentView,
  setCurrentView,
  userData,
  selectedTopic,
  handleOnboardingComplete,
  handleViewInterpretation,
  handleBackToDashboard,
  user,
  login,
  logout,
  isAuthenticated,
  hasBirthData,
}: AppContentProps) {
  // Landing Page with Astrolink-style form
  if (currentView === 'landing') {
    return (
      <LandingPageForm
        onComplete={handleOnboardingComplete}
        onLogin={login}
        isAuthenticated={isAuthenticated}
        logout={logout}
        setCurrentView={setCurrentView}
        saveBirthData={saveBirthData}
      />
    );
  }

  // Onboarding Flow
  if (currentView === 'onboarding') {
    return (
      <>
        <div className="absolute top-4 right-4 z-50">
          <ThemeToggle />
        </div>
        <Onboarding onComplete={handleOnboardingComplete} onLogin={login} />
      </>
    );
  }

  // Dashboard
  if (currentView === 'dashboard') {
    // If user is authenticated with birth data but hasn't generated chart yet
    // Show PreChartDashboard (even if userData is not set yet, we'll load it)
    if (isAuthenticated && user && hasBirthData && !shouldGenerateChart) {
      return (
        <PreChartDashboard
          user={user}
          onGenerateChart={() => {
            setShouldGenerateChart(true);
            // Convert birth data to userData format for AdvancedDashboard
            if (user.birthData) {
              setUserData({
                name: user.birthData.name,
                birthDate: new Date(user.birthData.birth_date),
                birthTime: user.birthData.birth_time,
                birthPlace: user.birthData.birth_place,
              });
            }
          }}
          onUpdateUser={async (name: string) => {
            // Update user name logic here
            console.log('Update user name:', name);
          }}
          onLogout={async () => {
            await logout();
            setShouldGenerateChart(false);
            setUserData(null);
            setCurrentView('landing');
          }}
        />
      );
    }
    
    // If we have userData (either loaded from DB or from onboarding), show AdvancedDashboard
    // This works for both authenticated and non-authenticated users
    if (userData) {
      return (
        <AdvancedDashboard userData={userData} onViewInterpretation={handleViewInterpretation} />
      );
    }
    
    // If user is authenticated but no birth data, show onboarding to collect birth data
    if (isAuthenticated && !hasBirthData) {
      return (
        <>
          <div className="absolute top-4 right-4 z-50">
            <ThemeToggle />
          </div>
          <Onboarding onComplete={handleOnboardingComplete} onLogin={login} />
        </>
      );
    }
    
    // If not authenticated and no userData, show onboarding
    if (!isAuthenticated && !userData) {
      return (
        <>
          <div className="absolute top-4 right-4 z-50">
            <ThemeToggle />
          </div>
          <Onboarding onComplete={handleOnboardingComplete} onLogin={login} />
        </>
      );
    }
  }

  // Interpretation Page
  if (currentView === 'interpretation') {
    return <InterpretationPage topicId={selectedTopic} onBack={handleBackToDashboard} />;
  }

  // Style Guide
  if (currentView === 'style-guide') {
    return (
      <div className="min-h-screen p-8 bg-gradient-to-b from-background via-background to-[#1a1f4a] dark:to-[#1a1f4a] light:to-[#F0E6D2]">
        <div className="absolute top-4 right-4 z-50">
          <ThemeToggle />
        </div>
        <div className="max-w-7xl mx-auto space-y-12">
          {/* Header */}
          <header className="text-center space-y-4 py-8">
            <h1 className="text-accent">Design System - Astrologia Premium</h1>
            <p className="text-secondary max-w-2xl mx-auto">
              Um sistema de design místico e profissional para aplicações de astrologia.
              Combinando elegância moderna com a sabedoria cósmica.
            </p>
            <div className="flex gap-3 justify-center">
              <AstroButton variant="secondary" onClick={() => setCurrentView('landing')}>
                Voltar ao Início
              </AstroButton>
              <ThemeToggle />
            </div>
          </header>

          {/* Theme System */}
          <section className="space-y-6">
            <div>
              <h2 className="text-accent mb-2">Sistema de Temas</h2>
              <p className="text-secondary">Tema Noturno (escuro) e Diurno (claro) para conforto visual</p>
            </div>

            <AstroCard>
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-foreground mb-2">Alternar entre Dia e Noite</h3>
                    <p className="text-secondary">
                      O sistema adapta automaticamente as cores para proporcionar a melhor experiência
                      em qualquer horário.
                    </p>
                  </div>
                  <ThemeToggle />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-border/30">
                  <div className="space-y-2">
                    <h4 className="text-foreground flex items-center gap-2">
                      <UIIcons.Moon size={18} className="text-accent" />
                      Tema Noturno (Padrão)
                    </h4>
                    <p className="text-sm text-secondary">
                      Fundo azul-marinho cósmico (#0A0E2F) com acentos dourados âmbar (#E8B95A). 
                      Ideal para leitura noturna e atmosfera mística profunda.
                    </p>
                  </div>
                  <div className="space-y-2">
                    <h4 className="text-foreground flex items-center gap-2">
                      <UIIcons.Sun size={18} className="text-accent" />
                      Tema Diurno (Claro)
                    </h4>
                    <p className="text-sm text-secondary">
                      Fundo quase branco com toque de creme (#FDFBF7) e acentos em dourado vibrante (#D4A024). 
                      Otimizado para leitura diurna com máximo conforto visual.
                    </p>
                  </div>
                </div>
              </div>
            </AstroCard>
          </section>

          {/* Color Palette */}
          <section className="space-y-6">
            <div>
              <h2 className="text-accent mb-2">Paleta de Cores</h2>
              <p className="text-secondary">Cores inspiradas no cosmos e em elementos celestiais (adaptam ao tema)</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <AstroCard>
                <div className="space-y-4">
                  <div className="w-full h-20 rounded-lg bg-background border border-border"></div>
                  <div>
                    <h3 className="text-foreground">Primária - Cosmos</h3>
                    <p className="text-secondary">#0A0E2F</p>
                    <p className="text-sm text-secondary/70">Fundo principal azul-marinho profundo</p>
                  </div>
                </div>
              </AstroCard>

              <AstroCard>
                <div className="space-y-4">
                  <div className="w-full h-20 rounded-lg bg-accent"></div>
                  <div>
                    <h3 className="text-foreground">Acento - Dourado</h3>
                    <p className="text-secondary">#E8B95A</p>
                    <p className="text-sm text-secondary/70">CTAs, destaques e ícones importantes</p>
                  </div>
                </div>
              </AstroCard>

              <AstroCard>
                <div className="space-y-4">
                  <div className="w-full h-20 rounded-lg bg-foreground"></div>
                  <div>
                    <h3 className="text-foreground">Texto Principal</h3>
                    <p className="text-secondary">#F0F0F0</p>
                    <p className="text-sm text-secondary/70">Branco suave para alta legibilidade</p>
                  </div>
                </div>
              </AstroCard>
            </div>
          </section>

          {/* Typography */}
          <section className="space-y-6">
            <div>
              <h2 className="text-accent mb-2">Tipografia</h2>
              <p className="text-secondary">Combinação elegante de serifada e sans-serif</p>
            </div>

            <AstroCard>
              <div className="space-y-6">
                <div className="space-y-2">
                  <h1 className="text-foreground">Playfair Display - Títulos H1</h1>
                  <p className="text-secondary">Fonte serifada elegante para headers principais</p>
                </div>

                <div className="space-y-2">
                  <h2 className="text-foreground">Playfair Display - Títulos H2</h2>
                  <p className="text-secondary">Subtítulos e seções importantes</p>
                </div>

                <div className="space-y-2">
                  <p className="text-foreground">Inter - Corpo de texto e parágrafos</p>
                  <p className="text-secondary">
                    Sans-serif moderna com excelente legibilidade para textos longos, labels e
                    elementos de interface.
                  </p>
                </div>
              </div>
            </AstroCard>
          </section>

          {/* Buttons */}
          <section className="space-y-6">
            <div>
              <h2 className="text-accent mb-2">Botões</h2>
              <p className="text-secondary">CTAs com hierarquia visual clara</p>
            </div>

            <AstroCard>
              <div className="space-y-6">
                <div className="space-y-3">
                  <h3 className="text-foreground">Primário - Ações Principais</h3>
                  <div className="flex flex-wrap gap-4">
                    <AstroButton variant="primary" size="lg">
                      Calcular Mapa Astral
                    </AstroButton>
                    <AstroButton variant="primary" size="md">
                      Entrar
                    </AstroButton>
                    <AstroButton variant="primary" size="sm">
                      Confirmar
                    </AstroButton>
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="text-foreground">Secundário - Ações Alternativas</h3>
                  <div className="flex flex-wrap gap-4">
                    <AstroButton variant="secondary" size="md">
                      Cancelar
                    </AstroButton>
                    <AstroButton variant="secondary" size="sm">
                      Voltar
                    </AstroButton>
                  </div>
                </div>
              </div>
            </AstroCard>
          </section>

          {/* Form Inputs */}
          <section className="space-y-6">
            <div>
              <h2 className="text-accent mb-2">Campos de Formulário</h2>
              <p className="text-secondary">Inputs com labels visíveis e bordas douradas em foco</p>
            </div>

            <AstroCard>
              <div className="space-y-6 max-w-md">
                <AstroInput label="Nome Completo" placeholder="Digite seu nome" />

                <AstroInput label="Email" type="email" placeholder="seu@email.com" />

                <AstroInput label="Data de Nascimento" type="date" />

                <AstroInput
                  label="Campo com Erro"
                  placeholder="Exemplo de erro"
                  error="Este campo é obrigatório"
                />
              </div>
            </AstroCard>
          </section>

          {/* Zodiac Icons */}
          <section className="space-y-6">
            <div>
              <h2 className="text-accent mb-2">Ícones do Zodíaco</h2>
              <p className="text-secondary">Representações visuais dos 12 signos</p>
            </div>

            <AstroCard>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
                {zodiacSigns.map((sign) => (
                  <div
                    key={sign.name}
                    className="flex flex-col items-center gap-3 p-4 rounded-lg hover:bg-accent/10 transition-colors"
                  >
                    <sign.icon size={40} className="text-accent" />
                    <div className="text-center">
                      <p className="text-foreground">{sign.name}</p>
                      <p className="text-secondary">{sign.symbol}</p>
                    </div>
                  </div>
                ))}
              </div>
            </AstroCard>
          </section>

          {/* Planet Icons */}
          <section className="space-y-6 pb-12">
            <div>
              <h2 className="text-accent mb-2">Ícones dos Planetas</h2>
              <p className="text-secondary">Símbolos dos 10 corpos celestiais</p>
            </div>

            <AstroCard>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {planets.map((planet) => (
                  <div
                    key={planet.name}
                    className="flex flex-col items-center gap-3 p-4 rounded-lg hover:bg-accent/10 transition-colors"
                  >
                    <planet.icon size={40} className="text-accent" />
                    <div className="text-center">
                      <p className="text-foreground">{planet.name}</p>
                      <p className="text-secondary">{planet.symbol}</p>
                    </div>
                  </div>
                ))}
              </div>
            </AstroCard>
          </section>
        </div>
      </div>
    );
  }

  return null;
}

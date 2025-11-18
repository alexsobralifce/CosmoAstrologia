import { useState } from 'react';
import { Onboarding, OnboardingData } from './components/onboarding';
import { AdvancedDashboard } from './components/advanced-dashboard';
import { InterpretationPage } from './components/interpretation-page';
import { AstroButton } from './components/astro-button';
import { zodiacSigns } from './components/zodiac-icons';
import { planets } from './components/planet-icons';
import { UIIcons } from './components/ui-icons';
import { AstroCard } from './components/astro-card';
import { AstroInput } from './components/astro-input';
import { ThemeProvider } from './components/theme-provider';
import { ThemeToggle } from './components/theme-toggle';

type AppView = 'landing' | 'onboarding' | 'dashboard' | 'interpretation' | 'style-guide';

export default function App() {
  const [currentView, setCurrentView] = useState<AppView>('landing');
  const [userData, setUserData] = useState<OnboardingData | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<string>('');

  const handleOnboardingComplete = (data: OnboardingData) => {
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
      />
    </ThemeProvider>
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
}

function AppContent({
  currentView,
  setCurrentView,
  userData,
  selectedTopic,
  handleOnboardingComplete,
  handleViewInterpretation,
  handleBackToDashboard,
}: AppContentProps) {
  // Landing Page
  if (currentView === 'landing') {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-background via-background to-[#1a1f4a] dark:to-[#1a1f4a] light:to-[#F0E6D2] relative overflow-hidden">
        {/* Theme Toggle in Corner */}
        <div className="absolute top-4 right-4 z-50">
          <ThemeToggle />
        </div>
        {/* Starry background effect */}
        <div className="absolute inset-0 opacity-30">
          {Array.from({ length: 50 }).map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-accent rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                opacity: Math.random() * 0.5 + 0.3,
              }}
            />
          ))}
        </div>

        <div className="max-w-4xl w-full relative z-10">
          <AstroCard className="text-center space-y-8">
            {/* Logo/Icon */}
            <div className="flex justify-center">
              <div className="w-24 h-24 rounded-full bg-accent/20 flex items-center justify-center">
                <UIIcons.Star size={48} className="text-accent" />
              </div>
            </div>

            {/* Hero Text */}
            <div className="space-y-4">
              <h1 className="text-accent">Descubra Seu Mapa Astral</h1>
              <p className="text-secondary max-w-2xl mx-auto">
                Uma experiência premium de astrologia. Explore as posições planetárias do momento
                do seu nascimento e desvende os segredos escritos nas estrelas.
              </p>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
              <AstroButton
                variant="primary"
                size="lg"
                onClick={() => setCurrentView('onboarding')}
              >
                Calcular Meu Mapa Astral
              </AstroButton>
              <AstroButton
                variant="secondary"
                size="lg"
                onClick={() => setCurrentView('style-guide')}
              >
                Ver Design System
              </AstroButton>
            </div>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
              <div className="space-y-3">
                <UIIcons.Star size={32} className="text-accent mx-auto" />
                <h3 className="text-foreground">Interpretações Detalhadas</h3>
                <p className="text-sm text-secondary">
                  Análises profundas de cada posição planetária e aspecto do seu mapa
                </p>
              </div>
              <div className="space-y-3">
                <UIIcons.Eye size={32} className="text-accent mx-auto" />
                <h3 className="text-foreground">Visualização Interativa</h3>
                <p className="text-sm text-secondary">
                  Explore seu mapa natal com gráficos elegantes e intuitivos
                </p>
              </div>
              <div className="space-y-3">
                <UIIcons.Heart size={32} className="text-accent mx-auto" />
                <h3 className="text-foreground">Experiência Premium</h3>
                <p className="text-sm text-secondary">
                  Design místico e profissional focado na clareza dos dados
                </p>
              </div>
            </div>
          </AstroCard>
        </div>
      </div>
    );
  }

  // Onboarding Flow
  if (currentView === 'onboarding') {
    return (
      <>
        <div className="absolute top-4 right-4 z-50">
          <ThemeToggle />
        </div>
        <Onboarding onComplete={handleOnboardingComplete} />
      </>
    );
  }

  // Dashboard
  if (currentView === 'dashboard' && userData) {
    return (
      <AdvancedDashboard userData={userData} onViewInterpretation={handleViewInterpretation} />
    );
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

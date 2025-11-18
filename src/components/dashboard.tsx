import { useState } from 'react';
import { AstroCard } from './astro-card';
import { AstroButton } from './astro-button';
import { BirthChartWheel } from './birth-chart-wheel';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';
import { UIIcons } from './ui-icons';
import { OnboardingData } from './onboarding';

interface DashboardProps {
  userData: OnboardingData;
  onViewInterpretation: (topic: string) => void;
}

interface Interpretation {
  id: string;
  title: string;
  summary: string;
  icon: any;
}

export const Dashboard = ({ userData, onViewInterpretation }: DashboardProps) => {
  const [activeSection, setActiveSection] = useState('overview');

  // Mock astrological data
  const bigThree = {
    sun: { sign: 'Leão', icon: zodiacSigns[4].icon },
    moon: { sign: 'Touro', icon: zodiacSigns[1].icon },
    ascendant: { sign: 'Gêmeos', icon: zodiacSigns[2].icon },
  };

  const interpretations: Interpretation[] = [
    {
      id: 'mercury-cancer',
      title: 'Seu Mercúrio em Câncer',
      summary: 'Você se comunica de forma emocional e intuitiva, valorizando conexões profundas...',
      icon: planets[2].icon,
    },
    {
      id: 'venus-gemini',
      title: 'Vênus em Gêmeos',
      summary: 'No amor, você busca variedade e comunicação. Conversas estimulantes são essenciais...',
      icon: planets[3].icon,
    },
    {
      id: 'mars-aries',
      title: 'Marte em Áries',
      summary: 'Sua energia é assertiva e direta. Você age com coragem e iniciativa...',
      icon: planets[4].icon,
    },
    {
      id: 'sun-house-5',
      title: 'Sol na Casa 5',
      summary: 'Sua essência brilha através da criatividade, romance e autoexpressão...',
      icon: planets[0].icon,
    },
  ];

  const menuItems = [
    { id: 'overview', label: 'Visão Geral', icon: UIIcons.Star },
    { id: 'planets', label: 'Planetas', icon: UIIcons.Star },
    { id: 'houses', label: 'Casas', icon: UIIcons.Star },
    { id: 'aspects', label: 'Aspectos', icon: UIIcons.Star },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-[#1a1f4a]">
      {/* Header */}
      <header className="border-b border-border/30 backdrop-blur-sm sticky top-0 z-10 bg-background/80">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h2 className="text-accent">Mapa Astral</h2>
          <div className="flex items-center gap-4">
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

      {/* Main Content - 3 Column Layout */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column - User Info & Navigation */}
          <aside className="lg:col-span-3 space-y-6">
            {/* User Card */}
            <AstroCard>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center">
                    <UIIcons.User size={32} className="text-accent" />
                  </div>
                  <div>
                    <h3 className="text-foreground">{userData.name}</h3>
                    <p className="text-sm text-secondary">
                      {userData.birthDate.toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                </div>
              </div>
            </AstroCard>

            {/* Big Three */}
            <AstroCard>
              <h3 className="text-foreground mb-4">Seus Três Pilares</h3>
              <div className="space-y-4">
                <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-accent/10 transition-colors">
                  <bigThree.sun.icon size={32} className="text-accent" />
                  <div>
                    <p className="text-sm text-secondary">Sol</p>
                    <p className="text-foreground">{bigThree.sun.sign}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-accent/10 transition-colors">
                  <bigThree.moon.icon size={32} className="text-accent" />
                  <div>
                    <p className="text-sm text-secondary">Lua</p>
                    <p className="text-foreground">{bigThree.moon.sign}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-accent/10 transition-colors">
                  <bigThree.ascendant.icon size={32} className="text-accent" />
                  <div>
                    <p className="text-sm text-secondary">Ascendente</p>
                    <p className="text-foreground">{bigThree.ascendant.sign}</p>
                  </div>
                </div>
              </div>
            </AstroCard>

            {/* Navigation */}
            <AstroCard>
              <nav className="space-y-2">
                {menuItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setActiveSection(item.id)}
                    className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                      activeSection === item.id
                        ? 'bg-accent/20 text-accent'
                        : 'text-secondary hover:bg-accent/10 hover:text-foreground'
                    }`}
                  >
                    <item.icon size={20} />
                    <span>{item.label}</span>
                  </button>
                ))}
              </nav>
            </AstroCard>
          </aside>

          {/* Center Column - Birth Chart */}
          <main className="lg:col-span-6 space-y-6">
            <AstroCard>
              <div className="space-y-6">
                <div className="text-center space-y-2">
                  <h2 className="text-accent">Seu Mapa Natal</h2>
                  <p className="text-secondary">
                    {userData.birthPlace} • {userData.birthTime}
                  </p>
                </div>

                <div className="p-6">
                  <BirthChartWheel />
                </div>

                <div className="flex items-center justify-center gap-6 flex-wrap text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-accent"></div>
                    <span className="text-secondary">Planetas</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full border border-accent"></div>
                    <span className="text-secondary">Casas</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-accent/20"></div>
                    <span className="text-secondary">Signos</span>
                  </div>
                </div>
              </div>
            </AstroCard>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-4">
              <AstroCard className="text-center">
                <UIIcons.Star size={32} className="text-accent mx-auto mb-2" />
                <h3 className="text-foreground">Elemento Dominante</h3>
                <p className="text-secondary">Fogo</p>
              </AstroCard>
              <AstroCard className="text-center">
                <UIIcons.Star size={32} className="text-accent mx-auto mb-2" />
                <h3 className="text-foreground">Modalidade</h3>
                <p className="text-secondary">Fixo</p>
              </AstroCard>
            </div>
          </main>

          {/* Right Column - Interpretations */}
          <aside className="lg:col-span-3 space-y-6">
            <div className="sticky top-24 space-y-4">
              <h3 className="text-accent px-2">Interpretações</h3>
              
              <div className="space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto pr-2">
                {interpretations.map((interp) => (
                  <AstroCard
                    key={interp.id}
                    className="hover:border-accent/50 transition-all cursor-pointer group"
                  >
                    <div className="space-y-3">
                      <div className="flex items-start gap-3">
                        <interp.icon size={24} className="text-accent mt-1 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <h4 className="text-foreground group-hover:text-accent transition-colors">
                            {interp.title}
                          </h4>
                          <p className="text-sm text-secondary line-clamp-2 mt-1">
                            {interp.summary}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => onViewInterpretation(interp.id)}
                        className="text-sm text-accent hover:text-accent/80 transition-colors flex items-center gap-1"
                      >
                        Ler interpretação completa
                        <UIIcons.ChevronDown size={16} className="rotate-[-90deg]" />
                      </button>
                    </div>
                  </AstroCard>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
};

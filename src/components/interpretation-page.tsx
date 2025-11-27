import React, { useState } from 'react';
import { AstroCard } from './astro-card';
import { UIIcons } from './ui-icons';
import { planets } from './planet-icons';
import { zodiacSigns } from './zodiac-icons';
import { AstroButton } from './astro-button';
import { ThemeToggle } from './theme-toggle';

interface InterpretationPageProps {
  topicId: string;
  onBack: () => void;
}

interface ContentSection {
  id: string;
  title: string;
  icon?: any;
  subsections?: ContentSection[];
}

export const InterpretationPage = ({ topicId, onBack }: InterpretationPageProps) => {
  const [activeSection, setActiveSection] = useState('overview');

  const navigationSections: ContentSection[] = [
    {
      id: 'planets',
      title: 'Planetas',
      icon: planets[0].icon,
      subsections: [
        { id: 'sun', title: 'Sol', icon: planets[0].icon },
        { id: 'moon', title: 'Lua', icon: planets[1].icon },
        { id: 'mercury', title: 'Mercúrio', icon: planets[2].icon },
        { id: 'venus', title: 'Vênus', icon: planets[3].icon },
        { id: 'mars', title: 'Marte', icon: planets[4].icon },
        { id: 'jupiter', title: 'Júpiter', icon: planets[5].icon },
        { id: 'saturn', title: 'Saturno', icon: planets[6].icon },
      ],
    },
    {
      id: 'houses',
      title: 'Casas',
      icon: UIIcons.Star,
      subsections: Array.from({ length: 12 }, (_, i) => ({
        id: `house-${i + 1}`,
        title: `Casa ${i + 1}`,
      })),
    },
    {
      id: 'aspects',
      title: 'Aspectos',
      icon: UIIcons.Star,
      subsections: [
        { id: 'conjunctions', title: 'Conjunções' },
        { id: 'oppositions', title: 'Oposições' },
        { id: 'squares', title: 'Quadraturas' },
        { id: 'trines', title: 'Trígonos' },
        { id: 'sextiles', title: 'Sextis' },
      ],
    },
  ];

  const contentData = {
    title: 'O Sol na Casa 5',
    icon: planets[0].icon,
    sections: [
      {
        heading: 'Visão Geral',
        content: `Ter o Sol na Casa 5 é uma posição extremamente favorável para a autoexpressão criativa e o prazer. Esta casa rege a criatividade, o romance, os hobbies, os filhos e tudo aquilo que nos traz alegria genuína. Quando o Sol, que representa nossa essência e vitalidade, está posicionado aqui, ele ilumina todas essas áreas da vida.`,
      },
      {
        heading: 'Criatividade e Expressão Pessoal',
        content: `Você tem uma necessidade inata de se expressar criativamente. Seja através da arte, da música, da escrita ou de qualquer outra forma de expressão, você brilha quando está criando algo que vem do coração. Sua identidade está intimamente ligada à sua capacidade de criar e compartilhar sua visão única com o mundo.

Esta posição sugere que você pode ter um talento natural para as artes performáticas. Você gosta de estar no centro das atenções e tem uma presença carismática que atrai os outros. Não é incomum encontrar pessoas com esta posição atuando, dançando, cantando ou se envolvendo em qualquer atividade que permita que sua personalidade brilhe.`,
      },
      {
        heading: 'Romance e Relacionamentos',
        content: `No amor, você é apaixonado e romântico. Você procura relacionamentos que sejam empolgantes e que tragam alegria à sua vida. O romance é importante para você, e você gosta de cortejar e ser cortejado. Você pode ser dramático em suas expressões de amor e aprecia parceiros que valorizem a paixão e a diversão.

Há uma tendência a idealizar os relacionamentos românticos, buscando aquela conexão mágica que faz seu coração cantar. Você quer se sentir vivo e inspirado pelo amor, e pode ter dificuldade com relacionamentos que se tornam muito rotineiros ou previsíveis.`,
      },
      {
        heading: 'Alegria e Prazer',
        content: `Você tem uma capacidade natural de encontrar alegria nas pequenas coisas da vida. Seus hobbies e interesses são uma parte importante de quem você é, e você investe tempo e energia em atividades que lhe trazem prazer. Você pode ter uma variedade de interesses criativos e recreativos, e adora experimentar coisas novas.

Esta posição também está ligada ao jogo e à especulação. Você pode gostar de assumir riscos calculados, seja em investimentos, jogos ou simplesmente na vida em geral. Há um elemento de sorte associado a esta posição, mas é importante não exagerar na busca por emoções fortes.`,
      },
      {
        heading: 'Relacionamento com Crianças',
        content: `A Casa 5 rege os filhos, e ter o Sol aqui pode indicar uma forte conexão com crianças. Se você tem filhos, eles são uma fonte de orgulho e alegria para você. Você pode ser um pai ou mãe muito envolvido e criativo, incentivando seus filhos a expressarem sua própria individualidade.

Mesmo que você não tenha filhos próprios, pode ter uma afinidade natural com crianças e desfrutar de passar tempo com elas. Você pode trabalhar em áreas relacionadas à educação infantil ou simplesmente gostar de manter vivo seu espírito jovem e lúdico.`,
      },
      {
        heading: 'Desafios Potenciais',
        content: `Embora esta seja geralmente uma posição muito positiva, há alguns desafios potenciais. Você pode ter uma tendência a ser excessivamente dramático ou a buscar atenção de maneiras que não são sempre construtivas. Aprender a equilibrar sua necessidade de estar no centro das atenções com a capacidade de compartilhar o palco com os outros é importante.

Também pode haver uma tendência a evitar responsabilidades em favor da busca do prazer. É importante encontrar um equilíbrio entre aproveitar a vida e cumprir suas obrigações. Lembre-se de que a verdadeira felicidade vem não apenas da diversão, mas também de um senso de propósito e realização.`,
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-[#1a1f4a] dark:to-[#1a1f4a] light:to-[#F0E6D2]">
      {/* Header */}
      <header className="border-b border-border/30 backdrop-blur-sm sticky top-0 z-10 bg-background/80">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <AstroButton variant="secondary" size="sm" onClick={onBack}>
              <UIIcons.ChevronDown size={20} className="rotate-90" />
              Voltar
            </AstroButton>
            <h2 className="text-accent">Interpretação Detalhada</h2>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <button className="p-2 rounded-lg hover:bg-accent/10 transition-colors">
              <UIIcons.Bookmark size={20} className="text-secondary" />
            </button>
            <button className="p-2 rounded-lg hover:bg-accent/10 transition-colors">
              <UIIcons.Share2 size={20} className="text-secondary" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content - 2 Column Layout */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Sidebar - Table of Contents (Sticky) */}
          <aside className="lg:col-span-3">
            <div className="sticky top-24 space-y-6">
              <AstroCard>
                <h3 className="text-foreground mb-4">Navegação</h3>
                <nav className="space-y-1">
                  {navigationSections.map((section) => (
                    <div key={section.id}>
                      <button
                        onClick={() => setActiveSection(section.id)}
                        className={`w-full flex items-center gap-2 p-2 rounded-lg transition-colors text-left ${
                          activeSection === section.id
                            ? 'bg-accent/20 text-accent'
                            : 'text-secondary hover:bg-accent/10 hover:text-foreground'
                        }`}
                      >
                        {section.icon && <section.icon size={18} />}
                        <span className="text-sm">{section.title}</span>
                      </button>
                      
                      {section.subsections && activeSection === section.id && (
                        <div className="ml-6 mt-1 space-y-1">
                          {section.subsections.map((subsection) => (
                            <button
                              key={subsection.id}
                              className="w-full flex items-center gap-2 p-2 rounded-lg transition-colors text-left text-sm text-secondary hover:bg-accent/10 hover:text-foreground"
                            >
                              {subsection.icon && <subsection.icon size={16} />}
                              <span>{subsection.title}</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </nav>
              </AstroCard>

              {/* Quick Info Card */}
              <AstroCard>
                <div className="space-y-3">
                  <h4 className="text-foreground">Nesta Interpretação</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <UIIcons.Clock size={16} className="text-accent" />
                      <span className="text-secondary">15 min de leitura</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <UIIcons.Star size={16} className="text-accent" />
                      <span className="text-secondary">Interpretação Premium</span>
                    </div>
                  </div>
                </div>
              </AstroCard>
            </div>
          </aside>

          {/* Right Content Area - Article */}
          <main className="lg:col-span-9">
            <AstroCard className="max-w-4xl">
              <article className="prose prose-invert max-w-none">
                {/* Article Header */}
                <div className="mb-8 pb-6 border-b border-border/30">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center">
                      <contentData.icon size={32} className="text-accent" />
                    </div>
                    <div>
                      <h1 className="text-accent mb-1">{contentData.title}</h1>
                      <p className="text-secondary">
                        Posição Natal • Autoexpressão e Criatividade
                      </p>
                    </div>
                  </div>
                </div>

                {/* Article Content */}
                <div className="space-y-8">
                  {contentData.sections.map((section, index) => (
                    <section key={index} className="space-y-4">
                      <h2 className="text-foreground flex items-center gap-3">
                        <span className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-accent text-sm">
                          {index + 1}
                        </span>
                        {section.heading}
                      </h2>
                      <div className="space-y-4">
                        {section.content.split('\n\n').map((paragraph, pIndex) => (
                          <p key={pIndex} className="text-secondary leading-relaxed">
                            {paragraph}
                          </p>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>

                {/* Related Topics */}
                <div className="mt-12 pt-8 border-t border-border/30">
                  <h3 className="text-foreground mb-4">Tópicos Relacionados</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      { title: 'Lua na Casa 2', icon: planets[1].icon },
                      { title: 'Mercúrio em Câncer', icon: planets[2].icon },
                      { title: 'Vênus em Gêmeos', icon: planets[3].icon },
                      { title: 'Casa 5 e Criatividade', icon: UIIcons.Star },
                    ].map((topic, i) => (
                      <button
                        key={i}
                        className="flex items-center gap-3 p-4 rounded-lg bg-card hover:bg-accent/10 border border-border/30 hover:border-accent/50 transition-all text-left group"
                      >
                        <topic.icon size={24} className="text-accent" />
                        <span className="text-foreground group-hover:text-accent transition-colors">
                          {topic.title}
                        </span>
                        <UIIcons.ChevronDown
                          size={16}
                          className="ml-auto rotate-[-90deg] text-secondary group-hover:text-accent transition-colors"
                        />
                      </button>
                    ))}
                  </div>
                </div>
              </article>
            </AstroCard>
          </main>
        </div>
      </div>
    </div>
  );
};

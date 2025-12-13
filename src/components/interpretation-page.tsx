'use client';

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

  // Mapear topicId para conteúdo
  const getContentData = (id: string) => {
    const contentMap: Record<string, any> = {
      'amor': {
        title: 'Amor e Relacionamentos',
        icon: UIIcons.Heart,
        subtitle: 'Posição Natal • Conexões e Harmonia',
        sections: [
          {
            heading: 'Visão Geral',
            content: `Os relacionamentos amorosos são uma área fundamental do seu mapa astral. A forma como você ama, se relaciona e se conecta emocionalmente com os outros revela muito sobre sua natureza mais profunda.`,
          },
          {
            heading: 'Vênus e a Expressão do Amor',
            content: `Vênus rege o amor, a beleza e os valores relacionados aos relacionamentos. A posição de Vênus no seu mapa indica como você expressa afeto, o que você valoriza em um parceiro e como busca harmonia nos relacionamentos.`,
          },
          {
            heading: 'Casa 7 e Parcerias',
            content: `A Casa 7 é a casa das parcerias e relacionamentos comprometidos. Ela revela o tipo de parceiro que você busca e como você se comporta em relacionamentos sérios.`,
          },
          {
            heading: 'Desafios e Crescimento',
            content: `Todo relacionamento traz desafios e oportunidades de crescimento. Compreender os aspectos desafiadores no seu mapa pode ajudá-lo a trabalhar em áreas que precisam de desenvolvimento para criar relacionamentos mais saudáveis e satisfatórios.`,
          },
        ],
      },
      'carreira': {
        title: 'Carreira e Finanças',
        icon: UIIcons.Briefcase,
        subtitle: 'Posição Natal • Sucesso e Realização',
        sections: [
          {
            heading: 'Visão Geral',
            content: `Sua carreira e vida financeira são áreas importantes do seu desenvolvimento pessoal. O mapa astral revela seus talentos, ambições e o caminho para o sucesso profissional.`,
          },
          {
            heading: 'Casa 10 e Profissão',
            content: `A Casa 10 é a casa da carreira e reputação pública. Ela indica como você é visto profissionalmente e que tipo de realizações você busca alcançar.`,
          },
          {
            heading: 'Saturno e Responsabilidade',
            content: `Saturno representa disciplina, estrutura e responsabilidade. Sua posição no mapa revela como você lida com autoridade, metas de longo prazo e construção de uma base sólida.`,
          },
          {
            heading: 'Casa 2 e Recursos',
            content: `A Casa 2 rege seus recursos, valores e segurança material. Ela mostra como você ganha dinheiro, o que você valoriza e como você administra seus recursos financeiros.`,
          },
        ],
      },
      'saude': {
        title: 'Saúde e Bem-Estar',
        icon: UIIcons.Activity,
        subtitle: 'Posição Natal • Vitalidade e Equilíbrio',
        sections: [
          {
            heading: 'Visão Geral',
            content: `A saúde é uma manifestação do equilíbrio entre corpo, mente e espírito. Seu mapa astral oferece insights sobre sua vitalidade, áreas que precisam de atenção e práticas que podem melhorar seu bem-estar geral.`,
          },
          {
            heading: 'Casa 6 e Saúde',
            content: `A Casa 6 rege a saúde física, rotinas diárias e hábitos de vida. Ela indica como você cuida do seu corpo e que tipo de práticas de saúde são mais benéficas para você.`,
          },
          {
            heading: 'Marte e Energia',
            content: `Marte representa energia física, força e ação. Sua posição revela seu nível de energia, como você canaliza sua força e quais atividades físicas são mais adequadas para você.`,
          },
          {
            heading: 'Equilíbrio e Prevenção',
            content: `Manter o equilíbrio é essencial para uma boa saúde. Compreender os aspectos do seu mapa pode ajudá-lo a identificar padrões que podem afetar seu bem-estar e tomar medidas preventivas.`,
          },
        ],
      },
      'familia': {
        title: 'Família e Amigos',
        icon: UIIcons.Users,
        subtitle: 'Posição Natal • Conexões e Raízes',
        sections: [
          {
            heading: 'Visão Geral',
            content: `As relações familiares e amizades formam a base do seu sistema de apoio. O mapa astral revela como você se relaciona com a família, amigos e sua comunidade.`,
          },
          {
            heading: 'Casa 4 e Família',
            content: `A Casa 4 representa suas raízes, lar e família de origem. Ela mostra sua conexão com o passado, sua necessidade de segurança emocional e como você cria um ambiente doméstico.`,
          },
          {
            heading: 'Casa 11 e Amizades',
            content: `A Casa 11 rege amizades, grupos sociais e aspirações coletivas. Ela indica o tipo de amigos que você atrai, seu papel em grupos e suas esperanças para o futuro.`,
          },
          {
            heading: 'Lua e Emoções Familiares',
            content: `A Lua representa suas emoções e necessidades emocionais. No contexto familiar, ela revela como você processa memórias familiares, seus padrões emocionais e o que você precisa para se sentir seguro e nutrido.`,
          },
        ],
      },
    };

    // Retornar conteúdo do mapa ou conteúdo padrão
    return contentMap[id] || {
      title: 'Interpretação Astrológica',
      icon: UIIcons.Star,
      subtitle: 'Posição Natal • Análise Detalhada',
      sections: [
        {
          heading: 'Visão Geral',
          content: `Esta interpretação explora aspectos importantes do seu mapa astral relacionados a esta área da vida.`,
        },
      ],
    };
  };

  const contentData = getContentData(topicId);

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

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-[#1a1f4a] dark:to-[#1a1f4a] light:to-[#F0E6D2]">
      {/* Header */}
      <header className="border-b border-border/30 backdrop-blur-sm sticky top-0 z-10 bg-background/80">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <AstroButton variant="secondary" size="sm" onClick={onBack} className="flex items-center gap-2">
              <UIIcons.ChevronLeft size={18} />
              <span>Voltar</span>
            </AstroButton>
            <h2 className="text-accent text-xl font-semibold">Interpretação Detalhada</h2>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <button className="p-2 rounded-lg hover:bg-accent/10 transition-colors" title="Favoritar">
              <UIIcons.Bookmark size={20} className="text-secondary" />
            </button>
            <button className="p-2 rounded-lg hover:bg-accent/10 transition-colors" title="Compartilhar">
              <UIIcons.Share2 size={20} className="text-secondary" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content - 2 Column Layout */}
      <div style={{ maxWidth: '100%', margin: '0 auto', padding: '0 1.5rem 2rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
          {/* Left Sidebar - Table of Contents (Sticky) - Only on large screens */}
          <aside style={{ display: 'none' }}>
            <div style={{ position: 'sticky', top: '6rem' }}>
              {/* Navigation Card */}
              <AstroCard className="p-5">
                <h3 className="text-foreground text-sm font-semibold mb-4 text-secondary/80">Navegação</h3>
                <nav className="space-y-1">
                  {navigationSections.map((section) => (
                    <div key={section.id}>
                      <button
                        onClick={() => setActiveSection(section.id)}
                        className={`w-full flex items-center gap-3 p-2.5 rounded-lg transition-all text-left ${
                          activeSection === section.id
                            ? 'bg-accent/20 text-accent font-medium'
                            : 'text-secondary hover:bg-accent/10 hover:text-foreground'
                        }`}
                      >
                        {section.icon && <section.icon size={18} className="flex-shrink-0" />}
                        <span className="text-sm">{section.title}</span>
                      </button>
                      
                      {section.subsections && activeSection === section.id && (
                        <div className="ml-8 mt-1 space-y-0.5">
                          {section.subsections.map((subsection) => (
                            <button
                              key={subsection.id}
                              className="w-full flex items-center gap-2.5 p-2 rounded-md transition-colors text-left text-sm text-secondary hover:bg-accent/10 hover:text-foreground"
                            >
                              {subsection.icon && <subsection.icon size={16} className="flex-shrink-0" />}
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
              <AstroCard className="p-5">
                <div className="space-y-4">
                  <h4 className="text-foreground text-sm font-semibold mb-3">Nesta Interpretação</h4>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
                        <UIIcons.Clock size={16} className="text-accent" />
                      </div>
                      <span className="text-secondary">15 min de leitura</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
                        <UIIcons.Star size={16} className="text-accent" />
                      </div>
                      <span className="text-secondary">Interpretação Premium</span>
                    </div>
                  </div>
                </div>
              </AstroCard>
            </div>
          </aside>

          {/* Right Content Area - Article - Full Width */}
          <main style={{ width: '100%', minWidth: 0 }}>
            <div style={{ 
              backgroundColor: 'hsl(var(--card))', 
              borderRadius: '0.5rem', 
              padding: '2.5rem 3rem', 
              boxShadow: '0px 10px 15px -3px rgba(0, 0, 0, 0.1), 0px 4px 6px -2px rgba(0, 0, 0, 0.05)',
              width: '100%',
              maxWidth: '100%',
              boxSizing: 'border-box',
              margin: '0 auto'
            }}>
              {/* Article Header */}
              <div style={{ marginBottom: '2rem', paddingBottom: '1.5rem', borderBottom: '1px solid hsl(var(--border) / 0.3)' }}>
                <h1 className="text-accent font-bold mb-3" style={{ fontSize: '1.875rem', lineHeight: '1.3', wordBreak: 'break-word', width: '100%' }}>
                  {contentData.title}
                </h1>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'hsl(var(--muted-foreground))', flexWrap: 'wrap' }}>
                  <contentData.icon size={16} style={{ flexShrink: 0, color: 'hsl(var(--accent) / 0.7)' }} />
                  <span style={{ wordBreak: 'break-word' }}>{contentData.subtitle}</span>
                </div>
              </div>

              {/* Article Content */}
              <div style={{ width: '100%', maxWidth: '100%' }}>
                {contentData.sections.map((section, index) => (
                  <div key={index} style={{ marginBottom: '3rem', display: 'flex', gap: '2rem', alignItems: 'flex-start', width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
                    {/* Large Section Number */}
                    <div style={{ flexShrink: 0, width: '4rem', minWidth: '4rem' }}>
                      <span className="text-accent font-bold" style={{ fontSize: '4rem', lineHeight: '1', display: 'block', color: 'hsl(var(--accent))' }}>
                        {index + 1}
                      </span>
                    </div>
                    
                    {/* Section Content */}
                    <div style={{ flex: '1 1 auto', minWidth: 0, width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
                      <h2 className="text-accent font-semibold mb-4" style={{ fontSize: '1.5rem', lineHeight: '1.4', wordBreak: 'break-word', width: '100%', color: 'hsl(var(--accent))', marginBottom: '1rem' }}>
                        {section.heading}
                      </h2>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', width: '100%', maxWidth: '100%' }}>
                        {section.content.split('\n\n').map((paragraph, pIndex) => (
                          <p 
                            key={pIndex} 
                            style={{ 
                              fontSize: '1rem', 
                              lineHeight: '1.8',
                              wordBreak: 'break-word',
                              overflowWrap: 'break-word',
                              width: '100%',
                              maxWidth: '100%',
                              margin: 0,
                              color: 'hsl(var(--muted-foreground))',
                              boxSizing: 'border-box'
                            }}
                          >
                            {paragraph}
                          </p>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Related Topics */}
              <div style={{ marginTop: '4rem', paddingTop: '2.5rem', borderTop: '1px solid hsl(var(--border) / 0.3)', width: '100%' }}>
                <h3 className="text-foreground font-semibold mb-6" style={{ fontSize: '1.125rem' }}>Tópicos Relacionados</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', width: '100%' }}>
                  {[
                    { title: 'Lua na Casa 2', icon: planets[1].icon },
                    { title: 'Mercúrio em Câncer', icon: planets[2].icon },
                    { title: 'Vênus em Gêmeos', icon: planets[3].icon },
                    { title: 'Casa 5 e Criatividade', icon: UIIcons.Star },
                  ].map((topic, i) => (
                    <button
                      key={i}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.75rem',
                        padding: '1rem',
                        borderRadius: '0.5rem',
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border) / 0.3)',
                        textAlign: 'left',
                        width: '100%',
                        minWidth: 0,
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                    >
                      <topic.icon size={24} style={{ flexShrink: 0, color: 'hsl(var(--accent))' }} />
                      <span className="text-foreground" style={{ flex: 1, minWidth: 0, wordBreak: 'break-word' }}>
                        {topic.title}
                      </span>
                      <UIIcons.ChevronDown
                        size={16}
                        className="rotate-[-90deg] text-secondary"
                        style={{ flexShrink: 0 }}
                      />
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};

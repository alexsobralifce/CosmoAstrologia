import React from 'react';
import { UIIcons } from '../ui-icons';
import { FutureTransitsSection } from '../future-transits-section';
import { useLanguage } from '../../i18n';
import { OnboardingData } from '../onboarding';

// ===== GUIA 2026 =====
interface Guide2026SectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const Guide2026Section = ({ userData, onBack }: Guide2026SectionProps) => {
  const { language } = useLanguage();

  // Destaques astrológicos de 2026
  const highlights = language === 'pt' ? [
    { icon: '♃', title: 'Júpiter em Câncer', period: 'Jun 2025 - Jul 2026', desc: 'Expansão emocional e familiar', color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { icon: '♄', title: 'Saturno em Áries', period: 'Mar 2025 - Mai 2026', desc: 'Novos começos estruturados', color: 'text-muted-foreground', bg: 'bg-gray-500/10' },
    { icon: '♅', title: 'Urano em Gêmeos', period: 'Jul 2025 - 2033', desc: 'Revolução na comunicação', color: 'text-teal-500', bg: 'bg-teal-500/10' },
    { icon: '♆', title: 'Netuno em Áries', period: 'Mar 2025 - 2039', desc: 'Nova era espiritual', color: 'text-blue-500', bg: 'bg-blue-500/10' },
  ] : [
    { icon: '♃', title: 'Jupiter in Cancer', period: 'Jun 2025 - Jul 2026', desc: 'Emotional and family expansion', color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { icon: '♄', title: 'Saturn in Aries', period: 'Mar 2025 - May 2026', desc: 'Structured new beginnings', color: 'text-muted-foreground', bg: 'bg-gray-500/10' },
    { icon: '♅', title: 'Uranus in Gemini', period: 'Jul 2025 - 2033', desc: 'Communication revolution', color: 'text-teal-500', bg: 'bg-teal-500/10' },
    { icon: '♆', title: 'Neptune in Aries', period: 'Mar 2025 - 2039', desc: 'New spiritual era', color: 'text-blue-500', bg: 'bg-blue-500/10' },
  ];

  return (
    <div className="transits-section-container">
      {/* Header */}
      <div className="transits-header">
        <div className="transits-header-content">
          <h2 className="transits-title">
            {language === 'pt' ? 'Trânsitos Astrológicos' : 'Astrological Transits'}
          </h2>
          <p className="transits-subtitle">
            {language === 'pt' ? 'Acompanhe os movimentos planetários e suas influências' : 'Track planetary movements and their influences'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="transits-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Destaques do Ano */}
      <div className="transits-highlights-card">
        <h3 className="transits-highlights-title">
          <UIIcons.Star size={18} style={{ color: 'hsl(var(--primary))' }} />
          {language === 'pt' ? 'Destaques Astrológicos' : 'Astrological Highlights'}
        </h3>
        <div className="transits-highlights-grid">
          {highlights.map((item, idx) => (
            <div key={idx} className="transits-highlight-item" style={{
              backgroundColor: item.bg.includes('amber') ? 'hsl(45, 90%, 60% / 0.1)' :
                              item.bg.includes('gray') ? 'hsl(0, 0%, 50% / 0.1)' :
                              item.bg.includes('teal') ? 'hsl(173, 80%, 40% / 0.1)' :
                              item.bg.includes('blue') ? 'hsl(217, 91%, 60% / 0.1)' : 'hsl(var(--muted) / 0.1)',
              borderColor: item.bg.includes('amber') ? 'hsl(45, 90%, 60% / 0.3)' :
                          item.bg.includes('gray') ? 'hsl(0, 0%, 50% / 0.3)' :
                          item.bg.includes('teal') ? 'hsl(173, 80%, 40% / 0.3)' :
                          item.bg.includes('blue') ? 'hsl(217, 91%, 60% / 0.3)' : 'hsl(var(--border) / 0.5)'
            }}>
              <div className="transits-highlight-header">
                <span className="transits-highlight-icon" style={{
                  color: item.color.includes('amber') ? 'hsl(45, 90%, 60%)' :
                         item.color.includes('muted') ? 'hsl(var(--muted-foreground))' :
                         item.color.includes('teal') ? 'hsl(173, 80%, 40%)' :
                         item.color.includes('blue') ? 'hsl(217, 91%, 60%)' : 'hsl(var(--foreground))'
                }}>{item.icon}</span>
                <span className="transits-highlight-period">{item.period}</span>
              </div>
              <p className="transits-highlight-title" style={{
                color: item.color.includes('amber') ? 'hsl(45, 90%, 60%)' :
                       item.color.includes('muted') ? 'hsl(var(--muted-foreground))' :
                       item.color.includes('teal') ? 'hsl(173, 80%, 40%)' :
                       item.color.includes('blue') ? 'hsl(217, 91%, 60%)' : 'hsl(var(--foreground))'
              }}>{item.title}</p>
              <p className="transits-highlight-desc">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Legenda de Tipos de Trânsitos */}
      <div className="transits-legend-card">
        <h3 className="transits-legend-title">
          <UIIcons.Info size={18} style={{ color: 'hsl(var(--primary))' }} />
          {language === 'pt' ? 'Tipos de Trânsitos' : 'Transit Types'}
        </h3>
        <div className="transits-legend-grid">
          <div className="transits-legend-item" style={{
            backgroundColor: 'hsl(45, 90%, 60% / 0.15)',
            borderColor: 'hsl(45, 90%, 60% / 0.3)'
          }}>
            <span className="transits-legend-icon">🌟</span>
            <div className="transits-legend-content">
              <p className="transits-legend-name">{language === 'pt' ? 'Expansão' : 'Expansion'}</p>
              <p className="transits-legend-planet">{language === 'pt' ? 'Júpiter' : 'Jupiter'}</p>
            </div>
          </div>
          <div className="transits-legend-item" style={{
            backgroundColor: 'hsl(25, 5%, 45% / 0.15)',
            borderColor: 'hsl(25, 5%, 45% / 0.3)'
          }}>
            <span className="transits-legend-icon">🏛️</span>
            <div className="transits-legend-content">
              <p className="transits-legend-name">{language === 'pt' ? 'Estrutura' : 'Structure'}</p>
              <p className="transits-legend-planet">{language === 'pt' ? 'Saturno' : 'Saturn'}</p>
            </div>
          </div>
          <div className="transits-legend-item" style={{
            backgroundColor: 'hsl(173, 80%, 40% / 0.15)',
            borderColor: 'hsl(173, 80%, 40% / 0.3)'
          }}>
            <span className="transits-legend-icon">⚡</span>
            <div className="transits-legend-content">
              <p className="transits-legend-name">{language === 'pt' ? 'Mudança' : 'Change'}</p>
              <p className="transits-legend-planet">{language === 'pt' ? 'Urano' : 'Uranus'}</p>
            </div>
          </div>
          <div className="transits-legend-item" style={{
            backgroundColor: 'hsl(280, 70%, 60% / 0.15)',
            borderColor: 'hsl(280, 70%, 60% / 0.3)'
          }}>
            <span className="transits-legend-icon">🌊</span>
            <div className="transits-legend-content">
              <p className="transits-legend-name">{language === 'pt' ? 'Espiritualidade' : 'Spirituality'}</p>
              <p className="transits-legend-planet">{language === 'pt' ? 'Netuno' : 'Neptune'}</p>
            </div>
          </div>
          <div className="transits-legend-item" style={{
            backgroundColor: 'hsl(0, 70%, 60% / 0.15)',
            borderColor: 'hsl(0, 70%, 60% / 0.3)'
          }}>
            <span className="transits-legend-icon">🔥</span>
            <div className="transits-legend-content">
              <p className="transits-legend-name">{language === 'pt' ? 'Transformação' : 'Transformation'}</p>
              <p className="transits-legend-planet">{language === 'pt' ? 'Plutão' : 'Pluto'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Future Transits Component */}
      <div>
        <h3 className="transits-highlights-title" style={{ marginBottom: '1rem' }}>
          <UIIcons.Calendar size={18} style={{ color: 'hsl(var(--primary))' }} />
          {language === 'pt' ? 'Seus Trânsitos Pessoais' : 'Your Personal Transits'}
        </h3>
        <FutureTransitsSection />
      </div>
    </div>
  );
};

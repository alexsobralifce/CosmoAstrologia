import { useState } from 'react';
import { ArrowRight, Mail, Star, Users, FileText, TrendingUp, Zap, Target, Heart, Check, Shield } from 'lucide-react';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import '../styles/landing-page.css';

interface LandingPageProps {
  onEnter: () => void;
  onGetStarted: () => void;
}

export function LandingPage({ onEnter, onGetStarted }: LandingPageProps) {
  const [email, setEmail] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.trim()) {
      onGetStarted();
    }
  };

  return (
    <div className="landing-page">
      {/* Header */}
      <header className="landing-header">
        <div className="landing-header-content">
          <div className="landing-logo">
            <div className="landing-logo-icon">
              <Star size={28} fill="currentColor" />
            </div>
            <div className="landing-logo-text">
              <h1>CosmoAstral</h1>
              <p>Sua jornada de autoconhecimento</p>
            </div>
          </div>
          <AstroButton onClick={onEnter} className="landing-header-cta">
            Entrar
            <ArrowRight size={16} />
          </AstroButton>
        </div>
      </header>

      {/* Hero Section */}
      <section className="landing-hero">
        <div className="landing-hero-stars">
          {Array.from({ length: 20 }).map((_, i) => (
            <div
              key={i}
              className="landing-star"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                opacity: Math.random() * 0.5 + 0.3,
                animationDelay: `${Math.random() * 3}s`,
              }}
            />
          ))}
        </div>
        <div className="landing-hero-content">
          <div className="landing-hero-badge">
            🎁 Acesso 100% gratuito ao seu mapa astral completo
          </div>
          <h2 className="landing-hero-title">
            Descubra os <span className="landing-hero-title-accent">segredos das estrelas</span> e transforme sua vida
          </h2>
          <p className="landing-hero-description">
            Entenda quem você realmente é, tome decisões com confiança e alcance seu verdadeiro potencial através da astrologia e numerologia.
          </p>
          <div className="landing-hero-trust">
            <div className="landing-hero-trust-item">
              <Check size={16} />
              <span>Grátis para começar</span>
            </div>
            <div className="landing-hero-trust-item">
              <Check size={16} />
              <span>Sem cartão de crédito</span>
            </div>
            <div className="landing-hero-trust-item">
              <Check size={16} />
              <span>Acesso imediato</span>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="landing-social-proof">
        <div className="landing-social-proof-grid">
          <div className="landing-social-proof-item">
            <div className="landing-social-proof-stars">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star key={i} size={20} fill="currentColor" />
              ))}
            </div>
            <div className="landing-social-proof-value">4.9/5</div>
            <div className="landing-social-proof-label">Avaliação média</div>
          </div>
          <div className="landing-social-proof-item">
            <Users size={32} />
            <div className="landing-social-proof-value">+10.000</div>
            <div className="landing-social-proof-label">Usuários ativos</div>
          </div>
          <div className="landing-social-proof-item">
            <FileText size={32} />
            <div className="landing-social-proof-value">+50.000</div>
            <div className="landing-social-proof-label">Mapas gerados</div>
          </div>
          <div className="landing-social-proof-item">
            <TrendingUp size={32} />
            <div className="landing-social-proof-value">98%</div>
            <div className="landing-social-proof-label">Satisfação</div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="landing-benefits">
        <div className="landing-benefits-content">
          <div className="landing-section-header">
            <h3 className="landing-section-title">O que você vai conquistar</h3>
            <p className="landing-section-description">
              Milhares de pessoas já transformaram suas vidas. Chegou a sua vez.
            </p>
          </div>
          <div className="landing-benefits-grid">
            <div className="landing-benefit-card">
              <div className="landing-benefit-icon landing-benefit-icon-purple">
                <Zap size={32} />
              </div>
              <h4 className="landing-benefit-title">Descubra seu verdadeiro potencial</h4>
              <p className="landing-benefit-description">
                Entenda seus dons naturais, talentos ocultos e o melhor caminho para sua realização pessoal e profissional.
              </p>
            </div>
            <div className="landing-benefit-card">
              <div className="landing-benefit-icon landing-benefit-icon-orange">
                <Target size={32} />
              </div>
              <h4 className="landing-benefit-title">Tome decisões com mais confiança</h4>
              <p className="landing-benefit-description">
                Saiba os melhores momentos para agir, investir em relacionamentos e fazer mudanças importantes na vida.
              </p>
            </div>
            <div className="landing-benefit-card">
              <div className="landing-benefit-icon landing-benefit-icon-pink">
                <Heart size={32} />
              </div>
              <h4 className="landing-benefit-title">Melhore seus relacionamentos</h4>
              <p className="landing-benefit-description">
                Compreenda suas dinâmicas afetivas e descubra como se conectar melhor com as pessoas que ama.
              </p>
            </div>
          </div>
          <form onSubmit={handleSubmit} className="landing-benefits-cta">
            <div className="landing-hero-input-wrapper">
              <Mail className="landing-hero-input-icon" size={20} />
              <AstroInput
                type="email"
                placeholder="Digite seu melhor email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="landing-hero-input"
              />
            </div>
            <AstroButton type="submit" className="landing-hero-button">
              Começar Grátis
              <ArrowRight size={20} />
            </AstroButton>
          </form>
        </div>
      </section>

      {/* Features Section */}
      <section className="landing-features">
        <div className="landing-features-content">
          <div className="landing-features-left">
            <div className="landing-features-badge">Plataforma Completa</div>
            <h3 className="landing-features-title">
              Tudo que você precisa para se conhecer profundamente
            </h3>
            <p className="landing-features-description">
              Acesso completo e ilimitado a todas as ferramentas de astrologia e numerologia. Sem cobranças ocultas, sem surpresas.
            </p>
            <ul className="landing-features-list">
              {[
                'Mapa Astral completo e personalizado',
                'Análise numerológica detalhada',
                'Previsões para o seu ano (Revolução Solar)',
                'Compatibilidade amorosa e profissional',
                'Acompanhamento de trânsitos atuais',
                'Relatórios em PDF para download',
                'Atualizações diárias personalizadas',
                'Suporte especializado',
              ].map((feature, i) => (
                <li key={i} className="landing-features-item">
                  <Check size={16} />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
            <div className="landing-features-security">
              <Shield size={20} />
              <span>Seus dados estão seguros e protegidos</span>
            </div>
          </div>
          <div className="landing-features-right">
            <div className="landing-features-card">
              <div className="landing-features-card-stars">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="landing-features-card-star" />
                ))}
              </div>
              <div className="landing-features-card-badge">⚡ Oferta Especial</div>
              <h4 className="landing-features-card-title">Comece gratuitamente hoje</h4>
              <p className="landing-features-card-description">
                Crie sua conta agora e tenha acesso imediato ao seu mapa astral completo. Sem necessidade de cartão de crédito.
              </p>
              <form onSubmit={handleSubmit} className="landing-features-card-cta">
                <div className="landing-hero-input-wrapper">
                  <Mail className="landing-hero-input-icon" size={20} />
                  <AstroInput
                    type="email"
                    placeholder="Digite seu melhor email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="landing-hero-input"
                  />
                </div>
                <AstroButton type="submit" className="landing-features-card-button">
                  Começar Grátis
                  <ArrowRight size={20} />
                </AstroButton>
              </form>
              <div className="landing-features-card-proof">
                <p className="landing-features-card-proof-text">Junte-se a milhares de usuários satisfeitos:</p>
                <div className="landing-features-card-proof-stats">
                  <div className="landing-features-card-proof-stars">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star key={i} size={20} fill="currentColor" />
                    ))}
                  </div>
                  <div className="landing-features-card-proof-divider" />
                  <div className="landing-features-card-proof-stat">
                    <div className="landing-features-card-proof-value">+10.000</div>
                    <div className="landing-features-card-proof-label">Usuários ativos</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="landing-testimonials">
        <div className="landing-testimonials-content">
          <div className="landing-section-header">
            <div className="landing-testimonials-badge">Depoimentos Reais</div>
            <h3 className="landing-section-title">Veja o que dizem quem já começou</h3>
            <p className="landing-section-description">
              Milhares de vidas transformadas através do autoconhecimento
            </p>
          </div>
          <div className="landing-testimonials-grid">
            {[
              {
                quote: '"O mapa astral me ajudou a entender meus pontos fortes e usar isso no meu negócio. Resultados incríveis em 3 meses!"',
                name: 'Maria Silva',
                role: 'Empresária',
                emoji: '👩‍💼',
              },
              {
                quote: '"A revolução solar foi exata. Consegui me preparar para mudanças profissionais e hoje estou no emprego dos sonhos."',
                name: 'João Santos',
                role: 'Analista de TI',
                emoji: '👨‍💻',
              },
              {
                quote: '"Uso as análises com meus pacientes. A precisão é impressionante e ajuda muito no processo terapêutico."',
                name: 'Ana Costa',
                role: 'Psicóloga',
                emoji: '👩‍⚕️',
              },
            ].map((testimonial, i) => (
              <div key={i} className="landing-testimonial-card">
                <div className="landing-testimonial-stars">
                  {Array.from({ length: 5 }).map((_, j) => (
                    <Star key={j} size={20} fill="currentColor" />
                  ))}
                </div>
                <p className="landing-testimonial-quote">{testimonial.quote}</p>
                <div className="landing-testimonial-author">
                  <div className="landing-testimonial-avatar">{testimonial.emoji}</div>
                  <div className="landing-testimonial-info">
                    <div className="landing-testimonial-name">{testimonial.name}</div>
                    <div className="landing-testimonial-role">{testimonial.role}</div>
                  </div>
                </div>
                <div className="landing-testimonial-quote-icon">"</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="landing-final-cta">
        <div className="landing-final-cta-content">
          <h3 className="landing-final-cta-title">Pronto para descobrir seu verdadeiro caminho?</h3>
          <p className="landing-final-cta-description">
            Não deixe para depois. Comece hoje sua jornada de autoconhecimento e desbloqueie todo o seu potencial.
          </p>
          <form onSubmit={handleSubmit} className="landing-hero-cta">
            <div className="landing-hero-input-wrapper">
              <Mail className="landing-hero-input-icon" size={20} />
              <AstroInput
                type="email"
                placeholder="Digite seu melhor email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="landing-hero-input"
              />
            </div>
            <AstroButton type="submit" className="landing-hero-button">
              Começar Grátis
              <ArrowRight size={20} />
            </AstroButton>
          </form>
          <div className="landing-hero-trust">
            <div className="landing-hero-trust-item">
              <Check size={16} />
              <span>100% Gratuito para começar</span>
            </div>
            <div className="landing-hero-trust-item">
              <Check size={16} />
              <span>Sem cartão de crédito</span>
            </div>
            <div className="landing-hero-trust-item">
              <Check size={16} />
              <span>Acesso imediato</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <p>© 2025 CosmoAstral. Desbloqueie os mistérios das suas estrelas.</p>
      </footer>
    </div>
  );
}


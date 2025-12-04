import React, { useState } from 'react';
import { UIIcons } from './ui-icons';
import { apiService } from '../services/api';
import { useLanguage } from '../i18n';
import { OnboardingData } from './onboarding';
import { AstroCard } from './astro-card';
import { AstroButton } from './astro-button';
import { formatGroqText } from '../utils/formatGroqText';
import '../styles/numerology-section.css';

interface NumerologySectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

interface NumerologyMap {
  full_name: string;
  birth_date: string;
  life_path: {
    number: number;
    raw_total: number;
    is_master: boolean;
    day: number;
    day_reduced: number;
    month: number;
    month_reduced: number;
    year: number;
    year_reduced: number;
  };
  destiny: {
    number: number;
    raw_total: number;
    is_master: boolean;
  };
  soul: {
    number: number;
    raw_total: number;
    is_master: boolean;
  };
  personality: {
    number: number;
    raw_total: number;
    is_master: boolean;
  };
  birthday: {
    number: number;
    day: number;
    is_master: boolean;
  };
  maturity: {
    number: number;
    raw_total: number;
    is_master: boolean;
  };
  pinnacles: Array<{
    number: number;
    period: string;
    start_age: number;
    end_age: number | null;
  }>;
  challenges: Array<{
    number: number;
    period: string;
    start_age: number;
    end_age: number | null;
  }>;
  personal_year: {
    number: number;
    year: number;
    raw_total: number;
    is_master: boolean;
  };
  birth_grid: {
    grid: Record<number, number>;
    arrows_strength: string[];
    arrows_weakness: string[];
    missing_numbers: number[];
  };
  karmic_debts: number[];
  life_cycle: {
    cycle: string;
    cycle_number: number;
    age: number;
  };
}

export const NumerologySection = ({ userData, onBack }: NumerologySectionProps) => {
  const { t, language } = useLanguage();
  const [numerologyMap, setNumerologyMap] = useState<NumerologyMap | null>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingInterpretation, setIsLoadingInterpretation] = useState(false);
  const [error, setError] = useState<string>('');
  const [quantitiesExplanation, setQuantitiesExplanation] = useState<string>('');
  const [isLoadingQuantities, setIsLoadingQuantities] = useState(false);

  // Buscar mapa numerológico
  const fetchNumerologyMap = async () => {
    try {
      setIsLoading(true);
      setError('');
      setInterpretation(''); // Limpar interpretação anterior
      
      const result = await apiService.getNumerologyMap();
      setNumerologyMap(result);
    } catch (err: any) {
      // Log apenas em desenvolvimento
      if (import.meta.env.DEV) {
        console.error('[Numerology] Erro ao buscar mapa:', err);
      }
      setError(err.message || (language === 'pt' 
        ? 'Erro ao calcular mapa numerológico' 
        : 'Error calculating numerology map'));
    } finally {
      setIsLoading(false);
    }
  };

  // Buscar interpretação numerológica
  const fetchInterpretation = async () => {
    if (!numerologyMap) {
      setError(language === 'pt' 
        ? 'Primeiro gere o mapa numerológico' 
        : 'First generate the numerology map');
      return;
    }

    try {
      setIsLoadingInterpretation(true);
      setError('');
      
      const result = await apiService.getNumerologyInterpretation({
        language: language
      });
      
      setInterpretation(result.interpretation);
    } catch (err: any) {
      // Log apenas em desenvolvimento
      if (import.meta.env.DEV) {
        console.error('[Numerology] Erro ao buscar interpretação:', err);
      }
      setError(err.message || (language === 'pt' 
        ? 'Erro ao gerar interpretação numerológica' 
        : 'Error generating numerology interpretation'));
    } finally {
      setIsLoadingInterpretation(false);
    }
  };

  const formatNumber = (num: number, isMaster: boolean) => {
    if (isMaster) {
      return (
        <span className="numerology-master-number">
          {num}
          <span className="numerology-master-badge">
            {language === 'pt' ? 'Mestre' : 'Master'}
          </span>
        </span>
      );
    }
    return <span className="numerology-number">{num}</span>;
  };

  return (
    <div className="dashboard-section-container">
      {/* Header */}
      <div className="dashboard-section-header">
        <button
          onClick={onBack}
          className="dashboard-section-back-button"
          aria-label={language === 'pt' ? 'Voltar' : 'Back'}
        >
          <UIIcons.ArrowLeft size={20} />
        </button>
        <div className="dashboard-section-header-content">
          <div className="dashboard-section-header-icon">
            <UIIcons.Hash size={32} className="text-accent" />
          </div>
          <div>
            <h1 className="dashboard-section-title">
              {language === 'pt' ? 'Mapa Numerológico' : 'Numerology Map'}
            </h1>
            <p className="dashboard-section-subtitle">
              {language === 'pt' 
                ? 'Descubra os números que regem sua vida através da numerologia pitagórica'
                : 'Discover the numbers that rule your life through Pythagorean numerology'}
            </p>
          </div>
        </div>
      </div>

      {/* Conteúdo */}
      <div className="dashboard-section-content">
        {/* Botão para gerar mapa numerológico */}
        {!numerologyMap && !isLoading && (
          <AstroCard>
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <p style={{ marginBottom: '1.5rem', color: 'hsl(var(--muted-foreground))' }}>
                {language === 'pt' 
                  ? 'Clique no botão abaixo para gerar seu mapa numerológico completo'
                  : 'Click the button below to generate your complete numerology map'}
              </p>
              <AstroButton
                onClick={fetchNumerologyMap}
                variant="primary"
                size="md"
                disabled={isLoading}
              >
                {isLoading 
                  ? (language === 'pt' ? 'Gerando...' : 'Generating...')
                  : (language === 'pt' ? 'Gerar Mapa Numerológico' : 'Generate Numerology Map')
                }
              </AstroButton>
            </div>
          </AstroCard>
        )}

        {/* Loading State */}
        {isLoading && (
          <AstroCard>
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <UIIcons.Loader size={24} className="animate-spin text-accent" style={{ margin: '0 auto' }} />
              <p style={{ marginTop: '1rem', color: 'hsl(var(--muted-foreground))' }}>
                {language === 'pt' ? 'Calculando mapa numerológico...' : 'Calculating numerology map...'}
              </p>
            </div>
          </AstroCard>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <AstroCard>
            <div style={{ padding: '1.5rem', color: 'hsl(var(--destructive))' }}>
              <UIIcons.AlertCircle size={20} className="text-destructive" style={{ marginBottom: '0.5rem' }} />
              <p>{error}</p>
              {numerologyMap && (
                <AstroButton 
                  onClick={fetchNumerologyMap}
                  variant="primary"
                  size="md"
                  style={{ marginTop: '1rem' }}
                >
                  {language === 'pt' ? 'Tentar novamente' : 'Try again'}
                </AstroButton>
              )}
            </div>
          </AstroCard>
        )}

      {/* Numerology Map Content */}
      {numerologyMap && !isLoading && (
        <div className="numerology-map-container">
          {/* Main Numbers Grid */}
          <div className="numerology-main-grid">
            {/* Life Path */}
            <AstroCard className="numerology-card numerology-card-primary">
              <div className="numerology-card-header">
                <h3 className="numerology-card-title">
                  {language === 'pt' ? 'Caminho de Vida' : 'Life Path'}
                </h3>
                <div className="numerology-card-number-large">
                  {formatNumber(numerologyMap.life_path.number, numerologyMap.life_path.is_master)}
                </div>
              </div>
              <div className="numerology-card-content">
                <p className="numerology-card-description">
                  {language === 'pt' 
                    ? 'O número mais importante da numerologia. Representa o caminho que você deve seguir nesta vida.'
                    : 'The most important number in numerology. Represents the path you should follow in this life.'}
                </p>
                <div className="numerology-card-details">
                  <div className="numerology-detail-item">
                    <span className="numerology-detail-label">
                      {language === 'pt' ? 'Dia:' : 'Day:'}
                    </span>
                    <span className="numerology-detail-value">
                      {numerologyMap.life_path.day} → {numerologyMap.life_path.day_reduced}
                    </span>
                  </div>
                  <div className="numerology-detail-item">
                    <span className="numerology-detail-label">
                      {language === 'pt' ? 'Mês:' : 'Month:'}
                    </span>
                    <span className="numerology-detail-value">
                      {numerologyMap.life_path.month} → {numerologyMap.life_path.month_reduced}
                    </span>
                  </div>
                  <div className="numerology-detail-item">
                    <span className="numerology-detail-label">
                      {language === 'pt' ? 'Ano:' : 'Year:'}
                    </span>
                    <span className="numerology-detail-value">
                      {numerologyMap.life_path.year} → {numerologyMap.life_path.year_reduced}
                    </span>
                  </div>
                </div>
              </div>
            </AstroCard>

            {/* Destiny / Expression */}
            <AstroCard className="numerology-card">
              <div className="numerology-card-header">
                <h3 className="numerology-card-title">
                  {language === 'pt' ? 'Número do Destino' : 'Destiny Number'}
                </h3>
                <div className="numerology-card-number">
                  {formatNumber(numerologyMap.destiny.number, numerologyMap.destiny.is_master)}
                </div>
              </div>
              <div className="numerology-card-content">
                <p className="numerology-card-description">
                  {language === 'pt' 
                    ? 'Também conhecido como Número da Expressão. Revela seus talentos naturais e potencial de realização.'
                    : 'Also known as Expression Number. Reveals your natural talents and potential for achievement.'}
                </p>
              </div>
            </AstroCard>

            {/* Soul / Heart's Desire */}
            <AstroCard className="numerology-card">
              <div className="numerology-card-header">
                <h3 className="numerology-card-title">
                  {language === 'pt' ? 'Número da Alma' : 'Soul Number'}
                </h3>
                <div className="numerology-card-number">
                  {formatNumber(numerologyMap.soul.number, numerologyMap.soul.is_master)}
                </div>
              </div>
              <div className="numerology-card-content">
                <p className="numerology-card-description">
                  {language === 'pt' 
                    ? 'Também conhecido como Desejo do Coração. Revela suas motivações internas e o que realmente deseja.'
                    : 'Also known as Heart\'s Desire. Reveals your internal motivations and what you truly desire.'}
                </p>
              </div>
            </AstroCard>

            {/* Personality */}
            <AstroCard className="numerology-card">
              <div className="numerology-card-header">
                <h3 className="numerology-card-title">
                  {language === 'pt' ? 'Número da Personalidade' : 'Personality Number'}
                </h3>
                <div className="numerology-card-number">
                  {formatNumber(numerologyMap.personality.number, numerologyMap.personality.is_master)}
                </div>
              </div>
              <div className="numerology-card-content">
                <p className="numerology-card-description">
                  {language === 'pt' 
                    ? 'Revela como você se apresenta ao mundo e como os outros o percebem.'
                    : 'Reveals how you present yourself to the world and how others perceive you.'}
                </p>
              </div>
            </AstroCard>

            {/* Birthday */}
            <AstroCard className="numerology-card">
              <div className="numerology-card-header">
                <h3 className="numerology-card-title">
                  {language === 'pt' ? 'Número do Aniversário' : 'Birthday Number'}
                </h3>
                <div className="numerology-card-number">
                  {formatNumber(numerologyMap.birthday.number, numerologyMap.birthday.is_master)}
                </div>
              </div>
              <div className="numerology-card-content">
                <p className="numerology-card-description">
                  {language === 'pt' 
                    ? 'Revela talentos e habilidades especiais que você possui.'
                    : 'Reveals special talents and abilities you possess.'}
                </p>
              </div>
            </AstroCard>

            {/* Maturity */}
            <AstroCard className="numerology-card">
              <div className="numerology-card-header">
                <h3 className="numerology-card-title">
                  {language === 'pt' ? 'Número da Maturidade' : 'Maturity Number'}
                </h3>
                <div className="numerology-card-number">
                  {formatNumber(numerologyMap.maturity.number, numerologyMap.maturity.is_master)}
                </div>
              </div>
              <div className="numerology-card-content">
                <p className="numerology-card-description">
                  {language === 'pt' 
                    ? 'Indica o potencial que você desenvolverá na segunda metade da vida.'
                    : 'Indicates the potential you will develop in the second half of life.'}
                </p>
              </div>
            </AstroCard>
          </div>

          {/* Pinnacles */}
          <AstroCard className="numerology-section-card">
            <h2 className="numerology-section-title">
              {language === 'pt' ? 'Pináculos da Vida' : 'Life Pinnacles'}
            </h2>
            <p className="numerology-section-subtitle">
              {language === 'pt' 
                ? 'Períodos de crescimento e oportunidades em diferentes fases da vida'
                : 'Periods of growth and opportunities in different phases of life'}
            </p>
            <div className="numerology-pinnacles-grid">
              {numerologyMap.pinnacles.map((pinnacle, index) => (
                <div key={index} className="numerology-pinnacle-item">
                  <div className="numerology-pinnacle-number">
                    {formatNumber(pinnacle.number, false)}
                  </div>
                  <div className="numerology-pinnacle-info">
                    <h4 className="numerology-pinnacle-title">
                      {language === 'pt' ? `Pináculo ${index + 1}` : `Pinnacle ${index + 1}`}
                    </h4>
                    <p className="numerology-pinnacle-period">{pinnacle.period}</p>
                  </div>
                </div>
              ))}
            </div>
          </AstroCard>

          {/* Challenges */}
          <AstroCard className="numerology-section-card">
            <h2 className="numerology-section-title">
              {language === 'pt' ? 'Desafios da Vida' : 'Life Challenges'}
            </h2>
            <p className="numerology-section-subtitle">
              {language === 'pt' 
                ? 'Lições e obstáculos que você enfrentará em diferentes períodos'
                : 'Lessons and obstacles you will face in different periods'}
            </p>
            <div className="numerology-challenges-grid">
              {numerologyMap.challenges.map((challenge, index) => (
                <div key={index} className="numerology-challenge-item">
                  <div className="numerology-challenge-number">
                    {formatNumber(challenge.number, false)}
                  </div>
                  <div className="numerology-challenge-info">
                    <h4 className="numerology-challenge-title">
                      {language === 'pt' ? `Desafio ${index + 1}` : `Challenge ${index + 1}`}
                    </h4>
                    <p className="numerology-challenge-period">{challenge.period}</p>
                  </div>
                </div>
              ))}
            </div>
          </AstroCard>

          {/* Personal Year */}
          <AstroCard className="numerology-section-card">
            <h2 className="numerology-section-title">
              {language === 'pt' ? 'Ano Pessoal' : 'Personal Year'}
            </h2>
            <p className="numerology-section-subtitle">
              {language === 'pt' 
                ? `Energia e temas para o ano de ${numerologyMap.personal_year.year}`
                : `Energy and themes for the year ${numerologyMap.personal_year.year}`}
            </p>
            <div className="numerology-personal-year">
              <div className="numerology-personal-year-number">
                {formatNumber(numerologyMap.personal_year.number, numerologyMap.personal_year.is_master)}
              </div>
              <p className="numerology-personal-year-description">
                {language === 'pt' 
                  ? 'O número do ano pessoal indica os temas e oportunidades que estarão presentes neste ano.'
                  : 'The personal year number indicates the themes and opportunities that will be present this year.'}
              </p>
            </div>
          </AstroCard>

          {/* Birth Grid */}
          {numerologyMap.birth_grid && (
            <AstroCard className="numerology-section-card">
              <h2 className="numerology-section-title">
                {language === 'pt' ? 'Grade de Nascimento' : 'Birth Grid'}
              </h2>
              <p className="numerology-section-subtitle">
                {language === 'pt' 
                  ? 'Análise das setas de força, fraqueza e lições cármicas'
                  : 'Analysis of strength arrows, weakness arrows and karmic lessons'}
              </p>
              
              {/* Visualização da Grade 3x3 */}
              {numerologyMap.birth_grid.grid && (
                <div style={{ marginBottom: '2rem' }}>
                  <h3 className="numerology-section-subtitle" style={{ marginBottom: '1rem' }}>
                    {language === 'pt' ? 'Grade 3x3' : '3x3 Grid'}
                  </h3>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: '0.5rem',
                    maxWidth: '300px',
                    margin: '0 auto'
                  }}>
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => {
                      const count = numerologyMap.birth_grid.grid[num] || 0;
                      const isMissing = numerologyMap.birth_grid.missing_numbers?.includes(num);
                      const hasNumber = count > 0;
                      
                      return (
                        <div
                          key={num}
                          style={{
                            aspectRatio: '1',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: `2px solid ${isMissing ? 'hsl(var(--destructive) / 0.5)' : hasNumber ? 'hsl(var(--accent) / 0.5)' : 'hsl(var(--border))'}`,
                            borderRadius: '0.5rem',
                            backgroundColor: isMissing 
                              ? 'hsl(var(--destructive) / 0.1)' 
                              : hasNumber 
                                ? 'hsl(var(--accent) / 0.1)' 
                                : 'hsl(var(--muted) / 0.3)',
                            position: 'relative'
                          }}
                        >
                          <span style={{
                            fontSize: '1.25rem',
                            fontWeight: '700',
                            color: isMissing 
                              ? 'hsl(var(--destructive))' 
                              : hasNumber 
                                ? 'hsl(var(--accent))' 
                                : 'hsl(var(--muted-foreground))'
                          }}>
                            {num}
                          </span>
                          {count > 0 && (
                            <span style={{
                              fontSize: '0.75rem',
                              color: 'hsl(var(--muted-foreground))',
                              marginTop: '0.25rem'
                            }}>
                              {count}x
                            </span>
                          )}
                          {isMissing && (
                            <span style={{
                              position: 'absolute',
                              top: '0.25rem',
                              right: '0.25rem',
                              fontSize: '0.625rem',
                              color: 'hsl(var(--destructive))',
                              fontWeight: '600'
                            }}>
                              ✗
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                  
                  {/* Legenda */}
                  <div style={{
                    marginTop: '1rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem',
                    fontSize: '0.875rem',
                    color: 'hsl(var(--muted-foreground))'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{
                        width: '1rem',
                        height: '1rem',
                        backgroundColor: 'hsl(var(--accent) / 0.1)',
                        border: '2px solid hsl(var(--accent) / 0.5)',
                        borderRadius: '0.25rem'
                      }} />
                      <span>{language === 'pt' ? 'Número presente' : 'Number present'}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{
                        width: '1rem',
                        height: '1rem',
                        backgroundColor: 'hsl(var(--destructive) / 0.1)',
                        border: '2px solid hsl(var(--destructive) / 0.5)',
                        borderRadius: '0.25rem'
                      }} />
                      <span>{language === 'pt' ? 'Número faltante (Lição Cármica)' : 'Missing number (Karmic Lesson)'}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{
                        width: '1rem',
                        height: '1rem',
                        backgroundColor: 'hsl(var(--muted) / 0.3)',
                        border: '2px solid hsl(var(--border))',
                        borderRadius: '0.25rem'
                      }} />
                      <span>{language === 'pt' ? 'Número ausente' : 'Number absent'}</span>
                    </div>
                  </div>
                  
                  {/* Explicação sobre Quantidades */}
                  <div style={{ marginTop: '1.5rem' }}>
                    <button
                      onClick={async () => {
                        if (!numerologyMap.birth_grid.grid) return;
                        setIsLoadingQuantities(true);
                        try {
                          const result = await apiService.getBirthGridQuantitiesInterpretation({
                            grid: numerologyMap.birth_grid.grid,
                            language: language
                          });
                          setQuantitiesExplanation(result.explanation);
                        } catch (err: any) {
                          console.error('[Numerology] Erro ao buscar explicação de quantidades:', err);
                          setQuantitiesExplanation(language === 'pt' 
                            ? 'Erro ao buscar explicação sobre as quantidades na grade.'
                            : 'Error fetching quantities explanation.');
                        } finally {
                          setIsLoadingQuantities(false);
                        }
                      }}
                      style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: 'hsl(var(--accent) / 0.1)',
                        border: '1px solid hsl(var(--accent) / 0.3)',
                        borderRadius: '0.5rem',
                        color: 'hsl(var(--accent))',
                        fontSize: '0.875rem',
                        fontWeight: '500',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        marginBottom: '1rem'
                      }}
                      disabled={isLoadingQuantities}
                    >
                      {isLoadingQuantities ? (
                        <>
                          <div className="numerology-spinner" style={{ width: '1rem', height: '1rem' }} />
                          {language === 'pt' ? 'Buscando explicação...' : 'Fetching explanation...'}
                        </>
                      ) : (
                        <>
                          <UIIcons.Info size={16} />
                          {language === 'pt' ? 'O que significam as quantidades (10x, 5x, etc.)?' : 'What do the quantities (10x, 5x, etc.) mean?'}
                        </>
                      )}
                    </button>
                    
                    {quantitiesExplanation && (
                      <div style={{
                        padding: '1rem',
                        backgroundColor: 'hsl(var(--muted) / 0.2)',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '0.75rem',
                        marginTop: '0.5rem'
                      }}>
                        <h4 style={{
                          margin: '0 0 0.75rem 0',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: 'hsl(var(--accent))',
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em'
                        }}>
                          {language === 'pt' ? 'Significado das Quantidades na Grade' : 'Meaning of Quantities in the Grid'}
                        </h4>
                        <div style={{
                          fontSize: '0.875rem',
                          color: 'hsl(var(--foreground))',
                          lineHeight: '1.6',
                          whiteSpace: 'pre-wrap'
                        }}>
                          {quantitiesExplanation}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Setas de Força */}
              {numerologyMap.birth_grid.arrows_strength && numerologyMap.birth_grid.arrows_strength.length > 0 && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 className="numerology-section-subtitle" style={{ color: 'hsl(var(--accent))', marginBottom: '0.5rem' }}>
                    {language === 'pt' ? 'Setas de Força' : 'Strength Arrows'}
                  </h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {numerologyMap.birth_grid.arrows_strength.map((arrow, index) => (
                      <span key={index} style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: 'hsl(var(--accent) / 0.1)',
                        border: '1px solid hsl(var(--accent) / 0.3)',
                        borderRadius: '0.5rem',
                        fontSize: '0.875rem',
                        color: 'hsl(var(--accent))'
                      }}>
                        {arrow}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Setas de Fraqueza */}
              {numerologyMap.birth_grid.arrows_weakness && numerologyMap.birth_grid.arrows_weakness.length > 0 && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 className="numerology-section-subtitle" style={{ color: 'hsl(var(--destructive))', marginBottom: '0.5rem' }}>
                    {language === 'pt' ? 'Setas de Fraqueza' : 'Weakness Arrows'}
                  </h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {numerologyMap.birth_grid.arrows_weakness.map((arrow, index) => (
                      <span key={index} style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: 'hsl(var(--destructive) / 0.1)',
                        border: '1px solid hsl(var(--destructive) / 0.3)',
                        borderRadius: '0.5rem',
                        fontSize: '0.875rem',
                        color: 'hsl(var(--destructive))'
                      }}>
                        {arrow}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Números Faltantes (Lições Cármicas) */}
              {numerologyMap.birth_grid.missing_numbers && numerologyMap.birth_grid.missing_numbers.length > 0 && (
                <div>
                  <h3 className="numerology-section-subtitle" style={{ marginBottom: '0.5rem' }}>
                    {language === 'pt' ? 'Números Faltantes (Lições Cármicas)' : 'Missing Numbers (Karmic Lessons)'}
                  </h3>
                  <p style={{ marginBottom: '1rem', fontSize: '0.875rem', color: 'hsl(var(--muted-foreground))' }}>
                    {language === 'pt' 
                      ? 'Estes números não aparecem no seu nome e representam lições que você precisa aprender nesta vida:'
                      : 'These numbers do not appear in your name and represent lessons you need to learn in this life:'}
                  </p>
                  
                  {/* Descrições das Lições Cármicas */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {numerologyMap.birth_grid.missing_numbers.map((num, index) => {
                      const karmicLessons: Record<number, { title: { pt: string; en: string }; description: { pt: string; en: string }; whatToLearn: { pt: string; en: string } }> = {
                        1: {
                          title: { pt: 'Número 1 - Liderança e Independência', en: 'Number 1 - Leadership and Independence' },
                          description: { 
                            pt: 'O número 1 representa iniciativa, liderança e independência. Quando este número está faltando, você pode ter dificuldade em tomar decisões sozinho, iniciar projetos ou assumir posições de liderança.',
                            en: 'Number 1 represents initiative, leadership and independence. When this number is missing, you may have difficulty making decisions alone, starting projects or assuming leadership positions.'
                          },
                          whatToLearn: {
                            pt: 'Você precisa aprender a confiar em sua própria capacidade de liderar e tomar decisões. Pratique iniciar projetos sozinhos, assumir responsabilidades e expressar suas opiniões com confiança. Desenvolva sua independência emocional e financeira.',
                            en: 'You need to learn to trust your own ability to lead and make decisions. Practice starting projects alone, taking responsibility and expressing your opinions with confidence. Develop your emotional and financial independence.'
                          }
                        },
                        2: {
                          title: { pt: 'Número 2 - Cooperação e Diplomacia', en: 'Number 2 - Cooperation and Diplomacy' },
                          description: {
                            pt: 'O número 2 representa cooperação, diplomacia e sensibilidade. Quando este número está faltando, você pode ter dificuldade em trabalhar em equipe, ser diplomático ou expressar suas emoções de forma equilibrada.',
                            en: 'Number 2 represents cooperation, diplomacy and sensitivity. When this number is missing, you may have difficulty working in teams, being diplomatic or expressing your emotions in a balanced way.'
                          },
                          whatToLearn: {
                            pt: 'Você precisa aprender a valorizar parcerias e colaborações. Pratique ouvir mais, ser paciente com os outros e encontrar soluções que beneficiem todos. Desenvolva sua capacidade de mediar conflitos e criar harmonia em relacionamentos.',
                            en: 'You need to learn to value partnerships and collaborations. Practice listening more, being patient with others and finding solutions that benefit everyone. Develop your ability to mediate conflicts and create harmony in relationships.'
                          }
                        },
                        3: {
                          title: { pt: 'Número 3 - Criatividade e Expressão', en: 'Number 3 - Creativity and Expression' },
                          description: {
                            pt: 'O número 3 representa criatividade, expressão artística e comunicação. Quando este número está faltando, você pode ter dificuldade em expressar sua criatividade, comunicar suas ideias ou encontrar alegria na vida.',
                            en: 'Number 3 represents creativity, artistic expression and communication. When this number is missing, you may have difficulty expressing your creativity, communicating your ideas or finding joy in life.'
                          },
                          whatToLearn: {
                            pt: 'Você precisa aprender a expressar sua criatividade e comunicar suas ideias de forma clara e inspiradora. Pratique atividades artísticas, escreva, cante, dance ou encontre outras formas de expressão. Desenvolva seu senso de humor e aprenda a encontrar alegria nas pequenas coisas.',
                            en: 'You need to learn to express your creativity and communicate your ideas clearly and inspiringly. Practice artistic activities, write, sing, dance or find other forms of expression. Develop your sense of humor and learn to find joy in small things.'
                          }
                        },
                        4: {
                          title: { pt: 'Número 4 - Organização e Estabilidade', en: 'Number 4 - Organization and Stability' },
                          description: {
                            pt: 'O número 4 representa organização, estabilidade e trabalho prático. Quando este número está faltando, você pode ter dificuldade em criar estruturas sólidas, manter rotinas ou ser disciplinado.',
                            en: 'Number 4 represents organization, stability and practical work. When this number is missing, you may have difficulty creating solid structures, maintaining routines or being disciplined.'
                          },
                          whatToLearn: {
                            pt: 'Você precisa aprender a criar estruturas sólidas e manter disciplina. Pratique organização, planejamento e estabeleça rotinas que funcionem para você. Desenvolva paciência e persistência para construir coisas duradouras.',
                            en: 'You need to learn to create solid structures and maintain discipline. Practice organization, planning and establish routines that work for you. Develop patience and persistence to build lasting things.'
                          }
                        },
                        5: {
                          title: { pt: 'Número 5 - Liberdade e Versatilidade', en: 'Number 5 - Freedom and Versatility' },
                          description: {
                            pt: 'O número 5 representa liberdade, versatilidade e aventura. Quando este número está faltando, você pode ter dificuldade em se adaptar a mudanças, buscar novas experiências ou expressar sua liberdade pessoal.',
                            en: 'Number 5 represents freedom, versatility and adventure. When this number is missing, you may have difficulty adapting to changes, seeking new experiences or expressing your personal freedom.'
                          },
                          whatToLearn: {
                            pt: 'Você precisa aprender a abraçar mudanças e buscar novas experiências. Pratique sair da zona de conforto, experimentar coisas novas e ser mais flexível. Desenvolva sua capacidade de se adaptar rapidamente e encontrar liberdade dentro de estruturas.',
                            en: 'You need to learn to embrace changes and seek new experiences. Practice stepping out of your comfort zone, trying new things and being more flexible. Develop your ability to adapt quickly and find freedom within structures.'
                          }
                        },
                        6: {
                          title: { pt: 'Número 6 - Responsabilidade e Cuidado', en: 'Number 6 - Responsibility and Care' },
                          description: {
                            pt: 'O número 6 representa responsabilidade, cuidado e serviço aos outros. Quando este número está faltando, você pode ter dificuldade em assumir responsabilidades, cuidar de outros ou criar harmonia em relacionamentos.',
                            en: 'Number 6 represents responsibility, care and service to others. When this number is missing, you may have difficulty taking responsibility, caring for others or creating harmony in relationships.'
                          },
                          whatToLearn: {
                            pt: 'Você precisa aprender a assumir responsabilidades e cuidar de outros de forma equilibrada. Pratique ser mais presente para família e amigos, oferecer ajuda quando necessário e criar harmonia em seus relacionamentos. Desenvolva seu senso de responsabilidade sem se sobrecarregar.',
                            en: 'You need to learn to take responsibility and care for others in a balanced way. Practice being more present for family and friends, offering help when needed and creating harmony in your relationships. Develop your sense of responsibility without overloading yourself.'
                          }
                        },
                        7: {
                          title: { pt: 'Número 7 - Introspecção e Espiritualidade', en: 'Number 7 - Introspection and Spirituality' },
                          description: {
                            pt: 'O número 7 representa introspecção, espiritualidade e busca por conhecimento profundo. Quando este número está faltando, você pode ter dificuldade em se conectar com seu mundo interior, buscar respostas espirituais ou desenvolver sua intuição.',
                            en: 'Number 7 represents introspection, spirituality and the search for deep knowledge. When this number is missing, you may have difficulty connecting with your inner world, seeking spiritual answers or developing your intuition.'
                          },
                          whatToLearn: {
                            pt: 'Você precisa aprender a se conectar com seu mundo interior e buscar conhecimento espiritual. Pratique meditação, introspecção e momentos de silêncio. Desenvolva sua intuição e busque respostas para questões profundas da vida. Reserve tempo para estudar e refletir sobre temas filosóficos e espirituais.',
                            en: 'You need to learn to connect with your inner world and seek spiritual knowledge. Practice meditation, introspection and moments of silence. Develop your intuition and seek answers to deep life questions. Set aside time to study and reflect on philosophical and spiritual themes.'
                          }
                        },
                        8: {
                          title: { pt: 'Número 8 - Poder e Realização Material', en: 'Number 8 - Power and Material Achievement' },
                          description: {
                            pt: 'O número 8 representa poder, realização material e autoridade. Quando este número está faltando, você pode ter dificuldade em manifestar poder pessoal, alcançar sucesso material ou assumir posições de autoridade.',
                            en: 'Number 8 represents power, material achievement and authority. When this number is missing, you may have difficulty manifesting personal power, achieving material success or assuming positions of authority.'
                          },
                          whatToLearn: {
                            pt: 'Você precisa aprender a manifestar seu poder pessoal e alcançar realizações materiais de forma equilibrada. Pratique assumir posições de liderança, desenvolver habilidades de negociação e criar estruturas que gerem resultados. Desenvolva confiança em sua capacidade de criar abundância e usar poder de forma ética.',
                            en: 'You need to learn to manifest your personal power and achieve material achievements in a balanced way. Practice assuming leadership positions, developing negotiation skills and creating structures that generate results. Develop confidence in your ability to create abundance and use power ethically.'
                          }
                        },
                        9: {
                          title: { pt: 'Número 9 - Compaixão e Serviço Universal', en: 'Number 9 - Compassion and Universal Service' },
                          description: {
                            pt: 'O número 9 representa compaixão, serviço universal e sabedoria. Quando este número está faltando, você pode ter dificuldade em desenvolver compaixão, servir causas maiores ou integrar sabedoria de experiências passadas.',
                            en: 'Number 9 represents compassion, universal service and wisdom. When this number is missing, you may have difficulty developing compassion, serving greater causes or integrating wisdom from past experiences.'
                          },
                          whatToLearn: {
                            pt: 'Você precisa aprender a desenvolver compaixão e servir causas maiores. Pratique ajudar outros sem esperar nada em troca, desenvolver empatia e trabalhar por causas que beneficiem a humanidade. Integre sabedoria de suas experiências e aprenda a perdoar e deixar ir o que não serve mais.',
                            en: 'You need to learn to develop compassion and serve greater causes. Practice helping others without expecting anything in return, develop empathy and work for causes that benefit humanity. Integrate wisdom from your experiences and learn to forgive and let go of what no longer serves.'
                          }
                        }
                      };
                      
                      const lesson = karmicLessons[num];
                      if (!lesson) return null;
                      
                      return (
                        <div key={index} style={{
                          padding: '1rem',
                          backgroundColor: 'hsl(var(--muted) / 0.2)',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '0.75rem',
                          borderLeft: '4px solid hsl(var(--destructive))'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                            <span style={{
                              width: '2.5rem',
                              height: '2.5rem',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              backgroundColor: 'hsl(var(--destructive) / 0.1)',
                              border: '2px solid hsl(var(--destructive))',
                              borderRadius: '0.5rem',
                              fontSize: '1.25rem',
                              fontWeight: '700',
                              color: 'hsl(var(--destructive))'
                            }}>
                              {num}
                            </span>
                            <h4 style={{
                              margin: 0,
                              fontSize: '1rem',
                              fontWeight: '600',
                              color: 'hsl(var(--foreground))'
                            }}>
                              {language === 'pt' ? lesson.title.pt : lesson.title.en}
                            </h4>
                          </div>
                          
                          <p style={{
                            margin: '0 0 0.75rem 0',
                            fontSize: '0.875rem',
                            color: 'hsl(var(--muted-foreground))',
                            lineHeight: '1.6'
                          }}>
                            {language === 'pt' ? lesson.description.pt : lesson.description.en}
                          </p>
                          
                          <div style={{
                            padding: '0.75rem',
                            backgroundColor: 'hsl(var(--accent) / 0.1)',
                            border: '1px solid hsl(var(--accent) / 0.3)',
                            borderRadius: '0.5rem'
                          }}>
                            <p style={{
                              margin: '0 0 0.5rem 0',
                              fontSize: '0.75rem',
                              fontWeight: '600',
                              color: 'hsl(var(--accent))',
                              textTransform: 'uppercase',
                              letterSpacing: '0.05em'
                            }}>
                              {language === 'pt' ? 'O QUE VOCÊ PRECISA APRENDER:' : 'WHAT YOU NEED TO LEARN:'}
                            </p>
                            <p style={{
                              margin: 0,
                              fontSize: '0.875rem',
                              color: 'hsl(var(--foreground))',
                              lineHeight: '1.6'
                            }}>
                              {language === 'pt' ? lesson.whatToLearn.pt : lesson.whatToLearn.en}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Mensagem quando não há setas ou números faltantes */}
              {(!numerologyMap.birth_grid.arrows_strength || numerologyMap.birth_grid.arrows_strength.length === 0) &&
               (!numerologyMap.birth_grid.arrows_weakness || numerologyMap.birth_grid.arrows_weakness.length === 0) &&
               (!numerologyMap.birth_grid.missing_numbers || numerologyMap.birth_grid.missing_numbers.length === 0) && (
                <p style={{ color: 'hsl(var(--muted-foreground))', fontStyle: 'italic' }}>
                  {language === 'pt' 
                    ? 'Não há setas de força, fraqueza ou números faltantes identificados na sua grade de nascimento.'
                    : 'No strength arrows, weakness arrows or missing numbers identified in your birth grid.'}
                </p>
              )}
            </AstroCard>
          )}

          {/* Karmic Debts */}
          {numerologyMap.karmic_debts && numerologyMap.karmic_debts.length > 0 && (
            <AstroCard className="numerology-section-card">
              <h2 className="numerology-section-title">
                {language === 'pt' ? 'Dívidas Cármicas' : 'Karmic Debts'}
              </h2>
              <p className="numerology-section-subtitle">
                {language === 'pt' 
                  ? 'Números que indicam lições cármicas a serem trabalhadas nesta vida'
                  : 'Numbers that indicate karmic lessons to be worked on in this life'}
              </p>
              
              {/* Explicação sobre Dívidas Cármicas */}
              <div style={{
                padding: '1.5rem',
                backgroundColor: 'hsl(var(--muted) / 0.2)',
                border: '1px solid hsl(var(--border))',
                borderRadius: '0.75rem',
                marginBottom: '1.5rem'
              }}>
                <h3 style={{
                  fontSize: '1rem',
                  fontWeight: '600',
                  color: 'hsl(var(--foreground))',
                  marginBottom: '0.75rem'
                }}>
                  {language === 'pt' ? 'O que são Dívidas Cármicas?' : 'What are Karmic Debts?'}
                </h3>
                <p style={{
                  fontSize: '0.875rem',
                  color: 'hsl(var(--foreground))',
                  lineHeight: '1.6',
                  margin: 0
                }}>
                  {language === 'pt' 
                    ? 'As dívidas cármicas são números especiais (13, 14, 16 e 19) que aparecem nos cálculos numerológicos quando reduzimos certos números. Eles indicam lições importantes que você precisa aprender nesta vida, relacionadas a padrões de comportamento ou atitudes que precisam ser transformados. Não são "castigos", mas sim oportunidades de crescimento e evolução espiritual.'
                    : 'Karmic debts are special numbers (13, 14, 16, and 19) that appear in numerological calculations when we reduce certain numbers. They indicate important lessons you need to learn in this life, related to behavior patterns or attitudes that need to be transformed. They are not "punishments", but rather opportunities for growth and spiritual evolution.'}
                </p>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginTop: '1rem' }}>
                {numerologyMap.karmic_debts.map((debt, index) => {
                  // Significados dos números de dívida cármica
                  const karmicDebtMeanings: Record<number, { title: { pt: string; en: string }; description: { pt: string; en: string }; lesson: { pt: string; en: string } }> = {
                    13: {
                      title: { pt: 'Dívida Cármica 13 - Trabalho e Transformação', en: 'Karmic Debt 13 - Work and Transformation' },
                      description: {
                        pt: 'A dívida cármica 13 está relacionada ao trabalho duro, disciplina e transformação através do esforço. Em vidas passadas, você pode ter evitado trabalho necessário ou usado trabalho de forma egoísta. Nesta vida, você precisa aprender a trabalhar com dedicação, paciência e propósito, transformando desafios em oportunidades de crescimento.',
                        en: 'Karmic debt 13 is related to hard work, discipline and transformation through effort. In past lives, you may have avoided necessary work or used work selfishly. In this life, you need to learn to work with dedication, patience and purpose, transforming challenges into opportunities for growth.'
                      },
                      lesson: {
                        pt: 'Aprenda a valorizar o trabalho honesto, desenvolver disciplina e usar seus esforços para criar algo de valor. Transforme obstáculos em oportunidades de crescimento pessoal.',
                        en: 'Learn to value honest work, develop discipline and use your efforts to create something of value. Transform obstacles into opportunities for personal growth.'
                      }
                    },
                    14: {
                      title: { pt: 'Dívida Cármica 14 - Liberdade e Responsabilidade', en: 'Karmic Debt 14 - Freedom and Responsibility' },
                      description: {
                        pt: 'A dívida cármica 14 está relacionada ao uso indevido da liberdade e falta de responsabilidade. Em vidas passadas, você pode ter abusado de sua liberdade ou não assumido responsabilidades. Nesta vida, você precisa aprender a equilibrar liberdade com responsabilidade, usando sua independência de forma construtiva.',
                        en: 'Karmic debt 14 is related to misuse of freedom and lack of responsibility. In past lives, you may have abused your freedom or not taken responsibility. In this life, you need to learn to balance freedom with responsibility, using your independence constructively.'
                      },
                      lesson: {
                        pt: 'Aprenda a usar sua liberdade com sabedoria e assumir responsabilidades. Equilibre independência com compromisso e use sua liberdade para criar algo positivo.',
                        en: 'Learn to use your freedom wisely and take responsibility. Balance independence with commitment and use your freedom to create something positive.'
                      }
                    },
                    16: {
                      title: { pt: 'Dívida Cármica 16 - Ego e Humildade', en: 'Karmic Debt 16 - Ego and Humility' },
                      description: {
                        pt: 'A dívida cármica 16 está relacionada ao ego excessivo e falta de humildade. Em vidas passadas, você pode ter sido orgulhoso, arrogante ou usado poder de forma destrutiva. Nesta vida, você precisa aprender humildade, desenvolver compaixão e usar qualquer poder ou autoridade que tenha de forma ética e construtiva.',
                        en: 'Karmic debt 16 is related to excessive ego and lack of humility. In past lives, you may have been proud, arrogant or used power destructively. In this life, you need to learn humility, develop compassion and use any power or authority you have ethically and constructively.'
                      },
                      lesson: {
                        pt: 'Aprenda a ser humilde, desenvolver compaixão e usar poder com sabedoria. Transforme orgulho em autoconfiança saudável e ego em serviço aos outros.',
                        en: 'Learn to be humble, develop compassion and use power wisely. Transform pride into healthy self-confidence and ego into service to others.'
                      }
                    },
                    19: {
                      title: { pt: 'Dívida Cármica 19 - Poder e Abuso', en: 'Karmic Debt 19 - Power and Abuse' },
                      description: {
                        pt: 'A dívida cármica 19 está relacionada ao abuso de poder e autoridade. Em vidas passadas, você pode ter usado poder de forma egoísta, manipuladora ou destrutiva. Nesta vida, você precisa aprender a usar poder de forma responsável, desenvolver liderança ética e servir ao bem maior em vez de interesses pessoais.',
                        en: 'Karmic debt 19 is related to abuse of power and authority. In past lives, you may have used power selfishly, manipulatively or destructively. In this life, you need to learn to use power responsibly, develop ethical leadership and serve the greater good rather than personal interests.'
                      },
                      lesson: {
                        pt: 'Aprenda a usar poder e autoridade de forma ética e responsável. Desenvolva liderança que serve aos outros e transforme ambição pessoal em serviço ao bem comum.',
                        en: 'Learn to use power and authority ethically and responsibly. Develop leadership that serves others and transform personal ambition into service to the common good.'
                      }
                    }
                  };

                  const meaning = karmicDebtMeanings[debt];
                  
                  return (
                    <div key={index} style={{
                      padding: '1.5rem',
                      backgroundColor: 'hsl(var(--destructive) / 0.1)',
                      border: '2px solid hsl(var(--destructive) / 0.3)',
                      borderRadius: '0.75rem',
                      textAlign: 'center',
                      minWidth: '280px',
                      flex: '1 1 280px'
                    }}>
                      <div style={{
                        fontSize: '2.5rem',
                        fontWeight: '700',
                        color: 'hsl(var(--destructive))',
                        marginBottom: '0.5rem'
                      }}>
                        {debt}
                      </div>
                      <p style={{
                        fontSize: '0.75rem',
                        color: 'hsl(var(--muted-foreground))',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        marginBottom: '1rem'
                      }}>
                        {language === 'pt' ? 'Dívida Cármica' : 'Karmic Debt'}
                      </p>
                      
                      {meaning && (
                        <div style={{
                          textAlign: 'left',
                          marginTop: '1rem',
                          paddingTop: '1rem',
                          borderTop: '1px solid hsl(var(--border))'
                        }}>
                          <h4 style={{
                            fontSize: '0.875rem',
                            fontWeight: '600',
                            color: 'hsl(var(--foreground))',
                            marginBottom: '0.5rem'
                          }}>
                            {language === 'pt' ? meaning.title.pt : meaning.title.en}
                          </h4>
                          <p style={{
                            fontSize: '0.8125rem',
                            color: 'hsl(var(--muted-foreground))',
                            lineHeight: '1.5',
                            marginBottom: '0.75rem'
                          }}>
                            {language === 'pt' ? meaning.description.pt : meaning.description.en}
                          </p>
                          <div style={{
                            padding: '0.75rem',
                            backgroundColor: 'hsl(var(--accent) / 0.1)',
                            border: '1px solid hsl(var(--accent) / 0.3)',
                            borderRadius: '0.5rem'
                          }}>
                            <p style={{
                              fontSize: '0.75rem',
                              fontWeight: '600',
                              color: 'hsl(var(--accent))',
                              textTransform: 'uppercase',
                              letterSpacing: '0.05em',
                              marginBottom: '0.5rem'
                            }}>
                              {language === 'pt' ? 'LIÇÃO A APRENDER:' : 'LESSON TO LEARN:'}
                            </p>
                            <p style={{
                              fontSize: '0.8125rem',
                              color: 'hsl(var(--foreground))',
                              lineHeight: '1.5',
                              margin: 0
                            }}>
                              {language === 'pt' ? meaning.lesson.pt : meaning.lesson.en}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </AstroCard>
          )}

          {/* Life Cycle - Triângulo Divino */}
          {numerologyMap.life_cycle && (
            <AstroCard className="numerology-section-card">
              <h2 className="numerology-section-title">
                {language === 'pt' ? 'O Grande Cenário - Triângulo Divino' : 'The Great Scenario - Divine Triangle'}
              </h2>
              <p className="numerology-section-subtitle">
                {language === 'pt' 
                  ? 'Baseado no Triângulo Divino de Javane & Bunker - Onde você está na sua jornada'
                  : 'Based on the Divine Triangle by Javane & Bunker - Where you are in your journey'}
              </p>
              
              {/* Visualização do Triângulo Divino */}
              <div style={{
                padding: '2rem',
                background: 'linear-gradient(135deg, hsl(var(--muted) / 0.3) 0%, hsl(var(--card)) 100%)',
                border: '1px solid hsl(var(--border))',
                borderRadius: '0.75rem',
                marginTop: '1.5rem',
                textAlign: 'center'
              }}>
                {/* Número do Ciclo */}
                <div style={{
                  fontSize: '4rem',
                  fontWeight: '700',
                  color: 'hsl(var(--accent))',
                  marginBottom: '1rem',
                  lineHeight: '1'
                }}>
                  {numerologyMap.life_cycle.cycle_number}
                </div>
                
                {/* Nome do Ciclo */}
                <h3 style={{
                  fontSize: '1.75rem',
                  fontWeight: '600',
                  color: 'hsl(var(--foreground))',
                  marginBottom: '0.75rem',
                  fontFamily: 'var(--font-serif)'
                }}>
                  {numerologyMap.life_cycle.cycle === 'Juventude' ? (language === 'pt' ? 'Juventude' : 'Youth') :
                   numerologyMap.life_cycle.cycle === 'Poder' ? (language === 'pt' ? 'Poder' : 'Power') :
                   (language === 'pt' ? 'Sabedoria' : 'Wisdom')}
                </h3>
                
                {/* Idade */}
                <div style={{
                  display: 'inline-block',
                  padding: '0.5rem 1.5rem',
                  backgroundColor: 'hsl(var(--accent) / 0.1)',
                  border: '1px solid hsl(var(--accent) / 0.3)',
                  borderRadius: '2rem',
                  marginBottom: '1.5rem'
                }}>
                  <p style={{
                    fontSize: '0.875rem',
                    color: 'hsl(var(--accent))',
                    fontWeight: '600',
                    margin: 0
                  }}>
                    {language === 'pt' 
                      ? `${numerologyMap.life_cycle.age} anos`
                      : `${numerologyMap.life_cycle.age} years`}
                  </p>
                </div>
                
                {/* Descrição do Ciclo */}
                <div style={{
                  marginTop: '1.5rem',
                  padding: '1.5rem',
                  backgroundColor: 'hsl(var(--muted) / 0.2)',
                  borderRadius: '0.75rem',
                  textAlign: 'left'
                }}>
                  <h4 style={{
                    fontSize: '1rem',
                    fontWeight: '600',
                    color: 'hsl(var(--foreground))',
                    marginBottom: '0.75rem'
                  }}>
                    {language === 'pt' ? 'Sobre este Ciclo:' : 'About this Cycle:'}
                  </h4>
                  <p style={{
                    fontSize: '0.875rem',
                    color: 'hsl(var(--foreground))',
                    lineHeight: '1.7',
                    margin: 0
                  }}>
                    {numerologyMap.life_cycle.cycle === 'Juventude' ? (
                      language === 'pt' 
                        ? 'O ciclo da Juventude (0-27 anos) é um período de descoberta, aprendizado e formação da identidade. É quando você estabelece as bases para sua vida adulta, explora diferentes caminhos e desenvolve suas habilidades fundamentais.'
                        : 'The Youth cycle (0-27 years) is a period of discovery, learning and identity formation. It is when you establish the foundations for your adult life, explore different paths and develop your fundamental skills.'
                    ) : numerologyMap.life_cycle.cycle === 'Poder' ? (
                      language === 'pt'
                        ? 'O ciclo do Poder (28-54 anos) é um período de ação, realização e construção. É quando você aplica o que aprendeu, constrói sua carreira, relacionamentos e legado. Um tempo de manifestação concreta dos seus talentos.'
                        : 'The Power cycle (28-54 years) is a period of action, achievement and building. It is when you apply what you have learned, build your career, relationships and legacy. A time of concrete manifestation of your talents.'
                    ) : (
                      language === 'pt'
                        ? 'O ciclo da Sabedoria (55+ anos) é um período de integração, ensino e transcendência. É quando você compartilha sua experiência, guia outros e encontra significado mais profundo na vida. Um tempo de sabedoria e legado espiritual.'
                        : 'The Wisdom cycle (55+ years) is a period of integration, teaching and transcendence. It is when you share your experience, guide others and find deeper meaning in life. A time of wisdom and spiritual legacy.'
                    )}
                  </p>
                </div>
                
                {/* Conexão Tarot/Planeta */}
                <div style={{
                  marginTop: '1.5rem',
                  padding: '1rem',
                  borderTop: '1px solid hsl(var(--border))',
                  fontSize: '0.875rem',
                  color: 'hsl(var(--muted-foreground))',
                  fontStyle: 'italic'
                }}>
                  {language === 'pt' 
                    ? 'Este número do ciclo está conectado a um Arcano Maior do Tarot e a um Planeta regente, revelando os temas espirituais e energéticos deste período da sua vida.'
                    : 'This cycle number is connected to a Major Arcana of Tarot and a ruling Planet, revealing the spiritual and energetic themes of this period of your life.'}
                </div>
              </div>
            </AstroCard>
          )}

          {/* Interpretação */}
          {isLoadingInterpretation ? (
            <AstroCard>
              <div style={{ textAlign: 'center', padding: '2rem' }}>
                <UIIcons.Loader size={24} className="animate-spin text-accent" style={{ margin: '0 auto' }} />
                <p style={{ marginTop: '1rem', color: 'hsl(var(--muted-foreground))' }}>
                  {language === 'pt' ? 'Gerando interpretação...' : 'Generating interpretation...'}
                </p>
              </div>
            </AstroCard>
          ) : interpretation ? (
            <AstroCard>
              <h2 className="numerology-interpretation-title">
                {language === 'pt' ? 'Interpretação Numerológica' : 'Numerology Interpretation'}
              </h2>
              <div className="numerology-interpretation-content">
                {formatGroqText(interpretation, language)}
              </div>
            </AstroCard>
          ) : null}
        </div>
      )}
      </div>
    </div>
  );
};


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
                  <p style={{ marginBottom: '0.75rem', fontSize: '0.875rem', color: 'hsl(var(--muted-foreground))' }}>
                    {language === 'pt' 
                      ? 'Estes números não aparecem no seu nome e representam lições que você precisa aprender nesta vida:'
                      : 'These numbers do not appear in your name and represent lessons you need to learn in this life:'}
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {numerologyMap.birth_grid.missing_numbers.map((num, index) => (
                      <span key={index} style={{
                        padding: '0.5rem 1rem',
                        backgroundColor: 'hsl(var(--muted) / 0.3)',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '0.5rem',
                        fontSize: '1rem',
                        fontWeight: '600',
                        color: 'hsl(var(--foreground))'
                      }}>
                        {num}
                      </span>
                    ))}
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
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginTop: '1rem' }}>
                {numerologyMap.karmic_debts.map((debt, index) => (
                  <div key={index} style={{
                    padding: '1.5rem',
                    backgroundColor: 'hsl(var(--destructive) / 0.1)',
                    border: '2px solid hsl(var(--destructive) / 0.3)',
                    borderRadius: '0.75rem',
                    textAlign: 'center',
                    minWidth: '120px'
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
                      letterSpacing: '0.05em'
                    }}>
                      {language === 'pt' ? 'Dívida Cármica' : 'Karmic Debt'}
                    </p>
                  </div>
                ))}
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
                {formatGroqText(interpretation)}
              </div>
            </AstroCard>
          ) : (
            <AstroCard>
              <div style={{ textAlign: 'center', padding: '2rem' }}>
                <p style={{ marginBottom: '1.5rem', color: 'hsl(var(--muted-foreground))' }}>
                  {language === 'pt' 
                    ? 'Gere uma interpretação completa e detalhada do seu mapa numerológico'
                    : 'Generate a complete and detailed interpretation of your numerology map'}
                </p>
                <AstroButton
                  onClick={fetchInterpretation}
                  variant="primary"
                  size="md"
                  disabled={isLoadingInterpretation}
                >
                  {isLoadingInterpretation 
                    ? (language === 'pt' ? 'Gerando...' : 'Generating...')
                    : (language === 'pt' ? 'Gerar Interpretação' : 'Generate Interpretation')
                  }
                </AstroButton>
              </div>
            </AstroCard>
          )}
        </div>
      )}
      </div>
    </div>
  );
};


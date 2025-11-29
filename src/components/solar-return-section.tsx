import React, { useState, useEffect } from 'react';
import { UIIcons } from './ui-icons';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';
import { apiService } from '../services/api';
import { useLanguage } from '../i18n';
import { OnboardingData } from './onboarding';
import { AstroCard } from './astro-card';
import { AstroButton } from './astro-button';
import { formatGroqText } from '../utils/formatGroqText';

interface SolarReturnSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const SolarReturnSection = ({ userData, onBack }: SolarReturnSectionProps) => {
  const { t, language } = useLanguage();
  const [targetYear, setTargetYear] = useState<number>(new Date().getFullYear());
  const [solarReturnData, setSolarReturnData] = useState<any>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string>('');

  // Calcular revolução solar
  const calculateSolarReturn = async () => {
    if (!userData.birthDate || !userData.birthTime || !userData.coordinates) {
      setError(language === 'pt' 
        ? 'Dados de nascimento incompletos' 
        : 'Incomplete birth data');
      return;
    }

    try {
      setIsCalculating(true);
      setError('');
      
      const birthDateISO = userData.birthDate.toISOString();
      
      const result = await apiService.calculateSolarReturn({
        birth_date: birthDateISO,
        birth_time: userData.birthTime,
        latitude: userData.coordinates.latitude,
        longitude: userData.coordinates.longitude,
        target_year: targetYear,
      });

      setSolarReturnData(result);
      
      // Calcular interpretação automaticamente após o cálculo
      await fetchInterpretation(result);
    } catch (err: any) {
      console.error('[Solar Return] Erro ao calcular:', err);
      setError(err.message || (language === 'pt' 
        ? 'Erro ao calcular revolução solar' 
        : 'Error calculating solar return'));
    } finally {
      setIsCalculating(false);
    }
  };

  // Buscar interpretação
  const fetchInterpretation = async (data?: any) => {
    const solarData = data || solarReturnData;
    if (!solarData) {
      return;
    }

    try {
      setIsLoading(true);
      setError('');

      const result = await apiService.getSolarReturnInterpretation({
        natal_sun_sign: userData.sunSign || 'Áries',
        natal_ascendant: userData.ascendant,
        solar_return_ascendant: solarData.ascendant_sign,
        solar_return_sun_house: solarData.sun_house,
        solar_return_moon_sign: solarData.moon_sign,
        solar_return_moon_house: solarData.moon_house,
        solar_return_venus_sign: solarData.venus_sign,
        solar_return_venus_house: solarData.venus_house,
        solar_return_mars_sign: solarData.mars_sign,
        solar_return_mars_house: solarData.mars_house,
        solar_return_jupiter_sign: solarData.jupiter_sign,
        solar_return_jupiter_house: solarData.jupiter_house,
        solar_return_saturn_sign: solarData.saturn_sign,
        solar_return_midheaven: solarData.midheaven_sign,
        target_year: targetYear,
        language: language,
      });

      if (result && result.interpretation) {
        setInterpretation(result.interpretation);
      }
    } catch (err: any) {
      console.error('[Solar Return] Erro ao buscar interpretação:', err);
      setError(err.message || (language === 'pt' 
        ? 'Erro ao gerar interpretação' 
        : 'Error generating interpretation'));
    } finally {
      setIsLoading(false);
    }
  };

  // Calcular automaticamente ao montar o componente
  useEffect(() => {
    calculateSolarReturn();
  }, [targetYear]);

  const SunIcon = planets.find(p => p.name === 'Sol')?.icon || UIIcons.Sun;
  const MoonIcon = planets.find(p => p.name === 'Lua')?.icon || UIIcons.Moon;
  const VenusIcon = planets.find(p => p.name === 'Vênus')?.icon || UIIcons.Heart;
  const MarsIcon = planets.find(p => p.name === 'Marte')?.icon || UIIcons.Zap;
  const JupiterIcon = planets.find(p => p.name === 'Júpiter')?.icon || UIIcons.Star;
  const SaturnIcon = planets.find(p => p.name === 'Saturno')?.icon || UIIcons.Star;

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
            <SunIcon size={32} className="text-accent" />
          </div>
          <div>
            <h1 className="dashboard-section-title">
              {language === 'pt' ? 'Revolução Solar' : 'Solar Return'}
            </h1>
            <p className="dashboard-section-subtitle">
              {language === 'pt' 
                ? 'Mapa anual do retorno do Sol à posição natal' 
                : 'Annual chart of the Sun\'s return to natal position'}
            </p>
          </div>
        </div>
      </div>

      {/* Conteúdo */}
      <div className="dashboard-section-content">
        {/* Card Informativo sobre Revolução Solar */}
        <AstroCard className="solar-return-info-card">
          <div className="solar-return-info-content">
            <div className="solar-return-info-icon">
              <UIIcons.Info size={24} className="text-accent" />
            </div>
            <div className="solar-return-info-text">
              <h3 className="solar-return-info-title">
                {language === 'pt' 
                  ? 'O que é a Revolução Solar?' 
                  : 'What is a Solar Return?'}
              </h3>
              <p className="solar-return-info-description">
                {language === 'pt' 
                  ? 'A Revolução Solar é um mapa astral calculado para o momento exato em que o Sol retorna à posição que ocupava no seu nascimento. Este mapa anual revela os temas, oportunidades e desafios que estarão presentes durante o próximo ano da sua vida.'
                  : 'A Solar Return is an astrological chart calculated for the exact moment when the Sun returns to the position it occupied at your birth. This annual chart reveals the themes, opportunities, and challenges that will be present during the next year of your life.'}
              </p>
              <div className="solar-return-info-benefits">
                <h4 className="solar-return-info-subtitle">
                  {language === 'pt' ? 'Benefícios:' : 'Benefits:'}
                </h4>
                <ul className="solar-return-info-list">
                  <li>
                    {language === 'pt' 
                      ? 'Entenda os temas principais que guiarão seu ano'
                      : 'Understand the main themes that will guide your year'}
                  </li>
                  <li>
                    {language === 'pt' 
                      ? 'Identifique oportunidades de crescimento e realização'
                      : 'Identify opportunities for growth and fulfillment'}
                  </li>
                  <li>
                    {language === 'pt' 
                      ? 'Prepare-se conscientemente para os desafios que virão'
                      : 'Consciously prepare for upcoming challenges'}
                  </li>
                  <li>
                    {language === 'pt' 
                      ? 'Tome decisões alinhadas com as energias do período'
                      : 'Make decisions aligned with the energies of the period'}
                  </li>
                </ul>
              </div>
              <div className="solar-return-info-tips">
                <h4 className="solar-return-info-subtitle">
                  {language === 'pt' ? 'Dicas:' : 'Tips:'}
                </h4>
                <ul className="solar-return-info-list">
                  <li>
                    {language === 'pt' 
                      ? 'Analise especialmente o Ascendente e a Casa onde o Sol está posicionado'
                      : 'Especially analyze the Ascendant and the House where the Sun is positioned'}
                  </li>
                  <li>
                    {language === 'pt' 
                      ? 'Preste atenção aos planetas nas casas angulares (1, 4, 7, 10)'
                      : 'Pay attention to planets in angular houses (1, 4, 7, 10)'}
                  </li>
                  <li>
                    {language === 'pt' 
                      ? 'Use esta informação como um guia, não como destino imutável'
                      : 'Use this information as a guide, not as an immutable destiny'}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </AstroCard>

        {/* Seletor de Ano */}
        <AstroCard>
          <div className="solar-return-year-selector">
            <label className="solar-return-year-label">
              {language === 'pt' ? 'Ano da Revolução Solar:' : 'Solar Return Year:'}
            </label>
            <div className="solar-return-year-controls">
              <button
                onClick={() => setTargetYear(targetYear - 1)}
                className="solar-return-year-button"
                disabled={isCalculating}
              >
                <UIIcons.ChevronLeft size={20} />
              </button>
              <input
                type="number"
                value={targetYear}
                onChange={(e) => setTargetYear(parseInt(e.target.value) || new Date().getFullYear())}
                className="solar-return-year-input"
                min={1900}
                max={2100}
                disabled={isCalculating}
              />
              <button
                onClick={() => setTargetYear(targetYear + 1)}
                className="solar-return-year-button"
                disabled={isCalculating}
              >
                <UIIcons.ChevronRight size={20} />
              </button>
            </div>
            <AstroButton
              onClick={calculateSolarReturn}
              disabled={isCalculating}
              variant="primary"
              size="md"
            >
              {isCalculating 
                ? (language === 'pt' ? 'Calculando...' : 'Calculating...')
                : (language === 'pt' ? 'Calcular Revolução Solar' : 'Calculate Solar Return')
              }
            </AstroButton>
          </div>
        </AstroCard>

        {/* Erro */}
        {error && (
          <AstroCard>
            <div className="solar-return-error">
              <UIIcons.AlertCircle size={20} className="text-destructive" />
              <p>{error}</p>
            </div>
          </AstroCard>
        )}

        {/* Dados da Revolução Solar */}
        {solarReturnData && (
          <>
            <AstroCard>
              <h2 className="solar-return-data-title">
                {language === 'pt' ? 'Dados da Revolução Solar' : 'Solar Return Data'}
              </h2>
              <div className="solar-return-data-grid">
                <div className="solar-return-data-item">
                  <div className="solar-return-data-icon">
                    <UIIcons.Star size={24} className="text-accent" />
                  </div>
                  <div className="solar-return-data-content">
                    <p className="solar-return-data-label">
                      {language === 'pt' ? 'Ascendente' : 'Ascendant'}
                    </p>
                    <p className="solar-return-data-value">
                      {solarReturnData.ascendant_sign}
                    </p>
                  </div>
                </div>

                <div className="solar-return-data-item">
                  <div className="solar-return-data-icon">
                    <SunIcon size={24} className="text-accent" />
                  </div>
                  <div className="solar-return-data-content">
                    <p className="solar-return-data-label">
                      {language === 'pt' ? 'Sol' : 'Sun'}
                    </p>
                    <p className="solar-return-data-value">
                      {solarReturnData.sun_sign} {language === 'pt' ? 'na Casa' : 'in House'} {solarReturnData.sun_house}
                    </p>
                  </div>
                </div>

                <div className="solar-return-data-item">
                  <div className="solar-return-data-icon">
                    <MoonIcon size={24} className="text-accent" />
                  </div>
                  <div className="solar-return-data-content">
                    <p className="solar-return-data-label">
                      {language === 'pt' ? 'Lua' : 'Moon'}
                    </p>
                    <p className="solar-return-data-value">
                      {solarReturnData.moon_sign} {language === 'pt' ? 'na Casa' : 'in House'} {solarReturnData.moon_house}
                    </p>
                  </div>
                </div>

                {solarReturnData.venus_sign && (
                  <div className="solar-return-data-item">
                    <div className="solar-return-data-icon">
                      <VenusIcon size={24} className="text-accent" />
                    </div>
                    <div className="solar-return-data-content">
                      <p className="solar-return-data-label">
                        {language === 'pt' ? 'Vênus' : 'Venus'}
                      </p>
                      <p className="solar-return-data-value">
                        {solarReturnData.venus_sign} {solarReturnData.venus_house && `${language === 'pt' ? 'na Casa' : 'in House'} ${solarReturnData.venus_house}`}
                      </p>
                    </div>
                  </div>
                )}

                {solarReturnData.mars_sign && (
                  <div className="solar-return-data-item">
                    <div className="solar-return-data-icon">
                      <MarsIcon size={24} className="text-accent" />
                    </div>
                    <div className="solar-return-data-content">
                      <p className="solar-return-data-label">
                        {language === 'pt' ? 'Marte' : 'Mars'}
                      </p>
                      <p className="solar-return-data-value">
                        {solarReturnData.mars_sign} {solarReturnData.mars_house && `${language === 'pt' ? 'na Casa' : 'in House'} ${solarReturnData.mars_house}`}
                      </p>
                    </div>
                  </div>
                )}

                {solarReturnData.jupiter_sign && (
                  <div className="solar-return-data-item">
                    <div className="solar-return-data-icon">
                      <JupiterIcon size={24} className="text-accent" />
                    </div>
                    <div className="solar-return-data-content">
                      <p className="solar-return-data-label">
                        {language === 'pt' ? 'Júpiter' : 'Jupiter'}
                      </p>
                      <p className="solar-return-data-value">
                        {solarReturnData.jupiter_sign} {solarReturnData.jupiter_house && `${language === 'pt' ? 'na Casa' : 'in House'} ${solarReturnData.jupiter_house}`}
                      </p>
                    </div>
                  </div>
                )}

                {solarReturnData.midheaven_sign && (
                  <div className="solar-return-data-item">
                    <div className="solar-return-data-icon">
                      <UIIcons.Star size={24} className="text-accent" />
                    </div>
                    <div className="solar-return-data-content">
                      <p className="solar-return-data-label">
                        {language === 'pt' ? 'Meio do Céu' : 'Midheaven'}
                      </p>
                      <p className="solar-return-data-value">
                        {solarReturnData.midheaven_sign}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </AstroCard>

            {/* Interpretação */}
            {isLoading ? (
              <AstroCard>
                <div className="solar-return-loading">
                  <UIIcons.Loader size={24} className="animate-spin text-accent" />
                  <p>{language === 'pt' ? 'Gerando interpretação...' : 'Generating interpretation...'}</p>
                </div>
              </AstroCard>
            ) : interpretation ? (
              <AstroCard>
                <h2 className="solar-return-interpretation-title">
                  {language === 'pt' ? 'Interpretação da Revolução Solar' : 'Solar Return Interpretation'}
                </h2>
                <div className="solar-return-interpretation-content">
                  {formatGroqText(interpretation)}
                </div>
              </AstroCard>
            ) : (
              <AstroCard>
                <AstroButton
                  onClick={() => fetchInterpretation()}
                  variant="primary"
                  size="md"
                >
                  {language === 'pt' ? 'Gerar Interpretação' : 'Generate Interpretation'}
                </AstroButton>
              </AstroCard>
            )}
          </>
        )}
      </div>
    </div>
  );
};


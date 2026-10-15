import React, { useState, useEffect } from 'react';
import { UIIcons } from '../ui-icons';
import { zodiacSigns } from '../zodiac-icons';
import { planets } from '../planet-icons';
import { BirthChartWheel } from '../birth-chart-wheel';
import { ElementChart } from '../element-chart';
import { apiService } from '../../services/api';
import { useLanguage } from '../../i18n';
import { OnboardingData } from '../onboarding';
import { RULER_BY_SIGN, RULER_DETAILS, getRulerSignAndHouse } from './overview/chart-ruler-data';
import { ChartRulerCard } from './overview/chart-ruler-card';
import { ElementsCard } from './overview/elements-card';
import { computeElementDistribution } from './overview/element-distribution';

// ===== VISÃO GERAL =====
interface OverviewSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const OverviewSection = ({ userData, onBack }: OverviewSectionProps) => {
  const { t, language } = useLanguage();
  const [chartRulerInterpretation, setChartRulerInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  // Determinar signo e regente baseado nos dados do usuário
  const ascendantSign = userData.ascendant || 'Áries';
  const sunSign = userData.sunSign || 'Áries';
  const moonSign = userData.moonSign || 'Touro';

  const chartRuler = RULER_BY_SIGN[ascendantSign] || 'Sol';

  const rulerData = getRulerSignAndHouse(userData, chartRuler, sunSign);
  const rulerSign = rulerData.sign;
  const rulerHouse = rulerData.house;

  const currentRulerDetails = RULER_DETAILS[chartRuler] || RULER_DETAILS['Sol'];

  const { elementData, dominantElement, missingElement } = computeElementDistribution(userData, language);

  useEffect(() => {
    const fetchInterpretation = async () => {
      try {
        setIsLoading(true);
        const result = await apiService.getChartRulerInterpretation({
          ascendant: ascendantSign,
          ruler: chartRuler,
          rulerSign: rulerSign,
          rulerHouse: rulerHouse,
        });
        setChartRulerInterpretation(result.interpretation);
      } catch (error) {
        console.error('Erro ao buscar interpretação:', error);
        setChartRulerInterpretation(
          language === 'pt' 
            ? `Com Ascendente em ${ascendantSign}, seu planeta regente é ${chartRuler}. Este planeta guia sua jornada de vida e influencia como você se expressa no mundo.`
            : `With Ascendant in ${ascendantSign}, your ruling planet is ${chartRuler}. This planet guides your life journey and influences how you express yourself in the world.`
        );
      } finally {
        setIsLoading(false);
      }
    };
    fetchInterpretation();
  }, [ascendantSign, chartRuler, rulerSign, rulerHouse, language]);

  const AscIcon = zodiacSigns.find(z => z.name === ascendantSign)?.icon || zodiacSigns[0].icon;
  const SunIcon = zodiacSigns.find(z => z.name === sunSign)?.icon || zodiacSigns[0].icon;
  const MoonIcon = zodiacSigns.find(z => z.name === moonSign)?.icon || zodiacSigns[0].icon;

  return (
    <div className="dashboard-section-container overview-container">
      {/* Header */}
      <div className="overview-header">
        <div className="overview-header-content">
          <h2 className="overview-title">
            {language === 'pt' ? 'Visão Geral do Seu Mapa' : 'Your Chart Overview'}
          </h2>
          <p className="overview-subtitle">
            {language === 'pt' ? 'Explore os principais elementos do seu mapa astral' : 'Explore the main elements of your birth chart'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="overview-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Big Three Cards */}
      <div className="overview-big-three">
        <div className="overview-big-three-grid">
          <div className="overview-big-three-card overview-big-three-card-sun">
            <div className="overview-big-three-card-header">
              <div className="overview-big-three-card-icon-container overview-big-three-card-icon-container-sun">
                <SunIcon size={28} className="text-foreground" />
              </div>
              <div>
                <p className="overview-big-three-card-label">{language === 'pt' ? 'Sol' : 'Sun'}</p>
                <p className="overview-big-three-card-sign">{sunSign}</p>
              </div>
            </div>
            <p className="overview-big-three-card-description">
              {language === 'pt' ? 'Sua essência e identidade central' : 'Your essence and core identity'}
            </p>
          </div>

          <div className="overview-big-three-card overview-big-three-card-moon">
            <div className="overview-big-three-card-header">
              <div className="overview-big-three-card-icon-container overview-big-three-card-icon-container-moon">
                <MoonIcon size={28} className="text-foreground" />
              </div>
              <div>
                <p className="overview-big-three-card-label">{language === 'pt' ? 'Lua' : 'Moon'}</p>
                <p className="overview-big-three-card-sign">{moonSign}</p>
              </div>
            </div>
            <p className="overview-big-three-card-description">
              {language === 'pt' ? 'Suas emoções e mundo interior' : 'Your emotions and inner world'}
            </p>
          </div>

          <div className="overview-big-three-card overview-big-three-card-asc">
            <div className="overview-big-three-card-header">
              <div className="overview-big-three-card-icon-container overview-big-three-card-icon-container-asc">
                <AscIcon size={28} className="text-foreground" />
              </div>
              <div>
                <p className="overview-big-three-card-label">{language === 'pt' ? 'Ascendente' : 'Ascendant'}</p>
                <p className="overview-big-three-card-sign">{ascendantSign}</p>
              </div>
            </div>
            <p className="overview-big-three-card-description">
              {language === 'pt' ? 'Como você se apresenta ao mundo' : 'How you present yourself to the world'}
            </p>
          </div>
        </div>
      </div>

      {/* Birth Chart Wheel */}
      <div className="overview-chart-wheel-section">
        <h3 className="overview-chart-wheel-title">
          {language === 'pt' ? 'Roda do Mapa Astral' : 'Birth Chart Wheel'}
        </h3>
        <div className="overview-chart-wheel-container">
          <BirthChartWheel userData={userData} size={500} />
        </div>
        
        {/* Legenda */}
        <div className="overview-chart-wheel-legend">
          <div className="overview-chart-wheel-legend-section">
            <h4 className="overview-chart-wheel-legend-title">
              {language === 'pt' ? 'Como ler o mapa' : 'How to read the chart'}
            </h4>
            <div className="overview-chart-wheel-legend-items">
              <div className="overview-chart-wheel-legend-item">
                <div className="overview-chart-wheel-legend-icon-container">
                  <div className="overview-chart-wheel-legend-icon-signs">
                    <span style={{ color: 'hsl(var(--primary))', fontSize: '1.5rem' }}>♈</span>
                  </div>
                </div>
                <div className="overview-chart-wheel-legend-content">
                  <p className="overview-chart-wheel-legend-label">
                    {language === 'pt' ? 'Signos do Zodíaco' : 'Zodiac Signs'}
                  </p>
                  <p className="overview-chart-wheel-legend-desc">
                    {language === 'pt' 
                      ? 'Os 12 signos na borda externa representam as constelações'
                      : 'The 12 signs on the outer edge represent the constellations'}
                  </p>
                </div>
              </div>
              
              <div className="overview-chart-wheel-legend-item">
                <div className="overview-chart-wheel-legend-icon-container">
                  <div className="overview-chart-wheel-legend-icon-planets">
                    <span style={{ color: 'hsl(var(--primary))', fontSize: '1.25rem' }}>☉</span>
                  </div>
                </div>
                <div className="overview-chart-wheel-legend-content">
                  <p className="overview-chart-wheel-legend-label">
                    {language === 'pt' ? 'Planetas' : 'Planets'}
                  </p>
                  <p className="overview-chart-wheel-legend-desc">
                    {language === 'pt' 
                      ? 'Símbolos planetários mostram onde cada planeta estava no seu nascimento'
                      : 'Planetary symbols show where each planet was at your birth'}
                  </p>
                </div>
              </div>
              
              <div className="overview-chart-wheel-legend-item">
                <div className="overview-chart-wheel-legend-icon-container">
                  <div className="overview-chart-wheel-legend-icon-houses">
                    <span style={{ color: 'hsl(var(--accent))', fontSize: '1.25rem', fontWeight: '600' }}>1</span>
                  </div>
                </div>
                <div className="overview-chart-wheel-legend-content">
                  <p className="overview-chart-wheel-legend-label">
                    {language === 'pt' ? 'Casas Astrológicas' : 'Astrological Houses'}
                  </p>
                  <p className="overview-chart-wheel-legend-desc">
                    {language === 'pt' 
                      ? 'As 12 casas dividem o mapa em áreas da vida (1-12)'
                      : 'The 12 houses divide the chart into life areas (1-12)'}
                  </p>
                </div>
              </div>
              
              <div className="overview-chart-wheel-legend-item">
                <div className="overview-chart-wheel-legend-icon-container">
                  <div className="overview-chart-wheel-legend-icon-lines">
                    <div className="overview-chart-wheel-legend-line"></div>
                  </div>
                </div>
                <div className="overview-chart-wheel-legend-content">
                  <p className="overview-chart-wheel-legend-label">
                    {language === 'pt' ? 'Linhas Divisórias' : 'Division Lines'}
                  </p>
                  <p className="overview-chart-wheel-legend-desc">
                    {language === 'pt' 
                      ? 'Separam as 12 casas astrológicas do mapa'
                      : 'Separate the 12 astrological houses of the chart'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Ruler & Elements Grid */}
      <div className="overview-details-grid">
        <ChartRulerCard
          language={language}
          ascendantSign={ascendantSign}
          chartRuler={chartRuler}
          isLoading={isLoading}
          chartRulerInterpretation={chartRulerInterpretation}
          currentRulerDetails={currentRulerDetails}
        />

        <ElementsCard
          language={language}
          t={t}
          elementData={elementData}
          dominantElement={dominantElement}
          missingElement={missingElement}
        />
      </div>
    </div>
  );
};

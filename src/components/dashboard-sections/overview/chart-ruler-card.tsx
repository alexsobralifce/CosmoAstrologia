import React from 'react';
import { UIIcons } from '../../ui-icons';
import { planets } from '../../planet-icons';
import { ChartRulerText } from './chart-ruler-text';
import { RULER_DETAILS } from './chart-ruler-data';

interface ChartRulerCardProps {
  language: string;
  ascendantSign: string;
  chartRuler: string;
  isLoading: boolean;
  chartRulerInterpretation: string;
  currentRulerDetails: (typeof RULER_DETAILS)[string];
}

/** Cartão "Regente do Mapa": interpretação da LLM, significado, características e pessoas famosas. */
export const ChartRulerCard = ({
  language,
  ascendantSign,
  chartRuler,
  isLoading,
  chartRulerInterpretation,
  currentRulerDetails,
}: ChartRulerCardProps) => {
  return (
    <div className="overview-detail-card">
      <h3 className="overview-detail-card-title">
        <UIIcons.Star size={20} className="text-primary" />
        {language === 'pt' ? 'Regente do Mapa' : 'Chart Ruler'}
      </h3>
      
      {/* Informações sobre a importância do regente */}
      <div className="overview-chart-ruler-importance">
        <div className="overview-chart-ruler-importance-header">
          <UIIcons.Info size={18} className="text-primary" />
          <h4 className="overview-chart-ruler-importance-title">
            {language === 'pt' ? 'Por que o regente do mapa é importante?' : 'Why is the chart ruler important?'}
          </h4>
        </div>
        <p className="overview-chart-ruler-importance-intro">
          {language === 'pt' 
            ? 'O regente do mapa astral é fundamental para o autoconhecimento, pois ele é o planeta que rege o seu signo ascendente, influenciando diretamente sua personalidade e energia vital. Ele funciona como um guia, revelando suas forças naturais, os tipos de energia que te impulsionam e para onde sua atenção tende a se voltar.'
            : 'The chart ruler is fundamental for self-knowledge, as it is the planet that rules your ascendant sign, directly influencing your personality and vital energy. It functions as a guide, revealing your natural strengths, the types of energy that drive you, and where your attention tends to turn.'}
        </p>
        <div className="overview-chart-ruler-importance-points">
          <div className="overview-chart-ruler-importance-point">
            <div className="overview-chart-ruler-importance-point-icon">
              <UIIcons.Compass size={16} />
            </div>
            <div className="overview-chart-ruler-importance-point-content">
              <p className="overview-chart-ruler-importance-point-title">
                {language === 'pt' ? 'Guia para a personalidade' : 'Guide for personality'}
              </p>
              <p className="overview-chart-ruler-importance-point-text">
                {language === 'pt' 
                  ? 'O planeta regente influencia o seu "jeito de ser", determinando características e comportamentos específicos.'
                  : 'The ruling planet influences your "way of being", determining specific characteristics and behaviors.'}
              </p>
            </div>
          </div>
          
          <div className="overview-chart-ruler-importance-point">
            <div className="overview-chart-ruler-importance-point-icon">
              <UIIcons.Sparkles size={16} />
            </div>
            <div className="overview-chart-ruler-importance-point-content">
              <p className="overview-chart-ruler-importance-point-title">
                {language === 'pt' ? 'Revela forças naturais' : 'Reveals natural strengths'}
              </p>
              <p className="overview-chart-ruler-importance-point-text">
                {language === 'pt' 
                  ? 'Indica onde reside sua força, seu impulso natural e para quais áreas da vida sua atenção retorna com frequência.'
                  : 'Indicates where your strength lies, your natural drive and which areas of life your attention frequently returns to.'}
              </p>
            </div>
          </div>
          
          <div className="overview-chart-ruler-importance-point">
            <div className="overview-chart-ruler-importance-point-icon">
              <UIIcons.Heart size={16} />
            </div>
            <div className="overview-chart-ruler-importance-point-content">
              <p className="overview-chart-ruler-importance-point-title">
                {language === 'pt' ? 'Influencia emoções e instintos' : 'Influences emotions and instincts'}
              </p>
              <p className="overview-chart-ruler-importance-point-text">
                {language === 'pt' 
                  ? 'Por exemplo, a Lua, planeta regente de algumas pessoas, está associada às emoções, instintos e reações emocionais, além da vida doméstica e passado.'
                  : 'For example, the Moon, ruling planet of some people, is associated with emotions, instincts and emotional reactions, as well as domestic life and the past.'}
              </p>
            </div>
          </div>
          
          <div className="overview-chart-ruler-importance-point">
            <div className="overview-chart-ruler-importance-point-icon">
              <UIIcons.Scale size={16} />
            </div>
            <div className="overview-chart-ruler-importance-point-content">
              <p className="overview-chart-ruler-importance-point-title">
                {language === 'pt' ? 'Ajuda no equilíbrio' : 'Helps with balance'}
              </p>
              <p className="overview-chart-ruler-importance-point-text">
                {language === 'pt' 
                  ? 'Ao conhecer as energias do seu regente, você pode usá-las de forma consciente para harmonizar e equilibrar sua personalidade.'
                  : 'By knowing the energies of your ruler, you can use them consciously to harmonize and balance your personality.'}
              </p>
            </div>
          </div>
          
          <div className="overview-chart-ruler-importance-point">
            <div className="overview-chart-ruler-importance-point-icon">
              <UIIcons.BookOpen size={16} />
            </div>
            <div className="overview-chart-ruler-importance-point-content">
              <p className="overview-chart-ruler-importance-point-title">
                {language === 'pt' ? 'Aprofunda a interpretação' : 'Deepens interpretation'}
              </p>
              <p className="overview-chart-ruler-importance-point-text">
                {language === 'pt' 
                  ? 'O regente do seu ascendente é o "regente" do seu mapa como um todo. Analisar a casa e a posição em que ele se encontra no seu mapa é essencial para uma análise mais completa.'
                  : 'The ruler of your ascendant is the "ruler" of your chart as a whole. Analyzing the house and position where it is located in your chart is essential for a more complete analysis.'}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="overview-chart-ruler-header">
        <div className="overview-chart-ruler-icon-container">
          {planets.find(p => p.name === chartRuler)?.icon && (
            (() => {
              const PlanetIcon = planets.find(p => p.name === chartRuler)?.icon;
              return PlanetIcon ? <PlanetIcon size={32} className="text-primary" /> : null;
            })()
          )}
        </div>
        <div className="overview-chart-ruler-info">
          <p className="overview-chart-ruler-name">{chartRuler}</p>
          <p className="overview-chart-ruler-desc">
            {language === 'pt' ? `Regente de ${ascendantSign}` : `Ruler of ${ascendantSign}`}
          </p>
        </div>
      </div>
      {isLoading ? (
        <div className="overview-chart-ruler-loading">
          <div className="overview-chart-ruler-spinner"></div>
          <p className="overview-chart-ruler-loading-text">
            {language === 'pt' ? 'Gerando interpretação...' : 'Generating interpretation...'}
          </p>
        </div>
      ) : (
        <div className="overview-chart-ruler-content">
          <ChartRulerText text={chartRulerInterpretation} />
          
          {/* Informações Adicionais sobre o Regente */}
          <div className="overview-chart-ruler-additional-info">
            <div className="overview-chart-ruler-info-section">
              <h4 className="overview-chart-ruler-info-title">
                {language === 'pt' ? 'O que significa ter ' : 'What it means to have '}
                <span className="overview-chart-ruler-info-highlight">{chartRuler}</span>
                {language === 'pt' ? ' como regente' : ' as ruler'}
              </h4>
              <p className="overview-chart-ruler-info-text">
                {currentRulerDetails.meaning[language === 'pt' ? 'pt' : 'en']}
              </p>
            </div>

            <div className="overview-chart-ruler-info-section">
              <h4 className="overview-chart-ruler-info-title">
                {language === 'pt' ? 'Características principais' : 'Main characteristics'}
              </h4>
              <ul className="overview-chart-ruler-characteristics">
                {currentRulerDetails.characteristics[language === 'pt' ? 'pt' : 'en'].map((char, idx) => (
                  <li key={idx} className="overview-chart-ruler-characteristic-item">
                    <span className="overview-chart-ruler-characteristic-marker">•</span>
                    {char}
                  </li>
                ))}
              </ul>
            </div>

            <div className="overview-chart-ruler-info-section">
              <h4 className="overview-chart-ruler-info-title">
                {language === 'pt' ? 'Pessoas famosas com esta regência' : 'Famous people with this rulership'}
              </h4>
              <div className="overview-chart-ruler-famous-people">
                {currentRulerDetails.famousPeople[language === 'pt' ? 'pt' : 'en'].map((person, idx) => (
                  <span key={idx} className="overview-chart-ruler-famous-person">
                    {person}
                  </span>
                ))}
              </div>
            </div>

            <div className="overview-chart-ruler-info-section">
              <h4 className="overview-chart-ruler-info-title">
                {language === 'pt' ? 'Influência na sua vida' : 'Influence on your life'}
              </h4>
              <p className="overview-chart-ruler-info-text">
                {currentRulerDetails.influence[language === 'pt' ? 'pt' : 'en']}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

import React, { useState } from 'react';
import { UIIcons } from './ui-icons';
import { BirthChartWheel } from './birth-chart-wheel';
import { apiService } from '../services/api';
import { useLanguage } from '../i18n';
import { OnboardingData } from './onboarding';
import { formatGroqText } from '../utils/formatGroqText';
import { removeDuplicatePlanetTitle } from '../utils/formatGroqText';

interface CompleteBirthChartProps {
  userData: OnboardingData;
  onBack: () => void;
}

interface PlanetInSign {
  planet: string;
  planet_key: string;
  sign: string;
  degree: number;
  degree_dms: string;
  is_retrograde: boolean;
  house: number;
}

interface SpecialPoint {
  point: string;
  point_key: string;
  sign: string;
  degree: number;
  degree_dms: string;
  house: number;
}

interface CompleteChartData {
  birth_data: {
    date: string;
    time: string;
    latitude: number;
    longitude: number;
  };
  planets_in_signs: PlanetInSign[];
  special_points: SpecialPoint[];
  planets_in_houses: Array<{
    house: number;
    planets: Array<PlanetInSign | SpecialPoint>;
  }>;
}

const HOUSE_NAMES_PT: Record<number, string> = {
  1: 'Primeira Casa',
  2: 'Segunda Casa',
  3: 'Terceira Casa',
  4: 'Quarta Casa',
  5: 'Quinta Casa',
  6: 'Sexta Casa',
  7: 'Sétima Casa',
  8: 'Oitava Casa',
  9: 'Nona Casa',
  10: 'Décima Casa',
  11: 'Décima Primeira Casa',
  12: 'Décima Segunda Casa',
};

const HOUSE_NAMES_EN: Record<number, string> = {
  1: 'First House',
  2: 'Second House',
  3: 'Third House',
  4: 'Fourth House',
  5: 'Fifth House',
  6: 'Sixth House',
  7: 'Seventh House',
  8: 'Eighth House',
  9: 'Ninth House',
  10: 'Tenth House',
  11: 'Eleventh House',
  12: 'Twelfth House',
};

// Definição das abas/tópicos
const TAB_SECTIONS = [
  {
    id: 'personal',
    titlePt: 'Planetas Pessoais',
    titleEn: 'Personal Planets',
    icon: UIIcons.Star,
    descriptionPt: 'Sol, Lua, Mercúrio, Vênus, Marte',
    descriptionEn: 'Sun, Moon, Mercury, Venus, Mars',
    planets: ['Sol', 'Lua', 'Mercúrio', 'Vênus', 'Marte'],
  },
  {
    id: 'social',
    titlePt: 'Planetas Sociais',
    titleEn: 'Social Planets',
    icon: UIIcons.Users,
    descriptionPt: 'Júpiter e Saturno',
    descriptionEn: 'Jupiter and Saturn',
    planets: ['Júpiter', 'Saturno'],
  },
  {
    id: 'transpersonal',
    titlePt: 'Planetas Transpessoais',
    titleEn: 'Transpersonal Planets',
    icon: UIIcons.Compass,
    descriptionPt: 'Urano, Netuno, Plutão',
    descriptionEn: 'Uranus, Neptune, Pluto',
    planets: ['Urano', 'Netuno', 'Plutão'],
  },
  {
    id: 'points',
    titlePt: 'Pontos Especiais',
    titleEn: 'Special Points',
    icon: UIIcons.Crosshair,
    descriptionPt: 'Ascendente, Meio do Céu, Nódulos',
    descriptionEn: 'Ascendant, Midheaven, Nodes',
    planets: ['Ascendente', 'Meio do Céu', 'Nódulo Norte', 'Nódulo Sul', 'Quíron'],
  },
  {
    id: 'houses',
    titlePt: 'Análise das Casas',
    titleEn: 'House Analysis',
    icon: UIIcons.Home,
    descriptionPt: 'Significado de cada casa no seu mapa',
    descriptionEn: 'Meaning of each house in your chart',
    planets: [],
  },
];

export const CompleteBirthChartSection = ({ userData, onBack }: CompleteBirthChartProps) => {
  const { language } = useLanguage();
  const [chartData, setChartData] = useState<CompleteChartData | null>(null);
  const [isLoadingChart, setIsLoadingChart] = useState(false);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  
  // Estados para cada seção
  const [interpretations, setInterpretations] = useState<Record<string, string>>({});
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({});
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({});

  const formatDate = (date: Date | string): string => {
    if (typeof date === 'string') {
      const d = new Date(date);
      if (!isNaN(d.getTime())) {
        return d.toLocaleDateString('pt-BR');
      }
      return date;
    }
    return date.toLocaleDateString('pt-BR');
  };

  // Carregar dados básicos do mapa (sem interpretações)
  const loadChartData = async () => {
    setIsLoadingChart(true);
    try {
      const birthDateStr = formatDate(userData.birthDate || new Date());
      const coordinates = userData.coordinates || { latitude: 0, longitude: 0 };
      
      const data = await apiService.getCompleteChart({
        birthDate: birthDateStr,
        birthTime: userData.birthTime || '12:00',
        latitude: coordinates.latitude,
        longitude: coordinates.longitude,
        birthPlace: userData.birthPlace || '',
        name: userData.name || 'Usuário',
      });
      
      setChartData(data);
    } catch (err: any) {
      console.error('Erro ao carregar mapa:', err);
    } finally {
      setIsLoadingChart(false);
    }
  };

  // Carregar interpretação de um item específico (sob demanda)
  const loadInterpretation = async (itemKey: string, planet: string, sign: string, house?: number) => {
    if (loadingStates[itemKey] || interpretations[itemKey]) {
      return;
    }

    setLoadingStates(prev => ({ ...prev, [itemKey]: true }));

    try {
      const sunSign = chartData?.planets_in_signs.find(p => p.planet === 'Sol')?.sign || userData.sunSign || 'Áries';
      const moonSign = chartData?.planets_in_signs.find(p => p.planet === 'Lua')?.sign || userData.moonSign || 'Touro';
      const ascendant = chartData?.special_points.find(p => p.point === 'Ascendente')?.sign || userData.ascendant || 'Gêmeos';

      const response = await apiService.getPlanetInterpretation({
        planet,
        sign,
        house,
        sunSign,
        moonSign,
        ascendant,
        userName: userData.name || 'Usuário',
      });

      setInterpretations(prev => ({
        ...prev,
        [itemKey]: response.interpretation,
      }));
    } catch (err) {
      console.error(`Erro ao carregar interpretação de ${planet}:`, err);
      setInterpretations(prev => ({
        ...prev,
        [itemKey]: language === 'pt' 
          ? 'Erro ao carregar interpretação. Tente novamente.'
          : 'Error loading interpretation. Please try again.',
      }));
    } finally {
      setLoadingStates(prev => ({ ...prev, [itemKey]: false }));
    }
  };

  // Toggle de item expandido (carrega interpretação se necessário)
  const toggleItem = (itemKey: string, planet: string, sign: string, house?: number) => {
    const isCurrentlyExpanded = expandedItems[itemKey];
    
    setExpandedItems(prev => ({
      ...prev,
      [itemKey]: !isCurrentlyExpanded,
    }));

    if (!isCurrentlyExpanded && !interpretations[itemKey]) {
      loadInterpretation(itemKey, planet, sign, house);
    }
  };

  // Obter itens de uma aba específica
  const getTabItems = (tabId: string) => {
    if (!chartData) return [];

    if (tabId === 'houses') {
      return chartData.planets_in_houses.map(houseData => ({
        key: `house-${houseData.house}`,
        name: language === 'pt' 
          ? HOUSE_NAMES_PT[houseData.house] || `Casa ${houseData.house}`
          : HOUSE_NAMES_EN[houseData.house] || `House ${houseData.house}`,
        type: 'house' as const,
        house: houseData.house,
        planets: houseData.planets,
      }));
    }

    const tab = TAB_SECTIONS.find(t => t.id === tabId);
    if (!tab) return [];

    const items: Array<{
      key: string;
      name: string;
      sign: string;
      house?: number;
      degree_dms?: string;
      is_retrograde?: boolean;
      type: 'planet' | 'point';
    }> = [];

    tab.planets.forEach(planetName => {
      const planet = chartData.planets_in_signs.find(p => p.planet === planetName);
      if (planet) {
        items.push({
          key: planet.planet_key,
          name: planet.planet,
          sign: planet.sign,
          house: planet.house,
          degree_dms: planet.degree_dms,
          is_retrograde: planet.is_retrograde,
          type: 'planet',
        });
      }

      const point = chartData.special_points.find(p => p.point === planetName);
      if (point) {
        items.push({
          key: point.point_key,
          name: point.point,
          sign: point.sign,
          house: point.house,
          degree_dms: point.degree_dms,
          type: 'point',
        });
      }
    });

    return items;
  };

  // Renderizar item individual
  const renderItem = (item: {
    key: string;
    name: string;
    sign: string;
    house?: number;
    degree_dms?: string;
    is_retrograde?: boolean;
    type?: 'planet' | 'point' | 'house';
    planets?: Array<PlanetInSign | SpecialPoint>;
  }) => {
    const isExpanded = expandedItems[item.key];
    const isLoading = loadingStates[item.key];
    const interpretation = interpretations[item.key];
    const houseNames = language === 'pt' ? HOUSE_NAMES_PT : HOUSE_NAMES_EN;

    if (item.type === 'house') {
      return (
        <div key={item.key} className="complete-chart-item-card">
          <button
            onClick={() => setExpandedItems(prev => ({ ...prev, [item.key]: !isExpanded }))}
            className="complete-chart-item-header"
          >
            <h4 className="complete-chart-item-name">{item.name}</h4>
            <UIIcons.ChevronDown
              size={20}
              className={`complete-chart-chevron ${isExpanded ? 'expanded' : ''}`}
            />
          </button>
          {isExpanded && (
            <div className="complete-chart-item-content">
              {item.planets?.length === 0 ? (
                <p className="complete-chart-empty-message">
                  {language === 'pt' ? 'Nenhum planeta nesta casa.' : 'No planets in this house.'}
                </p>
              ) : (
                item.planets?.map(planet => {
                  const planetKey = 'planet_key' in planet ? planet.planet_key : `point_${planet.point || planet.planet}`;
                  const planetName = 'planet' in planet ? planet.planet : planet.point || '';
                  
                  return (
                    <div key={planetKey} className="complete-chart-sub-item">
                      <button
                        onClick={() => toggleItem(planetKey, planetName, planet.sign, item.house)}
                        className="complete-chart-sub-item-header"
                      >
                        <span>
                          {planetName} em {planet.sign} {planet.degree_dms}
                          {'is_retrograde' in planet && planet.is_retrograde && (
                            <span className="complete-chart-retrograde"> Rx</span>
                          )}
                        </span>
                        {loadingStates[planetKey] ? (
                          <UIIcons.Loader size={16} className="animate-spin" />
                        ) : (
                          <UIIcons.ChevronDown
                            size={16}
                            className={`complete-chart-chevron ${expandedItems[planetKey] ? 'expanded' : ''}`}
                          />
                        )}
                      </button>
                      {expandedItems[planetKey] && interpretations[planetKey] && (
                        <div className="complete-chart-interpretation">
                          {formatGroqText(interpretations[planetKey], language, planetName, planet.sign)}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          )}
        </div>
      );
    }

    return (
      <div key={item.key} className="complete-chart-item-card">
        <button
          onClick={() => toggleItem(item.key, item.name, item.sign, item.house)}
          className="complete-chart-item-header"
        >
          <div>
            <h4 className="complete-chart-item-name">
              {item.name} em {item.sign} {item.degree_dms}
              {item.is_retrograde && <span className="complete-chart-retrograde"> Rx</span>}
              {item.house && (
                <span className="complete-chart-house-badge">
                  {' '}• {houseNames[item.house] || (language === 'pt' ? `Casa ${item.house}` : `House ${item.house}`)}
                </span>
              )}
            </h4>
          </div>
          {isLoading ? (
            <UIIcons.Loader size={20} className="animate-spin" />
          ) : (
            <UIIcons.ChevronDown
              size={20}
              className={`complete-chart-chevron ${isExpanded ? 'expanded' : ''}`}
            />
          )}
        </button>
        
        {isExpanded && interpretation && (
          <div className="complete-chart-item-content">
            <div className="complete-chart-interpretation">
              {formatGroqText(interpretation, language, item.name, item.sign)}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (!chartData && !isLoadingChart) {
    return (
      <div className="birth-chart-container">
        <button onClick={onBack} className="birth-chart-back-button">
          <UIIcons.ArrowLeft size={20} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
        
        <div className="birth-chart-section-loading">
          <h2 className="birth-chart-title">
            {language === 'pt' ? 'Mapa Astral Completo' : 'Complete Birth Chart'}
          </h2>
          <p>
            {language === 'pt' 
              ? 'Clique no botão abaixo para carregar os dados básicos do seu mapa astral.'
              : 'Click the button below to load your birth chart basic data.'}
          </p>
          <button
            onClick={loadChartData}
            className="birth-chart-generate-button"
          >
            {language === 'pt' ? 'Carregar Mapa Astral' : 'Load Birth Chart'}
          </button>
        </div>
      </div>
    );
  }

  if (isLoadingChart) {
    return (
      <div className="birth-chart-container">
        <div className="birth-chart-section-loading">
          <UIIcons.Loader size={32} className="animate-spin" />
          <p>
            {language === 'pt' 
              ? 'Carregando dados do mapa astral...'
              : 'Loading birth chart data...'}
          </p>
        </div>
      </div>
    );
  }

  if (!chartData) return null;

  return (
    <div className="birth-chart-container">
      <div className="birth-chart-header">
        <div className="birth-chart-header-content">
          <h2 className="birth-chart-title">
            {language === 'pt' ? 'Meu Mapa Astral Completo' : 'My Complete Birth Chart'}
          </h2>
          <p className="birth-chart-subtitle">
            {language === 'pt' 
              ? 'Explore seu mapa em seções organizadas. Clique nas abas para ver cada tópico.'
              : 'Explore your chart in organized sections. Click on tabs to see each topic.'}
          </p>
        </div>
        <button onClick={onBack} className="birth-chart-back-button">
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Rodinha do Mapa */}
      <div className="birth-chart-summary">
        <div className="birth-chart-wheel-container">
          <BirthChartWheel userData={userData} size={280} />
        </div>
      </div>

      {/* Abas de Navegação */}
      <div className="complete-chart-tabs">
        {TAB_SECTIONS.map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          const items = getTabItems(tab.id);

          return (
            <div key={tab.id} className="complete-chart-tab-container">
              <button
                onClick={() => setActiveTab(isActive ? null : tab.id)}
                className={`complete-chart-tab ${isActive ? 'active' : ''}`}
              >
                <div className="complete-chart-tab-icon">
                  <Icon size={24} />
                </div>
                <div className="complete-chart-tab-text">
                  <h3>{language === 'pt' ? tab.titlePt : tab.titleEn}</h3>
                  <p>{language === 'pt' ? tab.descriptionPt : tab.descriptionEn}</p>
                </div>
                <UIIcons.ChevronDown
                  size={20}
                  className={`complete-chart-chevron ${isActive ? 'expanded' : ''}`}
                />
              </button>

              {isActive && (
                <div className="complete-chart-tab-content">
                  {items.length === 0 ? (
                    <p className="complete-chart-empty-message">
                      {language === 'pt' 
                        ? 'Nenhum item encontrado nesta seção.'
                        : 'No items found in this section.'}
                    </p>
                  ) : (
                    items.map(item => renderItem(item))
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};


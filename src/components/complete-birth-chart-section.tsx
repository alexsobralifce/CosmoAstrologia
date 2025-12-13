import React, { useState } from 'react';
import { UIIcons } from './ui-icons';
import { zodiacSigns } from './zodiac-icons';
import { BirthChartWheel } from './birth-chart-wheel';
import { apiService } from '../services/api';
import { useLanguage } from '../i18n';
import { OnboardingData } from './onboarding';
import { formatGroqText } from '../utils/formatGroqText';
import { generateBirthChartPDF } from '../utils/generateBirthChartPDF';

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

// Ordem de prioridade para exibição dos planetas/pontos
const PLANET_PRIORITY: Record<string, number> = {
  'Sol': 1,
  'Lua': 2,
  'Mercúrio': 3,
  'Vênus': 4,
  'Marte': 5,
  'Júpiter': 6,
  'Saturno': 7,
  'Urano': 8,
  'Netuno': 9,
  'Plutão': 10,
  'Ascendente': 11,
  'Meio do Céu': 12,
  'Nódulo Norte': 13,
  'Nódulo Sul': 14,
  'Quíron': 15,
};

export const CompleteBirthChartSection = ({ userData, onBack }: CompleteBirthChartProps) => {
  const { language } = useLanguage();
  const [chartData, setChartData] = useState<CompleteChartData | null>(null);
  const [isLoadingChart, setIsLoadingChart] = useState(false);
  
  // Estados para cada item (carregamento sob demanda)
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

  // Obter todos os itens do mapa ordenados por prioridade (lista vertical simples)
  const getAllItems = () => {
    if (!chartData) return [];

    const items: Array<{
      key: string;
      name: string;
      sign: string;
      house?: number;
      degree_dms?: string;
      is_retrograde?: boolean;
      type: 'planet' | 'point';
      priority: number;
    }> = [];

    // Adicionar planetas nos signos
    chartData.planets_in_signs.forEach(planet => {
      items.push({
        key: planet.planet_key,
        name: planet.planet,
        sign: planet.sign,
        house: planet.house,
        degree_dms: planet.degree_dms,
        is_retrograde: planet.is_retrograde,
        type: 'planet',
        priority: PLANET_PRIORITY[planet.planet] || 999,
      });
    });

    // Adicionar pontos especiais
    chartData.special_points.forEach(point => {
      items.push({
        key: point.point_key,
        name: point.point,
        sign: point.sign,
        house: point.house,
        degree_dms: point.degree_dms,
        type: 'point',
        priority: PLANET_PRIORITY[point.point] || 999,
      });
    });

    // Ordenar por prioridade
    items.sort((a, b) => a.priority - b.priority);

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

    // Usar o estilo de card expansível igual ao full-birth-chart-section
    return (
      <div key={item.key} className={`birth-chart-section-card ${isExpanded ? 'expanded' : ''}`}>
        <button
          onClick={() => toggleItem(item.key, item.name, item.sign, item.house)}
          className="birth-chart-section-button"
        >
          <div className="birth-chart-section-header">
            <div className="birth-chart-section-icon-container bg-gradient-to-br from-primary/20 to-primary/10">
              <UIIcons.Star size={24} className="text-primary" />
            </div>
            <div className="birth-chart-section-title-container">
              <h3 className="birth-chart-section-title">
                {item.name} em {item.sign} {item.degree_dms}
                {item.is_retrograde && <span className="complete-chart-retrograde"> Rx</span>}
                {item.house && (
                  <span className="complete-chart-house-badge">
                    {' '}• {houseNames[item.house] || (language === 'pt' ? `Casa ${item.house}` : `House ${item.house}`)}
                  </span>
                )}
              </h3>
              {!isExpanded && interpretation && (
                <p className="birth-chart-section-preview">
                  {interpretation.substring(0, 100)}...
                </p>
              )}
            </div>
          </div>
          <div className="birth-chart-section-actions">
            {isLoading && (
              <div className="birth-chart-section-spinner"></div>
            )}
            <UIIcons.ChevronDown 
              size={24} 
              className={`birth-chart-section-chevron ${isExpanded ? 'expanded' : ''}`}
            />
          </div>
        </button>
        
        {isExpanded && (
          <div className="birth-chart-section-content">
            {isLoading ? (
              <div className="birth-chart-section-loading">
                <div className="birth-chart-section-loading-line"></div>
                <div className="birth-chart-section-loading-line w-5-6"></div>
                <div className="birth-chart-section-loading-line w-4-6"></div>
                <div className="birth-chart-section-loading-line"></div>
                <div className="birth-chart-section-loading-line w-3-4"></div>
              </div>
            ) : interpretation ? (
              <div className="birth-chart-section-text">
                {formatGroqText(interpretation, language, item.name, item.sign)}
              </div>
            ) : null}
          </div>
        )}
      </div>
    );
  };

  // Dados do usuário para exibição - usar dados do usuário ou do mapa carregado
  const sunSign = chartData?.planets_in_signs.find(p => p.planet === 'Sol')?.sign || userData.sunSign || 'Áries';
  const moonSign = chartData?.planets_in_signs.find(p => p.planet === 'Lua')?.sign || userData.moonSign || 'Touro';
  const ascendant = chartData?.special_points.find(p => p.point === 'Ascendente')?.sign || userData.ascendant || 'Gêmeos';
  
  // Ícones dos signos
  const SunIcon = zodiacSigns.find(z => z.name === sunSign)?.icon || zodiacSigns[0].icon;
  const MoonIcon = zodiacSigns.find(z => z.name === moonSign)?.icon || zodiacSigns[0].icon;
  const AscIcon = zodiacSigns.find(z => z.name === ascendant)?.icon || zodiacSigns[0].icon;

  if (!chartData && !isLoadingChart) {
  return (
    <div className="dashboard-section-container birth-chart-container">
      {/* Header - Mantém o mesmo formato do componente original */}
      <div className="birth-chart-header">
        <div className="birth-chart-header-content">
          <h2 className="birth-chart-title">
            {language === 'pt' ? 'Meu Mapa Astral Completo' : 'My Complete Birth Chart'}
          </h2>
          <p className="birth-chart-subtitle">
            {language === 'pt' 
              ? 'Uma análise profunda e personalizada da sua carta natal'
              : 'A deep and personalized analysis of your birth chart'}
          </p>
        </div>
        <div className="birth-chart-header-actions">
          <button
              onClick={loadChartData}
              disabled={isLoadingChart}
            className="birth-chart-generate-button"
          >
            <div className="birth-chart-generate-button-shine"></div>
              {isLoadingChart ? (
              <>
                <div className="birth-chart-generate-button-spinner"></div>
                <span className="birth-chart-generate-button-text">
                    {language === 'pt' ? 'Calculando mapa completo...' : 'Calculating complete chart...'}
                </span>
              </>
            ) : (
              <>
                <div className="birth-chart-generate-button-icon">
                  <UIIcons.Sparkles size={14} style={{ color: '#160F24' }} />
                </div>
                <span className="birth-chart-generate-button-text">
                  {language === 'pt' ? 'Gerar Análise Completa' : 'Generate Complete Analysis'}
                </span>
                <UIIcons.ChevronRight size={18} className="birth-chart-generate-button-chevron" style={{ color: '#160F24' }} />
              </>
            )}
          </button>
            <button
              onClick={onBack}
              className="birth-chart-back-button"
            >
              <UIIcons.ArrowLeft size={18} />
              {language === 'pt' ? 'Voltar' : 'Back'}
            </button>
          </div>
        </div>

        {/* Resumo do Mapa - Mostra sempre com dados do usuário */}
        <div className="birth-chart-summary">
          <div className="birth-chart-summary-content">
            {/* Wheel Preview */}
            <div className="birth-chart-wheel-container">
              <div className="birth-chart-wheel-wrapper">
                <BirthChartWheel userData={userData} size={280} />
              </div>
            </div>
            
            {/* Info Cards */}
            <div className="birth-chart-info">
              <div className="birth-chart-user-info">
                <UIIcons.User size={16} />
                <span className="birth-chart-user-name">{userData.name}</span>
                <span>•</span>
                <span>
                  {typeof userData.birthDate === 'string' 
                    ? userData.birthDate 
                    : userData.birthDate instanceof Date 
                      ? userData.birthDate.toLocaleDateString() 
                      : 'Data não informada'} {language === 'pt' ? 'às' : 'at'} {userData.birthTime || '12:00'}
                </span>
                <span>•</span>
                <span>{userData.birthPlace || 'Local não informado'}</span>
              </div>
              
              {/* Cards Sol, Lua e Ascendente */}
              <div className="birth-chart-planets-cards">
                {/* Sol */}
                <div className="birth-chart-planet-card birth-chart-planet-card-sun">
                  <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-sun">
                    <SunIcon size={28} className="text-foreground" />
                  </div>
                  <div>
                    <p className="birth-chart-planet-label">
                      {language === 'pt' ? 'Sol' : 'Sun'}
                    </p>
                    <p className="birth-chart-planet-sign">{sunSign}</p>
                  </div>
                  <p className="birth-chart-planet-desc">
                    {language === 'pt' ? 'Sua essência e identidade' : 'Your essence and identity'}
                  </p>
                </div>
                
                {/* Lua */}
                <div className="birth-chart-planet-card birth-chart-planet-card-moon">
                  <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-moon">
                    <MoonIcon size={28} className="text-foreground" />
                  </div>
                  <div>
                    <p className="birth-chart-planet-label">
                      {language === 'pt' ? 'Lua' : 'Moon'}
                    </p>
                    <p className="birth-chart-planet-sign">{moonSign}</p>
                  </div>
                  <p className="birth-chart-planet-desc">
                    {language === 'pt' ? 'Suas emoções e necessidades' : 'Your emotions and needs'}
                  </p>
                </div>
                
                {/* Ascendente */}
                <div className="birth-chart-planet-card birth-chart-planet-card-asc">
                  <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-asc">
                    <AscIcon size={28} className="text-foreground" />
                  </div>
                  <div>
                    <p className="birth-chart-planet-label">
                      {language === 'pt' ? 'Asc' : 'Asc'}
                    </p>
                    <p className="birth-chart-planet-sign">{ascendant}</p>
                  </div>
                  <p className="birth-chart-planet-desc">
                    {language === 'pt' ? 'Sua máscara social' : 'Your social mask'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isLoadingChart) {
    return (
      <div className="dashboard-section-container birth-chart-container">
        <div className="birth-chart-header">
          <div className="birth-chart-header-content">
            <h2 className="birth-chart-title">
              {language === 'pt' ? 'Meu Mapa Astral Completo' : 'My Complete Birth Chart'}
            </h2>
            <p className="birth-chart-subtitle">
              {language === 'pt' 
                ? 'Uma análise profunda e personalizada da sua carta natal'
                : 'A deep and personalized analysis of your birth chart'}
            </p>
          </div>
          <div className="birth-chart-header-actions">
            <button
              disabled={true}
              className="birth-chart-generate-button"
            >
              <div className="birth-chart-generate-button-spinner"></div>
              <span className="birth-chart-generate-button-text">
                {language === 'pt' ? 'Calculando mapa completo...' : 'Calculating complete chart...'}
              </span>
            </button>
            <button
              onClick={onBack}
              className="birth-chart-back-button"
            >
              <UIIcons.ArrowLeft size={18} />
              {language === 'pt' ? 'Voltar' : 'Back'}
            </button>
          </div>
        </div>

        {/* Resumo do Mapa - Mostra sempre com dados do usuário */}
        <div className="birth-chart-summary">
          <div className="birth-chart-summary-content">
            {/* Wheel Preview */}
            <div className="birth-chart-wheel-container">
              <div className="birth-chart-wheel-wrapper">
                <BirthChartWheel userData={userData} size={280} />
              </div>
            </div>
            
            {/* Info Cards */}
            <div className="birth-chart-info">
              <div className="birth-chart-user-info">
                <UIIcons.User size={16} />
                <span className="birth-chart-user-name">{userData.name}</span>
                <span>•</span>
                <span>
                  {typeof userData.birthDate === 'string' 
                    ? userData.birthDate 
                    : userData.birthDate instanceof Date 
                      ? userData.birthDate.toLocaleDateString() 
                      : 'Data não informada'} {language === 'pt' ? 'às' : 'at'} {userData.birthTime || '12:00'}
                </span>
                <span>•</span>
                <span>{userData.birthPlace || 'Local não informado'}</span>
              </div>
              
              {/* Cards Sol, Lua e Ascendente */}
              <div className="birth-chart-planets-cards">
                {/* Sol */}
                <div className="birth-chart-planet-card birth-chart-planet-card-sun">
                  <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-sun">
                    <SunIcon size={28} className="text-foreground" />
                  </div>
                  <div>
                    <p className="birth-chart-planet-label">
                      {language === 'pt' ? 'Sol' : 'Sun'}
                    </p>
                    <p className="birth-chart-planet-sign">{sunSign}</p>
                  </div>
                  <p className="birth-chart-planet-desc">
                    {language === 'pt' ? 'Sua essência e identidade' : 'Your essence and identity'}
                  </p>
                </div>
                
                {/* Lua */}
                <div className="birth-chart-planet-card birth-chart-planet-card-moon">
                  <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-moon">
                    <MoonIcon size={28} className="text-foreground" />
                  </div>
                  <div>
                    <p className="birth-chart-planet-label">
                      {language === 'pt' ? 'Lua' : 'Moon'}
                    </p>
                    <p className="birth-chart-planet-sign">{moonSign}</p>
                  </div>
                  <p className="birth-chart-planet-desc">
                    {language === 'pt' ? 'Suas emoções e necessidades' : 'Your emotions and needs'}
                  </p>
                </div>
                
                {/* Ascendente */}
                <div className="birth-chart-planet-card birth-chart-planet-card-asc">
                  <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-asc">
                    <AscIcon size={28} className="text-foreground" />
                  </div>
                  <div>
                    <p className="birth-chart-planet-label">
                      {language === 'pt' ? 'Asc' : 'Asc'}
                    </p>
                    <p className="birth-chart-planet-sign">{ascendant}</p>
                  </div>
                  <p className="birth-chart-planet-desc">
                    {language === 'pt' ? 'Sua máscara social' : 'Your social mask'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading State */}
        <div className="birth-chart-sections">
          <div className="birth-chart-section-loading">
            <div style={{ 
              textAlign: 'center', 
              padding: '2rem',
              color: 'hsl(var(--muted-foreground))'
            }}>
              <p style={{ marginBottom: '1rem', fontSize: '1rem' }}>
                {language === 'pt' 
                  ? 'Calculando mapa astral completo com todas as casas...' 
                  : 'Calculating complete birth chart with all houses...'}
              </p>
              <p style={{ fontSize: '0.875rem', opacity: 0.8 }}>
                {language === 'pt' 
                  ? 'Este processo pode levar até 2 minutos. Por favor, aguarde...' 
                  : 'This process may take up to 2 minutes. Please wait...'}
              </p>
            </div>
            <div className="birth-chart-section-loading-line"></div>
            <div className="birth-chart-section-loading-line w-5-6"></div>
            <div className="birth-chart-section-loading-line w-4-6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!chartData) return null;

  return (
    <div className="dashboard-section-container birth-chart-container">
      {/* Header - Mantém o mesmo formato do componente original */}
      <div className="birth-chart-header">
        <div className="birth-chart-header-content">
          <h2 className="birth-chart-title">
            {language === 'pt' ? 'Meu Mapa Astral Completo' : 'My Complete Birth Chart'}
          </h2>
          <p className="birth-chart-subtitle">
            {language === 'pt' 
              ? 'Uma análise profunda e personalizada da sua carta natal'
              : 'A deep and personalized analysis of your birth chart'}
          </p>
        </div>
        <div className="birth-chart-header-actions">
          <button
            onClick={onBack}
            className="birth-chart-back-button"
          >
            <UIIcons.ArrowLeft size={18} />
            {language === 'pt' ? 'Voltar' : 'Back'}
          </button>
        </div>
      </div>

      {/* Resumo do Mapa - Mantém o mesmo formato */}
      <div className="birth-chart-summary">
        <div className="birth-chart-summary-content">
          {/* Wheel Preview */}
          <div className="birth-chart-wheel-container">
            <div className="birth-chart-wheel-wrapper">
              <BirthChartWheel userData={userData} size={280} />
            </div>
          </div>
          
          {/* Info Cards */}
          <div className="birth-chart-info">
            <div className="birth-chart-user-info">
              <UIIcons.User size={16} />
              <span className="birth-chart-user-name">{userData.name}</span>
              <span>•</span>
              <span>
                {typeof userData.birthDate === 'string' 
                  ? userData.birthDate 
                  : userData.birthDate instanceof Date 
                    ? userData.birthDate.toLocaleDateString() 
                    : 'Data não informada'} {language === 'pt' ? 'às' : 'at'} {userData.birthTime || '12:00'}
              </span>
              <span>•</span>
              <span>{userData.birthPlace || 'Local não informado'}</span>
            </div>
            
            {/* Cards Sol, Lua e Ascendente */}
            <div className="birth-chart-planets-cards">
              {/* Sol */}
              <div className="birth-chart-planet-card birth-chart-planet-card-sun">
                <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-sun">
                  <SunIcon size={28} className="text-foreground" />
                </div>
                <div>
                  <p className="birth-chart-planet-label">
                    {language === 'pt' ? 'Sol' : 'Sun'}
                  </p>
                  <p className="birth-chart-planet-sign">{sunSign}</p>
                </div>
                <p className="birth-chart-planet-desc">
                  {language === 'pt' ? 'Sua essência e identidade' : 'Your essence and identity'}
                </p>
              </div>
              
              {/* Lua */}
              <div className="birth-chart-planet-card birth-chart-planet-card-moon">
                <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-moon">
                  <MoonIcon size={28} className="text-foreground" />
                </div>
                <div>
                  <p className="birth-chart-planet-label">
                    {language === 'pt' ? 'Lua' : 'Moon'}
                  </p>
                  <p className="birth-chart-planet-sign">{moonSign}</p>
                </div>
                <p className="birth-chart-planet-desc">
                  {language === 'pt' ? 'Suas emoções e necessidades' : 'Your emotions and needs'}
                </p>
              </div>
              
              {/* Ascendente */}
              <div className="birth-chart-planet-card birth-chart-planet-card-asc">
                <div className="birth-chart-planet-icon-container birth-chart-planet-icon-container-asc">
                  <AscIcon size={28} className="text-foreground" />
                </div>
                <div>
                  <p className="birth-chart-planet-label">
                    {language === 'pt' ? 'Asc' : 'Asc'}
                  </p>
                  <p className="birth-chart-planet-sign">{ascendant}</p>
                </div>
                <p className="birth-chart-planet-desc">
                  {language === 'pt' ? 'Sua máscara social' : 'Your social mask'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Lista de Planetas e Pontos - Cards Expansíveis Individuais */}
        <div className="birth-chart-sections">
        <div className="birth-chart-sections-title">
          <UIIcons.BookOpen size={24} />
          {language === 'pt' ? 'Análise Completa' : 'Complete Analysis'}
        </div>
        <p className="birth-chart-sections-description">
          {language === 'pt' 
            ? 'Clique em cada seção para expandir e ler a análise detalhada. Cada seção é carregada individualmente quando você expande.'
            : 'Click on each section to expand and read the detailed analysis. Each section is loaded individually when you expand it.'}
        </p>
        
        <div className="birth-chart-sections-list">
          {getAllItems().map(item => renderItem(item))}
          </div>
        </div>

      {/* Botão de PDF ao final */}
      <div className="birth-chart-pdf-section">
        <button
          onClick={async () => {
            if (!chartData) {
              alert(language === 'pt' 
                ? 'Por favor, aguarde o carregamento do mapa astral antes de gerar o PDF.'
                : 'Please wait for the birth chart to load before generating the PDF.');
              return;
            }

            // Criar seções de interpretação a partir das interpretações carregadas
            const sections: Record<string, { section: string; title: string; content: string; generated_by: string } | null> = {
              power: null,
              triad: null,
              personal: null,
              houses: null,
              karma: null,
              synthesis: null,
            };

            // Organizar interpretações por categoria (se necessário)
            // Por enquanto, vamos criar uma seção com todas as interpretações
            const allInterpretations: string[] = [];
            
            getAllItems().forEach(item => {
              const interpretation = interpretations[item.key];
              if (interpretation) {
                const itemTitle = `${item.name} em ${item.sign}${item.degree_dms ? ` ${item.degree_dms}` : ''}${item.house ? ` • Casa ${item.house}` : ''}`;
                allInterpretations.push(`\n\n## ${itemTitle}\n\n${interpretation}`);
              }
            });

            if (allInterpretations.length > 0) {
              sections.personal = {
                section: 'personal',
                title: language === 'pt' ? 'Interpretações dos Planetas e Pontos' : 'Planets and Points Interpretations',
                content: allInterpretations.join('\n'),
                generated_by: 'groq'
              };
            }

            // Gerar PDF com todos os dados
            generateBirthChartPDF({
              userData,
              sections,
              language,
              chartData: chartData
            });
          }}
          className="birth-chart-pdf-button"
          disabled={!chartData}
        >
          <UIIcons.FileText size={20} className="birth-chart-pdf-icon" />
          <span className="birth-chart-pdf-text">
            {language === 'pt' ? 'Gerar PDF do Mapa Astral Completo' : 'Generate Complete Birth Chart PDF'}
          </span>
          <UIIcons.Download size={18} className="birth-chart-pdf-download-icon" />
        </button>
        <p className="birth-chart-pdf-description">
          {language === 'pt' 
            ? 'Baixe seu mapa astral completo em PDF com todos os planetas, pontos especiais, casas e interpretações organizadas.'
            : 'Download your complete birth chart in PDF format with all planets, special points, houses and organized interpretations.'}
        </p>
        </div>
    </div>
  );
};


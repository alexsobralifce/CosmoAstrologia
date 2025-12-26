import React, { useState } from 'react';
import { UIIcons } from './ui-icons';
import { zodiacSigns } from './zodiac-icons';
import { BirthChartWheel } from './birth-chart-wheel';
import { apiService } from '../services/api';
import { useLanguage } from '../i18n';
import { OnboardingData } from './onboarding';
import { formatGroqText } from '../utils/formatGroqText';

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

interface HouseData {
  house: number;
  planets: Array<PlanetInSign | SpecialPoint>;
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
  planets_in_houses: HouseData[];
}

// Nomes das casas em português
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

export const CompleteBirthChartSection = ({ userData, onBack }: CompleteBirthChartProps) => {
  const { language } = useLanguage();
  const [chartData, setChartData] = useState<CompleteChartData | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [planetInterpretations, setPlanetInterpretations] = useState<Record<string, string>>({});
  const [loadingInterpretations, setLoadingInterpretations] = useState<Record<string, boolean>>({});

  // Formatar data para DD/MM/YYYY
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

  // Carregar dados do mapa completo (chamado quando clicar no botão)
  const loadCompleteChart = async () => {
    setIsGenerating(true);
    setError(null);
    
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
      
      // Carregar todas as interpretações automaticamente (sem bloquear o estado de geração)
      // As interpretações serão carregadas em background
      loadAllInterpretations(data).catch(err => {
        console.error('Erro ao carregar interpretações:', err);
      });
    } catch (err: any) {
      console.error('Erro ao carregar mapa completo:', err);
      setError(err.message || 'Erro ao carregar mapa astral completo');
    } finally {
      setIsGenerating(false);
    }
  };

  // Carregar todas as interpretações automaticamente
  const loadAllInterpretations = async (data: CompleteChartData) => {
    const allItems: Array<{
      key: string;
      name: string;
      sign: string;
      house?: number;
    }> = [];

    // Adicionar planetas nos signos
    data.planets_in_signs.forEach((planet) => {
      allItems.push({
        key: planet.planet_key,
        name: planet.planet,
        sign: planet.sign,
        house: planet.house,
      });
    });

    // Adicionar pontos especiais
    data.special_points.forEach((point) => {
      allItems.push({
        key: point.point_key,
        name: point.point,
        sign: point.sign,
        house: point.house,
      });
    });

    // Adicionar planetas nas casas
    data.planets_in_houses.forEach((houseData) => {
      houseData.planets.forEach((planet) => {
        const planetKey = 'planet_key' in planet ? planet.planet_key : `point_${planet.point || planet.planet}`;
        const planetName = 'planet' in planet ? planet.planet : planet.point || '';
        allItems.push({
          key: planetKey,
          name: planetName,
          sign: planet.sign,
          house: houseData.house,
        });
      });
    });

    // Obter signos do mapa para contexto (uma vez para todas as chamadas)
    const sunSign = data.planets_in_signs.find(p => p.planet === 'Sol')?.sign || userData.sunSign || 'Áries';
    const moonSign = data.planets_in_signs.find(p => p.planet === 'Lua')?.sign || userData.moonSign || 'Touro';
    const ascendant = data.special_points.find(p => p.point === 'Ascendente')?.sign || userData.ascendant || 'Gêmeos';
    
    // Usar Set para evitar duplicatas
    const loadedKeys = new Set<string>();
    
    // Ordenar por prioridade: planetas principais primeiro
    const priorityOrder: Record<string, number> = {
      'Sol': 1,
      'Lua': 2,
      'Ascendente': 3,
      'Meio do Céu': 4,
      'Mercúrio': 5,
      'Vênus': 6,
      'Marte': 7,
      'Júpiter': 8,
      'Saturno': 9,
      'Urano': 10,
      'Netuno': 11,
      'Plutão': 12,
      'Nódulo Norte': 13,
      'Nódulo Sul': 14,
      'Quíron': 15
    };
    
    // Ordenar items por prioridade
    allItems.sort((a, b) => {
      const priorityA = priorityOrder[a.name] || 999;
      const priorityB = priorityOrder[b.name] || 999;
      return priorityA - priorityB;
    });
    
    // Carregar uma interpretação por vez para mostrar progresso incremental
    // Isso permite que o usuário veja os resultados aparecendo progressivamente
    for (const item of allItems) {
      // Evitar carregar a mesma chave duas vezes
      if (loadedKeys.has(item.key)) {
        continue;
      }
      loadedKeys.add(item.key);
      
      setLoadingInterpretations(prev => ({ ...prev, [item.key]: true }));
      
      try {
        const response = await apiService.getPlanetInterpretation({
          planet: item.name,
          sign: item.sign,
          house: item.house,
          sunSign: sunSign,
          moonSign: moonSign,
          ascendant: ascendant,
          userName: userData.name || 'Usuário',
        });
        
        setPlanetInterpretations(prev => ({
          ...prev,
          [item.key]: response.interpretation,
        }));
      } catch (err) {
        console.error(`Erro ao carregar interpretação de ${item.name}:`, err);
        // Continuar para próximo item mesmo se houver erro
      } finally {
        setLoadingInterpretations(prev => ({ ...prev, [item.key]: false }));
      }
    }
  };


  // Dados do usuário para exibição
  const sunSign = userData.sunSign || 'Áries';
  const moonSign = userData.moonSign || 'Touro';
  const ascendant = userData.ascendant || 'Gêmeos';
  
  // Ícones dos signos
  const SunIcon = zodiacSigns.find(z => z.name === sunSign)?.icon || zodiacSigns[0].icon;
  const MoonIcon = zodiacSigns.find(z => z.name === moonSign)?.icon || zodiacSigns[0].icon;
  const AscIcon = zodiacSigns.find(z => z.name === ascendant)?.icon || zodiacSigns[0].icon;

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
            onClick={loadCompleteChart}
            disabled={isGenerating}
            className="birth-chart-generate-button"
          >
            <div className="birth-chart-generate-button-shine"></div>
            {isGenerating ? (
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

      {/* Loading State */}
      {isGenerating && (
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
      )}

      {/* Error State */}
      {error && !isGenerating && (
        <div className="birth-chart-sections">
          <div className="birth-chart-error">
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* MAPA ASTRAL COMPLETO - Tudo em uma única aba, ordenado numericamente */}
      {chartData && !isGenerating && (
        <div className="birth-chart-sections">
          <div className="complete-chart-planets-list">
            {/* Combinar todos os itens em uma única lista ordenada */}
            {(() => {
              // Criar lista unificada com todos os itens
              const allItems: Array<{
                key: string;
                name: string;
                sign: string;
                degree_dms: string;
                is_retrograde?: boolean;
                house: number;
                type: 'planet' | 'point' | 'house_planet';
                houseName?: string;
              }> = [];
              
              // Set para rastrear chaves já adicionadas e evitar duplicatas
              const addedKeys = new Set<string>();

              // Adicionar planetas nos signos
              chartData.planets_in_signs.forEach((planet) => {
                if (!addedKeys.has(planet.planet_key)) {
                  addedKeys.add(planet.planet_key);
                  const houseName = planet.house ? (HOUSE_NAMES_PT[planet.house] || `Casa ${planet.house}`) : undefined;
                  allItems.push({
                    key: planet.planet_key,
                    name: planet.planet,
                    sign: planet.sign,
                    degree_dms: planet.degree_dms,
                    is_retrograde: planet.is_retrograde,
                    house: planet.house,
                    type: 'planet',
                    houseName: houseName
                  });
                }
              });

              // Adicionar pontos especiais
              chartData.special_points.forEach((point) => {
                if (!addedKeys.has(point.point_key)) {
                  addedKeys.add(point.point_key);
                  const houseName = point.house ? (HOUSE_NAMES_PT[point.house] || `Casa ${point.house}`) : undefined;
                  allItems.push({
                    key: point.point_key,
                    name: point.point,
                    sign: point.sign,
                    degree_dms: point.degree_dms,
                    house: point.house,
                    type: 'point',
                    houseName: houseName
                  });
                }
              });

              // Adicionar planetas nas casas (apenas se não foram adicionados anteriormente)
              chartData.planets_in_houses.forEach((houseData) => {
                const houseName = HOUSE_NAMES_PT[houseData.house] || `Casa ${houseData.house}`;
                houseData.planets.forEach((planet) => {
                  const planetKey = 'planet_key' in planet ? planet.planet_key : `point_${planet.point || planet.planet}`;
                  const planetName = 'planet' in planet ? planet.planet : planet.point || '';
                  
                  // Verificar se já foi adicionado (pode estar em planets_in_signs ou special_points)
                  if (!addedKeys.has(planetKey)) {
                    addedKeys.add(planetKey);
                    allItems.push({
                      key: planetKey,
                      name: planetName,
                      sign: planet.sign,
                      degree_dms: planet.degree_dms,
                      is_retrograde: 'is_retrograde' in planet ? planet.is_retrograde : false,
                      house: houseData.house,
                      type: 'house_planet',
                      houseName: houseName
                    });
                  }
                });
              });

              // Ordenar numericamente por número (se houver ordem definida) ou manter ordem original
              // Para manter ordem lógica: planetas primeiro, depois pontos, depois casas
              const planetOrder: Record<string, number> = {
                'Sol': 1, 'Lua': 2, 'Mercúrio': 3, 'Vênus': 4, 'Marte': 5,
                'Júpiter': 6, 'Saturno': 7, 'Urano': 8, 'Netuno': 9, 'Plutão': 10,
                'Ascendente': 11, 'Meio do Céu': 12, 'Nódulo Norte': 13, 'Nódulo Sul': 14, 'Quíron': 15
              };

              allItems.sort((a, b) => {
                const orderA = planetOrder[a.name] || 999;
                const orderB = planetOrder[b.name] || 999;
                if (orderA !== orderB) return orderA - orderB;
                // Se mesma ordem, manter tipo: planet > point > house_planet
                const typeOrder = { 'planet': 1, 'point': 2, 'house_planet': 3 };
                return typeOrder[a.type] - typeOrder[b.type];
              });

              return allItems.map((item) => {
                const interpretation = planetInterpretations[item.key];
                const isLoadingInterpretation = loadingInterpretations[item.key];

                return (
                  <div key={item.key} className="complete-chart-planet-item">
                    <div className="complete-chart-planet-header">
                      <h4 className="complete-chart-planet-name">
                        {item.name} em {item.sign} {item.degree_dms}
                        {item.is_retrograde && (
                          <span className="complete-chart-retrograde"> Rx</span>
                        )}
                        {item.houseName && (
                          <span className="complete-chart-house-badge"> • {item.houseName}</span>
                        )}
                      </h4>
                    </div>
                    
                    {isLoadingInterpretation && (
                      <div className="birth-chart-section-loading">
                        <div className="birth-chart-section-loading-line"></div>
                        <div className="birth-chart-section-loading-line w-5-6"></div>
                      </div>
                    )}
                    
                    {interpretation && (
                      <div className="complete-chart-planet-interpretation">
                        {formatGroqText(interpretation, language, item.name, item.sign)}
                      </div>
                    )}
                  </div>
                );
              });
            })()}
          </div>
        </div>
      )}
    </div>
  );
};

export default CompleteBirthChartSection;

import { OnboardingData } from '../../onboarding';

type Element = 'Fogo' | 'Terra' | 'Ar' | 'Água';

// Mapeamento de signos para elementos
const SIGN_TO_ELEMENT: Record<string, Element> = {
  'Áries': 'Fogo', 'Leão': 'Fogo', 'Sagitário': 'Fogo',
  'Touro': 'Terra', 'Virgem': 'Terra', 'Capricórnio': 'Terra',
  'Gêmeos': 'Ar', 'Libra': 'Ar', 'Aquário': 'Ar',
  'Câncer': 'Água', 'Escorpião': 'Água', 'Peixes': 'Água'
};

/** Distribuição dos elementos (Fogo/Terra/Ar/Água) entre os signos dos planetas e do ascendente. */
export const computeElementDistribution = (userData: OnboardingData, language: string) => {
  // Calcular distribuição real dos elementos baseado nos planetas
  const planetSigns = [
    userData.sunSign,
    userData.moonSign,
    userData.ascendant,
    userData.mercurySign,
    userData.venusSign,
    userData.marsSign,
    userData.jupiterSign,
    userData.saturnSign,
    userData.uranusSign,
    userData.neptuneSign,
    userData.plutoSign,
  ].filter(Boolean) as string[];

  const elementCounts = {
    'Fogo': 0,
    'Terra': 0,
    'Ar': 0,
    'Água': 0
  };

  planetSigns.forEach(sign => {
    const element = SIGN_TO_ELEMENT[sign];
    if (element) {
      elementCounts[element]++;
    }
  });

  const total = planetSigns.length || 1; // Evitar divisão por zero

  const elementDataWithCounts = [
    { 
      name: language === 'pt' ? 'Fogo' : 'Fire', 
      percentage: Math.round((elementCounts['Fogo'] / total) * 100), 
      color: '#F97316',
      count: elementCounts['Fogo']
    },
    { 
      name: language === 'pt' ? 'Terra' : 'Earth', 
      percentage: Math.round((elementCounts['Terra'] / total) * 100), 
      color: '#22C55E',
      count: elementCounts['Terra']
    },
    { 
      name: language === 'pt' ? 'Ar' : 'Air', 
      percentage: Math.round((elementCounts['Ar'] / total) * 100), 
      color: '#3B82F6',
      count: elementCounts['Ar']
    },
    { 
      name: language === 'pt' ? 'Água' : 'Water', 
      percentage: Math.round((elementCounts['Água'] / total) * 100), 
      color: '#8B5CF6',
      count: elementCounts['Água']
    },
  ];

  // ElementData para o gráfico (sem count)
  const elementData = elementDataWithCounts.map(({ count, ...rest }) => rest);

  // Identificar elemento dominante e em falta
  const dominantElement = elementDataWithCounts.reduce((max, el) => el.percentage > max.percentage ? el : max);
  const missingElement = elementDataWithCounts.find(el => el.count === 0);

  return { elementData, dominantElement, missingElement };
};

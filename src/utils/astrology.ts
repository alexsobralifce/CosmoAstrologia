import { OnboardingData } from '../components/onboarding';

const toRadians = (deg: number) => (deg * Math.PI) / 180;
const toDegrees = (rad: number) => (rad * 180) / Math.PI;
const normalizeAngle = (deg: number) => {
  const normalized = deg % 360;
  return normalized < 0 ? normalized + 360 : normalized;
};

const ZODIAC_ORDER = [
  'Áries',
  'Touro',
  'Gêmeos',
  'Câncer',
  'Leão',
  'Virgem',
  'Libra',
  'Escorpião',
  'Sagitário',
  'Capricórnio',
  'Aquário',
  'Peixes',
];

const combineDateTime = (date: Date, time: string) => {
  const [hours, minutes] = time.split(':').map((part) => parseInt(part, 10));
  const combined = new Date(date);
  combined.setHours(hours || 0, minutes || 0, 0, 0);
  return combined;
};

const toJulianDay = (date: Date) => {
  return date.getTime() / 86400000 + 2440587.5;
};

const getZodiacFromLongitude = (longitude: number) => {
  const index = Math.floor(normalizeAngle(longitude) / 30) % 12;
  const sign = ZODIAC_ORDER[index];
  const degree = normalizeAngle(longitude) % 30;
  return { sign, degree };
};

const calculateSunLongitude = (date: Date) => {
  const jd = toJulianDay(date);
  const n = jd - 2451545.0;
  const L = normalizeAngle(280.460 + 0.9856474 * n);
  const g = normalizeAngle(357.528 + 0.9856003 * n);
  const lambda =
    L +
    1.915 * Math.sin(toRadians(g)) +
    0.020 * Math.sin(toRadians(2 * g));
  return normalizeAngle(lambda);
};

const calculateMoonLongitude = (date: Date) => {
  const jd = toJulianDay(date);
  const n = jd - 2451545.0;
  const L = normalizeAngle(218.316 + 13.176396 * n);
  const M = normalizeAngle(134.963 + 13.064993 * n);
  const F = normalizeAngle(93.272 + 13.229350 * n);

  const longitude =
    L +
    6.289 * Math.sin(toRadians(M)) +
    1.274 * Math.sin(toRadians(2 * (L - M))) +
    0.658 * Math.sin(toRadians(2 * L)) +
    0.214 * Math.sin(toRadians(2 * M)) -
    0.186 * Math.sin(toRadians(1.915 + 0.9856474 * n)) -
    0.114 * Math.sin(toRadians(2 * F));

  return normalizeAngle(longitude);
};

const calculateMeanNorthNodeLongitude = (date: Date) => {
  const jd = toJulianDay(date);
  const T = (jd - 2451545.0) / 36525.0;
  const longitude =
    125.04455501 -
    1934.1361849 * T +
    0.0020762 * T * T +
    (T * T * T) / 467410 -
    (T * T * T * T) / 60616000;
  return normalizeAngle(longitude);
};

const calculateAscendantLongitude = (
  date: Date,
  latitude: number,
  longitude: number
) => {
  const jd = toJulianDay(date);
  const T = (jd - 2451545.0) / 36525.0;
  // Fórmula de obliquidade da eclíptica (mesma do backend)
  const epsilon = 23.439291 - 0.0130042 * T - 1.64e-7 * T * T + 5.04e-7 * T * T * T;
  
  // Calcular GMST (Greenwich Mean Sidereal Time)
  const gmst =
    280.46061837 +
    360.98564736629 * (jd - 2451545.0) +
    0.000387933 * T * T -
    (T * T * T) / 38710000;
  
  // Local Sidereal Time (LST) = GMST + longitude (em graus)
  const lst = normalizeAngle(gmst + longitude);
  const lstRad = toRadians(lst);
  const latRad = toRadians(latitude);
  const epsilonRad = toRadians(epsilon);

  // Fórmula correta para o ascendente (mesma do backend)
  // ASC = atan2(cos(LST), -(sin(LST) * cos(obliquity) + tan(lat) * sin(obliquity)))
  const numerator = Math.cos(lstRad);
  const denominator = -(
    Math.sin(lstRad) * Math.cos(epsilonRad) +
    Math.tan(latRad) * Math.sin(epsilonRad)
  );
  
  const ascRad = Math.atan2(numerator, denominator);
  const ascDeg = normalizeAngle(toDegrees(ascRad));

  return ascDeg;
};

// Função para obter o planeta regente baseado no signo do ascendente
export const getChartRuler = (ascendantSign: string): string => {
  const rulerMap: Record<string, string> = {
    'Áries': 'Marte',
    'Touro': 'Vênus',
    'Gêmeos': 'Mercúrio',
    'Câncer': 'Lua',
    'Leão': 'Sol',
    'Virgem': 'Mercúrio',
    'Libra': 'Vênus',
    'Escorpião': 'Plutão', // Moderno (tradicional: Marte)
    'Sagitário': 'Júpiter',
    'Capricórnio': 'Saturno',
    'Aquário': 'Urano', // Moderno (tradicional: Saturno)
    'Peixes': 'Netuno', // Moderno (tradicional: Júpiter)
  };
  return rulerMap[ascendantSign] || 'Desconhecido';
};

export const calculateChartBasics = (data: OnboardingData) => {
  const { birthDate, birthTime, coordinates } = data;
  if (!birthDate || !birthTime) {
    return {
      sun: null,
      moon: null,
      ascendant: null,
      planets: [],
    };
  }

  const combined = combineDateTime(birthDate, birthTime);
  const sunLongitude = calculateSunLongitude(combined);
  const moonLongitude = calculateMoonLongitude(combined);

  const sun = getZodiacFromLongitude(sunLongitude);
  const moon = getZodiacFromLongitude(moonLongitude);

  let ascendant = null;
  if (coordinates) {
    const ascLongitude = calculateAscendantLongitude(
      combined,
      coordinates.latitude,
      coordinates.longitude
    );
    ascendant = getZodiacFromLongitude(ascLongitude);
  }

  return {
    sun,
    moon,
    ascendant,
    planets: [],
  };
};

export const getMoonSignForDate = (date: Date) => {
  const moonLongitude = calculateMoonLongitude(date);
  return getZodiacFromLongitude(moonLongitude);
};

export const getLunarNodesInfo = (date?: Date | null) => {
  if (!date) {
    return null;
  }
  const northLongitude = calculateMeanNorthNodeLongitude(date);
  const southLongitude = northLongitude + 180;
  return {
    north: getZodiacFromLongitude(northLongitude),
    south: getZodiacFromLongitude(southLongitude),
  };
};


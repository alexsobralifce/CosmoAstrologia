import type { HttpClient } from './http-client';

export const createInterpretationApi = (http: HttpClient) => ({
  async getInterpretation(params: {
    planet?: string;
    sign?: string;
    house?: number;
    aspect?: string;
    custom_query?: string;
    use_groq?: boolean;
  }): Promise<{
    interpretation: string;
    sources: Array<{
      source: string;
      page: number;
      relevance: number;
    }>;
    query_used: string;
    generated_by?: string;
  }> {
    // Timeout maior para interpretações com RAG/Groq (60 segundos)
    return await http.request('/api/interpretation', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  },

  async getPlanetInterpretation(params: {
    planet: string;
    sign?: string;
    house?: number;
    sunSign?: string;
    moonSign?: string;
    ascendant?: string;
    userName?: string;
  }): Promise<{
    interpretation: string;
    sources: Array<{
      source: string;
      page: number;
      relevance: number;
    }>;
    query_used: string;
    generated_by?: string;
  }> {
    // Timeout maior para interpretações com RAG/DeepSeek (120 segundos)
    return await http.request('/api/interpretation/planet', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 120000);
  },

  async getChartRulerInterpretation(params: {
    ascendant: string;
    ruler: string;
    rulerSign: string;
    rulerHouse: number;
  }): Promise<{
    interpretation: string;
    sources: Array<{
      source: string;
      page: number;
      relevance: number;
    }>;
    query_used: string;
    generated_by?: string;
  }> {
    // Timeout maior para interpretações com RAG/Groq (60 segundos)
    return await http.request('/api/interpretation/chart-ruler', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  },

  async getAspectInterpretation(params: {
    planet1: string;
    planet2: string;
    aspect: string;
  }): Promise<{
    interpretation: string;
    sources: Array<{
      source: string;
      page: number;
      relevance: number;
    }>;
    query_used: string;
    generated_by?: string;
  }> {
    // Timeout maior para interpretações com RAG/Groq (60 segundos)
    return await http.request('/api/interpretation/aspect', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  },

  async getDailyAdvice(params: {
    moonHouse: number;
    category: string;
    moonSign?: string;
    planetaryPositions?: Array<{
      name: string;
      house: number;
      sign?: string;
    }>;
  }): Promise<{
    interpretation: string;
    sources: Array<{
      source: string;
      page: number;
      relevance: number;
    }>;
    query_used: string;
    generated_by?: string;
  }> {
    // Timeout maior para interpretações com RAG/Groq (60 segundos)
    return await http.request('/api/interpretation/daily-advice', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  },

  // ===== MAPA ASTRAL COMPLETO =====

  async getCompleteChart(params: {
    birthDate: string; // DD/MM/YYYY
    birthTime: string; // HH:MM
    latitude: number;
    longitude: number;
    birthPlace: string;
    name: string;
  }): Promise<{
    birth_data: {
      date: string;
      time: string;
      latitude: number;
      longitude: number;
    };
    planets_in_signs: Array<{
      planet: string;
      planet_key: string;
      sign: string;
      degree: number;
      degree_dms: string;
      is_retrograde: boolean;
      house: number;
    }>;
    special_points: Array<{
      point: string;
      point_key: string;
      sign: string;
      degree: number;
      degree_dms: string;
      house: number;
    }>;
    planets_in_houses: Array<{
      house: number;
      planets: Array<{
        planet: string;
        planet_key: string;
        sign: string;
        degree: number;
        degree_dms: string;
        house: number;
        is_retrograde?: boolean;
      }>;
    }>;
  }> {
    // Timeout maior para cálculo completo do mapa astral (120 segundos)
    // O cálculo com casas astrológicas pode ser demorado
    return await http.request('/api/interpretation/complete-chart', {
      method: 'POST',
      body: JSON.stringify({
        birth_date: params.birthDate,
        birth_time: params.birthTime,
        latitude: params.latitude,
        longitude: params.longitude,
        birth_place: params.birthPlace,
        name: params.name,
      }),
    }, 120000); // 120 segundos de timeout
  },

  async generateBirthChartSection(params: {
    name: string;
    birthDate: string;
    birthTime: string;
    birthPlace: string;
    sunSign: string;
    moonSign: string;
    ascendant: string;
    sunHouse: number;
    moonHouse: number;
    section: string;
    language?: string;
    // Planetas opcionais
    mercurySign?: string;
    mercuryHouse?: number;
    venusSign?: string;
    venusHouse?: number;
    marsSign?: string;
    marsHouse?: number;
    jupiterSign?: string;
    jupiterHouse?: number;
    saturnSign?: string;
    saturnHouse?: number;
    uranusSign?: string;
    uranusHouse?: number;
    neptuneSign?: string;
    neptuneHouse?: number;
    plutoSign?: string;
    plutoHouse?: number;
    northNodeSign?: string;
    northNodeHouse?: number;
    southNodeSign?: string;
    southNodeHouse?: number;
    chironSign?: string;
    chironHouse?: number;
    midheavenSign?: string;
    icSign?: string;
  }): Promise<{
    section: string;
    title: string;
    content: string;
    generated_by: string;
  }> {
    // Timeout maior para geração completa (90 segundos)
    return await http.request('/api/full-birth-chart/section', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 90000);
  },

  async getSynastryInterpretation(params: {
    sign1: string;
    sign2: string;
    language?: string;
  }): Promise<{
    interpretation: string;
    generated_by: string;
    sign1_info?: string;
    sign2_info?: string;
  }> {
    return await http.request('/api/synastry/interpretation', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 120000); // Timeout maior para interpretações completas
  },
});

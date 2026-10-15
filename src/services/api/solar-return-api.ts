import type { HttpClient } from './http-client';

export const createSolarReturnApi = (http: HttpClient) => ({
  async calculateSolarReturn(params: {
    birth_date: string; // ISO format
    birth_time: string; // HH:MM
    latitude: number;
    longitude: number;
    target_year?: number;
  }): Promise<{
    solar_return_date: string;
    target_year: number;
    ascendant_sign: string;
    ascendant_degree: number;
    sun_sign: string;
    sun_degree: number;
    sun_house: number;
    moon_sign: string;
    moon_degree: number;
    moon_house: number;
    venus_sign?: string;
    venus_degree?: number;
    venus_house?: number;
    mars_sign?: string;
    mars_degree?: number;
    mars_house?: number;
    jupiter_sign?: string;
    jupiter_degree?: number;
    jupiter_house?: number;
    saturn_sign?: string;
    saturn_degree?: number;
    midheaven_sign?: string;
    midheaven_degree?: number;
  }> {
    // Timeout maior para cálculos (45 segundos)
    return await http.request('/api/solar-return/calculate', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 45000);
  },

  async getSolarReturnInterpretation(params: {
    natal_sun_sign: string;
    natal_ascendant?: string;
    solar_return_ascendant?: string;
    solar_return_sun_house?: number;
    solar_return_moon_sign?: string;
    solar_return_moon_house?: number;
    solar_return_venus_sign?: string;
    solar_return_venus_house?: number;
    solar_return_mars_sign?: string;
    solar_return_mars_house?: number;
    solar_return_jupiter_sign?: string;
    solar_return_jupiter_house?: number;
    solar_return_saturn_sign?: string;
    solar_return_midheaven?: string;
    target_year?: number;
    language?: string;
    // Dados para recálculo (opcional)
    birth_date?: string;
    birth_time?: string;
    latitude?: number;
    longitude?: number;
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
    // Timeout maior para interpretações (90 segundos)
    return await http.request('/api/solar-return/interpretation', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 90000);
  },

});

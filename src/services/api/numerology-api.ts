import type { HttpClient } from './http-client';

export const createNumerologyApi = (http: HttpClient) => ({
  async getNumerologyMap(): Promise<{
    full_name: string;
    birth_date: string;
    life_path: {
      number: number;
      raw_total: number;
      is_master: boolean;
      day: number;
      day_reduced: number;
      month: number;
      month_reduced: number;
      year: number;
      year_reduced: number;
    };
    destiny: {
      number: number;
      raw_total: number;
      is_master: boolean;
    };
    soul: {
      number: number;
      raw_total: number;
      is_master: boolean;
    };
    personality: {
      number: number;
      raw_total: number;
      is_master: boolean;
    };
    birthday: {
      number: number;
      day: number;
      is_master: boolean;
    };
    maturity: {
      number: number;
      raw_total: number;
      is_master: boolean;
    };
    pinnacles: Array<{
      number: number;
      period: string;
      start_age: number;
      end_age: number | null;
    }>;
    challenges: Array<{
      number: number;
      period: string;
      start_age: number;
      end_age: number | null;
    }>;
    personal_year: {
      number: number;
      year: number;
      raw_total: number;
      is_master: boolean;
    };
    birth_grid: {
      grid: Record<number, number>;
      arrows_strength: string[];
      arrows_weakness: string[];
      missing_numbers: number[];
    };
    karmic_debts: number[];
    life_cycle: {
      cycle: string;
      cycle_number: number;
      age: number;
    };
  }> {
    // Timeout maior para cálculo completo do mapa numerológico (120 segundos)
    return await http.request('/api/numerology/map', {
      method: 'GET',
    }, 120000);
  },

  async getNumerologyInterpretation(params: {
    language?: string;
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
    return await http.request('/api/numerology/interpretation', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 120000); // Timeout maior para interpretações completas
  },

  async getBirthGridQuantitiesInterpretation(params: {
    grid: Record<number, number>;
    language?: string;
  }): Promise<{
    explanation: string;
    sources: Array<{
      source: string;
      page: number;
      relevance: number;
    }>;
    query_used: string;
  }> {
    return await http.request('/api/numerology/birth-grid-quantities', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  },
});

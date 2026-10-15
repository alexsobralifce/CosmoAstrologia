import type { HttpClient } from './http-client';

export const createTransitsApi = (http: HttpClient) => ({
  async getBestTiming(params: {
    action_type: string;
    days_ahead?: number;
  }): Promise<{
    action_type: string;
    action_config: any;
    best_moments: Array<{
      date: string;
      score: number;
      aspects: any[];
      reasons: string[];
      is_moon_void: boolean;
    }>;
    total_checked: number;
    analysis_date: string;
  }> {
    return await http.request('/api/best-timing/calculate', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  },

  async getCurrentPersonalTransits(): Promise<{
    active_transits: any[];
    moon_void_of_course: {
      is_void: boolean;
      void_end?: string;
      void_start?: string;
      next_aspect?: string;
      next_aspect_time?: string;
      current_moon_sign?: string;
      void_duration_hours?: number;
    };
    date: string;
    count: number;
  }> {
    return await http.request('/api/transits/current', {
      method: 'GET',
    }, 60000);
  },

  async getDailyInfo(params?: {
    latitude?: number;
    longitude?: number;
  }): Promise<{
    date: string;
    day_name: string;
    day: number;
    month: string;
    year: number;
    moon_phase: string;
    moon_sign: string;
    moon_phase_description: string;
    calculated_at: string;
  }> {
    const queryParams = new URLSearchParams();
    if (params?.latitude !== undefined) {
      queryParams.append('latitude', params.latitude.toString());
    }
    if (params?.longitude !== undefined) {
      queryParams.append('longitude', params.longitude.toString());
    }

    const url = `/api/daily-info${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return await http.request(url, {
      method: 'GET',
    });
  },

  async getFutureTransits(params?: {
    months_ahead?: number;
    max_transits?: number;
  }): Promise<{
    transits: Array<{
      id: string;
      type: 'jupiter' | 'saturn-return' | 'uranus' | 'neptune' | 'pluto';
      title: string;
      planet: string;
      timeframe: string;
      description: string;
      isActive: boolean;
      date: string;
      start_date: string;
      end_date: string;
      aspect_type: string;
      aspect_type_display: string;
      natal_point: string;
    }>;
    count: number;
  }> {
    const queryParams = new URLSearchParams();
    if (params?.months_ahead) {
      queryParams.append('months_ahead', params.months_ahead.toString());
    }
    if (params?.max_transits) {
      queryParams.append('max_transits', params.max_transits.toString());
    }

    const query = queryParams.toString();
    // Timeout maior para cálculos de trânsitos (45 segundos)
    return await http.request(`/api/transits/future${query ? `?${query}` : ''}`, {
      method: 'GET',
    }, 45000);
  }

  // Interpretações específicas usando RAG + Groq,
});

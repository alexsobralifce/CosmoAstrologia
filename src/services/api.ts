/**
 * API service for communicating with the astrology backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Auth token management
let authToken: string | null = null;

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
};

export const getAuthToken = (): string | null => {
  if (!authToken) {
    authToken = localStorage.getItem('auth_token');
  }
  return authToken;
};

export interface BirthData {
  name: string;
  birth_date: string; // YYYY-MM-DD
  birth_time: string; // HH:MM
  birth_place: string;
}

export interface PlanetPosition {
  planet: string;
  sign: string;
  house: number;
  degree: number;
  minutes: number;
}

export interface House {
  number: number;
  cusp_sign: string;
  cusp_degree: number;
  planets_in_house: string[];
}

export interface Aspect {
  planet1: string;
  planet2: string;
  type: string;
  orb: number;
  is_positive: boolean;
}

export interface BigThree {
  sun: string;
  moon: string;
  ascendant: string;
}

export interface ElementData {
  name: string;
  percentage: number;
  color: string;
}

export interface ModalityData {
  name: string;
  percentage: number;
  color: string;
}

export interface ChartRuler {
  ascendant: string;
  ruler: string;
  ruler_sign: string;
  ruler_house: number;
}

export interface BirthChartResponse {
  birth_data: BirthData;
  big_three: BigThree;
  planets: PlanetPosition[];
  houses: House[];
  aspects: Aspect[];
  elements: ElementData[];
  modalities: ModalityData[];
  chart_ruler: ChartRuler;
}

export interface PlanetInterpretation {
  planet: string;
  sign: string;
  house: number;
  in_sign: string;
  in_house: string;
}

export interface HouseInterpretation {
  house_number: number;
  theme: string;
  interpretation: string;
}

export interface AspectInterpretation {
  aspect: Aspect;
  interpretation: string;
  tags: string[];
}

export interface DailyTransit {
  moon_sign: string;
  moon_house: number;
  moon_advice: string;
  is_mercury_retrograde: boolean;
  is_moon_void_of_course: boolean;
  void_ends_at: string | null;
}

export interface FutureTransit {
  type: string;
  title: string;
  planet: string;
  timeframe: string;
  description: string;
  is_active: boolean;
}

class ApiService {
  private async fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
    const token = getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async loginWithGoogle(): Promise<void> {
    // Redirect to backend OAuth endpoint
    window.location.href = `${API_BASE_URL}/api/auth/login`;
  }

  async getCurrentUser(): Promise<{
    id: string;
    email: string;
    name: string;
    picture?: string;
    created_at?: string;
  }> {
    return this.fetchJson('/api/auth/me');
  }

  async updateUser(name: string): Promise<{
    id: string;
    email: string;
    name: string;
    picture?: string;
    created_at?: string;
  }> {
    return this.fetchJson('/api/auth/me', {
      method: 'PUT',
      body: JSON.stringify({ name }),
    });
  }

  async getUserBirthData(): Promise<BirthData> {
    return this.fetchJson('/api/auth/birth-data');
  }

  async saveUserBirthData(birthData: BirthData): Promise<{ message: string }> {
    return this.fetchJson('/api/auth/birth-data', {
      method: 'POST',
      body: JSON.stringify(birthData),
    });
  }

  async logout(): Promise<void> {
    try {
      await this.fetchJson('/api/auth/logout', { method: 'POST' });
    } finally {
      setAuthToken(null);
    }
  }

  async saveChart(chartData: BirthData): Promise<void> {
    return this.fetchJson('/api/auth/save-chart', {
      method: 'POST',
      body: JSON.stringify(chartData),
    });
  }

  async getSavedChart(): Promise<BirthData> {
    return this.fetchJson('/api/auth/chart');
  }

  async calculateChart(birthData: BirthData): Promise<BirthChartResponse> {
    return this.fetchJson<BirthChartResponse>('/api/charts/calculate', {
      method: 'POST',
      body: JSON.stringify(birthData),
    });
  }

  async getPlanetInterpretation(
    planetName: string,
    sign: string,
    house: number,
    chart: BirthChartResponse
  ): Promise<PlanetInterpretation> {
    return this.fetchJson<PlanetInterpretation>(`/api/interpretations/planet/${planetName}?sign=${sign}&house=${house}`, {
      method: 'POST',
      body: JSON.stringify(chart),
    });
  }

  async getHouseInterpretation(houseNumber: number, chart: BirthChartResponse): Promise<HouseInterpretation> {
    return this.fetchJson<HouseInterpretation>(`/api/interpretations/house/${houseNumber}`, {
      method: 'POST',
      body: JSON.stringify(chart),
    });
  }

  async getAspectInterpretation(
    planet1: string,
    planet2: string,
    aspectType: string,
    orb: number,
    chart: BirthChartResponse
  ): Promise<AspectInterpretation> {
    return this.fetchJson<AspectInterpretation>(
      `/api/interpretations/aspect?planet1=${planet1}&planet2=${planet2}&aspect_type=${aspectType}&orb=${orb}`,
      {
        method: 'POST',
        body: JSON.stringify(chart),
      }
    );
  }

  async getChartRulerInterpretation(chart: BirthChartResponse): Promise<{
    concept: string;
    positioning: string;
    influence: string;
  }> {
    return this.fetchJson('/api/interpretations/chart-ruler', {
      method: 'POST',
      body: JSON.stringify(chart),
    });
  }

  async getDailyTransits(chart: BirthChartResponse, date?: string): Promise<DailyTransit> {
    const url = date
      ? `/api/transits/daily?date=${date}`
      : '/api/transits/daily';
    return this.fetchJson<DailyTransit>(url, {
      method: 'POST',
      body: JSON.stringify(chart),
    });
  }

  async getFutureTransits(chart: BirthChartResponse, monthsAhead: number = 24): Promise<FutureTransit[]> {
    return this.fetchJson<FutureTransit[]>(`/api/transits/future?months_ahead=${monthsAhead}`, {
      method: 'POST',
      body: JSON.stringify(chart),
    });
  }
}

export const apiService = new ApiService();


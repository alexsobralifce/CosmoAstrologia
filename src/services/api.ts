const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface BirthData {
  name: string;
  birth_date: string; // ISO format
  birth_time: string; // "HH:MM"
  birth_place: string;
  latitude: number;
  longitude: number;
}

export interface UserRegisterData {
  email: string;
  password?: string;
  name: string;
  birth_data: BirthData;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface BirthChartResponse {
  id: number;
  user_id: number;
  name: string;
  birth_date: string;
  birth_time: string;
  birth_place: string;
  latitude: number;
  longitude: number;
  sun_sign: string;
  moon_sign: string;
  ascendant_sign: string;
  sun_degree?: number;
  moon_degree?: number;
  ascendant_degree?: number;
  // Planetas principais
  mercury_sign?: string;
  mercury_degree?: number;
  venus_sign?: string;
  venus_degree?: number;
  mars_sign?: string;
  mars_degree?: number;
  jupiter_sign?: string;
  jupiter_degree?: number;
  saturn_sign?: string;
  saturn_degree?: number;
  uranus_sign?: string;
  uranus_degree?: number;
  neptune_sign?: string;
  neptune_degree?: number;
  pluto_sign?: string;
  pluto_degree?: number;
  midheaven_sign?: string;
  midheaven_degree?: number;
  planets_conjunct_midheaven?: string[];
  uranus_on_midheaven?: boolean;
  // Nodos Lunares
  north_node_sign?: string;
  north_node_degree?: number;
  south_node_sign?: string;
  south_node_degree?: number;
  // Quíron (a ferida do curador)
  chiron_sign?: string;
  chiron_degree?: number;
  is_primary: boolean;
  created_at: string;
  updated_at?: string;
}

class ApiService {
  private getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    timeout: number = 30000
  ): Promise<T> {
    const token = this.getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const url = `${API_BASE_URL}${endpoint}`;
    // Log apenas em desenvolvimento
    if (import.meta.env.DEV) {
      console.log(`[API] Requisição: ${options.method || 'GET'} ${url}`);
    }

    let response: Response;
    
    try {
      response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
      });
    } catch (fetchError) {
      clearTimeout(timeoutId);
      
      if (fetchError instanceof Error) {
        if (fetchError.name === 'AbortError') {
          throw new Error(`Timeout: A requisição demorou mais de ${timeout / 1000}s.`);
        }
        
        // Erro de conexão
        if (fetchError.message.includes('Failed to fetch') || 
            fetchError.message.includes('NetworkError') ||
            fetchError.message.includes('Network request failed')) {
          throw new Error(
            `Não foi possível conectar ao backend em ${API_BASE_URL}.\n\n` +
            `Verifique se o backend está rodando e acessível.`
          );
        }
      }
      
      throw fetchError;
    } finally {
      clearTimeout(timeoutId);
    }

      // Log apenas em desenvolvimento
      if (import.meta.env.DEV) {
        console.log(`[API] Resposta: ${response.status} ${response.statusText}`);
      }

    // Clonar a resposta para poder ler o body com segurança
    const clonedResponse = response.clone();
    
    let data: T | null = null;
    let errorText = '';

    try {
      // Tentar ler como JSON primeiro
      data = await response.json();
    } catch {
      // Se não for JSON, ler como texto do clone
      try {
        errorText = await clonedResponse.text();
      } catch {
        errorText = '';
      }
    }

    if (!response.ok) {
      let errorMessage = `Erro ${response.status}`;
      
      if (data && typeof data === 'object') {
        const errorData = data as Record<string, unknown>;
        errorMessage = (errorData.detail as string) || (errorData.message as string) || errorMessage;
      } else if (errorText) {
        // Tentar parsear o texto como JSON
        try {
          const parsed = JSON.parse(errorText);
          errorMessage = parsed.detail || parsed.message || errorText;
        } catch {
          errorMessage = errorText || errorMessage;
        }
      }
      
      // Log apenas em desenvolvimento
      if (import.meta.env.DEV) {
        console.error('[API] Erro:', errorMessage);
      }
      throw new Error(errorMessage);
    }

    if (data !== null) {
      // Log apenas em desenvolvimento
      if (import.meta.env.DEV) {
        console.log('[API] Dados recebidos');
      }
      return data;
    }

    return null as T;
  }

  async registerUser(data: UserRegisterData): Promise<AuthToken | { message: string; requires_verification: boolean; email: string }> {
    // Timeout maior para registro (60s) pois inclui cálculo do mapa astral
    const response = await this.request<AuthToken | { message: string; requires_verification: boolean; email: string }>(
      '/api/auth/register',
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      60000 // 60 segundos de timeout
    );

    // Se retornou token, salvar (caso não precise verificação)
    if (response && 'access_token' in response && response.access_token) {
      localStorage.setItem('auth_token', response.access_token);
    }

    return response;
  }

  async verifyEmail(email: string, code: string): Promise<AuthToken> {
    const response = await this.request<AuthToken>('/api/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ email, code }),
    });

    // Salvar token após verificação
    if (response.access_token) {
      localStorage.setItem('auth_token', response.access_token);
    }

    return response;
  }

  async resendVerificationCode(email: string): Promise<void> {
    await this.request('/api/auth/resend-verification', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async loginUser(email: string, password: string): Promise<AuthToken> {
    const response = await this.request<AuthToken>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    // Salvar token
    if (response.access_token) {
      localStorage.setItem('auth_token', response.access_token);
    }

    return response;
  }

  async getCurrentUser(): Promise<any> {
    const token = this.getAuthToken();
    if (!token) {
      return null;
    }

    try {
      return await this.request<any>('/api/auth/me');
    } catch {
      return null;
    }
  }

  async getUserBirthChart(): Promise<BirthChartResponse | null> {
    const token = this.getAuthToken();
    if (!token) {
      return null;
    }

    try {
      return await this.request<BirthChartResponse>('/api/auth/birth-chart');
    } catch {
      return null;
    }
  }

  async updateUser(data: {
    name?: string;
    email?: string;
    password?: string;
    birth_data?: BirthData;
  }): Promise<void> {
    await this.request('/api/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  logout() {
    localStorage.removeItem('auth_token');
  }

  // ===== AUTENTICAÇÃO GOOGLE =====
  
  async verifyGoogleToken(credential: string): Promise<{
    email: string;
    name: string;
    picture?: string;
    google_id: string;
  }> {
    const response = await this.request<{
      email: string;
      name: string;
      picture?: string;
      google_id: string;
    }>('/api/auth/google/verify', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    });

    return response;
  }

  async googleAuth(data: {
    email: string;
    name: string;
    google_id: string;
  }): Promise<{
    access_token: string;
    token_type: string;
    is_new_user: boolean;
    needs_onboarding: boolean;
  }> {
    const response = await this.request<{
      access_token: string;
      token_type: string;
      is_new_user: boolean;
      needs_onboarding: boolean;
    }>('/api/auth/google', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    // Salvar token
    if (response.access_token) {
      localStorage.setItem('auth_token', response.access_token);
    }

    return response;
  }

  async completeOnboarding(data: {
    name: string;
    birth_date: string; // ISO format
    birth_time: string; // HH:MM
    birth_place: string;
    latitude: number;
    longitude: number;
  }): Promise<BirthChartResponse> {
    return await this.request<BirthChartResponse>('/api/auth/complete-onboarding', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // RAG - Interpretação Astrológica
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
    return await this.request('/api/interpretation', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  }

  async searchDocuments(query: string, top_k: number = 5): Promise<{
    query: string;
    results: Array<{
      text: string;
      score: number;
      source: string;
      page: number;
    }>;
    count: number;
  }> {
    return await this.request(`/api/interpretation/search?query=${encodeURIComponent(query)}&top_k=${top_k}`, {
      method: 'GET',
    });
  }

  async getRAGStatus(): Promise<{
    available: boolean;
    document_count?: number;
    has_dependencies?: boolean;
    has_groq?: boolean;
    error?: string;
  }> {
    return await this.request('/api/interpretation/status', {
      method: 'GET',
    });
  }

  // Trânsitos Futuros
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
    return await this.request('/api/best-timing/calculate', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  }

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
    return await this.request('/api/transits/current', {
      method: 'GET',
    }, 60000);
  }

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
    return await this.request(url, {
      method: 'GET',
    });
  }

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
    return await this.request(`/api/transits/future${query ? `?${query}` : ''}`, {
      method: 'GET',
    }, 45000);
  }

  // Interpretações específicas usando RAG + Groq
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
    return await this.request('/api/interpretation/planet', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 120000);
  }

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
    return await this.request('/api/interpretation/chart-ruler', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  }

  async getPlanetHouseInterpretation(params: {
    planet: string;
    house: number;
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
    return await this.request('/api/interpretation/planet-house', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  }

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
    return await this.request('/api/interpretation/aspect', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  }

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
    return await this.request('/api/interpretation/daily-advice', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  }

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
    return await this.request('/api/interpretation/complete-chart', {
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
  }

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
    return await this.request('/api/full-birth-chart/section', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 90000);
  }

  async generateFullBirthChart(params: {
    name: string;
    birthDate: string;
    birthTime: string;
    birthPlace: string;
    sunSign: string;
    moonSign: string;
    ascendant: string;
    sunHouse: number;
    moonHouse: number;
    language?: string;
    // Demais planetas opcionais...
    [key: string]: string | number | undefined;
  }): Promise<{
    name: string;
    birthData: string;
    sections: Array<{
      section: string;
      title: string;
      content: string;
      generated_by: string;
    }>;
    generated_at: string;
  }> {
    // Timeout muito maior para geração completa de todas as seções (5 minutos)
    return await this.request('/api/full-birth-chart/all', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 300000);
  }

  // ===== REVOLUÇÃO SOLAR =====

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
    return await this.request('/api/solar-return/calculate', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 45000);
  }

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
    return await this.request('/api/solar-return/interpretation', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 90000);
  }

  // ===== NUMEROLOGY MAP =====
  
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
    return await this.request('/api/numerology/map', {
      method: 'GET',
    }, 120000);
  }

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
    return await this.request('/api/numerology/interpretation', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 120000); // Timeout maior para interpretações completas
  }

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
    return await this.request('/api/numerology/birth-grid-quantities', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
  }

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
    return await this.request('/api/synastry/interpretation', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 120000); // Timeout maior para interpretações completas
  }
}

export const apiService = new ApiService();


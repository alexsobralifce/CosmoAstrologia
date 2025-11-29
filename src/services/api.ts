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
    console.log(`[API] Requisição: ${options.method || 'GET'} ${url}`);

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

    console.log(`[API] Resposta: ${response.status} ${response.statusText}`);

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
      
      console.error('[API] Erro:', errorMessage);
      throw new Error(errorMessage);
    }

    if (data !== null) {
      console.log('[API] Dados recebidos');
      return data;
    }

    return null as T;
  }

  async registerUser(data: UserRegisterData): Promise<AuthToken> {
    const response = await this.request<AuthToken>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    // Salvar token
    if (response.access_token) {
      localStorage.setItem('auth_token', response.access_token);
    }

    return response;
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
    // Timeout maior para interpretações com RAG/Groq (60 segundos)
    return await this.request('/api/interpretation/planet', {
      method: 'POST',
      body: JSON.stringify(params),
    }, 60000);
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
    solar_return_ascendant: string;
    solar_return_sun_house: number;
    solar_return_moon_sign: string;
    solar_return_moon_house: number;
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
}

export const apiService = new ApiService();


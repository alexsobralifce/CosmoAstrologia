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
  // Planetas principais (opcionais, podem não estar no banco ainda)
  mercury_sign?: string;
  venus_sign?: string;
  mars_sign?: string;
  jupiter_sign?: string;
  saturn_sign?: string;
  uranus_sign?: string;
  neptune_sign?: string;
  pluto_sign?: string;
  midheaven_sign?: string;
  midheaven_degree?: number;
  planets_conjunct_midheaven?: string[];
  uranus_on_midheaven?: boolean;
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
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const token = this.getAuthToken();
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...options.headers,
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Adicionar timeout de 30 segundos
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      const url = `${API_BASE_URL}${endpoint}`;
      console.log(`[API] Fazendo requisição para: ${url}`, options.method || 'GET');

      try {
        const response = await fetch(url, {
          ...options,
          headers,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        console.log(`[API] Resposta recebida:`, response.status, response.statusText);

        if (!response.ok) {
          let errorMessage = `HTTP error! status: ${response.status}`;
          try {
            const error = await response.json();
            errorMessage = error.detail || error.message || errorMessage;
            console.error('[API] Erro da resposta:', error);
          } catch {
            // Se não conseguir parsear JSON, usar mensagem padrão
            const text = await response.text();
            if (text) {
              errorMessage = text;
            }
            console.error('[API] Erro ao parsear resposta:', text);
          }
          throw new Error(errorMessage);
        }

        // Verificar se há conteúdo para parsear
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          console.log('[API] Dados recebidos:', data);
          return data;
        }
        
        // Se não for JSON, retornar texto vazio ou null
        return null as T;
      } catch (fetchError) {
        clearTimeout(timeoutId);
        console.error('[API] Erro na requisição:', fetchError);
        
        if (fetchError instanceof Error) {
          if (fetchError.name === 'AbortError') {
            throw new Error('Tempo de espera esgotado. Verifique se o servidor está rodando.');
          }
          // Verificar se é erro de conexão
          if (
            fetchError.message.includes('Failed to fetch') || 
            fetchError.message.includes('NetworkError') ||
            fetchError.message.includes('Network request failed') ||
            fetchError.message.includes('ERR_CONNECTION_REFUSED') ||
            fetchError.message.includes('ERR_NETWORK')
          ) {
            throw new Error('Não foi possível conectar ao servidor. Verifique se o backend está rodando em http://localhost:8000');
          }
          throw fetchError;
        }
        throw new Error('Erro desconhecido na requisição');
      }
    } catch (error) {
      console.error('[API] Erro geral:', error);
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Erro desconhecido na requisição');
    }
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
    return await this.request('/api/interpretation', {
      method: 'POST',
      body: JSON.stringify(params),
    });
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
      aspect_type: string;
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
    return await this.request(`/api/transits/future${query ? `?${query}` : ''}`, {
      method: 'GET',
    });
  }

  // Interpretações específicas usando RAG + Groq
  async getPlanetInterpretation(params: {
    planet: string;
    sign?: string;
    house?: number;
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
    return await this.request('/api/interpretation/planet', {
      method: 'POST',
      body: JSON.stringify(params),
    });
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
    return await this.request('/api/interpretation/chart-ruler', {
      method: 'POST',
      body: JSON.stringify(params),
    });
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
    return await this.request('/api/interpretation/planet-house', {
      method: 'POST',
      body: JSON.stringify(params),
    });
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
    return await this.request('/api/interpretation/aspect', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }
}

export const apiService = new ApiService();


import type { HttpClient } from './http-client';
import type { AuthToken, BirthChartResponse, BirthData, UserRegisterData } from './types';

export const createAuthApi = (http: HttpClient) => ({
  async registerUser(data: UserRegisterData): Promise<AuthToken | { message: string; requires_verification: boolean; email: string }> {
    // Timeout maior para registro (60s) pois inclui cálculo do mapa astral
    const response = await http.request<AuthToken | { message: string; requires_verification: boolean; email: string }>(
      '/api/auth/register',
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      60000 // 60 segundos de timeout
    );

    // Se retornou token, salvar (caso não precise verificação)
    if (response && 'access_token' in response && response.access_token) {
      http.storeToken(response.access_token);
    }

    return response;
  },

  async verifyEmail(email: string, code: string): Promise<AuthToken> {
    const response = await http.request<AuthToken>('/api/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ email, code }),
    });

    // Salvar token após verificação
    if (response.access_token) {
      http.storeToken(response.access_token);
    }

    return response;
  },

  async resendVerificationCode(email: string): Promise<void> {
    await http.request('/api/auth/resend-verification', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  async loginUser(email: string, password: string): Promise<AuthToken> {
    const response = await http.request<AuthToken>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    // Salvar token
    if (response.access_token) {
      http.storeToken(response.access_token);
    }

    return response;
  },

  async getCurrentUser(): Promise<any> {
    const token = http.getAuthToken();
    if (!token) {
      return null;
    }

    try {
      return await http.request<any>('/api/auth/me');
    } catch {
      return null;
    }
  },

  async getUserBirthChart(): Promise<BirthChartResponse | null> {
    const token = http.getAuthToken();
    if (!token) {
      return null;
    }

    try {
      return await http.request<BirthChartResponse>('/api/auth/birth-chart');
    } catch {
      return null;
    }
  },

  async updateUser(data: {
    name?: string;
    email?: string;
    password?: string;
    birth_data?: BirthData;
  }): Promise<void> {
    await http.request('/api/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  logout() {
    http.clearToken();
    // Apaga também o cookie httpOnly (melhor esforço; não bloqueia a saída)
    if (typeof window !== 'undefined') {
      void http.request('/api/auth/logout', { method: 'POST' }).catch(() => undefined);
    }
  },

  // ===== AUTENTICAÇÃO GOOGLE =====

  async verifyGoogleToken(credential: string): Promise<{
    email: string;
    name: string;
    picture?: string;
    google_id: string;
  }> {
    const response = await http.request<{
      email: string;
      name: string;
      picture?: string;
      google_id: string;
    }>('/api/auth/google/verify', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    });

    return response;
  },

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
    const response = await http.request<{
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
      http.storeToken(response.access_token);
    }

    return response;
  },

  async completeOnboarding(data: {
    name: string;
    birth_date: string; // ISO format
    birth_time: string; // HH:MM
    birth_place: string;
    latitude: number;
    longitude: number;
  }): Promise<BirthChartResponse> {
    return await http.request<BirthChartResponse>('/api/auth/complete-onboarding', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // RAG - Interpretação Astrológica,
});

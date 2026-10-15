/**
 * Cliente HTTP único: token, timeout, mensagens de erro e log de desenvolvimento.
 * Os módulos de domínio (auth, interpretação, trânsitos...) recebem uma instância por parâmetro.
 */
// Get API base URL from environment variable
// In production, NEXT_PUBLIC_API_URL must be set to the backend URL
// In development, falls back to localhost:8000
const getApiBaseUrl = (): string => {
  // Priority 1: Environment variable (required in production)
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Modo cookie em produção: a API é acessada pelo mesmo site (proxy do Next em /api)
  if (process.env.NEXT_PUBLIC_AUTH_MODE === 'cookie' && process.env.NODE_ENV === 'production') {
    return '';
  }

  // Priority 2: Development fallback
  if (process.env.NODE_ENV === 'development' || !process.env.NODE_ENV) {
    return 'http://localhost:8000';
  }

  // Production without API URL configured - log error
  if (typeof window !== 'undefined') {
    console.error(
      '⚠️ NEXT_PUBLIC_API_URL não está configurado! ' +
      'Configure esta variável no Vercel para produção.'
    );
  }

  // Fallback to localhost (will fail in production, but prevents build errors)
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiBaseUrl();

/**
 * 'cookie': o login vive num cookie httpOnly (o JS não vê o token). Exige front e API no mesmo site
 *           (proxy do Next, ver next.config.cjs) e NEXT_PUBLIC_API_URL vazio em produção.
 * 'token':  comportamento antigo (token no localStorage + cabeçalho Authorization).
 */
export const AUTH_MODE: 'cookie' | 'token' = process.env.NEXT_PUBLIC_AUTH_MODE === 'cookie' ? 'cookie' : 'token';

export class HttpClient {
  getAuthToken(): string | null {
    if (AUTH_MODE === 'cookie' || typeof window === 'undefined') {
      return null;
    }
    return localStorage.getItem('auth_token');
  }

  /** Guarda o token só no modo 'token'; no modo 'cookie' o backend já definiu o cookie httpOnly. */
  storeToken(token: string): void {
    if (AUTH_MODE === 'token') {
      localStorage.setItem('auth_token', token);
    }
  }

  clearToken(): void {
    localStorage.removeItem('auth_token');
  }


  async request<T>(
    endpoint: string,
    options: RequestInit = {},
    timeout: number = 30000
  ): Promise<T> {
    const token = this.getAuthToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> | undefined),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const url = `${API_BASE_URL}${endpoint}`;
    // Log apenas em desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API] Requisição: ${options.method || 'GET'} ${url}`);
    }

    let response: Response;

    try {
      response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal,
        credentials: AUTH_MODE === 'cookie' ? 'include' : options.credentials,
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
    if (process.env.NODE_ENV === 'development') {
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
      if (process.env.NODE_ENV === 'development') {
        console.error('[API] Erro:', errorMessage);
      }
      throw new Error(errorMessage);
    }

    if (data !== null) {
      // Log apenas em desenvolvimento
      if (process.env.NODE_ENV === 'development') {
        console.log('[API] Dados recebidos');
      }
      return data;
    }

    return null as T;
  }

}

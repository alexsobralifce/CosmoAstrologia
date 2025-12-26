import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from '@/components/theme-provider';
import { LanguageProvider } from '@/i18n/language-provider';

// Wrapper com todos os providers necessários
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <ThemeProvider>
      <LanguageProvider>
        {children}
      </LanguageProvider>
    </ThemeProvider>
  );
};

// Função customizada de render com providers
const renderWithProviders = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => {
  return render(ui, { wrapper: AllTheProviders, ...options });
};

// Helper para criar dados de usuário mockados
export const createMockUser = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  email_verified: true,
  created_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

// Helper para criar mapa astral mockado
export const createMockBirthChart = (overrides = {}) => ({
  id: 1,
  user_id: 1,
  name: 'Test User',
  birth_date: '1990-01-01',
  birth_time: '12:00',
  birth_place: 'São Paulo, SP, Brasil',
  latitude: -23.5505,
  longitude: -46.6333,
  sun_sign: 'Capricorn',
  moon_sign: 'Aries',
  ascendant_sign: 'Leo',
  sun_degree: 10.5,
  moon_degree: 20.3,
  ascendant_degree: 15.7,
  mercury_sign: 'Sagittarius',
  mercury_degree: 5.2,
  venus_sign: 'Aquarius',
  venus_degree: 25.8,
  mars_sign: 'Scorpio',
  mars_degree: 12.4,
  jupiter_sign: 'Cancer',
  jupiter_degree: 8.9,
  saturn_sign: 'Capricorn',
  saturn_degree: 18.6,
  uranus_sign: 'Capricorn',
  uranus_degree: 7.3,
  neptune_sign: 'Capricorn',
  neptune_degree: 14.1,
  pluto_sign: 'Scorpio',
  pluto_degree: 16.2,
  midheaven_sign: 'Taurus',
  midheaven_degree: 22.5,
  north_node_sign: 'Gemini',
  north_node_degree: 9.8,
  south_node_sign: 'Sagittarius',
  south_node_degree: 9.8,
  chiron_sign: 'Cancer',
  chiron_degree: 11.4,
  is_primary: true,
  created_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

// Helper para mockar respostas de API
export const mockApiResponse = <T,>(
  data: T,
  options: {
    status?: number;
    statusText?: string;
    ok?: boolean;
    headers?: HeadersInit;
  } = {}
) => {
  const {
    status = 200,
    statusText = 'OK',
    ok = true,
    headers = { 'Content-Type': 'application/json' },
  } = options;

  return Promise.resolve({
    ok,
    status,
    statusText,
    headers: new Headers(headers),
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    clone: function () {
      return this;
    },
  } as Response);
};

// Helper para mockar erros de API
export const mockApiError = (
  status: number,
  message: string,
  data?: any
) => {
  return Promise.resolve({
    ok: false,
    status,
    statusText: message,
    headers: new Headers({ 'Content-Type': 'application/json' }),
    json: () => Promise.resolve(data || { detail: message }),
    text: () => Promise.resolve(JSON.stringify(data || { detail: message })),
    clone: function () {
      return this;
    },
  } as Response);
};

// Helper para aguardar chamadas de API
export const waitForApiCall = async (
  mockFn: jest.Mock,
  timeout = 5000
) => {
  const startTime = Date.now();
  while (!mockFn.mock.calls.length && Date.now() - startTime < timeout) {
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  return mockFn.mock.calls.length > 0;
};

// Helper para simular delay
export const delay = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

// Re-exportar tudo do testing-library
export * from '@testing-library/react';
export { renderWithProviders };

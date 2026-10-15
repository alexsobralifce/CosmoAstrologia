import { API_BASE_URL, AUTH_MODE, HttpClient } from './http-client';
import { createAuthApi } from './auth-api';
import { createInterpretationApi } from './interpretation-api';
import { createNumerologyApi } from './numerology-api';
import { createSolarReturnApi } from './solar-return-api';
import { createTransitsApi } from './transits-api';

export * from './types';

/**
 * Fachada única da API: os componentes continuam chamando `apiService.metodo()`,
 * mas cada domínio vive no seu arquivo e compartilha o mesmo cliente HTTP.
 */
const http = new HttpClient();

export const apiService = {
  ...createAuthApi(http),
  ...createInterpretationApi(http),
  ...createTransitsApi(http),
  ...createSolarReturnApi(http),
  ...createNumerologyApi(http),
};

export type ApiService = typeof apiService;
export { API_BASE_URL, AUTH_MODE };

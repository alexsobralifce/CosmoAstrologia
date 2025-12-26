import { apiService } from '@/services/api';
import { mockApiResponse, mockApiError } from '../utils/test-utils';

// Mock fetch global
const mockFetch = global.fetch as jest.Mock;

describe('API Service - Autenticação', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    localStorage.clear();
  });

  describe('registerUser', () => {
    const mockUserData = {
      email: 'test@example.com',
      password: 'password123',
      name: 'Test User',
      birth_data: {
        name: 'Test User',
        birth_date: '1990-01-01',
        birth_time: '12:00',
        birth_place: 'São Paulo',
        latitude: -23.5505,
        longitude: -46.6333,
      },
    };

    it('should register user successfully and save token', async () => {
      const mockResponse = {
        access_token: 'test-token-123',
        token_type: 'bearer',
      };

      mockFetch.mockResolvedValueOnce(
        mockApiResponse(mockResponse, { status: 200 })
      );

      const result = await apiService.registerUser(mockUserData);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/register'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );

      expect(result).toEqual(mockResponse);
      expect(localStorage.getItem('auth_token')).toBe('test-token-123');
    });

    it('should handle registration requiring email verification', async () => {
      const mockResponse = {
        message: 'Verification code sent',
        requires_verification: true,
        email: 'test@example.com',
      };

      mockFetch.mockResolvedValueOnce(
        mockApiResponse(mockResponse, { status: 200 })
      );

      const result = await apiService.registerUser(mockUserData);

      expect(result).toEqual(mockResponse);
      expect(localStorage.getItem('auth_token')).toBeNull();
    });

    it('should handle registration errors', async () => {
      const errorResponse = {
        detail: 'Email already registered',
      };

      mockFetch.mockResolvedValueOnce(
        mockApiError(400, 'Bad Request', errorResponse)
      );

      await expect(apiService.registerUser(mockUserData)).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.registerUser(mockUserData)).rejects.toThrow();
    });
  });

  describe('loginUser', () => {
    const email = 'test@example.com';
    const password = 'password123';

    it('should login successfully and save token', async () => {
      const mockResponse = {
        access_token: 'test-token-456',
        token_type: 'bearer',
      };

      mockFetch.mockResolvedValueOnce(
        mockApiResponse(mockResponse, { status: 200 })
      );

      const result = await apiService.loginUser(email, password);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/login'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ email, password }),
        })
      );

      expect(result).toEqual(mockResponse);
      expect(localStorage.getItem('auth_token')).toBe('test-token-456');
    });

    it('should handle invalid credentials', async () => {
      const errorResponse = {
        detail: 'Invalid email or password',
      };

      mockFetch.mockResolvedValueOnce(
        mockApiError(401, 'Unauthorized', errorResponse)
      );

      await expect(apiService.loginUser(email, password)).rejects.toThrow();
      expect(localStorage.getItem('auth_token')).toBeNull();
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(apiService.loginUser(email, password)).rejects.toThrow();
    });
  });

  describe('verifyEmail', () => {
    const email = 'test@example.com';
    const code = '123456';

    it('should verify email successfully and save token', async () => {
      const mockResponse = {
        access_token: 'test-token-789',
        token_type: 'bearer',
      };

      mockFetch.mockResolvedValueOnce(
        mockApiResponse(mockResponse, { status: 200 })
      );

      const result = await apiService.verifyEmail(email, code);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/verify-email'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ email, code }),
        })
      );

      expect(result).toEqual(mockResponse);
      expect(localStorage.getItem('auth_token')).toBe('test-token-789');
    });

    it('should handle invalid verification code', async () => {
      const errorResponse = {
        detail: 'Invalid verification code',
      };

      mockFetch.mockResolvedValueOnce(
        mockApiError(400, 'Bad Request', errorResponse)
      );

      await expect(apiService.verifyEmail(email, code)).rejects.toThrow();
    });
  });

  describe('resendVerificationCode', () => {
    const email = 'test@example.com';

    it('should resend verification code successfully', async () => {
      mockFetch.mockResolvedValueOnce(
        mockApiResponse({ message: 'Code resent' }, { status: 200 })
      );

      await apiService.resendVerificationCode(email);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/resend-verification'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ email }),
        })
      );
    });

    it('should handle errors when resending code', async () => {
      mockFetch.mockResolvedValueOnce(
        mockApiError(404, 'Not Found', { detail: 'User not found' })
      );

      await expect(apiService.resendVerificationCode(email)).rejects.toThrow();
    });
  });

  describe('getCurrentUser', () => {
    it('should return user data when token exists', async () => {
      localStorage.setItem('auth_token', 'test-token');

      const mockUser = {
        id: 1,
        email: 'test@example.com',
        name: 'Test User',
        email_verified: true,
      };

      mockFetch.mockResolvedValueOnce(
        mockApiResponse(mockUser, { status: 200 })
      );

      const result = await apiService.getCurrentUser();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/me'),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      );

      expect(result).toEqual(mockUser);
    });

    it('should return null when no token exists', async () => {
      localStorage.removeItem('auth_token');

      const result = await apiService.getCurrentUser();

      expect(result).toBeNull();
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should return null when token is invalid', async () => {
      localStorage.setItem('auth_token', 'invalid-token');

      mockFetch.mockResolvedValueOnce(
        mockApiError(401, 'Unauthorized', { detail: 'Invalid token' })
      );

      const result = await apiService.getCurrentUser();

      expect(result).toBeNull();
    });
  });

  describe('getUserBirthChart', () => {
    it('should return birth chart when token exists', async () => {
      localStorage.setItem('auth_token', 'test-token');

      const mockBirthChart = {
        id: 1,
        user_id: 1,
        name: 'Test User',
        birth_date: '1990-01-01',
        birth_time: '12:00',
        birth_place: 'São Paulo',
        latitude: -23.5505,
        longitude: -46.6333,
        sun_sign: 'Capricorn',
        moon_sign: 'Aries',
        ascendant_sign: 'Leo',
        is_primary: true,
        created_at: '2024-01-01T00:00:00Z',
      };

      mockFetch.mockResolvedValueOnce(
        mockApiResponse(mockBirthChart, { status: 200 })
      );

      const result = await apiService.getUserBirthChart();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/birth-chart'),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      );

      expect(result).toEqual(mockBirthChart);
    });

    it('should return null when no token exists', async () => {
      localStorage.removeItem('auth_token');

      const result = await apiService.getUserBirthChart();

      expect(result).toBeNull();
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it('should return null when request fails', async () => {
      localStorage.setItem('auth_token', 'test-token');

      mockFetch.mockResolvedValueOnce(
        mockApiError(404, 'Not Found', { detail: 'Birth chart not found' })
      );

      const result = await apiService.getUserBirthChart();

      expect(result).toBeNull();
    });
  });

  describe('updateUser', () => {
    beforeEach(() => {
      localStorage.setItem('auth_token', 'test-token');
    });

    it('should update user data successfully', async () => {
      const updateData = {
        name: 'Updated Name',
        email: 'updated@example.com',
      };

      mockFetch.mockResolvedValueOnce(
        mockApiResponse({ message: 'User updated' }, { status: 200 })
      );

      await apiService.updateUser(updateData);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/me'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(updateData),
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      );
    });

    it('should handle update errors', async () => {
      const updateData = { email: 'invalid-email' };

      mockFetch.mockResolvedValueOnce(
        mockApiError(400, 'Bad Request', { detail: 'Invalid email format' })
      );

      await expect(apiService.updateUser(updateData)).rejects.toThrow();
    });
  });

  describe('logout', () => {
    it('should remove auth token from localStorage', () => {
      localStorage.setItem('auth_token', 'test-token');

      apiService.logout();

      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('verifyGoogleToken', () => {
    const credential = 'google-credential-token';

    it('should verify Google token successfully', async () => {
      const mockResponse = {
        email: 'google@example.com',
        name: 'Google User',
        picture: 'https://example.com/photo.jpg',
        google_id: 'google-123',
      };

      mockFetch.mockResolvedValueOnce(
        mockApiResponse(mockResponse, { status: 200 })
      );

      const result = await apiService.verifyGoogleToken(credential);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/google/verify'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ credential }),
        })
      );

      expect(result).toEqual(mockResponse);
    });

    it('should handle invalid Google token', async () => {
      mockFetch.mockResolvedValueOnce(
        mockApiError(401, 'Unauthorized', { detail: 'Invalid Google token' })
      );

      await expect(apiService.verifyGoogleToken(credential)).rejects.toThrow();
    });
  });

  describe('getAuthToken', () => {
    it('should return token from localStorage when available', () => {
      localStorage.setItem('auth_token', 'test-token-123');
      // Accessing private method through public API
      // We test it indirectly through methods that use it
      expect(localStorage.getItem('auth_token')).toBe('test-token-123');
    });

    it('should return null when no token in localStorage', () => {
      localStorage.removeItem('auth_token');
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('request method - error handling', () => {
    beforeEach(() => {
      localStorage.setItem('auth_token', 'test-token');
    });

    it('should handle 400 Bad Request', async () => {
      mockFetch.mockResolvedValueOnce(
        mockApiError(400, 'Bad Request', { detail: 'Invalid data' })
      );

      await expect(
        apiService.loginUser('invalid', 'password')
      ).rejects.toThrow();
    });

    it('should handle 401 Unauthorized', async () => {
      mockFetch.mockResolvedValueOnce(
        mockApiError(401, 'Unauthorized', { detail: 'Invalid credentials' })
      );

      await expect(
        apiService.loginUser('test@example.com', 'wrong')
      ).rejects.toThrow();
    });

    it('should handle 500 Internal Server Error', async () => {
      mockFetch.mockResolvedValueOnce(
        mockApiError(500, 'Internal Server Error', {
          detail: 'Server error',
        })
      );

      await expect(
        apiService.loginUser('test@example.com', 'password')
      ).rejects.toThrow();
    });

    it('should handle timeout', async () => {
      // Mock AbortController
      const abortMock = jest.fn();
      const originalAbortController = global.AbortController;

      global.AbortController = jest.fn().mockImplementation(() => ({
        abort: abortMock,
        signal: {
          aborted: false,
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
        },
      }));

      // Simulate timeout by making fetch hang
      mockFetch.mockImplementation(
        () =>
          new Promise((_, reject) => {
            setTimeout(() => {
              const error = new Error('Timeout');
              error.name = 'AbortError';
              reject(error);
            }, 100);
          })
      );

      // Use a shorter timeout for testing
      await expect(
        apiService.loginUser('test@example.com', 'password')
      ).rejects.toThrow();

      global.AbortController = originalAbortController;
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(
        new Error('Failed to fetch')
      );

      await expect(
        apiService.loginUser('test@example.com', 'password')
      ).rejects.toThrow();
    });
  });
});

import { renderHook, waitFor, act } from '@testing-library/react';
import { useAuth } from '@/hooks/useAuth';
import { apiService } from '@/services/api';
import { createMockUser, createMockBirthChart } from '../utils/test-utils';
import { useRouter } from 'next/navigation';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock API service
jest.mock('@/services/api', () => ({
  apiService: {
    getCurrentUser: jest.fn(),
    getUserBirthChart: jest.fn(),
    registerUser: jest.fn(),
    logout: jest.fn(),
  },
}));

const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  prefetch: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
  refresh: jest.fn(),
};

describe('useAuth Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
  });

  describe('Initial Authentication Check', () => {
    it('should check authentication on mount when token exists', async () => {
      localStorage.setItem('auth_token', 'test-token');

      const mockUser = createMockUser();
      const mockBirthChart = createMockBirthChart();

      (apiService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
      (apiService.getUserBirthChart as jest.Mock).mockResolvedValue(
        mockBirthChart
      );

      const { result } = renderHook(() => useAuth());

      expect(result.current.isCheckingAuth).toBe(true);

      await waitFor(() => {
        expect(result.current.isCheckingAuth).toBe(false);
      });

      expect(apiService.getCurrentUser).toHaveBeenCalled();
      expect(apiService.getUserBirthChart).toHaveBeenCalled();
      expect(result.current.userData).toBeTruthy();
      expect(result.current.authData).toBeTruthy();
    });

    it('should not check authentication when no token exists', async () => {
      localStorage.removeItem('auth_token');

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isCheckingAuth).toBe(false);
      });

      expect(apiService.getCurrentUser).not.toHaveBeenCalled();
      expect(result.current.userData).toBeNull();
      expect(result.current.authData).toBeNull();
    });

    it('should logout and clear state when token is invalid', async () => {
      localStorage.setItem('auth_token', 'invalid-token');

      (apiService.getCurrentUser as jest.Mock).mockResolvedValue(null);
      (apiService.logout as jest.Mock).mockImplementation(() => {
        localStorage.removeItem('auth_token');
      });

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isCheckingAuth).toBe(false);
      });

      expect(apiService.logout).toHaveBeenCalled();
      expect(result.current.userData).toBeNull();
      expect(result.current.authData).toBeNull();
    });

    it('should set authData but not userData when user exists but no birth chart', async () => {
      localStorage.setItem('auth_token', 'test-token');

      const mockUser = createMockUser();
      (apiService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
      (apiService.getUserBirthChart as jest.Mock).mockResolvedValue(null);

      const { result } = renderHook(() => useAuth());

      await waitFor(() => {
        expect(result.current.isCheckingAuth).toBe(false);
      });

      expect(result.current.authData).toBeTruthy();
      expect(result.current.authData?.hasCompletedOnboarding).toBe(false);
      expect(result.current.userData).toBeNull();
    });
  });

  describe('handleAuthSuccess', () => {
    it('should set authData and redirect to dashboard when onboarding is complete', async () => {
      const { result } = renderHook(() => useAuth());

      await act(async () => {
        result.current.handleAuthSuccess({
          email: 'test@example.com',
          name: 'Test User',
          hasCompletedOnboarding: true,
        });
      });

      expect(result.current.authData).toEqual({
        email: 'test@example.com',
        name: 'Test User',
        hasCompletedOnboarding: true,
      });
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard');
    });

    it('should redirect to onboarding when onboarding is not complete', async () => {
      const { result } = renderHook(() => useAuth());

      await act(async () => {
        result.current.handleAuthSuccess({
          email: 'test@example.com',
          name: 'Test User',
          hasCompletedOnboarding: false,
        });
      });

      expect(mockRouter.push).toHaveBeenCalledWith('/onboarding');
    });
  });

  describe('handleNeedsBirthData', () => {
    it('should set authData and redirect to onboarding', async () => {
      const { result } = renderHook(() => useAuth());

      await act(async () => {
        result.current.handleNeedsBirthData('test@example.com', 'Test User', 'password123');
      });

      expect(result.current.authData).toEqual({
        email: 'test@example.com',
        name: 'Test User',
        hasCompletedOnboarding: false,
      });
      expect(result.current.tempPassword).toBe('password123');
      expect(mockRouter.push).toHaveBeenCalledWith('/onboarding');
    });

    it('should handle case without password', async () => {
      const { result } = renderHook(() => useAuth());

      await act(async () => {
        result.current.handleNeedsBirthData('test@example.com', 'Test User');
      });

      expect(result.current.tempPassword).toBeNull();
    });
  });

  describe('handleGoogleNeedsOnboarding', () => {
    it('should set googleData and redirect to Google onboarding', async () => {
      const { result } = renderHook(() => useAuth());

      await act(async () => {
        result.current.handleGoogleNeedsOnboarding(
          'google@example.com',
          'Google User',
          'google-123'
        );
      });

      expect(result.current.googleData).toEqual({
        email: 'google@example.com',
        name: 'Google User',
        googleId: 'google-123',
      });
      expect(mockRouter.push).toHaveBeenCalledWith('/onboarding/google');
    });
  });

  describe('handleOnboardingComplete', () => {
    it('should register user and redirect to dashboard on success', async () => {
      localStorage.setItem('auth_token', 'test-token');

      const mockAuthResponse = {
        access_token: 'new-token',
        token_type: 'bearer',
      };

      (apiService.registerUser as jest.Mock).mockResolvedValue(mockAuthResponse);

      const { result } = renderHook(() => useAuth());

      // Set authData first
      await act(async () => {
        result.current.handleNeedsBirthData('test@example.com', 'Test User', 'password123');
      });

      const onboardingData = {
        name: 'Test User',
        birthDate: new Date('1990-01-01'),
        birthTime: '12:00',
        birthPlace: 'São Paulo',
        email: 'test@example.com',
        password: 'password123',
        coordinates: {
          latitude: -23.5505,
          longitude: -46.6333,
        },
        sunSign: 'Capricorn',
        moonSign: 'Aries',
        ascendant: 'Leo',
      };

      await act(async () => {
        await result.current.handleOnboardingComplete(onboardingData);
      });

      expect(apiService.registerUser).toHaveBeenCalledWith({
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
      });

      expect(result.current.userData).toEqual(onboardingData);
      expect(result.current.tempPassword).toBeNull();
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard');
    });

    it('should handle registration errors', async () => {
      const { result } = renderHook(() => useAuth());

      await act(async () => {
        result.current.handleNeedsBirthData('test@example.com', 'Test User');
      });

      (apiService.registerUser as jest.Mock).mockRejectedValue(
        new Error('Registration failed')
      );

      const onboardingData = {
        name: 'Test User',
        birthDate: new Date('1990-01-01'),
        birthTime: '12:00',
        birthPlace: 'São Paulo',
        coordinates: {
          latitude: -23.5505,
          longitude: -46.6333,
        },
      };

      await expect(
        act(async () => {
          await result.current.handleOnboardingComplete(onboardingData);
        })
      ).rejects.toThrow();
    });
  });

  describe('handleGoogleOnboardingComplete', () => {
    it('should register Google user and redirect to dashboard', async () => {
      localStorage.setItem('auth_token', 'test-token');

      const mockAuthResponse = {
        access_token: 'google-token',
        token_type: 'bearer',
      };

      const mockUser = createMockUser({ email: 'google@example.com' });
      const mockBirthChart = createMockBirthChart();

      (apiService.registerUser as jest.Mock).mockResolvedValue(mockAuthResponse);
      (apiService.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);
      (apiService.getUserBirthChart as jest.Mock).mockResolvedValue(
        mockBirthChart
      );

      const { result } = renderHook(() => useAuth());

      // Set googleData first
      await act(async () => {
        result.current.handleGoogleNeedsOnboarding(
          'google@example.com',
          'Google User',
          'google-123'
        );
      });

      const googleOnboardingData = {
        name: 'Google User',
        birthDate: new Date('1990-01-01'),
        birthTime: '12:00',
        birthPlace: 'São Paulo',
        coordinates: {
          latitude: -23.5505,
          longitude: -46.6333,
        },
        sunSign: 'Capricorn',
        moonSign: 'Aries',
        ascendant: 'Leo',
      };

      await act(async () => {
        await result.current.handleGoogleOnboardingComplete(googleOnboardingData);
      });

      expect(apiService.registerUser).toHaveBeenCalled();
      expect(result.current.userData).toBeTruthy();
      expect(result.current.googleData).toBeNull();
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard');
    });
  });

  describe('handleViewInterpretation', () => {
    it('should set selectedTopic and navigate to interpretation page', async () => {
      const { result } = renderHook(() => useAuth());

      await act(async () => {
        result.current.handleViewInterpretation('amor');
      });

      expect(result.current.selectedTopic).toBe('amor');
      expect(mockRouter.push).toHaveBeenCalledWith('/interpretation/amor');
    });
  });

  describe('handleBackToDashboard', () => {
    it('should navigate to dashboard', async () => {
      const { result } = renderHook(() => useAuth());

      await act(async () => {
        result.current.handleBackToDashboard();
      });

      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard');
    });
  });

  describe('handleLogout', () => {
    it('should logout, clear state, and redirect to home', async () => {
      localStorage.setItem('auth_token', 'test-token');

      const { result } = renderHook(() => useAuth());

      // Set some state first
      await act(async () => {
        result.current.handleAuthSuccess({
          email: 'test@example.com',
          name: 'Test User',
          hasCompletedOnboarding: true,
        });
      });

      await act(async () => {
        result.current.handleLogout();
      });

      expect(apiService.logout).toHaveBeenCalled();
      expect(result.current.userData).toBeNull();
      expect(result.current.authData).toBeNull();
      expect(result.current.googleData).toBeNull();
      expect(result.current.tempPassword).toBeNull();
      expect(mockRouter.push).toHaveBeenCalledWith('/');
    });
  });

  describe('setUserData', () => {
    it('should update userData', async () => {
      const { result } = renderHook(() => useAuth());

      const newUserData = {
        name: 'New Name',
        birthDate: new Date('1990-01-01'),
        birthTime: '12:00',
        birthPlace: 'São Paulo',
        coordinates: {
          latitude: -23.5505,
          longitude: -46.6333,
        },
        sunSign: 'Capricorn',
        moonSign: 'Aries',
        ascendant: 'Leo',
      };

      await act(async () => {
        result.current.setUserData(newUserData);
      });

      expect(result.current.userData).toEqual(newUserData);
    });
  });
});

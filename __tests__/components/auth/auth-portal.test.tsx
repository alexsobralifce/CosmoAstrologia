import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthPortal } from '@/components/auth-portal';
import { apiService } from '@/services/api';
import { renderWithProviders, mockApiResponse, mockApiError } from '../../utils/test-utils';

// Mock import.meta.env before importing AuthPortal
Object.defineProperty(globalThis, 'import', {
  value: {
    meta: {
      env: {
        VITE_GOOGLE_CLIENT_ID: 'test-google-client-id',
        DEV: false,
        PROD: true,
      },
    },
  },
  writable: true,
  configurable: true,
});

// Mock API service
jest.mock('@/services/api', () => ({
  apiService: {
    registerUser: jest.fn(),
    loginUser: jest.fn(),
    verifyEmail: jest.fn(),
    resendVerificationCode: jest.fn(),
    verifyGoogleToken: jest.fn(),
  },
}));

// Mock Google Identity Services
global.window.google = {
  accounts: {
    id: {
      initialize: jest.fn(),
      prompt: jest.fn(),
      renderButton: jest.fn(),
    },
  },
} as any;

// Mock toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

describe('AuthPortal Component', () => {
  const mockOnAuthSuccess = jest.fn();
  const mockOnNeedsBirthData = jest.fn();
  const mockOnGoogleNeedsOnboarding = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('should render in login mode initially', () => {
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      expect(screen.getByText(/entrar|login/i)).toBeInTheDocument();
      expect(screen.queryByLabelText(/nome completo|full name/i)).not.toBeInTheDocument();
    });

    it('should switch to signup mode when toggle is clicked', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      const toggleButton = screen.getByText(/criar conta|sign up/i);
      await user.click(toggleButton);

      await waitFor(() => {
        expect(screen.getByLabelText(/nome completo|full name/i)).toBeInTheDocument();
      });
    });
  });

  describe('Email Validation', () => {
    it('should show error for empty email', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      const emailInput = screen.getByLabelText(/e-mail|email/i);
      const submitButton = screen.getByRole('button', { name: /entrar|login/i });

      await user.clear(emailInput);
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/e-mail é obrigatório|email is required/i)).toBeInTheDocument();
      });
    });

    it('should show error for invalid email format', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      const emailInput = screen.getByLabelText(/e-mail|email/i);
      await user.type(emailInput, 'invalid-email');

      const submitButton = screen.getByRole('button', { name: /entrar|login/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/e-mail inválido|invalid email/i)).toBeInTheDocument();
      });
    });

    it('should accept valid email', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      const emailInput = screen.getByLabelText(/e-mail|email/i);
      await user.type(emailInput, 'test@example.com');

      expect(emailInput).toHaveValue('test@example.com');
    });
  });

  describe('Password Validation', () => {
    it('should show error for empty password in login', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      const emailInput = screen.getByLabelText(/e-mail|email/i);
      const passwordInput = screen.getByLabelText(/senha|password/i);
      const submitButton = screen.getByRole('button', { name: /entrar|login/i });

      await user.type(emailInput, 'test@example.com');
      await user.clear(passwordInput);
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/senha é obrigatória|password is required/i)).toBeInTheDocument();
      });
    });

    it('should show error for password less than 6 characters in signup', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      // Switch to signup mode
      const toggleButton = screen.getByText(/criar conta|sign up/i);
      await user.click(toggleButton);

      await waitFor(async () => {
        const passwordInput = screen.getByLabelText(/senha|password/i);
        await user.type(passwordInput, '12345');
        const submitButton = screen.getByRole('button', { name: /criar conta|sign up/i });
        await user.click(submitButton);
      });

      await waitFor(() => {
        expect(screen.getByText(/mínimo de 6 caracteres|minimum 6 characters/i)).toBeInTheDocument();
      });
    });

    it('should show error when passwords do not match in signup', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      // Switch to signup mode
      const toggleButton = screen.getByText(/criar conta|sign up/i);
      await user.click(toggleButton);

      await waitFor(async () => {
        const passwordInput = screen.getByLabelText(/senha|password/i);
        const confirmPasswordInput = screen.getByLabelText(/confirmar senha|confirm password/i);
        const submitButton = screen.getByRole('button', { name: /criar conta|sign up/i });

        await user.type(passwordInput, 'password123');
        await user.type(confirmPasswordInput, 'password456');
        await user.click(submitButton);
      });

      await waitFor(() => {
        expect(screen.getByText(/senhas não coincidem|passwords do not match/i)).toBeInTheDocument();
      });
    });
  });

  describe('Login Flow', () => {
    it('should successfully login with valid credentials', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
      };

      (apiService.loginUser as jest.Mock).mockResolvedValue(mockResponse);

      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      const emailInput = screen.getByLabelText(/e-mail|email/i);
      const passwordInput = screen.getByLabelText(/senha|password/i);
      const submitButton = screen.getByRole('button', { name: /entrar|login/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      await waitFor(() => {
        expect(apiService.loginUser).toHaveBeenCalledWith('test@example.com', 'password123');
      });

      await waitFor(() => {
        expect(mockOnAuthSuccess).toHaveBeenCalled();
      });
    });

    it('should handle login error', async () => {
      const user = userEvent.setup();
      (apiService.loginUser as jest.Mock).mockRejectedValue(
        new Error('Invalid credentials')
      );

      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      const emailInput = screen.getByLabelText(/e-mail|email/i);
      const passwordInput = screen.getByLabelText(/senha|password/i);
      const submitButton = screen.getByRole('button', { name: /entrar|login/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(submitButton);

      await waitFor(() => {
        expect(apiService.loginUser).toHaveBeenCalled();
      });
    });
  });

  describe('Signup Flow', () => {
    it('should validate all required fields in signup', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      // Switch to signup mode
      const toggleButton = screen.getByText(/criar conta|sign up/i);
      await user.click(toggleButton);

      await waitFor(async () => {
        const submitButton = screen.getByRole('button', { name: /criar conta|sign up/i });
        await user.click(submitButton);
      });

      // Should show multiple validation errors
      await waitFor(() => {
        expect(screen.getByText(/nome é obrigatório|name is required/i)).toBeInTheDocument();
      });
    });

    it('should successfully register user with valid data', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        access_token: 'test-token',
        token_type: 'bearer',
      };

      (apiService.registerUser as jest.Mock).mockResolvedValue(mockResponse);

      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      // Switch to signup mode
      const toggleButton = screen.getByText(/criar conta|sign up/i);
      await user.click(toggleButton);

      await waitFor(async () => {
        const emailInput = screen.getByLabelText(/e-mail|email/i);
        const passwordInput = screen.getByLabelText(/senha|password/i);
        const confirmPasswordInput = screen.getByLabelText(/confirmar senha|confirm password/i);
        const nameInput = screen.getByLabelText(/nome completo|full name/i);
        const birthDateInput = screen.getByLabelText(/data de nascimento|birth date/i);
        const birthTimeInput = screen.getByLabelText(/hora de nascimento|birth time/i);
        const birthCityInput = screen.getByLabelText(/cidade de nascimento|birth city/i);
        const submitButton = screen.getByRole('button', { name: /criar conta|sign up/i });

        await user.type(emailInput, 'test@example.com');
        await user.type(passwordInput, 'password123');
        await user.type(confirmPasswordInput, 'password123');
        await user.type(nameInput, 'Test User');
        await user.type(birthDateInput, '01/01/1990');
        await user.type(birthTimeInput, '12:00');
        await user.type(birthCityInput, 'São Paulo');

        await user.click(submitButton);
      });

      await waitFor(() => {
        expect(apiService.registerUser).toHaveBeenCalled();
      });
    });

    it('should handle registration requiring email verification', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        message: 'Verification code sent',
        requires_verification: true,
        email: 'test@example.com',
      };

      (apiService.registerUser as jest.Mock).mockResolvedValue(mockResponse);

      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      // Switch to signup and fill form
      const toggleButton = screen.getByText(/criar conta|sign up/i);
      await user.click(toggleButton);

      await waitFor(async () => {
        const emailInput = screen.getByLabelText(/e-mail|email/i);
        const passwordInput = screen.getByLabelText(/senha|password/i);
        const confirmPasswordInput = screen.getByLabelText(/confirmar senha|confirm password/i);
        const nameInput = screen.getByLabelText(/nome completo|full name/i);
        const birthDateInput = screen.getByLabelText(/data de nascimento|birth date/i);
        const birthTimeInput = screen.getByLabelText(/hora de nascimento|birth time/i);
        const birthCityInput = screen.getByLabelText(/cidade de nascimento|birth city/i);
        const submitButton = screen.getByRole('button', { name: /criar conta|sign up/i });

        await user.type(emailInput, 'test@example.com');
        await user.type(passwordInput, 'password123');
        await user.type(confirmPasswordInput, 'password123');
        await user.type(nameInput, 'Test User');
        await user.type(birthDateInput, '01/01/1990');
        await user.type(birthTimeInput, '12:00');
        await user.type(birthCityInput, 'São Paulo');

        await user.click(submitButton);
      });

      await waitFor(() => {
        // Should show verification modal
        expect(screen.getByText(/código de verificação|verification code/i)).toBeInTheDocument();
      });
    });
  });

  describe('Birth Date and Time Formatting', () => {
    it('should format birth date as DD/MM/YYYY', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      // Switch to signup mode
      const toggleButton = screen.getByText(/criar conta|sign up/i);
      await user.click(toggleButton);

      await waitFor(async () => {
        const birthDateInput = screen.getByLabelText(/data de nascimento|birth date/i);
        await user.type(birthDateInput, '01011990');
        expect(birthDateInput).toHaveValue('01/01/1990');
      });
    });

    it('should format birth time as HH:MM', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      // Switch to signup mode
      const toggleButton = screen.getByText(/criar conta|sign up/i);
      await user.click(toggleButton);

      await waitFor(async () => {
        const birthTimeInput = screen.getByLabelText(/hora de nascimento|birth time/i);
        await user.type(birthTimeInput, '1230');
        expect(birthTimeInput).toHaveValue('12:30');
      });
    });

    it('should validate invalid birth date', async () => {
      const user = userEvent.setup();
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      // Switch to signup mode
      const toggleButton = screen.getByText(/criar conta|sign up/i);
      await user.click(toggleButton);

      await waitFor(async () => {
        const birthDateInput = screen.getByLabelText(/data de nascimento|birth date/i);
        await user.type(birthDateInput, '32/13/1990');
        await user.tab(); // Blur to trigger validation

        await waitFor(() => {
          expect(screen.getByText(/data inválida|invalid date/i)).toBeInTheDocument();
        });
      });
    });
  });

  describe('Google OAuth', () => {
    it('should render Google sign-in button', () => {
      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      expect(screen.getByText(/entrar com google|sign in with google/i)).toBeInTheDocument();
    });

    it('should handle Google OAuth callback', async () => {
      const mockGoogleResponse = {
        email: 'google@example.com',
        name: 'Google User',
        google_id: 'google-123',
      };

      (apiService.verifyGoogleToken as jest.Mock).mockResolvedValue(mockGoogleResponse);

      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      // Simulate Google OAuth callback
      const callback = (window as any).handleGoogleCredentialResponse;
      if (callback) {
        await callback({ credential: 'google-token' });
      }

      await waitFor(() => {
        expect(apiService.verifyGoogleToken).toHaveBeenCalled();
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading state during login', async () => {
      const user = userEvent.setup();
      (apiService.loginUser as jest.Mock).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ access_token: 'token' }), 100))
      );

      renderWithProviders(
        <AuthPortal
          onAuthSuccess={mockOnAuthSuccess}
          onNeedsBirthData={mockOnNeedsBirthData}
          onGoogleNeedsOnboarding={mockOnGoogleNeedsOnboarding}
        />
      );

      const emailInput = screen.getByLabelText(/e-mail|email/i);
      const passwordInput = screen.getByLabelText(/senha|password/i);
      const submitButton = screen.getByRole('button', { name: /entrar|login/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);

      // Should show loading indicator
      await waitFor(() => {
        expect(screen.getByText(/carregando|loading/i)).toBeInTheDocument();
      });
    });
  });
});

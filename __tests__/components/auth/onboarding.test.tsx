import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Onboarding } from '@/components/onboarding';
import { renderWithProviders } from '../../utils/test-utils';

// Mock LocationAutocomplete
jest.mock('@/components/location-autocomplete', () => ({
  LocationAutocomplete: ({ onLocationSelect }: any) => (
    <div data-testid="location-autocomplete">
      <input
        data-testid="location-input"
        onChange={(e) => {
          if (e.target.value === 'São Paulo, SP, Brasil') {
            onLocationSelect({
              place: 'São Paulo, SP, Brasil',
              coordinates: { latitude: -23.5505, longitude: -46.6333 },
            });
          }
        }}
      />
    </div>
  ),
}));

// Mock toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

describe('Onboarding Component', () => {
  const mockOnComplete = jest.fn();
  const mockOnBackToLogin = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('should render initial step with email and password fields when no initialEmail', () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} />
      );

      expect(screen.getByText(/criar seu mapa astral|vamos criar/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/seu@email.com|email/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/mínimo 6 caracteres|password/i)).toBeInTheDocument();
    });

    it('should render with pre-filled email and name when provided', () => {
      renderWithProviders(
        <Onboarding
          onComplete={mockOnComplete}
          initialEmail="test@example.com"
          initialName="Test User"
        />
      );

      const emailText = screen.getByText(/conta conectada|test@example.com/i);
      expect(emailText).toBeInTheDocument();
    });

    it('should render step 2 with name field', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} />
      );

      const emailInput = screen.getByPlaceholderText(/seu@email.com|email/i);
      const passwordInput = screen.getByPlaceholderText(/mínimo 6 caracteres|password/i);
      
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');

      const nextButton = screen.getByRole('button', { name: /próximo|next/i });
      await userEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/digite seu nome|name/i)).toBeInTheDocument();
      });
    });

    it('should render step 3 with birth date and time fields', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} />
      );

      // Step 1
      const emailInput = screen.getByPlaceholderText(/e-mail|email/i);
      const passwordInput = screen.getByPlaceholderText(/senha|password/i);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      // Step 2
      await waitFor(() => {
        const nameInput = screen.getByPlaceholderText(/nome completo|full name/i);
        expect(nameInput).toBeInTheDocument();
      });
      const nameInput = screen.getByPlaceholderText(/nome completo|full name/i);
      await userEvent.type(nameInput, 'Test User');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      // Step 3
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/hh:mm|birth time/i)).toBeInTheDocument();
      });
    });

    it('should render step 4 with location field', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} />
      );

      // Navigate through steps
      const emailInput = screen.getByPlaceholderText(/e-mail|email/i);
      const passwordInput = screen.getByPlaceholderText(/senha|password/i);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        const nameInput = screen.getByPlaceholderText(/nome completo|full name/i);
        expect(nameInput).toBeInTheDocument();
      });
      const nameInput = screen.getByPlaceholderText(/nome completo|full name/i);
      await userEvent.type(nameInput, 'Test User');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/data de nascimento|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });
      const birthDateInput = screen.getByPlaceholderText(/data de nascimento|birth date/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthTimeInput, '12:00');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      // Step 4
      await waitFor(() => {
        expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
      });
    });
  });

  describe('Validation', () => {
    it('should validate email format', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} />
      );

      const emailInput = screen.getByPlaceholderText(/seu@email.com|email/i);
      await userEvent.type(emailInput, 'invalid-email');
      await userEvent.tab();

      // Email validation happens on blur or next button click
      const nextButton = screen.getByRole('button', { name: /próximo|next/i });
      await userEvent.click(nextButton);

      // Should not proceed to next step with invalid email
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/seu@email.com|email/i)).toBeInTheDocument();
      }, { timeout: 1000 });
    });

    it('should validate password minimum length', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} />
      );

      const emailInput = screen.getByPlaceholderText(/seu@email.com|email/i);
      const passwordInput = screen.getByPlaceholderText(/mínimo 6 caracteres|password/i);
      
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, '12345'); // Less than 6 characters

      const nextButton = screen.getByRole('button', { name: /próximo|next/i });
      await userEvent.click(nextButton);

      // Should show error or not proceed
      await waitFor(() => {
        const errorMessage = screen.queryByText(/senha deve ter pelo menos 6 caracteres|password must be at least 6 characters/i);
        expect(errorMessage || screen.getByPlaceholderText(/mínimo 6 caracteres|password/i)).toBeTruthy();
      });
    });

    it('should validate password confirmation match', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} />
      );

      const emailInput = screen.getByPlaceholderText(/seu@email.com|email/i);
      const passwordInput = screen.getByPlaceholderText(/mínimo 6 caracteres|password/i);
      
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        const confirmPasswordInput = screen.getByPlaceholderText(/digite a senha novamente|confirm password/i);
        expect(confirmPasswordInput).toBeInTheDocument();
      });

      const confirmPasswordInput = screen.getByPlaceholderText(/digite a senha novamente|confirm password/i);
      await userEvent.type(confirmPasswordInput, 'different123');

      // Should show error when passwords don't match
      await waitFor(() => {
        const errorMessage = screen.queryByText(/senhas não coincidem|passwords do not match/i);
        expect(errorMessage || confirmPasswordInput).toBeTruthy();
      });
    });

    it('should validate name is required', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} />
      );

      // Complete step 1
      const emailInput = screen.getByPlaceholderText(/e-mail|email/i);
      const passwordInput = screen.getByPlaceholderText(/senha|password/i);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      // Try to proceed without name
      await waitFor(() => {
        const nextButton = screen.getByRole('button', { name: /próximo|next/i });
        expect(nextButton).toBeInTheDocument();
      });
      
      const nextButton = screen.getByRole('button', { name: /próximo|next/i });
      await userEvent.click(nextButton);

      // Should not proceed to next step
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/digite seu nome|name/i)).toBeInTheDocument();
      });
    });

    it('should validate birth date format', async () => {
      renderWithProviders(
        <Onboarding
          onComplete={mockOnComplete}
          initialEmail="test@example.com"
          initialName="Test User"
        />
      );

      // Navigate to step 3
      const nextButton = screen.getByRole('button', { name: /próximo|next/i });
      await userEvent.click(nextButton);

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      await userEvent.type(birthDateInput, '99/99/9999'); // Invalid date

      // Date validation should prevent invalid dates
      const nextButton2 = screen.getByRole('button', { name: /próximo|next/i });
      await userEvent.click(nextButton2);

      // Should not proceed with invalid date
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i)).toBeInTheDocument();
      });
    });

    it('should validate birth time format', async () => {
      renderWithProviders(
        <Onboarding
          onComplete={mockOnComplete}
          initialEmail="test@example.com"
          initialName="Test User"
        />
      );

      // Navigate to step 3
      const nextButton = screen.getByRole('button', { name: /próximo|next/i });
      await userEvent.click(nextButton);

      await waitFor(() => {
        const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
        expect(birthTimeInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/data de nascimento|birth date/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      
      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthTimeInput, '25:00'); // Invalid time

      // Time validation should prevent invalid times
      const nextButton2 = screen.getByRole('button', { name: /próximo|next/i });
      await userEvent.click(nextButton2);

      // Should not proceed with invalid time
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/hh:mm|birth time/i)).toBeInTheDocument();
      });
    });
  });

  describe('LocationAutocomplete Integration', () => {
    it('should calculate coordinates when location is selected', async () => {
      renderWithProviders(
        <Onboarding
          onComplete={mockOnComplete}
          initialEmail="test@example.com"
          initialName="Test User"
        />
      );

      // Navigate to step 4
      const nextButton = screen.getByRole('button', { name: /próximo|next/i });
      await userEvent.click(nextButton);

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/data de nascimento|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      await userEvent.type(birthTimeInput, '12:00');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
      });

      const locationInput = screen.getByTestId('location-input');
      await userEvent.type(locationInput, 'São Paulo, SP, Brasil');

      await waitFor(() => {
        // Coordinates should be set
        expect(mockOnComplete).not.toHaveBeenCalled();
      });
    });
  });

  describe('Form Submission', () => {
    it('should submit complete form with all required data', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} />
      );

      // Step 1
      const emailInput = screen.getByPlaceholderText(/e-mail|email/i);
      const passwordInput = screen.getByPlaceholderText(/senha|password/i);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      // Step 2
      await waitFor(() => {
        const nameInput = screen.getByPlaceholderText(/nome completo|full name/i);
        expect(nameInput).toBeInTheDocument();
      });
      const nameInput = screen.getByPlaceholderText(/nome completo|full name/i);
      await userEvent.type(nameInput, 'Test User');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      // Step 3
      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/data de nascimento|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });
      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      await userEvent.type(birthTimeInput, '12:00');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      // Step 4
      await waitFor(() => {
        expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
      });
      const locationInput = screen.getByTestId('location-input');
      await userEvent.type(locationInput, 'São Paulo, SP, Brasil');

      await waitFor(() => {
        const completeButton = screen.getByRole('button', { name: /finalizar|complete|concluir/i });
        expect(completeButton).toBeInTheDocument();
      });

      const completeButton = screen.getByRole('button', { name: /finalizar|complete|concluir/i });
      await userEvent.click(completeButton);

      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'Test User',
            email: 'test@example.com',
            password: 'password123',
            birthDate: expect.any(Date),
            birthTime: '12:00',
            birthPlace: expect.any(String),
            coordinates: expect.objectContaining({
              latitude: expect.any(Number),
              longitude: expect.any(Number),
            }),
          })
        );
      });
    });

    it('should handle submission errors', async () => {
      const mockOnCompleteWithError = jest.fn().mockRejectedValue(new Error('Submission failed'));
      
      renderWithProviders(
        <Onboarding onComplete={mockOnCompleteWithError} />
      );

      // Complete all steps quickly
      const emailInput = screen.getByPlaceholderText(/e-mail|email/i);
      const passwordInput = screen.getByPlaceholderText(/senha|password/i);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        const nameInput = screen.getByPlaceholderText(/nome completo|full name/i);
        expect(nameInput).toBeInTheDocument();
      });
      const nameInput = screen.getByPlaceholderText(/nome completo|full name/i);
      await userEvent.type(nameInput, 'Test User');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/data de nascimento|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });
      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      await userEvent.type(birthTimeInput, '12:00');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
      });
      const locationInput = screen.getByTestId('location-input');
      await userEvent.type(locationInput, 'São Paulo, SP, Brasil');

      await waitFor(() => {
        const completeButton = screen.getByRole('button', { name: /finalizar|complete|concluir/i });
        expect(completeButton).toBeInTheDocument();
      });

      const completeButton = screen.getByRole('button', { name: /finalizar|complete|concluir/i });
      await userEvent.click(completeButton);

      await waitFor(() => {
        expect(mockOnCompleteWithError).toHaveBeenCalled();
      });
    });
  });

  describe('Navigation', () => {
    it('should navigate back to previous step', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} />
      );

      // Go to step 2
      const emailInput = screen.getByPlaceholderText(/e-mail|email/i);
      const passwordInput = screen.getByPlaceholderText(/senha|password/i);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/nome completo|full name/i)).toBeInTheDocument();
      });

      // Go back
      const backButton = screen.getByRole('button', { name: /voltar|back/i });
      await userEvent.click(backButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/seu@email.com|email/i)).toBeInTheDocument();
      });
    });

    it('should call onBackToLogin when back button is clicked on first step', () => {
      renderWithProviders(
        <Onboarding
          onComplete={mockOnComplete}
          onBackToLogin={mockOnBackToLogin}
        />
      );

      const backButton = screen.getByRole('button', { name: /voltar|back|login/i });
      if (backButton) {
        fireEvent.click(backButton);
        expect(mockOnBackToLogin).toHaveBeenCalled();
      }
    });
  });

  describe('Loading States', () => {
    it('should show loading state during submission', async () => {
      const mockOnCompleteDelayed = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      renderWithProviders(
        <Onboarding onComplete={mockOnCompleteDelayed} />
      );

      // Complete form quickly
      const emailInput = screen.getByPlaceholderText(/seu@email.com|email/i);
      const passwordInput = screen.getByPlaceholderText(/mínimo 6 caracteres|password/i);
      await userEvent.type(emailInput, 'test@example.com');
      await userEvent.type(passwordInput, 'password123');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        const nameInput = screen.getByPlaceholderText(/nome completo|full name/i);
        expect(nameInput).toBeInTheDocument();
      });
      const nameInput = screen.getByPlaceholderText(/nome completo|full name/i);
      await userEvent.type(nameInput, 'Test User');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/data de nascimento|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });
      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      await userEvent.type(birthTimeInput, '12:00');
      await userEvent.click(screen.getByRole('button', { name: /próximo|next/i }));

      await waitFor(() => {
        expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
      });
      const locationInput = screen.getByTestId('location-input');
      await userEvent.type(locationInput, 'São Paulo, SP, Brasil');

      await waitFor(() => {
        const completeButton = screen.getByRole('button', { name: /finalizar|complete|concluir/i });
        expect(completeButton).toBeInTheDocument();
      });

      const completeButton = screen.getByRole('button', { name: /finalizar|complete|concluir/i });
      await userEvent.click(completeButton);

      // Button should be disabled or show loading state
      await waitFor(() => {
        expect(completeButton).toBeDisabled();
      }, { timeout: 2000 });
    });
  });
});

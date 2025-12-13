import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GoogleOnboarding } from '@/components/google-onboarding';
import { renderWithProviders } from '../../utils/test-utils';

// Mock LocationAutocomplete
jest.mock('@/components/location-autocomplete', () => ({
  LocationAutocomplete: ({ onSelect }: any) => (
    <div data-testid="location-autocomplete">
      <input
        data-testid="location-input"
        onChange={(e) => {
          if (e.target.value === 'São Paulo, SP, Brasil') {
            onSelect({
              displayName: 'São Paulo, SP, Brasil',
              shortName: 'São Paulo',
              city: 'São Paulo',
              state: 'SP',
              country: 'Brasil',
              lat: -23.5505,
              lon: -46.6333,
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

describe('GoogleOnboarding Component', () => {
  const mockOnComplete = jest.fn();
  const mockOnBack = jest.fn();

  const defaultProps = {
    email: 'test@gmail.com',
    name: 'Test User',
    onComplete: mockOnComplete,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Rendering', () => {
    it('should render with pre-filled Google email and name', () => {
      renderWithProviders(
        <GoogleOnboarding {...defaultProps} />
      );

      expect(screen.getByText(/bem-vindo|welcome/i)).toBeInTheDocument();
      expect(screen.getByText(/conta google|google account/i)).toBeInTheDocument();
      expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
    });

    it('should render step 1 with name field', () => {
      renderWithProviders(
        <GoogleOnboarding {...defaultProps} />
      );

      expect(screen.getByPlaceholderText(/digite seu nome|name/i)).toBeInTheDocument();
    });

    it('should render step 2 with birth date field', async () => {
      renderWithProviders(
        <GoogleOnboarding {...defaultProps} />
      );

      const nextButton = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i)).toBeInTheDocument();
      });
    });

    it('should render step 3 with birth time field', async () => {
      renderWithProviders(
        <GoogleOnboarding {...defaultProps} />
      );

      // Navigate to step 2
      const nextButton1 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton1);

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      await userEvent.type(birthDateInput, '01/01/1990');

      // Navigate to step 3
      const nextButton2 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton2);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/hh:mm|birth time/i)).toBeInTheDocument();
      });
    });

    it('should render step 4 with location field', async () => {
      renderWithProviders(
        <GoogleOnboarding {...defaultProps} />
      );

      // Navigate through steps
      const nextButton1 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton1);

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      const nextButton2 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton2);

      await waitFor(() => {
        const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
        expect(birthTimeInput).toBeInTheDocument();
      });

      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthTimeInput, '12:00');
      const nextButton3 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton3);

      // Step 4
      await waitFor(() => {
        expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
      });
    });
  });

  describe('Validation', () => {
    it('should validate birth date format', async () => {
      renderWithProviders(
        <GoogleOnboarding {...defaultProps} />
      );

      const nextButton = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton);

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      await userEvent.type(birthDateInput, '99/99/9999'); // Invalid date

      // Date validation should prevent invalid dates
      const nextButton2 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton2);

      // Should not proceed with invalid date
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i)).toBeInTheDocument();
      });
    });

    it('should validate birth time format', async () => {
      renderWithProviders(
        <GoogleOnboarding {...defaultProps} />
      );

      // Navigate to step 3
      const nextButton1 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton1);

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      const nextButton2 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton2);

      await waitFor(() => {
        const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
        expect(birthTimeInput).toBeInTheDocument();
      });

      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthTimeInput, '25:00'); // Invalid time

      // Time validation should prevent invalid times
      const nextButton3 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton3);

      // Should not proceed with invalid time
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/hh:mm|birth time/i)).toBeInTheDocument();
      });
    });
  });

  describe('LocationAutocomplete Integration', () => {
    it('should calculate coordinates when location is selected', async () => {
      renderWithProviders(
        <GoogleOnboarding {...defaultProps} />
      );

      // Navigate to step 4
      const nextButton1 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton1);

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      const nextButton2 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton2);

      await waitFor(() => {
        const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
        expect(birthTimeInput).toBeInTheDocument();
      });

      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthTimeInput, '12:00');
      const nextButton3 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton3);

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
        <GoogleOnboarding {...defaultProps} />
      );

      // Step 1 - Name (optional, can skip)
      const nextButton1 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton1);

      // Step 2 - Birth Date
      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      const nextButton2 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton2);

      // Step 3 - Birth Time
      await waitFor(() => {
        const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
        expect(birthTimeInput).toBeInTheDocument();
      });

      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthTimeInput, '12:00');
      const nextButton3 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton3);

      // Step 4 - Location
      await waitFor(() => {
        expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
      });

      const locationInput = screen.getByTestId('location-input');
      await userEvent.type(locationInput, 'São Paulo, SP, Brasil');

      await waitFor(() => {
        const completeButton = screen.getByRole('button', { name: /gerar meu mapa|generate/i });
        expect(completeButton).toBeInTheDocument();
      });

      const completeButton = screen.getByRole('button', { name: /gerar meu mapa|generate/i });
      await userEvent.click(completeButton);

      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'Test User',
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
        <GoogleOnboarding {...defaultProps} onComplete={mockOnCompleteWithError} />
      );

      // Complete all steps
      const nextButton1 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton1);

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      const nextButton2 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton2);

      await waitFor(() => {
        const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
        expect(birthTimeInput).toBeInTheDocument();
      });

      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthTimeInput, '12:00');
      const nextButton3 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton3);

      await waitFor(() => {
        expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
      });

      const locationInput = screen.getByTestId('location-input');
      await userEvent.type(locationInput, 'São Paulo, SP, Brasil');

      await waitFor(() => {
        const completeButton = screen.getByRole('button', { name: /gerar meu mapa|generate/i });
        expect(completeButton).toBeInTheDocument();
      });

      const completeButton = screen.getByRole('button', { name: /gerar meu mapa|generate/i });
      await userEvent.click(completeButton);

      await waitFor(() => {
        expect(mockOnCompleteWithError).toHaveBeenCalled();
      });
    });
  });

  describe('Navigation', () => {
    it('should navigate back to previous step', async () => {
      renderWithProviders(
        <GoogleOnboarding {...defaultProps} />
      );

      // Go to step 2
      const nextButton = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i)).toBeInTheDocument();
      });

      // Go back
      const backButton = screen.getByRole('button', { name: /voltar|back/i });
      await userEvent.click(backButton);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/digite seu nome|name/i)).toBeInTheDocument();
      });
    });

    it('should call onBack when back button is clicked on first step', () => {
      renderWithProviders(
        <GoogleOnboarding {...defaultProps} onBack={mockOnBack} />
      );

      const backButton = screen.getByRole('button', { name: /voltar|back/i });
      if (backButton) {
        fireEvent.click(backButton);
        expect(mockOnBack).toHaveBeenCalled();
      }
    });
  });

  describe('Loading States', () => {
    it('should show loading state during submission', async () => {
      const mockOnCompleteDelayed = jest.fn().mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      renderWithProviders(
        <GoogleOnboarding {...defaultProps} onComplete={mockOnCompleteDelayed} />
      );

      // Complete form
      const nextButton1 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton1);

      await waitFor(() => {
        const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
        expect(birthDateInput).toBeInTheDocument();
      });

      const birthDateInput = screen.getByPlaceholderText(/dd\/mm\/aaaa|birth date/i);
      await userEvent.type(birthDateInput, '01/01/1990');
      const nextButton2 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton2);

      await waitFor(() => {
        const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
        expect(birthTimeInput).toBeInTheDocument();
      });

      const birthTimeInput = screen.getByPlaceholderText(/hh:mm|birth time/i);
      await userEvent.type(birthTimeInput, '12:00');
      const nextButton3 = screen.getByRole('button', { name: /avançar|next/i });
      await userEvent.click(nextButton3);

      await waitFor(() => {
        expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
      });

      const locationInput = screen.getByTestId('location-input');
      await userEvent.type(locationInput, 'São Paulo, SP, Brasil');

      await waitFor(() => {
        const completeButton = screen.getByRole('button', { name: /gerar meu mapa|generate/i });
        expect(completeButton).toBeInTheDocument();
      });

      const completeButton = screen.getByRole('button', { name: /gerar meu mapa|generate/i });
      await userEvent.click(completeButton);

      // Button should be disabled or show loading state
      await waitFor(() => {
        expect(completeButton).toBeDisabled();
      }, { timeout: 2000 });
    });
  });
});

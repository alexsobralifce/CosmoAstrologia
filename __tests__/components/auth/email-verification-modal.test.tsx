import React from 'react';
import { act, render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EmailVerificationModal } from '@/components/email-verification-modal';
import { renderWithProviders } from '../../utils/test-utils';

// Com fake timers o userEvent precisa avançar o relógio falso, senão trava
// O contador reagenda um setTimeout a cada render, então o relógio avança de 1 em 1 segundo
const avancar = (segundos: number) => {
  for (let i = 0; i < segundos; i++) {
    act(() => {
      jest.advanceTimersByTime(1000);
    });
  }
};
const botaoReenviar = () => screen.getByRole('button', { name: /reenviar|resend/i });

const user = () => userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

// Mock toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

describe('EmailVerificationModal Component', () => {
  const mockOnVerify = jest.fn();
  const mockOnResend = jest.fn();
  const mockOnCancel = jest.fn();

  const defaultProps = {
    isOpen: true,
    email: 'test@example.com',
    onVerify: mockOnVerify,
    onResend: mockOnResend,
    onCancel: mockOnCancel,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Rendering', () => {
    it('should render modal when isOpen is true', () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      expect(screen.getByText(/verifique seu email|verify your email/i)).toBeInTheDocument();
      expect(screen.getByText(/test@example.com/i)).toBeInTheDocument();
    });

    it('should not render modal when isOpen is false', () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} isOpen={false} />
      );

      expect(screen.queryByText(/verifique seu email|verify your email/i)).not.toBeInTheDocument();
    });

    it('should render code input field', () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const codeInput = screen.getByPlaceholderText(/000000/);
      expect(codeInput).toBeInTheDocument();
    });

    it('should render verify button', () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const verifyButton = screen.getByRole('button', { name: /verificar|verify/i });
      expect(verifyButton).toBeInTheDocument();
    });

    it('should render resend button', () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      // O botão de reenvio só aparece quando o contador chega a zero
      avancar(60);
      expect(botaoReenviar()).toBeInTheDocument();
    });

    it('should render cancel button', () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const cancelButton = screen.getByRole('button', { name: /cancelar|cancel/i });
      expect(cancelButton).toBeInTheDocument();
    });
  });

  describe('Code Input', () => {
    it('should accept only numeric input', async () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const codeInput = screen.getByPlaceholderText(/000000/) as HTMLInputElement;
      await user().type(codeInput, 'abc123');

      // Should only contain numbers
      expect(codeInput.value).toBe('123');
    });

    it('should limit input to 6 digits', async () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const codeInput = screen.getByPlaceholderText(/000000/) as HTMLInputElement;
      await user().type(codeInput, '1234567890');

      // Should only contain first 6 digits
      expect(codeInput.value).toBe('123456');
    });

    it('should update code state when input changes', async () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const codeInput = screen.getByPlaceholderText(/000000/) as HTMLInputElement;
      await user().type(codeInput, '123456');

      expect(codeInput.value).toBe('123456');
    });
  });

  describe('Code Verification', () => {
    it('should call onVerify with code when verify button is clicked', async () => {
      mockOnVerify.mockResolvedValue(undefined);

      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const codeInput = screen.getByPlaceholderText(/000000/);
      await user().type(codeInput, '123456');

      const verifyButton = screen.getByRole('button', { name: /verificar|verify/i });
      await user().click(verifyButton);

      await waitFor(() => {
        expect(mockOnVerify).toHaveBeenCalledWith('123456');
      });
    });

    it('should show error for invalid code length', async () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const codeInput = screen.getByPlaceholderText(/000000/);
      await user().type(codeInput, '12345'); // Only 5 digits

      const verifyButton = screen.getByRole('button', { name: /verificar|verify/i });
      await user().click(verifyButton);

      // Should not call onVerify with incomplete code
      await waitFor(() => {
        expect(mockOnVerify).not.toHaveBeenCalled();
      });
    });

    it('should handle verification errors', async () => {
      mockOnVerify.mockRejectedValue(new Error('Invalid code'));

      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const codeInput = screen.getByPlaceholderText(/000000/);
      await user().type(codeInput, '123456');

      const verifyButton = screen.getByRole('button', { name: /verificar|verify/i });
      await user().click(verifyButton);

      await waitFor(() => {
        expect(mockOnVerify).toHaveBeenCalledWith('123456');
      });
    });

    it('should show loading state during verification', async () => {
      mockOnVerify.mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );

      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const codeInput = screen.getByPlaceholderText(/000000/);
      await user().type(codeInput, '123456');

      const verifyButton = screen.getByRole('button', { name: /verificar|verify/i });
      await user().click(verifyButton);

      // Button should be disabled during loading
      await waitFor(() => {
        expect(verifyButton).toBeDisabled();
      });
    });
  });

  describe('Resend Code', () => {
    it('should not offer resend while the countdown is running', () => {
      renderWithProviders(<EmailVerificationModal {...defaultProps} />);

      expect(screen.queryByRole('button', { name: /reenviar|resend/i })).not.toBeInTheDocument();
    });

    it('should call onResend when resend button is clicked', async () => {
      mockOnResend.mockResolvedValue(undefined);
      renderWithProviders(<EmailVerificationModal {...defaultProps} />);

      avancar(60);
      await user().click(botaoReenviar());

      await waitFor(() => expect(mockOnResend).toHaveBeenCalled());
    });

    it('should reset timer after resending', async () => {
      mockOnResend.mockResolvedValue(undefined);
      renderWithProviders(<EmailVerificationModal {...defaultProps} />);

      avancar(60);
      await user().click(botaoReenviar());

      await waitFor(() => expect(mockOnResend).toHaveBeenCalled());
      expect(await screen.findByText(/60s/)).toBeInTheDocument();
    });

    it('should clear code after resending', async () => {
      mockOnResend.mockResolvedValue(undefined);
      renderWithProviders(<EmailVerificationModal {...defaultProps} />);

      const codeInput = screen.getByPlaceholderText(/000000/) as HTMLInputElement;
      await user().type(codeInput, '123456');
      avancar(60);
      await user().click(botaoReenviar());

      await waitFor(() => expect(codeInput.value).toBe(''));
    });

    it('should handle resend errors', async () => {
      mockOnResend.mockRejectedValue(new Error('Resend failed'));
      renderWithProviders(<EmailVerificationModal {...defaultProps} />);

      avancar(60);
      await user().click(botaoReenviar());

      await waitFor(() => expect(mockOnResend).toHaveBeenCalled());
    });
  });

  describe('Modal Closing', () => {
    it('should call onCancel when cancel button is clicked', () => {
      renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const cancelButton = screen.getByRole('button', { name: /cancelar|cancel/i });
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
    });

    it('should reset code and timer when modal closes', () => {
      const { rerender } = renderWithProviders(
        <EmailVerificationModal {...defaultProps} />
      );

      const codeInput = screen.getByPlaceholderText(/000000/) as HTMLInputElement;
      fireEvent.change(codeInput, { target: { value: '123456' } });

      // Close modal
      rerender(
        <EmailVerificationModal {...defaultProps} isOpen={false} />
      );

      // Reopen modal
      rerender(
        <EmailVerificationModal {...defaultProps} isOpen={true} />
      );

      const newCodeInput = screen.getByPlaceholderText(/000000/) as HTMLInputElement;
      expect(newCodeInput.value).toBe('');
    });
  });

  describe('Timer', () => {
    it('should countdown from 60 seconds', () => {
      renderWithProviders(<EmailVerificationModal {...defaultProps} />);

      expect(screen.getByText(/60s/)).toBeInTheDocument();
      avancar(1);
      expect(screen.getByText(/59s/)).toBeInTheDocument();
    });

    it('should enable resend button when timer reaches 0', () => {
      renderWithProviders(<EmailVerificationModal {...defaultProps} />);

      avancar(60);
      expect(botaoReenviar()).not.toBeDisabled();
    });
  });
});

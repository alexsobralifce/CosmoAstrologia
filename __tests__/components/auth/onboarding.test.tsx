import React from 'react';
import { screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Onboarding } from '@/components/onboarding';
import { renderWithProviders } from '../../utils/test-utils';

// Mock LocationAutocomplete
jest.mock('@/components/location-autocomplete', () => ({
  LocationAutocomplete: ({ onChange, onSelect }: any) => (
    <div data-testid="location-autocomplete">
      <input
        data-testid="location-input"
        onChange={(e) => {
          onChange(e.target.value);
          if (e.target.value === 'São Paulo, SP, Brasil') {
            onSelect({ displayName: 'São Paulo, SP, Brasil', lat: -23.5505, lon: -46.6333 });
          }
        }}
      />
    </div>
  ),
}));

jest.mock('sonner', () => ({
  toast: { success: jest.fn(), error: jest.fn(), info: jest.fn() },
}));

// Fluxo real: 1) nome + e-mail + senha  2) data  3) hora  4) local
const avancar = () => screen.getByRole('button', { name: /avançar/i });
const submit = () => screen.getByRole('button', { name: /ver meu mapa astral|processando/i });
const horaInput = () => document.querySelector('input[type="time"]') as HTMLInputElement;

async function passo1(user: ReturnType<typeof userEvent.setup>, overrides: Partial<Record<'nome' | 'email' | 'senha' | 'confirma', string>> = {}) {
  const { nome = 'Test User', email = 'test@example.com', senha = 'password123', confirma = senha } = overrides;
  await user.type(screen.getByPlaceholderText('Digite seu nome'), nome);
  await user.type(screen.getByPlaceholderText('seu@email.com'), email);
  await user.type(screen.getByPlaceholderText('Mínimo 6 caracteres'), senha);
  await user.type(screen.getByPlaceholderText('Digite a senha novamente'), confirma);
}

async function passo2(user: ReturnType<typeof userEvent.setup>, data = '01/01/1990') {
  await user.type(screen.getByPlaceholderText('dd/mm/aaaa'), data);
}

function passo3(hora = '12:00') {
  fireEvent.change(horaInput(), { target: { value: hora } });
}

async function escolherLocal(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByTestId('location-input'), 'São Paulo, SP, Brasil');
}

/** Preenche tudo até o passo 4 (local). */
async function chegarAoPasso4(user: ReturnType<typeof userEvent.setup>) {
  await passo1(user);
  await user.click(avancar());
  await passo2(user);
  await user.click(avancar());
  passo3();
  await user.click(avancar());
  await screen.findByTestId('location-autocomplete');
}

describe('Onboarding Component', () => {
  const mockOnComplete = jest.fn();
  const mockOnBackToLogin = jest.fn();
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    user = userEvent.setup();
  });

  describe('Rendering', () => {
    it('renders step 1 with name, email and password fields when there is no initialEmail', () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);

      expect(screen.getByText(/vamos criar seu mapa astral/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Digite seu nome')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('seu@email.com')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Mínimo 6 caracteres')).toBeInTheDocument();
    });

    it('shows the connected account instead of the e-mail field when initialEmail is given', () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} initialEmail="test@example.com" initialName="Test User" />
      );

      expect(screen.getByText(/conta conectada/i)).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
      expect(screen.queryByPlaceholderText('seu@email.com')).not.toBeInTheDocument();
    });

    it('renders step 2 with the birth date field', async () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await passo1(user);
      await user.click(avancar());

      expect(await screen.findByPlaceholderText('dd/mm/aaaa')).toBeInTheDocument();
    });

    it('renders step 3 with the birth time field', async () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await passo1(user);
      await user.click(avancar());
      await passo2(user);
      await user.click(avancar());

      await waitFor(() => expect(horaInput()).toBeInTheDocument());
    });

    it('renders step 4 with the location field', async () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await chegarAoPasso4(user);

      expect(screen.getByTestId('location-autocomplete')).toBeInTheDocument();
    });
  });

  describe('Validation', () => {
    it('blocks "Avançar" when the e-mail is invalid', async () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await passo1(user, { email: 'invalid-email' });

      expect(avancar()).toBeDisabled();
    });

    it('blocks "Avançar" when the password has fewer than 6 characters', async () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await passo1(user, { senha: '12345' });

      expect(avancar()).toBeDisabled();
    });

    it('blocks "Avançar" when the password confirmation does not match', async () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await passo1(user, { confirma: 'different123' });

      expect(avancar()).toBeDisabled();
    });

    it('blocks "Avançar" when the name is empty', async () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await passo1(user, { nome: ' ' });

      expect(avancar()).toBeDisabled();
    });

    it('rejects an invalid birth date', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} initialEmail="test@example.com" initialName="Test User" />
      );
      await user.click(avancar());
      await passo2(user, '99/99/9999');

      expect(screen.getByText(/digite uma data válida/i)).toBeInTheDocument();
      expect(avancar()).toBeDisabled();
    });

    it('blocks "Avançar" on step 3 until a birth time is filled', async () => {
      renderWithProviders(
        <Onboarding onComplete={mockOnComplete} initialEmail="test@example.com" initialName="Test User" />
      );
      await user.click(avancar());
      await passo2(user);
      await user.click(avancar());

      await waitFor(() => expect(horaInput()).toBeInTheDocument());
      expect(avancar()).toBeDisabled();
      passo3('12:00');
      expect(avancar()).not.toBeDisabled();
    });
  });

  describe('Form Submission', () => {
    it('only enables the final button after a location is selected', async () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await chegarAoPasso4(user);

      expect(submit()).toBeDisabled();
      await escolherLocal(user);
      await waitFor(() => expect(submit()).not.toBeDisabled());
      expect(mockOnComplete).not.toHaveBeenCalled();
    });

    it('submits the complete data', async () => {
      mockOnComplete.mockResolvedValue(undefined);
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await chegarAoPasso4(user);
      await escolherLocal(user);
      await waitFor(() => expect(submit()).not.toBeDisabled());
      await user.click(submit());

      await waitFor(() =>
        expect(mockOnComplete).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'Test User',
            email: 'test@example.com',
            password: 'password123',
            birthDate: expect.any(Date),
            birthTime: '12:00',
            birthPlace: 'São Paulo, SP, Brasil',
            coordinates: { latitude: -23.5505, longitude: -46.6333 },
          })
        )
      );
    });

    it('recovers from a submission error', async () => {
      mockOnComplete.mockRejectedValue(new Error('Submission failed'));
      jest.spyOn(console, 'error').mockImplementation(() => {});
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await chegarAoPasso4(user);
      await escolherLocal(user);
      await waitFor(() => expect(submit()).not.toBeDisabled());
      await user.click(submit());

      await waitFor(() => expect(mockOnComplete).toHaveBeenCalled());
      await waitFor(() => expect(submit()).not.toBeDisabled());
      expect(screen.queryByText(/processando/i)).not.toBeInTheDocument();
    });

    it('shows a loading state while submitting', async () => {
      let resolver: () => void = () => {};
      mockOnComplete.mockImplementation(() => new Promise<void>((resolve) => { resolver = resolve; }));
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await chegarAoPasso4(user);
      await escolherLocal(user);
      await waitFor(() => expect(submit()).not.toBeDisabled());
      await user.click(submit());

      expect(await screen.findByText(/processando/i)).toBeInTheDocument();
      resolver();
      await waitFor(() => expect(screen.queryByText(/processando/i)).not.toBeInTheDocument());
    });
  });

  describe('Navigation', () => {
    it('goes back to the previous step', async () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} />);
      await passo1(user);
      await user.click(avancar());
      await screen.findByPlaceholderText('dd/mm/aaaa');

      await user.click(screen.getByRole('button', { name: /^voltar$/i }));

      expect(await screen.findByPlaceholderText('Digite seu nome')).toBeInTheDocument();
    });

    it('calls onBackToLogin from the first step', async () => {
      renderWithProviders(<Onboarding onComplete={mockOnComplete} onBackToLogin={mockOnBackToLogin} />);

      await user.click(screen.getByRole('button', { name: /voltar ao login/i }));

      expect(mockOnBackToLogin).toHaveBeenCalled();
    });
  });
});

import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthPortal } from '@/components/auth-portal';
import { apiService } from '@/services/api';
import { renderWithProviders } from '../../utils/test-utils';

jest.mock('@/services/api', () => ({
  apiService: {
    registerUser: jest.fn(),
    loginUser: jest.fn(),
    getCurrentUser: jest.fn(),
    getUserBirthChart: jest.fn(),
    verifyEmail: jest.fn(),
    resendVerificationCode: jest.fn(),
    verifyGoogleToken: jest.fn(),
  },
}));

jest.mock('sonner', () => ({
  toast: { success: jest.fn(), error: jest.fn(), info: jest.fn() },
}));

// Autocomplete real faz chamadas de geocodificação; o mock devolve uma seleção fixa
jest.mock('@/components/location-autocomplete', () => ({
  LocationAutocomplete: ({ onChange, onSelect, error }: any) => (
    <div>
      <input
        data-testid="city-input"
        onChange={(e) => {
          onChange(e.target.value);
          if (e.target.value === 'São Paulo') {
            onSelect({ displayName: 'São Paulo, SP, Brasil', shortName: 'São Paulo, SP', lat: -23.55, lon: -46.63 });
          }
        }}
      />
      {error && <span>{error}</span>}
    </div>
  ),
}));

const api = apiService as jest.Mocked<typeof apiService>;

// Rótulos reais: "Endereço de E-mail", "Senha", "Confirmar Senha", "Nome Completo", etc.
const campo = (nome: RegExp) => screen.getByLabelText(nome);
const botaoEntrar = () => screen.getByRole('button', { name: /^entrar$/i });
const botaoCadastrar = () => screen.getByRole('button', { name: /^cadastrar$/i });

describe('AuthPortal Component', () => {
  const onAuthSuccess = jest.fn();
  const onNeedsBirthData = jest.fn();
  const onGoogleNeedsOnboarding = jest.fn();
  let user: ReturnType<typeof userEvent.setup>;

  const renderPortal = () =>
    renderWithProviders(
      <AuthPortal
        onAuthSuccess={onAuthSuccess}
        onNeedsBirthData={onNeedsBirthData}
        onGoogleNeedsOnboarding={onGoogleNeedsOnboarding}
      />
    );

  const irParaCadastro = async () => {
    renderPortal();
    await user.click(botaoCadastrar());
    await screen.findByLabelText(/nome completo/i);
  };

  const preencherCadastro = async (overrides: { senha?: string; confirma?: string } = {}) => {
    const { senha = 'password123', confirma = senha } = overrides;
    await user.type(campo(/nome completo/i), 'Maria Teste');
    await user.type(campo(/data de nascimento/i), '15011990');
    await user.type(campo(/hora de nascimento/i), '1430');
    await user.type(screen.getByTestId('city-input'), 'São Paulo');
    await user.type(campo(/endereço de e-mail/i), 'maria@example.com');
    await user.type(campo(/^senha$/i), senha);
    await user.type(campo(/confirmar senha/i), confirma);
  };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    user = userEvent.setup();
  });

  describe('Rendering', () => {
    it('renders in login mode initially', () => {
      renderPortal();

      expect(botaoEntrar()).toBeInTheDocument();
      expect(screen.queryByLabelText(/nome completo/i)).not.toBeInTheDocument();
    });

    it('switches to signup mode', async () => {
      await irParaCadastro();

      expect(screen.getByLabelText(/nome completo/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirmar senha/i)).toBeInTheDocument();
    });
  });

  describe('Login validation', () => {
    it('keeps the submit button disabled while e-mail or password is empty', async () => {
      renderPortal();
      expect(botaoEntrar()).toBeDisabled();

      await user.type(campo(/endereço de e-mail/i), 'maria@example.com');
      expect(botaoEntrar()).toBeDisabled();

      await user.type(campo(/^senha$/i), 'password123');
      expect(botaoEntrar()).not.toBeDisabled();
    });

    it('shows an error for an invalid e-mail and does not call the API', async () => {
      renderPortal();
      await user.type(campo(/endereço de e-mail/i), 'invalid-email');
      await user.type(campo(/^senha$/i), 'password123');
      await user.click(botaoEntrar());

      expect(await screen.findByText(/e-mail inválido/i)).toBeInTheDocument();
      expect(api.loginUser).not.toHaveBeenCalled();
    });
  });

  describe('Login flow', () => {
    it('logs in and calls onAuthSuccess when the user has a birth chart', async () => {
      api.loginUser.mockResolvedValue({ access_token: 't', token_type: 'bearer' } as any);
      api.getCurrentUser.mockResolvedValue({ name: 'Maria' } as any);
      api.getUserBirthChart.mockResolvedValue({ sun_sign: 'Capricórnio' } as any);

      renderPortal();
      await user.type(campo(/endereço de e-mail/i), 'maria@example.com');
      await user.type(campo(/^senha$/i), 'password123');
      await user.click(botaoEntrar());

      await waitFor(() => expect(api.loginUser).toHaveBeenCalledWith('maria@example.com', 'password123'));
      await waitFor(
        () => expect(onAuthSuccess).toHaveBeenCalledWith(
          expect.objectContaining({ email: 'maria@example.com', hasCompletedOnboarding: true })
        ),
        { timeout: 3000 }
      );
    });

    it('asks for birth data when the user has no birth chart yet', async () => {
      api.loginUser.mockResolvedValue({ access_token: 't', token_type: 'bearer' } as any);
      api.getCurrentUser.mockResolvedValue({ name: 'Maria' } as any);
      api.getUserBirthChart.mockResolvedValue(null as any);

      renderPortal();
      await user.type(campo(/endereço de e-mail/i), 'maria@example.com');
      await user.type(campo(/^senha$/i), 'password123');
      await user.click(botaoEntrar());

      await waitFor(() => expect(onNeedsBirthData).toHaveBeenCalledWith('maria@example.com', 'Maria'), { timeout: 3000 });
      expect(onAuthSuccess).not.toHaveBeenCalled();
    });

    it('shows the generic credentials error without revealing which field is wrong', async () => {
      api.loginUser.mockRejectedValue(new Error('E-mail ou senha incorretos.'));
      const { toast } = jest.requireMock('sonner');

      renderPortal();
      await user.type(campo(/endereço de e-mail/i), 'maria@example.com');
      await user.type(campo(/^senha$/i), 'errada123');
      await user.click(botaoEntrar());

      await waitFor(() =>
        expect(toast.error).toHaveBeenCalledWith(expect.stringMatching(/e-mail ou senha incorretos/i), expect.anything())
      );
      expect(onAuthSuccess).not.toHaveBeenCalled();
    });

    it('replaces the form with the loader while the login is in flight', async () => {
      api.loginUser.mockImplementation(() => new Promise(() => {}));

      renderPortal();
      await user.type(campo(/endereço de e-mail/i), 'maria@example.com');
      await user.type(campo(/^senha$/i), 'password123');
      await user.click(botaoEntrar());

      await waitFor(() => expect(screen.queryByLabelText(/endereço de e-mail/i)).not.toBeInTheDocument());
    });
  });

  describe('Signup', () => {
    it('keeps the submit button disabled until every field is filled', async () => {
      await irParaCadastro();
      expect(botaoCadastrar()).toBeDisabled();

      await preencherCadastro();
      expect(botaoCadastrar()).not.toBeDisabled();
    });

    it('rejects a password shorter than 6 characters', async () => {
      await irParaCadastro();
      await preencherCadastro({ senha: '12345' });
      await user.click(botaoCadastrar());

      expect(await screen.findByText(/mínimo de 6 caracteres/i)).toBeInTheDocument();
      expect(api.registerUser).not.toHaveBeenCalled();
    });

    it('rejects mismatching passwords', async () => {
      await irParaCadastro();
      await preencherCadastro({ senha: 'password123', confirma: 'different123' });
      await user.click(botaoCadastrar());

      expect(await screen.findByText(/as senhas não coincidem/i)).toBeInTheDocument();
      expect(api.registerUser).not.toHaveBeenCalled();
    });

    it('registers and opens the e-mail verification modal', async () => {
      api.registerUser.mockResolvedValue({ message: 'ok', requires_verification: true, email: 'maria@example.com' } as any);

      await irParaCadastro();
      await preencherCadastro();
      await user.click(botaoCadastrar());

      await waitFor(() =>
        expect(api.registerUser).toHaveBeenCalledWith(
          expect.objectContaining({
            email: 'maria@example.com',
            name: 'Maria Teste',
            birth_data: expect.objectContaining({
              birth_time: '14:30',
              birth_place: 'São Paulo, SP',
              latitude: -23.55,
              longitude: -46.63,
            }),
          })
        )
      );
      expect(await screen.findByText(/verifique seu email/i)).toBeInTheDocument();
    });
  });

  describe('Birth date and time masks', () => {
    it('formats the birth date as DD/MM/AAAA', async () => {
      await irParaCadastro();
      await user.type(campo(/data de nascimento/i), '15011990');

      expect(campo(/data de nascimento/i)).toHaveValue('15/01/1990');
    });

    it('formats the birth time as HH:MM', async () => {
      await irParaCadastro();
      await user.type(campo(/hora de nascimento/i), '1430');

      expect(campo(/hora de nascimento/i)).toHaveValue('14:30');
    });

    it('flags an invalid birth date as soon as it is complete', async () => {
      await irParaCadastro();
      await user.type(campo(/data de nascimento/i), '99999999');

      expect(await screen.findByText(/data inválida/i)).toBeInTheDocument();
    });
  });

  describe('Google', () => {
    it('renders the Google sign-in button', () => {
      renderPortal();

      // Com client id configurado o Google Identity Services desenha o botão dentro do contêiner;
      // sem client id aparece o botão próprio "Google".
      expect(document.querySelector('.login-google-button-container, .login-google-button')).toBeInTheDocument();
    });
  });
});

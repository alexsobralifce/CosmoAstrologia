import React, { useState, useCallback, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import { AstroCard } from './astro-card';
import { UIIcons } from './ui-icons';
import { AuthLoader } from './auth-loader';
import { LocationAutocomplete, LocationSelection } from './location-autocomplete';
import { EmailVerificationModal } from './email-verification-modal';
import { useLanguage } from '../i18n';
import { toast } from 'sonner';
import { Chrome } from 'lucide-react';
import { apiService } from '../services/api';
import '../styles/login-page.css';
import '../styles/google-modal.css';

interface AuthPortalProps {
  onAuthSuccess: (userData: AuthUserData) => void;
  onNeedsBirthData: (email: string, name?: string, password?: string) => void;
  onGoogleNeedsOnboarding?: (email: string, name: string, googleId: string) => void;
}

export interface AuthUserData {
  email: string;
  name?: string;
  hasCompletedOnboarding: boolean;
}

type AuthMode = 'signup' | 'login';

export const AuthPortal = ({ onAuthSuccess, onNeedsBirthData, onGoogleNeedsOnboarding }: AuthPortalProps) => {
  const { t, language } = useLanguage();
  const [mode, setMode] = useState<AuthMode>('login'); // Começa no login
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [birthTime, setBirthTime] = useState('');
  const [birthCity, setBirthCity] = useState('');
  const [birthLocation, setBirthLocation] = useState<LocationSelection | null>(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{email?: string; password?: string; confirmPassword?: string; fullName?: string; birthDate?: string; birthTime?: string; birthCity?: string}>({});
  const [showVerificationModal, setShowVerificationModal] = useState(false);
  const [verificationEmail, setVerificationEmail] = useState('');

  // ===== FORMATAÇÃO DE DATA (DD/MM/AAAA) =====
  const formatBirthDate = useCallback((value: string) => {
    // Remove tudo que não é número
    let cleaned = value.replace(/\D/g, '');
    
    // Limita a 8 dígitos (DDMMAAAA)
    cleaned = cleaned.substring(0, 8);
    
    // Aplica a máscara DD/MM/AAAA
    if (cleaned.length >= 5) {
      return `${cleaned.substring(0, 2)}/${cleaned.substring(2, 4)}/${cleaned.substring(4)}`;
    } else if (cleaned.length >= 3) {
      return `${cleaned.substring(0, 2)}/${cleaned.substring(2)}`;
    } else if (cleaned.length >= 1) {
      return cleaned;
    }
    return '';
  }, []);

  const handleBirthDateChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatBirthDate(e.target.value);
    setBirthDate(formatted);
    
    // Validar data
    if (formatted.length === 10) {
      const [day, month, year] = formatted.split('/').map(Number);
      const date = new Date(year, month - 1, day);
      const isValid = date.getDate() === day && 
                     date.getMonth() === month - 1 && 
                     date.getFullYear() === year &&
                     year >= 1900 && year <= new Date().getFullYear();
      
      if (!isValid) {
        setErrors(prev => ({ ...prev, birthDate: language === 'pt' ? 'Data inválida' : 'Invalid date' }));
      } else {
        setErrors(prev => ({ ...prev, birthDate: undefined }));
      }
    } else {
      setErrors(prev => ({ ...prev, birthDate: undefined }));
    }
  }, [formatBirthDate, language]);

  // ===== FORMATAÇÃO DE HORA (HH:MM) =====
  const formatBirthTime = useCallback((value: string) => {
    // Remove tudo que não é número
    let cleaned = value.replace(/\D/g, '');
    
    // Limita a 4 dígitos (HHMM)
    cleaned = cleaned.substring(0, 4);
    
    // Aplica a máscara HH:MM
    if (cleaned.length >= 3) {
      return `${cleaned.substring(0, 2)}:${cleaned.substring(2)}`;
    } else if (cleaned.length >= 1) {
      return cleaned;
    }
    return '';
  }, []);

  const handleBirthTimeChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatBirthTime(e.target.value);
    setBirthTime(formatted);
    
    // Validar hora
    if (formatted.length === 5) {
      const [hours, minutes] = formatted.split(':').map(Number);
      const isValid = hours >= 0 && hours <= 23 && minutes >= 0 && minutes <= 59;
      
      if (!isValid) {
        setErrors(prev => ({ ...prev, birthTime: language === 'pt' ? 'Hora inválida' : 'Invalid time' }));
      } else {
        setErrors(prev => ({ ...prev, birthTime: undefined }));
      }
    } else {
      setErrors(prev => ({ ...prev, birthTime: undefined }));
    }
  }, [formatBirthTime, language]);

  // ===== HANDLER PARA SELEÇÃO DE CIDADE =====
  const handleLocationSelect = useCallback((selection: LocationSelection) => {
    setBirthLocation(selection);
    // Usar o nome curto (cidade, estado, país) em vez do nome completo
    setBirthCity(selection.shortName || selection.displayName);
    setErrors(prev => ({ ...prev, birthCity: undefined }));
  }, []);

  // Simulação de banco de dados de usuários
  const mockDatabase = [
    { email: 'joao@exemplo.com', password: '123456', hasCompletedOnboarding: true, name: 'João Silva' },
    { email: 'maria@exemplo.com', password: '123456', hasCompletedOnboarding: false, name: 'Maria Santos' },
  ];

  // ===== VALIDAÇÃO DE E-MAIL =====
  const validateEmail = useCallback((email: string): { valid: boolean; message?: string } => {
    if (!email.trim()) {
      return { valid: false, message: language === 'pt' ? 'E-mail é obrigatório' : 'Email is required' };
    }
    
    // Regex mais completa para validação de e-mail
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    
    if (!emailRegex.test(email)) {
      return { valid: false, message: language === 'pt' ? 'E-mail inválido. Ex: nome@dominio.com' : 'Invalid email. Ex: name@domain.com' };
    }
    
    // Verificar domínios comuns mal digitados
    const commonMistakes: Record<string, string> = {
      'gmial.com': 'gmail.com',
      'gmal.com': 'gmail.com',
      'gamil.com': 'gmail.com',
      'hotnail.com': 'hotmail.com',
      'hotmal.com': 'hotmail.com',
      'outloo.com': 'outlook.com',
      'yahooo.com': 'yahoo.com',
    };
    
    const domain = email.split('@')[1]?.toLowerCase();
    if (domain && commonMistakes[domain]) {
      return { 
        valid: false, 
        message: language === 'pt' 
          ? `Você quis dizer @${commonMistakes[domain]}?` 
          : `Did you mean @${commonMistakes[domain]}?` 
      };
    }
    
    return { valid: true };
  }, [language]);

  // ===== VALIDAÇÃO DE SENHA =====
  const validatePassword = useCallback((password: string): { valid: boolean; message?: string } => {
    if (!password) {
      return { valid: false, message: language === 'pt' ? 'Senha é obrigatória' : 'Password is required' };
    }
    if (password.length < 6) {
      return { valid: false, message: language === 'pt' ? 'Mínimo de 6 caracteres' : 'Minimum 6 characters' };
    }
    return { valid: true };
  }, [language]);

  // ===== VALIDAÇÃO DE DATA =====
  const validateBirthDate = useCallback((date: string): { valid: boolean; message?: string } => {
    if (!date || date.length !== 10) {
      return { valid: false, message: language === 'pt' ? 'Data inválida (DD/MM/AAAA)' : 'Invalid date (DD/MM/YYYY)' };
    }
    
    const [day, month, year] = date.split('/').map(Number);
    const dateObj = new Date(year, month - 1, day);
    const isValid = dateObj.getDate() === day && 
                   dateObj.getMonth() === month - 1 && 
                   dateObj.getFullYear() === year &&
                   year >= 1900 && year <= new Date().getFullYear();
    
    if (!isValid) {
      return { valid: false, message: language === 'pt' ? 'Data inválida' : 'Invalid date' };
    }
    
    return { valid: true };
  }, [language]);

  // ===== VALIDAÇÃO DE HORA =====
  const validateBirthTime = useCallback((time: string): { valid: boolean; message?: string } => {
    if (!time || time.length !== 5) {
      return { valid: false, message: language === 'pt' ? 'Hora inválida (HH:MM)' : 'Invalid time (HH:MM)' };
    }
    
    const [hours, minutes] = time.split(':').map(Number);
    const isValid = hours >= 0 && hours <= 23 && minutes >= 0 && minutes <= 59;
    
    if (!isValid) {
      return { valid: false, message: language === 'pt' ? 'Hora inválida' : 'Invalid time' };
    }
    
    return { valid: true };
  }, [language]);

  const handleEmailSignup = async () => {
    setErrors({});
    const newErrors: typeof errors = {};
    
    // Validação de Nome
    if (!fullName.trim()) {
      newErrors.fullName = language === 'pt' ? 'Nome é obrigatório' : 'Name is required';
    }
    
    // Validação de Data de Nascimento
    const dateValidation = validateBirthDate(birthDate);
    if (!dateValidation.valid) {
      newErrors.birthDate = dateValidation.message;
    }
    
    // Validação de Hora de Nascimento
    const timeValidation = validateBirthTime(birthTime);
    if (!timeValidation.valid) {
      newErrors.birthTime = timeValidation.message;
    }
    
    // Validação de Cidade de Nascimento
    if (!birthCity.trim()) {
      newErrors.birthCity = language === 'pt' ? 'Selecione uma cidade' : 'Select a city';
    }
    
    // Validação de Localização (precisa ter selecionado uma cidade do autocomplete)
    if (!birthLocation) {
      newErrors.birthCity = language === 'pt' ? 'Selecione uma cidade da lista' : 'Select a city from the list';
    }
    
    // Validação de E-mail
    const emailValidation = validateEmail(email);
    if (!emailValidation.valid) {
      newErrors.email = emailValidation.message;
    }
    
    // Validação de Senha
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.valid) {
      newErrors.password = passwordValidation.message;
    }
    
    // Validação de Confirmação de Senha
    if (!confirmPassword) {
      newErrors.confirmPassword = language === 'pt' ? 'Confirme sua senha' : 'Confirm your password';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = language === 'pt' ? 'As senhas não coincidem' : 'Passwords do not match';
    }
    
    // Se houver erros, exibir e parar
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      const errorCount = Object.keys(newErrors).length;
      toast.error(
        language === 'pt' ? 'Verifique os campos' : 'Check the fields',
        {
          description: language === 'pt' 
            ? `${errorCount} campo(s) com erro(s)`
            : `${errorCount} field(s) with error(s)`,
          duration: 3000
        }
      );
      return;
    }

    setIsLoading(true);

    try {
      // Converter data DD/MM/AAAA para Date
      const [day, month, year] = birthDate.split('/').map(Number);
      const birthDateObj = new Date(year, month - 1, day);

      // Preparar dados para registro
      const registerData = {
        email,
        password,
        name: fullName,
        birth_data: {
          name: fullName,
          birth_date: birthDateObj.toISOString(),
          birth_time: birthTime,
          birth_place: birthCity,
          latitude: birthLocation!.lat,
          longitude: birthLocation!.lon,
        },
      };

      console.log('[AUTH] Registrando usuário diretamente...', { email, name: fullName });

      // Registrar no backend
      const response = await apiService.registerUser(registerData);

      // Verificar se precisa verificação de email
      if (response && 'requires_verification' in response && response.requires_verification) {
        setVerificationEmail(email);
        setShowVerificationModal(true);
        toast.success(
          language === 'pt' ? 'Email de verificação enviado!' : 'Verification email sent!',
          {
            description: language === 'pt' 
              ? 'Verifique seu email e digite o código' 
              : 'Check your email and enter the code',
            duration: 5000
          }
        );
        return; // Não continuar para o dashboard ainda
      }

      // Se não precisa verificação (caso antigo), continuar normalmente
      toast.success(
        language === 'pt' ? 'Cadastro realizado com sucesso!' : 'Registration successful!',
        {
          description: language === 'pt' 
            ? 'Bem-vindo ao CosmoAstral!' 
            : 'Welcome to CosmoAstral!',
          duration: 3000
        }
      );

      // Ir direto para o dashboard (já está autenticado após registro)
      onAuthSuccess({
        email,
        name: fullName,
        hasCompletedOnboarding: true
      });

    } catch (error: unknown) {
      console.error('[AUTH] Erro ao registrar:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setIsLoading(false);
      
      // Verificar se é erro de e-mail já existente
      if (errorMessage.includes('already registered') || errorMessage.includes('já cadastrado')) {
        toast.error(
          language === 'pt' ? 'Este e-mail já possui uma conta.' : 'This email already has an account.',
          {
            description: language === 'pt' ? 'Tente fazer login.' : 'Try logging in.',
            action: {
              label: t('auth', 'login'),
              onClick: () => setMode('login')
            },
            duration: 5000
          }
        );
      } else {
        toast.error(
          language === 'pt' ? 'Erro ao cadastrar' : 'Registration error',
          {
            description: errorMessage,
            duration: 5000
          }
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Função para verificar código de email
  const handleVerifyEmail = async (code: string) => {
    try {
      const response = await apiService.verifyEmail(verificationEmail, code);
      
      toast.success(
        language === 'pt' ? 'Email verificado com sucesso!' : 'Email verified successfully!',
        {
          description: language === 'pt' 
            ? 'Bem-vindo ao CosmoAstral!' 
            : 'Welcome to CosmoAstral!',
          duration: 3000
        }
      );

      setShowVerificationModal(false);
      
      // Buscar dados do usuário e ir para o dashboard
      const userData = await apiService.getCurrentUser();
      const birthChart = await apiService.getUserBirthChart();
      
      if (birthChart) {
        onAuthSuccess({
          email: verificationEmail,
          name: userData?.name,
          hasCompletedOnboarding: true
        });
      } else {
        onNeedsBirthData(verificationEmail, userData?.name);
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      toast.error(
        language === 'pt' ? 'Código inválido' : 'Invalid code',
        {
          description: errorMessage.includes('expirado') || errorMessage.includes('expired')
            ? (language === 'pt' ? 'Código expirado. Solicite um novo.' : 'Code expired. Request a new one.')
            : (language === 'pt' ? 'Verifique o código e tente novamente.' : 'Check the code and try again.'),
          duration: 5000
        }
      );
      throw error;
    }
  };

  // Função para reenviar código
  const handleResendCode = async () => {
    try {
      await apiService.resendVerificationCode(verificationEmail);
      toast.success(
        language === 'pt' ? 'Código reenviado!' : 'Code resent!',
        {
          description: language === 'pt'
            ? 'Verifique seu email novamente'
            : 'Check your email again',
        }
      );
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      toast.error(
        language === 'pt' ? 'Erro ao reenviar código' : 'Error resending code',
        {
          description: errorMessage,
        }
      );
      throw error;
    }
  };

  const handleLogin = async () => {
    setErrors({});
    const newErrors: typeof errors = {};
    
    // Validação de E-mail
    const emailValidation = validateEmail(email);
    if (!emailValidation.valid) {
      newErrors.email = emailValidation.message;
    }
    
    // Validação de Senha
    if (!password) {
      newErrors.password = language === 'pt' ? 'Digite sua senha' : 'Enter your password';
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);

    try {
      // Fazer login no backend
      await apiService.loginUser(email, password);
      
      // Buscar dados do usuário
      const userData = await apiService.getCurrentUser();
      const birthChart = await apiService.getUserBirthChart();
      
      setIsLoading(false);
      
      if (birthChart) {
        // Usuário tem mapa astral completo
        toast.success(
          language === 'pt' ? 'Bem-vindo de volta!' : 'Welcome back!', 
          {
            description: language === 'pt' 
              ? `Olá, ${userData?.name || email}! Acessando seu mapa astral...`
              : `Hi, ${userData?.name || email}! Accessing your birth chart...`,
            duration: 2000
          }
        );
        setTimeout(() => {
          onAuthSuccess({
            email: email,
            name: userData?.name,
            hasCompletedOnboarding: true
          });
        }, 500);
      } else {
        // Usuário existe mas não completou onboarding
        toast.info(
          language === 'pt' ? 'Complete seu cadastro' : 'Complete your registration', 
          {
            description: language === 'pt' 
              ? 'Precisamos de algumas informações para criar seu mapa astral.'
              : 'We need some information to create your birth chart.',
            duration: 3000
          }
        );
        setTimeout(() => {
          onNeedsBirthData(email, userData?.name);
        }, 500);
      }
    } catch (error: unknown) {
      setIsLoading(false);
      const errorMessage = error instanceof Error ? error.message : '';
      
      // Verificar se é erro de usuário não encontrado
      if (errorMessage.toLowerCase().includes('not found') || 
          errorMessage.toLowerCase().includes('não encontrado') ||
          errorMessage.toLowerCase().includes('user not found') ||
          errorMessage.toLowerCase().includes('usuário não encontrado')) {
        // Usuário não existe - mostrar mensagem informativa para cadastro
        toast.error(
          language === 'pt' ? 'E-mail não cadastrado' : 'Email not registered', 
          {
            description: language === 'pt' 
              ? 'Este e-mail não possui cadastro. Clique em "Criar conta" para se cadastrar.'
              : 'This email is not registered. Click "Create account" to sign up.',
            duration: 5000
          }
        );
        setErrors({ email: language === 'pt' ? 'E-mail não cadastrado no sistema' : 'Email not registered' });
      } else if (errorMessage.toLowerCase().includes('incorrect') || 
                 errorMessage.toLowerCase().includes('invalid') ||
                 errorMessage.toLowerCase().includes('senha') ||
                 errorMessage.toLowerCase().includes('password')) {
        // Senha incorreta
        toast.error(
          language === 'pt' ? 'Senha incorreta' : 'Incorrect password', 
          {
            description: language === 'pt' 
              ? 'A senha digitada está incorreta. Tente novamente.'
              : 'The password entered is incorrect. Please try again.',
        duration: 4000
          }
        );
        setErrors({ password: language === 'pt' ? 'Senha incorreta' : 'Incorrect password' });
      } else {
        // Erro genérico
        toast.error(
          language === 'pt' ? 'Erro ao fazer login' : 'Login error', 
          {
            description: errorMessage || (language === 'pt' ? 'Verifique suas credenciais.' : 'Check your credentials.'),
            duration: 4000
          }
        );
      }
    }
  };

  // Estado para modal do Google
  const [showGoogleModal, setShowGoogleModal] = useState(false);
  const [googleEmail, setGoogleEmail] = useState('');
  const [googleName, setGoogleName] = useState('');
  const isProcessingGoogleLogin = useRef(false);
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
  const googleButtonRef = useRef<HTMLDivElement>(null);

  // Função para lidar com o callback do Google OAuth
  const handleGoogleCallback = useCallback(async (response: any) => {
    console.log('[AUTH] Google OAuth response recebida');
    setIsLoading(true);
    
    try {
      const credential = response.credential;
      
      if (!credential) {
        throw new Error('Credencial do Google não recebida');
      }

      // Verificar token com o backend
      const googleUserData = await apiService.verifyGoogleToken(credential);
      
      const { email, name, google_id } = googleUserData;
      const finalName = name || email.split('@')[0];
      
      // Chamar API de autenticação Google com os dados reais
      const authResponse = await apiService.googleAuth({
        email: email.toLowerCase().trim(),
        name: finalName,
        google_id: google_id || credential,
      });

      setIsLoading(false);

      if (authResponse.needs_onboarding) {
        // Usuário precisa completar onboarding
        toast.info(
          language === 'pt' ? 'Conta Google conectada!' : 'Google account connected!',
          {
            description: authResponse.is_new_user
              ? (language === 'pt' ? 'Vamos configurar seu mapa astral.' : "Let's set up your birth chart.")
              : (language === 'pt' ? 'Complete seu cadastro para continuar.' : 'Complete your registration to continue.'),
            duration: 3000
          }
        );

        if (onGoogleNeedsOnboarding) {
          onGoogleNeedsOnboarding(email.toLowerCase().trim(), finalName, google_id || credential);
        } else {
          onNeedsBirthData(email.toLowerCase().trim(), finalName);
        }
      } else {
        // Usuário já tem mapa astral - ir direto para dashboard
        toast.success(t('auth', 'loginSuccess'), {
          description: language === 'pt'
            ? `Bem-vindo de volta, ${finalName}!`
            : `Welcome back, ${finalName}!`,
          duration: 2000
        });

        onAuthSuccess({
          email: email.toLowerCase().trim(),
          name: finalName,
          hasCompletedOnboarding: true
        });
      }
    } catch (error: any) {
      console.error('[AUTH] Erro na autenticação Google:', error);
      setIsLoading(false);
      
      let errorMessage = language === 'pt' ? 'Erro ao conectar com Google' : 'Error connecting with Google';
      let errorDescription = language === 'pt'
        ? 'Tente novamente ou use outro método de login.'
        : 'Try again or use another login method.';

      if (error?.message) {
        errorDescription = error.message;
      } else if (typeof error === 'string') {
        errorDescription = error;
      }

      toast.error(errorMessage, {
        description: errorDescription,
        duration: 5000
      });
    } finally {
      isProcessingGoogleLogin.current = false;
    }
  }, [language, t, onAuthSuccess, onGoogleNeedsOnboarding, onNeedsBirthData]);

  // Inicializar Google Identity Services e renderizar botão
  useEffect(() => {
    // Só inicializar se tiver client ID
    if (!googleClientId) {
      return;
    }

    let checkInterval: NodeJS.Timeout | null = null;
    let isInitialized = false;

    const initGoogleAuth = () => {
      // Evitar múltiplas inicializações
      if (isInitialized) {
        return;
      }

      // @ts-expect-error google is loaded from script
      if (window.google?.accounts?.id && googleClientId && googleButtonRef.current) {
        try {
          // Limpar conteúdo anterior do container
          if (googleButtonRef.current) {
            googleButtonRef.current.innerHTML = '';
          }

          // @ts-expect-error
          window.google.accounts.id.initialize({
            client_id: googleClientId,
            callback: handleGoogleCallback,
            auto_select: false,
            cancel_on_tap_outside: true,
          });

          // Calcular largura em pixels baseado no container
          // Usar 100% da largura do container, mas o CSS vai controlar o tamanho final
          let buttonWidth = 350; // Valor padrão em pixels
          if (googleButtonRef.current) {
            // Usar getBoundingClientRect para obter largura precisa
            const rect = googleButtonRef.current.getBoundingClientRect();
            const containerWidth = rect.width || googleButtonRef.current.offsetWidth || googleButtonRef.current.clientWidth;
            if (containerWidth > 0) {
              // Usar a largura total do container, o CSS vai garantir que fique centralizado
              buttonWidth = Math.floor(containerWidth);
            }
          }

          // Renderizar botão do Google
          // @ts-expect-error
          window.google.accounts.id.renderButton(
            googleButtonRef.current,
            {
              type: 'standard',
              theme: 'outline',
              size: 'large',
              text: 'signin_with',
              width: buttonWidth, // Largura em pixels baseada no container
            }
          );
          
          // Forçar realinhamento após renderização
          setTimeout(() => {
            if (googleButtonRef.current) {
              const iframe = googleButtonRef.current.querySelector('iframe');
              if (iframe) {
                // Garantir que o iframe ocupe 100% mas fique centralizado
                iframe.style.width = '100%';
                iframe.style.maxWidth = '100%';
                iframe.style.margin = '0 auto';
                iframe.style.display = 'block';
                iframe.style.position = 'relative';
                iframe.style.left = '0';
                iframe.style.right = '0';
              }
              
              // Ajustar qualquer div wrapper que o Google possa criar
              const wrapper = googleButtonRef.current.querySelector('div');
              if (wrapper && wrapper !== googleButtonRef.current) {
                wrapper.style.width = '100%';
                wrapper.style.maxWidth = '100%';
                wrapper.style.display = 'flex';
                wrapper.style.alignItems = 'center';
                wrapper.style.justifyContent = 'center';
                wrapper.style.margin = '0';
                wrapper.style.padding = '0';
            }
            }
          }, 100);
          
          isInitialized = true;
          console.log('[AUTH] Google Identity Services inicializado e botão renderizado');
          
          // Limpar intervalo se ainda estiver rodando
          if (checkInterval) {
            clearInterval(checkInterval);
            checkInterval = null;
          }
        } catch (error: any) {
          console.error('[AUTH] Erro ao inicializar Google Identity Services:', error);
          
          // Se for erro de origin não permitido, mostrar mensagem útil
          if (error?.message?.includes('origin') || error?.message?.includes('not allowed') || error?.message?.includes('origin_mismatch')) {
            const currentOrigin = window.location.origin;
            console.warn('[AUTH] Origin não configurado no Google Cloud Console.');
            console.warn(`[AUTH] URL atual: ${currentOrigin}`);
            console.warn(`[AUTH] Adicione esta URL nas "Authorized JavaScript origins" do seu Client ID no Google Cloud Console: ${currentOrigin}`);
            console.warn('[AUTH] Guia completo: backend/CONFIGURAR_GOOGLE_OAUTH_LOCAL.md');
          }
        }
      }
    };

    // Tentar inicializar imediatamente
    initGoogleAuth();

    // Se não estiver disponível, tentar novamente após um delay (com limite de tentativas)
    // @ts-expect-error
    if (!window.google?.accounts?.id && !isInitialized) {
      let attempts = 0;
      const maxAttempts = 100; // Máximo de 10 segundos (100 * 100ms)
      
      checkInterval = setInterval(() => {
        attempts++;
        // @ts-expect-error
        if (window.google?.accounts?.id && googleButtonRef.current && !isInitialized) {
          initGoogleAuth();
        } else if (attempts >= maxAttempts) {
          // Parar após máximo de tentativas
          if (checkInterval) {
            clearInterval(checkInterval);
            checkInterval = null;
          }
          console.warn('[AUTH] Google Identity Services não carregou após 10 segundos');
        }
      }, 100);
    }

    // Cleanup: remover botão e limpar intervalos quando componente desmontar
    return () => {
      if (checkInterval) {
        clearInterval(checkInterval);
      }
      if (googleButtonRef.current) {
        googleButtonRef.current.innerHTML = '';
      }
      isInitialized = false;
    };
  }, [googleClientId, handleGoogleCallback]);

  // Monitorar mudanças no estado do modal (debug)
  useEffect(() => {
    if (showGoogleModal) {
      console.log('[AUTH] Modal do Google foi aberto');
    }
  }, [showGoogleModal]);


  const handleGoogleLogin = async () => {
    // Prevenir múltiplos cliques usando ref
    if (isProcessingGoogleLogin.current) {
      console.log('[AUTH] Google login já está sendo processado, ignorando clique');
      return;
    }

    if (isLoading) {
      console.log('[AUTH] Google login já em andamento', { isLoading });
      return;
    }

    isProcessingGoogleLogin.current = true;
    console.log('[AUTH] Iniciando Google OAuth...');

    try {
      // @ts-expect-error google is loaded from script
      const google = window.google;

      if (!google?.accounts?.id) {
        // Fallback: usar modal simulado se Google Identity Services não estiver disponível
        console.log('[AUTH] Google Identity Services não disponível, usando modal simulado');
        setShowGoogleModal(true);
        isProcessingGoogleLogin.current = false;
        return;
      }

      if (!googleClientId) {
        toast.warning(
          language === 'pt' 
            ? 'Google OAuth não configurado' 
            : 'Google OAuth not configured',
          {
            description: language === 'pt'
              ? 'Usando modo de teste. Configure VITE_GOOGLE_CLIENT_ID para usar OAuth real.'
              : 'Using test mode. Configure VITE_GOOGLE_CLIENT_ID to use real OAuth.',
            duration: 5000
          }
        );
        setShowGoogleModal(true);
        isProcessingGoogleLogin.current = false;
        return;
      }

      // Usar o método prompt do Google Identity Services
      // @ts-expect-error
      google.accounts.id.prompt((notification: any) => {
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          // Se o prompt não foi exibido, usar renderButton ou One Tap
          console.log('[AUTH] Prompt não exibido, tentando One Tap');
          
          // Tentar renderizar botão ou usar método alternativo
          // Por enquanto, usar modal como fallback
          setShowGoogleModal(true);
          isProcessingGoogleLogin.current = false;
        } else if (notification.isDismissedMoment()) {
          console.log('[AUTH] Usuário dispensou o prompt');
          isProcessingGoogleLogin.current = false;
        }
      });
    } catch (error: any) {
      console.error('[AUTH] Erro ao iniciar Google OAuth:', error);
      toast.error(
        language === 'pt' ? 'Erro ao iniciar autenticação Google' : 'Error starting Google authentication',
        {
          description: error?.message || (language === 'pt'
            ? 'Tente novamente ou use outro método de login.'
            : 'Try again or use another login method.'),
        }
      );
      isProcessingGoogleLogin.current = false;
    }
  };

  const handleGoogleModalSubmit = async () => {
    if (!googleEmail || !googleEmail.includes('@')) {
      toast.error(language === 'pt' ? 'Digite um email válido' : 'Enter a valid email');
      return;
    }

    setShowGoogleModal(false);
    setIsLoading(true);
    
    try {
      console.log('[AUTH] Autenticando com Google (simulação):', googleEmail);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Gerar ID baseado no email (consistente)
      const mockGoogleId = `google_${btoa(googleEmail).replace(/[^a-zA-Z0-9]/g, '')}`;
      const finalName = googleName.trim() || googleEmail.split('@')[0];
      
      // Chamar API do backend para autenticação Google
      const response = await apiService.googleAuth({
        email: googleEmail.toLowerCase().trim(),
        name: finalName,
        google_id: mockGoogleId,
      });

    setIsLoading(false);

      if (response.needs_onboarding) {
        // Usuário precisa completar onboarding
      toast.info(
        language === 'pt' ? 'Conta Google conectada!' : 'Google account connected!', 
        {
            description: response.is_new_user 
              ? (language === 'pt' ? 'Vamos configurar seu mapa astral.' : "Let's set up your birth chart.")
              : (language === 'pt' ? 'Complete seu cadastro para continuar.' : 'Complete your registration to continue.'),
          duration: 3000
        }
      );
        
        if (onGoogleNeedsOnboarding) {
          onGoogleNeedsOnboarding(googleEmail.toLowerCase().trim(), finalName, mockGoogleId);
    } else {
          onNeedsBirthData(googleEmail.toLowerCase().trim(), finalName);
        }
      } else {
        // Usuário já tem mapa astral - ir direto para dashboard
      toast.success(t('auth', 'loginSuccess'), {
        description: language === 'pt' 
            ? `Bem-vindo de volta, ${finalName}!`
            : `Welcome back, ${finalName}!`,
        duration: 2000
      });
        
        onAuthSuccess({
          email: googleEmail.toLowerCase().trim(),
          name: finalName,
          hasCompletedOnboarding: true
        });
      }
      
      // Limpar campos do modal
      setGoogleEmail('');
      setGoogleName('');
      
    } catch (error: any) {
      console.error('[AUTH] Erro na autenticação Google:', error);
      setIsLoading(false);
      
      // Extrair mensagem de erro específica se disponível
      let errorMessage = language === 'pt' ? 'Erro ao conectar com Google' : 'Error connecting with Google';
      let errorDescription = language === 'pt' 
        ? 'Tente novamente ou use outro método de login.'
        : 'Try again or use another login method.';
      
      if (error?.message) {
        errorDescription = error.message;
      } else if (typeof error === 'string') {
        errorDescription = error;
      }
      
      toast.error(errorMessage, {
        description: errorDescription,
        duration: 5000
      });
    }
  };

  const handleForgotPassword = () => {
    if (!email || !validateEmail(email)) {
      toast.error(
        language === 'pt' ? 'Digite seu e-mail primeiro' : 'Enter your email first', 
        {
          description: language === 'pt' 
            ? 'Informe o e-mail para recuperar sua senha.'
            : 'Enter your email to recover your password.',
          duration: 3000
        }
      );
      return;
    }
    
    toast.success(
      language === 'pt' ? 'E-mail de recuperação enviado!' : 'Recovery email sent!', 
      {
        description: language === 'pt' 
          ? 'Verifique sua caixa de entrada.'
          : 'Check your inbox.',
        duration: 4000
      }
    );
  };

  if (isLoading) {
    return <AuthLoader />;
  }

  const passwordsMatch = password && confirmPassword && password === confirmPassword;

  // Textos traduzidos
  const texts = {
    title: language === 'pt' ? 'CosmoAstral' : 'Cosmic Insight',
    subtitle: language === 'pt' ? 'Desbloqueie os mistérios das suas estrelas' : 'Unlock the mysteries of your stars',
    createAccount: language === 'pt' ? 'Criar Conta' : 'Create Account',
    welcomeBack: language === 'pt' ? 'Bem-vindo de Volta' : 'Welcome Back',
    beginJourney: language === 'pt' ? 'Comece sua jornada espiritual hoje' : 'Begin your spiritual journey today',
    signInAccess: language === 'pt' ? 'Entre para acessar seu painel personalizado' : 'Sign in to access your personalized dashboard',
    fullName: language === 'pt' ? 'Nome Completo' : 'Full Name',
    birthDate: language === 'pt' ? 'dd/mm/aaaa' : 'mm/dd/yyyy',
    birthTime: '--:--',
    cityOfBirth: language === 'pt' ? 'Cidade de Nascimento' : 'City of Birth',
    emailAddress: language === 'pt' ? 'Endereço de E-mail' : 'Email Address',
    passwordLabel: language === 'pt' ? 'Senha' : 'Password',
    confirmPassword: language === 'pt' ? 'Confirmar Senha' : 'Confirm Password',
    minChars: language === 'pt' ? 'Mínimo 6 caracteres' : 'Minimum 6 characters',
    reenterPassword: language === 'pt' ? 'Digite novamente sua senha' : 'Re-enter your password',
    forgotPassword: language === 'pt' ? 'Esqueceu a senha?' : 'Forgot password?',
    signUp: language === 'pt' ? 'Cadastrar' : 'Sign Up',
    signIn: language === 'pt' ? 'Entrar' : 'Sign In',
    orContinueWith: language === 'pt' ? 'OU CONTINUE COM' : 'OR CONTINUE WITH',
    alreadyHaveAccount: language === 'pt' ? 'Já tem uma conta?' : 'Already have an account?',
    dontHaveAccount: language === 'pt' ? 'Não tem uma conta?' : "Don't have an account?",
    demoMode: language === 'pt' ? 'Modo Demo' : 'Demo Mode',
    tryLoggingIn: language === 'pt' ? 'Tente fazer login com uma dessas contas:' : 'Try logging in with any of these accounts:',
  };

  return (
    <>
      {/* Modal de Login com Google (Simulação) - Renderizado via Portal */}
      {showGoogleModal && typeof window !== 'undefined' && createPortal(
        <div 
          className="google-modal-overlay"
          onClick={(e) => {
            // Fechar modal ao clicar fora
            if (e.target === e.currentTarget) {
              setShowGoogleModal(false);
              setGoogleEmail('');
              setGoogleName('');
            }
          }}
        >
          <div className="google-modal-content">
            <div className="google-modal-header">
              <div className="google-modal-google-icon">
                <svg viewBox="0 0 24 24" style={{ width: '24px', height: '24px' }}>
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              </div>
              <h2 className="google-modal-title">
                {language === 'pt' ? 'Entrar com Google' : 'Sign in with Google'}
              </h2>
            </div>
            
            <p className="google-modal-description">
              {language === 'pt' 
                ? 'Digite seu email do Google para continuar. Se já tiver uma conta, você será logado automaticamente.'
                : 'Enter your Google email to continue. If you already have an account, you will be logged in automatically.'}
            </p>
            
            <div className="google-modal-form">
              <div className="google-modal-input-group">
                <label className="google-modal-label">
                  {language === 'pt' ? 'Email do Google' : 'Google Email'}
                </label>
                <input
                  type="email"
                  value={googleEmail}
                  onChange={(e) => setGoogleEmail(e.target.value)}
                  placeholder={language === 'pt' ? 'seu.email@gmail.com' : 'your.email@gmail.com'}
                  className="google-modal-input"
                  autoFocus
                />
              </div>
              
              <div className="google-modal-input-group">
                <label className="google-modal-label">
                  {language === 'pt' ? 'Nome (opcional)' : 'Name (optional)'}
                </label>
                <input
                  type="text"
                  value={googleName}
                  onChange={(e) => setGoogleName(e.target.value)}
                  placeholder={language === 'pt' ? 'Como quer ser chamado?' : 'What do you want to be called?'}
                  className="google-modal-input"
                />
              </div>
            </div>
            
            <div className="google-modal-buttons">
              <button
                type="button"
                className="google-modal-button google-modal-button-cancel"
                onClick={() => {
                  setShowGoogleModal(false);
                  setGoogleEmail('');
                  setGoogleName('');
                }}
              >
                {language === 'pt' ? 'Cancelar' : 'Cancel'}
              </button>
              <button
                type="button"
                className="google-modal-button google-modal-button-continue"
                onClick={handleGoogleModalSubmit}
                disabled={!googleEmail || !googleEmail.includes('@') || isLoading}
              >
                {language === 'pt' ? 'Continuar' : 'Continue'}
              </button>
            </div>
            
            <p className="google-modal-note">
              <span>🔒</span>
              <span>
                {language === 'pt' 
                  ? 'Modo de simulação - Em produção, você será redirecionado para o Google'
                  : 'Simulation mode - In production, you will be redirected to Google'}
              </span>
            </p>
          </div>
        </div>,
        document.body
      )}

    {/* Container principal - CSS puro */}
    <div className="login-page-container">
      {/* Container centralizado - Figma: width 512px, gap 32px */}
      <div className="login-content-wrapper">
        {/* Logo e Título - FORA do card como no Figma */}
        <div className="login-header">
          {/* Logo - Figma: 61.85x61.85px, background #6E1AE6, border-radius 16px */}
          <div className="login-logo-wrapper">
            <div className="login-logo">
              <UIIcons.Star className="text-white" size={35} />
            </div>
          </div>
          {/* Título - Figma: Tinos, 36px, bold, center, #160F24, line-height 1.11 */}
          <div className="login-title-wrapper">
            <h1 className="login-title">
              {texts.title}
            </h1>
            {/* Subtítulo - Figma: Inter, 18px, center, #635C70, line-height 1.625 */}
            <p className="login-subtitle">
              {texts.subtitle}
            </p>
          </div>
        </div>

        {/* Card Principal - CSS puro */}
        <div className="login-card-figma">
          <div className="login-card-content">
            {/* Título do Card - Figma: gap 8px */}
            <div className="login-card-header">
              {/* Título - Figma: Tinos, 24px, bold, center, #160F24, line-height 1.33 */}
              <h2 className="login-card-title">
                {mode === 'signup' ? texts.createAccount : texts.welcomeBack}
              </h2>
              {/* Subtítulo - Figma: Inter, 14px, center, #635C70, line-height 1.43 */}
              <p className="login-card-subtitle">
                {mode === 'signup' ? texts.beginJourney : texts.signInAccess}
              </p>
            </div>

            {/* Formulário - CSS puro */}
            <div className="login-form-container">
              {/* Nome Completo (apenas no signup) */}
              {mode === 'signup' && (
                <div className="login-form-field">
                  <AstroInput
                    label={texts.fullName}
                    type="text"
                    placeholder={texts.fullName}
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    error={errors.fullName}
                  />
                </div>
              )}

              {/* Data e Hora de Nascimento (apenas no signup) */}
              {mode === 'signup' && (
                <div className="login-form-field-grid">
                  <div className="login-form-field-item">
                    <AstroInput
                      label={language === 'pt' ? 'Data de Nascimento' : 'Birth Date'}
                      type="text"
                      placeholder={texts.birthDate}
                      value={birthDate}
                      onChange={handleBirthDateChange}
                      error={errors.birthDate}
                      maxLength={10}
                      inputMode="numeric"
                    />
                    {birthDate && birthDate.length === 10 && !errors.birthDate && (
                      <div className="login-validation-message">
                        <UIIcons.CheckCircle size={12} />
                        <span>{language === 'pt' ? 'Data válida' : 'Valid date'}</span>
                      </div>
                    )}
                  </div>
                  <div className="login-form-field-item">
                    <AstroInput
                      label={language === 'pt' ? 'Hora de Nascimento' : 'Birth Time'}
                      type="text"
                      placeholder={texts.birthTime}
                      value={birthTime}
                      onChange={handleBirthTimeChange}
                      error={errors.birthTime}
                      maxLength={5}
                      inputMode="numeric"
                    />
                    {birthTime && birthTime.length === 5 && !errors.birthTime && (
                      <div className="login-validation-message">
                        <UIIcons.CheckCircle size={12} />
                        <span>{language === 'pt' ? 'Hora válida' : 'Valid time'}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Cidade de Nascimento com Autocomplete (apenas no signup) */}
              {mode === 'signup' && (
                <div className="login-city-field">
                  <label className="login-city-label">
                    {texts.cityOfBirth}
                  </label>
                  <LocationAutocomplete
                    placeholder={language === 'pt' ? 'Digite o nome da cidade...' : 'Type the city name...'}
                    value={birthCity}
                    onChange={(value) => {
                      setBirthCity(value);
                      if (!value.trim()) {
                        setBirthLocation(null);
                      }
                    }}
                    onSelect={handleLocationSelect}
                    error={errors.birthCity}
                  />
                  {birthLocation && (
                    <div className="login-validation-message">
                      <UIIcons.MapPin size={12} />
                      <span>{language === 'pt' ? 'Localização selecionada' : 'Location selected'}</span>
                    </div>
                  )}
                </div>
              )}

              {/* E-mail */}
              <div className="login-form-field">
                <AstroInput
                  label={texts.emailAddress}
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  error={errors.email}
                />
              </div>

              {/* Senha */}
              <div className="login-form-field">
                <div className="login-password-wrapper">
                  <AstroInput
                    label={texts.passwordLabel}
                    type={showPassword ? 'text' : 'password'}
                    placeholder={mode === 'signup' ? texts.minChars : '••••••'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    error={errors.password}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="login-password-toggle"
                  >
                    {showPassword ? <UIIcons.EyeOff size={18} /> : <UIIcons.Eye size={18} />}
                  </button>
                </div>
              </div>

              {/* Confirmar Senha (apenas no signup) */}
              {mode === 'signup' && (
                <div className="login-form-field">
                  <div className="login-password-wrapper">
                    <AstroInput
                      label={texts.confirmPassword}
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder={texts.reenterPassword}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      error={errors.confirmPassword}
                      className={confirmPassword && (passwordsMatch ? 'border-green-500' : 'border-destructive')}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="login-password-toggle"
                    >
                      {showConfirmPassword ? <UIIcons.EyeOff size={18} /> : <UIIcons.Eye size={18} />}
                    </button>
                    {confirmPassword && passwordsMatch && (
                      <UIIcons.CheckCircle className="login-password-check" size={18} />
                    )}
                  </div>
                </div>
              )}

              {/* Esqueceu senha (apenas no login) */}
              {mode === 'login' && (
                <div className="login-forgot-password">
                  <button
                    onClick={handleForgotPassword}
                    className="login-forgot-password-button"
                  >
                    {texts.forgotPassword}
                  </button>
                </div>
              )}

              {/* Botão Principal - CSS puro */}
              <button
                onClick={mode === 'signup' ? handleEmailSignup : handleLogin}
                disabled={
                  isLoading ||
                  !email || 
                  !password || 
                  (mode === 'signup' && (!confirmPassword || !fullName || !birthDate || !birthTime || !birthCity))
                }
                className="login-button-figma"
              >
                {mode === 'signup' ? texts.signUp : texts.signIn}
                <UIIcons.ArrowRight size={16} />
              </button>

              {/* Divisor - CSS puro */}
              <div className="login-divider">
                <div className="login-divider-line"></div>
                <div className="login-divider-wrapper">
                  <span className="login-divider-text">
                    {texts.orContinueWith}
                  </span>
                </div>
              </div>

              {/* Login Social - CSS puro */}
              {/* Botão do Google - renderizado pelo Google Identity Services se disponível, senão usa botão customizado */}
              {googleClientId ? (
                <div ref={googleButtonRef} className="login-google-button-container" />
              ) : (
                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleGoogleLogin();
                  }}
                  disabled={isLoading || showGoogleModal}
                  className="login-google-button"
                >
                  <Chrome size={16} className="login-google-icon" />
                  <span>Google</span>
                </button>
              )}
            </div>

            {/* Footer com microcopy - CSS puro */}
            <div className="login-footer">
              {mode === 'signup' ? (
                <p className="login-footer-text">
                  {texts.alreadyHaveAccount}{' '}
                  <button 
                    onClick={() => setMode('login')} 
                    className="login-footer-link"
                  >
                    {texts.signIn}
                  </button>
                </p>
              ) : (
                <p className="login-footer-text">
                  {texts.dontHaveAccount}{' '}
                  <button 
                    onClick={() => setMode('signup')} 
                    className="login-footer-link"
                  >
                    {texts.signUp}
                  </button>
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Modal de Verificação de Email */}
      <EmailVerificationModal
        isOpen={showVerificationModal}
        email={verificationEmail}
        onVerify={handleVerifyEmail}
        onResend={handleResendCode}
        onCancel={() => {
          setShowVerificationModal(false);
          setVerificationEmail('');
        }}
      />
    </div>
    </>
  );
};

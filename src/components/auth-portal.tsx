import { useState, useCallback, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import { AstroCard } from './astro-card';
import { UIIcons } from './ui-icons';
import { AuthLoader } from './auth-loader';
import { LocationAutocomplete, LocationSelection } from './location-autocomplete';
import { useLanguage } from '../i18n';
import { toast } from 'sonner';
import { Chrome } from 'lucide-react';
import { apiService } from '../services/api';

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
      await apiService.registerUser(registerData);

      toast.success(
        language === 'pt' ? 'Cadastro realizado com sucesso!' : 'Registration successful!',
        {
          description: language === 'pt' 
            ? 'Bem-vindo ao Cosmos Astral!' 
            : 'Welcome to Cosmos Astral!',
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

    if (isLoading || showGoogleModal) {
      console.log('[AUTH] Google login já em andamento ou modal aberto', { isLoading, showGoogleModal });
      return;
    }

    isProcessingGoogleLogin.current = true;
    console.log('[AUTH] Iniciando Google login...');
    
    try {
      // Verificar se Google Identity Services está disponível
      // @ts-expect-error google is loaded from script
      const google = window.google;
      
      if (!google?.accounts?.id) {
        // Modo simulação: mostrar modal para inserir email do Google
        console.log('[AUTH] Abrindo modal do Google (modo simulação)');
        setShowGoogleModal(true);
      } else {
        // TODO: Implementar autenticação real com Google Identity Services
      }
    } finally {
      // Resetar após um pequeno delay para permitir que o estado seja atualizado
      setTimeout(() => {
        isProcessingGoogleLogin.current = false;
      }, 300);
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
      
    } catch (error) {
      console.error('[AUTH] Erro na autenticação Google:', error);
      setIsLoading(false);
      toast.error(
        language === 'pt' ? 'Erro ao conectar com Google' : 'Error connecting with Google',
        {
          description: language === 'pt' 
            ? 'Tente novamente ou use outro método de login.'
            : 'Try again or use another login method.',
          duration: 4000
        }
      );
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
    title: language === 'pt' ? 'Cosmos Astral' : 'Cosmic Insight',
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
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center" 
          style={{ zIndex: 9999 }}
          onClick={(e) => {
            // Fechar modal ao clicar fora
            if (e.target === e.currentTarget) {
              setShowGoogleModal(false);
              setGoogleEmail('');
              setGoogleName('');
            }
          }}
        >
          <div className="bg-card border border-border rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl animate-fadeIn">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-md">
                <svg viewBox="0 0 24 24" className="w-6 h-6">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-foreground">
                {language === 'pt' ? 'Entrar com Google' : 'Sign in with Google'}
              </h2>
      </div>
            
            <p className="text-sm text-muted-foreground text-center mb-6">
              {language === 'pt' 
                ? 'Digite seu email do Google para continuar. Se já tiver uma conta, você será logado automaticamente.'
                : 'Enter your Google email to continue. If you already have an account, you will be logged in automatically.'}
            </p>
            
            <div className="space-y-4">
              <AstroInput
                label={language === 'pt' ? 'Email do Google' : 'Google Email'}
                type="email"
                placeholder="seu.email@gmail.com"
                value={googleEmail}
                onChange={(e) => setGoogleEmail(e.target.value)}
                autoFocus
              />
              
              <AstroInput
                label={language === 'pt' ? 'Seu Nome (opcional)' : 'Your Name (optional)'}
                placeholder={language === 'pt' ? 'Como quer ser chamado?' : 'What should we call you?'}
                value={googleName}
                onChange={(e) => setGoogleName(e.target.value)}
              />
              
              <div className="flex gap-3 pt-2">
                <AstroButton 
                  variant="secondary" 
                  onClick={() => {
                    setShowGoogleModal(false);
                    setGoogleEmail('');
                    setGoogleName('');
                  }}
                  className="flex-1"
                >
                  {language === 'pt' ? 'Cancelar' : 'Cancel'}
                </AstroButton>
                <AstroButton 
                  variant="primary" 
                  onClick={handleGoogleModalSubmit}
                  disabled={!googleEmail || !googleEmail.includes('@')}
                  className="flex-1"
                >
                  {language === 'pt' ? 'Continuar' : 'Continue'}
                </AstroButton>
              </div>
            </div>
            
            <p className="text-xs text-muted-foreground text-center mt-4">
              {language === 'pt' 
                ? '🔒 Modo de simulação - Em produção, você será redirecionado para o Google'
                : '🔒 Simulation mode - In production, you will be redirected to Google'}
            </p>
          </div>
        </div>,
        document.body
      )}

    <div className="min-h-screen w-full flex items-center justify-center p-4 relative overflow-hidden bg-background">

      {/* Fundo Cósmico Animado */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-[#0F1535] to-background pointer-events-none">
        {/* Estrelas */}
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-accent rounded-full animate-twinkle"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 2}s`
            }}
          />
        ))}
        
        {/* Gradientes místicos */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Container centralizado */}
      <div className="w-full max-w-md mx-auto relative z-10 flex flex-col items-center justify-center space-y-8">
        {/* Logo e Título - FORA do card como no Figma */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-3xl bg-primary flex items-center justify-center shadow-lg">
              <UIIcons.Star className="text-foreground" size={40} />
            </div>
          </div>
          <div className="space-y-2">
            <h1 className="text-4xl font-bold text-foreground" style={{ fontFamily: 'var(--font-serif)' }}>
              {texts.title}
            </h1>
            <p className="text-muted-foreground">
              {texts.subtitle}
            </p>
          </div>
        </div>

        {/* Card Principal */}
        <AstroCard className="w-full shadow-xl border-border" style={{ borderRadius: '24px' }}>
          <div className="space-y-6 p-8">
            {/* Título do Card */}
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold text-foreground" style={{ fontFamily: 'var(--font-serif)' }}>
                {mode === 'signup' ? texts.createAccount : texts.welcomeBack}
              </h2>
              <p className="text-muted-foreground text-sm">
                {mode === 'signup' ? texts.beginJourney : texts.signInAccess}
              </p>
            </div>

            {/* Formulário */}
            <div className="space-y-4">
              {/* Nome Completo (apenas no signup) */}
              {mode === 'signup' && (
                <div>
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
                <div className="grid grid-cols-2 gap-4">
                  <div>
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
                      <div className="flex items-center gap-1 mt-1 text-xs text-green-500">
                        <UIIcons.CheckCircle size={12} />
                        <span>{language === 'pt' ? 'Data válida' : 'Valid date'}</span>
                      </div>
                    )}
                  </div>
                  <div>
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
                      <div className="flex items-center gap-1 mt-1 text-xs text-green-500">
                        <UIIcons.CheckCircle size={12} />
                        <span>{language === 'pt' ? 'Hora válida' : 'Valid time'}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Cidade de Nascimento com Autocomplete (apenas no signup) */}
              {mode === 'signup' && (
                <div className="mb-4 pb-2 relative" style={{ zIndex: 100 }}>
                  <label className="block text-sm font-medium text-foreground mb-2">
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
                    <div className="flex items-center gap-1 mt-1 text-xs text-green-500">
                      <UIIcons.MapPin size={12} />
                      <span>{language === 'pt' ? 'Localização selecionada' : 'Location selected'}</span>
                    </div>
                  )}
                </div>
              )}

              {/* E-mail */}
              <div>
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
              <div>
                <div className="relative">
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
                    className="absolute right-3 top-[38px] text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <UIIcons.EyeOff size={18} /> : <UIIcons.Eye size={18} />}
                  </button>
                </div>
              </div>

              {/* Confirmar Senha (apenas no signup) */}
              {mode === 'signup' && (
                <div>
                  <div className="relative">
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
                      className="absolute right-3 top-[38px] text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {showConfirmPassword ? <UIIcons.EyeOff size={18} /> : <UIIcons.Eye size={18} />}
                    </button>
                    {confirmPassword && passwordsMatch && (
                      <UIIcons.CheckCircle className="absolute right-10 top-[40px] text-green-500" size={18} />
                    )}
                  </div>
                </div>
              )}

              {/* Esqueceu senha (apenas no login) */}
              {mode === 'login' && (
                <div className="text-right">
                  <button
                    onClick={handleForgotPassword}
                    className="text-sm text-accent hover:text-accent/80 transition-colors"
                  >
                    {texts.forgotPassword}
                  </button>
                </div>
              )}

              {/* Botão Principal */}
              <AstroButton
                onClick={mode === 'signup' ? handleEmailSignup : handleLogin}
                className="w-full rounded-2xl font-semibold btn-figma-orange"
                disabled={
                  !email || 
                  !password || 
                  (mode === 'signup' && (!confirmPassword || !fullName || !birthDate || !birthTime || !birthCity))
                }
              >
                {mode === 'signup' ? texts.signUp : texts.signIn}
                <UIIcons.ArrowRight size={20} />
              </AstroButton>

              {/* Divisor */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-card text-muted-foreground uppercase tracking-wider">{texts.orContinueWith}</span>
                </div>
              </div>

              {/* Login Social */}
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log('[DEBUG] Google button clicked - calling handleGoogleLogin');
                  handleGoogleLogin();
                }}
                disabled={isLoading || showGoogleModal}
                className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white dark:bg-card hover:bg-gray-50 dark:hover:bg-card/80 text-gray-900 dark:text-foreground rounded-lg transition-all duration-200 shadow-md hover:shadow-lg border border-gray-200 dark:border-border cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Chrome size={20} className="text-[#4285F4]" />
                <span className="font-medium">Google</span>
              </button>
            </div>

            {/* Footer com microcopy - Estilo Figma */}
            <div className="text-center text-sm text-muted-foreground">
              {mode === 'signup' ? (
                <p>
                  {texts.alreadyHaveAccount}{' '}
                  <button onClick={() => setMode('login')} className="text-secondary font-medium hover:underline">
                    {texts.signIn}
                  </button>
                </p>
              ) : (
                <p>
                  {texts.dontHaveAccount}{' '}
                  <button onClick={() => setMode('signup')} className="text-secondary font-medium hover:underline">
                    {texts.signUp}
                  </button>
                </p>
              )}
            </div>
          </div>
        </AstroCard>
              </div>
            </div>
    </>
  );
};

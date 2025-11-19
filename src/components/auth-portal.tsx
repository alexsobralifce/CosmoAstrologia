import { useState } from 'react';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import { AstroCard } from './astro-card';
import { UIIcons } from './ui-icons';
import { AuthLoader } from './auth-loader';
import { toast } from 'sonner';
import { Chrome } from 'lucide-react';
import { apiService } from '../services/api';

interface AuthPortalProps {
  onAuthSuccess: (userData: AuthUserData) => void;
  onNeedsBirthData: (email: string, name?: string, password?: string) => void;
}

export interface AuthUserData {
  email: string;
  name?: string;
  hasCompletedOnboarding: boolean;
}

type AuthMode = 'signup' | 'login';

export const AuthPortal = ({ onAuthSuccess, onNeedsBirthData }: AuthPortalProps) => {
  const [mode, setMode] = useState<AuthMode>('signup');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{email?: string; password?: string; confirmPassword?: string}>({});

  // Simulação de banco de dados de usuários
  const mockDatabase = [
    { email: 'joao@exemplo.com', password: '123456', hasCompletedOnboarding: true, name: 'João Silva' },
    { email: 'maria@exemplo.com', password: '123456', hasCompletedOnboarding: false, name: 'Maria Santos' },
  ];

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePassword = (password: string) => {
    return password.length >= 6;
  };

  const handleEmailSignup = async () => {
    setErrors({});
    
    // Validações
    if (!validateEmail(email)) {
      setErrors({ email: 'E-mail inválido' });
      return;
    }
    
    if (!validatePassword(password)) {
      setErrors({ password: 'Senha deve ter no mínimo 6 caracteres' });
      return;
    }
    
    if (password !== confirmPassword) {
      setErrors({ confirmPassword: 'As senhas não coincidem' });
      return;
    }

    setIsLoading(true);

    // Simular verificação de e-mail existente
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const existingUser = mockDatabase.find(user => user.email === email);
    
    if (existingUser) {
      setIsLoading(false);
      toast.error('Este e-mail já possui um mapa astral.', {
        description: 'Tente fazer login.',
        action: {
          label: 'Ir para Login',
          onClick: () => setMode('login')
        },
        duration: 5000
      });
      return;
    }

    setIsLoading(false);
    // Novo usuário - precisa coletar dados de nascimento
    // Passar a senha também para que possa ser salva no registro
    onNeedsBirthData(email, undefined, password);
  };

  const handleLogin = async () => {
    setErrors({});
    
    if (!validateEmail(email)) {
      setErrors({ email: 'E-mail inválido' });
      return;
    }
    
    if (!password) {
      setErrors({ password: 'Digite sua senha' });
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
        toast.success('Bem-vindo de volta!', {
          description: `Olá, ${userData?.name || email}! Acessando seu mapa astral...`,
          duration: 2000
        });
        setTimeout(() => {
          onAuthSuccess({
            email: email,
            name: userData?.name,
            hasCompletedOnboarding: true
          });
        }, 500);
      } else {
        // Usuário existe mas não completou onboarding
        toast.info('Complete seu cadastro', {
          description: 'Precisamos de algumas informações para criar seu mapa astral.',
          duration: 3000
        });
        setTimeout(() => {
          onNeedsBirthData(email, userData?.name);
        }, 500);
      }
    } catch (error: unknown) {
      setIsLoading(false);
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'E-mail ou senha incorretos.';
      toast.error('Credenciais inválidas', {
        description: errorMessage,
        duration: 4000
      });
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    
    // Simular autenticação Google
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Simulação: 50% chance de ser novo usuário, 50% usuário existente
    const isNewUser = Math.random() > 0.5;
    
    const mockGoogleData = {
      email: 'usuario@gmail.com',
      name: 'Usuário Google'
    };

    setIsLoading(false);

    if (isNewUser) {
      // Novo usuário via Google - precisa coletar dados de nascimento
      toast.info('Conta Google conectada!', {
        description: 'Vamos configurar seu mapa astral.',
        duration: 3000
      });
      setTimeout(() => {
        onNeedsBirthData(mockGoogleData.email, mockGoogleData.name);
      }, 500);
    } else {
      // Usuário existente via Google - vai direto pro dashboard
      toast.success('Login realizado com sucesso!', {
        description: `Bem-vindo de volta, ${mockGoogleData.name}!`,
        duration: 2000
      });
      setTimeout(() => {
        onAuthSuccess({
          email: mockGoogleData.email,
          name: mockGoogleData.name,
          hasCompletedOnboarding: true
        });
      }, 500);
    }
  };

  const handleForgotPassword = () => {
    if (!email || !validateEmail(email)) {
      toast.error('Digite seu e-mail primeiro', {
        description: 'Informe o e-mail para recuperar sua senha.',
        duration: 3000
      });
      return;
    }
    
    toast.success('E-mail de recuperação enviado!', {
      description: 'Verifique sua caixa de entrada.',
      duration: 4000
    });
  };

  if (isLoading) {
    return <AuthLoader />;
  }

  const passwordsMatch = password && confirmPassword && password === confirmPassword;

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Fundo Cósmico Animado */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-[#0F1535] to-background">
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

      {/* Card Principal */}
      <div className="w-full max-w-md relative z-10">
        <AstroCard className="shadow-2xl shadow-accent/20 border-accent/30">
          <div className="space-y-6">
            {/* Header com Logo/Título */}
            <div className="text-center space-y-2">
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent to-secondary flex items-center justify-center">
                  <UIIcons.Star className="text-background" size={32} />
                </div>
              </div>
              <h1 className="text-accent" style={{ fontFamily: 'var(--font-serif)' }}>
                {mode === 'signup' ? 'Descubra o seu Mapa Astral' : 'Bem-vindo de volta ao Cosmos'}
              </h1>
              <p className="text-secondary text-sm">
                {mode === 'signup' 
                  ? 'Crie sua conta e desvende os mistérios do universo' 
                  : 'Entre para acessar seu mapa astral personalizado'
                }
              </p>
            </div>

            {/* Toggle de Modo */}
            <div className="flex gap-2 p-1 bg-card/50 rounded-lg border border-border">
              <button
                onClick={() => setMode('signup')}
                className={`flex-1 py-2 px-4 rounded-md transition-all duration-300 ${
                  mode === 'signup'
                    ? 'bg-accent text-background shadow-lg'
                    : 'text-secondary hover:text-foreground'
                }`}
              >
                Criar Conta
              </button>
              <button
                onClick={() => setMode('login')}
                className={`flex-1 py-2 px-4 rounded-md transition-all duration-300 ${
                  mode === 'login'
                    ? 'bg-accent text-background shadow-lg'
                    : 'text-secondary hover:text-foreground'
                }`}
              >
                Entrar
              </button>
            </div>

            {/* Formulário */}
            <div className="space-y-4">
              {/* E-mail */}
              <div>
                <AstroInput
                  label="E-mail"
                  type="email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  error={errors.email}
                />
              </div>

              {/* Senha */}
              <div>
                <div className="relative">
                  <AstroInput
                    label="Senha"
                    type={showPassword ? 'text' : 'password'}
                    placeholder={mode === 'signup' ? 'Mínimo 6 caracteres' : '••••••'}
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
                      label="Confirmar Senha"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="Digite a senha novamente"
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
                    Esqueceu a senha?
                  </button>
                </div>
              )}

              {/* Botão Principal */}
              <AstroButton
                onClick={mode === 'signup' ? handleEmailSignup : handleLogin}
                className="w-full"
                disabled={!email || !password || (mode === 'signup' && !confirmPassword)}
              >
                {mode === 'signup' ? 'Continuar' : 'Acessar meu Mapa'}
              </AstroButton>

              {/* Divisor */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-card text-muted-foreground">ou continue com</span>
                </div>
              </div>

              {/* Login Social */}
              <button
                onClick={handleGoogleLogin}
                className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white hover:bg-gray-50 text-gray-800 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg border border-gray-200"
              >
                <Chrome size={20} className="text-[#4285F4]" />
                <span className="font-medium">Google</span>
              </button>
            </div>

            {/* Footer com microcopy */}
            <div className="text-center text-xs text-muted-foreground">
              {mode === 'signup' ? (
                <p>
                  Ao criar uma conta, você concorda com nossos{' '}
                  <a href="#" className="text-accent hover:underline">Termos de Uso</a>
                  {' '}e{' '}
                  <a href="#" className="text-accent hover:underline">Política de Privacidade</a>
                </p>
              ) : (
                <p>
                  Não tem uma conta?{' '}
                  <button onClick={() => setMode('signup')} className="text-accent hover:underline">
                    Criar agora
                  </button>
                </p>
              )}
            </div>
          </div>
        </AstroCard>

        {/* Informação de Demo */}
        <div className="mt-6 text-center">
          <AstroCard variant="solid" className="bg-accent/10 border-accent/30">
            <div className="flex items-start gap-2">
              <UIIcons.Info className="text-accent mt-0.5 flex-shrink-0" size={16} />
              <div className="text-xs text-secondary text-left">
                <p className="font-medium text-accent mb-1">Modo de Demonstração</p>
                <p>Para testar o login, use:</p>
                <p className="font-mono mt-1">joao@exemplo.com / 123456 (com mapa)</p>
                <p className="font-mono">maria@exemplo.com / 123456 (sem mapa)</p>
              </div>
            </div>
          </AstroCard>
        </div>
      </div>
    </div>
  );
};

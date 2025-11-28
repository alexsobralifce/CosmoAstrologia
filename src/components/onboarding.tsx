import React, { useEffect, useMemo, useState } from 'react';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import { AstroCard } from './astro-card';
import { UIIcons } from './ui-icons';
import { LocationAutocomplete, LocationSelection } from './location-autocomplete';
import { toast } from 'sonner';

interface OnboardingProps {
  onComplete: (data: OnboardingData) => void | Promise<void>;
  initialEmail?: string;
  initialName?: string;
  initialPassword?: string;
  onBackToLogin?: () => void;
}

export interface OnboardingData {
  name: string;
  birthDate: Date;
  birthTime: string;
  birthPlace: string;
  email?: string;
  password?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
  // Dados calculados do mapa astral
  sunSign?: string;
  sunDegree?: number;
  sunHouse?: number;
  moonSign?: string;
  moonDegree?: number;
  moonHouse?: number;
  ascendant?: string;
  ascendantDegree?: number;
  // Planetas
  mercurySign?: string;
  mercuryDegree?: number;
  mercuryHouse?: number;
  venusSign?: string;
  venusDegree?: number;
  venusHouse?: number;
  marsSign?: string;
  marsDegree?: number;
  marsHouse?: number;
  jupiterSign?: string;
  jupiterDegree?: number;
  jupiterHouse?: number;
  saturnSign?: string;
  saturnDegree?: number;
  saturnHouse?: number;
  uranusSign?: string;
  uranusDegree?: number;
  uranusHouse?: number;
  neptuneSign?: string;
  neptuneDegree?: number;
  neptuneHouse?: number;
  plutoSign?: string;
  plutoDegree?: number;
  plutoHouse?: number;
  // Meio do Céu
  midheavenSign?: string;
  midheavenDegree?: number;
  // Nodos Lunares
  northNodeSign?: string;
  northNodeDegree?: number;
  northNodeHouse?: number;
  southNodeSign?: string;
  southNodeDegree?: number;
  southNodeHouse?: number;
  // Quíron (a ferida do curador)
  chironSign?: string;
  chironDegree?: number;
  chironHouse?: number;
  // Lilith (Lua Negra)
  lilithSign?: string;
  lilithDegree?: number;
  lilithHouse?: number;
  // Fundo do Céu
  icSign?: string;
  icDegree?: number;
}

const STORAGE_KEY = 'saved_users';
const EXISTING_EMAILS = ['joao@exemplo.com', 'maria@exemplo.com'];

export const Onboarding = ({ onComplete, initialEmail, initialName, initialPassword, onBackToLogin }: OnboardingProps) => {
  const [step, setStep] = useState(1);
  const [name, setName] = useState(initialName || '');
  const [email, setEmail] = useState(initialEmail || '');
  const [password, setPassword] = useState(initialPassword || '');
  const [confirmPassword, setConfirmPassword] = useState(initialPassword || '');
  const [showPassword, setShowPassword] = useState(false);
  const [birthDate, setBirthDate] = useState<Date>();
  const [birthDateInput, setBirthDateInput] = useState('');
  const [birthTime, setBirthTime] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [birthCoordinates, setBirthCoordinates] = useState<{ latitude: number; longitude: number } | null>(null);
  const [showTimeHelp, setShowTimeHelp] = useState(false);
  const [emailExists, setEmailExists] = useState(false);
  const [showResetForm, setShowResetForm] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetMessage, setResetMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [confirmPasswordError, setConfirmPasswordError] = useState<string | null>(null);
  const storedUsers = useMemo(() => {
    try {
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      if (Array.isArray(parsed)) {
        return parsed as Array<{ email: string }>;
      }
      return [];
    } catch {
      return [];
    }
  }, []);

  const validateEmail = (value: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value.trim().toLowerCase());
  };

  const handleNext = () => {
    if (step < 4) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleComplete = async () => {
    const finalEmail = initialEmail || email;
    
    // Validações detalhadas
    if (!name || name.trim().length === 0) {
      console.error('Nome é obrigatório');
      return;
    }
    
    if (!birthDate) {
      console.error('Data de nascimento é obrigatória');
      return;
    }
    
    if (!birthTime || birthTime.trim().length === 0) {
      console.error('Hora de nascimento é obrigatória');
      return;
    }
    
    if (!birthPlace || birthPlace.trim().length === 0) {
      console.error('Local de nascimento é obrigatório');
      return;
    }
    
    if (!initialEmail && (!finalEmail || !validateEmail(finalEmail))) {
      console.error('Email é obrigatório e deve ser válido');
      return;
    }
    
    // Validar senha apenas se não houver initialEmail e initialPassword (novo registro direto no onboarding)
    // Se há initialPassword, significa que veio do auth-portal e já foi validada lá
    if (!initialEmail && !initialPassword) {
      if (!password || password.trim().length === 0) {
        setPasswordError('Senha é obrigatória');
        toast.error('Senha é obrigatória para registro');
        return;
      }
      
      if (password.length < 6) {
        setPasswordError('A senha deve ter pelo menos 6 caracteres');
        toast.error('A senha deve ter pelo menos 6 caracteres');
        return;
      }
      
      if (password !== confirmPassword) {
        setConfirmPasswordError('As senhas não coincidem');
        toast.error('As senhas não coincidem. Por favor, verifique e tente novamente.');
        return;
      }
    } else if (!initialEmail && initialPassword) {
      // Se há initialPassword mas o usuário editou, validar novamente
      const currentPassword = password || initialPassword;
      if (currentPassword !== confirmPassword && confirmPassword) {
        setConfirmPasswordError('As senhas não coincidem');
        toast.error('As senhas não coincidem. Por favor, verifique e tente novamente.');
        return;
      }
    }
    
    if (step === 4 && !birthCoordinates) {
      console.error('Coordenadas geográficas são obrigatórias. Selecione uma cidade da lista.');
      return;
    }

    console.log('Dados completos:', {
      name,
      birthDate,
      birthTime,
      birthPlace,
      email: finalEmail,
      password: password ? '***' : 'não fornecida',
      coordinates: birthCoordinates,
    });

    setIsSubmitting(true);
    
    try {
      // Preparar dados
      // Prioridade: initialPassword (vem do auth-portal) > password (digitado no onboarding)
      // Se há initialEmail, a senha deve vir de initialPassword (coletada no auth-portal)
      // Se não há initialEmail, a senha deve vir de password (digitada no step 1)
      let finalPassword: string | undefined;
      if (initialEmail && initialPassword) {
        // Veio do auth-portal - usar initialPassword
        finalPassword = initialPassword;
      } else if (!initialEmail && password) {
        // Novo registro direto no onboarding - usar password digitado
        finalPassword = password;
      } else if (initialPassword) {
        // Fallback: se houver initialPassword, usar ela
        finalPassword = initialPassword;
      } else if (password) {
        // Fallback: se houver password, usar ela
        finalPassword = password;
      }
      
      const onboardingData = {
        name,
        birthDate,
        birthTime,
        birthPlace,
        email: finalEmail || undefined,
        password: finalPassword,
        coordinates: birthCoordinates || undefined,
      };

      console.log('[DEBUG Onboarding] Dados preparados para envio:', {
        name,
        email: finalEmail,
        hasPassword: !!finalPassword,
        passwordSource: initialPassword ? 'initialPassword' : password ? 'password' : 'nenhuma',
        hasInitialEmail: !!initialEmail,
        hasInitialPassword: !!initialPassword,
        hasPasswordField: !!password,
      });

      // Chamar onComplete (que é assíncrono)
      await onComplete(onboardingData);

      console.log('onComplete concluído com sucesso');

      // Salvar email se necessário
      if (finalEmail) {
        const normalized = finalEmail.toLowerCase();
        const filtered = storedUsers.filter((user) => user.email !== normalized);
        const updated = [...filtered, { email: normalized }];
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      }

      // Resetar estado de submissão após sucesso
      setIsSubmitting(false);
    } catch (error) {
      console.error('Erro ao completar onboarding:', error);
      setIsSubmitting(false);
      // O erro já foi tratado no App.tsx com toast, não precisamos fazer nada aqui
    }
  };

  const handleBirthDateInput = (rawValue: string) => {
    const digits = rawValue.replace(/\D/g, '').slice(0, 8);
    let formatted = digits;

    if (digits.length > 4) {
      formatted = `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`;
    } else if (digits.length > 2) {
      formatted = `${digits.slice(0, 2)}/${digits.slice(2)}`;
    }

    setBirthDateInput(formatted);

    if (digits.length === 8) {
      const day = Number(digits.slice(0, 2));
      const month = Number(digits.slice(2, 4)) - 1;
      const year = Number(digits.slice(4));

      const parsedDate = new Date(year, month, day);
      const isValid =
        parsedDate.getFullYear() === year &&
        parsedDate.getMonth() === month &&
        parsedDate.getDate() === day;

      if (isValid) {
        setBirthDate(parsedDate);
        return;
      }
    }

    setBirthDate(undefined);
  };

  const isStepValid = () => {
    switch (step) {
      case 1:
        if (initialEmail) {
          // Se há initialEmail, pode ter initialPassword (vem do auth-portal)
          // Nesse caso, não precisa validar senha novamente
          return name.trim().length > 0;
        }
        // Novo registro direto no onboarding - validar tudo
        const currentPassword = password || '';
        const currentConfirmPassword = confirmPassword || '';
        
        // Validar se ambos os campos de senha foram preenchidos e são iguais
        const passwordsMatch = currentPassword === currentConfirmPassword && currentPassword.length > 0;
        const passwordValid = currentPassword.trim().length >= 6;
        const hasPassword = currentPassword.trim().length > 0;
        
        const emailValid = validateEmail(email);
        const nameValid = name.trim().length > 0;
        
        // emailExists bloqueia se o email já existe no sistema
        // Se emailExists é true, não pode avançar
        // Se emailExists é false ou email ainda não foi verificado, pode avançar
        const emailNotExists = !emailExists;
        
        const isValid = (
          nameValid &&
          emailValid &&
          emailNotExists &&
          hasPassword &&
          passwordValid &&
          passwordsMatch
        );
        
        // Debug temporário
        if (step === 1) {
          console.log('[DEBUG Step 1]', {
            nameValid,
            emailValid,
            emailNotExists,
            emailExists,
            hasPassword,
            passwordValid,
            passwordsMatch,
            isValid,
            passwordLength: currentPassword.length,
            confirmLength: currentConfirmPassword.length,
          });
        }
        
        return isValid;
      case 2:
        return birthDate !== undefined;
      case 3:
        return birthTime.length > 0;
      case 4:
        return birthPlace.trim().length > 0 && !!birthCoordinates;
      default:
        return true;
    }
  };

  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (!value) {
      setEmailExists(false);
      setShowResetForm(false);
      return;
    }
    const normalized = value.trim().toLowerCase();
    const exists =
      EXISTING_EMAILS.includes(normalized) ||
      storedUsers.some((user) => user.email === normalized);
    setEmailExists(exists);
    setShowResetForm(false);
    setResetMessage(null);
  };

  const handleSendReset = () => {
    if (!validateEmail(resetEmail)) {
      setResetMessage('Digite um e-mail válido para recuperar sua senha.');
      return;
    }
    setResetMessage('Enviamos instruções para redefinir sua senha.');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-background via-background to-[#1a1f4a] dark:to-[#1a1f4a] light:to-[#F0E6D2]">
      <div className="w-full max-w-2xl">
        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            {[1, 2, 3, 4].map((s) => (
              <div
                key={s}
                className={`h-2 flex-1 mx-1 rounded-full transition-all duration-300 ${
                  s <= step ? 'bg-accent' : 'bg-card'
                }`}
              />
            ))}
          </div>
          <p className="text-center text-secondary">Etapa {step} de 4</p>
        </div>

        <AstroCard className="space-y-8">
          {/* Step 1: Name */}
          {step === 1 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent">
                  {initialName ? `Alinhando os Astros para ${initialName.split(' ')[0]}` : 'Vamos criar seu Mapa Astral'}
                </h1>
                <p className="text-secondary">
                  {initialName 
                    ? 'Confirme seu nome ou edite se necessário.' 
                    : 'Para começar, precisamos do seu nome completo.'
                  }
                </p>
              </div>
              <AstroInput
                label="Nome Completo"
                placeholder="Digite seu nome"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus={!initialName}
              />
              {initialEmail ? (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-accent/10 border border-accent/20">
                  <UIIcons.CheckCircle className="text-accent flex-shrink-0" size={16} />
                  <p className="text-sm text-secondary">
                    Conta conectada: <span className="text-foreground font-medium">{initialEmail}</span>
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  <AstroInput
                    label="E-mail"
                    type="email"
                    placeholder="seu@email.com"
                    value={email}
                    onChange={(e) => handleEmailChange(e.target.value)}
                  />
                  {email && emailExists && (
                    <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-sm text-destructive space-y-2">
                      <div className="flex items-center gap-2">
                        <UIIcons.AlertCircle size={16} />
                        <span>Este e-mail já possui cadastro.</span>
                      </div>
                      <button
                        className="text-accent underline font-medium"
                        onClick={() => {
                          setShowResetForm(true);
                          setResetEmail(email);
                          setResetMessage(null);
                        }}
                      >
                        Redefinir senha
                      </button>
                    </div>
                  )}
                  {showResetForm && (
                    <div className="space-y-2 p-3 rounded-lg bg-card border border-border">
                      <AstroInput
                        label="E-mail para recuperar"
                        value={resetEmail}
                        onChange={(e) => setResetEmail(e.target.value)}
                      />
                      <AstroButton variant="secondary" onClick={handleSendReset}>
                        Enviar nova senha
                      </AstroButton>
                      {resetMessage && (
                        <p className="text-sm text-secondary">{resetMessage}</p>
                      )}
                    </div>
                  )}
                  
                  {!emailExists && (
                    <>
                      <div className="relative">
                        <AstroInput
                          label="Senha"
                          type={showPassword ? "text" : "password"}
                          placeholder="Mínimo 6 caracteres"
                          value={password}
                          onChange={(e) => {
                            const newPassword = e.target.value;
                            setPassword(newPassword);
                            // Limpar erro de confirmação quando a senha principal muda
                            if (confirmPassword && newPassword !== confirmPassword) {
                              setConfirmPasswordError('As senhas não coincidem');
                            } else {
                              setConfirmPasswordError(null);
                            }
                            // Validar tamanho mínimo
                            if (newPassword && newPassword.length < 6) {
                              setPasswordError('A senha deve ter pelo menos 6 caracteres');
                            } else {
                              setPasswordError(null);
                            }
                          }}
                          error={passwordError || undefined}
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3 top-9 text-secondary hover:text-foreground transition-colors"
                        >
                          {showPassword ? (
                            <UIIcons.EyeOff size={18} />
                          ) : (
                            <UIIcons.Eye size={18} />
                          )}
                        </button>
                      </div>
                      
                      <div className="relative">
                        <AstroInput
                          label="Confirmar Senha"
                          type={showPassword ? "text" : "password"}
                          placeholder="Digite a senha novamente"
                          value={confirmPassword}
                          onChange={(e) => {
                            const newConfirmPassword = e.target.value;
                            setConfirmPassword(newConfirmPassword);
                            // Validar se as senhas coincidem
                            if (newConfirmPassword && password && newConfirmPassword !== password) {
                              setConfirmPasswordError('As senhas não coincidem');
                            } else {
                              setConfirmPasswordError(null);
                            }
                          }}
                          error={confirmPasswordError || undefined}
                        />
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Step 2: Birth Date */}
          {step === 2 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent">Qual sua data de nascimento?</h1>
                <p className="text-secondary">Digite no formato dia/mês/ano.</p>
              </div>
              <div className="space-y-2">
                <AstroInput
                  label="Data de Nascimento"
                  placeholder="dd/mm/aaaa"
                  value={birthDateInput}
                  onChange={(e) => handleBirthDateInput(e.target.value)}
                  maxLength={10}
                />
                {birthDateInput && birthDate === undefined && (
                  <p className="text-sm text-destructive">Digite uma data válida.</p>
                )}
              </div>
            </div>
          )}

          {/* Step 3: Birth Time */}
          {step === 3 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent">E a hora em que você nasceu?</h1>
                <p className="text-secondary">A hora exata é importante para calcular o ascendente.</p>
              </div>
              <AstroInput
                label="Hora de Nascimento"
                type="time"
                value={birthTime}
                onChange={(e) => setBirthTime(e.target.value)}
                autoFocus
              />
              <button
                onClick={() => setShowTimeHelp(!showTimeHelp)}
                className="text-sm text-accent hover:text-accent/80 transition-colors flex items-center gap-2"
              >
                <UIIcons.Info size={16} />
                Não sabe a hora exata?
              </button>
              {showTimeHelp && (
                <AstroCard variant="solid" className="text-sm space-y-2">
                  <p className="text-foreground">Sem problemas!</p>
                  <p className="text-secondary">
                    O ascendente pode ter uma pequena variação, mas ainda conseguimos calcular
                    seu mapa principal com Sol, Lua e os outros planetas. Se possível, consulte
                    sua certidão de nascimento para obter a hora exata.
                  </p>
                </AstroCard>
              )}
            </div>
          )}

          {/* Step 4: Birth Place */}
          {step === 4 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent">Onde você nasceu?</h1>
                <p className="text-secondary">Digite a cidade e selecione na lista.</p>
              </div>
              <div className="space-y-4">
                <LocationAutocomplete
                  label="Local de Nascimento"
                  placeholder="Digite a cidade e selecione"
                  value={birthPlace}
                  onChange={(val) => {
                    setBirthPlace(val);
                    setBirthCoordinates(null);
                  }}
                  onSelect={(selection: LocationSelection) => {
                    setBirthPlace(selection.displayName);
                    setBirthCoordinates({
                      latitude: selection.lat,
                      longitude: selection.lon,
                    });
                  }}
                />
                {birthPlace && !birthCoordinates && (
                  <p className="text-sm text-secondary">
                    Selecione um item da lista para capturar as coordenadas geográficas.
                  </p>
                )}
                {birthCoordinates && (
                  <div className="text-xs text-secondary flex items-center gap-2">
                    <UIIcons.MapPin size={14} className="text-accent" />
                    <span>
                      Coordenadas: {birthCoordinates.latitude.toFixed(4)}°, {birthCoordinates.longitude.toFixed(4)}°
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex gap-4 pt-4">
            {step > 1 && (
              <AstroButton variant="secondary" onClick={handleBack} className="flex-1">
                Voltar
              </AstroButton>
            )}
            {step === 1 && onBackToLogin && (
              <AstroButton
                variant="secondary"
                onClick={onBackToLogin}
                className="flex-1"
              >
                <UIIcons.ArrowLeft className="mr-2" size={16} />
                Voltar ao Login
              </AstroButton>
            )}
            {step < 4 ? (
              <AstroButton
                variant="primary"
                onClick={handleNext}
                disabled={!isStepValid()}
                className="flex-1"
              >
                Avançar
              </AstroButton>
            ) : (
              <AstroButton
                variant="primary"
                onClick={(e) => {
                  e.preventDefault();
                  if (!isSubmitting && isStepValid()) {
                    handleComplete();
                  }
                }}
                disabled={!isStepValid() || isSubmitting}
                className="flex-1"
              >
                {isSubmitting ? (
                  <span className="flex items-center gap-2">
                    <UIIcons.Loader className="w-4 h-4 animate-spin" />
                    Processando...
                  </span>
                ) : (
                  'Ver meu mapa astral'
                )}
              </AstroButton>
            )}
          </div>
        </AstroCard>
      </div>
    </div>
  );
};

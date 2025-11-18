import { useState, useEffect } from 'react';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import { AstroCard } from './astro-card';
import { DatePicker } from './date-picker';
import { LocationAutocomplete } from './location-autocomplete';
import { UIIcons } from './ui-icons';

interface OnboardingProps {
  onComplete: (data: OnboardingData) => void;
  onLogin?: () => void;
}

export interface OnboardingData {
  name: string;
  birthDate: Date;
  birthTime: string;
  birthPlace: string;
}

export const Onboarding = ({ onComplete, onLogin }: OnboardingProps) => {
  // Check if there's a saved step from OAuth callback
  const savedStep = sessionStorage.getItem('onboarding_step');
  const [step, setStep] = useState(savedStep ? parseInt(savedStep) : 1);
  const [name, setName] = useState('');
  const [birthDate, setBirthDate] = useState<Date>();
  const [birthTime, setBirthTime] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [showTimeHelp, setShowTimeHelp] = useState(false);

  // Clear saved step after loading
  useEffect(() => {
    if (savedStep) {
      sessionStorage.removeItem('onboarding_step');
    }
  }, [savedStep]);

  const handleNext = () => {
    if (step < 5) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleComplete = async () => {
    if (name && birthDate && birthTime && birthPlace) {
      onComplete({ name, birthDate, birthTime, birthPlace });
    }
  };

  const isStepValid = () => {
    switch (step) {
      case 1:
        return name.trim().length > 0;
      case 2:
        return birthDate !== undefined;
      case 3:
        return birthTime.length > 0;
      case 4:
        return birthPlace.trim().length > 0;
      case 5:
        // Step 5 is optional account creation - always valid
        return true;
      default:
        return true;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-background via-background to-[#1a1f4a] dark:to-[#1a1f4a] light:to-[#F0E6D2]">
      <div className="w-full max-w-2xl">
        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            {[1, 2, 3, 4, 5].map((s) => (
              <div
                key={s}
                className={`h-2 flex-1 mx-1 rounded-full transition-all duration-300 ${
                  s <= step ? 'bg-accent' : 'bg-card'
                }`}
              />
            ))}
          </div>
          <p className="text-center text-secondary">Etapa {step} de 5</p>
        </div>

        <AstroCard className="space-y-8">
          {/* Step 1: Name */}
          {step === 1 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent">Vamos criar seu Mapa Astral</h1>
                <p className="text-secondary">Para começar, precisamos do seu nome completo.</p>
              </div>
              <AstroInput
                label="Nome Completo"
                placeholder="Digite seu nome"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
              />
            </div>
          )}

          {/* Step 2: Birth Date */}
          {step === 2 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent">Qual sua data de nascimento?</h1>
                <p className="text-secondary">Escolha a data exata do seu nascimento.</p>
              </div>
              <div className="space-y-4">
                <DatePicker
                  value={birthDate}
                  onChange={setBirthDate}
                  minYear={1900}
                  maxYear={new Date().getFullYear()}
                />
              </div>
            </div>
          )}

          {/* Step 4: Birth Time */}
          {step === 4 && (
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

          {/* Step 5: Optional Account Creation */}
          {step === 5 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent">Salve seu Mapa Astral</h1>
                <p className="text-secondary">
                  Crie uma conta gratuita para salvar seu mapa e acessá-lo sempre que quiser. 
                  Você também pode pular e ver seu mapa agora mesmo!
                </p>
              </div>

              <div className="space-y-4">
                <AstroButton
                  variant="google"
                  className="w-full gap-3"
                  onClick={() => {
                    // Save birth data for after authentication
                    if (name && birthDate && birthTime && birthPlace) {
                      sessionStorage.setItem('birth_data_to_save', JSON.stringify({
                        name,
                        birthDate: birthDate.toISOString(),
                        birthTime,
                        birthPlace
                      }));
                    }
                    // Trigger Google OAuth
                    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                    window.location.href = `${API_BASE_URL}/api/auth/login`;
                  }}
                >
                  <svg width="20" height="20" viewBox="0 0 18 18">
                    <path
                      fill="#4285F4"
                      d="M16.51 8H8.98v3h4.3c-.18 1-.74 1.48-1.6 2.04v2.01h2.6a7.8 7.8 0 0 0 2.38-5.88c0-.57-.05-.66-.15-1.18z"
                    />
                    <path
                      fill="#34A853"
                      d="M8.98 17c2.16 0 3.97-.72 5.3-1.94l-2.6-2a4.8 4.8 0 0 1-7.18-2.54H1.83v2.07A8 8 0 0 0 8.98 17z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M4.5 10.52a4.8 4.8 0 0 1 0-3.04V5.41H1.83a8 8 0 0 0 0 7.18l2.67-2.07z"
                    />
                    <path
                      fill="#EA4335"
                      d="M8.98 4.18c1.17 0 2.23.4 3.06 1.2l2.3-2.3A8 8 0 0 0 1.83 5.4L4.5 7.49a4.77 4.77 0 0 1 4.48-3.3z"
                    />
                  </svg>
                  Criar Conta com Google
                </AstroButton>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-border"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-card text-secondary">Ou</span>
                  </div>
                </div>

                {onLogin && (
                  <AstroButton 
                    variant="secondary" 
                    className="w-full" 
                    onClick={onLogin}
                  >
                    <UIIcons.User size={16} />
                    Já tenho conta - Fazer Login
                  </AstroButton>
                )}

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-border"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-card text-secondary">Ou</span>
                  </div>
                </div>

                <AstroButton 
                  variant="outline" 
                  className="w-full" 
                  onClick={handleComplete}
                >
                  Ver Mapa Agora (sem criar conta)
                </AstroButton>
              </div>
            </div>
          )}

          {/* Step 4: Birth Place */}
          {step === 4 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent">Onde você nasceu?</h1>
                <p className="text-secondary">Digite a cidade e selecione da lista.</p>
              </div>
              <div className="space-y-4">
                <LocationAutocomplete
                  label="Local de Nascimento"
                  placeholder="Ex: São Paulo, SP"
                  value={birthPlace}
                  onChange={setBirthPlace}
                  autoFocus
                />
                <div className="flex items-start gap-2 p-3 rounded-lg bg-accent/10 border border-accent/20">
                  <UIIcons.MapPin className="text-accent mt-0.5 flex-shrink-0" size={16} />
                  <p className="text-sm text-secondary">
                    Precisamos do local exato para calcular as posições planetárias corretas
                    baseadas na latitude e longitude.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex gap-4 pt-4">
            {step > 1 && step < 5 && (
              <AstroButton variant="secondary" onClick={handleBack} className="flex-1">
                Voltar
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
            ) : step === 4 ? (
              <AstroButton
                variant="primary"
                onClick={handleNext}
                disabled={!isStepValid()}
                className="flex-1"
              >
                Continuar
              </AstroButton>
            ) : null}
            {/* Step 5 buttons are handled inside the step component */}
          </div>
        </AstroCard>
      </div>
    </div>
  );
};

import { useState } from 'react';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import { AstroCard } from './astro-card';
import { Calendar } from './ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { UIIcons } from './ui-icons';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface OnboardingProps {
  onComplete: (data: OnboardingData) => void;
  initialEmail?: string;
  initialName?: string;
}

export interface OnboardingData {
  name: string;
  birthDate: Date;
  birthTime: string;
  birthPlace: string;
}

export const Onboarding = ({ onComplete, initialEmail, initialName }: OnboardingProps) => {
  const [step, setStep] = useState(1);
  const [name, setName] = useState(initialName || '');
  const [birthDate, setBirthDate] = useState<Date>();
  const [birthTime, setBirthTime] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [showTimeHelp, setShowTimeHelp] = useState(false);

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

  const handleComplete = () => {
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
              {initialEmail && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-accent/10 border border-accent/20">
                  <UIIcons.CheckCircle className="text-accent flex-shrink-0" size={16} />
                  <p className="text-sm text-secondary">
                    Conta conectada: <span className="text-foreground font-medium">{initialEmail}</span>
                  </p>
                </div>
              )}
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
                <Popover>
                  <PopoverTrigger asChild>
                    <button className="w-full px-4 py-3 rounded-lg bg-input-background border border-[var(--input-border)] text-foreground transition-all duration-200 hover:border-[var(--input-border-active)] focus:outline-none focus:border-[var(--input-border-active)] focus:ring-2 focus:ring-accent/20 text-left flex items-center justify-between">
                      {birthDate ? (
                        format(birthDate, "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
                      ) : (
                        <span className="text-secondary">Selecione a data</span>
                      )}
                      <UIIcons.Calendar className="text-accent" size={20} />
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0 bg-card border border-border backdrop-blur-md">
                    <Calendar
                      mode="single"
                      selected={birthDate}
                      onSelect={setBirthDate}
                      initialFocus
                      disabled={(date) => date > new Date()}
                      captionLayout="dropdown-buttons"
                      fromYear={1900}
                      toYear={new Date().getFullYear()}
                    />
                  </PopoverContent>
                </Popover>
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
                <p className="text-secondary">Digite a cidade e o estado.</p>
              </div>
              <div className="space-y-4">
                <AstroInput
                  label="Local de Nascimento"
                  placeholder="Ex: São Paulo, SP"
                  value={birthPlace}
                  onChange={(e) => setBirthPlace(e.target.value)}
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

          {/* Step 5: Login/Finalization */}
          {step === 5 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent">Seu mapa está quase pronto!</h1>
                <p className="text-secondary">
                  Crie sua conta para salvar e acessar suas interpretações.
                </p>
              </div>

              <div className="space-y-4">
                <AstroButton
                  variant="google"
                  className="w-full gap-3"
                  onClick={handleComplete}
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
                  Entrar com Google
                </AstroButton>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-border"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-card text-secondary">Ou</span>
                  </div>
                </div>

                <div className="space-y-3">
                  <AstroInput type="email" placeholder="seu@email.com" label="Email" />
                  <AstroInput type="password" placeholder="••••••••" label="Senha" />
                  <AstroButton variant="primary" className="w-full" onClick={handleComplete}>
                    Criar Conta
                  </AstroButton>
                </div>

                <p className="text-center text-sm text-secondary">
                  Já tem uma conta?{' '}
                  <button className="text-accent hover:text-accent/80 transition-colors">
                    Entrar
                  </button>
                </p>
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
            {step < 5 && (
              <AstroButton
                variant="primary"
                onClick={handleNext}
                disabled={!isStepValid()}
                className="flex-1"
              >
                Avançar
              </AstroButton>
            )}
          </div>
        </AstroCard>
      </div>
    </div>
  );
};

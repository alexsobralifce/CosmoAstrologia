import { useState } from 'react';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import { AstroCard } from './astro-card';
import { UIIcons } from './ui-icons';
import { LocationAutocomplete, LocationSelection } from './location-autocomplete';
import { toast } from 'sonner';
import { useLanguage } from '../i18n';

interface GoogleOnboardingProps {
  email: string;
  name: string;
  onComplete: (data: GoogleOnboardingData) => void | Promise<void>;
  onBack?: () => void;
}

export interface GoogleOnboardingData {
  name: string;
  birthDate: Date;
  birthTime: string;
  birthPlace: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
}

export const GoogleOnboarding = ({ email, name: initialName, onComplete, onBack }: GoogleOnboardingProps) => {
  const { language } = useLanguage();
  const [step, setStep] = useState(1);
  const [name, setName] = useState(initialName || '');
  const [birthDateInput, setBirthDateInput] = useState('');
  const [birthDate, setBirthDate] = useState<Date>();
  const [birthTime, setBirthTime] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [birthCoordinates, setBirthCoordinates] = useState<{ latitude: number; longitude: number } | null>(null);
  const [showTimeHelp, setShowTimeHelp] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const texts = {
    welcome: language === 'pt' ? 'Bem-vindo ao Cosmos Astral!' : 'Welcome to Cosmos Astral!',
    googleConnected: language === 'pt' ? 'Sua conta Google foi conectada com sucesso.' : 'Your Google account has been connected.',
    completeProfile: language === 'pt' ? 'Complete seu perfil para gerar seu mapa astral personalizado.' : 'Complete your profile to generate your personalized birth chart.',
    step1Title: language === 'pt' ? 'Confirme seu nome' : 'Confirm your name',
    step1Desc: language === 'pt' ? 'Este nome aparecerá no seu mapa astral.' : 'This name will appear on your birth chart.',
    step2Title: language === 'pt' ? 'Qual sua data de nascimento?' : 'What is your birth date?',
    step2Desc: language === 'pt' ? 'Digite no formato dia/mês/ano.' : 'Enter in day/month/year format.',
    step3Title: language === 'pt' ? 'E a hora em que você nasceu?' : 'What time were you born?',
    step3Desc: language === 'pt' ? 'A hora exata é importante para calcular o ascendente.' : 'The exact time is important to calculate your ascendant.',
    step4Title: language === 'pt' ? 'Onde você nasceu?' : 'Where were you born?',
    step4Desc: language === 'pt' ? 'Digite a cidade e selecione na lista.' : 'Type your city and select from the list.',
    fullName: language === 'pt' ? 'Nome Completo' : 'Full Name',
    birthDateLabel: language === 'pt' ? 'Data de Nascimento' : 'Birth Date',
    birthTimeLabel: language === 'pt' ? 'Hora de Nascimento' : 'Birth Time',
    birthPlaceLabel: language === 'pt' ? 'Local de Nascimento' : 'Birth Place',
    back: language === 'pt' ? 'Voltar' : 'Back',
    next: language === 'pt' ? 'Avançar' : 'Next',
    generateChart: language === 'pt' ? 'Gerar meu Mapa Astral' : 'Generate my Birth Chart',
    processing: language === 'pt' ? 'Processando...' : 'Processing...',
    invalidDate: language === 'pt' ? 'Digite uma data válida.' : 'Enter a valid date.',
    selectCity: language === 'pt' ? 'Selecione um item da lista para capturar as coordenadas.' : 'Select an item from the list to capture coordinates.',
    dontKnowTime: language === 'pt' ? 'Não sabe a hora exata?' : "Don't know the exact time?",
    timeHelpTitle: language === 'pt' ? 'Sem problemas!' : 'No problem!',
    timeHelpText: language === 'pt' 
      ? 'O ascendente pode ter uma pequena variação, mas ainda conseguimos calcular seu mapa principal com Sol, Lua e os outros planetas. Se possível, consulte sua certidão de nascimento para obter a hora exata.'
      : 'The ascendant may have a slight variation, but we can still calculate your main chart with the Sun, Moon, and other planets. If possible, check your birth certificate for the exact time.',
    stepOf: language === 'pt' ? 'Etapa' : 'Step',
    of: language === 'pt' ? 'de' : 'of',
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
        parsedDate.getDate() === day &&
        year >= 1900 && year <= new Date().getFullYear();

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
        return name.trim().length > 0;
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
    if (!birthDate || !birthCoordinates) {
      toast.error(language === 'pt' ? 'Preencha todos os campos' : 'Fill in all fields');
      return;
    }

    setIsSubmitting(true);

    try {
      await onComplete({
        name,
        birthDate,
        birthTime,
        birthPlace,
        coordinates: birthCoordinates,
      });
    } catch (error) {
      console.error('Erro ao completar onboarding:', error);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-b from-background via-background to-[#1a1f4a] dark:to-[#1a1f4a]">
      <div className="w-full max-w-2xl">
        {/* Header com informação do Google */}
        <div className="mb-6 text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-md">
              <svg viewBox="0 0 24 24" className="w-6 h-6">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
            </div>
            <UIIcons.CheckCircle className="text-green-500" size={20} />
          </div>
          <p className="text-sm text-muted-foreground">{email}</p>
        </div>

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
          <p className="text-center text-secondary">{texts.stepOf} {step} {texts.of} 4</p>
        </div>

        <AstroCard className="space-y-8">
          {/* Step 1: Name */}
          {step === 1 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent text-2xl font-serif">{texts.welcome}</h1>
                <p className="text-secondary">{texts.googleConnected}</p>
                <p className="text-secondary">{texts.completeProfile}</p>
              </div>
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-foreground">{texts.step1Title}</h2>
                <p className="text-sm text-secondary">{texts.step1Desc}</p>
                <AstroInput
                  label={texts.fullName}
                  placeholder={language === 'pt' ? 'Digite seu nome completo' : 'Enter your full name'}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  autoFocus
                />
              </div>
            </div>
          )}

          {/* Step 2: Birth Date */}
          {step === 2 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent text-2xl font-serif">{texts.step2Title}</h1>
                <p className="text-secondary">{texts.step2Desc}</p>
              </div>
              <div className="space-y-2">
                <AstroInput
                  label={texts.birthDateLabel}
                  placeholder="dd/mm/aaaa"
                  value={birthDateInput}
                  onChange={(e) => handleBirthDateInput(e.target.value)}
                  maxLength={10}
                  autoFocus
                />
                {birthDateInput && birthDate === undefined && (
                  <p className="text-sm text-destructive">{texts.invalidDate}</p>
                )}
              </div>
            </div>
          )}

          {/* Step 3: Birth Time */}
          {step === 3 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent text-2xl font-serif">{texts.step3Title}</h1>
                <p className="text-secondary">{texts.step3Desc}</p>
              </div>
              <AstroInput
                label={texts.birthTimeLabel}
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
                {texts.dontKnowTime}
              </button>
              {showTimeHelp && (
                <AstroCard variant="solid" className="text-sm space-y-2">
                  <p className="text-foreground font-medium">{texts.timeHelpTitle}</p>
                  <p className="text-secondary">{texts.timeHelpText}</p>
                </AstroCard>
              )}
            </div>
          )}

          {/* Step 4: Birth Place */}
          {step === 4 && (
            <div className="space-y-6 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-accent text-2xl font-serif">{texts.step4Title}</h1>
                <p className="text-secondary">{texts.step4Desc}</p>
              </div>
              <div className="space-y-4">
                <LocationAutocomplete
                  label={texts.birthPlaceLabel}
                  placeholder={language === 'pt' ? 'Digite a cidade e selecione' : 'Type your city and select'}
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
                  <p className="text-sm text-secondary">{texts.selectCity}</p>
                )}
                {birthCoordinates && (
                  <div className="text-xs text-secondary flex items-center gap-2">
                    <UIIcons.MapPin size={14} className="text-accent" />
                    <span>
                      {language === 'pt' ? 'Coordenadas' : 'Coordinates'}: {birthCoordinates.latitude.toFixed(4)}°, {birthCoordinates.longitude.toFixed(4)}°
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex gap-4 pt-4">
            {step > 1 ? (
              <AstroButton variant="secondary" onClick={handleBack} className="flex-1">
                <UIIcons.ArrowLeft className="mr-2" size={16} />
                {texts.back}
              </AstroButton>
            ) : onBack && (
              <AstroButton variant="secondary" onClick={onBack} className="flex-1">
                <UIIcons.ArrowLeft className="mr-2" size={16} />
                {texts.back}
              </AstroButton>
            )}
            {step < 4 ? (
              <AstroButton
                variant="primary"
                onClick={handleNext}
                disabled={!isStepValid()}
                className="flex-1"
              >
                {texts.next}
                <UIIcons.ArrowRight className="ml-2" size={16} />
              </AstroButton>
            ) : (
              <AstroButton
                variant="primary"
                onClick={handleComplete}
                disabled={!isStepValid() || isSubmitting}
                className="flex-1"
              >
                {isSubmitting ? (
                  <span className="flex items-center gap-2">
                    <UIIcons.Loader className="w-4 h-4 animate-spin" />
                    {texts.processing}
                  </span>
                ) : (
                  <>
                    <UIIcons.Star className="mr-2" size={16} />
                    {texts.generateChart}
                  </>
                )}
              </AstroButton>
            )}
          </div>
        </AstroCard>
      </div>
    </div>
  );
};


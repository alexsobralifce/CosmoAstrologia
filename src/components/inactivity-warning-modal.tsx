import { useEffect, useState } from 'react';
import { UIIcons } from './ui-icons';

interface InactivityWarningModalProps {
  isOpen: boolean;
  remainingSeconds: number;
  onContinue: () => void;
  onLogout: () => void;
}

export const InactivityWarningModal = ({
  isOpen,
  remainingSeconds: initialSeconds,
  onContinue,
  onLogout,
}: InactivityWarningModalProps) => {
  const [countdown, setCountdown] = useState(initialSeconds);

  useEffect(() => {
    if (!isOpen) return;

    setCountdown(initialSeconds);

    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isOpen, initialSeconds]);

  // Auto logout quando countdown chega a 0
  useEffect(() => {
    if (countdown === 0 && isOpen) {
      onLogout();
    }
  }, [countdown, isOpen, onLogout]);

  if (!isOpen) return null;

  const minutes = Math.floor(countdown / 60);
  const seconds = countdown % 60;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn">
      <div className="bg-card border border-border rounded-2xl shadow-2xl max-w-md w-full p-8 space-y-6 animate-fadeIn">
        {/* Ícone de alerta */}
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-full bg-amber-500/10 flex items-center justify-center">
            <UIIcons.AlertCircle size={32} className="text-amber-500" />
          </div>
        </div>

        {/* Título */}
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-foreground font-serif">
            Sessão Inativa
          </h2>
          <p className="text-muted-foreground">
            Sua sessão está prestes a expirar por inatividade
          </p>
        </div>

        {/* Countdown */}
        <div className="bg-muted/50 rounded-xl p-6 text-center">
          <p className="text-sm text-muted-foreground mb-2">
            Tempo restante:
          </p>
          <div className="text-4xl font-bold text-amber-500 font-mono">
            {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
          </div>
        </div>

        {/* Mensagem */}
        <p className="text-sm text-center text-muted-foreground">
          Clique em "Continuar Conectado" para permanecer na sua sessão.
        </p>

        {/* Botões */}
        <div className="flex gap-3">
          <button
            onClick={onLogout}
            className="flex-1 py-3 px-4 rounded-xl border border-border bg-muted hover:bg-muted/80 text-foreground font-medium transition-all duration-200"
          >
            Sair Agora
          </button>
          <button
            onClick={onContinue}
            className="flex-1 py-3 px-4 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground font-medium transition-all duration-200 shadow-lg shadow-primary/20"
          >
            Continuar Conectado
          </button>
        </div>

        {/* Informação adicional */}
        <div className="pt-4 border-t border-border">
          <div className="flex items-start gap-2 text-xs text-muted-foreground">
            <UIIcons.Info size={14} className="mt-0.5 flex-shrink-0" />
            <p>
              Por segurança, encerramos sessões inativas após 30 minutos. 
              Isso ajuda a proteger suas informações pessoais.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};


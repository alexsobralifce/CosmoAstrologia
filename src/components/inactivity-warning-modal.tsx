import React, { useEffect, useState } from 'react';
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
    <div className="modal-overlay">
      <div className="modal-content">
        {/* Ícone de alerta */}
        <div className="modal-header">
          <div className="modal-icon-container">
            <UIIcons.AlertCircle size={32} className="text-amber-500" />
          </div>
        </div>

        {/* Título */}
        <div className="modal-header">
          <h2 className="modal-title">
            Sessão Inativa
          </h2>
          <p className="modal-description">
            Sua sessão está prestes a expirar por inatividade
          </p>
        </div>

        {/* Countdown */}
        <div className="modal-countdown-container">
          <p className="modal-countdown-label">
            Tempo restante:
          </p>
          <div className="modal-countdown-time">
            {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
          </div>
        </div>

        {/* Mensagem */}
        <p className="modal-message">
          Clique em "Continuar Conectado" para permanecer na sua sessão.
        </p>

        {/* Botões */}
        <div className="modal-footer">
          <button
            onClick={onLogout}
            className="modal-button modal-button-secondary"
          >
            Sair Agora
          </button>
          <button
            onClick={onContinue}
            className="modal-button modal-button-primary"
          >
            Continuar Conectado
          </button>
        </div>

        {/* Informação adicional */}
        <div className="modal-info-section">
          <div className="modal-info-content">
            <UIIcons.Info size={14} className="modal-info-icon" />
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


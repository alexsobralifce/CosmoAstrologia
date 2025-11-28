import React, { useEffect, useState } from 'react';
import { UIIcons } from './ui-icons';
import { useLanguage } from '../i18n';

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
  const { language } = useLanguage();
  const [countdown, setCountdown] = useState(initialSeconds);
  
  // Traduções
  const texts = {
    title: {
      pt: 'Sessão Inativa',
      en: 'Inactive Session'
    },
    description: {
      pt: 'Sua sessão está prestes a expirar por inatividade',
      en: 'Your session is about to expire due to inactivity'
    },
    remainingTime: {
      pt: 'Tempo restante:',
      en: 'Time remaining:'
    },
    message: {
      pt: 'Clique em "Continuar Conectado" para permanecer na sua sessão.',
      en: 'Click "Stay Connected" to remain in your session.'
    },
    logoutNow: {
      pt: 'Sair Agora',
      en: 'Logout Now'
    },
    stayConnected: {
      pt: 'Continuar Conectado',
      en: 'Stay Connected'
    },
    infoText: {
      pt: 'Por segurança, encerramos sessões inativas após 10 minutos. Isso ajuda a proteger suas informações pessoais.',
      en: 'For security purposes, we end inactive sessions after 10 minutes. This helps protect your personal information.'
    }
  };

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
            {texts.title[language]}
          </h2>
          <p className="modal-description">
            {texts.description[language]}
          </p>
        </div>

        {/* Countdown */}
        <div className="modal-countdown-container">
          <p className="modal-countdown-label">
            {texts.remainingTime[language]}
          </p>
          <div className="modal-countdown-time">
            {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
          </div>
        </div>

        {/* Mensagem */}
        <p className="modal-message">
          {texts.message[language]}
        </p>

        {/* Botões */}
        <div className="modal-footer">
          <button
            onClick={onLogout}
            className="modal-button modal-button-secondary"
          >
            {texts.logoutNow[language]}
          </button>
          <button
            onClick={onContinue}
            className="modal-button modal-button-primary"
          >
            {texts.stayConnected[language]}
          </button>
        </div>

        {/* Informação adicional */}
        <div className="modal-info-section">
          <div className="modal-info-content">
            <UIIcons.Info size={14} className="modal-info-icon" />
            <p>
              {texts.infoText[language]}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};


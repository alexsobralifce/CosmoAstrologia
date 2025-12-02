import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { AstroButton } from './astro-button';
import { AstroInput } from './astro-input';
import { AstroCard } from './astro-card';
import { UIIcons } from './ui-icons';
import { useLanguage } from '../i18n';
import { toast } from 'sonner';
import '../styles/login-page.css';

interface EmailVerificationModalProps {
  isOpen: boolean;
  email: string;
  onVerify: (code: string) => Promise<void>;
  onResend: () => Promise<void>;
  onCancel: () => void;
}

export const EmailVerificationModal: React.FC<EmailVerificationModalProps> = ({
  isOpen,
  email,
  onVerify,
  onResend,
  onCancel,
}) => {
  const { language, t } = useLanguage();
  const [code, setCode] = useState('');
  const [timeLeft, setTimeLeft] = useState(60); // 1 minuto
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setCode('');
      setTimeLeft(60);
      return;
    }

    // Contador regressivo
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [isOpen, timeLeft]);

  const handleVerify = async () => {
    if (code.length !== 6) {
      toast.error(
        language === 'pt' ? 'Código inválido' : 'Invalid code',
        {
          description: language === 'pt' 
            ? 'Digite um código de 6 dígitos' 
            : 'Enter a 6-digit code',
        }
      );
      return;
    }

    setIsLoading(true);
    try {
      await onVerify(code);
    } catch (error) {
      // Erro já tratado no onVerify
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setIsResending(true);
    try {
      await onResend();
      setTimeLeft(60); // Reiniciar contador
      setCode('');
      toast.success(
        language === 'pt' ? 'Código reenviado!' : 'Code resent!',
        {
          description: language === 'pt'
            ? 'Verifique seu email novamente'
            : 'Check your email again',
        }
      );
    } catch (error) {
      // Erro já tratado no onResend
    } finally {
      setIsResending(false);
    }
  };

  const handleCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
    setCode(value);
  };

  if (!isOpen) return null;

  const texts = {
    title: {
      pt: 'Verifique seu email',
      en: 'Verify your email',
    },
    description: {
      pt: `Enviamos um código de verificação para ${email}`,
      en: `We sent a verification code to ${email}`,
    },
    codeLabel: {
      pt: 'Código de verificação',
      en: 'Verification code',
    },
    codePlaceholder: {
      pt: '000000',
      en: '000000',
    },
    timeLeft: {
      pt: 'Tempo restante',
      en: 'Time remaining',
    },
    verify: {
      pt: 'Verificar',
      en: 'Verify',
    },
    resend: {
      pt: 'Reenviar código',
      en: 'Resend code',
    },
    cancel: {
      pt: 'Cancelar',
      en: 'Cancel',
    },
    verifying: {
      pt: 'Verificando...',
      en: 'Verifying...',
    },
    resending: {
      pt: 'Reenviando...',
      en: 'Resending...',
    },
  };

  return createPortal(
    <div className="modal-overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 10000,
    }}>
      <AstroCard className="verification-modal" style={{
        maxWidth: '500px',
        width: '90%',
        padding: '2rem',
      }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <UIIcons.Mail size={48} style={{ marginBottom: '1rem', opacity: 0.8 }} />
          <h2 style={{ marginBottom: '0.5rem' }}>{texts.title[language]}</h2>
          <p style={{ opacity: 0.8, fontSize: '0.9rem' }}>{texts.description[language]}</p>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 500 }}>
            {texts.codeLabel[language]}
          </label>
          <AstroInput
            type="text"
            value={code}
            onChange={handleCodeChange}
            placeholder={texts.codePlaceholder[language]}
            maxLength={6}
            style={{
              textAlign: 'center',
              fontSize: '1.5rem',
              letterSpacing: '0.5rem',
              fontFamily: 'monospace',
              width: '100%',
            }}
            disabled={isLoading || isResending}
          />
        </div>

        <div style={{ 
          textAlign: 'center', 
          marginBottom: '1.5rem',
          padding: '1rem',
          backgroundColor: 'rgba(0, 0, 0, 0.1)',
          borderRadius: '8px',
        }}>
          {timeLeft > 0 ? (
            <p style={{ margin: 0, fontSize: '0.9rem' }}>
              {texts.timeLeft[language]}: <strong>{timeLeft}s</strong>
            </p>
          ) : (
            <AstroButton
              onClick={handleResend}
              disabled={isResending}
              variant="outline"
              size="sm"
            >
              {isResending ? texts.resending[language] : texts.resend[language]}
            </AstroButton>
          )}
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <AstroButton
            onClick={handleVerify}
            disabled={code.length !== 6 || isLoading || isResending}
            style={{ flex: 1 }}
          >
            {isLoading ? texts.verifying[language] : texts.verify[language]}
          </AstroButton>
          <AstroButton
            onClick={onCancel}
            disabled={isLoading || isResending}
            variant="outline"
            style={{ flex: 1 }}
          >
            {texts.cancel[language]}
          </AstroButton>
        </div>
      </AstroCard>
    </div>,
    document.body
  );
};


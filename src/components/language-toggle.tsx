import React from 'react';
import { useLanguage } from '../i18n';

interface LanguageToggleProps {
  className?: string;
  variant?: 'flag' | 'text';
}

export const LanguageToggle = ({ className = '', variant = 'flag' }: LanguageToggleProps) => {
  const { language, toggleLanguage } = useLanguage();

  return (
    <button
      onClick={toggleLanguage}
      className={`
        flex items-center justify-center
        w-9 h-9 rounded-lg
        bg-muted/50 hover:bg-muted border border-border/50
        transition-all duration-200 hover:border-primary/30 hover:scale-105
        ${className}
      `}
      title={language === 'pt' ? 'Switch to English' : 'Mudar para Português'}
      aria-label={language === 'pt' ? 'Switch to English' : 'Mudar para Português'}
    >
      {variant === 'flag' ? (
        <span className="text-lg leading-none">
          {language === 'pt' ? '🇧🇷' : '🇺🇸'}
        </span>
      ) : (
        <span className="text-xs font-bold text-foreground">
          {language === 'pt' ? 'PT' : 'EN'}
        </span>
      )}
    </button>
  );
};

// Versão ainda mais compacta (só bandeira, sem borda)
export const LanguageToggleMini = ({ className = '' }: { className?: string }) => {
  const { language, toggleLanguage } = useLanguage();

  return (
    <button
      onClick={toggleLanguage}
      className={`
        flex items-center justify-center
        w-8 h-8 rounded-md
        hover:bg-muted/50 transition-all duration-200 hover:scale-110
        ${className}
      `}
      title={language === 'pt' ? 'Switch to English' : 'Mudar para Português'}
      aria-label={language === 'pt' ? 'Switch to English' : 'Mudar para Português'}
    >
      <span className="text-base leading-none">
        {language === 'pt' ? '🇧🇷' : '🇺🇸'}
      </span>
    </button>
  );
};

'use client';

import React from 'react';
import { useLanguage } from '../i18n';
import '../styles/controls.css';

interface LanguageToggleProps {
  className?: string;
  variant?: 'flag' | 'text';
}

export const LanguageToggle = ({ className = '', variant = 'flag' }: LanguageToggleProps) => {
  const { language, toggleLanguage } = useLanguage();

  return (
    <div
      onClick={toggleLanguage}
      className={`language-toggle-container ${className}`}
      data-language={language}
      title={language === 'pt' ? 'Switch to English' : 'Mudar para Português'}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggleLanguage();
        }
      }}
      aria-label={language === 'pt' ? 'Switch to English' : 'Mudar para Português'}
    >
      <div className="language-toggle-indicator"></div>
      <div className={`language-toggle-flag ${language === 'pt' ? 'active' : ''}`}>
        <span>🇧🇷</span>
      </div>
      <div className={`language-toggle-flag ${language === 'en' ? 'active' : ''}`}>
        <span>🇺🇸</span>
      </div>
    </div>
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

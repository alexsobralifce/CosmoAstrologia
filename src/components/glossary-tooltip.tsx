'use client';

import React, { useState, useRef, useEffect } from 'react';
import { getGlossaryTerm } from '../utils/astrologicalGlossary';
import { useLanguage } from '../i18n';
import { UIIcons } from './ui-icons';

interface GlossaryTooltipProps {
  term: string;
  children: React.ReactNode;
  className?: string;
  showOnHover?: boolean;
  showOnClick?: boolean;
}

export const GlossaryTooltip: React.FC<GlossaryTooltipProps> = ({
  term,
  children,
  className = '',
  showOnHover = true,
  showOnClick = false,
}) => {
  const { language } = useLanguage();
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const tooltipRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLSpanElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const glossaryTerm = getGlossaryTerm(term, language);

  // Se não encontrar o termo, renderiza o children normalmente
  if (!glossaryTerm) {
    return <span className={className}>{children}</span>;
  }

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const handleMouseEnter = () => {
    if (showOnHover) {
      setIsVisible(true);
      // Pequeno delay para garantir que o DOM está atualizado
      setTimeout(() => {
        updatePosition();
      }, 10);
    }
  };

  const handleMouseLeave = () => {
    if (showOnHover) {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => {
        setIsVisible(false);
      }, 200);
    }
  };

  const handleClick = (e: React.MouseEvent) => {
    if (showOnClick) {
      e.preventDefault();
      e.stopPropagation();
      updatePosition();
      setIsVisible(!isVisible);
    }
  };

  const updatePosition = () => {
    if (triggerRef.current && tooltipRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      let left = rect.left + rect.width / 2 - tooltipRect.width / 2;
      let top = rect.bottom + 10;

      // Ajustar se sair da tela à direita
      if (left + tooltipRect.width > viewportWidth - 10) {
        left = viewportWidth - tooltipRect.width - 10;
      }

      // Ajustar se sair da tela à esquerda
      if (left < 10) {
        left = 10;
      }

      // Se não couber embaixo, mostrar em cima
      if (top + tooltipRect.height > viewportHeight - 10) {
        top = rect.top - tooltipRect.height - 10;
      }

      setPosition({ top, left });
    }
  };

  useEffect(() => {
    if (isVisible && tooltipRef.current && triggerRef.current) {
      // Usar requestAnimationFrame para garantir que o DOM está atualizado
      requestAnimationFrame(() => {
        updatePosition();
      });
    }
  }, [isVisible]);

  return (
    <span
      ref={triggerRef}
      className={`glossary-term ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
      style={{ cursor: showOnClick || showOnHover ? 'help' : 'default' }}
    >
      {children}
      {isVisible && (
        <div
          ref={tooltipRef}
          className="glossary-tooltip"
          style={{
            position: 'fixed',
            top: `${position.top}px`,
            left: `${position.left}px`,
            zIndex: 9999,
          }}
          onMouseEnter={() => {
            if (timeoutRef.current) {
              clearTimeout(timeoutRef.current);
            }
          }}
          onMouseLeave={handleMouseLeave}
        >
          <div className="glossary-tooltip-header">
            <div className="glossary-tooltip-icon">
              <UIIcons.Info size={16} />
            </div>
            <h4 className="glossary-tooltip-title">{glossaryTerm.term}</h4>
            {showOnClick && (
              <button
                className="glossary-tooltip-close"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setIsVisible(false);
                }}
              >
                ×
              </button>
            )}
          </div>
          <p className="glossary-tooltip-content">{glossaryTerm.explanation}</p>
        </div>
      )}
    </span>
  );
};

// Componente para destacar termos técnicos em um texto
interface HighlightGlossaryTermsProps {
  text: string;
  className?: string;
}

export const HighlightGlossaryTerms: React.FC<HighlightGlossaryTermsProps> = ({
  text,
  className = '',
}) => {
  const { language } = useLanguage();
  
  // Lista de termos para destacar (em ordem de tamanho, do maior para o menor)
  const terms = language === 'pt' 
    ? [
        'Regente do Mapa',
        'Tríade Fundamental',
        'Casas Astrológicas',
        'Nodo Norte',
        'Nodo Sul',
        'Ascendente',
        'Signo Solar',
        'Signo Lunar',
        'Quadratura',
        'Conjunção',
        'Oposição',
        'Sextil',
        'Trígono',
        'Exaltação',
        'Regência',
        'Quíron',
        'Lilith',
      ]
    : [
        'Chart Ruler',
        'Fundamental Triad',
        'Astrological Houses',
        'North Node',
        'South Node',
        'Ascendant',
        'Sun Sign',
        'Moon Sign',
        'Square',
        'Conjunction',
        'Opposition',
        'Sextile',
        'Trine',
        'Exaltation',
        'Rulership',
        'Chiron',
        'Lilith',
      ];

  let processedText = text;

  // Substituir termos por componentes com tooltip
  terms.forEach((term) => {
    const regex = new RegExp(`\\b${term}\\b`, 'gi');
    processedText = processedText.replace(regex, `{{GLOSSARY:${term}}}`);
  });

  // Dividir o texto em partes
  const parts = processedText.split(/(\{\{GLOSSARY:[^}]+\}\})/);

  return (
    <span className={className}>
      {parts.map((part, index) => {
        const match = part.match(/^\{\{GLOSSARY:(.+)\}\}$/);
        if (match) {
          const term = match[1];
          return (
            <GlossaryTooltip key={index} term={term} showOnHover={true}>
              <span className="glossary-term-highlight">{term}</span>
            </GlossaryTooltip>
          );
        }
        return <React.Fragment key={index}>{part}</React.Fragment>;
      })}
    </span>
  );
};


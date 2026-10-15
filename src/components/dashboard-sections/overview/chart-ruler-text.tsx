import React from 'react';
import { InlineBold } from '../../ui/inline-bold';

/** Organiza o texto da LLM em tópicos (numerados, bullets, títulos e parágrafos). */
export const ChartRulerText = ({ text }: { text: string }) => {
  if (!text) return null;

  // Dividir o texto em parágrafos
  const paragraphs = text.split('\n').filter(p => p.trim());
  
  // Identificar tópicos (números, bullets, títulos em negrito, etc.)
  const formattedParagraphs: React.ReactNode[] = [];
  
  paragraphs.forEach((paragraph, index) => {
    const trimmed = paragraph.trim();
    if (!trimmed) return;

    // Verificar se é um tópico numerado (1., 2., etc.)
    const numberedMatch = trimmed.match(/^(\d+)[\.\)]\s*(.+)$/);
    // Verificar se é um bullet (-, •, etc.)
    const bulletMatch = trimmed.match(/^[-•*]\s*(.+)$/);
    // Verificar se é um título (texto em negrito ou em maiúsculas curtas)
    const titleMatch = trimmed.match(/^([A-ZÁÊÇ][A-ZÁÊÇ\s]{2,30}):?\s*$/);
    // Verificar se contém texto em negrito (markdown **texto**)
    const boldMatch = trimmed.match(/\*\*(.+?)\*\*/);

    if (numberedMatch) {
      // Tópico numerado
      formattedParagraphs.push(
        <div key={index} className="overview-chart-ruler-numbered">
          <p className="overview-chart-ruler-content">
            <span className="overview-chart-ruler-number">{numberedMatch[1]}.</span> {numberedMatch[2]}
          </p>
        </div>
      );
    } else if (bulletMatch) {
      // Tópico com bullet
      formattedParagraphs.push(
        <div key={index} className="overview-chart-ruler-bullet">
          <p className="overview-chart-ruler-content">
            <span className="overview-chart-ruler-bullet-marker">•</span> {bulletMatch[1]}
          </p>
        </div>
      );
    } else if (boldMatch || (titleMatch && trimmed.length < 50)) {
      // Título ou texto em negrito
              formattedParagraphs.push(
        <div key={index}>
          <p className="overview-chart-ruler-heading"><InlineBold text={trimmed} /></p>
        </div>
      );
    } else {
      // Parágrafo normal
      formattedParagraphs.push(
        <div key={index} className="overview-chart-ruler-paragraph">
          <p className="overview-chart-ruler-content">{trimmed}</p>
        </div>
      );
    }
  });

  return <div>{formattedParagraphs}</div>;
};

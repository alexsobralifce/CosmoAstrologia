import React from 'react';

/**
 * Formata textos vindos do Groq removendo asteriscos de títulos
 * e organizando o conteúdo de forma elegante e justificada
 */
export const formatGroqText = (text: string): React.ReactNode => {
  if (!text) return null;

  // Dividir em parágrafos
  const paragraphs = text.split(/\n\n+/).filter(p => p.trim());
  const formattedElements: React.ReactNode[] = [];

  paragraphs.forEach((paragraph, index) => {
    let cleaned = paragraph.trim();
    
    // Remover conteúdo de suporte
    cleaned = cleaned.replace(/##?\s*📞\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/##?\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/Para dúvidas sobre interpretação astrológica[\s\S]*?Consulta com astrólogo profissional[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/Livros de astrologia na pasta.*?/gi, '');
    cleaned = cleaned.replace(/Análise com IA.*?/gi, '');
    cleaned = cleaned.replace(/Consulta com astrólogo profissional.*?/gi, '');
    cleaned = cleaned.replace(/Desenvolvido com.*?autoconhecimento profundo[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/^[-]{3,}$/gm, '');
    
    if (!cleaned.trim()) return;

    // Remover TODOS os asteriscos do texto (negrito, itálico, etc.)
    // Primeiro, remover markdown de negrito **texto**
    cleaned = cleaned.replace(/\*\*([^*]+?)\*\*/g, '$1');
    // Depois, remover markdown de itálico *texto* (mas não se for bullet point)
    cleaned = cleaned.replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '$1');
    // Remover asteriscos soltos no início e fim
    cleaned = cleaned.replace(/^\*+\s*|\s*\*+$/g, '');
    // Remover asteriscos múltiplos consecutivos
    cleaned = cleaned.replace(/\*{2,}/g, '');
    // Limpar espaços extras que possam ter ficado
    cleaned = cleaned.trim();

    // Detectar se é um título (linha curta sem ponto final, não começa com minúscula)
    const isTitle = cleaned.length < 80 && 
                    !cleaned.includes('.') && 
                    !cleaned.match(/^[a-záàâãéêíóôõúç]/) &&
                    cleaned.length > 0;
    
    if (isTitle) {
      // É um título - formatar elegantemente
      formattedElements.push(
        <h4 key={index} className="groq-formatted-title">
          {cleaned}
        </h4>
      );
    } else {
      // Parágrafo normal - justificar
      if (cleaned) {
        formattedElements.push(
          <p key={index} className="groq-formatted-paragraph">
            {cleaned}
          </p>
        );
      }
    }
  });

  return <div className="groq-formatted-container">{formattedElements}</div>;
};

/**
 * Formata texto simples (sem estrutura de títulos) removendo todos os asteriscos
 */
export const formatGroqParagraph = (text: string): string => {
  if (!text) return '';
  
  let cleaned = text;
  // Remover markdown de negrito **texto**
  cleaned = cleaned.replace(/\*\*([^*]+?)\*\*/g, '$1');
  // Remover markdown de itálico *texto* (mas não se for bullet point)
  cleaned = cleaned.replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, '$1');
  // Remover asteriscos soltos no início e fim
  cleaned = cleaned.replace(/^\*+\s*|\s*\*+$/g, '');
  // Remover asteriscos múltiplos consecutivos
  cleaned = cleaned.replace(/\*{2,}/g, '');
  
  return cleaned.trim();
};


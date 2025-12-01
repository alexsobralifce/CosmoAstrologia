/**
 * Formata conteúdo de seções especiais (triad e power) removendo repetições,
 * parágrafos genéricos e organizando o conteúdo de forma complementar.
 * Esta função garante consistência entre o que é exibido na tela e no PDF.
 */
export const formatTriadContent = (content: string): string => {
  // Dividir em parágrafos
  const paragraphs = content.split('\n\n').map(p => p.trim()).filter(p => p.length > 0);
  
  // Remover informações de suporte primeiro
  let cleanedParagraphs = paragraphs.map(p => {
    let cleaned = p;
    cleaned = cleaned.replace(/##?\s*📞\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/##?\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/Para dúvidas sobre interpretação astrológica[\s\S]*?Consulta com astrólogo profissional[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/Livros de astrologia na pasta.*?/gi, '');
    cleaned = cleaned.replace(/Análise com IA.*?/gi, '');
    cleaned = cleaned.replace(/Consulta com astrólogo profissional.*?/gi, '');
    cleaned = cleaned.replace(/Desenvolvido com.*?autoconhecimento profundo[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/^[-]{3,}$/gm, '');
    return cleaned.trim();
  }).filter(p => p.length > 0);
  
  // Detectar repetições e remover
  const uniqueParagraphs: string[] = [];
  const seenConcepts = new Set<string>();
  
  for (const paragraph of cleanedParagraphs) {
    // Extrair conceitos principais do parágrafo
    const concepts = paragraph.toLowerCase().match(/\b(sol|lua|ascendente|sun|moon|ascendant|essência|essence|emoção|emotion|máscara|mask|identidade|identity|necessidade|need)\b/gi) || [];
    
    // Verificar se este parágrafo já foi visto (conteúdo similar)
    let isDuplicate = false;
    const paragraphKey = concepts.join('|').toLowerCase();
    
    // Verificar similaridade de conteúdo (palavras-chave repetidas)
    if (seenConcepts.has(paragraphKey)) {
      // Verificar se é uma variação do mesmo conceito
      const paragraphWords = paragraph.toLowerCase().split(/\s+/).filter(w => w.length > 4);
      for (const seenPara of uniqueParagraphs) {
        const seenWords = seenPara.toLowerCase().split(/\s+/).filter(w => w.length > 4);
        const commonWords = paragraphWords.filter(w => seenWords.includes(w));
        // Se mais de 40% das palavras são comuns e falam da mesma coisa, é duplicata
        if (commonWords.length > Math.max(paragraphWords.length, seenWords.length) * 0.4) {
          // Verificar se falam dos mesmos conceitos
          const commonConcepts = concepts.filter(c => 
            seenPara.toLowerCase().includes(c.toLowerCase())
          );
          if (commonConcepts.length >= 2) {
            isDuplicate = true;
            break;
          }
        }
      }
    }
    
    // Se não é duplicata, adicionar
    if (!isDuplicate) {
      uniqueParagraphs.push(paragraph);
      seenConcepts.add(paragraphKey);
    }
  }
  
  // Remover parágrafos muito genéricos que não agregam valor
  const meaningfulParagraphs = uniqueParagraphs.filter(p => {
    // Remover parágrafos muito curtos ou genéricos
    if (p.length < 50) return false;
    
    // Remover parágrafos que são apenas definições genéricas
    const genericPhrases = [
      /^o sol é/i,
      /^a lua é/i,
      /^o ascendente é/i,
      /^o sol representa/i,
      /^a lua representa/i,
      /^o ascendente representa/i,
      /^quando o sol/i,
      /^quando a lua/i,
      /^quando o ascendente/i,
    ];
    
    return !genericPhrases.some(pattern => pattern.test(p));
  });
  
  // Reorganizar para garantir complementaridade
  // Agrupar por tema (Sol, Lua, Ascendente, Interação)
  const solParagraphs: string[] = [];
  const luaParagraphs: string[] = [];
  const ascParagraphs: string[] = [];
  const interactionParagraphs: string[] = [];
  
  meaningfulParagraphs.forEach(p => {
    const hasSol = /\b(sol|sun)\b/i.test(p);
    const hasLua = /\b(lua|moon)\b/i.test(p);
    const hasAsc = /\b(ascendente|ascendant)\b/i.test(p);
    
    // Se menciona interação entre os três, priorizar
    if (hasSol && hasLua && hasAsc) {
      interactionParagraphs.push(p);
    } else if (hasSol && hasLua) {
      interactionParagraphs.push(p);
    } else if (hasSol && hasAsc) {
      interactionParagraphs.push(p);
    } else if (hasLua && hasAsc) {
      interactionParagraphs.push(p);
    } else if (hasSol && !hasLua && !hasAsc) {
      solParagraphs.push(p);
    } else if (hasLua && !hasSol && !hasAsc) {
      luaParagraphs.push(p);
    } else if (hasAsc && !hasSol && !hasLua) {
      ascParagraphs.push(p);
    } else {
      // Parágrafos gerais ou de síntese
      interactionParagraphs.push(p);
    }
  });
  
  // Combinar de forma complementar: interações primeiro, depois individuais
  const finalParagraphs = [
    ...interactionParagraphs,
    ...solParagraphs.slice(0, 1), // Limitar a 1 parágrafo por planeta individual
    ...luaParagraphs.slice(0, 1),
    ...ascParagraphs.slice(0, 1),
  ];
  
  // Garantir que temos pelo menos 2 parágrafos
  if (finalParagraphs.length < 2 && meaningfulParagraphs.length >= 2) {
    return meaningfulParagraphs.join('\n\n');
  }
  
  return finalParagraphs.join('\n\n');
};


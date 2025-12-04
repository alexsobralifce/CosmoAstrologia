import React from 'react';
import { PlanetaryDignitiesVisual, extractDignitiesFromText } from '../components/planetary-dignities-visual';
import { AspectsVisual, extractAspectsFromText } from '../components/aspects-visual';

/**
 * Remove títulos duplicados de planetas do início do texto
 * Isso evita duplicação já que o título já aparece no cabeçalho
 */
export const removeDuplicatePlanetTitle = (text: string, planetName?: string, sign?: string): string => {
  if (!text) return text;
  
  let cleaned = text;
  
  // Se temos o nome do planeta e signo específicos, criar padrão mais preciso
  if (planetName && sign) {
    // Remover linha que começa exatamente com o planeta e signo (com ou sem graus)
    const planetEscaped = planetName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const signEscaped = sign.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    
    // Padrão: "Sol em Libra" ou "Sol em Libra 27° 11' 30"" ou "Sol em Libra • Oitava Casa"
    // Remover tanto no início do texto quanto no início de parágrafos (após quebra de linha)
    const patterns = [
      // No início do texto ou após quebra de linha
      new RegExp(`(^|\\n)\\s*${planetEscaped}\\s+em\\s+${signEscaped}(?:\\s+\\d+[°º]\\s*\\d+['′]?\\s*\\d*["″]?)?(?:\\s*•\\s*[\\wÀ-ÿ\\s]+)?\\s*(?=\\n|$)`, 'gmi'),
      // Versão mais simples sem graus
      new RegExp(`(^|\\n)\\s*${planetEscaped}\\s+em\\s+${signEscaped}\\s*(?=\\n|$)`, 'gmi'),
    ];
    
    patterns.forEach(pattern => {
      cleaned = cleaned.replace(pattern, '$1'); // Mantém apenas a quebra de linha, remove o título
    });
  }
  
  // Limpeza genérica para qualquer planeta (fallback) - também no início ou após quebra de linha
  cleaned = cleaned.replace(/(^|\n)\s*(Sol|Lua|Mercúrio|Vênus|Marte|Júpiter|Saturno|Urano|Netuno|Plutão|Ascendente|Meio do Céu|Nódulo Norte|Nódulo Sul|Quíron)\s+em\s+[\wÀ-ÿ]+(?:\s+\d+[°º]\s*\d+['′]?\s*\d*["″]?)?(?:\s*•\s*[\wÀ-ÿ\s]+)?\s*(?=\n|$)/gmi, '$1');
  cleaned = cleaned.replace(/(^|\n)\s*(Sol|Lua|Mercúrio|Vênus|Marte|Júpiter|Saturno|Urano|Netuno|Plutão|Ascendente|Meio do Céu|Nódulo Norte|Nódulo Sul|Quíron)\s+em\s+[\wÀ-ÿ]+\s*(?=\n|$)/gmi, '$1');
  
  // Limpar linhas vazias no início e múltiplas quebras de linha consecutivas
  cleaned = cleaned.replace(/^\n+/, '').replace(/\n{3,}/g, '\n\n').trim();
  
  return cleaned;
};

/**
 * Formata textos vindos do Groq removendo asteriscos de títulos
 * e organizando o conteúdo de forma elegante e justificada
 */
export const formatGroqText = (text: string, language?: string, planetName?: string, sign?: string): React.ReactNode => {
  if (!text) return null;

  // Extrair dignidades e aspectos do texto completo
  const dignities = extractDignitiesFromText(text);
  const aspects = extractAspectsFromText(text);
  const hasDignities = dignities.length > 0;
  const hasAspects = aspects.length > 0;

  // Pré-processar texto para remover seções de dignidades e aspectos ANTES de dividir em parágrafos
  let processedText = text;
  
  // Remover títulos duplicados de planetas no início da interpretação
  processedText = removeDuplicatePlanetTitle(processedText, planetName, sign);
  
  if (hasDignities) {
    // Remover seção completa de dignidades planetárias (com título e emojis)
    processedText = processedText.replace(/🌟\s*DIGNIDADES\s*PLANETÁRIAS[\s\S]*?(?=\n\n|🌟|$)/gi, '');
    processedText = processedText.replace(/DIGNIDADES\s*PLANETÁRIAS[\s\S]*?(?=\n\n|🌟|$)/gi, '');
    processedText = processedText.replace(/DIGNIDADES[\s\S]*?PLANETÁRIAS[\s\S]*?(?=\n\n|🌟|$)/gi, '');
    
    // Remover linhas individuais de dignidades - padrões mais abrangentes
    // Usar padrão mais flexível que captura qualquer palavra (incluindo acentos)
    // Padrão 1: "* Lua em Leão: PEREGRINO" (com asterisco)
    processedText = processedText.replace(/^\s*\*\s+[\wÀ-ÿ]+\s+em\s+[\wÀ-ÿ]+:\s+(QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$/gmi, '');
    // Padrão 2: "- Lua em Leão: PEREGRINO" (com hífen)
    processedText = processedText.replace(/^\s*-\s+[\wÀ-ÿ]+\s+em\s+[\wÀ-ÿ]+:\s+(QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$/gmi, '');
    // Padrão 3: "Lua em Leão: PEREGRINO" (sem marcador)
    processedText = processedText.replace(/^\s*[\wÀ-ÿ]+\s+em\s+[\wÀ-ÿ]+:\s+(QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$/gmi, '');
    
    // Remover blocos completos de dignidades (múltiplas linhas consecutivas)
    processedText = processedText.replace(/(?:^\s*[-*]\s+[\wÀ-ÿ]+\s+em\s+[\wÀ-ÿ]+:\s+(?:QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$\n?)+/gmi, '');
    processedText = processedText.replace(/(?:^\s*[\wÀ-ÿ]+\s+em\s+[\wÀ-ÿ]+:\s+(?:QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$\n?)+/gmi, '');
    
    // Limpar linhas vazias extras que possam ter sido criadas
    processedText = processedText.replace(/\n{3,}/g, '\n\n');
  }

  // Remover seções de aspectos
  if (hasAspects) {
    // Remover seção completa de aspectos (com título)
    processedText = processedText.replace(/ASPECTOS[\s\S]*?(?=\n\n|🌟|$)/gi, '');
    processedText = processedText.replace(/🌟\s*ASPECTOS[\s\S]*?(?=\n\n|🌟|$)/gi, '');
    
    // Remover linhas individuais de aspectos
    // Padrão 1: "* Sextil Sol-Lua" (com asterisco)
    processedText = processedText.replace(/^\s*[-*]\s+(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+-[\wÀ-ÿ]+\s*$/gmi, '');
    // Padrão 2: "Sextil Sol-Lua" (sem marcador)
    processedText = processedText.replace(/^\s*(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+-[\wÀ-ÿ]+\s*$/gmi, '');
    
    // Remover blocos completos de aspectos (múltiplas linhas consecutivas)
    processedText = processedText.replace(/(?:^\s*[-*]\s+(?:Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+-[\wÀ-ÿ]+\s*$\n?)+/gmi, '');
    processedText = processedText.replace(/(?:^\s*(?:Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+-[\wÀ-ÿ]+\s*$\n?)+/gmi, '');
    
    // Limpar linhas vazias extras
    processedText = processedText.replace(/\n{3,}/g, '\n\n');
  }

  // Remover informações duplicadas que não devem aparecer em nenhuma seção
  // Dados de nascimento
  processedText = processedText.replace(/MAPA ASTRAL DE[\s\S]*?DADOS DE NASCIMENTO[\s\S]*?(?=\n\n|LUMINARES|TEMPERAMENTO|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  processedText = processedText.replace(/DADOS DE NASCIMENTO[\s\S]*?(?=\n\n|LUMINARES|TEMPERAMENTO|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  processedText = processedText.replace(/Data:[\s\S]*?Local:[\s\S]*?(?=\n\n|LUMINARES|TEMPERAMENTO|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  
  // Luminares e planetas pessoais
  processedText = processedText.replace(/LUMINARES E PLANETAS PESSOAIS[\s\S]*?(?=\n\n|TEMPERAMENTO|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  
  // Temperamento
  processedText = processedText.replace(/TEMPERAMENTO[\s\S]*?elemento dominante[\s\S]*?(?=\n\n|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  processedText = processedText.replace(/O mapa apresenta predominância[\s\S]*?elemento dominante[\s\S]*?(?=\n\n|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  
  // Regente do mapa
  processedText = processedText.replace(/REGENTE DO MAPA[\s\S]*?(?=\n\n|DIGNIDADES|ASPECTOS|$)/gi, '');
  
  // Remover conteúdo técnico de dados pré-calculados
  processedText = processedText.replace(/CONTRIBUIÇÃO DE CADA PLANETA[\s\S]*?(?=\n\n|🔒|⚠️|📊|🔗|$)/gi, '');
  // Remover linhas individuais de contribuição de planetas (formato: Sol/Sun em Libra (Ar): 3 pontos)
  processedText = processedText.replace(/^\s*[\wÀ-ÿ\/]+\s+em\s+[\wÀ-ÿ]+\s+\([\wÀ-ÿ]+\):\s+\d+\s+pontos?\s*$/gmi, '');
  processedText = processedText.replace(/🔒\s*DADOS PRÉ-CALCULADOS[\s\S]*?(?=\n\n|⚠️|📊|🔗|$)/gi, '');
  processedText = processedText.replace(/⚠️\s*INSTRUÇÃO CRÍTICA PARA A IA[\s\S]*?(?=\n\n|⚠️|📊|🔗|$)/gi, '');
  processedText = processedText.replace(/⚠️⚠️⚠️\s*VALIDAÇÃO OBRIGATÓRIA[\s\S]*?(?=\n\n|⚠️|📊|🔗|$)/gi, '');
  processedText = processedText.replace(/📊[\s\S]*?(?=\n\n|🔗|⚠️|$)/gi, '');
  processedText = processedText.replace(/🔗\s*ASPECTOS VALIDADOS[\s\S]*?(?=\n\n|LISTA|⚠️|$)/gi, '');
  processedText = processedText.replace(/LISTA COMPLETA DE ASPECTOS[\s\S]*?(?=\n\n|$)/gi, '');
  
  // Remover listas de aspectos individuais (formato: • Sol Sextil Lua, etc.)
  processedText = processedText.replace(/^\s*[•·]\s*[\wÀ-ÿ]+\s+(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+[\s\S]*?distância:[\s\S]*?°\)\s*$/gmi, '');
  processedText = processedText.replace(/^\s*[•·]\s*[\wÀ-ÿ]+\s+(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+\s*$/gmi, '');
  
  // Remover linhas com apenas emojis ou símbolos técnicos
  processedText = processedText.replace(/^[🔒⚠️📊🔗⭐🌟\s]+$/gm, '');
  
  // Remover separadores visuais (barras e linhas decorativas)
  processedText = processedText.replace(/[═─━┃│┊┋]{3,}/g, '');
  processedText = processedText.replace(/^[═─━┃│┊┋\s]+$/gm, '');
  
  // Remover linhas que são apenas traços, hífens ou caracteres de separação
  processedText = processedText.replace(/^[-─━─━\s]+$/gm, '');
  
  // Limpar linhas vazias extras novamente
  processedText = processedText.replace(/\n{3,}/g, '\n\n');

  // Dividir em parágrafos
  const paragraphs = processedText.split(/\n\n+/).filter(p => p.trim());
  const formattedElements: React.ReactNode[] = [];

  // Se há dignidades, adicionar o componente visual antes do conteúdo
  if (hasDignities) {
    formattedElements.push(
      <PlanetaryDignitiesVisual 
        key="dignities-visual" 
        dignities={dignities} 
        language={language || 'pt'} 
      />
    );
  }

  // Se há aspectos, adicionar o componente visual
  if (hasAspects) {
    formattedElements.push(
      <AspectsVisual 
        key="aspects-visual" 
        aspects={aspects} 
        language={language || 'pt'} 
      />
    );
  }

  paragraphs.forEach((paragraph, index) => {
    let cleaned = paragraph.trim();
    
    // Remover informações duplicadas que não devem aparecer na seção karma
    // Dados de nascimento
    cleaned = cleaned.replace(/DADOS DE NASCIMENTO[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/Data:[\s\S]*?Local:[\s\S]*?(?=\n\n|$)/gi, '');
    
    // Luminares e planetas pessoais
    cleaned = cleaned.replace(/LUMINARES E PLANETAS PESSOAIS[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/Sol:[\s\S]*?Marte:[\s\S]*?(?=\n\n|$)/gi, '');
    
    // Temperamento
    cleaned = cleaned.replace(/TEMPERAMENTO[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/O mapa apresenta predominância[\s\S]*?elemento dominante[\s\S]*?(?=\n\n|$)/gi, '');
    
    // Regente do mapa
    cleaned = cleaned.replace(/REGENTE DO MAPA[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/Ascendente:[\s\S]*?Regente:[\s\S]*?(?=\n\n|$)/gi, '');
    
    // Dignidades planetárias (já removidas anteriormente, mas garantir)
    cleaned = cleaned.replace(/DIGNIDADES PLANETÁRIAS[\s\S]*?(?=\n\n|$)/gi, '');
    
    // Remover conteúdo técnico de dados pré-calculados (garantir remoção em parágrafos individuais)
    cleaned = cleaned.replace(/CONTRIBUIÇÃO DE CADA PLANETA[\s\S]*?(?=\n\n|$)/gi, '');
    // Remover linhas individuais de contribuição de planetas
    cleaned = cleaned.replace(/^\s*[\wÀ-ÿ\/]+\s+em\s+[\wÀ-ÿ]+\s+\([\wÀ-ÿ]+\):\s+\d+\s+pontos?\s*$/gmi, '');
    cleaned = cleaned.replace(/🔒\s*DADOS PRÉ-CALCULADOS[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/⚠️\s*INSTRUÇÃO CRÍTICA PARA A IA[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/⚠️⚠️⚠️\s*VALIDAÇÃO OBRIGATÓRIA[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/📊[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/🔗\s*ASPECTOS VALIDADOS[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/LISTA COMPLETA DE ASPECTOS[\s\S]*?(?=\n\n|$)/gi, '');
    
    // Remover listas de aspectos individuais
    cleaned = cleaned.replace(/^\s*[•·]\s*[\wÀ-ÿ]+\s+(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+[\s\S]*?distância:[\s\S]*?°\)\s*$/gmi, '');
    cleaned = cleaned.replace(/^\s*[•·]\s*[\wÀ-ÿ]+\s+(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+\s*$/gmi, '');
    
    // Remover linhas com apenas emojis ou símbolos técnicos
    cleaned = cleaned.replace(/^[🔒⚠️📊🔗⭐🌟\s]+$/gm, '');
    
    // Remover conteúdo de suporte
    cleaned = cleaned.replace(/##?\s*📞\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/##?\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/Para dúvidas sobre interpretação astrológica[\s\S]*?Consulta com astrólogo profissional[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/Livros de astrologia na pasta.*?/gi, '');
    cleaned = cleaned.replace(/Análise com IA.*?/gi, '');
    cleaned = cleaned.replace(/Consulta com astrólogo profissional.*?/gi, '');
    cleaned = cleaned.replace(/Desenvolvido com.*?autoconhecimento profundo[\s\S]*?(?=\n\n|$)/gi, '');
    cleaned = cleaned.replace(/^[-]{3,}$/gm, '');
    
      // Remover separadores visuais (barras e linhas decorativas) do parágrafo
      cleaned = cleaned.replace(/[═─━┃│┊┋]{3,}/g, '');
      cleaned = cleaned.replace(/^[═─━┃│┊┋\s]+$/gm, '');
      
      // Remover linhas que são apenas traços, hífens ou caracteres de separação
      cleaned = cleaned.replace(/^[-─━─━\s]+$/gm, '');
    
    if (!cleaned.trim()) return;
      
      // Ignorar parágrafos que são apenas traços ou caracteres de separação
      if (/^[-─━─━\s]+$/.test(cleaned)) return;

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
    // Ignorar se for apenas traços, hífens ou caracteres de separação
    const isTitle = cleaned.length < 80 && 
                    !cleaned.includes('.') && 
                    !cleaned.match(/^[a-záàâãéêíóôõúç]/) &&
                    cleaned.length > 0 &&
                    !/^[-─━─━\s]+$/.test(cleaned) &&
                    cleaned.trim().length > 1; // Deve ter pelo menos 2 caracteres para ser um título válido
    
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


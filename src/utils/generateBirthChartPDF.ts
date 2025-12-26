import jsPDF from 'jspdf';
import { OnboardingData } from '../components/onboarding';
import { formatTriadContent } from './formatTriadContent';
import { getAllGlossaryTerms } from './astrologicalGlossary';

interface BirthChartSection {
  section: string;
  title: string;
  content: string;
  generated_by: string;
}

interface PlanetInSign {
  planet: string;
  planet_key: string;
  sign: string;
  degree: number;
  degree_dms: string;
  is_retrograde?: boolean; // Opcional para compatibilidade com API
  house: number;
}

interface SpecialPoint {
  point: string;
  point_key: string;
  sign: string;
  degree: number;
  degree_dms: string;
  house: number;
}

interface CompleteChartData {
  birth_data: {
    date: string;
    time: string;
    latitude: number;
    longitude: number;
  };
  planets_in_signs: PlanetInSign[];
  special_points: SpecialPoint[];
  planets_in_houses: Array<{
    house: number;
    planets: Array<{
      planet?: string;
      point?: string;
      planet_key?: string;
      point_key?: string;
      sign: string;
      degree: number;
      degree_dms: string;
      house: number;
      is_retrograde?: boolean;
    }>;
  }>;
}

interface GeneratePDFOptions {
  userData: OnboardingData;
  sections: Record<string, BirthChartSection | null>;
  language: 'pt' | 'en';
  chartData?: CompleteChartData | null; // Dados completos do mapa astral
}

// ===== CONFIGURAÇÕES PROFISSIONAIS =====
const PDF_CONFIG = {
  pageWidth: 210, // A4 width in mm
  pageHeight: 297, // A4 height in mm
  margin: {
    top: 20,
    bottom: 20,
    left: 20,
    right: 20,
    inner: 15, // Margem interna entre colunas (se houver)
  },
  lineHeight: {
    normal: 5.5,
    title: 8,
    subtitle: 6.5,
    small: 4.5,
  },
  fontSize: {
    h1: 20,
    h2: 16,
    h3: 14,
    body: 10,
    small: 8,
    tiny: 7,
  },
  colors: {
    primary: { r: 139, g: 92, b: 246 }, // Purple
    secondary: { r: 100, g: 100, b: 200 },
    text: { r: 30, g: 30, b: 30 },
    textLight: { r: 80, g: 80, b: 80 },
    textMuted: { r: 120, g: 120, b: 120 },
    border: { r: 200, g: 200, b: 200 },
    background: { r: 250, g: 250, b: 250 },
  },
};

// Função para limpar conteúdo técnico (mesma lógica do formatGroqText)
const cleanTechnicalContent = (text: string): string => {
  let processedText = text;
  
  // Remover informações duplicadas que não devem aparecer em nenhuma seção
  processedText = processedText.replace(/MAPA ASTRAL DE[\s\S]*?DADOS DE NASCIMENTO[\s\S]*?(?=\n\n|LUMINARES|TEMPERAMENTO|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  processedText = processedText.replace(/DADOS DE NASCIMENTO[\s\S]*?(?=\n\n|LUMINARES|TEMPERAMENTO|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  processedText = processedText.replace(/Data:[\s\S]*?Local:[\s\S]*?(?=\n\n|LUMINARES|TEMPERAMENTO|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  processedText = processedText.replace(/LUMINARES E PLANETAS PESSOAIS[\s\S]*?(?=\n\n|TEMPERAMENTO|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  processedText = processedText.replace(/TEMPERAMENTO[\s\S]*?elemento dominante[\s\S]*?(?=\n\n|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  processedText = processedText.replace(/O mapa apresenta predominância[\s\S]*?elemento dominante[\s\S]*?(?=\n\n|REGENTE|DIGNIDADES|ASPECTOS|$)/gi, '');
  processedText = processedText.replace(/REGENTE DO MAPA[\s\S]*?(?=\n\n|DIGNIDADES|ASPECTOS|$)/gi, '');
  
  // Remover conteúdo técnico de dados pré-calculados
  processedText = processedText.replace(/CONTRIBUIÇÃO DE CADA PLANETA[\s\S]*?(?=\n\n|🔒|⚠️|📊|🔗|$)/gi, '');
  processedText = processedText.replace(/^\s*[\wÀ-ÿ\/]+\s+em\s+[\wÀ-ÿ]+\s+\([\wÀ-ÿ]+\):\s+\d+\s+pontos?\s*$/gmi, '');
  processedText = processedText.replace(/🔒\s*DADOS PRÉ-CALCULADOS[\s\S]*?(?=\n\n|⚠️|📊|🔗|$)/gi, '');
  processedText = processedText.replace(/⚠️\s*INSTRUÇÃO CRÍTICA PARA A IA[\s\S]*?(?=\n\n|⚠️|📊|🔗|$)/gi, '');
  processedText = processedText.replace(/⚠️⚠️⚠️\s*VALIDAÇÃO OBRIGATÓRIA[\s\S]*?(?=\n\n|⚠️|📊|🔗|$)/gi, '');
  processedText = processedText.replace(/📊[\s\S]*?(?=\n\n|🔗|⚠️|$)/gi, '');
  processedText = processedText.replace(/🔗\s*ASPECTOS VALIDADOS[\s\S]*?(?=\n\n|LISTA|⚠️|$)/gi, '');
  processedText = processedText.replace(/LISTA COMPLETA DE ASPECTOS[\s\S]*?(?=\n\n|$)/gi, '');
  
  // Remover listas de aspectos individuais
  processedText = processedText.replace(/^\s*[•·]\s*[\wÀ-ÿ]+\s+(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+[\s\S]*?distância:[\s\S]*?°\)\s*$/gmi, '');
  processedText = processedText.replace(/^\s*[•·]\s*[\wÀ-ÿ]+\s+(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+\s*$/gmi, '');
  
  // Remover separadores visuais (barras e linhas decorativas)
  processedText = processedText.replace(/[═─━┃│┊┋]{3,}/g, '');
  processedText = processedText.replace(/^[═─━┃│┊┋\s]+$/gm, '');
  processedText = processedText.replace(/^[-─━─━\s]+$/gm, '');
  
  // Remover linhas com apenas emojis ou símbolos técnicos
  processedText = processedText.replace(/^[🔒⚠️📊🔗⭐🌟\s]+$/gm, '');
  
  // Remover dignidades planetárias
  processedText = processedText.replace(/🌟\s*DIGNIDADES\s*PLANETÁRIAS[\s\S]*?(?=\n\n|🌟|$)/gi, '');
  processedText = processedText.replace(/DIGNIDADES\s*PLANETÁRIAS[\s\S]*?(?=\n\n|🌟|$)/gi, '');
  processedText = processedText.replace(/DIGNIDADES[\s\S]*?PLANETÁRIAS[\s\S]*?(?=\n\n|🌟|$)/gi, '');
  processedText = processedText.replace(/^\s*\*\s+[\wÀ-ÿ]+\s+em\s+[\wÀ-ÿ]+:\s+(QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$/gmi, '');
  processedText = processedText.replace(/^\s*-\s+[\wÀ-ÿ]+\s+em\s+[\wÀ-ÿ]+:\s+(QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$/gmi, '');
  processedText = processedText.replace(/^\s*[\wÀ-ÿ]+\s+em\s+[\wÀ-ÿ]+:\s+(QUEDA|PEREGRINO|EXALTAÇÃO|DOMICÍLIO|DETRIMENTO)\s*$/gmi, '');
  
  // Remover aspectos
  processedText = processedText.replace(/ASPECTOS[\s\S]*?(?=\n\n|🌟|$)/gi, '');
  processedText = processedText.replace(/🌟\s*ASPECTOS[\s\S]*?(?=\n\n|🌟|$)/gi, '');
  processedText = processedText.replace(/^\s*[-*]\s+(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+-[\wÀ-ÿ]+\s*$/gmi, '');
  processedText = processedText.replace(/^\s*(Conjunção|Sextil|Trígono|Quadratura|Oposição|Conjunction|Sextile|Trine|Square|Opposition)\s+[\wÀ-ÿ]+-[\wÀ-ÿ]+\s*$/gmi, '');
  
  // Remover conteúdo de suporte
  processedText = processedText.replace(/##?\s*📞\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
  processedText = processedText.replace(/##?\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
  processedText = processedText.replace(/Para dúvidas sobre interpretação astrológica[\s\S]*?Consulta com astrólogo profissional[\s\S]*?(?=\n\n|$)/gi, '');
  processedText = processedText.replace(/Livros de astrologia na pasta.*?/gi, '');
  processedText = processedText.replace(/Análise com IA.*?/gi, '');
  processedText = processedText.replace(/Consulta com astrólogo profissional.*?/gi, '');
  processedText = processedText.replace(/Desenvolvido com.*?autoconhecimento profundo[\s\S]*?(?=\n\n|$)/gi, '');
  processedText = processedText.replace(/^[-]{3,}$/gm, '');
  
  // Limpar linhas vazias extras
  processedText = processedText.replace(/\n{3,}/g, '\n\n');
  
  return processedText;
};

// Função para limpar e formatar texto preservando estrutura
const cleanAndFormatText = (text: string): { paragraphs: string[]; hasFormatting: boolean } => {
  // Primeiro aplicar limpeza técnica (mesma do formatGroqText)
  let cleaned = cleanTechnicalContent(text);
  
  // Remove tags HTML mas preserva estrutura
  cleaned = cleaned.replace(/<[^>]*>/g, '');
  
  // Preserva markdown de negrito e itálico para formatação depois
  const hasBold = cleaned.includes('**');
  const hasItalic = cleaned.includes('*');
  
  // Remove markdown básico mas mantém estrutura de parágrafos
  cleaned = cleaned.replace(/\*\*(.*?)\*\*/g, '$1'); // Remove ** mas vamos formatar depois
  cleaned = cleaned.replace(/\*(.*?)\*/g, '$1');
  cleaned = cleaned.replace(/#{1,6}\s+/g, '');
  cleaned = cleaned.replace(/```[\s\S]*?```/g, '');
  
  // Limpa quebras de linha múltiplas mas preserva parágrafos
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n');
  cleaned = cleaned.trim();
  
  // Separa em parágrafos e filtra linhas vazias ou apenas traços
  const paragraphs = cleaned.split('\n\n')
    .filter(p => {
      const trimmed = p.trim();
      // Ignorar parágrafos vazios ou que são apenas traços/hífens
      return trimmed.length > 0 && !/^[-─━─━\s]+$/.test(trimmed) && trimmed.length > 1;
    });
  
  return { paragraphs, hasFormatting: hasBold || hasItalic };
};

// Função para dividir texto em linhas respeitando largura máxima
const splitTextIntoLines = (
  doc: jsPDF,
  text: string,
  maxWidth: number,
  fontSize: number = PDF_CONFIG.fontSize.body
): string[] => {
  doc.setFontSize(fontSize);
  const words = text.split(/\s+/);
  const lines: string[] = [];
  let currentLine = '';

  words.forEach((word) => {
    const testLine = currentLine + (currentLine ? ' ' : '') + word;
    const testWidth = doc.getTextWidth(testLine);

    if (testWidth > maxWidth && currentLine) {
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = testLine;
    }
  });

  if (currentLine) {
    lines.push(currentLine);
  }

  return lines;
};

// Função para adicionar uma seção ao PDF
const addSectionToPDF = (
  doc: jsPDF,
  title: string,
  content: string,
  startY: number,
  pageWidth: number,
  margin: number
): number => {
  const pageHeight = doc.internal.pageSize.height;
  let y = startY;
  const maxWidth = pageWidth - (margin * 2);
  
  // Adicionar título da seção
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(100, 100, 200);
  
  const titleLines = splitTextIntoLines(doc, title, maxWidth);
  titleLines.forEach((line) => {
    if (y > pageHeight - 30) {
      doc.addPage();
      y = margin;
    }
    doc.text(line, margin, y);
    y += 7;
  });
  
  y += 3;
  
  // Adicionar conteúdo
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(60, 60, 60);
  
  const cleanContentResult = cleanAndFormatText(content);
  const paragraphs = cleanContentResult.paragraphs;
  
  paragraphs.forEach((paragraph) => {
    const paragraphLines = splitTextIntoLines(doc, paragraph.trim(), maxWidth);
    
    paragraphLines.forEach((line) => {
      if (y > pageHeight - 30) {
        doc.addPage();
        y = margin;
      }
      doc.text(line, margin, y);
      y += 6;
    });
    
    y += 4; // Espaço entre parágrafos
  });
  
  return y + 10; // Espaço após seção
};

// Função para criar logo como texto/ícone
const addLogo = (doc: jsPDF, margin: number): number => {
  doc.setFontSize(24);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(139, 92, 246); // Cor roxa/violeta do tema
  
  // Desenhar ícone sparkles como texto
  doc.text('✨', margin, 25);
  
  // Nome do sistema
  doc.setFontSize(20);
  doc.text('CosmoAstral', margin + 25, 27);
  
  // Tagline
  doc.setFontSize(10);
  doc.setFont('helvetica', 'italic');
  doc.setTextColor(120, 120, 120);
  doc.text('Seu Guia Celestial', margin + 25, 35);
  
  return 45;
};

// Função para adicionar tabela de planetas em signos
const addPlanetsInSignsTable = (
  doc: jsPDF,
  planets: PlanetInSign[],
  startY: number,
  pageWidth: number,
  margin: number,
  language: 'pt' | 'en'
): number => {
  const pageHeight = doc.internal.pageSize.height;
  let y = startY;
  const maxWidth = pageWidth - (margin * 2);
  
  // Título da seção
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(100, 100, 200);
  const title = language === 'pt' ? 'Planetas em Signos' : 'Planets in Signs';
  doc.text(title, margin, y);
  y += 10;
  
  // Cabeçalho da tabela
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(60, 60, 60);
  doc.text(language === 'pt' ? 'Planeta' : 'Planet', margin, y);
  doc.text(language === 'pt' ? 'Signo' : 'Sign', margin + 50, y);
  doc.text(language === 'pt' ? 'Grau' : 'Degree', margin + 100, y);
  doc.text(language === 'pt' ? 'Casa' : 'House', margin + 140, y);
  y += 7;
  
  // Linha separadora
  doc.setDrawColor(200, 200, 200);
  doc.line(margin, y - 3, pageWidth - margin, y - 3);
  y += 3;
  
  // Dados dos planetas
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(80, 80, 80);
  
  planets.forEach((planet) => {
    if (y > pageHeight - 30) {
      doc.addPage();
      y = margin + 10;
    }
    
    const planetName = planet.planet;
    const sign = planet.sign;
    const degree = planet.degree_dms;
    const house = planet.house;
    const retrograde = (planet.is_retrograde === true) ? ' Rx' : '';
    
    doc.text(planetName + retrograde, margin, y);
    doc.text(sign, margin + 50, y);
    doc.text(degree, margin + 100, y);
    doc.text(house.toString(), margin + 140, y);
    y += 6;
  });
  
  return y + 10;
};

// Função para adicionar pontos especiais
const addSpecialPointsSection = (
  doc: jsPDF,
  points: SpecialPoint[],
  startY: number,
  pageWidth: number,
  margin: number,
  language: 'pt' | 'en'
): number => {
  const pageHeight = doc.internal.pageSize.height;
  let y = startY;
  const maxWidth = pageWidth - (margin * 2);
  
  // Título da seção
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(100, 100, 200);
  const title = language === 'pt' ? 'Pontos Especiais' : 'Special Points';
  doc.text(title, margin, y);
  y += 10;
  
  // Cabeçalho
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(60, 60, 60);
  doc.text(language === 'pt' ? 'Ponto' : 'Point', margin, y);
  doc.text(language === 'pt' ? 'Signo' : 'Sign', margin + 60, y);
  doc.text(language === 'pt' ? 'Grau' : 'Degree', margin + 110, y);
  doc.text(language === 'pt' ? 'Casa' : 'House', margin + 150, y);
  y += 7;
  
  // Linha separadora
  doc.setDrawColor(200, 200, 200);
  doc.line(margin, y - 3, pageWidth - margin, y - 3);
  y += 3;
  
  // Dados dos pontos
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(80, 80, 80);
  
  points.forEach((point) => {
    if (y > pageHeight - 30) {
      doc.addPage();
      y = margin + 10;
    }
    
    doc.text(point.point, margin, y);
    doc.text(point.sign, margin + 60, y);
    doc.text(point.degree_dms, margin + 110, y);
    doc.text(point.house.toString(), margin + 150, y);
    y += 6;
  });
  
  return y + 10;
};

// Função para adicionar planetas nas casas
const addPlanetsInHousesSection = (
  doc: jsPDF,
  houses: Array<{ 
    house: number; 
    planets: Array<{
      planet?: string;
      point?: string;
      planet_key?: string;
      point_key?: string;
      sign: string;
      degree: number;
      degree_dms: string;
      house: number;
      is_retrograde?: boolean;
    }> 
  }>,
  startY: number,
  pageWidth: number,
  margin: number,
  language: 'pt' | 'en'
): number => {
  const pageHeight = doc.internal.pageSize.height;
  let y = startY;
  const maxWidth = pageWidth - (margin * 2);
  
  // Títulos das casas
  const houseNames = language === 'pt'
    ? {
        1: 'Primeira Casa', 2: 'Segunda Casa', 3: 'Terceira Casa', 4: 'Quarta Casa',
        5: 'Quinta Casa', 6: 'Sexta Casa', 7: 'Sétima Casa', 8: 'Oitava Casa',
        9: 'Nona Casa', 10: 'Décima Casa', 11: 'Décima Primeira Casa', 12: 'Décima Segunda Casa'
      }
    : {
        1: 'First House', 2: 'Second House', 3: 'Third House', 4: 'Fourth House',
        5: 'Fifth House', 6: 'Sixth House', 7: 'Seventh House', 8: 'Eighth House',
        9: 'Ninth House', 10: 'Tenth House', 11: 'Eleventh House', 12: 'Twelfth House'
      };
  
  // Título da seção
  doc.setFontSize(14);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(100, 100, 200);
  const title = language === 'pt' ? 'Planetas nas Casas' : 'Planets in Houses';
  doc.text(title, margin, y);
  y += 10;
  
  doc.setFontSize(9);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(80, 80, 80);
  
  houses.forEach((houseData) => {
    if (y > pageHeight - 40) {
      doc.addPage();
      y = margin + 10;
    }
    
    const houseNum = houseData.house;
    const planets = houseData.planets;
    
    if (planets.length > 0) {
      // Nome da casa
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(60, 60, 60);
      doc.text(`${houseNames[houseNum as keyof typeof houseNames] || `Casa ${houseNum}`}:`, margin, y);
      y += 6;
      
      // Planetas na casa
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(80, 80, 80);
      planets.forEach((planet) => {
        const planetName = planet.planet || planet.point || 'N/A';
        const sign = planet.sign || 'N/A';
        const degree = planet.degree_dms || 'N/A';
        const retrograde = (planet.is_retrograde === true) ? ' Rx' : '';
        
        doc.text(`  • ${planetName}${retrograde} em ${sign} ${degree}`, margin + 5, y);
        y += 5;
      });
      
      y += 3;
    }
  });
  
  return y + 10;
};

export const generateBirthChartPDF = ({
  userData,
  sections,
  language,
  chartData
}: GeneratePDFOptions): void => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 15;
  let y = margin;
  
  // ===== CAPA =====
  // Logo
  y = addLogo(doc, margin);
  y += 20;
  
  // Título principal
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(60, 60, 60);
  const title = language === 'pt' ? 'Mapa Astral Completo' : 'Complete Birth Chart';
  doc.text(title, pageWidth / 2, y, { align: 'center' });
  y += 10;
  
  // Informações do usuário
  doc.setFontSize(12);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(100, 100, 100);
  
  const userName = userData.name || (language === 'pt' ? 'Usuário' : 'User');
  const birthDate = typeof userData.birthDate === 'string' 
    ? userData.birthDate 
    : userData.birthDate instanceof Date 
      ? userData.birthDate.toLocaleDateString(language === 'pt' ? 'pt-BR' : 'en-US')
      : '';
  const birthTime = userData.birthTime || '';
  const birthPlace = userData.birthPlace || '';
  
  // Nome
  doc.text(`${language === 'pt' ? 'Nome:' : 'Name:'} ${userName}`, pageWidth / 2, y, { align: 'center' });
  y += 7;
  
  // Data e hora
  const dateTimeText = `${language === 'pt' ? 'Data de Nascimento:' : 'Birth Date:'} ${birthDate} ${language === 'pt' ? 'às' : 'at'} ${birthTime}`;
  const dateTimeLines = splitTextIntoLines(doc, dateTimeText, pageWidth - (margin * 2));
  dateTimeLines.forEach((line) => {
    doc.text(line, pageWidth / 2, y, { align: 'center' });
    y += 6;
  });
  
  // Local - usar splitTextIntoLines para evitar truncamento
  const placeLabel = language === 'pt' ? 'Local:' : 'Place:';
  const placeText = `${placeLabel} ${birthPlace}`;
  const placeLines = splitTextIntoLines(doc, placeText, pageWidth - (margin * 2));
  placeLines.forEach((line) => {
    doc.text(line, pageWidth / 2, y, { align: 'center' });
    y += 6;
  });
  y += 9; // Espaço adicional após local
  
  // Resumo do mapa
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(60, 60, 60);
  doc.text(language === 'pt' ? 'Resumo do Mapa' : 'Chart Summary', margin, y);
  y += 8;
  
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(80, 80, 80);
  
  const sunSign = userData.sunSign || '';
  const moonSign = userData.moonSign || '';
  const ascendant = userData.ascendant || '';
  
  doc.text(`☀️ ${language === 'pt' ? 'Sol' : 'Sun'}: ${sunSign}`, margin, y);
  y += 6;
  doc.text(`🌙 ${language === 'pt' ? 'Lua' : 'Moon'}: ${moonSign}`, margin, y);
  y += 6;
  doc.text(`⬆️ ${language === 'pt' ? 'Ascendente' : 'Ascendant'}: ${ascendant}`, margin, y);
  
  // Data de geração
  y = pageHeight - 30;
  doc.setFontSize(8);
  doc.setFont('helvetica', 'italic');
  doc.setTextColor(150, 150, 150);
  const generationDate = new Date().toLocaleDateString(language === 'pt' ? 'pt-BR' : 'en-US', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
  doc.text(
    `${language === 'pt' ? 'Gerado em' : 'Generated on'}: ${generationDate}`,
    pageWidth / 2,
    y,
    { align: 'center' }
  );
  
  // Nova página para os dados do mapa
  doc.addPage();
  y = margin;
  
  // ===== DADOS COMPLETOS DO MAPA ASTRAL =====
  if (chartData) {
    // Planetas em Signos
    if (chartData.planets_in_signs && chartData.planets_in_signs.length > 0) {
      y = addPlanetsInSignsTable(doc, chartData.planets_in_signs, y, pageWidth, margin, language);
      
      // Adicionar separador
      if (y < pageHeight - 30) {
        doc.setDrawColor(200, 200, 200);
        doc.line(margin, y, pageWidth - margin, y);
        y += 15;
      }
    }
    
    // Pontos Especiais
    if (chartData.special_points && chartData.special_points.length > 0) {
      if (y > pageHeight - 50) {
        doc.addPage();
        y = margin;
      }
      y = addSpecialPointsSection(doc, chartData.special_points, y, pageWidth, margin, language);
      
      // Adicionar separador
      if (y < pageHeight - 30) {
        doc.setDrawColor(200, 200, 200);
        doc.line(margin, y, pageWidth - margin, y);
        y += 15;
      }
    }
    
    // Planetas nas Casas
    if (chartData.planets_in_houses && chartData.planets_in_houses.length > 0) {
      if (y > pageHeight - 60) {
        doc.addPage();
        y = margin;
      }
      y = addPlanetsInHousesSection(doc, chartData.planets_in_houses, y, pageWidth, margin, language);
    }
  }
  
  // Nova página para as seções de interpretação
  doc.addPage();
  y = margin;
  
  // ===== SEÇÕES DE INTERPRETAÇÃO DO MAPA ASTRAL =====
  const sectionOrder = ['power', 'triad', 'personal', 'houses', 'karma', 'synthesis'];
  const sectionTitles = {
    pt: {
      power: 'A Engenharia da Sua Energia (Temperamento)',
      triad: 'O Núcleo da Personalidade (A Tríade Primordial)',
      personal: 'Estratégia de Tomada de Decisão & Carreira',
      houses: 'Relacionamentos e Vida Afetiva',
      karma: 'O Caminho Kármico e Desafios de Crescimento',
      synthesis: 'Síntese e Orientação Estratégica'
    },
    en: {
      power: 'The Engineering of Your Energy (Temperament)',
      triad: 'The Core of Personality (The Primordial Triad)',
      personal: 'Decision Making Strategy & Career',
      houses: 'Relationships and Affective Life',
      karma: 'The Karmic Path and Growth Challenges',
      synthesis: 'Strategic Synthesis and Guidance'
    }
  };
  
  sectionOrder.forEach((sectionKey) => {
    const section = sections[sectionKey];
    if (section && section.content) {
      const title = section.title || sectionTitles[language][sectionKey as keyof typeof sectionTitles.pt];
      
      // Aplicar a mesma formatação usada na tela para garantir fidelidade
      // As seções 'triad' e 'power' passam por formatTriadContent para remover repetições
      let contentToUse = section.content;
      if (sectionKey === 'triad' || sectionKey === 'power') {
        contentToUse = formatTriadContent(section.content);
      }
      
      y = addSectionToPDF(doc, title, contentToUse, y, pageWidth, margin);
      
      // Adicionar linha separadora
      if (y < pageHeight - 30) {
        doc.setDrawColor(200, 200, 200);
        doc.line(margin, y, pageWidth - margin, y);
        y += 10;
      }
    }
  });
  
  // ===== REFERÊNCIAS =====
  doc.addPage();
  y = margin;
  
  // Título das Referências
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(60, 60, 60);
  doc.text(language === 'pt' ? 'Referências do Sistema' : 'System References', margin, y);
  y += 15;
  
  // Referências
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(100, 100, 200);
  doc.text(language === 'pt' ? 'Metodologia e Fontes Astrológicas:' : 'Methodology and Astrological Sources:', margin, y);
  y += 10;
  
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(60, 60, 60);
  
  const references = language === 'pt' ? [
    '• Stephen Arroyo - Astrologia Psicológica e visão energética dos elementos',
    '• Sakoian & Acker - Técnica rigorosa de aspectos e orbes planetários',
    '• Kris Brandt Riske - Aplicação prática das Casas Astrológicas',
    '• Astrologia Junguiana - Abordagem psicológica profunda do mapa natal',
    '• Astrologia Evolutiva - Foco em crescimento pessoal e livre-arbítrio'
  ] : [
    '• Stephen Arroyo - Psychological Astrology and energetic vision of elements',
    '• Sakoian & Acker - Rigorous technique of aspects and planetary orbs',
    '• Kris Brandt Riske - Practical application of Astrological Houses',
    '• Jungian Astrology - Deep psychological approach to the birth chart',
    '• Evolutionary Astrology - Focus on personal growth and free will'
  ];
  
  references.forEach((ref) => {
    if (y > pageHeight - 30) {
      doc.addPage();
      y = margin;
    }
    doc.text(ref, margin + 5, y);
    y += 7;
  });
  
  y += 10;
  
  // Nota sobre IA
  doc.setFontSize(11);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(100, 100, 200);
  doc.text(language === 'pt' ? 'Sobre a Interpretação:' : 'About the Interpretation:', margin, y);
  y += 10;
  
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(60, 60, 60);
  
  const aboutText = language === 'pt' 
    ? 'Esta interpretação foi gerada usando inteligência artificial treinada em fontes astrológicas tradicionais, combinando Astrologia Psicológica (linha Junguiana) e Astrologia Evolutiva. As análises focam no potencial de crescimento e livre-arbítrio, evitando determinismos. Use estas informações como ferramenta de autoconhecimento.'
    : 'This interpretation was generated using artificial intelligence trained on traditional astrological sources, combining Psychological Astrology (Jungian approach) and Evolutionary Astrology. The analyses focus on growth potential and free will, avoiding determinism. Use this information as a self-knowledge tool.';
  
  const aboutLines = splitTextIntoLines(doc, aboutText, pageWidth - (margin * 2));
  aboutLines.forEach((line) => {
    if (y > pageHeight - 30) {
      doc.addPage();
      y = margin;
    }
    doc.text(line, margin, y);
    y += 6;
  });
  
  // ===== GLOSSÁRIO DE TERMOS TÉCNICOS =====
  y += 15;
  if (y > pageHeight - 60) {
    doc.addPage();
    y = margin;
  }
  
  // Título do Glossário
  doc.setFontSize(16);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(60, 60, 60);
  doc.text(language === 'pt' ? 'Glossário de Termos Técnicos' : 'Glossary of Technical Terms', margin, y);
  y += 12;
  
  // Introdução do Glossário
  doc.setFontSize(9);
  doc.setFont('helvetica', 'italic');
  doc.setTextColor(80, 80, 80);
  const glossaryIntro = language === 'pt' 
    ? 'Abaixo estão explicações dos principais termos técnicos de astrologia utilizados neste mapa astral:'
    : 'Below are explanations of the main technical terms in astrology used in this birth chart:';
  const glossaryIntroLines = splitTextIntoLines(doc, glossaryIntro, pageWidth - (margin * 2), 9);
  glossaryIntroLines.forEach((line) => {
    if (y > pageHeight - 30) {
      doc.addPage();
      y = margin;
    }
    doc.text(line, margin, y);
    y += 5;
  });
  y += 8;
  
  // Obter termos do glossário
  const glossaryTerms = getAllGlossaryTerms(language as 'pt' | 'en');
  
  // Organizar termos por categoria
  const termsByCategory: Record<string, typeof glossaryTerms> = {
    basic: [],
    planets: [],
    houses: [],
    aspects: [],
    points: [],
    advanced: [],
  };
  
  glossaryTerms.forEach(term => {
    if (termsByCategory[term.category]) {
      termsByCategory[term.category].push(term);
    }
  });
  
  // Categorias em ordem de importância
  const categoryOrder = ['basic', 'planets', 'houses', 'aspects', 'points', 'advanced'];
  const categoryNames = language === 'pt' 
    ? {
        basic: 'Termos Básicos',
        planets: 'Planetas',
        houses: 'Casas',
        aspects: 'Aspectos',
        points: 'Pontos Importantes',
        advanced: 'Termos Avançados',
      }
    : {
        basic: 'Basic Terms',
        planets: 'Planets',
        houses: 'Houses',
        aspects: 'Aspects',
        points: 'Important Points',
        advanced: 'Advanced Terms',
      };
  
  categoryOrder.forEach(category => {
    const categoryTerms = termsByCategory[category];
    if (categoryTerms.length === 0) return;
    
    // Título da categoria
    if (y > pageHeight - 50) {
      doc.addPage();
      y = margin;
    }
    
    doc.setFontSize(12);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(100, 100, 200);
    doc.text(categoryNames[category as keyof typeof categoryNames] || category, margin, y);
    y += 10;
    
    // Termos da categoria
    categoryTerms.forEach(term => {
      if (y > pageHeight - 40) {
        doc.addPage();
        y = margin;
      }
      
      // Nome do termo
      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(60, 60, 60);
      doc.text(term.term + ':', margin + 5, y);
      y += 6;
      
      // Explicação do termo
      doc.setFontSize(9);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(80, 80, 80);
      const explanationLines = splitTextIntoLines(doc, term.explanation, pageWidth - (margin * 2) - 10, 9);
      explanationLines.forEach((line) => {
        if (y > pageHeight - 30) {
          doc.addPage();
          y = margin;
        }
        doc.text(line, margin + 10, y);
        y += 5;
      });
      
      y += 5; // Espaço entre termos
    });
    
    y += 5; // Espaço extra entre categorias
  });
  
  // Rodapé
  y = pageHeight - 20;
  doc.setFontSize(8);
  doc.setFont('helvetica', 'italic');
  doc.setTextColor(150, 150, 150);
  doc.text('CosmoAstral - www.cosmoastral.com.br', pageWidth / 2, y, { align: 'center' });
  
  // Salvar PDF
  const fileName = `Mapa_Astral_${userName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(fileName);
};


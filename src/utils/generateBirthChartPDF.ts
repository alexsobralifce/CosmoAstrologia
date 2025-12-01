import jsPDF from 'jspdf';
import { OnboardingData } from '../components/onboarding';
import { formatTriadContent } from './formatTriadContent';

interface BirthChartSection {
  section: string;
  title: string;
  content: string;
  generated_by: string;
}

interface GeneratePDFOptions {
  userData: OnboardingData;
  sections: Record<string, BirthChartSection | null>;
  language: 'pt' | 'en';
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

// Função para limpar e formatar texto preservando estrutura
const cleanAndFormatText = (text: string): { paragraphs: string[]; hasFormatting: boolean } => {
  // Remove tags HTML mas preserva estrutura
  let cleaned = text.replace(/<[^>]*>/g, '');
  
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
  
  // Separa em parágrafos
  const paragraphs = cleaned.split('\n\n').filter(p => p.trim().length > 0);
  
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
  doc.text('Cosmos Astral', margin + 25, 27);
  
  // Tagline
  doc.setFontSize(10);
  doc.setFont('helvetica', 'italic');
  doc.setTextColor(120, 120, 120);
  doc.text('Seu Guia Celestial', margin + 25, 35);
  
  return 45;
};

export const generateBirthChartPDF = ({
  userData,
  sections,
  language
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
  
  doc.text(`${language === 'pt' ? 'Nome:' : 'Name:'} ${userName}`, pageWidth / 2, y, { align: 'center' });
  y += 7;
  doc.text(`${language === 'pt' ? 'Data de Nascimento:' : 'Birth Date:'} ${birthDate} ${language === 'pt' ? 'às' : 'at'} ${birthTime}`, pageWidth / 2, y, { align: 'center' });
  y += 7;
  doc.text(`${language === 'pt' ? 'Local:' : 'Place:'} ${birthPlace}`, pageWidth / 2, y, { align: 'center' });
  y += 15;
  
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
  
  // Nova página para as seções
  doc.addPage();
  y = margin;
  
  // ===== SEÇÕES DO MAPA ASTRAL =====
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
  
  // Rodapé
  y = pageHeight - 20;
  doc.setFontSize(8);
  doc.setFont('helvetica', 'italic');
  doc.setTextColor(150, 150, 150);
  doc.text('Cosmos Astral - www.cosmosastral.com', pageWidth / 2, y, { align: 'center' });
  
  // Salvar PDF
  const fileName = `Mapa_Astral_${userName.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(fileName);
};


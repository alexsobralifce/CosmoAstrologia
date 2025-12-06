import React, { useState, useEffect } from 'react';
import { UIIcons } from './ui-icons';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';
import { BirthChartWheel } from './birth-chart-wheel';
import { ElementChart } from './element-chart';
import { FutureTransitsSection } from './future-transits-section';
import { apiService } from '../services/api';
import { useLanguage } from '../i18n';
import { OnboardingData } from './onboarding';
import { AstroCard } from './astro-card';

// Função utilitária para remover informações de suporte e conteúdo técnico
const removeSupportAndTechnicalContent = (text: string): string => {
  let cleaned = text;
  
  // Remover seção "Suporte" completa (todas as variações)
  cleaned = cleaned.replace(/##?\s*📞\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
  cleaned = cleaned.replace(/##?\s*Suporte[\s\S]*?(?=\n\n|$)/gi, '');
  cleaned = cleaned.replace(/Suporte[\s\S]*?Consulta com astrólogo profissional[\s\S]*?(?=\n\n|$)/gi, '');
  cleaned = cleaned.replace(/Para dúvidas sobre interpretação astrológica[\s\S]*?Consulta com astrólogo profissional[\s\S]*?(?=\n\n|$)/gi, '');
  
  // Remover linhas específicas de suporte
  cleaned = cleaned.replace(/Livros de astrologia na pasta.*?/gi, '');
  cleaned = cleaned.replace(/Análise com IA.*?botão.*?/gi, '');
  cleaned = cleaned.replace(/Análise com IA.*?/gi, '');
  cleaned = cleaned.replace(/Consulta com astrólogo profissional.*?/gi, '');
  
  // Remover rodapé
  cleaned = cleaned.replace(/Desenvolvido com.*?autoconhecimento profundo[\s\S]*?(?=\n\n|$)/gi, '');
  cleaned = cleaned.replace(/Desenvolvido com.*?❤️.*?autoconhecimento[\s\S]*?(?=\n\n|$)/gi, '');
  
  // Remover separadores markdown
  cleaned = cleaned.replace(/^[-]{3,}$/gm, '');
  cleaned = cleaned.replace(/^[=]{3,}$/gm, '');
  
  return cleaned;
};

// ===== VISÃO GERAL =====
interface OverviewSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const OverviewSection = ({ userData, onBack }: OverviewSectionProps) => {
  const { t, language } = useLanguage();
  const [chartRulerInterpretation, setChartRulerInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  // Determinar signo e regente baseado nos dados do usuário
  const ascendantSign = userData.ascendant || 'Áries';
  const sunSign = userData.sunSign || 'Áries';
  const moonSign = userData.moonSign || 'Touro';

  // Mapeamento de regentes
  const rulerMap: Record<string, string> = {
    'Áries': 'Marte', 'Touro': 'Vênus', 'Gêmeos': 'Mercúrio', 'Câncer': 'Lua',
    'Leão': 'Sol', 'Virgem': 'Mercúrio', 'Libra': 'Vênus', 'Escorpião': 'Plutão',
    'Sagitário': 'Júpiter', 'Capricórnio': 'Saturno', 'Aquário': 'Urano', 'Peixes': 'Netuno'
  };

  const chartRuler = rulerMap[ascendantSign] || 'Sol';

  // Função para obter signo e casa do regente baseado no nome do planeta
  const getRulerSignAndHouse = (rulerName: string): { sign: string; house: number } => {
    const planetToDataMap: Record<string, { signKey: keyof typeof userData; houseKey: keyof typeof userData }> = {
      'Sol': { signKey: 'sunSign', houseKey: 'sunHouse' },
      'Lua': { signKey: 'moonSign', houseKey: 'moonHouse' },
      'Mercúrio': { signKey: 'mercurySign', houseKey: 'mercuryHouse' },
      'Vênus': { signKey: 'venusSign', houseKey: 'venusHouse' },
      'Marte': { signKey: 'marsSign', houseKey: 'marsHouse' },
      'Júpiter': { signKey: 'jupiterSign', houseKey: 'jupiterHouse' },
      'Saturno': { signKey: 'saturnSign', houseKey: 'saturnHouse' },
      'Urano': { signKey: 'uranusSign', houseKey: 'uranusHouse' },
      'Netuno': { signKey: 'neptuneSign', houseKey: 'neptuneHouse' },
      'Plutão': { signKey: 'plutoSign', houseKey: 'plutoHouse' },
    };

    const planetData = planetToDataMap[rulerName];
    if (planetData) {
      return {
        sign: (userData[planetData.signKey] as string) || sunSign,
        house: (userData[planetData.houseKey] as number) || 1
      };
    }
    return { sign: sunSign, house: 1 };
  };

  const rulerData = getRulerSignAndHouse(chartRuler);
  const rulerSign = rulerData.sign;
  const rulerHouse = rulerData.house;

  // Informações detalhadas sobre cada planeta regente
  const rulerDetails: Record<string, {
    meaning: { pt: string; en: string };
    famousPeople: { pt: string[]; en: string[] };
    characteristics: { pt: string[]; en: string[] };
    influence: { pt: string; en: string };
  }> = {
    'Sol': {
      meaning: {
        pt: 'Ter o Sol como regente significa que sua identidade e propósito de vida são fundamentais para sua expressão no mundo. Você brilha naturalmente e busca reconhecimento.',
        en: 'Having the Sun as ruler means your identity and life purpose are fundamental to your expression in the world. You naturally shine and seek recognition.'
      },
      famousPeople: {
        pt: ['Leonardo DiCaprio', 'Oprah Winfrey', 'Madonna', 'Barack Obama', 'Jennifer Lopez'],
        en: ['Leonardo DiCaprio', 'Oprah Winfrey', 'Madonna', 'Barack Obama', 'Jennifer Lopez']
      },
      characteristics: {
        pt: ['Liderança natural', 'Confiança e carisma', 'Busca por reconhecimento', 'Criatividade expressiva', 'Vitalidade e energia'],
        en: ['Natural leadership', 'Confidence and charisma', 'Seeking recognition', 'Expressive creativity', 'Vitality and energy']
      },
      influence: {
        pt: 'O Sol como regente traz uma necessidade de expressar sua essência única e ser reconhecido por suas conquistas. Você tem uma presença marcante e inspira outros.',
        en: 'The Sun as ruler brings a need to express your unique essence and be recognized for your achievements. You have a striking presence and inspire others.'
      }
    },
    'Lua': {
      meaning: {
        pt: 'Ter a Lua como regente significa que suas emoções e intuição guiam sua vida. Você é sensível, adaptável e profundamente conectado ao seu mundo interior.',
        en: 'Having the Moon as ruler means your emotions and intuition guide your life. You are sensitive, adaptable and deeply connected to your inner world.'
      },
      famousPeople: {
        pt: ['Princesa Diana', 'Meryl Streep', 'Tom Hanks', 'Julia Roberts', 'Johnny Depp'],
        en: ['Princess Diana', 'Meryl Streep', 'Tom Hanks', 'Julia Roberts', 'Johnny Depp']
      },
      characteristics: {
        pt: ['Sensibilidade emocional', 'Intuição desenvolvida', 'Adaptabilidade', 'Cuidado e proteção', 'Memória emocional forte'],
        en: ['Emotional sensitivity', 'Developed intuition', 'Adaptability', 'Care and protection', 'Strong emotional memory']
      },
      influence: {
        pt: 'A Lua como regente traz uma natureza emocional profunda e uma capacidade única de se conectar com as necessidades dos outros. Você nutre e protege naturalmente.',
        en: 'The Moon as ruler brings a deep emotional nature and a unique ability to connect with the needs of others. You naturally nurture and protect.'
      }
    },
    'Mercúrio': {
      meaning: {
        pt: 'Ter Mercúrio como regente significa que comunicação, aprendizado e movimento são essenciais para você. Você é curioso, versátil e sempre em busca de conhecimento.',
        en: 'Having Mercury as ruler means communication, learning and movement are essential to you. You are curious, versatile and always seeking knowledge.'
      },
      famousPeople: {
        pt: ['Albert Einstein', 'Stephen Hawking', 'Neil deGrasse Tyson', 'Emma Watson', 'Daniel Radcliffe'],
        en: ['Albert Einstein', 'Stephen Hawking', 'Neil deGrasse Tyson', 'Emma Watson', 'Daniel Radcliffe']
      },
      characteristics: {
        pt: ['Comunicação fluida', 'Curiosidade intelectual', 'Versatilidade', 'Raciocínio rápido', 'Adaptação mental'],
        en: ['Fluid communication', 'Intellectual curiosity', 'Versatility', 'Quick reasoning', 'Mental adaptation']
      },
      influence: {
        pt: 'Mercúrio como regente traz uma mente ágil e uma necessidade constante de aprender e comunicar. Você processa informações rapidamente e se adapta facilmente.',
        en: 'Mercury as ruler brings an agile mind and a constant need to learn and communicate. You process information quickly and adapt easily.'
      }
    },
    'Vênus': {
      meaning: {
        pt: 'Ter Vênus como regente significa que amor, beleza, harmonia e valores são centrais na sua vida. Você busca relacionamentos significativos e aprecia o que é belo.',
        en: 'Having Venus as ruler means love, beauty, harmony and values are central to your life. You seek meaningful relationships and appreciate what is beautiful.'
      },
      famousPeople: {
        pt: ['Marilyn Monroe', 'Grace Kelly', 'Audrey Hepburn', 'Ryan Gosling', 'Scarlett Johansson'],
        en: ['Marilyn Monroe', 'Grace Kelly', 'Audrey Hepburn', 'Ryan Gosling', 'Scarlett Johansson']
      },
      characteristics: {
        pt: ['Charme natural', 'Apreciação pela beleza', 'Busca por harmonia', 'Valores relacionais', 'Estilo e elegância'],
        en: ['Natural charm', 'Appreciation for beauty', 'Seeking harmony', 'Relational values', 'Style and elegance']
      },
      influence: {
        pt: 'Vênus como regente traz uma natureza harmoniosa e uma capacidade de criar beleza e conexões. Você valoriza relacionamentos e busca equilíbrio em todas as áreas.',
        en: 'Venus as ruler brings a harmonious nature and an ability to create beauty and connections. You value relationships and seek balance in all areas.'
      }
    },
    'Marte': {
      meaning: {
        pt: 'Ter Marte como regente significa que ação, coragem e iniciativa são suas forças. Você é determinado, direto e não tem medo de lutar pelo que deseja.',
        en: 'Having Mars as ruler means action, courage and initiative are your strengths. You are determined, direct and not afraid to fight for what you want.'
      },
      famousPeople: {
        pt: ['Bruce Lee', 'Muhammad Ali', 'Serena Williams', 'Tom Cruise', 'Angelina Jolie'],
        en: ['Bruce Lee', 'Muhammad Ali', 'Serena Williams', 'Tom Cruise', 'Angelina Jolie']
      },
      characteristics: {
        pt: ['Iniciativa e ação', 'Coragem e determinação', 'Competitividade', 'Impulso e energia', 'Liderança assertiva'],
        en: ['Initiative and action', 'Courage and determination', 'Competitiveness', 'Drive and energy', 'Assertive leadership']
      },
      influence: {
        pt: 'Marte como regente traz uma energia combativa e uma necessidade de agir. Você é pioneiro, corajoso e não hesita em defender seus ideais.',
        en: 'Mars as ruler brings a combative energy and a need to act. You are a pioneer, courageous and do not hesitate to defend your ideals.'
      }
    },
    'Júpiter': {
      meaning: {
        pt: 'Ter Júpiter como regente significa que expansão, sabedoria e oportunidades são seus guias. Você busca crescimento, conhecimento e tem uma visão otimista da vida.',
        en: 'Having Jupiter as ruler means expansion, wisdom and opportunities are your guides. You seek growth, knowledge and have an optimistic view of life.'
      },
      famousPeople: {
        pt: ['Walt Disney', 'Richard Branson', 'Oprah Winfrey', 'Morgan Freeman', 'Denzel Washington'],
        en: ['Walt Disney', 'Richard Branson', 'Oprah Winfrey', 'Morgan Freeman', 'Denzel Washington']
      },
      characteristics: {
        pt: ['Otimismo e fé', 'Busca por sabedoria', 'Expansão e crescimento', 'Generosidade', 'Visão ampla'],
        en: ['Optimism and faith', 'Seeking wisdom', 'Expansion and growth', 'Generosity', 'Broad vision']
      },
      influence: {
        pt: 'Júpiter como regente traz uma natureza expansiva e uma busca constante por significado e crescimento. Você atrai oportunidades e tem uma visão positiva da vida.',
        en: 'Jupiter as ruler brings an expansive nature and a constant search for meaning and growth. You attract opportunities and have a positive view of life.'
      }
    },
    'Saturno': {
      meaning: {
        pt: 'Ter Saturno como regente significa que disciplina, estrutura e responsabilidade são fundamentais. Você constrói com paciência e valoriza a maturidade e o trabalho árduo.',
        en: 'Having Saturn as ruler means discipline, structure and responsibility are fundamental. You build with patience and value maturity and hard work.'
      },
      famousPeople: {
        pt: ['Warren Buffett', 'Michelle Obama', 'Meryl Streep', 'Clint Eastwood', 'Helen Mirren'],
        en: ['Warren Buffett', 'Michelle Obama', 'Meryl Streep', 'Clint Eastwood', 'Helen Mirren']
      },
      characteristics: {
        pt: ['Disciplina e estrutura', 'Responsabilidade', 'Paciência e persistência', 'Maturidade', 'Construção sólida'],
        en: ['Discipline and structure', 'Responsibility', 'Patience and persistence', 'Maturity', 'Solid building']
      },
      influence: {
        pt: 'Saturno como regente traz uma natureza séria e responsável. Você constrói sua vida com método e disciplina, valorizando o trabalho árduo e a consistência.',
        en: 'Saturn as ruler brings a serious and responsible nature. You build your life with method and discipline, valuing hard work and consistency.'
      }
    },
    'Urano': {
      meaning: {
        pt: 'Ter Urano como regente significa que inovação, liberdade e originalidade são essenciais. Você é único, revolucionário e busca quebrar padrões estabelecidos.',
        en: 'Having Uranus as ruler means innovation, freedom and originality are essential. You are unique, revolutionary and seek to break established patterns.'
      },
      famousPeople: {
        pt: ['Elon Musk', 'Lady Gaga', 'David Bowie', 'Björk', 'Tim Burton'],
        en: ['Elon Musk', 'Lady Gaga', 'David Bowie', 'Björk', 'Tim Burton']
      },
      characteristics: {
        pt: ['Originalidade e inovação', 'Independência radical', 'Rebeldia construtiva', 'Visão futurista', 'Quebra de padrões'],
        en: ['Originality and innovation', 'Radical independence', 'Constructive rebellion', 'Futuristic vision', 'Breaking patterns']
      },
      influence: {
        pt: 'Urano como regente traz uma natureza única e revolucionária. Você é inovador, independente e tem uma visão única do mundo, sempre buscando progresso.',
        en: 'Uranus as ruler brings a unique and revolutionary nature. You are innovative, independent and have a unique view of the world, always seeking progress.'
      }
    },
    'Netuno': {
      meaning: {
        pt: 'Ter Netuno como regente significa que espiritualidade, intuição e criatividade são seus guias. Você é sensível, compassivo e profundamente conectado ao mundo espiritual.',
        en: 'Having Neptune as ruler means spirituality, intuition and creativity are your guides. You are sensitive, compassionate and deeply connected to the spiritual world.'
      },
      famousPeople: {
        pt: ['Princesa Diana', 'Kurt Cobain', 'Jimi Hendrix', 'Amy Winehouse', 'Heath Ledger'],
        en: ['Princess Diana', 'Kurt Cobain', 'Jimi Hendrix', 'Amy Winehouse', 'Heath Ledger']
      },
      characteristics: {
        pt: ['Intuição profunda', 'Criatividade artística', 'Compaixão e empatia', 'Sensibilidade espiritual', 'Imaginação vívida'],
        en: ['Deep intuition', 'Artistic creativity', 'Compassion and empathy', 'Spiritual sensitivity', 'Vivid imagination']
      },
      influence: {
        pt: 'Netuno como regente traz uma natureza sensível e intuitiva. Você é artista, místico e tem uma conexão profunda com o mundo invisível e espiritual.',
        en: 'Neptune as ruler brings a sensitive and intuitive nature. You are an artist, mystic and have a deep connection with the invisible and spiritual world.'
      }
    },
    'Plutão': {
      meaning: {
        pt: 'Ter Plutão como regente significa que transformação, poder e regeneração são seus temas. Você passa por profundas transformações e tem uma intensidade única.',
        en: 'Having Pluto as ruler means transformation, power and regeneration are your themes. You go through deep transformations and have a unique intensity.'
      },
      famousPeople: {
        pt: ['Frida Kahlo', 'Leonardo da Vinci', 'Edgar Allan Poe', 'Sigmund Freud', 'Marilyn Manson'],
        en: ['Frida Kahlo', 'Leonardo da Vinci', 'Edgar Allan Poe', 'Sigmund Freud', 'Marilyn Manson']
      },
      characteristics: {
        pt: ['Intensidade profunda', 'Transformação constante', 'Poder de regeneração', 'Psicologia profunda', 'Mistério e profundidade'],
        en: ['Deep intensity', 'Constant transformation', 'Regenerative power', 'Deep psychology', 'Mystery and depth']
      },
      influence: {
        pt: 'Plutão como regente traz uma natureza intensa e transformadora. Você passa por ciclos profundos de morte e renascimento, sempre emergindo mais forte.',
        en: 'Pluto as ruler brings an intense and transformative nature. You go through deep cycles of death and rebirth, always emerging stronger.'
      }
    }
  };

  const currentRulerDetails = rulerDetails[chartRuler] || rulerDetails['Sol'];

  // Função para formatar o texto do regente organizando por tópicos
  const formatChartRulerText = (text: string): React.ReactNode => {
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
        const content = boldMatch ? trimmed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') : trimmed;
        formattedParagraphs.push(
          <div key={index}>
            <p 
              className="overview-chart-ruler-heading" 
              dangerouslySetInnerHTML={{ __html: content }}
            />
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

  // Mapeamento de signos para elementos
  const signToElement: Record<string, 'Fogo' | 'Terra' | 'Ar' | 'Água'> = {
    'Áries': 'Fogo', 'Leão': 'Fogo', 'Sagitário': 'Fogo',
    'Touro': 'Terra', 'Virgem': 'Terra', 'Capricórnio': 'Terra',
    'Gêmeos': 'Ar', 'Libra': 'Ar', 'Aquário': 'Ar',
    'Câncer': 'Água', 'Escorpião': 'Água', 'Peixes': 'Água'
  };

  // Calcular distribuição real dos elementos baseado nos planetas
  const planetSigns = [
    userData.sunSign,
    userData.moonSign,
    userData.ascendant,
    userData.mercurySign,
    userData.venusSign,
    userData.marsSign,
    userData.jupiterSign,
    userData.saturnSign,
    userData.uranusSign,
    userData.neptuneSign,
    userData.plutoSign,
  ].filter(Boolean) as string[];

  const elementCounts = {
    'Fogo': 0,
    'Terra': 0,
    'Ar': 0,
    'Água': 0
  };

  planetSigns.forEach(sign => {
    const element = signToElement[sign];
    if (element) {
      elementCounts[element]++;
    }
  });

  const total = planetSigns.length || 1; // Evitar divisão por zero

  const elementDataWithCounts = [
    { 
      name: language === 'pt' ? 'Fogo' : 'Fire', 
      percentage: Math.round((elementCounts['Fogo'] / total) * 100), 
      color: '#F97316',
      count: elementCounts['Fogo']
    },
    { 
      name: language === 'pt' ? 'Terra' : 'Earth', 
      percentage: Math.round((elementCounts['Terra'] / total) * 100), 
      color: '#22C55E',
      count: elementCounts['Terra']
    },
    { 
      name: language === 'pt' ? 'Ar' : 'Air', 
      percentage: Math.round((elementCounts['Ar'] / total) * 100), 
      color: '#3B82F6',
      count: elementCounts['Ar']
    },
    { 
      name: language === 'pt' ? 'Água' : 'Water', 
      percentage: Math.round((elementCounts['Água'] / total) * 100), 
      color: '#8B5CF6',
      count: elementCounts['Água']
    },
  ];

  // ElementData para o gráfico (sem count)
  const elementData = elementDataWithCounts.map(({ count, ...rest }) => rest);

  // Identificar elemento dominante e em falta
  const dominantElement = elementDataWithCounts.reduce((max, el) => el.percentage > max.percentage ? el : max);
  const missingElement = elementDataWithCounts.find(el => el.count === 0);


  useEffect(() => {
    const fetchInterpretation = async () => {
      try {
        setIsLoading(true);
        const result = await apiService.getChartRulerInterpretation({
          ascendant: ascendantSign,
          ruler: chartRuler,
          rulerSign: rulerSign,
          rulerHouse: rulerHouse,
        });
        setChartRulerInterpretation(result.interpretation);
      } catch (error) {
        console.error('Erro ao buscar interpretação:', error);
        setChartRulerInterpretation(
          language === 'pt' 
            ? `Com Ascendente em ${ascendantSign}, seu planeta regente é ${chartRuler}. Este planeta guia sua jornada de vida e influencia como você se expressa no mundo.`
            : `With Ascendant in ${ascendantSign}, your ruling planet is ${chartRuler}. This planet guides your life journey and influences how you express yourself in the world.`
        );
      } finally {
        setIsLoading(false);
      }
    };
    fetchInterpretation();
  }, [ascendantSign, chartRuler, rulerSign, rulerHouse, language]);

  const AscIcon = zodiacSigns.find(z => z.name === ascendantSign)?.icon || zodiacSigns[0].icon;
  const SunIcon = zodiacSigns.find(z => z.name === sunSign)?.icon || zodiacSigns[0].icon;
  const MoonIcon = zodiacSigns.find(z => z.name === moonSign)?.icon || zodiacSigns[0].icon;

  return (
    <div className="dashboard-section-container overview-container">
      {/* Header */}
      <div className="overview-header">
        <div className="overview-header-content">
          <h2 className="overview-title">
            {language === 'pt' ? 'Visão Geral do Seu Mapa' : 'Your Chart Overview'}
          </h2>
          <p className="overview-subtitle">
            {language === 'pt' ? 'Explore os principais elementos do seu mapa astral' : 'Explore the main elements of your birth chart'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="overview-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Big Three Cards */}
      <div className="overview-big-three">
        <div className="overview-big-three-grid">
          <div className="overview-big-three-card overview-big-three-card-sun">
            <div className="overview-big-three-card-header">
              <div className="overview-big-three-card-icon-container overview-big-three-card-icon-container-sun">
                <SunIcon size={28} className="text-foreground" />
              </div>
              <div>
                <p className="overview-big-three-card-label">{language === 'pt' ? 'Sol' : 'Sun'}</p>
                <p className="overview-big-three-card-sign">{sunSign}</p>
              </div>
            </div>
            <p className="overview-big-three-card-description">
              {language === 'pt' ? 'Sua essência e identidade central' : 'Your essence and core identity'}
            </p>
          </div>

          <div className="overview-big-three-card overview-big-three-card-moon">
            <div className="overview-big-three-card-header">
              <div className="overview-big-three-card-icon-container overview-big-three-card-icon-container-moon">
                <MoonIcon size={28} className="text-foreground" />
              </div>
              <div>
                <p className="overview-big-three-card-label">{language === 'pt' ? 'Lua' : 'Moon'}</p>
                <p className="overview-big-three-card-sign">{moonSign}</p>
              </div>
            </div>
            <p className="overview-big-three-card-description">
              {language === 'pt' ? 'Suas emoções e mundo interior' : 'Your emotions and inner world'}
            </p>
          </div>

          <div className="overview-big-three-card overview-big-three-card-asc">
            <div className="overview-big-three-card-header">
              <div className="overview-big-three-card-icon-container overview-big-three-card-icon-container-asc">
                <AscIcon size={28} className="text-foreground" />
              </div>
              <div>
                <p className="overview-big-three-card-label">{language === 'pt' ? 'Ascendente' : 'Ascendant'}</p>
                <p className="overview-big-three-card-sign">{ascendantSign}</p>
              </div>
            </div>
            <p className="overview-big-three-card-description">
              {language === 'pt' ? 'Como você se apresenta ao mundo' : 'How you present yourself to the world'}
            </p>
          </div>
        </div>
      </div>

      {/* Birth Chart Wheel */}
      <div className="overview-chart-wheel-section">
        <h3 className="overview-chart-wheel-title">
          {language === 'pt' ? 'Roda do Mapa Astral' : 'Birth Chart Wheel'}
        </h3>
        <div className="overview-chart-wheel-container">
          <BirthChartWheel userData={userData} size={500} />
        </div>
        
        {/* Legenda */}
        <div className="overview-chart-wheel-legend">
          <div className="overview-chart-wheel-legend-section">
            <h4 className="overview-chart-wheel-legend-title">
              {language === 'pt' ? 'Como ler o mapa' : 'How to read the chart'}
            </h4>
            <div className="overview-chart-wheel-legend-items">
              <div className="overview-chart-wheel-legend-item">
                <div className="overview-chart-wheel-legend-icon-container">
                  <div className="overview-chart-wheel-legend-icon-signs">
                    <span style={{ color: 'hsl(var(--primary))', fontSize: '1.5rem' }}>♈</span>
                  </div>
                </div>
                <div className="overview-chart-wheel-legend-content">
                  <p className="overview-chart-wheel-legend-label">
                    {language === 'pt' ? 'Signos do Zodíaco' : 'Zodiac Signs'}
                  </p>
                  <p className="overview-chart-wheel-legend-desc">
                    {language === 'pt' 
                      ? 'Os 12 signos na borda externa representam as constelações'
                      : 'The 12 signs on the outer edge represent the constellations'}
                  </p>
                </div>
              </div>
              
              <div className="overview-chart-wheel-legend-item">
                <div className="overview-chart-wheel-legend-icon-container">
                  <div className="overview-chart-wheel-legend-icon-planets">
                    <span style={{ color: 'hsl(var(--primary))', fontSize: '1.25rem' }}>☉</span>
                  </div>
                </div>
                <div className="overview-chart-wheel-legend-content">
                  <p className="overview-chart-wheel-legend-label">
                    {language === 'pt' ? 'Planetas' : 'Planets'}
                  </p>
                  <p className="overview-chart-wheel-legend-desc">
                    {language === 'pt' 
                      ? 'Símbolos planetários mostram onde cada planeta estava no seu nascimento'
                      : 'Planetary symbols show where each planet was at your birth'}
                  </p>
                </div>
              </div>
              
              <div className="overview-chart-wheel-legend-item">
                <div className="overview-chart-wheel-legend-icon-container">
                  <div className="overview-chart-wheel-legend-icon-houses">
                    <span style={{ color: 'hsl(var(--accent))', fontSize: '1.25rem', fontWeight: '600' }}>1</span>
                  </div>
                </div>
                <div className="overview-chart-wheel-legend-content">
                  <p className="overview-chart-wheel-legend-label">
                    {language === 'pt' ? 'Casas Astrológicas' : 'Astrological Houses'}
                  </p>
                  <p className="overview-chart-wheel-legend-desc">
                    {language === 'pt' 
                      ? 'As 12 casas dividem o mapa em áreas da vida (1-12)'
                      : 'The 12 houses divide the chart into life areas (1-12)'}
                  </p>
                </div>
              </div>
              
              <div className="overview-chart-wheel-legend-item">
                <div className="overview-chart-wheel-legend-icon-container">
                  <div className="overview-chart-wheel-legend-icon-lines">
                    <div className="overview-chart-wheel-legend-line"></div>
                  </div>
                </div>
                <div className="overview-chart-wheel-legend-content">
                  <p className="overview-chart-wheel-legend-label">
                    {language === 'pt' ? 'Linhas Divisórias' : 'Division Lines'}
                  </p>
                  <p className="overview-chart-wheel-legend-desc">
                    {language === 'pt' 
                      ? 'Separam as 12 casas astrológicas do mapa'
                      : 'Separate the 12 astrological houses of the chart'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chart Ruler & Elements Grid */}
      <div className="overview-details-grid">
        {/* Chart Ruler */}
        <div className="overview-detail-card">
          <h3 className="overview-detail-card-title">
            <UIIcons.Star size={20} className="text-primary" />
            {language === 'pt' ? 'Regente do Mapa' : 'Chart Ruler'}
          </h3>
          
          {/* Informações sobre a importância do regente */}
          <div className="overview-chart-ruler-importance">
            <div className="overview-chart-ruler-importance-header">
              <UIIcons.Info size={18} className="text-primary" />
              <h4 className="overview-chart-ruler-importance-title">
                {language === 'pt' ? 'Por que o regente do mapa é importante?' : 'Why is the chart ruler important?'}
              </h4>
            </div>
            <p className="overview-chart-ruler-importance-intro">
              {language === 'pt' 
                ? 'O regente do mapa astral é fundamental para o autoconhecimento, pois ele é o planeta que rege o seu signo ascendente, influenciando diretamente sua personalidade e energia vital. Ele funciona como um guia, revelando suas forças naturais, os tipos de energia que te impulsionam e para onde sua atenção tende a se voltar.'
                : 'The chart ruler is fundamental for self-knowledge, as it is the planet that rules your ascendant sign, directly influencing your personality and vital energy. It functions as a guide, revealing your natural strengths, the types of energy that drive you, and where your attention tends to turn.'}
            </p>
            <div className="overview-chart-ruler-importance-points">
              <div className="overview-chart-ruler-importance-point">
                <div className="overview-chart-ruler-importance-point-icon">
                  <UIIcons.Compass size={16} />
                </div>
                <div className="overview-chart-ruler-importance-point-content">
                  <p className="overview-chart-ruler-importance-point-title">
                    {language === 'pt' ? 'Guia para a personalidade' : 'Guide for personality'}
                  </p>
                  <p className="overview-chart-ruler-importance-point-text">
                    {language === 'pt' 
                      ? 'O planeta regente influencia o seu "jeito de ser", determinando características e comportamentos específicos.'
                      : 'The ruling planet influences your "way of being", determining specific characteristics and behaviors.'}
                  </p>
                </div>
              </div>
              
              <div className="overview-chart-ruler-importance-point">
                <div className="overview-chart-ruler-importance-point-icon">
                  <UIIcons.Sparkles size={16} />
                </div>
                <div className="overview-chart-ruler-importance-point-content">
                  <p className="overview-chart-ruler-importance-point-title">
                    {language === 'pt' ? 'Revela forças naturais' : 'Reveals natural strengths'}
                  </p>
                  <p className="overview-chart-ruler-importance-point-text">
                    {language === 'pt' 
                      ? 'Indica onde reside sua força, seu impulso natural e para quais áreas da vida sua atenção retorna com frequência.'
                      : 'Indicates where your strength lies, your natural drive and which areas of life your attention frequently returns to.'}
                  </p>
                </div>
              </div>
              
              <div className="overview-chart-ruler-importance-point">
                <div className="overview-chart-ruler-importance-point-icon">
                  <UIIcons.Heart size={16} />
                </div>
                <div className="overview-chart-ruler-importance-point-content">
                  <p className="overview-chart-ruler-importance-point-title">
                    {language === 'pt' ? 'Influencia emoções e instintos' : 'Influences emotions and instincts'}
                  </p>
                  <p className="overview-chart-ruler-importance-point-text">
                    {language === 'pt' 
                      ? 'Por exemplo, a Lua, planeta regente de algumas pessoas, está associada às emoções, instintos e reações emocionais, além da vida doméstica e passado.'
                      : 'For example, the Moon, ruling planet of some people, is associated with emotions, instincts and emotional reactions, as well as domestic life and the past.'}
                  </p>
                </div>
              </div>
              
              <div className="overview-chart-ruler-importance-point">
                <div className="overview-chart-ruler-importance-point-icon">
                  <UIIcons.Scale size={16} />
                </div>
                <div className="overview-chart-ruler-importance-point-content">
                  <p className="overview-chart-ruler-importance-point-title">
                    {language === 'pt' ? 'Ajuda no equilíbrio' : 'Helps with balance'}
                  </p>
                  <p className="overview-chart-ruler-importance-point-text">
                    {language === 'pt' 
                      ? 'Ao conhecer as energias do seu regente, você pode usá-las de forma consciente para harmonizar e equilibrar sua personalidade.'
                      : 'By knowing the energies of your ruler, you can use them consciously to harmonize and balance your personality.'}
                  </p>
                </div>
              </div>
              
              <div className="overview-chart-ruler-importance-point">
                <div className="overview-chart-ruler-importance-point-icon">
                  <UIIcons.BookOpen size={16} />
                </div>
                <div className="overview-chart-ruler-importance-point-content">
                  <p className="overview-chart-ruler-importance-point-title">
                    {language === 'pt' ? 'Aprofunda a interpretação' : 'Deepens interpretation'}
                  </p>
                  <p className="overview-chart-ruler-importance-point-text">
                    {language === 'pt' 
                      ? 'O regente do seu ascendente é o "regente" do seu mapa como um todo. Analisar a casa e a posição em que ele se encontra no seu mapa é essencial para uma análise mais completa.'
                      : 'The ruler of your ascendant is the "ruler" of your chart as a whole. Analyzing the house and position where it is located in your chart is essential for a more complete analysis.'}
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="overview-chart-ruler-header">
            <div className="overview-chart-ruler-icon-container">
              {planets.find(p => p.name === chartRuler)?.icon && (
                (() => {
                  const PlanetIcon = planets.find(p => p.name === chartRuler)?.icon;
                  return PlanetIcon ? <PlanetIcon size={32} className="text-primary" /> : null;
                })()
              )}
            </div>
            <div className="overview-chart-ruler-info">
              <p className="overview-chart-ruler-name">{chartRuler}</p>
              <p className="overview-chart-ruler-desc">
                {language === 'pt' ? `Regente de ${ascendantSign}` : `Ruler of ${ascendantSign}`}
              </p>
            </div>
          </div>
          {isLoading ? (
            <div className="overview-chart-ruler-loading">
              <div className="overview-chart-ruler-spinner"></div>
              <p className="overview-chart-ruler-loading-text">
                {language === 'pt' ? 'Gerando interpretação...' : 'Generating interpretation...'}
              </p>
            </div>
          ) : (
            <div className="overview-chart-ruler-content">
              {formatChartRulerText(chartRulerInterpretation)}
              
              {/* Informações Adicionais sobre o Regente */}
              <div className="overview-chart-ruler-additional-info">
                <div className="overview-chart-ruler-info-section">
                  <h4 className="overview-chart-ruler-info-title">
                    {language === 'pt' ? 'O que significa ter ' : 'What it means to have '}
                    <span className="overview-chart-ruler-info-highlight">{chartRuler}</span>
                    {language === 'pt' ? ' como regente' : ' as ruler'}
                  </h4>
                  <p className="overview-chart-ruler-info-text">
                    {currentRulerDetails.meaning[language === 'pt' ? 'pt' : 'en']}
                  </p>
                </div>

                <div className="overview-chart-ruler-info-section">
                  <h4 className="overview-chart-ruler-info-title">
                    {language === 'pt' ? 'Características principais' : 'Main characteristics'}
                  </h4>
                  <ul className="overview-chart-ruler-characteristics">
                    {currentRulerDetails.characteristics[language === 'pt' ? 'pt' : 'en'].map((char, idx) => (
                      <li key={idx} className="overview-chart-ruler-characteristic-item">
                        <span className="overview-chart-ruler-characteristic-marker">•</span>
                        {char}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="overview-chart-ruler-info-section">
                  <h4 className="overview-chart-ruler-info-title">
                    {language === 'pt' ? 'Pessoas famosas com esta regência' : 'Famous people with this rulership'}
                  </h4>
                  <div className="overview-chart-ruler-famous-people">
                    {currentRulerDetails.famousPeople[language === 'pt' ? 'pt' : 'en'].map((person, idx) => (
                      <span key={idx} className="overview-chart-ruler-famous-person">
                        {person}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="overview-chart-ruler-info-section">
                  <h4 className="overview-chart-ruler-info-title">
                    {language === 'pt' ? 'Influência na sua vida' : 'Influence on your life'}
                  </h4>
                  <p className="overview-chart-ruler-info-text">
                    {currentRulerDetails.influence[language === 'pt' ? 'pt' : 'en']}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Elements Distribution */}
        <div className="overview-detail-card">
          <h3 className="overview-detail-card-title">
            <UIIcons.Sparkles size={20} className="text-primary" />
            {language === 'pt' ? 'Distribuição dos Elementos' : 'Elements Distribution'}
          </h3>
          <div className="overview-elements-container">
            <ElementChart 
              data={elementData} 
              title="" 
            />
            
            {/* Explicação dos Elementos */}
            <div className="overview-elements-explanation" style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid hsl(var(--border))' }}>
              <h4 className="overview-elements-explanation-title" style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '1rem', color: 'hsl(var(--foreground))' }}>
                {language === 'pt' ? 'O que significam os elementos no seu mapa?' : 'What do the elements mean in your chart?'}
              </h4>
              
              <div className="overview-elements-meanings" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
                <div className="overview-element-meaning" style={{ padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'hsl(var(--muted) / 0.5)' }}>
                  <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.5' }}>
                    <strong style={{ color: '#F97316' }}>{language === 'pt' ? '🔥 Fogo' : '🔥 Fire'}</strong>: {language === 'pt' ? 'Energia, ação, entusiasmo e liderança. Você é alguém que age, toma iniciativa e busca expressar sua criatividade no mundo.' : 'Energy, action, enthusiasm and leadership. You are someone who acts, takes initiative and seeks to express your creativity in the world.'}
                  </p>
                </div>
                <div className="overview-element-meaning" style={{ padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'hsl(var(--muted) / 0.5)' }}>
                  <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.5' }}>
                    <strong style={{ color: '#22C55E' }}>{language === 'pt' ? '🌍 Terra' : '🌍 Earth'}</strong>: {language === 'pt' ? 'Praticidade, estabilidade e realização material. Você valoriza segurança, estrutura e construir coisas concretas na vida.' : 'Practicality, stability and material realization. You value security, structure and building concrete things in life.'}
                  </p>
                </div>
                <div className="overview-element-meaning" style={{ padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'hsl(var(--muted) / 0.5)' }}>
                  <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.5' }}>
                    <strong style={{ color: '#3B82F6' }}>{language === 'pt' ? '💨 Ar' : '💨 Air'}</strong>: {language === 'pt' ? 'Comunicação, intelecto e conexões sociais. Você precisa de troca de ideias, aprendizado constante e relacionar-se com pessoas.' : 'Communication, intellect and social connections. You need exchange of ideas, constant learning and relating to people.'}
                  </p>
                </div>
                <div className="overview-element-meaning" style={{ padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'hsl(var(--muted) / 0.5)' }}>
                  <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.5' }}>
                    <strong style={{ color: '#8B5CF6' }}>{language === 'pt' ? '💧 Água' : '💧 Water'}</strong>: {language === 'pt' ? 'Emoções, intuição e profundidade emocional. Você sente tudo intensamente e busca conexões profundas e autênticas.' : 'Emotions, intuition and emotional depth. You feel everything intensely and seek deep and authentic connections.'}
                  </p>
                </div>
              </div>

              {/* Explicação do desequilíbrio */}
              <div className="overview-elements-balance" style={{ marginBottom: '1.5rem' }}>
                <h5 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem', color: 'hsl(var(--foreground))' }}>
                  {language === 'pt' ? 'Por que você tem mais de alguns elementos?' : 'Why do you have more of some elements?'}
                </h5>
                <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))', marginBottom: '0.5rem' }}>
                  {language === 'pt' 
                    ? `Ter mais ${dominantElement.name.toLowerCase()} no seu mapa (${dominantElement.percentage}%) mostra que essa energia é muito presente na sua personalidade. Isso não é bom nem ruim - é simplesmente quem você é. Os elementos aparecem de forma desigual porque seus planetas estão distribuídos entre signos diferentes, cada um com seu próprio elemento.`
                    : `Having more ${dominantElement.name.toLowerCase()} in your chart (${dominantElement.percentage}%) shows that this energy is very present in your personality. This is neither good nor bad - it's simply who you are. Elements appear unevenly because your planets are distributed among different signs, each with its own element.`}
                </p>
              </div>

              {/* Como isso influencia */}
              <div className="overview-elements-influence" style={{ marginBottom: '1.5rem' }}>
                <h5 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem', color: 'hsl(var(--foreground))' }}>
                  {language === 'pt' ? 'Como isso influencia sua vida?' : 'How does this influence your life?'}
                </h5>
                <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))', marginBottom: '0.75rem' }}>
                  {language === 'pt'
                    ? `Com mais ${dominantElement.name.toLowerCase()}, você tem essa energia como sua força natural. Mas elementos em falta ou pouco presentes mostram áreas que você pode precisar desenvolver mais conscientemente.`
                    : `With more ${dominantElement.name.toLowerCase()}, you have this energy as your natural strength. But missing or low elements show areas you may need to develop more consciously.`}
                </p>
                {missingElement && (
                  <div style={{ padding: '0.75rem', borderRadius: '0.5rem', backgroundColor: 'hsl(var(--primary) / 0.1)', border: '1px solid hsl(var(--primary) / 0.2)' }}>
                    <p style={{ margin: 0, fontSize: '0.875rem', lineHeight: '1.6' }}>
                      {language === 'pt'
                        ? `💡 Você não tem planetas em signos de ${missingElement.name}, o que significa que essa energia pode ser menos natural para você. Isso não é um problema - apenas indica uma área para desenvolver ao longo da vida.`
                        : `💡 You don't have planets in ${missingElement.name} signs, which means this energy may be less natural for you. This is not a problem - it just indicates an area to develop throughout life.`}
                    </p>
                  </div>
                )}
              </div>

              {/* Dicas práticas para evoluir */}
              <div className="overview-elements-tips">
                <h5 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem', color: 'hsl(var(--foreground))' }}>
                  {language === 'pt' ? '💫 Como você pode evoluir?' : '💫 How can you evolve?'}
                </h5>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {language === 'pt' ? (
                    <>
                      <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                        <strong>• Use sua força natural:</strong> O elemento que você tem mais ({dominantElement.name.toLowerCase()}) é sua energia dominante. Use isso a seu favor - é onde você brilha naturalmente.
                      </p>
                      <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                        <strong>• Desenvolva o que falta:</strong> {missingElement 
                          ? `O elemento ${missingElement.name.toLowerCase()} está ausente no seu mapa. Pratique atividades que desenvolvam essa energia: ${missingElement.name === 'Fogo' ? 'exercícios físicos, esportes, atividades criativas e liderança' : missingElement.name === 'Terra' ? 'organização, planejamento, atividades práticas e conexão com a natureza' : missingElement.name === 'Ar' ? 'leitura, estudos, conversas profundas e networking' : 'meditação, arte, terapia e conexão emocional profunda'}.`
                          : 'Procure equilibrar todos os elementos na sua vida para uma experiência mais completa.'}
                      </p>
                      <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                        <strong>• Equilibre os extremos:</strong> Se você tem muito de um elemento (acima de 40%), pode estar exagerando nessa energia. Pratique o oposto: se tem muito Fogo, desacelere e reflita mais; se tem muita Terra, experimente mais; se tem muito Ar, conecte-se com suas emoções; se tem muita Água, aterre-se e seja mais prático.
                      </p>
                    </>
                  ) : (
                    <>
                      <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                        <strong>• Use your natural strength:</strong> The element you have most ({dominantElement.name.toLowerCase()}) is your dominant energy. Use this to your advantage - it's where you naturally shine.
                      </p>
                      <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                        <strong>• Develop what's missing:</strong> {missingElement
                          ? `The ${missingElement.name.toLowerCase()} element is missing in your chart. Practice activities that develop this energy.`
                          : 'Seek to balance all elements in your life for a more complete experience.'}
                      </p>
                      <p style={{ fontSize: '0.875rem', lineHeight: '1.6', color: 'hsl(var(--muted-foreground))' }}>
                        <strong>• Balance extremes:</strong> If you have too much of one element (above 40%), you may be overdoing this energy. Practice the opposite.
                      </p>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ===== PLANETAS =====
interface PlanetsSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

// Informações sobre cada planeta
const planetInfo = {
  pt: {
    Sol: { symbol: '☉', domain: 'Identidade, Ego, Propósito', element: 'Fogo', keywords: ['Essência', 'Vitalidade', 'Autoexpressão'] },
    Lua: { symbol: '☽', domain: 'Emoções, Inconsciente, Passado', element: 'Água', keywords: ['Intuição', 'Memória', 'Nutrição'] },
    Mercúrio: { symbol: '☿', domain: 'Comunicação, Mente, Aprendizado', element: 'Ar/Terra', keywords: ['Pensamento', 'Fala', 'Escrita'] },
    Vênus: { symbol: '♀', domain: 'Amor, Beleza, Valores', element: 'Terra/Ar', keywords: ['Afeto', 'Prazer', 'Harmonia'] },
    Marte: { symbol: '♂', domain: 'Ação, Energia, Coragem', element: 'Fogo', keywords: ['Impulso', 'Desejo', 'Conquista'] },
    Júpiter: { symbol: '♃', domain: 'Expansão, Sorte, Sabedoria', element: 'Fogo', keywords: ['Crescimento', 'Fé', 'Abundância'] },
    Saturno: { symbol: '♄', domain: 'Estrutura, Limites, Tempo', element: 'Terra', keywords: ['Disciplina', 'Maturidade', 'Karma'] },
    Urano: { symbol: '♅', domain: 'Inovação, Liberdade, Revolução', element: 'Ar', keywords: ['Originalidade', 'Mudança', 'Despertar'] },
    Netuno: { symbol: '♆', domain: 'Espiritualidade, Sonhos, Ilusão', element: 'Água', keywords: ['Imaginação', 'Compaixão', 'Transcendência'] },
    Plutão: { symbol: '♇', domain: 'Transformação, Poder, Renascimento', element: 'Água', keywords: ['Intensidade', 'Regeneração', 'Profundidade'] },
  },
  en: {
    Sun: { symbol: '☉', domain: 'Identity, Ego, Purpose', element: 'Fire', keywords: ['Essence', 'Vitality', 'Self-expression'] },
    Moon: { symbol: '☽', domain: 'Emotions, Unconscious, Past', element: 'Water', keywords: ['Intuition', 'Memory', 'Nurturing'] },
    Mercury: { symbol: '☿', domain: 'Communication, Mind, Learning', element: 'Air/Earth', keywords: ['Thought', 'Speech', 'Writing'] },
    Venus: { symbol: '♀', domain: 'Love, Beauty, Values', element: 'Earth/Air', keywords: ['Affection', 'Pleasure', 'Harmony'] },
    Mars: { symbol: '♂', domain: 'Action, Energy, Courage', element: 'Fire', keywords: ['Drive', 'Desire', 'Conquest'] },
    Jupiter: { symbol: '♃', domain: 'Expansion, Luck, Wisdom', element: 'Fire', keywords: ['Growth', 'Faith', 'Abundance'] },
    Saturn: { symbol: '♄', domain: 'Structure, Limits, Time', element: 'Earth', keywords: ['Discipline', 'Maturity', 'Karma'] },
    Uranus: { symbol: '♅', domain: 'Innovation, Freedom, Revolution', element: 'Air', keywords: ['Originality', 'Change', 'Awakening'] },
    Neptune: { symbol: '♆', domain: 'Spirituality, Dreams, Illusion', element: 'Water', keywords: ['Imagination', 'Compassion', 'Transcendence'] },
    Pluto: { symbol: '♇', domain: 'Transformation, Power, Rebirth', element: 'Water', keywords: ['Intensity', 'Regeneration', 'Depth'] },
  },
};

// Componente para formatar a interpretação dos planetas
const FormattedPlanetInterpretation = ({ 
  text, 
  language, 
  planetName,
  sign,
  house 
}: { 
  text: string; 
  language: string; 
  planetName: string;
  sign: string;
  house: number;
}) => {
  const planetData = language === 'pt' 
    ? planetInfo.pt[planetName as keyof typeof planetInfo.pt]
    : planetInfo.en[planetName as keyof typeof planetInfo.en];

  // Cores por tipo de planeta
  // Cores agora são aplicadas via CSS classes, não mais via Tailwind

  // Dividir o texto em parágrafos
  const paragraphs = text.split(/\n\n+/).filter(p => p.trim());

  // Agrupar por seção principal (PASSADO/KARMA, PRESENTE/ESSÊNCIA, etc.)
  interface Section {
    mainTitle: string;
    mainTitleRaw: string;
    subsections: Array<{
      subTitle: string;
      content: string;
      color: string;
    }>;
  }

  const sections: Section[] = [];
  let currentSection: Section | null = null;

  paragraphs.forEach((paragraph) => {
    const trimmed = paragraph.trim();
    
    // Verificar se é um título principal (PASSADO/KARMA, PRESENTE/ESSÊNCIA, etc.)
    const mainTitleMatch = trimmed.match(/^\*\*(PASSADO|PRESENTE|FUTURO|PAST|PRESENT|FUTURE)[\s\/]*(KARMA|ESSÊNCIA|EVOLUÇÃO|KARMA|ESSENCE|EVOLUTION)?\*\*\s*$/i);
    
    if (mainTitleMatch) {
      // Salvar seção anterior se existir
      if (currentSection && currentSection.subsections.length > 0) {
        sections.push(currentSection);
      }
      
      // Criar nova seção principal
      currentSection = {
        mainTitle: trimmed.replace(/^\*\*|\*\*$/g, ''),
        mainTitleRaw: trimmed,
        subsections: []
      };
    } else if (currentSection) {
      // Identificar tipo de subseção
      const lowerP = paragraph.toLowerCase();
      let subTitle = language === 'pt' ? 'Análise' : 'Analysis';
      let color = 'text-purple-500';
      
      if (lowerP.includes('personalidade') || lowerP.includes('personality') || lowerP.includes('essência') || lowerP.includes('essence')) {
        subTitle = language === 'pt' ? 'Personalidade' : 'Personality';
        color = 'text-blue-500';
      } else if (lowerP.includes('desafio') || lowerP.includes('challenge') || lowerP.includes('dificuldade') || lowerP.includes('difficulty')) {
        subTitle = language === 'pt' ? 'Desafios' : 'Challenges';
        color = 'text-red-500';
      } else if (lowerP.includes('potencial') || lowerP.includes('potential') || lowerP.includes('talento') || lowerP.includes('talent') || lowerP.includes('dom') || lowerP.includes('gift')) {
        subTitle = language === 'pt' ? 'Potenciais e Dons' : 'Potentials and Gifts';
        color = 'text-emerald-500';
      } else if (lowerP.includes('conselho') || lowerP.includes('advice') || lowerP.includes('orientação') || lowerP.includes('guidance') || lowerP.includes('recomend')) {
        subTitle = language === 'pt' ? 'Orientações' : 'Guidance';
        color = 'text-amber-500';
      } else if (lowerP.includes('relacionamento') || lowerP.includes('relationship') || lowerP.includes('amor') || lowerP.includes('love')) {
        subTitle = language === 'pt' ? 'Relacionamentos' : 'Relationships';
        color = 'text-pink-500';
      } else if (lowerP.includes('carreira') || lowerP.includes('career') || lowerP.includes('profissão') || lowerP.includes('profession') || lowerP.includes('trabalho') || lowerP.includes('work')) {
        subTitle = language === 'pt' ? 'Carreira' : 'Career';
        color = 'text-indigo-500';
      }
      
      currentSection.subsections.push({
        subTitle,
        content: paragraph,
        color
      });
    }
  });

  // Adicionar última seção
  if (currentSection && currentSection.subsections.length > 0) {
    sections.push(currentSection);
  }

  return (
    <div className="planet-interpretation-container">
      {/* Header do Planeta */}
      <div className={`planet-interpretation-header planet-interpretation-header-${planetName.toLowerCase()}`}>
        <div className="planet-interpretation-header-content">
          <div className="planet-interpretation-icon-container">
            <span className={`planet-interpretation-icon planet-interpretation-icon-${planetName.toLowerCase()}`}>
              {planetData?.symbol || '★'}
            </span>
          </div>
          <div>
            <h3 className="planet-interpretation-title">
              {planetName} {language === 'pt' ? 'em' : 'in'} {sign}
            </h3>
            <p className={`planet-interpretation-meta planet-interpretation-meta-${planetName.toLowerCase()}`}>
              Casa {house} • {planetData?.domain}
            </p>
          </div>
        </div>
        
        {/* Palavras-chave */}
        {planetData?.keywords && (
          <div className="planet-interpretation-keywords">
            {planetData.keywords.map((keyword, idx) => (
              <span 
                key={idx}
                className={`planet-interpretation-keyword planet-interpretation-keyword-${planetName.toLowerCase()}`}
              >
                {keyword}
              </span>
            ))}
          </div>
        )}
        
        {/* Elemento */}
        <div className="planet-interpretation-element">
          <span className="planet-interpretation-element-label">{language === 'pt' ? 'Elemento:' : 'Element:'}</span>
          <span className={`planet-interpretation-element-value planet-interpretation-element-value-${planetName.toLowerCase()}`}>{planetData?.element}</span>
        </div>
      </div>

      {/* Seções da Interpretação */}
      {sections.length > 0 ? (
        <div className="planet-interpretation-sections">
          <h4 className="planet-interpretation-sections-title">
            {language === 'pt' ? 'Interpretação Completa' : 'Complete Interpretation'}
          </h4>
          
          {/* Card único com todos os tópicos */}
          <div className="planet-interpretation-sections-card">
            {sections.map((section, sectionIndex) => (
              <div key={sectionIndex} className="planet-interpretation-section">
                {/* Título Principal */}
                <h5 className="planet-interpretation-section-main-title">
                  {section.mainTitle}
                </h5>
                
                {/* Subseções */}
                <div className="planet-interpretation-subsections">
                  {section.subsections.map((subsection, subIndex) => (
                    <div key={subIndex} className="planet-interpretation-subsection">
                      {/* Subtítulo */}
                      <p className={`planet-interpretation-subsection-title planet-interpretation-subsection-title-${subsection.color.replace('text-', '')}`}>
                        {subsection.subTitle}
                      </p>
                      
                      {/* Conteúdo */}
                      <p className="planet-interpretation-subsection-content">
                        {subsection.content}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : text && text.trim() ? (
        // Fallback: se não houver seções estruturadas, exibir o texto diretamente
        <div className="planet-interpretation-sections">
          <h4 className="planet-interpretation-sections-title">
            {language === 'pt' ? 'Interpretação' : 'Interpretation'}
          </h4>
          <div className="planet-interpretation-sections-card">
            <div className="planet-interpretation-section">
              {paragraphs.map((paragraph, index) => (
                <p key={index} className="planet-interpretation-subsection-content" style={{ marginBottom: '1rem' }}>
                  {paragraph.trim()}
                </p>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export const PlanetsSection = ({ userData, onBack }: PlanetsSectionProps) => {
  const { language } = useLanguage();
  const [selectedPlanet, setSelectedPlanet] = useState<string | null>(null);
  const [selectedPlanetData, setSelectedPlanetData] = useState<{ sign: string; house: number } | null>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // Lista de planetas com signos reais do userData
  const planetData = [
    { name: 'Sol', nameEn: 'Sun', sign: userData.sunSign || 'Áries', house: userData.sunHouse || 1, color: 'text-orange-500', bgColor: 'bg-orange-500/10' },
    { name: 'Lua', nameEn: 'Moon', sign: userData.moonSign || 'Touro', house: userData.moonHouse || 4, color: 'text-purple-500', bgColor: 'bg-purple-500/10' },
    { name: 'Mercúrio', nameEn: 'Mercury', sign: userData.mercurySign || 'Gêmeos', house: userData.mercuryHouse || 3, color: 'text-cyan-500', bgColor: 'bg-cyan-500/10' },
    { name: 'Vênus', nameEn: 'Venus', sign: userData.venusSign || 'Touro', house: userData.venusHouse || 2, color: 'text-pink-500', bgColor: 'bg-pink-500/10' },
    { name: 'Marte', nameEn: 'Mars', sign: userData.marsSign || 'Áries', house: userData.marsHouse || 1, color: 'text-red-500', bgColor: 'bg-red-500/10' },
    { name: 'Júpiter', nameEn: 'Jupiter', sign: userData.jupiterSign || 'Sagitário', house: userData.jupiterHouse || 9, color: 'text-amber-500', bgColor: 'bg-amber-500/10' },
    { name: 'Saturno', nameEn: 'Saturn', sign: userData.saturnSign || 'Capricórnio', house: userData.saturnHouse || 10, color: 'text-muted-foreground', bgColor: 'bg-gray-500/10' },
    { name: 'Urano', nameEn: 'Uranus', sign: userData.uranusSign || 'Aquário', house: userData.uranusHouse || 11, color: 'text-teal-500', bgColor: 'bg-teal-500/10' },
    { name: 'Netuno', nameEn: 'Neptune', sign: userData.neptuneSign || 'Peixes', house: userData.neptuneHouse || 12, color: 'text-blue-500', bgColor: 'bg-blue-500/10' },
    { name: 'Plutão', nameEn: 'Pluto', sign: userData.plutoSign || 'Escorpião', house: userData.plutoHouse || 8, color: 'text-rose-500', bgColor: 'bg-rose-500/10' },
  ];

  // Categorias de planetas
  const planetCategories = {
    pt: [
      { name: 'Luminares', planets: ['Sol', 'Lua'], desc: 'A essência e as emoções' },
      { name: 'Pessoais', planets: ['Mercúrio', 'Vênus', 'Marte'], desc: 'Comunicação, amor e ação' },
      { name: 'Sociais', planets: ['Júpiter', 'Saturno'], desc: 'Expansão e estrutura' },
      { name: 'Transpessoais', planets: ['Urano', 'Netuno', 'Plutão'], desc: 'Transformação coletiva' },
    ],
    en: [
      { name: 'Luminaries', planets: ['Sun', 'Moon'], desc: 'Essence and emotions' },
      { name: 'Personal', planets: ['Mercury', 'Venus', 'Mars'], desc: 'Communication, love and action' },
      { name: 'Social', planets: ['Jupiter', 'Saturn'], desc: 'Expansion and structure' },
      { name: 'Transpersonal', planets: ['Uranus', 'Neptune', 'Pluto'], desc: 'Collective transformation' },
    ],
  };

  const fetchPlanetInterpretation = async (planetName: string, sign: string, house: number) => {
    try {
      setIsLoading(true);
      setSelectedPlanet(planetName);
      setSelectedPlanetData({ sign, house });
      
      // Validar dados antes de fazer a chamada
      if (!planetName) {
        throw new Error('Nome do planeta é obrigatório');
      }
      
      if (!sign) {
        throw new Error('Signo do planeta é obrigatório');
      }
      
      console.log('Buscando interpretação para:', { planet: planetName, sign, house });
      
      const result = await apiService.getPlanetInterpretation({
        planet: planetName,
        sign: sign,
        house: house && house > 0 ? house : undefined,
        sunSign: userData.sunSign,
        moonSign: userData.moonSign,
        ascendant: userData.ascendant,
        userName: userData.name,
      });
      
      console.log('Resultado recebido:', result);
      
      if (result && result.interpretation && result.interpretation.trim()) {
        setInterpretation(result.interpretation);
      } else {
        throw new Error('Interpretação não retornada ou está vazia');
      }
    } catch (error) {
      console.error('Erro ao buscar interpretação:', error);
      const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
      setInterpretation(
        language === 'pt'
          ? `Erro ao buscar interpretação para ${planetName} em ${sign}${house ? ` na Casa ${house}` : ''}. ${errorMessage}`
          : `Error fetching interpretation for ${planetName} in ${sign}${house ? ` in House ${house}` : ''}. ${errorMessage}`
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif text-3xl font-bold text-foreground">
            {language === 'pt' ? 'Planetas no Seu Mapa' : 'Planets in Your Chart'}
          </h2>
          <p className="text-muted-foreground mt-2">
            {language === 'pt' ? 'Explore as energias planetárias que compõem sua essência' : 'Explore the planetary energies that make up your essence'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Legenda de Categorias */}
      <div className="bg-card rounded-xl p-5 border border-border">
        <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
          <UIIcons.Info size={18} className="text-primary" />
          {language === 'pt' ? 'Categorias Planetárias' : 'Planetary Categories'}
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {(language === 'pt' ? planetCategories.pt : planetCategories.en).map((cat, idx) => (
            <div key={idx} className="p-3 rounded-lg bg-muted/50 text-center">
              <p className="font-medium text-sm text-foreground">{cat.name}</p>
              <p className="text-xs text-muted-foreground mt-1">{cat.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Planets Grid */}
      <div>
        <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2">
          <UIIcons.Star size={18} className="text-primary" />
          {language === 'pt' ? 'Seus Planetas' : 'Your Planets'}
        </h3>
        <p className="text-sm text-muted-foreground mb-4">
          {language === 'pt' 
            ? 'Clique em qualquer planeta para ver sua análise completa abaixo' 
            : 'Click on any planet to see its complete analysis below'}
        </p>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {planetData.map((planet, index) => {
          const PlanetIcon = planets[index]?.icon;
          const SignIcon = zodiacSigns.find(z => z.name === planet.sign)?.icon;
          const isSelected = selectedPlanet === planet.name;
          const info = language === 'pt' 
            ? planetInfo.pt[planet.name as keyof typeof planetInfo.pt]
            : planetInfo.en[planet.nameEn as keyof typeof planetInfo.en];
          
          // Validar se o planeta tem signo antes de renderizar
          if (!planet.sign) {
            console.warn(`Planeta ${planet.name} não tem signo definido`);
            return null;
          }
          
          return (
            <button
              key={planet.name}
              onClick={() => {
                console.log('Clique no planeta:', planet.name, 'Signo:', planet.sign, 'Casa:', planet.house);
                fetchPlanetInterpretation(planet.name, planet.sign, planet.house || 0);
              }}
              className={`p-4 rounded-xl border transition-all hover:scale-105 ${
                isSelected 
                    ? `${planet.bgColor} border-current shadow-lg` 
                  : 'bg-card border-border hover:border-primary/50'
              }`}
            >
              <div className="flex flex-col items-center gap-3">
                  <div className={`w-12 h-12 rounded-full ${planet.bgColor} flex items-center justify-center`}>
                    {PlanetIcon && <PlanetIcon size={28} className={planet.color} />}
                  </div>
                <div className="text-center">
                    <p className={`font-semibold ${isSelected ? planet.color : 'text-foreground'}`}>
                      {language === 'pt' ? planet.name : planet.nameEn}
                    </p>
                    <p className="text-lg font-bold text-muted-foreground">{info?.symbol || '?'}</p>
                  <div className="flex items-center justify-center gap-1 mt-1">
                    {SignIcon && <SignIcon size={14} className="text-muted-foreground" />}
                    <p className="text-xs text-muted-foreground">{planet.sign}</p>
                  </div>
                    {planet.house && planet.house > 0 && (
                      <p className="text-xs text-muted-foreground">
                        {language === 'pt' ? 'Casa' : 'House'} {planet.house}
                      </p>
                    )}
                </div>
              </div>
            </button>
          );
        })}
        </div>
      </div>

      {/* Interpretation Panel */}
      {selectedPlanet && selectedPlanetData && (
        <div className="bg-card rounded-xl p-6 border border-border animate-fadeIn">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 gap-4">
              <UIIcons.Loader className="w-8 h-8 animate-spin text-primary" />
              <p className="text-muted-foreground">
                {language === 'pt' ? 'Analisando o planeta...' : 'Analyzing the planet...'}
              </p>
            </div>
          ) : interpretation ? (
            <FormattedPlanetInterpretation 
              text={interpretation} 
              language={language}
              planetName={selectedPlanet}
              sign={selectedPlanetData.sign}
              house={selectedPlanetData.house}
            />
          ) : (
            <div className="flex flex-col items-center justify-center py-12 gap-4">
              <UIIcons.AlertCircle className="w-8 h-8 text-muted-foreground" />
              <p className="text-muted-foreground">
                {language === 'pt' 
                  ? 'Não foi possível carregar a interpretação. Tente novamente.' 
                  : 'Could not load interpretation. Please try again.'}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ===== CASAS =====
interface HousesSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const HousesSection = ({ userData, onBack }: HousesSectionProps) => {
  const { language } = useLanguage();
  const [selectedHouse, setSelectedHouse] = useState<number | null>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const houseMeanings = {
    pt: [
      { house: 1, title: 'Identidade', desc: 'Aparência física, personalidade e primeira impressão' },
      { house: 2, title: 'Recursos', desc: 'Finanças pessoais, valores e posses materiais' },
      { house: 3, title: 'Comunicação', desc: 'Irmãos, vizinhos, estudos e aprendizado' },
      { house: 4, title: 'Lar', desc: 'Família, raízes, lar e vida doméstica' },
      { house: 5, title: 'Criatividade', desc: 'Romance, filhos, diversão e hobbies' },
      { house: 6, title: 'Rotina', desc: 'Saúde, trabalho diário e prestação de serviço' },
      { house: 7, title: 'Parcerias', desc: 'Casamento, sociedades e contratos' },
      { house: 8, title: 'Transformação', desc: 'Crises, heranças, sexualidade e recursos compartilhados' },
      { house: 9, title: 'Expansão', desc: 'Viagens longas, filosofia e ensino superior' },
      { house: 10, title: 'Carreira', desc: 'Profissão, vocação, status e reputação pública' },
      { house: 11, title: 'Amizades', desc: 'Grupos, redes sociais, sonhos e causas coletivas' },
      { house: 12, title: 'Espiritualidade', desc: 'Inconsciente, karma, isolamento e transcendência' },
    ],
    en: [
      { house: 1, title: 'Identity', desc: 'Physical appearance, personality and first impression' },
      { house: 2, title: 'Resources', desc: 'Personal finances, values and material possessions' },
      { house: 3, title: 'Communication', desc: 'Siblings, neighbors, studies and learning' },
      { house: 4, title: 'Home', desc: 'Family, roots, home and domestic life' },
      { house: 5, title: 'Creativity', desc: 'Romance, children, fun and hobbies' },
      { house: 6, title: 'Routine', desc: 'Health, daily work and service provision' },
      { house: 7, title: 'Partnerships', desc: 'Marriage, partnerships and contracts' },
      { house: 8, title: 'Transformation', desc: 'Crises, inheritance, sexuality and shared resources' },
      { house: 9, title: 'Expansion', desc: 'Long travels, philosophy and higher education' },
      { house: 10, title: 'Career', desc: 'Profession, vocation, status and public reputation' },
      { house: 11, title: 'Friendships', desc: 'Groups, social networks, dreams and collective causes' },
      { house: 12, title: 'Spirituality', desc: 'Unconscious, karma, isolation and transcendence' },
    ],
  };

  const houses = houseMeanings[language === 'pt' ? 'pt' : 'en'];

  const fetchHouseInterpretation = async (house: number) => {
    try {
      setIsLoading(true);
      setSelectedHouse(house);
      const result = await apiService.getInterpretation({
        house: house,
        custom_query: `Casa ${house} no mapa astral significado interpretação áreas da vida`,
        use_groq: true,
      });
      setInterpretation(result.interpretation);
    } catch (error) {
      console.error('Erro ao buscar interpretação:', error);
      const houseData = houses.find(h => h.house === house);
      setInterpretation(
        language === 'pt'
          ? `A Casa ${house} rege ${houseData?.desc}. Esta área do mapa revela como você lida com esses temas na sua vida.`
          : `House ${house} rules ${houseData?.desc}. This area of the chart reveals how you handle these themes in your life.`
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard-section-container">
      {/* Header */}
      <div className="section-header">
        <div className="section-header-content">
          <h2 className="section-title">
            {language === 'pt' ? 'As 12 Casas Astrológicas' : 'The 12 Astrological Houses'}
          </h2>
          <p className="section-subtitle">
            {language === 'pt' ? 'Cada casa representa uma área da sua vida' : 'Each house represents an area of your life'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="section-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Explicação */}
      <div className="houses-info-container">
        <div className="houses-info-content">
          <div className="houses-info-icon">
            <UIIcons.Info size={20} className="text-primary" />
          </div>
          <div className="houses-info-text">
            <h3 className="houses-info-title">
              {language === 'pt' ? 'Como usar esta seção' : 'How to use this section'}
            </h3>
            <p className="houses-info-description">
              {language === 'pt' 
                ? 'As 12 casas astrológicas dividem o mapa natal em áreas específicas da vida, cada uma representando diferentes aspectos da sua experiência humana. Clique em qualquer uma das casas abaixo para ver uma análise personalizada baseada no seu mapa natal.'
                : 'The 12 astrological houses divide the birth chart into specific life areas, each representing different aspects of your human experience. Click on any house below to see a personalized analysis based on your birth chart.'}
            </p>
            <div className="houses-info-categories">
              <div className="houses-info-category">
                <span className="houses-info-category-bullet">•</span>
                <span className="houses-info-category-text">
                  {language === 'pt' ? 'Casas 1-4: Identidade e Fundamentos' : 'Houses 1-4: Identity and Foundations'}
                </span>
              </div>
              <div className="houses-info-category">
                <span className="houses-info-category-bullet">•</span>
                <span className="houses-info-category-text">
                  {language === 'pt' ? 'Casas 5-8: Criatividade e Relações' : 'Houses 5-8: Creativity and Relationships'}
                </span>
              </div>
              <div className="houses-info-category">
                <span className="houses-info-category-bullet">•</span>
                <span className="houses-info-category-text">
                  {language === 'pt' ? 'Casas 9-12: Expansão e Transcendência' : 'Houses 9-12: Expansion and Transcendence'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Houses Grid */}
      <div className="houses-list-container">
        <h3 className="houses-list-title">
          <UIIcons.Home size={18} className="text-primary" />
          {language === 'pt' ? 'Selecione uma Casa para Ver a Análise' : 'Select a House to See the Analysis'}
        </h3>
        <div className="houses-grid">
          {houses.map((house) => {
            const isSelected = selectedHouse === house.house;
            return (
              <button
                key={house.house}
                onClick={() => fetchHouseInterpretation(house.house)}
                className={`house-card ${isSelected ? 'selected' : ''}`}
              >
                <div className="house-card-number">
                  {house.house}
                </div>
                <p className="house-card-title">{house.title}</p>
                <p className="house-card-desc">{house.desc}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Interpretation Panel */}
      {selectedHouse && (
        <div className="house-interpretation-panel">
          <div className="house-interpretation-header">
            <div className="house-interpretation-number">
              {selectedHouse}
            </div>
            <div className="house-interpretation-title-container">
              <h3 className="house-interpretation-title">
                Casa {selectedHouse}: {houses.find(h => h.house === selectedHouse)?.title}
              </h3>
              <div className="house-interpretation-meta">
                <UIIcons.Home size={14} />
                <span>{houses.find(h => h.house === selectedHouse)?.desc}</span>
              </div>
            </div>
          </div>

          {isLoading ? (
            <div className="house-loading-container">
              <UIIcons.Loader className="house-loading-spinner" />
              <p className="house-loading-text">
                {language === 'pt' ? 'Buscando interpretação personalizada...' : 'Fetching personalized interpretation...'}
              </p>
            </div>
          ) : (
            <div className="house-interpretation-content">
              <div className="house-interpretation-divider"></div>
              <div className="house-interpretation-text">
                {interpretation.split('\n\n').map((paragraph, idx) => {
                  // Detecta se é um título/tópico (linhas que começam com maiúscula e terminam com :)
                  const isHeading = paragraph.match(/^[A-ZÁÀÂÃÉÊÍÓÔÕÚÇ][^.!?]*:$/);
                  // Detecta listas com marcadores
                  const isList = paragraph.includes('\n-') || paragraph.includes('\n•') || paragraph.includes('\n*');
                  
                  if (isHeading) {
                    return (
                      <h4 key={idx} className="house-interpretation-heading">
                        <span className="house-interpretation-heading-bullet"></span>
                        {paragraph.replace(':', '')}
                      </h4>
                    );
                  } else if (isList) {
                    const items = paragraph.split('\n').filter(line => line.trim());
                    return (
                      <ul key={idx} className="house-interpretation-list">
                        {items.map((item, i) => {
                          const cleanItem = item.replace(/^[-•*]\s*/, '').trim();
                          if (!cleanItem) return null;
                          return (
                            <li key={i} className="house-interpretation-list-item">
                              <span className="house-interpretation-list-bullet">•</span>
                              <span>{cleanItem}</span>
                            </li>
                          );
                        })}
                      </ul>
                    );
                  } else if (paragraph.trim()) {
                    return (
                      <p key={idx} className="house-interpretation-text">
                        {paragraph}
                      </p>
                    );
                  }
                  return null;
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ===== GUIA 2026 =====
interface Guide2026SectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const Guide2026Section = ({ userData, onBack }: Guide2026SectionProps) => {
  const { language } = useLanguage();

  // Destaques astrológicos de 2026
  const highlights = language === 'pt' ? [
    { icon: '♃', title: 'Júpiter em Câncer', period: 'Jun 2025 - Jul 2026', desc: 'Expansão emocional e familiar', color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { icon: '♄', title: 'Saturno em Áries', period: 'Mar 2025 - Mai 2026', desc: 'Novos começos estruturados', color: 'text-muted-foreground', bg: 'bg-gray-500/10' },
    { icon: '♅', title: 'Urano em Gêmeos', period: 'Jul 2025 - 2033', desc: 'Revolução na comunicação', color: 'text-teal-500', bg: 'bg-teal-500/10' },
    { icon: '♆', title: 'Netuno em Áries', period: 'Mar 2025 - 2039', desc: 'Nova era espiritual', color: 'text-blue-500', bg: 'bg-blue-500/10' },
  ] : [
    { icon: '♃', title: 'Jupiter in Cancer', period: 'Jun 2025 - Jul 2026', desc: 'Emotional and family expansion', color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { icon: '♄', title: 'Saturn in Aries', period: 'Mar 2025 - May 2026', desc: 'Structured new beginnings', color: 'text-muted-foreground', bg: 'bg-gray-500/10' },
    { icon: '♅', title: 'Uranus in Gemini', period: 'Jul 2025 - 2033', desc: 'Communication revolution', color: 'text-teal-500', bg: 'bg-teal-500/10' },
    { icon: '♆', title: 'Neptune in Aries', period: 'Mar 2025 - 2039', desc: 'New spiritual era', color: 'text-blue-500', bg: 'bg-blue-500/10' },
  ];

  return (
    <div className="transits-section-container">
      {/* Header */}
      <div className="transits-header">
        <div className="transits-header-content">
          <h2 className="transits-title">
            {language === 'pt' ? 'Trânsitos Astrológicos' : 'Astrological Transits'}
          </h2>
          <p className="transits-subtitle">
            {language === 'pt' ? 'Acompanhe os movimentos planetários e suas influências' : 'Track planetary movements and their influences'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="transits-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Destaques do Ano */}
      <div className="transits-highlights-card">
        <h3 className="transits-highlights-title">
          <UIIcons.Star size={18} style={{ color: 'hsl(var(--primary))' }} />
          {language === 'pt' ? 'Destaques Astrológicos' : 'Astrological Highlights'}
        </h3>
        <div className="transits-highlights-grid">
          {highlights.map((item, idx) => (
            <div key={idx} className="transits-highlight-item" style={{
              backgroundColor: item.bg.includes('amber') ? 'hsl(45, 90%, 60% / 0.1)' :
                              item.bg.includes('gray') ? 'hsl(0, 0%, 50% / 0.1)' :
                              item.bg.includes('teal') ? 'hsl(173, 80%, 40% / 0.1)' :
                              item.bg.includes('blue') ? 'hsl(217, 91%, 60% / 0.1)' : 'hsl(var(--muted) / 0.1)',
              borderColor: item.bg.includes('amber') ? 'hsl(45, 90%, 60% / 0.3)' :
                          item.bg.includes('gray') ? 'hsl(0, 0%, 50% / 0.3)' :
                          item.bg.includes('teal') ? 'hsl(173, 80%, 40% / 0.3)' :
                          item.bg.includes('blue') ? 'hsl(217, 91%, 60% / 0.3)' : 'hsl(var(--border) / 0.5)'
            }}>
              <div className="transits-highlight-header">
                <span className="transits-highlight-icon" style={{
                  color: item.color.includes('amber') ? 'hsl(45, 90%, 60%)' :
                         item.color.includes('muted') ? 'hsl(var(--muted-foreground))' :
                         item.color.includes('teal') ? 'hsl(173, 80%, 40%)' :
                         item.color.includes('blue') ? 'hsl(217, 91%, 60%)' : 'hsl(var(--foreground))'
                }}>{item.icon}</span>
                <span className="transits-highlight-period">{item.period}</span>
              </div>
              <p className="transits-highlight-title" style={{
                color: item.color.includes('amber') ? 'hsl(45, 90%, 60%)' :
                       item.color.includes('muted') ? 'hsl(var(--muted-foreground))' :
                       item.color.includes('teal') ? 'hsl(173, 80%, 40%)' :
                       item.color.includes('blue') ? 'hsl(217, 91%, 60%)' : 'hsl(var(--foreground))'
              }}>{item.title}</p>
              <p className="transits-highlight-desc">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Legenda de Tipos de Trânsitos */}
      <div className="transits-legend-card">
        <h3 className="transits-legend-title">
          <UIIcons.Info size={18} style={{ color: 'hsl(var(--primary))' }} />
          {language === 'pt' ? 'Tipos de Trânsitos' : 'Transit Types'}
        </h3>
        <div className="transits-legend-grid">
          <div className="transits-legend-item" style={{
            backgroundColor: 'hsl(45, 90%, 60% / 0.15)',
            borderColor: 'hsl(45, 90%, 60% / 0.3)'
          }}>
            <span className="transits-legend-icon">🌟</span>
            <div className="transits-legend-content">
              <p className="transits-legend-name">{language === 'pt' ? 'Expansão' : 'Expansion'}</p>
              <p className="transits-legend-planet">{language === 'pt' ? 'Júpiter' : 'Jupiter'}</p>
            </div>
          </div>
          <div className="transits-legend-item" style={{
            backgroundColor: 'hsl(25, 5%, 45% / 0.15)',
            borderColor: 'hsl(25, 5%, 45% / 0.3)'
          }}>
            <span className="transits-legend-icon">🏛️</span>
            <div className="transits-legend-content">
              <p className="transits-legend-name">{language === 'pt' ? 'Estrutura' : 'Structure'}</p>
              <p className="transits-legend-planet">{language === 'pt' ? 'Saturno' : 'Saturn'}</p>
            </div>
          </div>
          <div className="transits-legend-item" style={{
            backgroundColor: 'hsl(173, 80%, 40% / 0.15)',
            borderColor: 'hsl(173, 80%, 40% / 0.3)'
          }}>
            <span className="transits-legend-icon">⚡</span>
            <div className="transits-legend-content">
              <p className="transits-legend-name">{language === 'pt' ? 'Mudança' : 'Change'}</p>
              <p className="transits-legend-planet">{language === 'pt' ? 'Urano' : 'Uranus'}</p>
            </div>
          </div>
          <div className="transits-legend-item" style={{
            backgroundColor: 'hsl(280, 70%, 60% / 0.15)',
            borderColor: 'hsl(280, 70%, 60% / 0.3)'
          }}>
            <span className="transits-legend-icon">🌊</span>
            <div className="transits-legend-content">
              <p className="transits-legend-name">{language === 'pt' ? 'Espiritualidade' : 'Spirituality'}</p>
              <p className="transits-legend-planet">{language === 'pt' ? 'Netuno' : 'Neptune'}</p>
            </div>
          </div>
          <div className="transits-legend-item" style={{
            backgroundColor: 'hsl(0, 70%, 60% / 0.15)',
            borderColor: 'hsl(0, 70%, 60% / 0.3)'
          }}>
            <span className="transits-legend-icon">🔥</span>
            <div className="transits-legend-content">
              <p className="transits-legend-name">{language === 'pt' ? 'Transformação' : 'Transformation'}</p>
              <p className="transits-legend-planet">{language === 'pt' ? 'Plutão' : 'Pluto'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Future Transits Component */}
      <div>
        <h3 className="transits-highlights-title" style={{ marginBottom: '1rem' }}>
          <UIIcons.Calendar size={18} style={{ color: 'hsl(var(--primary))' }} />
          {language === 'pt' ? 'Seus Trânsitos Pessoais' : 'Your Personal Transits'}
        </h3>
        <FutureTransitsSection />
      </div>
    </div>
  );
};

// ===== ASPECTOS =====
interface AspectsSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

// Ícones de símbolo para cada aspecto
const AspectSymbols = {
  Conjunção: '☌',
  Conjunction: '☌',
  Trígono: '△',
  Trine: '△',
  Sextil: '✱',
  Sextile: '✱',
  Quadratura: '□',
  Square: '□',
  Oposição: '☍',
  Opposition: '☍',
};

// Dados detalhados dos tipos de aspectos
const aspectTypeInfo = {
  pt: {
    Conjunção: {
      symbol: '☌',
      nature: 'União / Fusão',
      description: 'Os planetas atuam juntos, fundindo suas energias. Pode ser harmonioso ou tenso dependendo dos planetas envolvidos.',
      keywords: ['Intensificação', 'Foco', 'Potencial'],
      color: 'blue',
    },
    Trígono: {
      symbol: '△',
      nature: 'Harmonioso / Fluido',
      description: 'Fluxo natural de energia entre os planetas. Talentos inatos e facilidades.',
      keywords: ['Talento Natural', 'Fluidez', 'Oportunidade'],
      color: 'green',
    },
    Sextil: {
      symbol: '✱',
      nature: 'Oportunidade / Cooperação',
      description: 'Aspectos que trazem oportunidades quando há esforço consciente para aproveitá-las.',
      keywords: ['Potencial', 'Cooperação', 'Desenvolvimento'],
      color: 'cyan',
    },
    Quadratura: {
      symbol: '□',
      nature: 'Desafio / Tensão',
      description: 'Tensão que exige ação. Conflitos internos que podem gerar grande crescimento quando trabalhados.',
      keywords: ['Desafio', 'Crescimento', 'Ação Necessária'],
      color: 'red',
    },
    Oposição: {
      symbol: '☍',
      nature: 'Polaridade / Equilíbrio',
      description: 'Forças opostas que pedem integração. Frequentemente se manifesta em relacionamentos externos.',
      keywords: ['Equilíbrio', 'Consciência', 'Integração'],
      color: 'orange',
    },
  },
  en: {
    Conjunction: {
      symbol: '☌',
      nature: 'Union / Fusion',
      description: 'The planets work together, merging their energies. Can be harmonious or tense depending on the planets involved.',
      keywords: ['Intensification', 'Focus', 'Potential'],
      color: 'blue',
    },
    Trine: {
      symbol: '△',
      nature: 'Harmonious / Fluid',
      description: 'Natural energy flow between planets. Innate talents and ease.',
      keywords: ['Natural Talent', 'Flow', 'Opportunity'],
      color: 'green',
    },
    Sextile: {
      symbol: '✱',
      nature: 'Opportunity / Cooperation',
      description: 'Aspects that bring opportunities when there is conscious effort to take advantage of them.',
      keywords: ['Potential', 'Cooperation', 'Development'],
      color: 'cyan',
    },
    Square: {
      symbol: '□',
      nature: 'Challenge / Tension',
      description: 'Tension that demands action. Internal conflicts that can generate great growth when worked on.',
      keywords: ['Challenge', 'Growth', 'Action Required'],
      color: 'red',
    },
    Opposition: {
      symbol: '☍',
      nature: 'Polarity / Balance',
      description: 'Opposing forces that ask for integration. Often manifests in external relationships.',
      keywords: ['Balance', 'Awareness', 'Integration'],
      color: 'orange',
    },
  },
};

// Componente para formatar a interpretação dos aspectos
const FormattedAspectInterpretation = ({ 
  text, 
  language, 
  planet1, 
  planet2, 
  aspectType 
}: { 
  text: string; 
  language: string; 
  planet1: string;
  planet2: string;
  aspectType: string;
}) => {
  const aspectInfo = language === 'pt' 
    ? aspectTypeInfo.pt[aspectType as keyof typeof aspectTypeInfo.pt]
    : aspectTypeInfo.en[aspectType as keyof typeof aspectTypeInfo.en];

  // Cores agora são aplicadas via CSS classes, não mais via Tailwind

  // Dividir o texto em seções se houver parágrafos
  const paragraphs = text.split(/\n\n+/).filter(p => p.trim());
  
  // Identificar seções do texto
  const identifySection = (paragraph: string): { type: string; content: string } => {
    const lowerP = paragraph.toLowerCase();
    if (lowerP.includes('energia') || lowerP.includes('energy') || lowerP.includes('dinâmica') || lowerP.includes('dynamic')) {
      return { type: 'energy', content: paragraph };
    }
    if (lowerP.includes('desafio') || lowerP.includes('challenge') || lowerP.includes('tensão') || lowerP.includes('tension')) {
      return { type: 'challenge', content: paragraph };
    }
    if (lowerP.includes('potencial') || lowerP.includes('potential') || lowerP.includes('oportunidade') || lowerP.includes('opportunity')) {
      return { type: 'potential', content: paragraph };
    }
    if (lowerP.includes('conselho') || lowerP.includes('advice') || lowerP.includes('orientação') || lowerP.includes('guidance')) {
      return { type: 'advice', content: paragraph };
    }
    return { type: 'general', content: paragraph };
  };

  const sectionIcons: Record<string, { icon: React.ReactNode; title: { pt: string; en: string }; color: string }> = {
    energy: {
      icon: <UIIcons.Zap size={20} />,
      title: { pt: '⚡ Energia da Conexão', en: '⚡ Connection Energy' },
      color: 'amber-500',
    },
    challenge: {
      icon: <UIIcons.AlertCircle size={20} />,
      title: { pt: '🔥 Desafios e Tensões', en: '🔥 Challenges and Tensions' },
      color: 'red-500',
    },
    potential: {
      icon: <UIIcons.Star size={20} />,
      title: { pt: '✨ Potenciais e Dons', en: '✨ Potentials and Gifts' },
      color: 'emerald-500',
    },
    advice: {
      icon: <UIIcons.Compass size={20} />,
      title: { pt: '🧭 Orientações Práticas', en: '🧭 Practical Guidance' },
      color: 'blue-500',
    },
    general: {
      icon: <UIIcons.BookOpen size={20} />,
      title: { pt: '📖 Interpretação', en: '📖 Interpretation' },
      color: 'purple-500',
    },
  };

  return (
    <div className="aspect-interpretation-container">
      {/* Header do Aspecto */}
      <div className={`aspect-interpretation-header aspect-interpretation-header-${aspectInfo?.color || 'blue'}`}>
        <div className="aspect-interpretation-header-content">
          <div className={`aspect-interpretation-icon-container aspect-interpretation-icon-container-${aspectInfo?.color || 'blue'}`}>
            <span className={`aspect-interpretation-icon aspect-interpretation-icon-${aspectInfo?.color || 'blue'}`}>
              {aspectInfo?.symbol || '☌'}
            </span>
          </div>
          <div>
            <h3 className="aspect-interpretation-title">
              {planet1} {aspectInfo?.symbol} {planet2}
            </h3>
            <p className={`aspect-interpretation-meta aspect-interpretation-meta-${aspectInfo?.color || 'blue'}`}>
              {aspectType} • {aspectInfo?.nature}
            </p>
          </div>
        </div>
        
        {/* Palavras-chave */}
        {aspectInfo?.keywords && (
          <div className="aspect-interpretation-keywords">
            {aspectInfo.keywords.map((keyword, idx) => (
              <span 
                key={idx}
                className={`aspect-interpretation-keyword aspect-interpretation-keyword-${aspectInfo.color}`}
              >
                {keyword}
              </span>
            ))}
          </div>
        )}
        
        <p className="aspect-interpretation-description">
          {aspectInfo?.description}
        </p>
      </div>

      {/* Seções da Interpretação */}
      {paragraphs.length > 0 && (
        <div className="aspect-interpretation-sections">
          <h4 className="aspect-interpretation-sections-title">
            <UIIcons.BookOpen size={20} className="aspect-interpretation-sections-icon" />
            {language === 'pt' ? 'Análise Detalhada' : 'Detailed Analysis'}
          </h4>
          
          {paragraphs.map((paragraph, index) => {
            const section = identifySection(paragraph);
            const sectionInfo = sectionIcons[section.type];
            
            return (
              <div 
                key={index}
                className="aspect-interpretation-section-card"
              >
                <div className="aspect-interpretation-section-content">
                  <div className={`aspect-interpretation-section-icon aspect-interpretation-section-icon-${sectionInfo.color.replace('text-', '')}`}>
                    {sectionInfo.icon}
                  </div>
                  <div className="aspect-interpretation-section-text">
                    {paragraphs.length > 1 && (
                      <p className={`aspect-interpretation-section-label aspect-interpretation-section-label-${sectionInfo.color.replace('text-', '')}`}>
                        {language === 'pt' ? sectionInfo.title.pt : sectionInfo.title.en}
                      </p>
                    )}
                    <p className="aspect-interpretation-section-paragraph">
                      {section.content}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export const AspectsSection = ({ userData, onBack }: AspectsSectionProps) => {
  const { language } = useLanguage();
  const [selectedAspect, setSelectedAspect] = useState<string | null>(null);
  const [selectedAspectData, setSelectedAspectData] = useState<{
    planet1: string;
    planet2: string;
    type: string;
    typeEn: string;
  } | null>(null);
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  // Aspectos exemplo (seriam calculados a partir dos dados reais)
  const aspects = [
    { planet1: 'Sol', planet2: 'Lua', type: 'Trígono', typeEn: 'Trine', color: 'text-green-500', bgColor: 'bg-green-500/10', symbol: '△' },
    { planet1: 'Vênus', planet2: 'Marte', type: 'Conjunção', typeEn: 'Conjunction', color: 'text-blue-500', bgColor: 'bg-blue-500/10', symbol: '☌' },
    { planet1: 'Mercúrio', planet2: 'Júpiter', type: 'Sextil', typeEn: 'Sextile', color: 'text-cyan-500', bgColor: 'bg-cyan-500/10', symbol: '✱' },
    { planet1: 'Saturno', planet2: 'Plutão', type: 'Quadratura', typeEn: 'Square', color: 'text-red-500', bgColor: 'bg-red-500/10', symbol: '□' },
    { planet1: 'Sol', planet2: 'Saturno', type: 'Oposição', typeEn: 'Opposition', color: 'text-orange-500', bgColor: 'bg-orange-500/10', symbol: '☍' },
  ];

  // Legenda detalhada dos aspectos com significado completo e ícones SVG
  const aspectLegend = language === 'pt' ? [
    { type: 'Conjunção', symbol: '☌', icon: UIIcons.ConjunctionIcon, bgColor: '#3b82f6', textColor: 'text-blue-500', desc: 'Fusão de energias', meaning: '0° - Planetas unidos, intensificam um ao outro' },
    { type: 'Trígono', symbol: '△', icon: UIIcons.TrineIcon, bgColor: '#22c55e', textColor: 'text-green-500', desc: 'Fluxo harmonioso', meaning: '120° - Talentos naturais e facilidades' },
    { type: 'Sextil', symbol: '⚹', icon: UIIcons.SextileIcon, bgColor: '#06b6d4', textColor: 'text-cyan-500', desc: 'Oportunidades', meaning: '60° - Potencial que requer ação consciente' },
    { type: 'Quadratura', symbol: '□', icon: UIIcons.SquareAspectIcon, bgColor: '#ef4444', textColor: 'text-red-500', desc: 'Desafios', meaning: '90° - Tensão que gera crescimento' },
    { type: 'Oposição', symbol: '☍', icon: UIIcons.OppositionIcon, bgColor: '#f97316', textColor: 'text-orange-500', desc: 'Polaridades', meaning: '180° - Equilíbrio entre forças opostas' },
  ] : [
    { type: 'Conjunction', symbol: '☌', icon: UIIcons.ConjunctionIcon, bgColor: '#3b82f6', textColor: 'text-blue-500', desc: 'Energy fusion', meaning: '0° - Planets united, intensify each other' },
    { type: 'Trine', symbol: '△', icon: UIIcons.TrineIcon, bgColor: '#22c55e', textColor: 'text-green-500', desc: 'Harmonious flow', meaning: '120° - Natural talents and ease' },
    { type: 'Sextile', symbol: '⚹', icon: UIIcons.SextileIcon, bgColor: '#06b6d4', textColor: 'text-cyan-500', desc: 'Opportunities', meaning: '60° - Potential requiring conscious action' },
    { type: 'Square', symbol: '□', icon: UIIcons.SquareAspectIcon, bgColor: '#ef4444', textColor: 'text-red-500', desc: 'Challenges', meaning: '90° - Tension that generates growth' },
    { type: 'Opposition', symbol: '☍', icon: UIIcons.OppositionIcon, bgColor: '#f97316', textColor: 'text-orange-500', desc: 'Polarities', meaning: '180° - Balance between opposing forces' },
  ];

  const fetchAspectInterpretation = async (planet1: string, planet2: string, aspect: string, aspectEn: string) => {
    try {
      setIsLoading(true);
      setSelectedAspect(`${planet1}-${planet2}`);
      setSelectedAspectData({ planet1, planet2, type: aspect, typeEn: aspectEn });
      const result = await apiService.getAspectInterpretation({
        planet1,
        planet2,
        aspect,
      });
      setInterpretation(result.interpretation);
    } catch (error) {
      console.error('Erro ao buscar interpretação:', error);
      setInterpretation(
        language === 'pt'
          ? `O aspecto de ${aspect} entre ${planet1} e ${planet2} cria uma dinâmica única no seu mapa. Este aspecto influencia como essas energias planetárias interagem na sua vida, revelando padrões de comportamento e áreas de desenvolvimento pessoal.`
          : `The ${aspectEn} aspect between ${planet1} and ${planet2} creates a unique dynamic in your chart. This aspect influences how these planetary energies interact in your life, revealing behavior patterns and areas of personal development.`
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dashboard-section-container">
      {/* Header */}
      <div className="section-header">
        <div className="section-header-content">
          <h2 className="section-title">
            {language === 'pt' ? 'Aspectos Planetários' : 'Planetary Aspects'}
          </h2>
          <p className="section-subtitle">
            {language === 'pt' ? 'As conexões entre os planetas do seu mapa' : 'The connections between planets in your chart'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="section-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Legenda Detalhada dos Aspectos */}
      <div className="aspects-legend-container">
        <h3 className="aspects-legend-title">
          <UIIcons.Info size={18} className="text-primary" />
          {language === 'pt' ? 'Tipos de Aspectos' : 'Aspect Types'}
        </h3>
        <div className="aspects-legend-grid">
          {aspectLegend.map((item) => {
            const IconComponent = item.icon;
            return (
              <div 
                key={item.type} 
                className="aspects-legend-item"
                style={{ 
                  borderColor: item.bgColor,
                  backgroundColor: `${item.bgColor}10` 
                }}
              >
                {/* Ícone SVG Grande */}
                <div className="aspects-legend-icon-container">
                  <div 
                    className="aspects-legend-icon-circle"
                    style={{ backgroundColor: item.bgColor }}
                  >
                    <IconComponent size={28} color="currentColor" />
                  </div>
                  <div className="aspects-legend-text">
                    <p className="aspects-legend-type">{item.type}</p>
                    <p className={`aspects-legend-desc ${item.textColor}`}>{item.desc}</p>
                  </div>
                </div>
                {/* Significado */}
                <p className="aspects-legend-meaning">
                  {item.meaning}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Lista de Aspectos */}
      <div className="aspects-list-container">
        <h3 className="aspects-list-title">
          <UIIcons.Sparkles size={18} className="text-primary" />
          {language === 'pt' ? 'Seus Aspectos' : 'Your Aspects'}
        </h3>
        <div className="aspects-list-grid">
          {aspects.map((aspect, index) => {
            const Planet1Icon = planets.find(p => p.name === aspect.planet1)?.icon;
            const Planet2Icon = planets.find(p => p.name === aspect.planet2)?.icon;
            const isSelected = selectedAspect === `${aspect.planet1}-${aspect.planet2}`;

            return (
              <button
                key={index}
                onClick={() => fetchAspectInterpretation(aspect.planet1, aspect.planet2, aspect.type, aspect.typeEn)}
                className={`aspect-card ${isSelected ? 'selected' : ''}`}
              >
                <div className="aspect-card-header">
                  <div className="aspect-card-planets">
                    {Planet1Icon && <Planet1Icon size={28} className={aspect.color} />}
                    <span className={`aspect-card-symbol ${aspect.color}`}>{aspect.symbol}</span>
                    {Planet2Icon && <Planet2Icon size={28} className={aspect.color} />}
                  </div>
                  <UIIcons.ChevronRight size={20} className={`aspect-card-chevron ${isSelected ? 'text-primary' : ''}`} />
                </div>
                <div className="aspect-card-body">
                  <p className="aspect-card-planet-names">
                    {aspect.planet1} {language === 'pt' ? 'e' : 'and'} {aspect.planet2}
                  </p>
                  <p className={`aspect-card-type ${aspect.color}`}>
                    {language === 'pt' ? aspect.type : aspect.typeEn}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Painel de Interpretação */}
      {selectedAspect && selectedAspectData && (
        <div className="aspect-interpretation-panel">
          {isLoading ? (
            <div className="aspect-loading-container">
              <UIIcons.Loader className="aspect-loading-spinner" />
              <p className="aspect-loading-text">
                {language === 'pt' ? 'Analisando o aspecto...' : 'Analyzing the aspect...'}
              </p>
            </div>
          ) : (
            <FormattedAspectInterpretation 
              text={interpretation} 
              language={language}
              planet1={selectedAspectData.planet1}
              planet2={selectedAspectData.planet2}
              aspectType={language === 'pt' ? selectedAspectData.type : selectedAspectData.typeEn}
            />
          )}
        </div>
      )}
    </div>
  );
};

// ===== NODOS LUNARES =====
interface LunarNodesSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const LunarNodesSection = ({ userData, onBack }: LunarNodesSectionProps) => {
  const { language } = useLanguage();
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  // Dados dos nodos (reais do mapa do usuário)
  const northNode = userData.northNodeSign || 'Virgem';
  const southNode = userData.southNodeSign || 'Peixes';
  const northNodeDegree = userData.northNodeDegree ? Math.floor(userData.northNodeDegree) : 0;
  const southNodeDegree = userData.southNodeDegree ? Math.floor(userData.southNodeDegree) : 0;
  
  // Saturno do usuário (importante para karma e desafios)
  const saturnSign = userData.saturnSign || 'Capricórnio';
  const saturnDegree = userData.saturnDegree ? Math.floor(userData.saturnDegree) : 0;
  
  // Quíron - a ferida do curador
  const chironSign = userData.chironSign || 'Áries';
  const chironDegree = userData.chironDegree ? Math.floor(userData.chironDegree) : 0;

  useEffect(() => {
    const fetchInterpretation = async () => {
      try {
        setIsLoading(true);
        
        // Prompt Mestre com hierarquia de corpos celestes
        const promptPt = `
**CONTEXTO DO SISTEMA:**
Você é o COSMOS ASTRAL, uma engine astrológica avançada. Sua função é gerar uma síntese coerente, não uma lista de definições.

**DIRETRIZES DE HIERARQUIA E PESO:**
- Nível 1 (Peso Máximo): Sol, Lua e Regente do Ascendente
- Nível 2 (Peso Alto): Planetas Pessoais (Mercúrio, Vênus, Marte)
- Nível 3 (Peso Médio): Nodos Lunares, Saturno, Júpiter
- Nível 4 (Peso Refinado): Quíron, Lilith, Planetas Transpessoais

**DEFINIÇÕES ESPECÍFICAS DE INTERPRETAÇÃO:**
• NODOS LUNARES: Interprete como jornada da alma - Nodo Sul (passado/zona de conforto) → Nodo Norte (futuro/desafio evolutivo)
• QUÍRON: A "ferida que vira dom". Onde a pessoa sente inadequação, mas onde se torna mestre em ajudar outros
• SATURNO: O mestre kármico que exige maturidade e onde recompensas vêm tarde, mas sólidas
• Nunca gere contradições sem explicá-las como "tensões internas de amadurecimento"
• NÃO inclua código Python, blocos de código ou períodos orbitais (29.5, 11.86, etc.) - isso não é relevante para a interpretação
• NÃO inclua informações sobre Astrologia Védica, Jyotish, zodíaco Sideral, Dasas, Vargas ou diferenças entre Tropical e Sideral

**DADOS DO NATIVO:**
- Nome: ${userData.name}
- Sol em ${userData.sunSign} (Nível 1 - Essência, Ego Consciente)
- Lua em ${userData.moonSign} (Nível 1 - Inconsciente, Emoções)
- Ascendente em ${userData.ascendant} (Nível 1 - Identidade Projetada)
- Nodo Norte em ${northNode} ${northNodeDegree}° (Nível 3 - Missão de Vida)
- Nodo Sul em ${southNode} ${southNodeDegree}° (Nível 3 - Bagagem de Vidas Passadas)
- Saturno em ${saturnSign} ${saturnDegree}° (Nível 3 - Mestre Kármico, Estrutura)
- Quíron em ${chironSign} ${chironDegree}° (Nível 4 - O Curador Ferido)

**SEÇÃO: CARMA, DESAFIOS E EVOLUÇÃO (A MISSÃO DA ALMA)**

Estruture em três blocos:

**PASSADO/KARMA:** Analise o Nodo Sul em ${southNode} como zona de conforto e padrões trazidos. Como isso se conecta com Saturno em ${saturnSign}?

**PRESENTE/ESSÊNCIA:** Como a combinação Sol em ${userData.sunSign}, Lua em ${userData.moonSign} e Ascendente em ${userData.ascendant} cria tensões ou harmonias com o eixo nodal? Onde está a ferida (Quíron em ${chironSign})?

**FUTURO/EVOLUÇÃO:** O que o Nodo Norte em ${northNode} pede como desafio evolutivo? Como transformar a ferida de Quíron em dom de cura?

**EXEMPLO DE PROFUNDIDADE:**
"Seu Nodo Sul em Libra indica que você se definiu através dos outros. Seu desafio kármico (Nodo Norte em Áries) é aprender a bancar suas vontades sozinho. Quíron em Gêmeos sugere uma ferida na comunicação - talvez você tenha sido silenciado. Mas essa mesma ferida te torna um comunicador extraordinário quando curada. Saturno em Capricórnio avisa: o reconhecimento virá tarde, mas sólido."

Escreva a análise completa para ${userData.name}, com 2-3 parágrafos por seção.
`;

        const promptEn = `
**SYSTEM CONTEXT:**
You are COSMOS ASTRAL, an advanced astrological engine. Your function is to generate a coherent synthesis, not a list of definitions.

**HIERARCHY AND WEIGHT GUIDELINES:**
- Level 1 (Maximum Weight): Sun, Moon and Ascendant Ruler
- Level 2 (High Weight): Personal Planets (Mercury, Venus, Mars)
- Level 3 (Medium Weight): Lunar Nodes, Saturn, Jupiter
- Level 4 (Refined Weight): Chiron, Lilith, Transpersonal Planets

**SPECIFIC INTERPRETATION DEFINITIONS:**
• LUNAR NODES: Interpret as soul journey - South Node (past/comfort zone) → North Node (future/evolutionary challenge)
• CHIRON: The "wound that becomes gift". Where the person feels inadequacy, but becomes a master at helping others
• SATURN: The karmic master demanding maturity, where rewards come late but solid
• Never generate contradictions without explaining them as "internal tensions of maturation"
• DO NOT include Python code, code blocks, or orbital periods (29.5, 11.86, etc.) - this is not relevant for interpretation
• DO NOT include information about Vedic Astrology, Jyotish, Sidereal zodiac, Dasas, Vargas or differences between Tropical and Sidereal

**NATIVE'S DATA:**
- Name: ${userData.name}
- Sun in ${userData.sunSign} (Level 1 - Essence, Conscious Ego)
- Moon in ${userData.moonSign} (Level 1 - Unconscious, Emotions)
- Ascendant in ${userData.ascendant} (Level 1 - Projected Identity)
- North Node in ${northNode} ${northNodeDegree}° (Level 3 - Life Mission)
- South Node in ${southNode} ${southNodeDegree}° (Level 3 - Past Lives Baggage)
- Saturn in ${saturnSign} ${saturnDegree}° (Level 3 - Karmic Master, Structure)
- Chiron in ${chironSign} ${chironDegree}° (Level 4 - The Wounded Healer)

**SECTION: KARMA, CHALLENGES AND EVOLUTION (THE SOUL'S MISSION)**

Structure in three blocks:

**PAST/KARMA:** Analyze the South Node in ${southNode} as comfort zone and brought patterns. How does this connect with Saturn in ${saturnSign}?

**PRESENT/ESSENCE:** How does the combination Sun in ${userData.sunSign}, Moon in ${userData.moonSign} and Ascendant in ${userData.ascendant} create tensions or harmonies with the nodal axis? Where is the wound (Chiron in ${chironSign})?

**FUTURE/EVOLUTION:** What does the North Node in ${northNode} ask as evolutionary challenge? How to transform Chiron's wound into healing gift?

**DEPTH EXAMPLE:**
"Your South Node in Libra indicates you defined yourself through others. Your karmic challenge (North Node in Aries) is learning to stand by your wishes alone. Chiron in Gemini suggests a wound in communication - perhaps you were silenced. But this same wound makes you an extraordinary communicator when healed. Saturn in Capricorn warns: recognition will come late, but solid."

Write the complete analysis for ${userData.name}, with 2-3 paragraphs per section.
`;

        const result = await apiService.getInterpretation({
          custom_query: language === 'pt' ? promptPt : promptEn,
          use_groq: true,
        });
        setInterpretation(result.interpretation);
      } catch (error) {
        console.error('Erro ao buscar interpretação:', error);
        setInterpretation(
          language === 'pt'
            ? `Com o Nodo Norte em ${northNode}, seu propósito de vida está ligado ao desenvolvimento das qualidades desse signo. O Nodo Sul em ${southNode} indica padrões que você traz de experiências passadas. Saturno em ${saturnSign} mostra onde estão seus maiores desafios e lições de vida.`
            : `With the North Node in ${northNode}, your life purpose is linked to developing the qualities of that sign. The South Node in ${southNode} indicates patterns you bring from past experiences. Saturn in ${saturnSign} shows where your greatest challenges and life lessons are.`
        );
      } finally {
        setIsLoading(false);
      }
    };
    fetchInterpretation();
  }, [language, northNode, southNode, saturnSign, userData]);

  const NorthIcon = zodiacSigns.find(z => z.name === northNode)?.icon;
  const SouthIcon = zodiacSigns.find(z => z.name === southNode)?.icon;
  const SaturnIcon = zodiacSigns.find(z => z.name === saturnSign)?.icon;
  const ChironIcon = zodiacSigns.find(z => z.name === chironSign)?.icon;

  return (
    <div className="lunar-nodes-section-container">
      {/* Header */}
      <div className="lunar-nodes-section-header">
        <div>
          <h2 className="lunar-nodes-section-title">
            {language === 'pt' ? 'Nodos Lunares e Saturno' : 'Lunar Nodes and Saturn'}
          </h2>
          <p className="lunar-nodes-section-subtitle">
            {language === 'pt' ? 'Seu propósito de vida, karma e lições a aprender' : 'Your life purpose, karma and lessons to learn'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="lunar-nodes-section-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Nodes, Saturn and Chiron Cards */}
      <div className="lunar-nodes-cards-grid">
        {/* North Node */}
        <div className="lunar-nodes-card lunar-nodes-card-amber">
          <div className="lunar-nodes-card-header">
            <div className="lunar-nodes-card-icon-container lunar-nodes-card-icon-container-amber">
              <UIIcons.ArrowUp size={32} className="lunar-nodes-card-icon lunar-nodes-card-icon-amber" />
            </div>
            <div>
              <p className="lunar-nodes-card-label">{language === 'pt' ? 'Nodo Norte' : 'North Node'}</p>
              <div className="lunar-nodes-card-sign-container">
                {NorthIcon && <NorthIcon size={20} className="lunar-nodes-card-sign-icon lunar-nodes-card-sign-icon-amber" />}
                <p className="lunar-nodes-card-sign-name">{northNode}</p>
              </div>
              <p className="lunar-nodes-card-degree">{northNodeDegree}°</p>
            </div>
          </div>
          <p className="lunar-nodes-card-description">
            {language === 'pt' 
              ? 'O destino e o propósito que você deve buscar nesta vida' 
              : 'The destiny and purpose you should seek in this life'}
          </p>
        </div>

        {/* South Node */}
        <div className="lunar-nodes-card lunar-nodes-card-indigo">
          <div className="lunar-nodes-card-header">
            <div className="lunar-nodes-card-icon-container lunar-nodes-card-icon-container-indigo">
              <UIIcons.ArrowDown size={32} className="lunar-nodes-card-icon lunar-nodes-card-icon-indigo" />
            </div>
            <div>
              <p className="lunar-nodes-card-label">{language === 'pt' ? 'Nodo Sul' : 'South Node'}</p>
              <div className="lunar-nodes-card-sign-container">
                {SouthIcon && <SouthIcon size={20} className="lunar-nodes-card-sign-icon lunar-nodes-card-sign-icon-indigo" />}
                <p className="lunar-nodes-card-sign-name">{southNode}</p>
              </div>
              <p className="lunar-nodes-card-degree">{southNodeDegree}°</p>
            </div>
          </div>
          <p className="lunar-nodes-card-description">
            {language === 'pt' 
              ? 'Padrões do passado que você traz como zona de conforto' 
              : 'Past patterns you bring as a comfort zone'}
          </p>
        </div>

        {/* Saturn */}
        <div className="lunar-nodes-card lunar-nodes-card-gray">
          <div className="lunar-nodes-card-header">
            <div className="lunar-nodes-card-icon-container lunar-nodes-card-icon-container-gray">
              <UIIcons.AlertCircle size={32} className="lunar-nodes-card-icon lunar-nodes-card-icon-gray" />
            </div>
            <div>
              <p className="lunar-nodes-card-label">{language === 'pt' ? 'Saturno' : 'Saturn'}</p>
              <div className="lunar-nodes-card-sign-container">
                {SaturnIcon && <SaturnIcon size={20} className="lunar-nodes-card-sign-icon lunar-nodes-card-sign-icon-gray" />}
                <p className="lunar-nodes-card-sign-name">{saturnSign}</p>
              </div>
              <p className="lunar-nodes-card-degree">{saturnDegree}°</p>
            </div>
          </div>
          <p className="lunar-nodes-card-description">
            {language === 'pt' 
              ? 'Onde estão seus maiores desafios e lições de vida' 
              : 'Where your greatest challenges and life lessons are'}
          </p>
        </div>

        {/* Chiron - A ferida do curador */}
        <div className="lunar-nodes-card lunar-nodes-card-rose">
          <div className="lunar-nodes-card-header">
            <div className="lunar-nodes-card-icon-container lunar-nodes-card-icon-container-rose">
              <UIIcons.Heart size={32} className="lunar-nodes-card-icon lunar-nodes-card-icon-rose" />
            </div>
            <div>
              <p className="lunar-nodes-card-label">{language === 'pt' ? 'Quíron' : 'Chiron'}</p>
              <div className="lunar-nodes-card-sign-container">
                {ChironIcon && <ChironIcon size={20} className="lunar-nodes-card-sign-icon lunar-nodes-card-sign-icon-rose" />}
                <p className="lunar-nodes-card-sign-name">{chironSign}</p>
              </div>
              <p className="lunar-nodes-card-degree">{chironDegree}°</p>
            </div>
          </div>
          <p className="lunar-nodes-card-description">
            {language === 'pt' 
              ? 'A ferida que pode se tornar seu maior dom de cura' 
              : 'The wound that can become your greatest healing gift'}
          </p>
        </div>
      </div>

      {/* Interpretation */}
      <div className="lunar-nodes-interpretation-card">
        <h3 className="lunar-nodes-interpretation-title">
          {language === 'pt' ? 'Interpretação do Eixo Nodal' : 'Nodal Axis Interpretation'}
        </h3>
        {isLoading ? (
          <div className="lunar-nodes-interpretation-loading">
            <UIIcons.Loader size={20} className="lunar-nodes-interpretation-loader" />
            <p className="lunar-nodes-interpretation-loading-text">
              {language === 'pt' ? 'Gerando interpretação...' : 'Generating interpretation...'}
            </p>
          </div>
        ) : (
          <FormattedInterpretation text={interpretation} language={language} />
        )}
      </div>
    </div>
  );
};

// Componente para formatar a interpretação com ícones e estrutura
const FormattedInterpretation = ({ text, language }: { text: string; language: string }) => {
  // Função para identificar e formatar seções
  const formatText = (rawText: string) => {
    // Limpar o texto de conteúdo técnico e de suporte ANTES de processar
    let cleanedText = removeSupportAndTechnicalContent(rawText);
    
    // Detectar seções comuns
    const sections: Array<{ title: string; icon: React.ReactNode; content: string; color: string }> = [];
    
    // Padrões para identificar seções
    const patterns = {
      passado: /\*?\*?(PASSADO|KARMA|Passado|Karma|passado|karma)[\/\s]*(KARMA|karma|Karma)?\*?\*?/gi,
      presente: /\*?\*?(PRESENTE|ESSÊNCIA|Presente|Essência|presente|essência)[\/\s]*(ESSÊNCIA|essência|Essência)?\*?\*?/gi,
      futuro: /\*?\*?(FUTURO|EVOLUÇÃO|Futuro|Evolução|futuro|evolução)[\/\s]*(EVOLUÇÃO|evolução|Evolução)?\*?\*?/gi,
    };

    // Dividir o texto em parágrafos
    const paragraphs: string[] = cleanedText.split(/\n\n+/);
    let currentSection: { title: string; icon: React.ReactNode; content: string[]; color: string } | null = null;
    const result: Array<{ title: string; icon: React.ReactNode; content: string; color: string }> = [];

    for (const paragraph of paragraphs) {
      const trimmed = paragraph.trim();
      if (!trimmed) continue;

      // Verificar se é uma nova seção
      let isNewSection = false;
      
      if (patterns.passado.test(trimmed)) {
        if (currentSection && currentSection.content.length > 0) {
          result.push({ 
            title: currentSection.title, 
            icon: currentSection.icon, 
            content: currentSection.content.join('\n\n'),
            color: currentSection.color
          });
        }
        currentSection = {
          title: language === 'pt' ? '🌙 Passado / Karma' : '🌙 Past / Karma',
            icon: <UIIcons.Moon size={24} className="formatted-interpretation-icon-indigo" />,
          content: [],
          color: 'indigo'
        };
        // Remover o título do parágrafo
        const cleaned = trimmed.replace(patterns.passado, '').replace(/^\*+|\*+$/g, '').trim();
        if (cleaned) currentSection.content.push(cleaned);
        isNewSection = true;
      } else if (patterns.presente.test(trimmed)) {
        if (currentSection && currentSection.content.length > 0) {
          result.push({ 
            title: currentSection.title, 
            icon: currentSection.icon, 
            content: currentSection.content.join('\n\n'),
            color: currentSection.color
          });
        }
        currentSection = {
          title: language === 'pt' ? '☀️ Presente / Essência' : '☀️ Present / Essence',
            icon: <UIIcons.Sun size={24} className="formatted-interpretation-icon-amber" />,
          content: [],
          color: 'amber'
        };
        const cleaned = trimmed.replace(patterns.presente, '').replace(/^\*+|\*+$/g, '').trim();
        if (cleaned) currentSection.content.push(cleaned);
        isNewSection = true;
      } else if (patterns.futuro.test(trimmed)) {
        if (currentSection && currentSection.content.length > 0) {
          result.push({ 
            title: currentSection.title, 
            icon: currentSection.icon, 
            content: currentSection.content.join('\n\n'),
            color: currentSection.color
          });
        }
        currentSection = {
          title: language === 'pt' ? '⭐ Futuro / Evolução' : '⭐ Future / Evolution',
            icon: <UIIcons.Star size={24} className="formatted-interpretation-icon-emerald" />,
          content: [],
          color: 'emerald'
        };
        const cleaned = trimmed.replace(patterns.futuro, '').replace(/^\*+|\*+$/g, '').trim();
        if (cleaned) currentSection.content.push(cleaned);
        isNewSection = true;
      }

      if (!isNewSection && currentSection) {
        // Limpar asteriscos e formatar
        const cleaned = trimmed.replace(/^\*+|\*+$/g, '').trim();
        if (cleaned) currentSection.content.push(cleaned);
      } else if (!isNewSection && !currentSection) {
        // Se não há seção atual, criar uma seção de resumo
        const existingSummary = result.find(r => r.title.includes('Resumo') || r.title.includes('Summary'));
        if (!existingSummary) {
          currentSection = {
            title: language === 'pt' ? '📋 Resumo' : '📋 Summary',
            icon: <UIIcons.BookOpen size={24} className="formatted-interpretation-icon-gray" />,
            content: [trimmed],
            color: 'gray'
          };
        }
      }
    }

    // Adicionar última seção
    if (currentSection && currentSection.content.length > 0) {
      result.push({ 
        title: currentSection.title, 
        icon: currentSection.icon, 
        content: currentSection.content.join('\n\n'),
        color: currentSection.color
      });
    }

    return result;
  };

  const sections = formatText(text);

  // Se não conseguiu dividir em seções, mostrar texto original formatado
  if (sections.length === 0) {
    return (
      <div className="formatted-interpretation-fallback">
        {text.split('\n\n').map((paragraph, index) => (
          <p key={index} className="formatted-interpretation-paragraph">{paragraph}</p>
        ))}
      </div>
    );
  }

  return (
    <div className="formatted-interpretation-container">
      {sections.map((section, index) => (
        <div 
          key={index} 
          className={`formatted-interpretation-section formatted-interpretation-section-${section.color}`}
        >
          {/* Título acima */}
          <h4 className="formatted-interpretation-section-title">{section.title}</h4>
          
          {/* Ícone e nome da análise */}
          <div className="formatted-interpretation-section-icon-container">
            {section.icon}
          </div>
          
          {/* Conteúdo da análise */}
          <div className="formatted-interpretation-section-content">
            {section.content.split('\n\n').filter(p => p.trim()).map((paragraph, pIndex) => {
              // Limpar o parágrafo de markdown não processado
              let cleaned = paragraph.trim();
              
              // Remover trechos técnicos específicos que não devem aparecer
              // Remover "Estrutura de Chunking Sugerida" e todo o conteúdo relacionado
              cleaned = cleaned.replace(/Estrutura de Chunking Sugerida[\s\S]*?(?=\n\n|$)/gi, '');
              cleaned = cleaned.replace(/Tópico:\s*\[.*?\]/gi, '');
              cleaned = cleaned.replace(/Categoria:\s*\[.*?\]/gi, '');
              cleaned = cleaned.replace(/Tags:\s*\[.*?\]/gi, '');
              cleaned = cleaned.replace(/Conteúdo Teórico:\s*\[.*?\]/gi, '');
              cleaned = cleaned.replace(/Conteúdo Prático:\s*\[.*?\]/gi, '');
              
              // Remover seção "Arquitetura:" e blocos de código
              cleaned = cleaned.replace(/Arquitetura:[\s\S]*?(?=\n\n|$)/gi, '');
              cleaned = cleaned.replace(/analise_ciclos\.py[\s\S]*?(?=\n\n|$)/gi, '');
              cleaned = cleaned.replace(/AnalisadorCiclos[\s\S]*?(?=\n\n|$)/gi, '');
              
              // Remover caracteres de estrutura de árvore
              cleaned = cleaned.replace(/├──[^\n]*/g, '');
              cleaned = cleaned.replace(/│\s+[^\n]*/g, '');
              cleaned = cleaned.replace(/└──[^\n]*/g, '');
              
              // Aplicar limpeza de suporte e conteúdo técnico
              cleaned = removeSupportAndTechnicalContent(cleaned);
              
              // Remover blocos de código Python com PERIODOS_ORBITAIS especificamente
              cleaned = cleaned.replace(/PERIODOS_ORBITAIS\s*=\s*\{[\s\S]*?\}/g, '');
              cleaned = cleaned.replace(/`python\s*PERIODOS_ORBITAIS[\s\S]*?`/g, '');
              cleaned = cleaned.replace(/python\s*PERIODOS_ORBITAIS[\s\S]*?(?=\n\n|$)/gi, '');
              
              // Remover informações sobre Astrologia Védica/Jyotish
              cleaned = cleaned.replace(/###\s*Astrologia Védica[\s\S]*?(?=###|$)/gi, '');
              cleaned = cleaned.replace(/Astrologia Védica \(Jyotish\)[\s\S]*?(?=\n\n|$)/gi, '');
              cleaned = cleaned.replace(/Jyotish[\s\S]*?(?=\n\n|$)/gi, '');
              cleaned = cleaned.replace(/zodíaco Sideral[\s\S]*?(?=\n\n|$)/gi, '');
              cleaned = cleaned.replace(/Diferença Tropical vs Sideral[\s\S]*?(?=\n\n|$)/gi, '');
              cleaned = cleaned.replace(/Dasas[\s\S]*?(?=\n\n|$)/gi, '');
              cleaned = cleaned.replace(/Vargas[\s\S]*?(?=\n\n|$)/gi, '');
              cleaned = cleaned.replace(/~24 graus[\s\S]*?(?=\n\n|$)/gi, '');
              
              // Remover asteriscos soltos e códigos markdown não processados
              cleaned = cleaned.replace(/^\*+\s*|\s*\*+$/g, ''); // Remove asteriscos no início/fim
              cleaned = cleaned.replace(/\*\*([^*]+)\*\*/g, '$1'); // Remove markdown **texto**
              cleaned = cleaned.replace(/\*([^*]+)\*/g, '$1'); // Remove markdown *texto*
              cleaned = cleaned.replace(/`([^`]+)`/g, '$1'); // Remove código inline
              cleaned = cleaned.replace(/```[\s\S]*?```/g, ''); // Remove blocos de código
              cleaned = cleaned.replace(/^#{1,6}\s+/gm, ''); // Remove headers markdown
              cleaned = cleaned.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1'); // Remove links markdown
              
              // Remover linhas que contêm apenas caracteres técnicos ou estruturais
              cleaned = cleaned.split('\n').filter(line => {
                const trimmed = line.trim();
                // Remover linhas que são apenas estrutura técnica
                if (/^[├│└─\s]+$/.test(trimmed)) return false;
                if (/^Tópico:|^Categoria:|^Tags:|^Conteúdo Teórico:|^Conteúdo Prático:/i.test(trimmed)) return false;
                if (/^Arquitetura:/i.test(trimmed)) return false;
                if (/analise_ciclos|AnalisadorCiclos/i.test(trimmed)) return false;
                // Remover linhas com código Python de PERIODOS_ORBITAIS
                if (/PERIODOS_ORBITAIS\s*=\s*\{/i.test(trimmed)) return false;
                if (/Saturno.*29\.5|Júpiter.*11\.86|Urano.*84\.0|Netuno.*164\.8|Plutão.*248\.0/.test(trimmed)) return false;
                // Remover linhas sobre Astrologia Védica/Jyotish
                if (/Astrologia Védica|Jyotish|zodíaco Sideral|Tropical vs Sideral|Dasas|Vargas|~24 graus/i.test(trimmed)) return false;
                // Remover linhas relacionadas a Suporte
                if (/^Suporte$/i.test(trimmed)) return false;
                if (/Para dúvidas sobre interpretação/i.test(trimmed)) return false;
                if (/Livros de astrologia na pasta/i.test(trimmed)) return false;
                if (/Análise com IA.*botão/i.test(trimmed)) return false;
                if (/Consulta com astrólogo profissional/i.test(trimmed)) return false;
                if (/Desenvolvido com.*autoconhecimento/i.test(trimmed)) return false;
                if (/^[-]{3,}$/.test(trimmed)) return false; // Remove separadores ---
                return true;
              }).join('\n');
              
              // Destacar termos importantes APÓS limpar
              const formatted = cleaned
                .replace(/\bO Nodo Norte\b/g, '**O Nodo Norte**')
                .replace(/\bO Nodo Sul\b/g, '**O Nodo Sul**')
                .replace(/\bSaturno\b/g, '**Saturno**')
                .replace(/\bSol\b(?=\s+em)/g, '**Sol**')
                .replace(/\bLua\b(?=\s+em)/g, '**Lua**')
                .replace(/\bAscendente\b/g, '**Ascendente**')
                .replace(/\bQuíron\b/g, '**Quíron**')
                .replace(/\bChiron\b/g, '**Chiron**');
              
              if (!formatted.trim()) return null;
              
              // Renderizar com negrito
              const parts = formatted.split(/\*\*(.*?)\*\*/g);
              return (
                <p key={pIndex} className="formatted-interpretation-paragraph">
                  {parts.map((part, partIndex) => 
                    partIndex % 2 === 1 ? (
                      <strong key={partIndex} className="formatted-interpretation-strong">{part}</strong>
                    ) : (
                      <span key={partIndex}>{part}</span>
                    )
                  )}
                </p>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

// ===== BIORRITMOS =====
interface BiorhythmsSectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const BiorhythmsSection = ({ userData, onBack }: BiorhythmsSectionProps) => {
  const { language } = useLanguage();
  
  // Calcular biorritmos baseados na data de nascimento
  const birthDate = userData.birthDate ? new Date(userData.birthDate) : new Date('1990-01-01');
  const today = new Date();
  const daysSinceBirth = Math.floor((today.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24));

  const physical = Math.sin((2 * Math.PI * daysSinceBirth) / 23) * 100;
  const emotional = Math.sin((2 * Math.PI * daysSinceBirth) / 28) * 100;
  const intellectual = Math.sin((2 * Math.PI * daysSinceBirth) / 33) * 100;

  const biorhythms = [
    { 
      name: language === 'pt' ? 'Físico' : 'Physical', 
      value: physical, 
      color: 'rgb(239, 68, 68)', 
      period: 23,
      desc: language === 'pt' ? 'Energia, força, coordenação' : 'Energy, strength, coordination'
    },
    { 
      name: language === 'pt' ? 'Emocional' : 'Emotional', 
      value: emotional, 
      color: 'rgb(59, 130, 246)', 
      period: 28,
      desc: language === 'pt' ? 'Humor, sensibilidade, criatividade' : 'Mood, sensitivity, creativity'
    },
    { 
      name: language === 'pt' ? 'Intelectual' : 'Intellectual', 
      value: intellectual, 
      color: 'rgb(34, 197, 94)', 
      period: 33,
      desc: language === 'pt' ? 'Raciocínio, memória, comunicação' : 'Reasoning, memory, communication'
    },
  ];

  return (
    <div className="biorhythms-section">
      {/* Header */}
      <div className="section-header">
        <div className="section-header-content">
          <h2 className="section-title">
            {language === 'pt' ? 'Seus Biorritmos' : 'Your Biorhythms'}
          </h2>
          <p className="section-subtitle">
            {language === 'pt' ? 'Ciclos naturais baseados na sua data de nascimento' : 'Natural cycles based on your birth date'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="section-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Importance Section */}
      <div className="biorhythms-importance-card">
        <div className="biorhythms-importance-header">
          <h3 className="biorhythms-importance-title">
            {language === 'pt' ? 'A Importância de Entender os Biorritmos' : 'The Importance of Understanding Biorhythms'}
          </h3>
        </div>
        <div className="biorhythms-importance-content">
          <p className="biorhythms-importance-intro">
            {language === 'pt' 
              ? 'A importância de entender os biorritmos é otimizar o bem-estar e a produtividade, ao alinhar as atividades do dia a dia com os picos naturais de energia e concentração do seu corpo. Conhecer e respeitar seu "relógio biológico" ajuda a evitar o cansaço e a irritabilidade, melhorando o humor, a autoestima e o rendimento em tarefas que exigem foco ou criatividade.'
              : 'The importance of understanding biorhythms is to optimize well-being and productivity by aligning daily activities with your body\'s natural peaks of energy and concentration. Knowing and respecting your "biological clock" helps avoid fatigue and irritability, improving mood, self-esteem and performance in tasks that require focus or creativity.'}
          </p>
          
          <h4 className="biorhythms-benefits-title">
            {language === 'pt' ? 'Principais benefícios de conhecer seus biorritmos' : 'Main benefits of knowing your biorhythms'}
          </h4>
          
          <div className="biorhythms-benefits-grid">
            <div className="biorhythms-benefit-item">
              <div className="biorhythms-benefit-icon">
                <UIIcons.TrendingUp size={24} />
              </div>
              <div className="biorhythms-benefit-content">
                <h5 className="biorhythms-benefit-name">
                  {language === 'pt' ? 'Mais produtividade' : 'More productivity'}
                </h5>
                <p className="biorhythms-benefit-desc">
                  {language === 'pt' 
                    ? 'Adequar tarefas aos seus horários de pico de concentração, como estudar pela manhã ou após o almoço, se você for matutino.'
                    : 'Adapt tasks to your peak concentration times, such as studying in the morning or after lunch, if you are a morning person.'}
                </p>
              </div>
            </div>

            <div className="biorhythms-benefit-item">
              <div className="biorhythms-benefit-icon">
                <UIIcons.Heart size={24} />
              </div>
              <div className="biorhythms-benefit-content">
                <h5 className="biorhythms-benefit-name">
                  {language === 'pt' ? 'Melhor bem-estar' : 'Better well-being'}
                </h5>
                <p className="biorhythms-benefit-desc">
                  {language === 'pt' 
                    ? 'Evitar a sensação de "preguiça" ou frustração por não conseguir ser produtivo em certos horários, percebendo que é uma questão de ajuste e não de falta de vontade.'
                    : 'Avoid the feeling of "laziness" or frustration at not being able to be productive at certain times, realizing that it is a matter of adjustment and not lack of will.'}
                </p>
              </div>
            </div>

            <div className="biorhythms-benefit-item">
              <div className="biorhythms-benefit-icon">
                <UIIcons.Zap size={24} />
              </div>
              <div className="biorhythms-benefit-content">
                <h5 className="biorhythms-benefit-name">
                  {language === 'pt' ? 'Gerenciamento de energia' : 'Energy management'}
                </h5>
                <p className="biorhythms-benefit-desc">
                  {language === 'pt' 
                    ? 'Planejar atividades físicas mais leves nos períodos de menor energia física, e aproveitar os momentos de alta criatividade para projetos inovadores.'
                    : 'Plan lighter physical activities during periods of lower physical energy, and take advantage of high creativity moments for innovative projects.'}
                </p>
              </div>
            </div>

            <div className="biorhythms-benefit-item">
              <div className="biorhythms-benefit-icon">
                <UIIcons.Shield size={24} />
              </div>
              <div className="biorhythms-benefit-content">
                <h5 className="biorhythms-benefit-name">
                  {language === 'pt' ? 'Saúde física e mental' : 'Physical and mental health'}
                </h5>
                <p className="biorhythms-benefit-desc">
                  {language === 'pt' 
                    ? 'Respeitar os ciclos do corpo pode melhorar o humor e a autoestima, pois reduz a autocrítica pela falta de produtividade em determinados momentos.'
                    : 'Respecting the body\'s cycles can improve mood and self-esteem, as it reduces self-criticism for lack of productivity at certain times.'}
                </p>
              </div>
            </div>

            <div className="biorhythms-benefit-item">
              <div className="biorhythms-benefit-icon">
                <UIIcons.RefreshCw size={24} />
              </div>
              <div className="biorhythms-benefit-content">
                <h5 className="biorhythms-benefit-name">
                  {language === 'pt' ? 'Adaptação a mudanças' : 'Adaptation to changes'}
                </h5>
                <p className="biorhythms-benefit-desc">
                  {language === 'pt' 
                    ? 'Entender os biorritmos ajuda a se adaptar melhor a mudanças como o jet lag, que é um desajuste natural do relógio biológico.'
                    : 'Understanding biorhythms helps you adapt better to changes such as jet lag, which is a natural disruption of the biological clock.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Biorhythm Cards */}
      <div className="biorhythms-cards-grid">
        {biorhythms.map((bio) => (
          <div key={bio.name} className="biorhythm-card">
            <div className="biorhythm-card-header">
              <h3 className="biorhythm-card-title">{bio.name}</h3>
              <span 
                className="biorhythm-card-value" 
                style={{ color: bio.color }}
              >
                {Math.round(Math.abs(bio.value))}%
              </span>
            </div>
            
            {/* Progress Bar */}
            <div className="biorhythm-progress-container">
              <div 
                className="biorhythm-progress-bar"
                style={{ 
                  width: `${Math.abs(bio.value)}%`,
                  backgroundColor: bio.color
                }}
              />
            </div>

            <p className="biorhythm-card-desc">{bio.desc}</p>
            <p className="biorhythm-card-period">
              {language === 'pt' ? `Ciclo de ${bio.period} dias` : `${bio.period}-day cycle`}
            </p>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="biorhythms-summary-card">
        <h3 className="biorhythms-summary-title">
          {language === 'pt' ? 'Resumo do Dia' : 'Daily Summary'}
        </h3>
        <p className="biorhythms-summary-text">
          {language === 'pt' 
            ? `Hoje você está no dia ${daysSinceBirth} desde o seu nascimento. ${
                physical > 50 ? 'Sua energia física está alta, ótimo para exercícios e atividades físicas.' :
                physical < -50 ? 'Sua energia física está baixa, priorize o descanso.' :
                'Sua energia física está moderada, mantenha um ritmo equilibrado.'
              } ${
                emotional > 50 ? 'Emocionalmente você está receptivo e criativo.' :
                emotional < -50 ? 'Emocionalmente pode ser um dia mais introspectivo.' :
                'Suas emoções estão estáveis.'
              } ${
                intellectual > 50 ? 'Mentalmente é um ótimo dia para estudos e decisões importantes.' :
                intellectual < -50 ? 'Evite decisões complexas hoje, se possível.' :
                'Seu raciocínio está funcionando normalmente.'
              }`
            : `Today you are on day ${daysSinceBirth} since your birth. ${
                physical > 50 ? 'Your physical energy is high, great for exercise and physical activities.' :
                physical < -50 ? 'Your physical energy is low, prioritize rest.' :
                'Your physical energy is moderate, maintain a balanced pace.'
              } ${
                emotional > 50 ? 'Emotionally you are receptive and creative.' :
                emotional < -50 ? 'Emotionally it may be a more introspective day.' :
                'Your emotions are stable.'
              } ${
                intellectual > 50 ? 'Mentally it is a great day for studies and important decisions.' :
                intellectual < -50 ? 'Avoid complex decisions today if possible.' :
                'Your reasoning is working normally.'
              }`
          }
        </p>
      </div>
    </div>
  );
};

// ===== SINASTRIA =====
interface SynastrySectionProps {
  userData: OnboardingData;
  onBack: () => void;
}

export const SynastrySection = ({ userData, onBack }: SynastrySectionProps) => {
  const { language } = useLanguage();
  const [partnerSign, setPartnerSign] = useState<string>('');
  const [interpretation, setInterpretation] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const userSunSign = userData.sunSign || 'Áries';

  // Função para formatar o texto da compatibilidade organizando por tópicos
  const formatCompatibilityText = (text: string): React.ReactNode => {
    if (!text || !text.trim()) {
      console.warn('[Sinastria] Texto vazio para formatar');
      return null;
    }

    // Remover conteúdo indesejado: tudo a partir de "### Astrologia Moderna" ou "## 📞 Suporte"
    let cleanedText = removeSupportAndTechnicalContent(text);
    const unwantedPatterns = [
      /###\s*Astrologia Moderna.*$/s,
      /##\s*📞\s*Suporte.*$/s,
      /###\s*Astrologia Moderna \(Psicológica\).*$/s,
      /##\s*Suporte.*$/s
    ];
    
    for (const pattern of unwantedPatterns) {
      const match = cleanedText.match(pattern);
      if (match) {
        cleanedText = cleanedText.substring(0, match.index).trim();
        break;
      }
    }

    // Dividir o texto em parágrafos (por quebras de linha duplas ou simples)
    const paragraphs = cleanedText.split(/\n\n|\n/).filter(p => p.trim());
    
    if (paragraphs.length === 0) {
      console.warn('[Sinastria] Nenhum parágrafo encontrado');
      return <p className="synastry-text-paragraph">{text}</p>;
    }
    
    // Identificar tópicos (números, bullets, títulos em negrito, etc.)
    const formattedParagraphs: React.ReactNode[] = [];
    
    // Detectar se estamos em uma seção de exemplos práticos
    let isExamplesSection = false;
    
    paragraphs.forEach((paragraph, index) => {
      const trimmed = paragraph.trim();
      if (!trimmed) return;

      // Verificar se é uma seção de exemplos práticos
      const isExamplesTitle = trimmed.toLowerCase().includes('exemplo') && 
                              (trimmed.toLowerCase().includes('prático') || trimmed.toLowerCase().includes('prática'));
      
      if (isExamplesTitle) {
        isExamplesSection = true;
        // Título da seção de exemplos
        const titleText = trimmed.replace(/\*\*/g, '').replace(/:/g, '');
        formattedParagraphs.push(
          <h4 key={index} className="synastry-examples-title">
            {titleText}
          </h4>
        );
        return;
      }

      // Se estamos na seção de exemplos, formatar como exemplo
      if (isExamplesSection) {
        // Remover bullet points se existirem
        const cleanLine = trimmed.replace(/^[•\-]\s*/, '');
        formattedParagraphs.push(
          <div key={index} className="synastry-example-item">
            <div className="synastry-example-box">
              <p className="synastry-example-text">{cleanLine}</p>
            </div>
          </div>
        );
        return;
      }

      // Verificar se é um tópico numerado (1., 2., etc.)
      const numberedMatch = trimmed.match(/^(\d+)[\.\)]\s*(.+)$/);
      // Verificar se é um bullet (-, •, etc.)
      const bulletMatch = trimmed.match(/^[-•*]\s*(.+)$/);
      // Verificar se contém texto em negrito (markdown **texto**)
      const boldMatch = trimmed.match(/\*\*(.+?)\*\*/);
      // Verificar se é um título (linha que termina com : e tem menos de 60 chars)
      const isTitle = trimmed.endsWith(':') && trimmed.length < 60 && !trimmed.includes('.');

      if (isTitle || (boldMatch && trimmed.length < 60)) {
        // Título ou texto em negrito como título
        const titleText = boldMatch ? boldMatch[1] : trimmed.replace(':', '');
        formattedParagraphs.push(
          <h4 key={index} className="synastry-text-title">
            {titleText}
          </h4>
        );
      } else if (numberedMatch) {
        // Tópico numerado
        formattedParagraphs.push(
          <div key={index} className="synastry-text-numbered">
            <span className="synastry-text-number">{numberedMatch[1]}.</span>
            <span className="synastry-text-content">{numberedMatch[2]}</span>
          </div>
        );
      } else if (bulletMatch) {
        // Tópico com bullet
        formattedParagraphs.push(
          <div key={index} className="synastry-text-bullet">
            <span className="synastry-text-bullet-marker">•</span>
            <span className="synastry-text-content">{bulletMatch[1]}</span>
          </div>
        );
      } else {
        // Parágrafo normal - processar markdown inline
        const processedText = trimmed.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        formattedParagraphs.push(
          <p 
            key={index} 
            className="synastry-text-paragraph"
            dangerouslySetInnerHTML={{ __html: processedText }}
          />
        );
      }
    });

    return <div className="synastry-text-container">{formattedParagraphs}</div>;
  };

  const fetchCompatibility = async () => {
    if (!partnerSign) {
      console.warn('[Sinastria] Nenhum signo do parceiro selecionado');
      return;
    }
    
    try {
      setIsLoading(true);
      setInterpretation(''); // Limpar interpretação anterior
      
      console.log(`[Sinastria] Buscando compatibilidade: ${userSunSign} + ${partnerSign}`);
      
      // Usar o novo endpoint específico de sinastria que busca características de cada signo
      const result = await apiService.getSynastryInterpretation({
        sign1: userSunSign,
        sign2: partnerSign,
        language: language,
      });
      
      console.log('[Sinastria] Resposta recebida:', {
        hasInterpretation: !!result?.interpretation,
        length: result?.interpretation?.length || 0,
        generatedBy: result?.generated_by,
        hasSign1Info: !!result?.sign1_info,
        hasSign2Info: !!result?.sign2_info
      });
      
      // Verificar se a interpretação foi gerada corretamente
      if (result && result.interpretation) {
        const interpretationText = result.interpretation.trim();
        
        if (interpretationText.length > 20) {
          // Se tiver conteúdo válido, usar
          setInterpretation(interpretationText);
          console.log('[Sinastria] Interpretação definida com sucesso');
        } else {
          console.warn('[Sinastria] Interpretação muito curta - pode ser que não houve informações suficientes no RAG');
          throw new Error(language === 'pt' 
            ? 'Interpretação muito curta. Pode não haver informações suficientes sobre estes signos na base de conhecimento.'
            : 'Interpretation too short. There may not be enough information about these signs in the knowledge base.');
        }
      } else {
        console.error('[Sinastria] Resposta sem interpretação válida');
        throw new Error('Resposta sem interpretação');
      }
    } catch (error: any) {
      console.error('[Sinastria] Erro ao buscar compatibilidade:', error);
      
      // Não usar fallback estático - mostrar erro real
      const errorMessage = language === 'pt'
        ? `**Erro ao gerar interpretação de sinastria**

Não foi possível gerar uma interpretação personalizada para ${userSunSign} e ${partnerSign} no momento.

**Possíveis causas:**
- Informações insuficientes na base de conhecimento sobre estes signos
- Problema temporário no serviço de interpretação
- Erro de conexão com o servidor

**O que fazer:**
- Tente novamente em alguns instantes
- Verifique sua conexão com a internet
- Se o problema persistir, entre em contato com o suporte

**Detalhes técnicos:**
${error?.message || 'Erro desconhecido'}`
        : `**Error generating synastry interpretation**

Unable to generate a personalized interpretation for ${userSunSign} and ${partnerSign} at this time.

**Possible causes:**
- Insufficient information in the knowledge base about these signs
- Temporary problem with the interpretation service
- Connection error with the server

**What to do:**
- Try again in a few moments
- Check your internet connection
- If the problem persists, contact support

**Technical details:**
${error?.message || 'Unknown error'}`;
      
      setInterpretation(errorMessage);
      console.error('[Sinastria] Erro capturado - sem fallback estático');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="section-header">
        <div className="section-header-content">
          <h2 className="section-title">
            {language === 'pt' ? 'Sinastria' : 'Synastry'}
          </h2>
          <p className="section-subtitle">
            {language === 'pt' ? 'Análise de compatibilidade entre mapas' : 'Compatibility analysis between charts'}
          </p>
        </div>
        <button
          onClick={onBack}
          className="section-back-button"
        >
          <UIIcons.ArrowLeft size={18} />
          {language === 'pt' ? 'Voltar' : 'Back'}
        </button>
      </div>

      {/* Information Card */}
      <div className="synastry-info-card">
        <h3 className="synastry-info-title">
          {language === 'pt' ? 'O que é Sinastria?' : 'What is Synastry?'}
        </h3>
        <p className="synastry-info-text">
          {language === 'pt' 
            ? 'A sinastria é uma técnica astrológica que analisa a compatibilidade entre dois mapas astrais, comparando as posições planetárias de duas pessoas para entender as dinâmicas do relacionamento. Ela revela pontos de conexão, desafios e potenciais de crescimento conjunto, ajudando a compreender melhor como as energias de cada pessoa interagem e se complementam.'
            : 'Synastry is an astrological technique that analyzes compatibility between two birth charts by comparing the planetary positions of two people to understand relationship dynamics. It reveals connection points, challenges, and potential for joint growth, helping to better understand how each person\'s energies interact and complement each other.'}
        </p>
      </div>

      {/* Your Sign */}
      <div className="synastry-user-sign-card">
        <div className="synastry-user-sign-content">
          <div className="synastry-sign-icon-container">
            {(() => {
              const SignIcon = zodiacSigns.find(z => z.name === userSunSign)?.icon;
              return SignIcon ? <SignIcon size={32} className="synastry-sign-icon" /> : null;
            })()}
          </div>
          <div>
            <p className="synastry-user-sign-label">{language === 'pt' ? 'Seu Signo Solar' : 'Your Sun Sign'}</p>
            <p className="synastry-user-sign-name">{userSunSign}</p>
          </div>
        </div>
      </div>

      {/* Partner Sign Selection */}
      <div className="synastry-partner-selection-card">
        <h3 className="synastry-partner-selection-title">
          {language === 'pt' ? 'Selecione o signo do parceiro(a)' : 'Select partner\'s sign'}
        </h3>
        <div className="synastry-signs-grid">
          {zodiacSigns.map((sign) => {
            const SignIcon = sign.icon;
            const isSelected = partnerSign === sign.name;
            return (
              <button
                key={sign.name}
                onClick={() => setPartnerSign(sign.name)}
                className={`synastry-sign-button ${isSelected ? 'synastry-sign-button-selected' : ''}`}
              >
                <div className="synastry-sign-button-icon-container">
                  <SignIcon size={24} className={`synastry-sign-button-icon ${isSelected ? 'synastry-sign-button-icon-selected' : ''}`} />
                </div>
                <p className="synastry-sign-button-name">{sign.name}</p>
              </button>
            );
          })}
        </div>
        
        {partnerSign && (
          <button
            onClick={fetchCompatibility}
            disabled={isLoading}
            className="synastry-analyze-button"
          >
            {isLoading ? (
              <span className="synastry-analyze-button-content">
                <UIIcons.Loader className="synastry-analyze-button-loader" />
                {language === 'pt' ? 'Analisando...' : 'Analyzing...'}
              </span>
            ) : (
              language === 'pt' ? 'Analisar Compatibilidade' : 'Analyze Compatibility'
            )}
          </button>
        )}
      </div>

      {/* Interpretation */}
      {interpretation ? (
        <div className="synastry-interpretation-card">
          <h3 className="synastry-interpretation-title">
            {userSunSign} + {partnerSign}
          </h3>
          <div className="synastry-interpretation-content">
            {formatCompatibilityText(interpretation)}
          </div>
        </div>
      ) : isLoading ? (
        <div className="synastry-interpretation-card">
          <div className="synastry-loading-container">
            <UIIcons.Loader className="synastry-loading-spinner" />
            <p className="synastry-loading-text">
              {language === 'pt' ? 'Analisando compatibilidade...' : 'Analyzing compatibility...'}
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
};


// Exportar SolarReturnSection
export { SolarReturnSection } from './solar-return-section';

// Exportar NumerologySection
export { NumerologySection } from './numerology-section';

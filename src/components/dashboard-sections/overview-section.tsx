import React, { useState, useEffect } from 'react';
import { UIIcons } from '../ui-icons';
import { zodiacSigns } from '../zodiac-icons';
import { planets } from '../planet-icons';
import { BirthChartWheel } from '../birth-chart-wheel';
import { ElementChart } from '../element-chart';
import { apiService } from '../../services/api';
import { useLanguage } from '../../i18n';
import { OnboardingData } from '../onboarding';
import { InlineBold } from '../ui/inline-bold';

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

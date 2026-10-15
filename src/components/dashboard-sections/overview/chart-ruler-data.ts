import { OnboardingData } from '../../onboarding';

// Planeta regente de cada signo (usado para o regente do mapa)
export const RULER_BY_SIGN: Record<string, string> = {
  'Áries': 'Marte', 'Touro': 'Vênus', 'Gêmeos': 'Mercúrio', 'Câncer': 'Lua',
  'Leão': 'Sol', 'Virgem': 'Mercúrio', 'Libra': 'Vênus', 'Escorpião': 'Plutão',
  'Sagitário': 'Júpiter', 'Capricórnio': 'Saturno', 'Aquário': 'Urano', 'Peixes': 'Netuno'
};

// Signo e casa do regente no mapa do usuário
export const getRulerSignAndHouse = (
  userData: OnboardingData,
  rulerName: string,
  fallbackSign: string
): { sign: string; house: number } => {
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
      sign: (userData[planetData.signKey] as string) || fallbackSign,
      house: (userData[planetData.houseKey] as number) || 1
    };
  }
  return { sign: fallbackSign, house: 1 };
};

// Informações detalhadas sobre cada planeta regente
export const RULER_DETAILS: Record<string, {
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

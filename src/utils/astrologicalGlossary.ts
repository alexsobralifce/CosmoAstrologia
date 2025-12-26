export type Language = 'pt' | 'en';

export interface GlossaryTerm {
  term: string;
  explanation: string;
  category: 'basic' | 'planets' | 'houses' | 'aspects' | 'points' | 'advanced';
}

export const astrologicalGlossary: Record<Language, Record<string, GlossaryTerm>> = {
  pt: {
    // Termos Básicos
    'Ascendente': {
      term: 'Ascendente',
      explanation: 'O Ascendente é o signo que estava surgindo no horizonte leste no momento do seu nascimento. Ele representa como você se apresenta ao mundo, sua máscara social, o primeiro passo na vida e como os outros te veem inicialmente. É diferente do seu signo solar e influencia muito sua aparência e personalidade exterior.',
      category: 'basic',
    },
    'Regente do Mapa': {
      term: 'Regente do Mapa',
      explanation: 'O Regente do Mapa (também chamado de Regente Ascendente) é o planeta que governa o signo do seu Ascendente. Ele é considerado o planeta mais importante do seu mapa, pois representa sua energia vital, motivação principal e a forma como você expressa sua identidade no mundo. Onde ele está posicionado mostra onde você direciona sua energia e foco.',
      category: 'basic',
    },
    'Signo Solar': {
      term: 'Signo Solar',
      explanation: 'O Signo Solar é determinado pela posição do Sol no momento do seu nascimento. Representa sua essência, identidade central, ego e a pessoa que você está se tornando. É a sua energia fundamental e como você brilha no mundo. É o signo mais conhecido e representa cerca de 30% da sua personalidade.',
      category: 'basic',
    },
    'Signo Lunar': {
      term: 'Signo Lunar',
      explanation: 'O Signo Lunar é determinado pela posição da Lua no momento do seu nascimento. Representa suas emoções, necessidades internas, instintos, memórias e como você reage emocionalmente. É sua parte mais sensível, intuitiva e relacionada ao conforto e segurança. Mostra como você processa sentimentos e busca carinho.',
      category: 'basic',
    },
    'Casas Astrológicas': {
      term: 'Casas Astrológicas',
      explanation: 'As Casas Astrológicas são 12 divisões do mapa astral que representam diferentes áreas da vida. Cada casa simboliza um cenário onde as energias dos planetas se manifestam. Por exemplo, a Casa 1 representa você mesmo, a Casa 4 sua família e lar, a Casa 7 relacionamentos, e a Casa 10 sua carreira. O planeta que está em cada casa mostra como você vivencia aquela área da vida.',
      category: 'houses',
    },
    'Casa': {
      term: 'Casa',
      explanation: 'Uma Casa Astrológica é uma das 12 divisões do mapa astral que representa áreas específicas da vida. Cada casa tem um tema: Casa 1 (identidade), Casa 2 (recursos), Casa 3 (comunicação), Casa 4 (lar), Casa 5 (criatividade), Casa 6 (trabalho), Casa 7 (relacionamentos), Casa 8 (transformação), Casa 9 (sabedoria), Casa 10 (carreira), Casa 11 (amizades), Casa 12 (espiritualidade).',
      category: 'houses',
    },
    'Aspectos': {
      term: 'Aspectos',
      explanation: 'Aspectos são ângulos formados entre planetas no mapa astral. Eles mostram como as diferentes energias planetárias interagem e se relacionam. Aspectos harmônicos (como trígono e sextil) indicam facilidades e talentos naturais. Aspectos tensos (como quadratura e oposição) indicam desafios que promovem crescimento. Os aspectos são como o "roteiro" que mostra como os planetas conversam entre si.',
      category: 'aspects',
    },
    'Trígono': {
      term: 'Trígono',
      explanation: 'O Trígono é um aspecto harmonioso de 120 graus entre dois planetas. Representa talentos naturais, facilidades e fluidez. As energias dos planetas envolvidos trabalham juntas de forma natural e espontânea. É como ter um dom inato que não requer esforço consciente para se manifestar.',
      category: 'aspects',
    },
    'Sextil': {
      term: 'Sextil',
      explanation: 'O Sextil é um aspecto harmonioso de 60 graus entre dois planetas. Representa oportunidades e cooperação. As energias se complementam e oferecem chances de crescimento quando trabalhadas intencionalmente. Diferente do trígono, o sextil precisa ser desenvolvido com esforço consciente.',
      category: 'aspects',
    },
    'Quadratura': {
      term: 'Quadratura',
      explanation: 'A Quadratura é um aspecto tenso de 90 graus entre dois planetas. Representa conflitos internos que exigem ação e resolução. É através das quadraturas que crescemos, desenvolvemos força e superamos obstáculos. São como "exercícios espirituais" que nos fortalecem, mesmo sendo desafiadores.',
      category: 'aspects',
    },
    'Oposição': {
      term: 'Oposição',
      explanation: 'A Oposição é um aspecto de 180 graus entre dois planetas, criando uma polaridade. Forças opostas pedem integração e equilíbrio. Frequentemente se manifesta em relacionamentos externos, onde encontramos pessoas que nos desafiam ou completam. É uma energia que pede consciência e negociação entre extremos.',
      category: 'aspects',
    },
    'Conjunção': {
      term: 'Conjunção',
      explanation: 'A Conjunção ocorre quando dois planetas estão próximos, com 0 graus de separação (com uma pequena tolerância chamada "orbe"). Representa a fusão de energias, onde os planetas se unem e suas qualidades se misturam. Pode ser intensa e transformadora, criando uma energia combinada única.',
      category: 'aspects',
    },
    'Nodo Norte': {
      term: 'Nodo Norte',
      explanation: 'O Nodo Norte (ou Nodo Lunar Norte) representa o destino e propósito de vida que você deve buscar nesta encarnação. É seu caminho de evolução, as qualidades que precisa desenvolver e as experiências que precisa vivenciar para crescer. Mostra para onde você deve direcionar seus esforços e onde encontrar satisfação e realização.',
      category: 'points',
    },
    'Nodo Sul': {
      term: 'Nodo Sul',
      explanation: 'O Nodo Sul (ou Nodo Lunar Sul) representa talentos, padrões e comportamentos que você já desenvolveu em vidas passadas ou na infância. São facilidades e vícios que você traz naturalmente, mas que podem te manter preso ao passado. Mostra de onde você vem e o que precisa deixar para trás para evoluir.',
      category: 'points',
    },
    'MC': {
      term: 'MC (Meio do Céu)',
      explanation: 'O MC (Meio do Céu) é o ponto mais alto do mapa astral, relacionado à Casa 10. Representa sua vocação, carreira, reputação pública, objetivos de vida e como você quer ser reconhecido no mundo. É sua imagem profissional e o legado que você quer deixar. O signo no MC mostra como você se expressa publicamente.',
      category: 'points',
    },
    'IC': {
      term: 'IC (Fundo do Céu)',
      explanation: 'O IC (Fundo do Céu) é o ponto mais baixo do mapa astral, relacionado à Casa 4. Representa suas raízes, família, lar, vida privada e fundamentos emocionais. É seu mundo íntimo, seu refúgio e o que te dá segurança. O signo no IC mostra como você vivencia sua vida doméstica e familiar.',
      category: 'points',
    },
    'Regência': {
      term: 'Regência',
      explanation: 'Regência é a relação entre um planeta e um signo, onde cada planeta "governa" ou tem afinidade especial com um ou dois signos. Por exemplo, Marte rege Áries e Escorpião, Vênus rege Touro e Libra. Quando um planeta está no signo que rege, ele está em sua "casa" e expressa suas qualidades de forma mais natural e poderosa.',
      category: 'advanced',
    },
    'Exaltação': {
      term: 'Exaltação',
      explanation: 'Exaltação é uma posição onde um planeta expressa suas melhores qualidades. É como estar em "primeira classe" - o planeta funciona de forma excelente, embora de forma diferente de quando está no signo que rege. Por exemplo, o Sol está exaltado em Áries e a Lua em Touro.',
      category: 'advanced',
    },
    'Quíron': {
      term: 'Quíron',
      explanation: 'Quíron é um planeta menor (asteroide) conhecido como "o ferido-curador". Representa suas feridas profundas, traumas de infância e áreas onde você se sente vulnerável. Mas também mostra seu potencial de cura, compaixão e capacidade de ajudar outros através de suas próprias experiências dolorosas. É onde você encontra sua missão de cura.',
      category: 'planets',
    },
    'Lilith': {
      term: 'Lilith',
      explanation: 'Lilith (também chamada de Lua Negra) representa sua natureza selvagem, instintiva e não-domada. É a parte de você que rejeita convenções sociais, que busca independência absoluta e que pode desafiar o que é esperado. Mostra suas sombras, sua sexualidade autêntica e onde você precisa se libertar de expectativas alheias.',
      category: 'points',
    },
    'Tríade Fundamental': {
      term: 'Tríade Fundamental',
      explanation: 'A Tríade Fundamental é formada pelo Sol, Lua e Ascendente - os três pontos mais importantes do mapa astral. O Sol representa quem você está se tornando (sua essência), a Lua representa quem você é interiormente (suas emoções) e o Ascendente representa como você aparece no mundo (sua máscara). Juntos, eles formam o núcleo da sua personalidade.',
      category: 'basic',
    },
  },
  en: {
    // Basic Terms
    'Ascendente': {
      term: 'Ascendant',
      explanation: 'The Ascendant is the zodiac sign that was rising on the eastern horizon at the moment of your birth. It represents how you present yourself to the world, your social mask, your first step in life, and how others initially see you. It is different from your sun sign and greatly influences your appearance and outer personality.',
      category: 'basic',
    },
    'Regente do Mapa': {
      term: 'Chart Ruler',
      explanation: 'The Chart Ruler (also called Ascendant Ruler) is the planet that rules the sign of your Ascendant. It is considered the most important planet in your chart, as it represents your vital energy, main motivation, and how you express your identity in the world. Where it is positioned shows where you direct your energy and focus.',
      category: 'basic',
    },
    'Signo Solar': {
      term: 'Sun Sign',
      explanation: 'Your Sun Sign is determined by the position of the Sun at the moment of your birth. It represents your essence, core identity, ego, and the person you are becoming. It is your fundamental energy and how you shine in the world. It is the most well-known sign and represents about 30% of your personality.',
      category: 'basic',
    },
    'Signo Lunar': {
      term: 'Moon Sign',
      explanation: 'Your Moon Sign is determined by the position of the Moon at the moment of your birth. It represents your emotions, internal needs, instincts, memories, and how you react emotionally. It is your most sensitive, intuitive part, related to comfort and security. It shows how you process feelings and seek affection.',
      category: 'basic',
    },
    'Casas Astrológicas': {
      term: 'Astrological Houses',
      explanation: 'The Astrological Houses are 12 divisions of the birth chart that represent different areas of life. Each house symbolizes a setting where planetary energies manifest. For example, House 1 represents yourself, House 4 your family and home, House 7 relationships, and House 10 your career. The planet in each house shows how you experience that area of life.',
      category: 'houses',
    },
    'Casa': {
      term: 'House',
      explanation: 'An Astrological House is one of 12 divisions of the birth chart that represents specific life areas. Each house has a theme: House 1 (identity), House 2 (resources), House 3 (communication), House 4 (home), House 5 (creativity), House 6 (work), House 7 (relationships), House 8 (transformation), House 9 (wisdom), House 10 (career), House 11 (friendships), House 12 (spirituality).',
      category: 'houses',
    },
    'Aspectos': {
      term: 'Aspects',
      explanation: 'Aspects are angles formed between planets in the birth chart. They show how different planetary energies interact and relate. Harmonious aspects (like trine and sextile) indicate natural talents and ease. Tense aspects (like square and opposition) indicate challenges that promote growth. Aspects are like the "script" that shows how planets communicate with each other.',
      category: 'aspects',
    },
    'Trígono': {
      term: 'Trine',
      explanation: 'The Trine is a harmonious aspect of 120 degrees between two planets. It represents natural talents, ease, and flow. The energies of the involved planets work together naturally and spontaneously. It is like having an innate gift that does not require conscious effort to manifest.',
      category: 'aspects',
    },
    'Sextil': {
      term: 'Sextile',
      explanation: 'The Sextile is a harmonious aspect of 60 degrees between two planets. It represents opportunities and cooperation. The energies complement each other and offer growth chances when worked on intentionally. Unlike the trine, the sextile needs to be developed with conscious effort.',
      category: 'aspects',
    },
    'Quadratura': {
      term: 'Square',
      explanation: 'The Square is a tense aspect of 90 degrees between two planets. It represents internal conflicts that require action and resolution. It is through squares that we grow, develop strength, and overcome obstacles. They are like "spiritual exercises" that strengthen us, even though they are challenging.',
      category: 'aspects',
    },
    'Oposição': {
      term: 'Opposition',
      explanation: 'The Opposition is an aspect of 180 degrees between two planets, creating a polarity. Opposing forces ask for integration and balance. It often manifests in external relationships, where we meet people who challenge or complete us. It is an energy that asks for awareness and negotiation between extremes.',
      category: 'aspects',
    },
    'Conjunção': {
      term: 'Conjunction',
      explanation: 'The Conjunction occurs when two planets are close, with 0 degrees of separation (with a small tolerance called "orb"). It represents the fusion of energies, where planets unite and their qualities mix. It can be intense and transformative, creating a unique combined energy.',
      category: 'aspects',
    },
    'Nodo Norte': {
      term: 'North Node',
      explanation: 'The North Node (or Lunar North Node) represents the destiny and life purpose you should seek in this incarnation. It is your path of evolution, the qualities you need to develop, and the experiences you need to have to grow. It shows where you should direct your efforts and where to find satisfaction and fulfillment.',
      category: 'points',
    },
    'Nodo Sul': {
      term: 'South Node',
      explanation: 'The South Node (or Lunar South Node) represents talents, patterns, and behaviors you have already developed in past lives or childhood. They are natural abilities and vices you bring, but which may keep you stuck in the past. It shows where you come from and what you need to leave behind to evolve.',
      category: 'points',
    },
    'MC': {
      term: 'MC (Midheaven)',
      explanation: 'The MC (Midheaven) is the highest point of the birth chart, related to House 10. It represents your vocation, career, public reputation, life goals, and how you want to be recognized in the world. It is your professional image and the legacy you want to leave. The sign on the MC shows how you express yourself publicly.',
      category: 'points',
    },
    'IC': {
      term: 'IC (Imum Coeli)',
      explanation: 'The IC (Imum Coeli) is the lowest point of the birth chart, related to House 4. It represents your roots, family, home, private life, and emotional foundations. It is your intimate world, your refuge, and what gives you security. The sign on the IC shows how you experience your domestic and family life.',
      category: 'points',
    },
    'Regência': {
      term: 'Rulership',
      explanation: 'Rulership is the relationship between a planet and a sign, where each planet "governs" or has a special affinity with one or two signs. For example, Mars rules Aries and Scorpio, Venus rules Taurus and Libra. When a planet is in the sign it rules, it is in its "home" and expresses its qualities in a more natural and powerful way.',
      category: 'advanced',
    },
    'Exaltação': {
      term: 'Exaltation',
      explanation: 'Exaltation is a position where a planet expresses its best qualities. It is like being in "first class" - the planet functions excellently, though differently than when in the sign it rules. For example, the Sun is exalted in Aries and the Moon in Taurus.',
      category: 'advanced',
    },
    'Quíron': {
      term: 'Chiron',
      explanation: 'Chiron is a minor planet (asteroid) known as "the wounded-healer". It represents your deep wounds, childhood traumas, and areas where you feel vulnerable. But it also shows your healing potential, compassion, and ability to help others through your own painful experiences. It is where you find your healing mission.',
      category: 'planets',
    },
    'Lilith': {
      term: 'Lilith',
      explanation: 'Lilith (also called Black Moon) represents your wild, instinctive, and untamed nature. It is the part of you that rejects social conventions, seeks absolute independence, and may challenge what is expected. It shows your shadows, your authentic sexuality, and where you need to free yourself from others\' expectations.',
      category: 'points',
    },
    'Tríade Fundamental': {
      term: 'Fundamental Triad',
      explanation: 'The Fundamental Triad is formed by the Sun, Moon, and Ascendant - the three most important points in the birth chart. The Sun represents who you are becoming (your essence), the Moon represents who you are internally (your emotions), and the Ascendant represents how you appear in the world (your mask). Together, they form the core of your personality.',
      category: 'basic',
    },
  },
};

/**
 * Obtém a explicação de um termo técnico
 */
export function getGlossaryTerm(term: string, language: Language = 'pt'): GlossaryTerm | null {
  // Tentar encontrar o termo exato
  const exactMatch = astrologicalGlossary[language][term];
  if (exactMatch) {
    return exactMatch;
  }

  // Tentar encontrar por variações comuns
  const variations: Record<string, string[]> = {
    pt: {
      'Ascendente': ['Asc', 'ASC', 'Ascendente'],
      'Regente do Mapa': ['Regente', 'Regente do Mapa', 'Regente Ascendente'],
      'Signo Solar': ['Sol', 'Signo Solar', 'Signo do Sol'],
      'Signo Lunar': ['Lua', 'Signo Lunar', 'Signo da Lua'],
      'Casas Astrológicas': ['Casas', 'Casas Astrológicas'],
      'Tríade Fundamental': ['Tríade', 'Tríade Fundamental'],
    },
    en: {
      'Ascendente': ['Ascendant', 'ASC', 'Rising Sign'],
      'Regente do Mapa': ['Chart Ruler', 'Ruler', 'Ascendant Ruler'],
      'Signo Solar': ['Sun', 'Sun Sign'],
      'Signo Lunar': ['Moon', 'Moon Sign'],
      'Casas Astrológicas': ['Houses', 'Astrological Houses'],
      'Tríade Fundamental': ['Triad', 'Fundamental Triad'],
    },
  };

  const langVariations = variations[language] || {};
  for (const [key, values] of Object.entries(langVariations)) {
    if (values.includes(term)) {
      return astrologicalGlossary[language][key] || null;
    }
  }

  return null;
}

/**
 * Obtém todos os termos de uma categoria
 */
export function getGlossaryByCategory(
  category: GlossaryTerm['category'],
  language: Language = 'pt'
): GlossaryTerm[] {
  return Object.values(astrologicalGlossary[language]).filter(
    (term) => term.category === category
  );
}

/**
 * Obtém todos os termos do glossário
 */
export function getAllGlossaryTerms(language: Language = 'pt'): GlossaryTerm[] {
  return Object.values(astrologicalGlossary[language]);
}


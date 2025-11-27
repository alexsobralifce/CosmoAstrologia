import { AstroCard } from './astro-card';
import { zodiacSigns } from './zodiac-icons';
import { planets } from './planet-icons';
import { UIIcons } from './ui-icons';
import { AlertCircle, CheckCircle, Clock, Heart, DollarSign, Users, Activity, Calendar, ChevronDown, Loader2 } from 'lucide-react';
import { Badge } from './ui/badge';
import { useState } from 'react';
import { apiService } from '../services/api';

interface PlanetData {
  name: string;
  sign: string;
  house: number;
  degree: number;
  icon: any;
}

interface DailyAdviceSectionProps {
  moonSign: string;
  moonHouse: number;
  isMercuryRetrograde?: boolean;
  isMoonVoidOfCourse?: boolean;
  voidEndsAt?: string;
  planetaryData?: PlanetData[];
}

export const DailyAdviceSection = ({ 
  moonSign, 
  moonHouse, 
  isMercuryRetrograde = false,
  isMoonVoidOfCourse = false,
  voidEndsAt = "16:30",
  planetaryData = []
}: DailyAdviceSectionProps) => {
  const MoonIcon = zodiacSigns.find(z => z.name === moonSign)?.icon;
  const MercuryIcon = planets.find(p => p.name === 'Mercúrio')?.icon;
  const [expandedTab, setExpandedTab] = useState<string | null>(null);
  const [adviceCache, setAdviceCache] = useState<Record<string, string>>({});
  const [loadingAdvice, setLoadingAdvice] = useState<Record<string, boolean>>({});

  const getMoonAdvice = () => {
    const houseAdvice: Record<number, string> = {
      1: "Hoje, sua segurança emocional vem de focar em si mesmo. É um bom dia para novos começos e cuidar da sua aparência.",
      2: "Hoje, sua segurança emocional vem de estabilidade financeira. Foque em administrar recursos e valorizar o que já possui.",
      3: "Hoje, sua segurança emocional vem de comunicação e aprendizado. É um bom dia para conversas, estudos e conectar-se com irmãos.",
      4: "Hoje, sua segurança emocional vem do lar e família. Fique perto de quem ama e cuide do seu espaço pessoal.",
      5: "Hoje, sua segurança emocional vem de criatividade e diversão. É um bom dia para hobbies, romance e expressão pessoal.",
      6: "Hoje, sua segurança emocional vem de rotina e produtividade. Organize suas tarefas, cuide da saúde e seja útil.",
      7: "Hoje, sua segurança emocional vem de parcerias. É um bom dia para colaborações, negociações e tempo com parceiros.",
      8: "Hoje, sua segurança emocional vem de transformação e intimidade. Explore questões profundas e compartilhe recursos.",
      9: "Hoje, sua segurança emocional vem de exploração e filosofia. É um bom dia para viagens, estudos superiores e expandir horizontes.",
      10: "Hoje, sua segurança emocional vem de carreira e reconhecimento público. Foque em metas profissionais e sua reputação.",
      11: "Hoje, sua segurança emocional vem de estar com amigos e grupos. É um bom dia para networking e atividades humanitárias.",
      12: "Hoje, sua segurança emocional vem de solitude e reflexão. É um bom dia para meditação, descanso e processos internos."
    };
    
    return houseAdvice[moonHouse] || "Sintonize-se com suas emoções hoje.";
  };

  // Função para analisar impacto planetário por categoria
  const analyzePlanetaryInfluence = (category: string): { positive: string[], challenges: string[] } => {
    const positive: string[] = [];
    const challenges: string[] = [];

    if (!planetaryData || planetaryData.length === 0) {
      return { positive, challenges };
    }

    // Planetas relevantes por categoria e suas casas mais significativas
    const categoryAnalysis: Record<string, {
      planets: string[];
      houses: number[];
      houseMeanings: Record<number, string>;
      beneficialPlanets: string[];
      challengingPlanets: string[];
    }> = {
      love: {
        planets: ['Vênus', 'Lua', 'Júpiter', 'Marte'],
        houses: [5, 7, 11, 1, 4],
        houseMeanings: {
          1: 'autoconfiança e atratividade pessoal',
          4: 'lar acolhedor e segurança emocional',
          5: 'romance, paixão e criatividade',
          7: 'parcerias e compromissos',
          11: 'amizades que podem evoluir para romance'
        },
        beneficialPlanets: ['Vênus', 'Júpiter'],
        challengingPlanets: ['Saturno', 'Marte']
      },
      career: {
        planets: ['Sol', 'Saturno', 'Marte', 'Júpiter', 'Mercúrio'],
        houses: [2, 6, 10, 1, 3],
        houseMeanings: {
          1: 'presença profissional e primeira impressão',
          2: 'recursos financeiros e valores',
          3: 'comunicação profissional e networking',
          6: 'trabalho diário e rotina profissional',
          10: 'carreira pública e reconhecimento'
        },
        beneficialPlanets: ['Sol', 'Júpiter'],
        challengingPlanets: ['Saturno']
      },
      family: {
        planets: ['Lua', 'Vênus', 'Saturno', 'Júpiter'],
        houses: [4, 7, 10, 3],
        houseMeanings: {
          3: 'comunicação com irmãos e parentes próximos',
          4: 'raízes familiares e lar',
          7: 'harmonia e equilíbrio familiar',
          10: 'autoridade e responsabilidades familiares'
        },
        beneficialPlanets: ['Lua', 'Vênus', 'Júpiter'],
        challengingPlanets: ['Saturno']
      },
      health: {
        planets: ['Marte', 'Saturno', 'Lua', 'Sol'],
        houses: [1, 6, 12, 4],
        houseMeanings: {
          1: 'vitalidade física e energia',
          4: 'ambiente doméstico e bem-estar',
          6: 'hábitos saudáveis e rotina',
          12: 'cura emocional e processos internos'
        },
        beneficialPlanets: ['Sol', 'Lua'],
        challengingPlanets: ['Saturno', 'Marte']
      },
      period: {
        planets: ['Sol', 'Lua', 'Mercúrio', 'Vênus', 'Marte', 'Júpiter', 'Saturno'],
        houses: [1, 4, 7, 10],
        houseMeanings: {
          1: 'novos começos e identidade',
          4: 'fundação e raízes',
          7: 'equilíbrio e parcerias',
          10: 'reconhecimento e autoridade'
        },
        beneficialPlanets: ['Sol', 'Júpiter', 'Vênus'],
        challengingPlanets: ['Saturno', 'Marte', 'Plutão']
      }
    };

    const analysis = categoryAnalysis[category];
    if (!analysis) return { positive, challenges };

    analysis.planets.forEach(planetName => {
      const planet = planetaryData.find(p => p.name === planetName);
      if (!planet) return;

      // Verificar se planeta está em casa relevante para a categoria
      if (analysis.houses.includes(planet.house)) {
        const meaning = analysis.houseMeanings[planet.house];
        if (meaning) {
          const isBeneficial = analysis.beneficialPlanets.includes(planetName);
          const isChallenging = analysis.challengingPlanets.includes(planetName);
          
          if (isBeneficial) {
            positive.push(`${planetName} na Casa ${planet.house} fortalece ${meaning}.`);
          } else if (isChallenging) {
            // Planetas desafiadores em casas difíceis (6, 8, 12) podem trazer mais tensão
            if ([6, 8, 12].includes(planet.house)) {
              challenges.push(`${planetName} na Casa ${planet.house} requer atenção cuidadosa a ${meaning}.`);
            } else {
              positive.push(`${planetName} na Casa ${planet.house} traz determinação para ${meaning}.`);
            }
          } else {
            // Planetas neutros (como Lua, Mercúrio)
            if (planetName === 'Lua') {
              positive.push(`Sua Lua natal na Casa ${planet.house} conecta suas emoções com ${meaning}.`);
            } else {
              positive.push(`${planetName} na Casa ${planet.house} influencia ${meaning}.`);
            }
          }
        }
      }
    });

    return { positive, challenges };
  };

  const getAdviceByCategoryLocal = (category: string) => {
    const planetaryInfluence = analyzePlanetaryInfluence(category);
    
    const adviceMap: Record<string, Record<number, string>> = {
      love: {
        1: "Hoje é um dia para se conhecer melhor antes de buscar conexões. Trabalhe sua autoestima e autenticidade.",
        2: "A estabilidade financeira pode influenciar sua segurança em relacionamentos. Cuide de si mesmo primeiro.",
        3: "Comunicação é chave hoje. Expresse seus sentimentos com clareza e ouça atentamente seu parceiro ou interesses românticos.",
        4: "Foque em criar um ambiente acolhedor em casa. Relacionamentos familiares e domésticos estão em destaque.",
        5: "Dia perfeito para romance e diversão! Seja espontâneo, criativo e aproveite momentos de prazer com quem ama.",
        6: "Cuidar de si mesmo é essencial para relacionamentos saudáveis. Trabalhe em rotinas que fortaleçam seu bem-estar.",
        7: "Excelente momento para parcerias e compromissos. Seja diplomático e busque equilíbrio nos relacionamentos.",
        8: "Profundidade e intimidade estão em foco. Explore conexões mais profundas e transformadoras.",
        9: "Relacionamentos podem trazer novas perspectivas e crescimento. Esteja aberto a diferentes visões de mundo.",
        10: "Relacionamentos profissionais e networking podem trazer oportunidades românticas. Mantenha-se profissional.",
        11: "Amizades podem evoluir para algo mais. Conecte-se com grupos e pessoas que compartilham seus valores.",
        12: "Momento de reflexão sobre padrões relacionais. Trabalhe questões internas antes de buscar novas conexões."
      },
      career: {
        1: "Projete confiança e profissionalismo hoje. É um bom dia para apresentações e primeiras impressões.",
        2: "Foque em estabilidade financeira e valorização de recursos. Revise orçamentos e invista com sabedoria.",
        3: "Comunicação profissional está em alta. Reuniões, negociações e networking serão produtivos.",
        4: "Trabalhe em projetos que tragam segurança e estabilidade. Considere trabalhar de casa se possível.",
        5: "Criatividade e inovação podem destacar você profissionalmente. Arrisque-se em projetos criativos.",
        6: "Organização e eficiência são suas aliadas. Complete tarefas pendentes e melhore processos de trabalho.",
        7: "Parcerias e colaborações são favorecidas. Busque acordos mutuamente benéficos.",
        8: "Transformações profundas na carreira podem ocorrer. Esteja aberto a mudanças e reinvenções.",
        9: "Oportunidades de expansão através de educação ou viagens. Considere cursos ou projetos internacionais.",
        10: "Dia excelente para avanços na carreira e reconhecimento. Foque em metas ambiciosas e visibilidade.",
        11: "Networking e conexões profissionais podem abrir portas. Participe de eventos e grupos do setor.",
        12: "Reflita sobre sua trajetória profissional. Trabalhe em projetos que tenham significado pessoal."
      },
      family: {
        1: "Priorize seu bem-estar pessoal para poder estar presente para a família. Cuide de si primeiro.",
        2: "Questões financeiras familiares podem surgir. Seja prático e responsável com recursos compartilhados.",
        3: "Comunicação familiar está em destaque. Converse abertamente com irmãos e parentes próximos.",
        4: "Dia perfeito para atividades em família e cuidado do lar. Crie memórias e fortaleça laços domésticos.",
        5: "Diversão e criatividade com a família são favorecidas. Planeje atividades recreativas juntos.",
        6: "Cuidar da saúde familiar e rotinas domésticas. Organize responsabilidades e tarefas do lar.",
        7: "Harmonia e equilíbrio nas relações familiares. Busque compromissos e soluções colaborativas.",
        8: "Questões profundas ou transformações familiares podem surgir. Enfrente com coragem e honestidade.",
        9: "Família pode trazer novas perspectivas. Esteja aberto a diferentes visões e tradições familiares.",
        10: "Liderança familiar e responsabilidades podem ser testadas. Mantenha autoridade com compaixão.",
        11: "Reuniões familiares e celebrações com amigos próximos são favorecidas. Aproveite momentos sociais.",
        12: "Reflita sobre padrões familiares e heranças emocionais. Trabalhe em cura e compreensão."
      },
      health: {
        1: "Foque em sua aparência física e autoimagem. Exercícios e cuidados pessoais estão favorecidos.",
        2: "Saúde financeira impacta bem-estar geral. Cuide de recursos para manter qualidade de vida.",
        3: "Comunicação sobre saúde é importante. Consulte profissionais e compartilhe preocupações.",
        4: "Ambiente doméstico afeta sua saúde. Organize seu espaço para promover bem-estar.",
        5: "Atividades físicas divertidas e criativas são ideais. Encontre prazer no movimento e exercício.",
        6: "Rotina de saúde e bem-estar está em foco. Estabeleça hábitos saudáveis e mantenha disciplina.",
        7: "Parcerias podem apoiar seus objetivos de saúde. Considere treinar ou fazer dieta com alguém.",
        8: "Transformações profundas na saúde podem ocorrer. Esteja aberto a mudanças significativas.",
        9: "Exploração de práticas alternativas de saúde ou viagens para tratamentos podem ser benéficas.",
        10: "Disciplina e comprometimento com metas de saúde. Foque em resultados de longo prazo.",
        11: "Grupos de apoio e atividades sociais relacionadas à saúde são favorecidos.",
        12: "Cuidado com saúde mental e emocional. Priorize descanso, meditação e processos internos."
      },
      period: {
        1: "Período de novos começos e autodescoberta. Foque em quem você é e quem deseja se tornar.",
        2: "Período de estabilização financeira e valorização de recursos. Construa segurança material.",
        3: "Período de comunicação, aprendizado e conexões próximas. Expanda seu conhecimento e rede.",
        4: "Período de foco no lar e família. Crie raízes e fortaleça sua base emocional.",
        5: "Período de criatividade, romance e expressão pessoal. Aproveite a vida e seja autêntico.",
        6: "Período de organização, rotina e serviço. Melhore hábitos e cuide de responsabilidades.",
        7: "Período de parcerias e relacionamentos significativos. Busque equilíbrio e colaboração.",
        8: "Período de transformação profunda e renovação. Deixe ir o que não serve mais.",
        9: "Período de expansão de horizontes e busca por significado. Explore filosofias e culturas.",
        10: "Período de foco em carreira e reconhecimento público. Trabalhe em metas ambiciosas.",
        11: "Período de conexões sociais e realização de sonhos. Aproveite amizades e grupos.",
        12: "Período de introspecção e cura. Trabalhe em questões internas e prepare-se para novos ciclos."
      }
    };

    const baseAdvice = adviceMap[category]?.[moonHouse] || "Sintonize-se com as energias do momento.";
    
    // Combinar conselho base com influências planetárias
    const parts: string[] = [baseAdvice];
    
    if (planetaryInfluence.positive.length > 0) {
      parts.push("\n\n✨ Influências Positivas:");
      planetaryInfluence.positive.forEach(msg => {
        parts.push(`\n• ${msg}`);
      });
    }
    
    if (planetaryInfluence.challenges.length > 0) {
      parts.push("\n\n⚠️ Atenção:");
      planetaryInfluence.challenges.forEach(msg => {
        parts.push(`\n• ${msg}`);
      });
    }
    
    return parts.join("");
  };

  const tabs = [
    {
      id: 'love',
      title: 'Amor e Relacionamentos',
      icon: Heart,
      color: 'text-red-700 dark:text-red-300',
      bgColor: 'bg-red-100 dark:bg-red-500/15',
      borderColor: 'border-red-300 dark:border-red-500/30'
    },
    {
      id: 'career',
      title: 'Dinheiro e Carreira',
      icon: DollarSign,
      color: 'text-green-700 dark:text-green-300',
      bgColor: 'bg-green-100 dark:bg-green-500/15',
      borderColor: 'border-green-300 dark:border-green-500/30'
    },
    {
      id: 'family',
      title: 'Família e Amigos',
      icon: Users,
      color: 'text-blue-700 dark:text-blue-300',
      bgColor: 'bg-blue-100 dark:bg-blue-500/15',
      borderColor: 'border-blue-300 dark:border-blue-500/30'
    },
    {
      id: 'health',
      title: 'Saúde e Bem Estar',
      icon: Activity,
      color: 'text-purple-700 dark:text-purple-300',
      bgColor: 'bg-purple-100 dark:bg-purple-500/15',
      borderColor: 'border-purple-300 dark:border-purple-500/30'
    },
    {
      id: 'period',
      title: 'Período Atual',
      icon: Calendar,
      color: 'text-orange-700 dark:text-orange-300',
      bgColor: 'bg-orange-100 dark:bg-orange-500/15',
      borderColor: 'border-orange-300 dark:border-orange-500/30'
    }
  ];

  const toggleTab = async (tabId: string) => {
    const isCurrentlyExpanded = expandedTab === tabId;
    
    if (isCurrentlyExpanded) {
      // Fechar aba
      setExpandedTab(null);
      return;
    }
    
    // Abrir aba
    setExpandedTab(tabId);
    
    // Se já temos o conselho em cache, não buscar novamente
    if (adviceCache[tabId]) {
      return;
    }
    
    // Buscar conselho da API
    if (!loadingAdvice[tabId]) {
      setLoadingAdvice(prev => ({ ...prev, [tabId]: true }));
      
      try {
        // Preparar posições planetárias relevantes
        const planetaryPositions = planetaryData
          ?.filter(planet => {
            const relevantPlanets = {
              love: ['Vênus', 'Lua', 'Júpiter', 'Marte'],
              career: ['Sol', 'Saturno', 'Marte', 'Júpiter'],
              family: ['Lua', 'Vênus', 'Saturno'],
              health: ['Marte', 'Saturno', 'Lua', 'Sol'],
              period: ['Sol', 'Lua', 'Mercúrio', 'Vênus', 'Marte']
            };
            return relevantPlanets[tabId as keyof typeof relevantPlanets]?.includes(planet.name);
          })
          .map(planet => ({
            name: planet.name,
            house: planet.house,
            sign: planet.sign
          }));
        
        const result = await apiService.getDailyAdvice({
          moonHouse,
          category: tabId,
          moonSign,
          planetaryPositions
        });
        
        // Salvar no cache
        setAdviceCache(prev => ({ ...prev, [tabId]: result.interpretation }));
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido';
        // Log apenas se não for timeout (timeout é esperado em algumas situações)
        if (!errorMessage.includes('Tempo de espera esgotado')) {
          console.error(`[DailyAdvice] Erro ao buscar conselho para ${tabId}:`, error);
        }
        // Em caso de erro, usar conselho local como fallback
        const fallbackAdvice = getAdviceByCategoryLocal(tabId);
        setAdviceCache(prev => ({ ...prev, [tabId]: fallbackAdvice }));
      } finally {
        setLoadingAdvice(prev => ({ ...prev, [tabId]: false }));
      }
    }
  };
  
  // Função que retorna o conselho (da API ou local)
  const getAdviceByCategory = (category: string) => {
    // Se temos conselho da API em cache, usar ele
    if (adviceCache[category]) {
      return adviceCache[category];
    }
    
    // Caso contrário, usar conselho local como fallback
    return getAdviceByCategoryLocal(category);
  };

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-primary mb-1" style={{ fontFamily: 'var(--font-serif)' }}>
          Conselhos para Hoje
        </h2>
        <p className="text-sm text-muted-foreground">
          Guia prático baseado nos trânsitos atuais
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {/* Trânsito da Lua - Sempre Visível */}
        <AstroCard className="border-l-4 border-l-accent shadow-lg shadow-accent/10 hover:shadow-xl hover:shadow-accent/20 transition-all duration-300 animate-fadeIn">
          <div className="flex items-start gap-4">
            {MoonIcon && <MoonIcon size={40} className="text-accent flex-shrink-0 drop-shadow-lg" />}
            <div className="flex-1 space-y-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-foreground">Humor do Dia: Lua em {moonSign}</h3>
                  <Badge variant="outline" className="bg-accent/10 text-accent border-accent/30">
                    Ativo Hoje
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">Casa {moonHouse}</p>
              </div>
              <p className="text-foreground">
                {getMoonAdvice()}
              </p>
            </div>
          </div>
        </AstroCard>

        {/* Mercúrio Retrógrado - Condicional */}
        {isMercuryRetrograde && (
          <AstroCard className="border-l-4 border-l-red-500 bg-red-100 dark:bg-red-500/15 shadow-lg shadow-red-200 dark:shadow-red-500/10 hover:shadow-xl transition-all duration-300 animate-fadeIn">
            <div className="flex items-start gap-4">
              <div className="relative flex-shrink-0">
                {MercuryIcon && <MercuryIcon size={40} className="text-red-600 dark:text-red-400 drop-shadow-lg" />}
                <div className="absolute -top-1 -right-1 bg-red-600 dark:bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold shadow-md">
                  R
                </div>
              </div>
              <div className="flex-1 space-y-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <AlertCircle size={18} className="text-red-600 dark:text-red-400" />
                    <h3 className="text-foreground font-semibold">Alerta: Mercúrio Retrógrado Ativo</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">Em efeito por ~3 semanas</p>
                </div>
                
                <div className="space-y-3 text-base">
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-red-100 dark:bg-red-500/15 border border-red-300 dark:border-red-500/30">
                    <AlertCircle size={20} className="text-red-700 dark:text-red-300 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <span className="text-red-700 dark:text-red-300 font-semibold block mb-1">Não Fazer:</span>
                      <span className="text-foreground leading-relaxed">
                        Evite assinar contratos, tomar decisões finais ou fazer grandes compras 
                        (especialmente eletrônicos ou veículos). A comunicação pode estar confusa.
                      </span>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-green-100 dark:bg-green-500/15 border border-green-300 dark:border-green-500/30">
                    <CheckCircle size={20} className="text-green-700 dark:text-green-300 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <span className="text-green-700 dark:text-green-300 font-semibold block mb-1">Fazer:</span>
                      <span className="text-foreground leading-relaxed">
                        Ótimo momento para Revisar, Reavaliar e Replanejar. Reconecte-se com pessoas 
                        do passado ou revise projetos antigos.
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </AstroCard>
        )}

        {/* Lua Fora de Curso - Condicional */}
        {isMoonVoidOfCourse && (
          <AstroCard className="border-l-4 border-l-gray-500 bg-gray-100 dark:bg-gray-500/15 shadow-lg shadow-gray-200 dark:shadow-gray-500/10 hover:shadow-xl transition-all duration-300 animate-fadeIn">
            <div className="flex items-start gap-4">
              <Clock size={40} className="text-gray-600 dark:text-gray-400 flex-shrink-0 drop-shadow-lg" />
              <div className="flex-1 space-y-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-foreground">Pausa Cósmica: Lua Fora de Curso</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">Termina às {voidEndsAt} hoje</p>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <AlertCircle size={16} className="text-gray-600 dark:text-gray-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="text-gray-700 dark:text-gray-300 font-medium">Não Fazer:</span>
                      <span className="text-foreground ml-1">
                        Evite iniciar qualquer empreendimento significativo (reuniões importantes, 
                        primeiros encontros, lançar um projeto). O que for começado agora tende a não 
                        trazer resultados.
                      </span>
                    </div>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle size={16} className="text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <span className="text-green-700 dark:text-green-300 font-medium">Fazer:</span>
                      <span className="text-foreground ml-1">
                        Perfeito para tarefas rotineiras, organizar sua mesa, meditar ou finalizar 
                        assuntos pendentes.
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </AstroCard>
        )}
      </div>

      {/* Abas Expansíveis de Conselhos */}
      <div className="space-y-2 mt-6">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isExpanded = expandedTab === tab.id;
          
          return (
            <AstroCard 
              key={tab.id}
              className={`border-l-4 ${tab.borderColor} ${tab.bgColor} transition-all duration-300 cursor-pointer hover:shadow-lg`}
              onClick={() => toggleTab(tab.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <Icon size={24} className={`${tab.color} flex-shrink-0`} />
                  <h3 className="text-foreground font-medium">{tab.title}</h3>
                </div>
                <ChevronDown 
                  size={20} 
                  className={`text-foreground/70 dark:text-foreground/80 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
                />
              </div>
              
              {isExpanded && (
                <div className="mt-4 pt-4 border-t border-border animate-fadeIn">
                  {loadingAdvice[tab.id] ? (
                    <div className="flex items-center gap-3 py-4">
                      <Loader2 size={20} className="text-primary animate-spin" />
                      <p className="text-muted-foreground">Buscando conselhos personalizados...</p>
                    </div>
                  ) : (
                    <p className="text-foreground leading-relaxed whitespace-pre-line">
                      {getAdviceByCategory(tab.id)}
                    </p>
                  )}
                </div>
              )}
            </AstroCard>
          );
        })}
      </div>
    </div>
  );
};

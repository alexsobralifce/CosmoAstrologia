import React, { useState, useEffect } from 'react';
import { UIIcons } from '../ui-icons';
import { zodiacSigns } from '../zodiac-icons';
import { apiService } from '../../services/api';
import { useLanguage } from '../../i18n';
import { OnboardingData } from '../onboarding';
import { removeSupportAndTechnicalContent } from './text-cleaners';

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

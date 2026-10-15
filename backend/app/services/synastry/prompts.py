"""Prompts da sinastria por idioma (pt/en). Texto movido sem alterações de app/api/interpretation/synastry.py."""

SYSTEM_PROMPTS = {
    'pt': """Você é um astrólogo experiente especializado em sinastria e análise de compatibilidade entre SIGNOS DO ZODÍACO. 
Sua função é criar interpretações PRÁTICAS, DETALHADAS e PERSONALIZADAS sobre relacionamentos, focando em dinâmicas reais e aplicáveis.

REGRA CRÍTICA - USE APENAS O CONTEXTO FORNECIDO:
- Você DEVE usar EXCLUSIVAMENTE as informações sobre os SIGNOS fornecidas no contexto abaixo
- NÃO invente características ou informações que não estejam no contexto
- NÃO use conhecimento genérico - baseie-se APENAS nas informações específicas do contexto
- NÃO mencione posicionamentos planetários específicos (ex: "Vênus em Libra na Casa 7") a menos que estejam explicitamente no contexto
- NÃO confunda REGÊNCIA PLANETÁRIA (ex: Vênus rege Libra) com POSICIONAMENTO (ex: Vênus em Libra)
- Estamos analisando SIGNOS, não mapas astrais específicos - fale sobre características gerais dos signos
- Se o contexto mencionar características específicas de um signo, USE-AS na interpretação
- Se o contexto mencionar dinâmicas específicas entre os signos, USE-AS na interpretação
- Crie uma interpretação única e personalizada baseada APENAS nas informações do contexto fornecido
- Seja específico sobre como as características mencionadas no contexto interagem
- Foque em dinâmicas práticas do relacionamento baseadas nas informações do contexto
- Inclua pontos fortes, desafios e orientações práticas específicas baseadas no contexto""",
    'en': """You are an experienced astrologer specialized in synastry and compatibility analysis between ZODIAC SIGNS. 
Your function is to create PRACTICAL, DETAILED and PERSONALIZED interpretations about relationships, focusing on real and applicable dynamics.

CRITICAL RULE - USE ONLY THE PROVIDED CONTEXT:
- You MUST use EXCLUSIVELY the information about the SIGNS provided in the context below
- DO NOT invent characteristics or information that is not in the context
- DO NOT use generic knowledge - base yourself ONLY on the specific information in the context
- DO NOT mention specific planetary positions (e.g., "Venus in Libra in House 7") unless explicitly in the context
- DO NOT confuse PLANETARY RULERSHIP (e.g., Venus rules Libra) with POSITION (e.g., Venus in Libra)
- We are analyzing SIGNS, not specific birth charts - speak about general sign characteristics
- If the context mentions specific characteristics of a sign, USE THEM in the interpretation
- If the context mentions specific dynamics between the signs, USE THEM in the interpretation
- Create a unique and personalized interpretation based ONLY on the information in the provided context
- Be specific about how the characteristics mentioned in the context interact
- Focus on practical relationship dynamics based on the information in the context
- Include strengths, challenges and specific practical guidance based on the context""",
}


def _user_prompt_pt(sign1: str, sign2: str, full_context: str) -> str:
    return f"""SINASTRIA / COMPATIBILIDADE ENTRE {sign1.upper()} E {sign2.upper()}:

═══════════════════════════════════════════════════════════════
CONTEXTO ASTROLÓGICO DETALHADO (BASEADO NO RAG):
═══════════════════════════════════════════════════════════════

{full_context}

═══════════════════════════════════════════════════════════════

INSTRUÇÕES CRÍTICAS:
Você DEVE criar uma interpretação COMPLETA, PRÁTICA e PERSONALIZADA sobre a compatibilidade entre {sign1} e {sign2}.

REGRA ABSOLUTA: Use APENAS as informações fornecidas no contexto acima. NÃO invente nada que não esteja no contexto.

IMPORTANTE CRÍTICO SOBRE ASTROLOGIA E CÁLCULOS:
- Estamos analisando SIGNOS DO ZODÍACO (Libra, Escorpião, etc.), não mapas astrais específicos
- NÃO mencione posicionamentos planetários específicos (ex: "Vênus em Libra na Casa 7") a menos que estejam explicitamente no contexto
- NÃO confunda REGÊNCIA (Vênus rege Libra) com POSICIONAMENTO (Vênus em Libra)
- NÃO invente cálculos astrológicos - se precisar de cálculos, eles devem ser feitos pela biblioteca padrão (Swiss Ephemeris) e validados antes
- NÃO mencione aspectos, casas ou graus específicos a menos que estejam no contexto validado
- Fale sobre características gerais dos signos, não sobre configurações específicas de mapa
- Se o contexto mencionar que um planeta rege um signo, você pode mencionar isso, mas NÃO invente posicionamentos ou cálculos
- TODOS os dados astrológicos calculados devem vir de cálculos validados, não de invenção

A interpretação DEVE:
1. Usar EXCLUSIVAMENTE as características específicas de cada signo mencionadas no contexto acima
2. Explicar como essas características (mencionadas no contexto) interagem na prática
3. Ser específica sobre esta combinação particular baseada nas informações do contexto
4. Incluir exemplos práticos de como essa dinâmica (baseada no contexto) se manifesta
5. Focar em características gerais dos signos, não em posicionamentos planetários específicos

Estruture a interpretação com:

1. **Dinâmica Geral do Relacionamento** (2-3 parágrafos)
   - Como as características de {sign1} e {sign2} se complementam ou desafiam
   - O que torna esta combinação única

2. **Pontos Fortes e Complementaridade** (2-3 parágrafos)
   - Quais características de cada signo criam harmonia
   - Como eles se apoiam mutuamente
   - Exemplos práticos de situações onde brilham juntos

3. **Desafios e Áreas de Atenção** (2-3 parágrafos)
   - Onde podem surgir tensões baseadas nas características de cada signo
   - Diferenças que precisam ser compreendidas e respeitadas
   - Exemplos práticos de situações que podem ser desafiadoras

4. **Orientações Práticas** (2-3 parágrafos)
   - Como cada signo pode se adaptar para melhorar o relacionamento
   - Estratégias específicas de comunicação e resolução de conflitos
   - Atividades e abordagens que funcionam bem para esta combinação

5. **Exemplos Práticos** (OBRIGATÓRIO - pelo menos 5 exemplos concretos)
   - Situações do dia a dia onde essa dinâmica aparece
   - Como lidar com decisões, conflitos, celebrações, etc.

IMPORTANTE CRÍTICO:
- Escreva NO MÍNIMO 8 parágrafos completos
- SEMPRE use informações específicas do contexto fornecido acima sobre cada signo
- NÃO invente características que não estejam no contexto
- NÃO use respostas genéricas - seja específico sobre {sign1} e {sign2} baseado no contexto
- Mencione características específicas que aparecem no contexto (ex: "como mencionado no contexto, {sign1} tem...")
- Use linguagem didática, atual e aplicável ao dia a dia
- Foque em dinâmicas reais de relacionamento baseadas nas informações do contexto
- Se o contexto não mencionar algo específico, não invente - trabalhe com o que está disponível"""


def _user_prompt_en(sign1: str, sign2: str, full_context: str) -> str:
    return f"""SYNASTRY / COMPATIBILITY BETWEEN {sign1.upper()} AND {sign2.upper()}:

═══════════════════════════════════════════════════════════════
DETAILED ASTROLOGICAL CONTEXT (FROM RAG):
═══════════════════════════════════════════════════════════════

{full_context}

═══════════════════════════════════════════════════════════════

CRITICAL INSTRUCTIONS:
You MUST create a COMPLETE, PRACTICAL and PERSONALIZED interpretation about the compatibility between {sign1} and {sign2}.

ABSOLUTE RULE: Use ONLY the information provided in the context above. DO NOT invent anything that is not in the context.

CRITICAL IMPORTANT ABOUT ASTROLOGY AND CALCULATIONS:
- We are analyzing ZODIAC SIGNS (Libra, Scorpio, etc.), not specific birth charts
- DO NOT mention specific planetary positions (e.g., "Venus in Libra in House 7") unless explicitly in the context
- DO NOT confuse RULERSHIP (Venus rules Libra) with POSITION (Venus in Libra)
- DO NOT invent astrological calculations - if calculations are needed, they must be done by the standard library (Swiss Ephemeris) and validated first
- DO NOT mention aspects, houses or specific degrees unless they are in the validated context
- Speak about general sign characteristics, not specific chart configurations
- If the context mentions that a planet rules a sign, you can mention that, but DO NOT invent positions or calculations
- ALL calculated astrological data must come from validated calculations, not invention

The interpretation MUST:
1. Use EXCLUSIVELY the specific characteristics of each sign mentioned in the context above
2. Explain how these characteristics (mentioned in the context) interact in practice
3. Be specific about this particular combination based on the information in the context
4. Include practical examples of how this dynamic (based on the context) manifests
5. Focus on general sign characteristics, not specific planetary positions

Structure the interpretation with:

1. **General Relationship Dynamics** (2-3 paragraphs)
   - How the characteristics of {sign1} and {sign2} complement or challenge each other
   - What makes this combination unique

2. **Strengths and Complementarity** (2-3 paragraphs)
   - Which characteristics of each sign create harmony
   - How they support each other
   - Practical examples of situations where they shine together

3. **Challenges and Areas of Attention** (2-3 paragraphs)
   - Where tensions may arise based on each sign's characteristics
   - Differences that need to be understood and respected
   - Practical examples of situations that may be challenging

4. **Practical Guidance** (2-3 paragraphs)
   - How each sign can adapt to improve the relationship
   - Specific communication and conflict resolution strategies
   - Activities and approaches that work well for this combination

5. **Practical Examples** (MANDATORY - at least 5 concrete examples)
   - Day-to-day situations where this dynamic appears
   - How to handle decisions, conflicts, celebrations, etc.

CRITICAL IMPORTANT:
- Write AT LEAST 8 complete paragraphs
- ALWAYS use specific information from the context provided above about each sign
- DO NOT invent characteristics that are not in the context
- DO NOT use generic responses - be specific about {sign1} and {sign2} based on the context
- Mention specific characteristics that appear in the context (e.g., "as mentioned in the context, {sign1} has...")
- Use didactic, current and applicable language
- Focus on real relationship dynamics based on the information in the context
- If the context doesn't mention something specific, don't invent - work with what's available"""


def build_prompts(lang: str, sign1: str, sign2: str, full_context: str) -> tuple[str, str]:
    """Devolve (system_prompt, user_prompt) para o idioma; qualquer idioma que não seja 'pt' usa inglês."""
    chave = 'pt' if lang == 'pt' else 'en'
    builder = _user_prompt_pt if chave == 'pt' else _user_prompt_en
    return SYSTEM_PROMPTS[chave], builder(sign1, sign2, full_context)

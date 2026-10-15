from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel
from typing import Optional


router = APIRouter()


class SynastryRequest(BaseModel):
    sign1: str  # Signo da primeira pessoa
    sign2: str  # Signo da segunda pessoa
    language: str = 'pt'  # Idioma da interpretação



class SynastryResponse(BaseModel):
    interpretation: str
    generated_by: str
    sign1_info: Optional[str] = None  # Informações sobre signo 1
    sign2_info: Optional[str] = None  # Informações sobre signo 2



@router.post("/synastry/interpretation", response_model=SynastryResponse)
async def get_synastry_interpretation(
    request: SynastryRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Endpoint específico para sinastria que busca características detalhadas
    de cada signo no RAG antes de gerar a interpretação.
    """
    try:
        from app.services.rag_service_fastembed import get_rag_service
        from app.services.ai_provider_service import get_ai_provider
        
        rag_service = get_rag_service()
        provider = get_ai_provider()
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de IA não disponível"
            )
        
        lang = request.language.lower()
        sign1 = request.sign1.strip()
        sign2 = request.sign2.strip()
        
        print(f"[SINASTRIA] Gerando interpretação para {sign1} + {sign2} (idioma: {lang})")
        
        # 1. Buscar informações específicas sobre o Signo 1 (busca mais abrangente)
        sign1_queries = [
            f"{sign1} características personalidade traços comportamento",
            f"{sign1} emoções valores comunicação relacionamentos",
            f"{sign1} signo elemento modalidade",
            f"{sign1} planeta regente casa natural"
        ] if lang == 'pt' else [
            f"{sign1} characteristics personality traits behavior",
            f"{sign1} emotions values communication relationships",
            f"{sign1} sign element modality",
            f"{sign1} ruling planet natural house"
        ]
        
        print(f"[SINASTRIA] Buscando informações detalhadas sobre {sign1}...")
        sign1_all_results = []
        for query in sign1_queries:
            results = rag_service.search(
                query=query,
                top_k=8,
                category='astrology',
                expand_query=True
            )
            sign1_all_results.extend(results)
        
        # Remover duplicatas mantendo os mais relevantes
        seen_texts = set()
        sign1_unique_results = []
        for r in sign1_all_results:
            text = r.get('text', '')[:200]  # Primeiros 200 chars como chave
            if text not in seen_texts:
                seen_texts.add(text)
                sign1_unique_results.append(r)
        
        # Ordenar por relevância e pegar os melhores
        sign1_unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        sign1_context = "\n\n".join([r.get('text', '') for r in sign1_unique_results[:10]])
        print(f"[SINASTRIA] Encontradas {len(sign1_unique_results)} informações sobre {sign1} (usando top 10)")
        
        # 2. Buscar informações específicas sobre o Signo 2 (busca mais abrangente)
        sign2_queries = [
            f"{sign2} características personalidade traços comportamento",
            f"{sign2} emoções valores comunicação relacionamentos",
            f"{sign2} signo elemento modalidade",
            f"{sign2} planeta regente casa natural"
        ] if lang == 'pt' else [
            f"{sign2} characteristics personality traits behavior",
            f"{sign2} emotions values communication relationships",
            f"{sign2} sign element modality",
            f"{sign2} ruling planet natural house"
        ]
        
        print(f"[SINASTRIA] Buscando informações detalhadas sobre {sign2}...")
        sign2_all_results = []
        for query in sign2_queries:
            results = rag_service.search(
                query=query,
                top_k=8,
                category='astrology',
                expand_query=True
            )
            sign2_all_results.extend(results)
        
        # Remover duplicatas mantendo os mais relevantes
        seen_texts = set()
        sign2_unique_results = []
        for r in sign2_all_results:
            text = r.get('text', '')[:200]  # Primeiros 200 chars como chave
            if text not in seen_texts:
                seen_texts.add(text)
                sign2_unique_results.append(r)
        
        # Ordenar por relevância e pegar os melhores
        sign2_unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        sign2_context = "\n\n".join([r.get('text', '') for r in sign2_unique_results[:10]])
        print(f"[SINASTRIA] Encontradas {len(sign2_unique_results)} informações sobre {sign2} (usando top 10)")
        
        # 3. Buscar informações específicas sobre sinastria/compatibilidade entre os dois signos
        synastry_queries = [
            f"sinastria compatibilidade {sign1} com {sign2}",
            f"relacionamento {sign1} {sign2} dinâmica",
            f"{sign1} {sign2} pontos fortes desafios",
            f"compatibilidade {sign1} {sign2} casal"
        ] if lang == 'pt' else [
            f"synastry compatibility {sign1} with {sign2}",
            f"relationship {sign1} {sign2} dynamics",
            f"{sign1} {sign2} strengths challenges",
            f"compatibility {sign1} {sign2} couple"
        ]
        
        print(f"[SINASTRIA] Buscando informações sobre compatibilidade {sign1} + {sign2}...")
        synastry_all_results = []
        for query in synastry_queries:
            results = rag_service.search(
                query=query,
                top_k=8,
                category='astrology',
                expand_query=True
            )
            synastry_all_results.extend(results)
        
        # Remover duplicatas mantendo os mais relevantes
        seen_texts = set()
        synastry_unique_results = []
        for r in synastry_all_results:
            text = r.get('text', '')[:200]
            if text not in seen_texts:
                seen_texts.add(text)
                synastry_unique_results.append(r)
        
        # Ordenar por relevância e pegar os melhores
        synastry_unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        synastry_context = "\n\n".join([r.get('text', '') for r in synastry_unique_results[:10]])
        print(f"[SINASTRIA] Encontradas {len(synastry_unique_results)} informações sobre compatibilidade (usando top 10)")
        
        # Validar que temos contexto suficiente
        if not sign1_context or len(sign1_context) < 100:
            print(f"[SINASTRIA] AVISO: Pouco contexto encontrado sobre {sign1}, tentando busca alternativa...")
            # Busca alternativa mais genérica
            alt_results = rag_service.search(
                query=sign1,
                top_k=10,
                category='astrology',
                expand_query=True
            )
            if alt_results:
                sign1_context = "\n\n".join([r.get('text', '') for r in alt_results[:5]])
        
        if not sign2_context or len(sign2_context) < 100:
            print(f"[SINASTRIA] AVISO: Pouco contexto encontrado sobre {sign2}, tentando busca alternativa...")
            # Busca alternativa mais genérica
            alt_results = rag_service.search(
                query=sign2,
                top_k=10,
                category='astrology',
                expand_query=True
            )
            if alt_results:
                sign2_context = "\n\n".join([r.get('text', '') for r in alt_results[:5]])
        
        # 4. Limpar e filtrar contexto para remover informações confusas
        def clean_context(text: str, sign_name: str) -> str:
            """Remove informações sobre posicionamentos específicos que podem confundir"""
            if not text:
                return text
            
            # Manter apenas informações sobre características gerais do signo
            # Remover referências a posicionamentos específicos que não sejam relevantes
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                # Manter linhas que falam sobre características, personalidade, comportamento
                # Remover linhas que mencionam posicionamentos específicos sem contexto
                if any(keyword in line.lower() for keyword in [
                    'característica', 'personalidade', 'traço', 'comportamento',
                    'emoção', 'valor', 'comunicação', 'relacionamento',
                    'elemento', 'modalidade', 'rege', 'regente',
                    'characteristic', 'personality', 'trait', 'behavior',
                    'emotion', 'value', 'communication', 'relationship',
                    'element', 'modality', 'rules', 'ruling'
                ]):
                    cleaned_lines.append(line)
                elif sign_name.lower() in line.lower():
                    # Manter linhas que mencionam o signo
                    cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines) if cleaned_lines else text
        
        # Limpar contextos
        sign1_context_cleaned = clean_context(sign1_context, sign1)
        sign2_context_cleaned = clean_context(sign2_context, sign2)
        synastry_context_cleaned = clean_context(synastry_context, f"{sign1} {sign2}")
        
        # 5. Combinar todo o contexto
        full_context = f"""
INFORMAÇÕES SOBRE {sign1.upper()} (CARACTERÍSTICAS GERAIS DO SIGNO):
{sign1_context_cleaned}

---

INFORMAÇÕES SOBRE {sign2.upper()} (CARACTERÍSTICAS GERAIS DO SIGNO):
{sign2_context_cleaned}

---

INFORMAÇÕES SOBRE COMPATIBILIDADE ENTRE {sign1.upper()} E {sign2.upper()}:
{synastry_context_cleaned}
"""
        
        # Log do contexto encontrado
        total_context_length = len(sign1_context) + len(sign2_context) + len(synastry_context)
        print(f"[SINASTRIA] Contexto total encontrado: {total_context_length} caracteres")
        print(f"[SINASTRIA] - {sign1}: {len(sign1_context)} caracteres")
        print(f"[SINASTRIA] - {sign2}: {len(sign2_context)} caracteres")
        print(f"[SINASTRIA] - Compatibilidade: {len(synastry_context)} caracteres")
        
        # Validação: garantir que temos contexto suficiente
        if total_context_length < 200:
            print(f"[SINASTRIA] AVISO: Contexto muito pequeno ({total_context_length} chars). Buscando mais informações...")
            # Busca de emergência mais genérica
            emergency_results = rag_service.search(
                query=f"{sign1} {sign2}",
                top_k=15,
                category='astrology',
                expand_query=True
            )
            if emergency_results:
                emergency_context = "\n\n".join([r.get('text', '') for r in emergency_results[:10]])
                full_context += f"\n\n---\n\nINFORMAÇÕES ADICIONAIS:\n{emergency_context}"
                print(f"[SINASTRIA] Contexto de emergência adicionado: {len(emergency_context)} caracteres")
        
        # Garantir que o contexto não está vazio
        if not full_context or len(full_context.strip()) < 100:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Não foi possível encontrar informações suficientes sobre {sign1} e {sign2} na base de conhecimento. Tente novamente mais tarde."
            )
        
        # VALIDAÇÃO: Verificar se o contexto contém informações válidas sobre os signos
        # Remover informações que possam ser confusas ou incorretas
        def validate_context(context_text: str, sign_name: str) -> tuple:
            """
            Valida o contexto do RAG e retorna contexto limpo + avisos.
            Remove informações que possam ser calculadas incorretamente ou inventadas.
            """
            if not context_text:
                return "", []
            
            warnings = []
            lines = context_text.split('\n')
            validated_lines = []
            
            for line in lines:
                line_lower = line.lower()
                
                # AVISO: Se mencionar posicionamentos específicos sem contexto de cálculo
                if any(phrase in line_lower for phrase in [
                    f'{sign_name.lower()} em ', f'{sign_name.lower()} na casa',
                    f'in {sign_name.lower()}', f'em {sign_name.lower()} na'
                ]):
                    # Verificar se é uma menção válida (regência) ou inválida (posicionamento inventado)
                    if any(valid in line_lower for valid in ['rege', 'regente', 'rules', 'ruling']):
                        # É sobre regência - válido
                        validated_lines.append(line)
                    else:
                        # Pode ser posicionamento inventado - remover
                        warnings.append(f"Removida linha que pode conter posicionamento inventado: {line[:100]}")
                        continue
                
                # Manter linhas sobre características gerais
                if any(keyword in line_lower for keyword in [
                    'característica', 'personalidade', 'traço', 'comportamento',
                    'elemento', 'modalidade', 'rege', 'regente',
                    'characteristic', 'personality', 'trait', 'behavior',
                    'element', 'modality', 'rules', 'ruling'
                ]):
                    validated_lines.append(line)
                elif sign_name.lower() in line_lower:
                    # Manter se menciona o signo
                    validated_lines.append(line)
            
            validated_text = '\n'.join(validated_lines)
            
            # Validar tamanho mínimo
            if len(validated_text) < 50:
                warnings.append(f"Contexto validado muito pequeno para {sign_name}")
            
            return validated_text, warnings
        
        # Validar cada contexto
        sign1_validated, sign1_warnings = validate_context(sign1_context_cleaned, sign1)
        sign2_validated, sign2_warnings = validate_context(sign2_context_cleaned, sign2)
        synastry_validated, synastry_warnings = validate_context(synastry_context_cleaned, f"{sign1} {sign2}")
        
        # Log de avisos
        all_warnings = sign1_warnings + sign2_warnings + synastry_warnings
        if all_warnings:
            print(f"[SINASTRIA] AVISOS DE VALIDAÇÃO:")
            for warning in all_warnings:
                print(f"  - {warning}")
        
        # Atualizar contexto com versões validadas
        full_context = f"""
INFORMAÇÕES SOBRE {sign1.upper()} (CARACTERÍSTICAS GERAIS DO SIGNO - VALIDADAS):
{sign1_validated}

---

INFORMAÇÕES SOBRE {sign2.upper()} (CARACTERÍSTICAS GERAIS DO SIGNO - VALIDADAS):
{sign2_validated}

---

INFORMAÇÕES SOBRE COMPATIBILIDADE ENTRE {sign1.upper()} E {sign2.upper()} (VALIDADAS):
{synastry_validated}
"""
        
        # Validação final: garantir que temos contexto válido suficiente
        total_validated_length = len(sign1_validated) + len(sign2_validated) + len(synastry_validated)
        if total_validated_length < 200:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Contexto validado insuficiente sobre {sign1} e {sign2}. Informações encontradas: {total_validated_length} caracteres (mínimo: 200)."
            )
        
        print(f"[SINASTRIA] Contexto validado: {total_validated_length} caracteres")
        
        # 6. Gerar interpretação personalizada usando o contexto completo
        if lang == 'pt':
            system_prompt = """Você é um astrólogo experiente especializado em sinastria e análise de compatibilidade entre SIGNOS DO ZODÍACO. 
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
- Inclua pontos fortes, desafios e orientações práticas específicas baseadas no contexto"""
            
            user_prompt = f"""SINASTRIA / COMPATIBILIDADE ENTRE {sign1.upper()} E {sign2.upper()}:

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
        else:
            system_prompt = """You are an experienced astrologer specialized in synastry and compatibility analysis between ZODIAC SIGNS. 
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
- Include strengths, challenges and specific practical guidance based on the context"""
            
            user_prompt = f"""SYNASTRY / COMPATIBILITY BETWEEN {sign1.upper()} AND {sign2.upper()}:

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
        
        # Usar modelo profissional do Groq (configurável via GROQ_MODEL)
        from app.core.config import settings
        groq_model = getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant')
        
        print(f"[SINASTRIA] Gerando interpretação com IA (modelo: {groq_model})...")
        interpretation = provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=4000,
            model=groq_model
        )
        
        # Limpar interpretação (remover instruções internas se houver)
        interpretation = interpretation.strip()
        
        return SynastryResponse(
            interpretation=interpretation,
            generated_by=provider.get_provider_name(),
            sign1_info=sign1_context[:500] if sign1_context else None,
            sign2_info=sign2_context[:500] if sign2_context else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao gerar interpretação de sinastria: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar interpretação de sinastria: {str(e)}"
        )

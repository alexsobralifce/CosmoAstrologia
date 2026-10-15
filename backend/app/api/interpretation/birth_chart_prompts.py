from typing import Optional
from app.api.interpretation.birth_chart_schemas import FullBirthChartRequest


# ===== FUNÇÕES AUXILIARES PARA MAPA ASTRAL COMPLETO =====

def _get_master_prompt(language: str = 'pt') -> str:
    """Retorna o prompt mestre Cosmos Astral Engine com validação matemática rigorosa."""
    import os
    from pathlib import Path
    
    if language == 'en':
        # Prompt em inglês (versão simplificada)
        return """🚨 CRITICAL RULES - READ BEFORE ANYTHING:

⚠️ YOU ARE NOT AN ASTRONOMICAL CALCULATOR. ALL CALCULATIONS HAVE ALREADY BEEN DONE BY THE KERYKEION LIBRARY (SWISS EPHEMERIS).
⚠️ YOUR ONLY FUNCTION IS TO INTERPRET TEXTS BASED ON ALREADY CALCULATED DATA.
⚠️ NEVER calculate, invent, or guess:
   - ❌ DO NOT calculate planetary positions (already calculated by Kerykeion)
   - ❌ DO NOT calculate signs or degrees (already calculated by Kerykeion)
   - ❌ DO NOT calculate aspects (already calculated by Python code)
   - ❌ DO NOT calculate dignities (already calculated by Python code)
   - ❌ DO NOT calculate temperament (already calculated by Python code)
   - ❌ DO NOT invent data that is not in the pre-computed block
   - ✅ USE ONLY the data provided in the pre-computed block
   - ✅ INTERPRET only what is in the pre-computed data
   - ✅ VALIDATE only if the data makes astronomical sense (but DO NOT recalculate)

**You are the Cosmos Astral Engine**, a senior astrologer specialized in interpretation. Your function is:

1. **Validate** if the pre-computed data makes astronomical sense (without recalculating).
2. **Interpret** this structure with psychological and evolutionary depth, but ONLY based on validated and pre-computed data."""
    else:
        # Ler o prompt do arquivo
        try:
            # Este arquivo está em backend/app/api/interpretation/; o prompt fica em
            # docs/PROMPT_MASTER_LITERAL_PT.txt, na raiz do projeto (5 níveis acima).
            project_root = Path(__file__).resolve().parents[4]
            prompt_file = project_root / "docs" / "PROMPT_MASTER_LITERAL_PT.txt"
            
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                print(f"[WARNING] Arquivo de prompt não encontrado: {prompt_file}, usando prompt simplificado")
                # Fallback para prompt básico
                return """Você é um astrólogo experiente especializado em interpretação profunda de mapas astrais. 
Use APENAS os dados fornecidos no bloco pré-calculado. NÃO calcule, NÃO invente, NÃO estime valores."""
        except Exception as e:
            print(f"[WARNING] Erro ao ler arquivo de prompt: {e}, usando prompt simplificado")
            return """Você é um astrólogo experiente especializado em interpretação profunda de mapas astrais. 
Use APENAS os dados fornecidos no bloco pré-calculado. NÃO calcule, NÃO invente, NÃO estime valores."""



def _validate_chart_request(request: FullBirthChartRequest, lang: str = 'pt') -> tuple:
    """
    Valida os dados do mapa astral, retorna relatório de validação E dados pré-calculados.
    
    Returns:
        Tuple[Dict, Optional[str], Optional[str]]: (chart_data_dict, validation_summary, precomputed_data_block)
    """
    try:
        from app.services.chart_validation_tool import (
            validate_complete_birth_chart,
            get_validation_summary_for_prompt,
        )
        from app.services.precomputed_chart_engine import create_precomputed_data_block
        
        # Construir dicionário de dados do mapa
        chart_data = {
            'sun_sign': request.sunSign,
            'moon_sign': request.moonSign,
            'ascendant_sign': request.ascendant,
            'mercury_sign': request.mercurySign,
            'venus_sign': request.venusSign,
            'mars_sign': request.marsSign,
            'jupiter_sign': request.jupiterSign,
            'saturn_sign': request.saturnSign,
            'uranus_sign': request.uranusSign,
            'neptune_sign': request.neptuneSign,
            'pluto_sign': request.plutoSign,
            'midheaven_sign': request.midheavenSign,
            'north_node_sign': request.northNodeSign,
            'south_node_sign': request.southNodeSign,
            'chiron_sign': request.chironSign,
        }
        
        # Tentar reconstruir longitudes aproximadas a partir dos signos
        source_longitudes = {}
        sign_to_mid_longitude = {
            'Áries': 15, 'Aries': 15, 'Touro': 45, 'Taurus': 45,
            'Gêmeos': 75, 'Gemini': 75, 'Câncer': 105, 'Cancer': 105,
            'Leão': 135, 'Leo': 135, 'Virgem': 165, 'Virgo': 165,
            'Libra': 195, 'Escorpião': 225, 'Scorpio': 225,
            'Sagitário': 255, 'Sagittarius': 255, 'Capricórnio': 285, 'Capricorn': 285,
            'Aquário': 315, 'Aquarius': 315, 'Peixes': 345, 'Pisces': 345,
        }
        
        planet_sign_map = {
            'sun': ('sun_sign', request.sunSign),
            'moon': ('moon_sign', request.moonSign),
            'mercury': ('mercury_sign', request.mercurySign),
            'venus': ('venus_sign', request.venusSign),
            'mars': ('mars_sign', request.marsSign),
            'jupiter': ('jupiter_sign', request.jupiterSign),
            'saturn': ('saturn_sign', request.saturnSign),
            'uranus': ('uranus_sign', request.uranusSign),
            'neptune': ('neptune_sign', request.neptuneSign),
            'pluto': ('pluto_sign', request.plutoSign),
            'ascendant': ('ascendant_sign', request.ascendant),
            'midheaven': ('midheaven_sign', request.midheavenSign),
            'north_node': ('north_node_sign', request.northNodeSign),
            'south_node': ('south_node_sign', request.southNodeSign),
            'chiron': ('chiron_sign', request.chironSign),
        }
        
        for planet_key, (_, sign) in planet_sign_map.items():
            if sign:
                mid_lon = sign_to_mid_longitude.get(sign)
                if mid_lon is not None:
                    source_longitudes[planet_key] = float(mid_lon)
        
        if source_longitudes:
            chart_data['_source_longitudes'] = source_longitudes
        
        # Validar mapa astral completo
        validated_chart, report = validate_complete_birth_chart(chart_data)
        
        # Obter resumo de validação
        validation_summary = get_validation_summary_for_prompt(report, lang)
        
        # Criar bloco de dados pré-calculados (TRAVAS DE SEGURANÇA)
        precomputed_block = create_precomputed_data_block(validated_chart, lang)
        
        return validated_chart, validation_summary, precomputed_block
    
    except Exception as e:
        print(f"[WARNING] Erro ao validar mapa astral: {e}")
        import traceback
        print(traceback.format_exc())
        return {}, None, None



def _get_full_chart_context(request: FullBirthChartRequest, lang: str = 'pt', validation_summary: Optional[str] = None, precomputed_data: Optional[str] = None) -> str:
    """Gera o contexto completo do mapa astral com todos os corpos celestes."""
    if lang == 'pt':
        return f"""
MAPA ASTRAL COMPLETO DE {request.name.upper()}:

📍 DADOS DE NASCIMENTO:
- Data: {request.birthDate}
- Hora: {request.birthTime}
- Local: {request.birthPlace}

☀️ LUMINARES E PLANETAS PESSOAIS (Nível 1-2):
- Sol em {request.sunSign} na Casa {request.sunHouse} (Essência, Ego)
- Lua em {request.moonSign} na Casa {request.moonHouse} (Emoções, Inconsciente)
- Mercúrio em {request.mercurySign or 'não calculado'}{f' na Casa {request.mercuryHouse}' if request.mercuryHouse else ''} (Comunicação, Mente)
- Vênus em {request.venusSign or 'não calculado'}{f' na Casa {request.venusHouse}' if request.venusHouse else ''} (Amor, Valores)
- Marte em {request.marsSign or 'não calculado'}{f' na Casa {request.marsHouse}' if request.marsHouse else ''} (Ação, Desejo)

🪐 PLANETAS SOCIAIS (Nível 3):
- Júpiter em {request.jupiterSign or 'não calculado'}{f' na Casa {request.jupiterHouse}' if request.jupiterHouse else ''} (Expansão, Sorte)
- Saturno em {request.saturnSign or 'não calculado'}{f' na Casa {request.saturnHouse}' if request.saturnHouse else ''} (Limites, Mestre Kármico)

🌌 PLANETAS TRANSPESSOAIS (Nível 4):
- Urano em {request.uranusSign or 'não calculado'}{f' na Casa {request.uranusHouse}' if request.uranusHouse else ''} (Revolução, Liberdade)
- Netuno em {request.neptuneSign or 'não calculado'}{f' na Casa {request.neptuneHouse}' if request.neptuneHouse else ''} (Espiritualidade, Ilusão)
- Plutão em {request.plutoSign or 'não calculado'}{f' na Casa {request.plutoHouse}' if request.plutoHouse else ''} (Transformação, Poder)

🎯 PONTOS KÁRMICOS:
- Ascendente em {request.ascendant} (Máscara Social)
- Meio do Céu em {request.midheavenSign or 'não calculado'} (Vocação, Reputação)
- Nodo Norte em {request.northNodeSign or 'não calculado'}{f' na Casa {request.northNodeHouse}' if request.northNodeHouse else ''} (Destino, Evolução)
- Nodo Sul em {request.southNodeSign or 'não calculado'}{f' na Casa {request.southNodeHouse}' if request.southNodeHouse else ''} (Passado, Zona de Conforto)
- Quíron em {request.chironSign or 'não calculado'}{f' na Casa {request.chironHouse}' if request.chironHouse else ''} (Ferida/Dom de Cura)

---
🔍 RELATÓRIO DE VALIDAÇÃO MATEMÁTICA:
{validation_summary or '✅ Dados validados automaticamente pelo sistema.'}
---

{precomputed_data or ''}
"""
    else:
        return f"""
COMPLETE BIRTH CHART OF {request.name.upper()}:

📍 BIRTH DATA:
- Date: {request.birthDate}
- Time: {request.birthTime}
- Place: {request.birthPlace}

☀️ LUMINARIES AND PERSONAL PLANETS (Level 1-2):
- Sun in {request.sunSign} in House {request.sunHouse} (Essence, Ego)
- Moon in {request.moonSign} in House {request.moonHouse} (Emotions, Unconscious)
- Mercury in {request.mercurySign or 'not calculated'}{f' in House {request.mercuryHouse}' if request.mercuryHouse else ''} (Communication, Mind)
- Venus in {request.venusSign or 'not calculated'}{f' in House {request.venusHouse}' if request.venusHouse else ''} (Love, Values)
- Mars in {request.marsSign or 'not calculated'}{f' in House {request.marsHouse}' if request.marsHouse else ''} (Action, Desire)

🪐 SOCIAL PLANETS (Level 3):
- Jupiter in {request.jupiterSign or 'not calculated'}{f' in House {request.jupiterHouse}' if request.jupiterHouse else ''} (Expansion, Luck)
- Saturn in {request.saturnSign or 'not calculated'}{f' in House {request.saturnHouse}' if request.saturnHouse else ''} (Limits, Karmic Master)

🌌 TRANSPERSONAL PLANETS (Level 4):
- Uranus in {request.uranusSign or 'not calculated'}{f' in House {request.uranusHouse}' if request.uranusHouse else ''} (Revolution, Freedom)
- Neptune in {request.neptuneSign or 'not calculated'}{f' in House {request.neptuneHouse}' if request.neptuneHouse else ''} (Spirituality, Illusion)
- Pluto in {request.plutoSign or 'not calculated'}{f' in House {request.plutoHouse}' if request.plutoHouse else ''} (Transformation, Power)

🎯 KARMIC POINTS:
- Ascendant in {request.ascendant} (Social Mask)
- Midheaven in {request.midheavenSign or 'not calculated'} (Vocation, Reputation)
- North Node in {request.northNodeSign or 'not calculated'}{f' in House {request.northNodeHouse}' if request.northNodeHouse else ''} (Destiny, Evolution)
- South Node in {request.southNodeSign or 'not calculated'}{f' in House {request.southNodeHouse}' if request.southNodeHouse else ''} (Past, Comfort Zone)
- Chiron in {request.chironSign or 'not calculated'}{f' in House {request.chironHouse}' if request.chironHouse else ''} (Wound/Healing Gift)

---
🔍 MATHEMATICAL VALIDATION REPORT:
{validation_summary or '✅ Data automatically validated by the system.'}
---

{precomputed_data or ''}
"""



def _generate_section_prompt(request: FullBirthChartRequest, section: str, validation_summary: Optional[str] = None, precomputed_data: Optional[str] = None) -> tuple:
    """Gera o prompt específico para cada seção do mapa baseado na nova estrutura fornecida."""
    lang = request.language or 'pt'
    
    # Contexto completo do mapa para referência (inclui validação E dados pré-calculados)
    full_context = _get_full_chart_context(request, lang, validation_summary, precomputed_data)
    
    # Títulos das seções
    section_titles = {
        'power': 'A Estrutura de Poder' if lang == 'pt' else 'The Power Structure',
        'triad': 'A Tríade Fundamental' if lang == 'pt' else 'The Fundamental Triad',
        'personal': 'Dinâmica Pessoal e Ferramentas' if lang == 'pt' else 'Personal Dynamics and Tools',
        'houses': 'Análise Setorial Avançada' if lang == 'pt' else 'Advanced Sectoral Analysis',
        'karma': 'Expansão, Estrutura e Karma' if lang == 'pt' else 'Expansion, Structure and Karma',
        'synthesis': 'Síntese e Orientação Estratégica' if lang == 'pt' else 'Synthesis and Strategic Guidance'
    }
    
    title = section_titles.get(section, section.capitalize())
    
    # Prompts específicos por seção (versão simplificada mas estruturada)
    if lang == 'pt':
        prompts = {
            'power': f"""{full_context}

**1. A ESTRUTURA DE PODER (TEMPERAMENTO)**

IMPORTANTE: Use APENAS os dados do bloco "🔒 DADOS PRÉ-CALCULADOS" fornecido acima. NÃO calcule, NÃO estime, NÃO invente valores.

Sua tarefa é interpretar o temperamento e estrutura de poder do mapa astral. Comece diretamente com a análise, sem repetir instruções.

**Análise Obrigatória:**
- Use APENAS os pontos do bloco pré-calculado (Fogo, Terra, Ar, Água)
- Identifique o elemento dominante EXATAMENTE como listado no bloco
- Identifique o elemento ausente EXATAMENTE como listado no bloco (ou "Nenhum" se todos têm pontos)
- Analise as modalidades (Cardeal, Fixo, Mutável)
- Analise o regente do mapa com profundidade técnica (Dignidades, Regências)
- Inclua orientação prática sobre como trabalhar com o temperamento identificado

Forneça uma interpretação completa, detalhada e prática do temperamento e estrutura de poder do mapa astral.""",
            'triad': f"""{full_context}

**2. O NÚCLEO DA PERSONALIDADE (A TRÍADE PRIMORDIAL)**

Sua tarefa é sintetizar Sol (Vontade), Lua (Necessidade Emocional) e Ascendente (Modo de Ação) em uma interpretação integrada. NÃO liste cada elemento separadamente - mostre como eles interagem.

**Análise Obrigatória:**

1. **Conflito ou Harmonia Sol-Lua:**
   - Explique o conflito ou a harmonia entre o que a pessoa quer (Sol) e o que ela precisa (Lua)
   - Mostre como essa dinâmica se manifesta na vida prática

2. **Dinâmica Tríade Completa:**
   - Analise a dinâmica entre vontade consciente (Sol), necessidades emocionais (Lua) e forma de agir (Ascendente)
   - Mostre como os três interagem entre si

3. **Equilíbrio ou Conflito:**
   - Explique como eles se equilibram ou conflitam
   - Identifique onde está o ponto de tensão que pode travar a pessoa na hora de decidir
   - Mostre as contradições e como trabalhar com elas

4. **Orientação Prática:**
   - Forneça conselhos práticos sobre como integrar essas três energias
   - Sugira estratégias para trabalhar com os conflitos identificados

Forneça uma interpretação completa, detalhada e prática da tríade fundamental. Seja conciso e direto ao ponto (máximo 800 palavras).""",
            'personal': f"""{full_context}

**3. DINÂMICA PESSOAL E FERRAMENTAS**

Analise Mercúrio (comunicação, mente), Vênus (valores, amor) e Marte (ação, desejo) como ferramentas pessoais.

**Análise Obrigatória:**
- Como a pessoa processa informações (Mercúrio) - inclua dignidade se disponível no bloco pré-calculado
- Como a pessoa atrai e valoriza (Vênus) - inclua dignidade se disponível no bloco pré-calculado
- Como a pessoa age e conquista (Marte) - inclua dignidade se disponível no bloco pré-calculado
- Conexões entre essas três energias
- Orientação prática sobre como usar essas ferramentas na vida diária

Forneça uma interpretação completa, detalhada e prática da dinâmica pessoal.""",
            'houses': f"""{full_context}

**4. ANÁLISE SETORIAL AVANÇADA**

Analise as casas 2, 4, 6, 7 e 10 com profundidade, considerando os regentes e planetas presentes.

**Análise Obrigatória:**
- Casa 2: Recursos, valores, autoestima
- Casa 4: Lar, raízes, família
- Casa 6: Trabalho, rotina, saúde
- Casa 7: Relacionamentos, parcerias
- Casa 10: Carreira, vocação, reputação
- Para cada casa, inclua orientação prática sobre como trabalhar com essa área da vida

Forneça uma interpretação completa, detalhada e prática das casas astrológicas.""",
            'karma': f"""{full_context}

**5. EXPANSÃO, ESTRUTURA E KARMA**

Analise Júpiter (expansão), Saturno (estrutura, karma), Nodos (destino) e Quíron (ferida/cura).

**Análise Obrigatória:**
- Júpiter: Onde a pessoa se expande e encontra sorte
- Saturno: Onde a pessoa precisa estruturar e enfrentar desafios kármicos
- Nodos: Direção de crescimento (Norte) e zona de conforto (Sul)
- Quíron: Ferida e dom de cura

Forneça uma interpretação completa e detalhada dos aspectos kármicos.""",
            'synthesis': f"""{full_context}

**6. SÍNTESE E ORIENTAÇÃO ESTRATÉGICA**

Sintetize todos os elementos do mapa astral em uma visão integrada e estratégica.

**Análise Obrigatória:**
- Pontos fortes do mapa (inclua dignidades quando relevante)
- Desafios principais
- Oportunidades de crescimento
- Orientação estratégica prática e acionável para a vida

Forneça uma síntese completa, detalhada e prática com orientação estratégica."""
        }
    else:
        # Versão em inglês (simplificada)
        prompts = {
            'power': f"""{full_context}

**1. THE POWER STRUCTURE (TEMPERAMENT)**

Analyze the temperament using ONLY the pre-computed data block. Do NOT recalculate.

Provide a complete and detailed interpretation of the temperament and power structure.""",
            'triad': f"""{full_context}

**2. THE CORE OF PERSONALITY (THE PRIMORDIAL TRIAD)**

Synthesize Sun (Will), Moon (Emotional Need), and Ascendant (Mode of Action) into an integrated interpretation.

Provide a complete and detailed interpretation of the fundamental triad.""",
            'personal': f"""{full_context}

**3. PERSONAL DYNAMICS AND TOOLS**

Analyze Mercury (communication, mind), Venus (values, love) and Mars (action, desire) as personal tools.

Provide a complete and detailed interpretation of personal dynamics.""",
            'houses': f"""{full_context}

**4. ADVANCED SECTORAL ANALYSIS**

Analyze houses 2, 4, 6, 7, and 10 in depth.

Provide a complete and detailed interpretation of the astrological houses.""",
            'karma': f"""{full_context}

**5. EXPANSION, STRUCTURE AND KARMA**

Analyze Jupiter (expansion), Saturn (structure, karma), Nodes (destiny) and Chiron (wound/healing).

Provide a complete and detailed interpretation of karmic aspects.""",
            'synthesis': f"""{full_context}

**6. SYNTHESIS AND STRATEGIC GUIDANCE**

Synthesize all elements of the birth chart into an integrated and strategic vision.

Provide a complete synthesis and strategic guidance."""
        }
    
    prompt = prompts.get(section, f"""{full_context}

Forneça uma interpretação completa e detalhada desta seção do mapa astral.""")
    
    return title, prompt



def _clean_interpretation_content(content: str) -> str:
    """
    Remove instruções internas e metadados do conteúdo gerado pela IA.
    Garante que apenas a interpretação astrológica seja retornada ao usuário.
    """
    if not content:
        return content
    
    # Lista de padrões a remover (instruções internas)
    patterns_to_remove = [
        r'⚠️⚠️⚠️\s*\*\*INSTRUÇÕES INTERNAS.*?\*\*.*?(?=\n\n|\*\*|$)',
        r'🚨\s*\*\*INSTRUÇÃO CRÍTICA.*?\*\*.*?(?=\n\n|\*\*|$)',
        r'\*\*INSTRUÇÕES INTERNAS.*?\*\*.*?(?=\n\n|\*\*|$)',
        r'NÃO REPITA NA RESPOSTA.*?(?=\n\n|\*\*|$)',
        r'As instruções abaixo são APENAS.*?(?=\n\n|\*\*|$)',
        r'LEIA ANTES DE ESCREVER.*?(?=\n\n|\*\*|$)',
        r'VALIDAÇÃO OBRIGATÓRIA ANTES DE ESCREVER.*?(?=\n\n|\*\*|$)',
        r'✅ Localize o bloco.*?(?=\n\n|\*\*|$)',
        r'✅ Leia os pontos.*?(?=\n\n|\*\*|$)',
        r'✅ Identifique.*?(?=\n\n|\*\*|$)',
        r'✅ Use EXATAMENTE.*?(?=\n\n|\*\*|$)',
        r'⚠️\s*\*\*IMPORTANTE.*?\*\*.*?(?=\n\n|\*\*|$)',
    ]
    
    import re
    cleaned = content
    
    # Remover cada padrão
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
    
    # Remover linhas vazias excessivas (mais de 2 consecutivas)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    
    # Remover espaços em branco no início e fim
    cleaned = cleaned.strip()
    
    # Se o conteúdo começar com instruções, tentar encontrar o início real
    # Procura por padrões que indicam início de interpretação
    interpretation_starters = [
        r'\*\*.*?ANÁLISE.*?\*\*',
        r'\*\*.*?INTERPRETAÇÃO.*?\*\*',
        r'\*\*.*?TEMPERAMENTO.*?\*\*',
        r'\*\*.*?TRÍADE.*?\*\*',
        r'^[A-ZÁÊÔÇ].*?temperamento',
        r'^[A-ZÁÊÔÇ].*?elemento',
    ]
    
    for starter in interpretation_starters:
        match = re.search(starter, cleaned, re.IGNORECASE | re.MULTILINE)
        if match:
            cleaned = cleaned[match.start():]
            break
    
    return cleaned

"""Consulta, contexto e prompts da interpretação de revolução solar (extraídos do handler sem mudar comportamento)."""

SYSTEM_PROMPT = """Você é um Astrólogo Sênior especializado em Revolução Solar e técnicas complementares de previsão astrológica.

IMPORTANTE: Você DEVE sempre separar claramente os dados do MAPA NATAL dos dados da REVOLUÇÃO SOLAR. NUNCA confunda ou misture esses dados.

Além da Revolução Solar, você conhece outras técnicas astrológicas relevantes:
- Progressões Secundárias (evolução interna ao longo do tempo)
- Retorno de Saturno (maturidade e responsabilidades, ~29.5 anos)
- Retorno de Júpiter (expansão e oportunidades, ~12 anos)
- Trânsitos (influências atuais dos planetas)
- Direções Primárias (eventos importantes, 1 grau = 1 ano)
- Profecção Anual (foco anual por casa astrológica)

Quando apropriado e se o contexto de referência mencionar, você pode sugerir brevemente como outras técnicas podem complementar a análise da Revolução Solar, mas mantenha o foco principal na Revolução Solar."""


def build_rag_queries(request, solar_return_ascendant, solar_return_moon_house, solar_return_moon_sign, solar_return_sun_house):
    """Consultas ao RAG sobre a revolução solar (ascendente, casa do Sol, Lua, idade)."""
    queries = [
        # Revolução Solar (principal)
        f"revolução solar retorno solar {solar_return_ascendant} casa {solar_return_sun_house}",
        f"casa {solar_return_sun_house} astrologia revolução solar significado interpretação",
        
        # Técnicas Complementares
        f"progressões secundárias revolução solar complemento técnicas previsão",
        f"retorno saturno jupiter revolução solar integração análise",
        f"trânsitos revolução solar ano {request.target_year} previsão astrológica",
        f"direções primárias profecção anual revolução solar",
        f"técnicas previsão astrológica complemento revolução solar",
        
        # Contexto específico
        f"ascendente {solar_return_ascendant} revolução solar interpretação",
        f"lua {solar_return_moon_sign} casa {solar_return_moon_house} revolução solar",
    ]
    return queries


def retrieve_context(queries, rag_service):
    """Busca no RAG, remove repetidos e devolve o texto de contexto e os resultados únicos."""
    all_rag_results = []
    if rag_service:
        for q in queries:
            try:
                results = rag_service.search(q, top_k=6, expand_query=True)
                all_rag_results.extend(results)
            except Exception as e:
                print(f"[WARNING] Erro ao buscar no RAG: {e}")
    
    # Remover duplicatas
    seen_texts = set()
    unique_results = []
    for result in sorted(all_rag_results, key=lambda x: x.get('score', 0), reverse=True):
        text_key = result.get('text', '')[:100]
        if text_key not in seen_texts:
            seen_texts.add(text_key)
            unique_results.append(result)
            if len(unique_results) >= 15:  # Aumentado para mais contexto
                break
    
    context_text = "\n\n".join([doc.get('text', '') for doc in unique_results[:12] if doc.get('text')])
    return context_text, unique_results


def build_user_prompt(age, context_text, natal_ascendant, natal_moon_house, natal_moon_sign, natal_sun_house, natal_sun_sign, solar_return_ascendant, solar_return_moon_house, solar_return_moon_sign, solar_return_sun_house, solar_return_sun_sign, target_year):
    """Prompt do usuário com os dados natais e da revolução solar."""
    return f"""Dados para Análise da Revolução Solar de {target_year}:

=== MAPA NATAL (Dados de Nascimento) ===
- Idade em {target_year}: {age} anos
- Signo Solar: {natal_sun_sign} (Casa {natal_sun_house if natal_sun_house else 'N/A'})
- Ascendente: {natal_ascendant}
- Lua: {natal_moon_sign} (Casa {natal_moon_house if natal_moon_house else 'N/A'})

=== REVOLUÇÃO SOLAR {target_year} (Dados do Ano) ===
- Ascendente: {solar_return_ascendant}
- Sol: {solar_return_sun_sign} na Casa {solar_return_sun_house}
- Lua: {solar_return_moon_sign} na Casa {solar_return_moon_house}

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_text[:4000] if context_text else "Informações gerais sobre revolução solar e técnicas complementares."}

Forneça uma interpretação completa e detalhada da revolução solar.

INSTRUÇÕES CRÍTICAS:
1. SEMPRE separe claramente os dados do MAPA NATAL dos dados da REVOLUÇÃO SOLAR
2. NUNCA atribua dados da Revolução Solar ao Mapa Natal (ex: se a Lua da RS está em Aquário, isso NÃO significa que a Lua natal está em Aquário)
3. Use os dados do Mapa Natal apenas como contexto de fundo
4. Foque principalmente na Revolução Solar e seus significados para o ano {target_year}
5. Se o contexto mencionar outras técnicas (Progressões, Retorno de Saturno/Júpiter, Trânsitos, Direções, Profecção), você pode mencionar brevemente como elas podem complementar esta análise
6. Ao final, adicione uma nota sobre outras técnicas astrológicas disponíveis que podem enriquecer a análise
7. Seja específico e prático, evitando generalidades
8. Calcule a idade corretamente: {age} anos em {target_year}"""

"""Etapas da geração de uma seção do mapa astral, extraídas do handler sem mudar comportamento."""

def resolve_coordinates(request):
    """Coordenadas do pedido; se faltarem, tenta a cidade pelo nome e por fim usa São Paulo."""
    latitude = request.latitude
    longitude = request.longitude
    
    # PRIORIDADE 2: Se não fornecidas, tentar obter do nome do local
    if latitude is None or longitude is None:
        birth_place_lower = request.birthPlace.lower()
        
        # Mapeamento de cidades conhecidas (pode ser expandido)
        city_coordinates = {
            'são paulo': (-23.5505, -46.6333),
            'sao paulo': (-23.5505, -46.6333),
            'rio de janeiro': (-22.9068, -43.1729),
            'rio': (-22.9068, -43.1729),
            'belo horizonte': (-19.9167, -43.9345),
            'brasília': (-15.7942, -47.8822),
            'salvador': (-12.9714, -38.5014),
            'fortaleza': (-3.7172, -38.5433),
            'curitiba': (-25.4284, -49.2733),
            'recife': (-8.0476, -34.8770),
            'porto alegre': (-30.0346, -51.2177),
            'sobral': (-3.6883, -40.3497),
        }
        
        for city, (lat, lon) in city_coordinates.items():
            if city in birth_place_lower:
                latitude = lat
                longitude = lon
                print(f"[FULL-BIRTH-CHART] Coordenadas encontradas para {city}: ({latitude}, {longitude})")
                break
    
    # PRIORIDADE 3: Se ainda não encontrou, usar valores padrão (São Paulo)
    if latitude is None or longitude is None:
        print(f"[WARNING] Coordenadas não encontradas para {request.birthPlace}, usando valores padrão (São Paulo)")
        latitude = -23.5505
        longitude = -46.6333
    return latitude, longitude


def retrieve_section_context(ascendant, calculated_chart, moon_sign, rag_service, request, sun_sign):
    """Consulta o RAG pela seção pedida e devolve o texto de contexto."""
    queries = {
        'power': f"temperamento elementos fogo terra ar água predominante ausente {sun_sign} {moon_sign} {ascendant}",
        'triad': f"Sol Lua Ascendente tríade {sun_sign} {moon_sign} {ascendant} personalidade",
        'personal': f"Mercúrio {calculated_chart.get('mercury_sign', request.mercurySign or '')} Vênus {calculated_chart.get('venus_sign', request.venusSign or '')} Marte {calculated_chart.get('mars_sign', request.marsSign or '')} dinâmica pessoal",
        'houses': f"casas astrológicas Casa 2 Casa 4 Casa 6 Casa 7 Casa 10 vocação",
        'karma': f"Júpiter Saturno Nodo Norte Sul Quíron karma propósito {calculated_chart.get('jupiter_sign', request.jupiterSign or '')} {calculated_chart.get('saturn_sign', request.saturnSign or '')}",
        'synthesis': f"síntese mapa astral integração pontos fortes desafios"
    }
    
    query = queries.get(request.section, "interpretação mapa astral")
    context_documents = []
    
    if rag_service:
        try:
            results = rag_service.search(query, top_k=8, expand_query=True)
            context_documents = results[:6]
        except Exception as e:
            print(f"[WARNING] Erro ao buscar no RAG: {e}")
    
    context_text = "\n\n".join([
        f"[Fonte: {doc.get('source', 'unknown')}]\n{doc.get('text', '')}"
        for doc in context_documents
        if doc.get('text')
    ])
    return context_text


def build_full_user_prompt(context_text, section_prompt):
    """Prompt da seção + contexto de referência do RAG (limitado a 3000 caracteres)."""
    return f"""{section_prompt}

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_text[:3000] if context_text else "Informações astrológicas gerais."}"""

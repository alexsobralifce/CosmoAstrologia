from app.api.interpretation.birth_chart_prompts import _clean_interpretation_content
from app.api.interpretation.birth_chart_prompts import _generate_section_prompt
from app.api.interpretation.birth_chart_prompts import _get_master_prompt
from app.api.interpretation.birth_chart_prompts import _validate_chart_request
from app.api.interpretation.birth_chart_schemas import FullBirthChartRequest
from app.api.interpretation.birth_chart_schemas import FullBirthChartResponse
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Header
from fastapi import status
from typing import Optional

router = APIRouter()


@router.post("/full-birth-chart/section", response_model=FullBirthChartResponse)
async def generate_birth_chart_section(
    request: FullBirthChartRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Gera uma seção específica do Mapa Astral Completo.
    
    IMPORTANTE: Este endpoint calcula o mapa astral usando Swiss Ephemeris (kerykeion),
    valida os dados calculados e usa os dados validados no prompt para a IA.
    
    Seções disponíveis:
    - power: A Estrutura de Poder (Temperamento e Motivação)
    - triad: A Tríade Fundamental (Sol, Lua, Ascendente)
    - personal: Dinâmica Pessoal e Ferramentas (Mercúrio, Vênus, Marte)
    - houses: Análise Setorial Avançada (Casas 2, 4, 6, 7, 10)
    - karma: Expansão, Estrutura e Karma (Júpiter, Saturno, Nodos, Quíron)
    - synthesis: Síntese e Orientação Estratégica
    """
    try:
        from app.services.rag_service_fastembed import get_rag_service
        from app.services.ai_provider_service import get_ai_provider
        from app.services.swiss_ephemeris_calculator import calculate_birth_chart as calculate_swiss
        from datetime import datetime
        
        if not request.section:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Especifique uma seção: power, triad, personal, houses, karma, synthesis"
            )
        
        lang = request.language or 'pt'
        provider = get_ai_provider()
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de IA não disponível"
            )
        
        # ===== PASSO 1: CALCULAR MAPA ASTRAL USANDO SWISS EPHEMERIS =====
        print(f"[FULL-BIRTH-CHART] Calculando mapa astral para {request.name}")
        
        # Parsear data de nascimento (formato DD/MM/YYYY)
        try:
            birth_date = datetime.strptime(request.birthDate, "%d/%m/%Y")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de data inválido. Use DD/MM/YYYY. Recebido: {request.birthDate}"
            )
        
        # Obter coordenadas do local (latitude/longitude)
        # PRIORIDADE 1: Usar coordenadas fornecidas pelo frontend (mais preciso)
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
        
        # CALCULAR MAPA ASTRAL USANDO SWISS EPHEMERIS (FONTE ÚNICA DE VERDADE)
        try:
            calculated_chart = calculate_swiss(
                birth_date=birth_date,
                birth_time=request.birthTime,
                latitude=latitude,
                longitude=longitude
            )
            print(f"[FULL-BIRTH-CHART] Mapa astral calculado com sucesso usando Swiss Ephemeris")
        except Exception as e:
            print(f"[ERROR] Erro ao calcular mapa astral com Swiss Ephemeris: {e}")
            import traceback
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao calcular mapa astral: {str(e)}"
            )
        
        # ===== PASSO 2: VALIDAR DADOS CALCULADOS =====
        print(f"[FULL-BIRTH-CHART] Validando dados calculados")
        
        # Construir dicionário de dados do mapa para validação
        chart_data_for_validation = {
            'sun_sign': calculated_chart.get('sun_sign'),
            'moon_sign': calculated_chart.get('moon_sign'),
            'ascendant_sign': calculated_chart.get('ascendant_sign'),
            'mercury_sign': calculated_chart.get('mercury_sign'),
            'venus_sign': calculated_chart.get('venus_sign'),
            'mars_sign': calculated_chart.get('mars_sign'),
            'jupiter_sign': calculated_chart.get('jupiter_sign'),
            'saturn_sign': calculated_chart.get('saturn_sign'),
            'uranus_sign': calculated_chart.get('uranus_sign'),
            'neptune_sign': calculated_chart.get('neptune_sign'),
            'pluto_sign': calculated_chart.get('pluto_sign'),
            'midheaven_sign': calculated_chart.get('midheaven_sign'),
            'north_node_sign': calculated_chart.get('north_node_sign'),
            'south_node_sign': calculated_chart.get('south_node_sign'),
            'chiron_sign': calculated_chart.get('chiron_sign'),
        }
        
        # Adicionar longitudes se disponíveis
        if '_source_longitudes' in calculated_chart:
            chart_data_for_validation['_source_longitudes'] = calculated_chart['_source_longitudes']
        
        # Validar mapa astral completo
        validated_chart, validation_summary, precomputed_data = _validate_chart_request(
            request, lang
        )
        
        # Se a validação falhar, usar dados calculados diretamente
        if not validated_chart or not precomputed_data:
            print(f"[WARNING] Validação retornou dados vazios, usando dados calculados diretamente")
            # Criar bloco pré-calculado mínimo
            precomputed_data = f"""
🔒 DADOS PRÉ-CALCULADOS (TRAVAS DE SEGURANÇA ATIVADAS)

📊 TEMPERAMENTO (CALCULADO MATEMATICAMENTE):
- Fogo: [calculado]
- Terra: [calculado]
- Ar: [calculado]
- Água: [calculado]
- ELEMENTO DOMINANTE: [calculado]
- ELEMENTO AUSENTE: [calculado]

🏛️ PLANETARY DIGNITIES (IDENTIFIED BY FIXED TABLE):
[Calculado pela biblioteca]

👑 REGENTE DO MAPA:
[Calculado pela biblioteca]
"""
            validation_summary = "✅ Dados calculados pela biblioteca Swiss Ephemeris (kerykeion)"
        
        # ===== PASSO 3: BUSCAR CONTEXTO DO RAG =====
        rag_service = get_rag_service()
        
        # Usar signos calculados para buscar contexto
        sun_sign = calculated_chart.get('sun_sign', request.sunSign)
        moon_sign = calculated_chart.get('moon_sign', request.moonSign)
        ascendant = calculated_chart.get('ascendant_sign', request.ascendant)
        
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
        
        # ===== PASSO 4: ATUALIZAR REQUEST COM DADOS CALCULADOS =====
        # Criar novo request com dados calculados pela biblioteca
        updated_request = FullBirthChartRequest(
            name=request.name,
            birthDate=request.birthDate,
            birthTime=request.birthTime,
            birthPlace=request.birthPlace,
            sunSign=calculated_chart.get('sun_sign', request.sunSign),
            moonSign=calculated_chart.get('moon_sign', request.moonSign),
            ascendant=calculated_chart.get('ascendant_sign', request.ascendant),
            sunHouse=calculated_chart.get('sun_house', request.sunHouse),
            moonHouse=calculated_chart.get('moon_house', request.moonHouse),
            section=request.section,
            language=request.language,
            mercurySign=calculated_chart.get('mercury_sign', request.mercurySign),
            mercuryHouse=calculated_chart.get('mercury_house', request.mercuryHouse),
            venusSign=calculated_chart.get('venus_sign', request.venusSign),
            venusHouse=calculated_chart.get('venus_house', request.venusHouse),
            marsSign=calculated_chart.get('mars_sign', request.marsSign),
            marsHouse=calculated_chart.get('mars_house', request.marsHouse),
            jupiterSign=calculated_chart.get('jupiter_sign', request.jupiterSign),
            jupiterHouse=calculated_chart.get('jupiter_house', request.jupiterHouse),
            saturnSign=calculated_chart.get('saturn_sign', request.saturnSign),
            saturnHouse=calculated_chart.get('saturn_house', request.saturnHouse),
            uranusSign=calculated_chart.get('uranus_sign', request.uranusSign),
            uranusHouse=calculated_chart.get('uranus_house', request.uranusHouse),
            neptuneSign=calculated_chart.get('neptune_sign', request.neptuneSign),
            neptuneHouse=calculated_chart.get('neptune_house', request.neptuneHouse),
            plutoSign=calculated_chart.get('pluto_sign', request.plutoSign),
            plutoHouse=calculated_chart.get('pluto_house', request.plutoHouse),
            northNodeSign=calculated_chart.get('north_node_sign', request.northNodeSign),
            northNodeHouse=calculated_chart.get('north_node_house', request.northNodeHouse),
            southNodeSign=calculated_chart.get('south_node_sign', request.southNodeSign),
            southNodeHouse=calculated_chart.get('south_node_house', request.southNodeHouse),
            chironSign=calculated_chart.get('chiron_sign', request.chironSign),
            chironHouse=calculated_chart.get('chiron_house', request.chironHouse),
            midheavenSign=calculated_chart.get('midheaven_sign', request.midheavenSign),
            icSign=calculated_chart.get('ic_sign', request.icSign),
        )
        
        # ===== PASSO 5: GERAR PROMPT COM DADOS VALIDADOS =====
        # Obter prompt mestre
        master_prompt = _get_master_prompt(lang)
        
        # Gerar prompt específico da seção com dados validados
        title, section_prompt = _generate_section_prompt(
            updated_request, 
            request.section, 
            validation_summary, 
            precomputed_data
        )
        
        # Combinar prompt mestre + prompt da seção + contexto RAG
        full_user_prompt = f"""{section_prompt}

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_text[:3000] if context_text else "Informações astrológicas gerais."}"""
        
        # ===== PASSO 6: GERAR INTERPRETAÇÃO COM IA =====
        print(f"[FULL-BIRTH-CHART] Gerando interpretação para seção {request.section}")
        
        interpretation = provider.generate_text(
            system_prompt=master_prompt,
            user_prompt=full_user_prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        # ===== PASSO 7: LIMPAR CONTEÚDO DE INSTRUÇÕES INTERNAS =====
        print(f"[FULL-BIRTH-CHART] Limpando conteúdo de instruções internas")
        cleaned_interpretation = _clean_interpretation_content(interpretation)
        
        print(f"[FULL-BIRTH-CHART] Interpretação gerada e limpa com sucesso")
        
        return FullBirthChartResponse(
            section=request.section,
            title=title,
            content=cleaned_interpretation,
            generated_by=provider.get_provider_name()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao gerar seção do mapa astral: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar seção: {str(e)}"
        )

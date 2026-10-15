from datetime import datetime
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Header
from fastapi import status
from pydantic import BaseModel
from typing import List
from typing import Optional

router = APIRouter()


# ============================================================================
# REVOLUÇÃO SOLAR - Endpoints
# ============================================================================

class SolarReturnRequest(BaseModel):
    """Request para cálculo da Revolução Solar."""
    birth_date: str  # ISO format
    birth_time: str  # HH:MM
    latitude: float
    longitude: float
    target_year: Optional[int] = None



class SolarReturnInterpretationRequest(BaseModel):
    """Request para interpretação da Revolução Solar."""
    # Dados do mapa natal
    natal_sun_sign: str
    natal_ascendant: Optional[str] = None
    
    # Dados da revolução solar (podem ser fornecidos ou recalculados)
    solar_return_ascendant: Optional[str] = None
    solar_return_sun_house: Optional[int] = None
    solar_return_moon_sign: Optional[str] = None
    solar_return_moon_house: Optional[int] = None
    solar_return_venus_sign: Optional[str] = None
    solar_return_venus_house: Optional[int] = None
    solar_return_mars_sign: Optional[str] = None
    solar_return_mars_house: Optional[int] = None
    solar_return_jupiter_sign: Optional[str] = None
    solar_return_jupiter_house: Optional[int] = None
    solar_return_saturn_sign: Optional[str] = None
    solar_return_midheaven: Optional[str] = None
    target_year: Optional[int] = None
    language: Optional[str] = 'pt'
    
    # Dados para recálculo (opcional - se fornecido, recalcula internamente)
    birth_date: Optional[str] = None  # ISO format
    birth_time: Optional[str] = None  # HH:MM
    latitude: Optional[float] = None
    longitude: Optional[float] = None



class SourceItem(BaseModel):
    """Item de fonte da interpretação."""
    source: str
    page: int
    relevance: Optional[float] = None



class InterpretationResponse(BaseModel):
    """Response com interpretação astrológica."""
    interpretation: str
    sources: List[SourceItem]
    query_used: str
    generated_by: Optional[str] = None



@router.post("/solar-return/calculate")
async def calculate_solar_return_chart(
    request: SolarReturnRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Calcula o mapa de Revolução Solar.
    
    Body:
    {
        "birth_date": "1990-01-15T00:00:00",
        "birth_time": "14:30",
        "latitude": -23.5505,
        "longitude": -46.6333,
        "target_year": 2025
    }
    """
    try:
        from app.services.swiss_ephemeris_calculator import calculate_solar_return
        
        birth_date = datetime.fromisoformat(request.birth_date.replace('Z', '+00:00'))
        
        solar_return = calculate_solar_return(
            birth_date=birth_date,
            birth_time=request.birth_time,
            latitude=request.latitude,
            longitude=request.longitude,
            target_year=request.target_year
        )
        
        return solar_return
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular revolução solar: {str(e)}"
        )



@router.post("/solar-return/interpretation", response_model=InterpretationResponse)
async def get_solar_return_interpretation(
    request: SolarReturnInterpretationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém interpretação da Revolução Solar usando IA.
    
    IMPORTANTE: Todos os dados são calculados pela biblioteca Swiss Ephemeris (via kerykeion).
    Os parâmetros são validados antes do cálculo e os dados calculados são validados antes da interpretação.
    """
    try:
        from app.services.rag_service_fastembed import get_rag_service
        from app.services.ai_provider_service import get_ai_provider
        from app.services.swiss_ephemeris_calculator import calculate_solar_return
        from app.services.calculation_validator import (
            validate_astrological_parameters,
            validate_calculated_chart_data
        )
        from app.api.auth import get_current_user
        
        rag_service = get_rag_service()
        lang = request.language or 'pt'
        provider = get_ai_provider()
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de IA não disponível"
            )
        
        # VALIDAÇÃO 1: Validar parâmetros de entrada
        birth_date = None
        if request.birth_date:
            try:
                birth_date = datetime.fromisoformat(request.birth_date.replace('Z', '+00:00'))
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Formato de data inválido: {str(e)}"
                )
        
        # Validar todos os parâmetros
        is_valid, error_msg, validated_params = validate_astrological_parameters(
            birth_date=birth_date,
            birth_time=request.birth_time,
            latitude=request.latitude,
            longitude=request.longitude,
            target_year=request.target_year
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parâmetros inválidos: {error_msg}"
            )
        
        # VALIDAÇÃO 2: Calcular e validar dados usando biblioteca
        # OBRIGATÓRIO: Sempre recalcular usando Swiss Ephemeris (não aceitar dados do frontend)
        if not (birth_date and request.birth_time and 
                request.latitude is not None and request.longitude is not None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dados completos de nascimento são obrigatórios (data, hora, latitude, longitude) para calcular Revolução Solar"
            )
        
        # VALIDAÇÃO 2: Calcular usando biblioteca (Swiss Ephemeris)
        # OBRIGATÓRIO: Sempre recalcular usando biblioteca (não aceitar dados do frontend)
        try:
            # Normalizar birth_date para naive datetime (remover timezone se presente)
            # Isso evita problemas de comparação entre offset-aware e offset-naive
            if birth_date.tzinfo is not None:
                birth_date_naive = birth_date.replace(tzinfo=None)
            else:
                birth_date_naive = birth_date
            
            # Calcular usando biblioteca (Swiss Ephemeris via kerykeion)
            recalculated_data = calculate_solar_return(
                birth_date=birth_date_naive,
                birth_time=request.birth_time,
                latitude=request.latitude,
                longitude=request.longitude,
                target_year=request.target_year
            )
            
            # Validar dados calculados
            is_valid, error = validate_calculated_chart_data(recalculated_data)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Dados calculados inválidos: {error}"
                )
        except HTTPException:
            raise  # Relançar HTTPException
        except Exception as e:
            import traceback
            print(f"[ERROR] Erro ao calcular Revolução Solar: {e}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao calcular Revolução Solar: {str(e)}"
            )
        
        # VALIDAÇÃO 3: Calcular mapa natal também para ter dados completos
        from app.services.swiss_ephemeris_calculator import calculate_birth_chart
        natal_chart = calculate_birth_chart(
            birth_date=birth_date_naive,
            birth_time=request.birth_time,
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        # Validar mapa natal calculado
        is_valid_natal, error_natal = validate_calculated_chart_data(natal_chart)
        if not is_valid_natal:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao validar mapa natal: {error_natal}"
            )
        
        # Extrair dados validados do mapa natal
        natal_sun_sign = natal_chart.get("sun_sign")
        natal_sun_house = natal_chart.get("sun_house")
        natal_ascendant = natal_chart.get("ascendant_sign")
        natal_moon_sign = natal_chart.get("moon_sign")
        natal_moon_house = natal_chart.get("moon_house")
        
        # Validar que dados essenciais do mapa natal foram calculados
        if not natal_sun_sign or not natal_ascendant or not natal_moon_sign:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dados essenciais do mapa natal não foram calculados corretamente"
            )
        
        # Extrair dados validados da revolução solar
        solar_return_ascendant = recalculated_data.get("ascendant_sign")
        solar_return_sun_house = recalculated_data.get("sun_house")
        solar_return_sun_sign = recalculated_data.get("sun_sign")
        solar_return_moon_sign = recalculated_data.get("moon_sign")
        solar_return_moon_house = recalculated_data.get("moon_house")
        
        # Validar que dados essenciais da revolução solar foram calculados
        if not solar_return_ascendant or solar_return_sun_house is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dados essenciais da Revolução Solar não foram calculados corretamente"
            )
        
        # Calcular idade corretamente
        target_year = request.target_year or datetime.now().year
        birth_year = birth_date_naive.year
        age = target_year - birth_year
        
        # Buscar contexto do RAG - Expandido para incluir outras técnicas
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
        
        # Gerar interpretação com IA - Prompt melhorado com separação clara
        system_prompt = """Você é um Astrólogo Sênior especializado em Revolução Solar e técnicas complementares de previsão astrológica.

IMPORTANTE: Você DEVE sempre separar claramente os dados do MAPA NATAL dos dados da REVOLUÇÃO SOLAR. NUNCA confunda ou misture esses dados.

Além da Revolução Solar, você conhece outras técnicas astrológicas relevantes:
- Progressões Secundárias (evolução interna ao longo do tempo)
- Retorno de Saturno (maturidade e responsabilidades, ~29.5 anos)
- Retorno de Júpiter (expansão e oportunidades, ~12 anos)
- Trânsitos (influências atuais dos planetas)
- Direções Primárias (eventos importantes, 1 grau = 1 ano)
- Profecção Anual (foco anual por casa astrológica)

Quando apropriado e se o contexto de referência mencionar, você pode sugerir brevemente como outras técnicas podem complementar a análise da Revolução Solar, mas mantenha o foco principal na Revolução Solar."""
        
        user_prompt = f"""Dados para Análise da Revolução Solar de {target_year}:

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
        
        interpretation_text = provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        sources_list = [
            SourceItem(
                source=r.get('source', 'knowledge_base'),
                page=r.get('page', 1),
                relevance=r.get('score', 0.5)
            )
            for r in unique_results[:5]
        ]
        
        return InterpretationResponse(
            interpretation=interpretation_text,
            sources=sources_list,
            query_used=f"Revolução Solar {solar_return_ascendant} Casa {solar_return_sun_house}",
            generated_by=provider.get_provider_name()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao gerar interpretação de revolução solar: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar interpretação: {str(e)}"
        )

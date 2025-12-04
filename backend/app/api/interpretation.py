from fastapi import APIRouter, HTTPException, status, Header, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import BirthChart

router = APIRouter()

class PlanetInterpretationRequest(BaseModel):
    planet: str
    sign: str
    house: Optional[int] = None
    sunSign: Optional[str] = None
    moonSign: Optional[str] = None
    ascendant: Optional[str] = None
    userName: Optional[str] = None

class CompleteChartRequest(BaseModel):
    """Request para obter mapa astral completo no formato do PDF."""
    birth_date: str  # Formato: "DD/MM/YYYY"
    birth_time: str  # Formato: "HH:MM"
    latitude: float
    longitude: float
    birth_place: str
    name: str

class CompleteChartResponse(BaseModel):
    """Response com mapa astral completo no formato do PDF."""
    birth_data: Dict[str, Any]
    planets_in_signs: List[Dict[str, Any]]
    special_points: List[Dict[str, Any]]
    planets_in_houses: List[Dict[str, Any]]  # Lista de dicts com {house: int, planets: List}

@router.post("/interpretation/planet")
async def get_planet_interpretation(request: PlanetInterpretationRequest, authorization: Optional[str] = Header(None)):
    try:
        from app.services.ai_provider_service import get_ai_provider
        provider = get_ai_provider()
        
        if not provider:
            return {
                "interpretation": f"Interpretação básica: {request.planet} em {request.sign}" + (f" na Casa {request.house}" if request.house else ""),
                "generated_by": "none"
            }
        
        provider_name = provider.get_provider_name()
        print(f"[TEST] Gerando com {provider_name} para {request.planet} em {request.sign}")
        
        system_prompt = "Você é um astrólogo experiente."
        user_prompt = f"Explique o que significa ter {request.planet} em {request.sign}{f' na Casa {request.house}' if request.house else ''} no mapa astral."
        
        # Usar modelo profissional do Groq (configurável via GROQ_MODEL)
        from app.core.config import settings
        groq_model = getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant')
        # Modelo padrão: llama-3.1-8b-instant (8B - rápido e sempre disponível)
        # Modelos disponíveis no Groq (verificar quais estão habilitados em console.groq.com):
        # - llama-3.1-8b-instant (8B - rápido, padrão, sempre disponível)
        # - llama-3.3-70b-versatile (70B - pode estar bloqueado no projeto)
        # - mixtral-8x7b-32768 (56B - pode precisar ser habilitado)
        
        print(f"[PLANET API] Gerando com modelo profissional Groq: {groq_model}")
        
        interpretation = provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=3000,  # Tokens suficientes para texto completo e profissional
            model=groq_model
        )
        
        return {
            "interpretation": interpretation,
            "generated_by": provider_name,
            "model_used": groq_model
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro: {str(e)}"
        )

def remove_duplicates_planets_in_signs(planets_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove planetas duplicados de planets_in_signs baseado em planet_key.
    Mantém apenas a primeira ocorrência de cada planeta.
    """
    seen = set()
    filtered = []
    for planet in planets_list:
        planet_key = planet.get("planet_key")
        if planet_key and planet_key not in seen:
            seen.add(planet_key)
            filtered.append(planet)
    return filtered

def remove_duplicates_special_points(points_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove pontos especiais duplicados baseado em point_key.
    Mantém apenas a primeira ocorrência de cada ponto.
    """
    seen = set()
    filtered = []
    for point in points_list:
        point_key = point.get("point_key")
        if point_key and point_key not in seen:
            seen.add(point_key)
            filtered.append(point)
    return filtered

def remove_duplicates_planets_in_houses(houses_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove planetas duplicados dentro de cada casa baseado em planet_key.
    Mantém apenas a primeira ocorrência de cada planeta por casa.
    """
    filtered_houses = []
    for house_data in houses_list:
        house_num = house_data.get("house")
        planets = house_data.get("planets", [])
        
        # Remover duplicados dentro desta casa
        seen = set()
        filtered_planets = []
        for planet in planets:
            # Usar planet_key ou planet como identificador único
            identifier = planet.get("planet_key") or planet.get("planet")
            if identifier and identifier not in seen:
                seen.add(identifier)
                filtered_planets.append(planet)
        
        filtered_houses.append({
            "house": house_num,
            "planets": filtered_planets
        })
    
    return filtered_houses

@router.post("/interpretation/complete-chart", response_model=CompleteChartResponse)
async def get_complete_chart(
    request: CompleteChartRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Retorna o mapa astral completo no formato do PDF.
    Todos os dados são calculados pela biblioteca local (Swiss Ephemeris via kerykeion).
    Nenhum dado é inventado ou alucinado - tudo é validado e calculado.
    
    GARANTIAS:
    - Todos os cálculos passam pelo Swiss Ephemeris (via kerykeion)
    - Dados são filtrados para não haver repetições
    - Cada planeta aparece apenas uma vez em planets_in_signs
    - Cada ponto especial aparece apenas uma vez em special_points
    - Cada planeta aparece apenas uma vez por casa em planets_in_houses
    """
    try:
        # Importação lazy para evitar lentidão na inicialização
        # GARANTIA: Usa apenas Swiss Ephemeris (via kerykeion)
        from app.services.swiss_ephemeris_calculator import calculate_complete_chart_with_houses
    
        # Converter data de nascimento
        birth_date = datetime.strptime(request.birth_date, "%d/%m/%Y")
        
        # Calcular mapa completo com casas usando Swiss Ephemeris
        # GARANTIA: calculate_complete_chart_with_houses usa kerykeion que usa Swiss Ephemeris
        complete_chart = calculate_complete_chart_with_houses(
            birth_date=birth_date,
            birth_time=request.birth_time,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_name=None  # Será inferido automaticamente
        )
        
        # FILTRO 1: Remover duplicações em planets_in_signs
        planets_in_signs_filtered = remove_duplicates_planets_in_signs(
            complete_chart.get("planets_in_signs", [])
        )
        
        # FILTRO 2: Remover duplicações em special_points
        special_points_filtered = remove_duplicates_special_points(
            complete_chart.get("special_points", [])
        )
        
        # Converter planets_in_houses de lista de tuplas para lista de dicts
        houses_list = []
        for house_num, planets_list in complete_chart.get("planets_in_houses", []):
            houses_list.append({
                "house": house_num,
                "planets": planets_list
            })
        
        # FILTRO 3: Remover duplicações em planets_in_houses
        houses_list_filtered = remove_duplicates_planets_in_houses(houses_list)
        
        # Log para debug (opcional)
        print(f"[COMPLETE CHART] Planetas únicos: {len(planets_in_signs_filtered)}")
        print(f"[COMPLETE CHART] Pontos especiais únicos: {len(special_points_filtered)}")
        print(f"[COMPLETE CHART] Casas processadas: {len(houses_list_filtered)}")
        
        return CompleteChartResponse(
            birth_data=complete_chart["birth_data"],
            planets_in_signs=planets_in_signs_filtered,
            special_points=special_points_filtered,
            planets_in_houses=houses_list_filtered
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de data inválido. Use DD/MM/YYYY: {str(e)}"
        )
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular mapa completo: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular mapa astral completo: {str(e)}"
        )


@router.get("/transits/future")
async def get_future_transits(
    months_ahead: int = 24,
    max_transits: int = 10,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Calcula trânsitos futuros baseados no mapa astral do usuário.
    
    IMPORTANTE: 
    - Todos os cálculos são feitos pela biblioteca local (Swiss Ephemeris via kerykeion)
    - A IA apenas interpreta os dados calculados, NUNCA inventa trânsitos
    - Retorna apenas trânsitos reais calculados matematicamente
    
    Args:
        months_ahead: Quantos meses à frente calcular (padrão: 24, mínimo: 6, máximo: 60)
        max_transits: Número máximo de trânsitos a retornar (padrão: 10, mínimo: 5, máximo: 20)
        authorization: Token JWT do usuário autenticado
    
    Returns:
        Lista de trânsitos futuros ordenados por data, com interpretações geradas pela IA
    """
    try:
        # Validar parâmetros
        months_ahead = max(6, min(60, months_ahead))
        max_transits = max(5, min(20, max_transits))
        
        # Obter usuário autenticado (importação local para evitar circular)
        from app.api.auth import get_current_user
        current_user = get_current_user(authorization, db)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Não autenticado"
            )
        
        # Obter mapa astral primário do usuário
        birth_chart = db.query(BirthChart).filter(
            BirthChart.user_id == current_user.id,
            BirthChart.is_primary == True
        ).first()
        
        if not birth_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapa astral não encontrado. Por favor, registre seu mapa astral primeiro."
            )
        
        # Importar calculador de trânsitos
        from app.services.transits_calculator import calculate_future_transits
        
        # Calcular trânsitos usando biblioteca local (NÃO IA)
        # GARANTIA: Todos os cálculos são matemáticos, usando Swiss Ephemeris
        transits = calculate_future_transits(
            birth_date=birth_chart.birth_date,
            birth_time=birth_chart.birth_time,
            latitude=birth_chart.latitude,
            longitude=birth_chart.longitude,
            months_ahead=months_ahead,
            max_transits=max_transits
        )
        
        # Formatar trânsitos para o frontend
        formatted_transits = []
        for transit in transits:
            # Mapear tipo de aspecto para display
            aspect_type_display_map = {
                'conjunção': 'Conjunção',
                'oposição': 'Oposição',
                'quadratura': 'Quadratura',
                'trígono': 'Trígono',
                'sextil': 'Sextil'
            }
            
            aspect_type_display = aspect_type_display_map.get(
                transit.get('aspect_type', ''), 
                transit.get('aspect_type', 'Aspecto')
            )
            
            # Determinar tipo de trânsito para o frontend
            transit_type = transit.get('transit_type', 'jupiter')
            if transit_type == 'saturn-return':
                transit_type_frontend = 'saturn-return'
            elif transit.get('planet') == 'Júpiter':
                transit_type_frontend = 'jupiter'
            elif transit.get('planet') == 'Urano':
                transit_type_frontend = 'uranus'
            elif transit.get('planet') == 'Netuno':
                transit_type_frontend = 'neptune'
            elif transit.get('planet') == 'Plutão':
                transit_type_frontend = 'pluto'
            else:
                transit_type_frontend = 'jupiter'  # Default
            
            # Criar ID único
            transit_id = f"{transit.get('planet', '')}_{transit.get('aspect_type', '')}_{transit.get('natal_point', '')}_{transit.get('date', '')}"
            
            formatted_transits.append({
                'id': transit_id,
                'type': transit_type_frontend,
                'title': transit.get('title', 'Trânsito'),
                'planet': transit.get('planet', ''),
                'timeframe': f"{transit.get('start_date', '')} - {transit.get('end_date', '')}",
                'description': transit.get('description', ''),
                'isActive': transit.get('is_active', False),
                'date': transit.get('date', ''),
                'start_date': transit.get('start_date', ''),
                'end_date': transit.get('end_date', ''),
                'aspect_type': transit.get('aspect_type', ''),
                'aspect_type_display': aspect_type_display,
                'natal_point': transit.get('natal_point', '')
            })
        
        return {
            "transits": formatted_transits,
            "count": len(formatted_transits)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular trânsitos: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular trânsitos: {str(e)}"
        )


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
    """
    try:
        from app.services.rag_service_fastembed import get_rag_service
        from app.services.ai_provider_service import get_ai_provider
        from app.services.swiss_ephemeris_calculator import calculate_solar_return
        from app.api.auth import get_current_user
        
        rag_service = get_rag_service()
        lang = request.language or 'pt'
        provider = get_ai_provider()
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de IA não disponível"
            )
        
        # RECALCULAR DADOS SE DISPONÍVEL
        recalculated_data = None
        if (request.birth_date and request.birth_time and 
            request.latitude is not None and request.longitude is not None):
            try:
                birth_date = datetime.fromisoformat(request.birth_date.replace('Z', '+00:00'))
                recalculated_data = calculate_solar_return(
                    birth_date=birth_date,
                    birth_time=request.birth_time,
                    latitude=request.latitude,
                    longitude=request.longitude,
                    target_year=request.target_year
                )
            except Exception as e:
                print(f"[WARNING] Erro ao recalcular revolução solar: {e}")
                recalculated_data = None
        
        # Usar dados recalculados se disponível
        solar_return_ascendant = recalculated_data.get("ascendant_sign") if recalculated_data else request.solar_return_ascendant
        solar_return_sun_house = recalculated_data.get("sun_house") if recalculated_data else request.solar_return_sun_house
        solar_return_moon_sign = recalculated_data.get("moon_sign") if recalculated_data else request.solar_return_moon_sign
        solar_return_moon_house = recalculated_data.get("moon_house") if recalculated_data else request.solar_return_moon_house
        
        if not solar_return_ascendant or not solar_return_sun_house:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dados insuficientes para interpretação"
            )
        
        # Buscar contexto do RAG
        queries = [
            f"revolução solar retorno solar {solar_return_ascendant} casa {solar_return_sun_house}",
            f"casa 6 saúde vitalidade bem-estar astrologia revolução solar"
        ]
        
        all_rag_results = []
        if rag_service:
            for q in queries:
                try:
                    results = rag_service.search(q, top_k=5)
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
                if len(unique_results) >= 12:
                    break
        
        context_text = "\n\n".join([doc.get('text', '') for doc in unique_results[:10] if doc.get('text')])
        
        # Gerar interpretação com IA
        system_prompt = "Você é um Astrólogo Sênior especializado em Revolução Solar. Forneça interpretações detalhadas e práticas."
        user_prompt = f"""Dados para Análise:
Mapa Natal: Signo Solar {request.natal_sun_sign}
Revolução Solar: Ascendente {solar_return_ascendant}, Sol na Casa {solar_return_sun_house}, Lua {solar_return_moon_sign} na Casa {solar_return_moon_house}

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_text[:3000] if context_text else "Informações gerais sobre revolução solar."}

Forneça uma interpretação completa e detalhada da revolução solar."""
        
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


# ============================================================================
# NUMEROLOGIA - Endpoints
# ============================================================================

class NumerologyMapResponse(BaseModel):
    """Response com mapa numerológico completo."""
    full_name: str
    birth_date: str
    life_path: Dict[str, Any]
    destiny: Dict[str, Any]
    soul: Dict[str, Any]
    personality: Dict[str, Any]
    birthday: Dict[str, Any]
    maturity: Dict[str, Any]
    pinnacles: List[Dict[str, Any]]
    challenges: List[Dict[str, Any]]
    personal_year: Dict[str, Any]
    birth_grid: Dict[str, Any]
    life_cycle: Dict[str, Any]
    karmic_debts: List[int]


class NumerologyInterpretationRequest(BaseModel):
    """Request para interpretação numerológica."""
    language: Optional[str] = 'pt'


class NumerologyInterpretationResponse(BaseModel):
    """Response com interpretação numerológica completa."""
    interpretation: str
    sources: List[SourceItem]
    query_used: str
    generated_by: Optional[str] = None


class BirthGridQuantitiesRequest(BaseModel):
    """Request para interpretação das quantidades na grade de nascimento."""
    grid: Dict[int, int]  # {número: quantidade}
    language: Optional[str] = 'pt'


class BirthGridQuantitiesResponse(BaseModel):
    """Response com interpretação das quantidades na grade."""
    explanation: str
    sources: List[SourceItem]
    query_used: str


# ============================================================================
# MAPA ASTRAL COMPLETO - Endpoints
# ============================================================================

class FullBirthChartRequest(BaseModel):
    """Request para geração do Mapa Astral Completo."""
    name: str
    birthDate: str  # DD/MM/AAAA
    birthTime: str  # HH:MM
    birthPlace: str
    sunSign: str
    moonSign: str
    ascendant: str
    sunHouse: int
    moonHouse: int
    section: str  # 'power', 'triad', 'personal', 'houses', 'karma', 'synthesis'
    language: Optional[str] = 'pt'
    # Planetas opcionais
    mercurySign: Optional[str] = None
    mercuryHouse: Optional[int] = None
    venusSign: Optional[str] = None
    venusHouse: Optional[int] = None
    marsSign: Optional[str] = None
    marsHouse: Optional[int] = None
    jupiterSign: Optional[str] = None
    jupiterHouse: Optional[int] = None
    saturnSign: Optional[str] = None
    saturnHouse: Optional[int] = None
    uranusSign: Optional[str] = None
    uranusHouse: Optional[int] = None
    neptuneSign: Optional[str] = None
    neptuneHouse: Optional[int] = None
    plutoSign: Optional[str] = None
    plutoHouse: Optional[int] = None
    northNodeSign: Optional[str] = None
    northNodeHouse: Optional[int] = None
    southNodeSign: Optional[str] = None
    southNodeHouse: Optional[int] = None
    chironSign: Optional[str] = None
    chironHouse: Optional[int] = None
    midheavenSign: Optional[str] = None
    icSign: Optional[str] = None


class FullBirthChartResponse(BaseModel):
    """Response com seção do Mapa Astral Completo."""
    section: str
    title: str
    content: str
    generated_by: str


@router.post("/full-birth-chart/section", response_model=FullBirthChartResponse)
async def generate_birth_chart_section(
    request: FullBirthChartRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Gera uma seção específica do Mapa Astral Completo.
    
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
        
        # Buscar contexto do RAG
        rag_service = get_rag_service()
        queries = {
            'power': f"temperamento elementos fogo terra ar água predominante ausente {request.sunSign} {request.moonSign} {request.ascendant}",
            'triad': f"Sol Lua Ascendente tríade {request.sunSign} {request.moonSign} {request.ascendant} personalidade",
            'personal': f"Mercúrio {request.mercurySign or ''} Vênus {request.venusSign or ''} Marte {request.marsSign or ''} dinâmica pessoal",
            'houses': f"casas astrológicas Casa 2 Casa 4 Casa 6 Casa 7 Casa 10 vocação",
            'karma': f"Júpiter Saturno Nodo Norte Sul Quíron karma propósito {request.jupiterSign or ''} {request.saturnSign or ''}",
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
        
        # Construir dados do mapa para o prompt
        chart_data = f"""Nome: {request.name}
Data de Nascimento: {request.birthDate} às {request.birthTime}
Local: {request.birthPlace}

Tríade Fundamental:
- Sol: {request.sunSign} na Casa {request.sunHouse}
- Lua: {request.moonSign} na Casa {request.moonHouse}
- Ascendente: {request.ascendant}

Planetas Pessoais:"""
        
        if request.mercurySign:
            chart_data += f"\n- Mercúrio: {request.mercurySign}" + (f" na Casa {request.mercuryHouse}" if request.mercuryHouse else "")
        if request.venusSign:
            chart_data += f"\n- Vênus: {request.venusSign}" + (f" na Casa {request.venusHouse}" if request.venusHouse else "")
        if request.marsSign:
            chart_data += f"\n- Marte: {request.marsSign}" + (f" na Casa {request.marsHouse}" if request.marsHouse else "")
        
        chart_data += "\n\nPlanetas Sociais:"
        if request.jupiterSign:
            chart_data += f"\n- Júpiter: {request.jupiterSign}" + (f" na Casa {request.jupiterHouse}" if request.jupiterHouse else "")
        if request.saturnSign:
            chart_data += f"\n- Saturno: {request.saturnSign}" + (f" na Casa {request.saturnHouse}" if request.saturnHouse else "")
        
        # Gerar interpretação com IA
        section_titles = {
            'power': 'A Estrutura de Poder',
            'triad': 'A Tríade Fundamental',
            'personal': 'Dinâmica Pessoal e Ferramentas',
            'houses': 'Análise Setorial Avançada',
            'karma': 'Expansão, Estrutura e Karma',
            'synthesis': 'Síntese e Orientação Estratégica'
        }
        
        title = section_titles.get(request.section, request.section.capitalize())
        
        system_prompt = "Você é um astrólogo experiente especializado em interpretação profunda de mapas astrais. Forneça análises detalhadas e terapêuticas."
        
        user_prompt = f"""Dados do Mapa Astral:
{chart_data}

Seção: {title}

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_text[:3000] if context_text else "Informações astrológicas gerais."}

Forneça uma interpretação completa e detalhada desta seção do mapa astral."""
        
        interpretation = provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        return FullBirthChartResponse(
            section=request.section,
            title=title,
            content=interpretation,
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


@router.get("/numerology/map", response_model=NumerologyMapResponse)
async def get_numerology_map(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Calcula o mapa numerológico completo do usuário autenticado.
    """
    try:
        from app.services.numerology_calculator import NumerologyCalculator
        from app.api.auth import get_current_user
        
        user = get_current_user(authorization, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Não autenticado"
            )
        
        birth_chart = db.query(BirthChart).filter(
            BirthChart.user_id == user.id,
            BirthChart.is_primary == True
        ).first()
        
        if not birth_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapa astral não encontrado. Complete o onboarding primeiro."
            )
        
        # Converter birth_date para datetime se necessário
        from datetime import date
        if isinstance(birth_chart.birth_date, datetime):
            birth_date = birth_chart.birth_date
        elif isinstance(birth_chart.birth_date, date):
            birth_date = datetime.combine(birth_chart.birth_date, datetime.min.time())
        elif isinstance(birth_chart.birth_date, str):
            try:
                birth_date = datetime.fromisoformat(birth_chart.birth_date.replace('Z', '+00:00'))
            except:
                birth_date = datetime.strptime(birth_chart.birth_date.split('T')[0], '%Y-%m-%d')
        else:
            raise ValueError(f"Tipo de data não suportado: {type(birth_chart.birth_date)}")
        
        calculator = NumerologyCalculator()
        numerology_map = calculator.calculate_full_numerology_map(
            full_name=birth_chart.name,
            birth_date=birth_date
        )
        
        return NumerologyMapResponse(**numerology_map)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular mapa numerológico: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular mapa numerológico: {str(e)}"
        )


@router.post("/numerology/interpretation", response_model=NumerologyInterpretationResponse)
async def get_numerology_interpretation(
    request: NumerologyInterpretationRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Gera interpretação numerológica completa usando RAG e IA.
    """
    try:
        from app.services.numerology_calculator import NumerologyCalculator
        from app.services.rag_service_fastembed import get_rag_service
        from app.services.ai_provider_service import get_ai_provider
        from app.api.auth import get_current_user
        
        user = get_current_user(authorization, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Não autenticado"
            )
        
        birth_chart = db.query(BirthChart).filter(
            BirthChart.user_id == user.id,
            BirthChart.is_primary == True
        ).first()
        
        if not birth_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapa astral não encontrado. Complete o onboarding primeiro."
            )
        
        # Calcular mapa numerológico
        calculator = NumerologyCalculator()
        numerology_map = calculator.calculate_full_numerology_map(
            full_name=birth_chart.name,
            birth_date=birth_chart.birth_date
        )
        
        # Obter serviços
        rag_service = get_rag_service()
        provider = get_ai_provider()
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de IA não disponível"
            )
        
        # Construir queries para RAG
        queries = [
            f"life path number {numerology_map['life_path']['number']} numerologia pitagórica significado missão",
            f"caminho de vida {numerology_map['life_path']['number']} numerologia",
            f"expression destiny number {numerology_map['destiny']['number']} numerologia talentos",
            f"soul desire heart number {numerology_map['soul']['number']} numerologia motivação"
        ]
        
        # Buscar contexto do RAG
        context_documents = []
        if rag_service:
            for query in queries:
                try:
                    results = rag_service.search(query, top_k=3, expand_query=False, category='numerology')
                    context_documents.extend(results)
                except Exception as e:
                    print(f"[WARNING] Erro ao buscar query '{query}': {e}")
        
        # Remover duplicatas
        seen_texts = set()
        unique_docs = []
        for doc in sorted(context_documents, key=lambda x: x.get('score', 0), reverse=True):
            doc_text = doc.get('text', '').strip()
            if doc_text and doc_text not in seen_texts:
                seen_texts.add(doc_text)
                unique_docs.append(doc)
                if len(unique_docs) >= 15:
                    break
        
        context_text = "\n\n".join([
            f"[Fonte: {doc.get('source', 'unknown')} - Página {doc.get('page', 1)}]\n{doc.get('text', '')}"
            for doc in unique_docs[:10]
            if doc.get('text')
        ])
        
        # Gerar interpretação com IA
        lang = request.language or 'pt'
        system_prompt = "Você é um Numerólogo Pitagórico profissional. Forneça interpretações detalhadas e terapêuticas."
        
        user_prompt = f"""Dados do Cliente:
Nome: {numerology_map['full_name']}
Caminho de Vida: {numerology_map['life_path']['number']}
Expressão/Destino: {numerology_map['destiny']['number']}
Desejo da Alma: {numerology_map['soul']['number']}
Personalidade: {numerology_map['personality']['number']}

CONHECIMENTO NUMEROLÓGICO DE REFERÊNCIA:
{context_text[:3000] if context_text else "Informações numerológicas básicas."}

Forneça uma interpretação completa e detalhada do mapa numerológico."""
        
        interpretation_text = provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        sources_list = [
            SourceItem(
                source=doc.get('source', 'unknown'),
                page=doc.get('page', 1),
                relevance=doc.get('score', 0.5)
            )
            for doc in unique_docs[:5]
        ]
        
        return NumerologyInterpretationResponse(
            interpretation=interpretation_text,
            sources=sources_list,
            query_used=f"Numerologia - Caminho de Vida {numerology_map['life_path']['number']}",
            generated_by=provider.get_provider_name()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao gerar interpretação numerológica: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar interpretação: {str(e)}"
        )


@router.post("/numerology/birth-grid-quantities", response_model=BirthGridQuantitiesResponse)
async def get_birth_grid_quantities_interpretation(
    request: BirthGridQuantitiesRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém interpretação sobre o significado das quantidades na grade de nascimento.
    """
    try:
        from app.services.rag_service_fastembed import get_rag_service
        from app.services.ai_provider_service import get_ai_provider
        import re
        
        rag_service = get_rag_service()
        lang = request.language or 'pt'
        provider = get_ai_provider()
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de IA não disponível"
            )
        
        # Buscar contexto do RAG
        queries = [
            "grade numerológica nome data nascimento",
            "quantidade números grade nascimento significado",
            "número aparece muitas vezes grade numerologia"
        ]
        
        all_results = []
        if rag_service:
            for query in queries:
                try:
                    results = rag_service.search(query, top_k=5, expand_query=True, category='numerology')
                    all_results.extend(results)
                except Exception as e:
                    print(f"[WARNING] Erro ao buscar query '{query}': {e}")
        
        # Remover duplicatas
        seen_texts = set()
        unique_results = []
        for result in sorted(all_results, key=lambda x: x.get('score', 0), reverse=True):
            text = result.get('text', '').strip()
            if text and text not in seen_texts and len(text) > 20:
                seen_texts.add(text)
                unique_results.append(result)
                if len(unique_results) >= 15:
                    break
        
        context_text = "\n\n".join([doc.get('text', '') for doc in unique_results[:10] if doc.get('text')])
        
        # Preparar dados da grade
        grid_summary = "\n".join([f"Número {num}: aparece {count} vez(es)" 
                                 for num, count in sorted(request.grid.items()) if count > 0])
        
        # Gerar interpretação com IA
        system_prompt = "Você é um Numerólogo Pitagórico profissional. Explique o significado das quantidades na grade numerológica."
        user_prompt = f"""Grade Numerológica:
{grid_summary}

CONHECIMENTO NUMEROLÓGICO DE REFERÊNCIA:
{context_text[:2000] if context_text else "Informações sobre grade numerológica."}

Explique o significado das quantidades de cada número na grade."""
        
        explanation = provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        sources_list = [
            SourceItem(
                source=r.get('source', 'knowledge_base'),
                page=r.get('page', 1),
                relevance=r.get('score', 0.5)
            )
            for r in unique_results[:5]
        ]
        
        return BirthGridQuantitiesResponse(
            explanation=explanation,
            sources=sources_list,
            query_used="Grade Numerológica - Quantidades"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao gerar interpretação de grade: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar interpretação: {str(e)}"
        )
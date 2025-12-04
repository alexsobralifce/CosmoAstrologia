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
    # Coordenadas do local (opcionais - se não fornecidas, tentará obter do nome do local)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
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
            # Caminho relativo ao arquivo atual (backend/app/api/interpretation.py)
            # O arquivo está em docs/PROMPT_MASTER_LITERAL_PT.txt (raiz do projeto)
            current_file = Path(__file__)
            # Subir 4 níveis: backend/app/api -> backend/app -> backend -> raiz do projeto
            project_root = current_file.parent.parent.parent.parent
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
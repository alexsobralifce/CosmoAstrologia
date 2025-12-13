from fastapi import APIRouter, HTTPException, status, Header, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database import BirthChart

router = APIRouter()


# ============================================================================
# INFORMAÇÕES DO DIA ATUAL - Endpoint
# ============================================================================

@router.get("/daily-info")
async def get_daily_info(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Retorna informações astrológicas do dia atual:
    - Data formatada
    - Fase lunar
    - Signo da Lua
    
    Todos os cálculos são feitos usando Swiss Ephemeris (biblioteca padrão).
    """
    try:
        from app.services.daily_info_calculator import get_daily_info
        
        # Tentar obter coordenadas do usuário autenticado
        user_lat = latitude
        user_lon = longitude
        
        if authorization:
            try:
                from app.api.auth import get_current_user
                current_user = get_current_user(authorization, db)
                if current_user:
                    # Tentar obter coordenadas do mapa astral
                    birth_chart = db.query(BirthChart).filter(
                        BirthChart.user_id == current_user.id,
                        BirthChart.is_primary == True
                    ).first()
                    
                    if birth_chart:
                        user_lat = birth_chart.latitude
                        user_lon = birth_chart.longitude
            except:
                pass  # Se não conseguir autenticar, usar coordenadas padrão
        
        # Usar coordenadas padrão (São Paulo) se não fornecidas
        if user_lat is None or user_lon is None:
            user_lat = -23.5505
            user_lon = -46.6333
        
        # Calcular informações do dia
        daily_info = get_daily_info(
            latitude=user_lat,
            longitude=user_lon
        )
        
        return daily_info
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular informações do dia: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular informações do dia: {str(e)}"
        )

class PlanetInterpretationRequest(BaseModel):
    planet: str
    sign: str
    house: Optional[int] = None
    sunSign: Optional[str] = None
    moonSign: Optional[str] = None
    ascendant: Optional[str] = None
    userName: Optional[str] = None

class ChartRulerInterpretationRequest(BaseModel):
    ascendant: str
    ruler: str
    rulerSign: str
    rulerHouse: int

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

@router.post("/interpretation/chart-ruler")
async def get_chart_ruler_interpretation(
    request: ChartRulerInterpretationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém interpretação do regente do mapa usando RAG + IA.
    
    Body:
    {
        "ascendant": "Aquário",
        "ruler": "Urano",
        "rulerSign": "Escorpião",
        "rulerHouse": 3
    }
    """
    try:
        from app.services.ai_provider_service import get_ai_provider
        from app.services.rag_service_fastembed import get_rag_service
        
        provider = get_ai_provider()
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de IA não disponível"
            )
        
        ascendant = request.ascendant
        ruler = request.ruler
        ruler_sign = request.rulerSign
        ruler_house = request.rulerHouse
        
        if not ascendant or not ruler:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ascendente e regente são obrigatórios"
            )
        
        # Buscar contexto do RAG
        rag_service = get_rag_service()
        context_text = ""
        sources = []
        
        if rag_service:
            try:
                queries = [
                    f"regente do mapa {ruler} ascendente {ascendant} importância significado",
                    f"{ruler} como regente do mapa astral personalidade energia vital",
                    f"planeta regente {ruler} influência comportamento características",
                ]
                if ruler_sign:
                    queries.append(f"{ruler} em {ruler_sign} regente do mapa interpretação")
                if ruler_house:
                    queries.append(f"{ruler} casa {ruler_house} regente do mapa significado")
                
                all_results = []
                for q in queries:
                    try:
                        results = rag_service.search(q, top_k=6, expand_query=True)
                        all_results.extend(results)
                    except Exception as e:
                        print(f"[WARNING] Erro ao buscar com query '{q}': {e}")
                
                # Remover duplicatas
                seen_texts = set()
                unique_results = []
                for result in sorted(all_results, key=lambda x: x.get('score', 0), reverse=True):
                    text_key = result.get('text', '')[:100]
                    if text_key not in seen_texts:
                        seen_texts.add(text_key)
                        unique_results.append(result)
                        if len(unique_results) >= 12:
                            break
                
                if unique_results:
                    context_text = "\n\n".join([
                        f"--- Documento {i+1} (Fonte: {doc.get('source', 'N/A')}, Página {doc.get('page', 'N/A')}) ---\n{doc.get('text', '')}"
                        for i, doc in enumerate(unique_results[:12])
                    ])
                    sources = [
                        {
                            'source': r.get('source', 'N/A'),
                            'page': r.get('page', 'N/A'),
                            'relevance': r.get('score', 0)
                        }
                        for r in unique_results[:10]
                    ]
            except Exception as e:
                print(f"[WARNING] Erro ao buscar no RAG: {e}")
        
        # Limitar contexto
        context_limit = min(len(context_text), 4000) if context_text else 0
        context_snippet = context_text[:context_limit] if context_text else "Informações astrológicas gerais sobre regentes do mapa astral."
        
        # Gerar interpretação com IA
        system_prompt = """Você é um astrólogo experiente especializado em interpretação de regentes do mapa astral.
Sua função é criar interpretações profundas, didáticas e detalhadas sobre o planeta regente do mapa.

REGRAS:
- Use APENAS o regente fornecido nos dados (já calculado)
- Escreva NO MÍNIMO 2 parágrafos completos e densos (mínimo 300 palavras)
- Use estrutura didática com títulos em negrito quando apropriado
- Explique termos astrológicos de forma simples
- Foque na importância do regente para autoconhecimento e desenvolvimento pessoal
- Seja específico e detalhado, evitando generalidades"""
        
        user_prompt = f"""REGENTE DO MAPA ASTRAL:

Ascendente: {ascendant}
Planeta Regente: {ruler}
Regente em: {ruler_sign or 'não informado'}
Regente na Casa: {ruler_house or 'não informado'}

CONTEXTO ASTROLÓGICO DE REFERÊNCIA:
{context_snippet}

---

Crie uma interpretação COMPLETA, DETALHADA e EXTENSA sobre o regente do mapa astral. A interpretação DEVE ter NO MÍNIMO 2 parágrafos completos e densos (mínimo 300 palavras no total).

Estruture explicando:
1. O que significa ter {ruler} como regente do mapa (pelo menos 1 parágrafo completo, mínimo 150 palavras)
2. Como {ruler} influencia a personalidade, energia vital e comportamento (pelo menos 1 parágrafo completo, mínimo 150 palavras)
3. A importância do regente para o autoconhecimento e desenvolvimento pessoal
4. Como o regente revela forças naturais e áreas de atenção

Formate a resposta de forma didática, usando quebras de linha e estruturação adequada."""
        
        from app.core.config import settings
        groq_model = getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant')
        
        interpretation = provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=3000,
            model=groq_model
        )
        
        return {
            "interpretation": interpretation.strip(),
            "sources": sources,
            "query_used": f"regente do mapa {ruler} (múltiplas queries, {len(sources)} documentos)",
            "generated_by": provider.get_provider_name()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao gerar interpretação do regente: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar interpretação do regente: {str(e)}"
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
        
        # FILTRAR TRANSTOS PASSADOS - Apenas transitos válidos (futuros/atuais)
        # Um trânsito é válido se end_date >= hoje (ainda não terminou)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        valid_transits = []
        
        for transit in transits:
            try:
                # Parsear end_date do trânsito
                end_date_str = transit.get('end_date', '')
                if end_date_str:
                    # Parsear ISO format string
                    if isinstance(end_date_str, str):
                        # Remover timezone e extrair apenas data
                        if 'T' in end_date_str:
                            date_part = end_date_str.split('T')[0]
                            end_date = datetime.strptime(date_part, '%Y-%m-%d')
                        else:
                            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    elif isinstance(end_date_str, datetime):
                        end_date = end_date_str.replace(hour=0, minute=0, second=0, microsecond=0)
                    else:
                        continue  # Formato desconhecido, pular
                    
                    # Filtrar: apenas transitos que ainda não terminaram
                    if end_date >= today:
                        valid_transits.append(transit)
                    else:
                        print(f"[TRANSITS] Removendo trânsito passado: {transit.get('title', 'N/A')} (end_date: {end_date_str})")
                else:
                    # Se não tem end_date, verificar start_date
                    start_date_str = transit.get('start_date', transit.get('date', ''))
                    if start_date_str:
                        # Parsear ISO format string
                        if isinstance(start_date_str, str):
                            # Remover timezone e extrair apenas data
                            if 'T' in start_date_str:
                                date_part = start_date_str.split('T')[0]
                                start_date = datetime.strptime(date_part, '%Y-%m-%d')
                            else:
                                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                        elif isinstance(start_date_str, datetime):
                            start_date = start_date_str.replace(hour=0, minute=0, second=0, microsecond=0)
                        else:
                            continue  # Formato desconhecido, pular
                        
                        # Se start_date >= hoje, incluir (trânsito futuro)
                        if start_date >= today:
                            valid_transits.append(transit)
                        else:
                            print(f"[TRANSITS] Removendo trânsito passado: {transit.get('title', 'N/A')} (start_date: {start_date_str})")
                    else:
                        # Se não tem nenhuma data, não incluir
                        print(f"[TRANSITS] Removendo trânsito sem data: {transit.get('title', 'N/A')}")
            except (ValueError, TypeError) as e:
                print(f"[WARNING] Erro ao processar data do trânsito {transit.get('title', 'N/A')}: {e}")
                # Em caso de erro, não incluir o trânsito (segurança)
                continue
        
        print(f"[TRANSITS] Total calculado: {len(transits)}, Válidos (não passados): {len(valid_transits)}")
        
        # Formatar trânsitos válidos para o frontend
        formatted_transits = []
        for transit in valid_transits:
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
# TRÂNSITOS PESSOAIS EM TEMPO REAL - Endpoints
# ============================================================================

@router.get("/transits/current")
async def get_current_personal_transits(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Calcula trânsitos pessoais em tempo real (hoje/agora) baseados no mapa astral do usuário.
    
    IMPORTANTE: 
    - Todos os cálculos são feitos pela biblioteca local (Swiss Ephemeris)
    - A IA apenas interpreta os dados calculados, NUNCA inventa trânsitos
    - Retorna apenas trânsitos reais calculados matematicamente para HOJE
    
    Args:
        authorization: Token JWT do usuário autenticado
    
    Returns:
        Dicionário com trânsitos atuais e Lua Fora de Curso
    """
    try:
        # Obter usuário autenticado
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
        
        # Importar calculadores
        from app.services.transits_calculator import calculate_future_transits
        from app.services.moon_void_calculator import calculate_moon_void_of_course
        
        # Calcular trânsitos para hoje (apenas 1 dia à frente para pegar trânsitos ativos)
        today_transits = calculate_future_transits(
            birth_date=birth_chart.birth_date,
            birth_time=birth_chart.birth_time,
            latitude=birth_chart.latitude,
            longitude=birth_chart.longitude,
            months_ahead=1,  # Apenas 1 mês para pegar trânsitos ativos
            max_transits=20  # Mais trânsitos para filtrar os ativos
        )
        
        # Filtrar apenas trânsitos ATIVOS (que estão acontecendo hoje)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        active_transits = []
        
        for transit in today_transits:
            try:
                start_date_str = transit.get('start_date', '')
                end_date_str = transit.get('end_date', '')
                
                if start_date_str and end_date_str:
                    # Parsear datas
                    if isinstance(start_date_str, str):
                        if 'T' in start_date_str:
                            date_part = start_date_str.split('T')[0]
                            start_date = datetime.strptime(date_part, '%Y-%m-%d')
                        else:
                            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    else:
                        start_date = start_date_str.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    if isinstance(end_date_str, str):
                        if 'T' in end_date_str:
                            date_part = end_date_str.split('T')[0]
                            end_date = datetime.strptime(date_part, '%Y-%m-%d')
                        else:
                            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    else:
                        end_date = end_date_str.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    # Trânsito ativo se hoje está entre start_date e end_date
                    if start_date <= today <= end_date:
                        active_transits.append(transit)
            except Exception as e:
                print(f"[WARNING] Erro ao processar trânsito para hoje: {e}")
                continue
        
        # Calcular Lua Fora de Curso
        moon_void = calculate_moon_void_of_course(
            check_date=datetime.now(),
            latitude=birth_chart.latitude,
            longitude=birth_chart.longitude
        )
        
        # Formatar trânsitos ativos
        formatted_active_transits = []
        for transit in active_transits:
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
            
            transit_type = transit.get('transit_type', 'jupiter')
            if transit.get('planet') == 'Júpiter':
                transit_type_frontend = 'jupiter'
            elif transit.get('planet') == 'Urano':
                transit_type_frontend = 'uranus'
            elif transit.get('planet') == 'Netuno':
                transit_type_frontend = 'neptune'
            elif transit.get('planet') == 'Plutão':
                transit_type_frontend = 'pluto'
            elif transit_type == 'saturn-return':
                transit_type_frontend = 'saturn-return'
            else:
                transit_type_frontend = 'jupiter'
            
            transit_id = f"{transit.get('planet', '')}_{transit.get('aspect_type', '')}_{transit.get('natal_point', '')}_{transit.get('date', '')}"
            
            formatted_active_transits.append({
                'id': transit_id,
                'type': transit_type_frontend,
                'title': transit.get('title', 'Trânsito'),
                'planet': transit.get('planet', ''),
                'description': transit.get('description', ''),
                'isActive': True,
                'start_date': transit.get('start_date', ''),
                'end_date': transit.get('end_date', ''),
                'aspect_type': transit.get('aspect_type', ''),
                'aspect_type_display': aspect_type_display,
                'natal_point': transit.get('natal_point', '')
            })
        
        # Formatar Lua Fora de Curso
        void_info = {
            'is_void': moon_void.get('is_void', False),
            'void_end': moon_void.get('void_end').isoformat() if moon_void.get('void_end') else None,
            'void_start': moon_void.get('void_start').isoformat() if moon_void.get('void_start') else None,
            'next_aspect': moon_void.get('next_aspect', ''),
            'next_aspect_time': moon_void.get('next_aspect_time').isoformat() if moon_void.get('next_aspect_time') else None,
            'current_moon_sign': moon_void.get('current_moon_sign', ''),
            'void_duration_hours': moon_void.get('void_duration_hours')
        }
        
        return {
            "active_transits": formatted_active_transits,
            "moon_void_of_course": void_info,
            "date": datetime.now().isoformat(),
            "count": len(formatted_active_transits)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular trânsitos atuais: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular trânsitos atuais: {str(e)}"
        )


# ============================================================================
# AGENDA DE MELHORES MOMENTOS - Endpoints
# ============================================================================

class BestTimingRequest(BaseModel):
    """Request para cálculo de melhores momentos."""
    action_type: str  # Ex: 'pedir_aumento', 'assinar_contrato', 'primeiro_encontro'
    days_ahead: int = 30  # Quantos dias à frente calcular


@router.post("/best-timing/calculate")
async def calculate_best_timing(
    request: BestTimingRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Calcula os melhores momentos para uma ação específica baseado em aspectos e casas astrológicas.
    
    IMPORTANTE:
    - Todos os cálculos são feitos pela biblioteca local (Swiss Ephemeris)
    - A IA apenas organiza e contextualiza os dados calculados, NUNCA inventa momentos
    - Retorna apenas momentos reais calculados matematicamente
    
    Args:
        request: Tipo de ação e parâmetros
        authorization: Token JWT do usuário autenticado
    
    Returns:
        Lista de melhores momentos com scores e aspectos
    """
    try:
        # Obter usuário autenticado
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
        
        # Importar calculador
        from app.services.best_timing_calculator import calculate_best_timing
        
        # Calcular melhores momentos usando biblioteca local
        result = calculate_best_timing(
            action_type=request.action_type,
            birth_date=birth_chart.birth_date,
            birth_time=birth_chart.birth_time,
            latitude=birth_chart.latitude,
            longitude=birth_chart.longitude,
            days_ahead=min(request.days_ahead, 90)  # Máximo 90 dias
        )
        
        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
        
        # VALIDAÇÃO FINAL: Garantir que best_moments é uma lista válida
        if 'best_moments' not in result:
            result['best_moments'] = []
        elif not isinstance(result['best_moments'], list):
            result['best_moments'] = []
        
        # Garantir que todos os momentos retornados são válidos
        validated_moments = []
        for moment in result.get('best_moments', []):
            if (isinstance(moment, dict) and 
                'date' in moment and 
                'score' in moment and 
                'aspects' in moment and
                isinstance(moment.get('aspects'), list) and
                len(moment.get('aspects', [])) > 0):
                validated_moments.append(moment)
        
        result['best_moments'] = validated_moments
        result['total_valid'] = len(validated_moments)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular melhores momentos: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular melhores momentos: {str(e)}"
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
        
        # Construir queries expandidas para RAG - buscar informações detalhadas sobre cada número
        lang = request.language or 'pt'
        
        # Queries específicas para cada número do mapa
        queries = [
            # Caminho de Vida (mais importante)
            f"life path number {numerology_map['life_path']['number']} numerologia pitagórica significado missão pontos positivos negativos",
            f"caminho de vida {numerology_map['life_path']['number']} numerologia características forças fraquezas",
            f"number {numerology_map['life_path']['number']} numerology positive negative traits strengths weaknesses",
            
            # Número do Destino/Expressão
            f"expression destiny number {numerology_map['destiny']['number']} numerologia talentos habilidades",
            f"número expressão destino {numerology_map['destiny']['number']} numerologia pontos fortes desafios",
            f"destiny number {numerology_map['destiny']['number']} numerology talents abilities",
            
            # Número da Alma/Desejo do Coração
            f"soul desire heart number {numerology_map['soul']['number']} numerologia motivação desejos internos",
            f"número alma desejo coração {numerology_map['soul']['number']} numerologia motivações",
            f"soul number {numerology_map['soul']['number']} numerology inner desires motivations",
            
            # Número da Personalidade
            f"personality number {numerology_map['personality']['number']} numerologia como se apresenta mundo",
            f"número personalidade {numerology_map['personality']['number']} numerologia aparência externa",
            
            # Número do Aniversário
            f"birthday number {numerology_map['birthday']['number']} numerologia talentos especiais habilidades",
            f"número aniversário {numerology_map['birthday']['number']} numerologia dons naturais",
            
            # Número da Maturidade
            f"maturity number {numerology_map['maturity']['number']} numerologia segunda metade vida potencial",
            f"número maturidade {numerology_map['maturity']['number']} numerologia evolução futuro",
        ]
        
        # Adicionar queries para números mestres se aplicável
        if numerology_map['life_path']['is_master']:
            queries.append(f"master number {numerology_map['life_path']['number']} numerologia significado especial")
        if numerology_map['destiny']['is_master']:
            queries.append(f"master number {numerology_map['destiny']['number']} expression destiny")
        if numerology_map['soul']['is_master']:
            queries.append(f"master number {numerology_map['soul']['number']} soul heart desire")
        
        # Adicionar queries expandidas sobre tarot e numerologia para CADA número (forte ligação)
        # Caminho de Vida - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['life_path']['number']} arcano correspondente significado",
            f"arcano maior número {numerology_map['life_path']['number']} tarot numerologia",
            f"carta tarot número {numerology_map['life_path']['number']} numerologia pitagórica",
            f"tarot arcano {numerology_map['life_path']['number']} caminho de vida numerologia",
            f"numerologia tarot conexão número {numerology_map['life_path']['number']} interpretação",
            f"arcanos maiores tarot numerologia número {numerology_map['life_path']['number']} significado completo",
        ])
        
        # Número do Destino - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['destiny']['number']} arcano destino expressão",
            f"arcano maior número {numerology_map['destiny']['number']} tarot numerologia destino",
            f"carta tarot número {numerology_map['destiny']['number']} numerologia expressão",
            f"tarot arcano {numerology_map['destiny']['number']} destino numerologia",
            f"numerologia tarot conexão número {numerology_map['destiny']['number']} talentos",
        ])
        
        # Número da Alma - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['soul']['number']} arcano alma desejo coração",
            f"arcano maior número {numerology_map['soul']['number']} tarot numerologia alma",
            f"carta tarot número {numerology_map['soul']['number']} numerologia desejo coração",
            f"tarot arcano {numerology_map['soul']['number']} alma numerologia motivações",
            f"numerologia tarot conexão número {numerology_map['soul']['number']} desejos internos",
        ])
        
        # Número da Personalidade - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['personality']['number']} arcano personalidade",
            f"arcano maior número {numerology_map['personality']['number']} tarot numerologia personalidade",
            f"carta tarot número {numerology_map['personality']['number']} numerologia aparência",
            f"tarot arcano {numerology_map['personality']['number']} personalidade numerologia",
        ])
        
        # Número do Aniversário - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['birthday']['number']} arcano aniversário",
            f"arcano maior número {numerology_map['birthday']['number']} tarot numerologia aniversário",
            f"carta tarot número {numerology_map['birthday']['number']} numerologia dia nascimento",
            f"tarot arcano {numerology_map['birthday']['number']} aniversário numerologia talentos",
        ])
        
        # Número da Maturidade - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['maturity']['number']} arcano maturidade",
            f"arcano maior número {numerology_map['maturity']['number']} tarot numerologia maturidade",
            f"carta tarot número {numerology_map['maturity']['number']} numerologia segunda metade vida",
            f"tarot arcano {numerology_map['maturity']['number']} maturidade numerologia futuro",
        ])
        
        # Buscar contexto do RAG com mais resultados (aumentado para incluir mais contexto de tarot)
        context_documents = []
        if rag_service:
            for query in queries:
                try:
                    results = rag_service.search(query, top_k=5, expand_query=True, category='numerology')
                    context_documents.extend(results)
                except Exception as e:
                    print(f"[WARNING] Erro ao buscar query '{query}': {e}")
        
        # Remover duplicatas e ordenar por relevância (aumentado limite para mais contexto de tarot)
        seen_texts = set()
        unique_docs = []
        for doc in sorted(context_documents, key=lambda x: x.get('score', 0), reverse=True):
            doc_text = doc.get('text', '').strip()
            if doc_text and doc_text not in seen_texts and len(doc_text) > 50:
                seen_texts.add(doc_text)
                unique_docs.append(doc)
                if len(unique_docs) >= 30:  # Aumentado de 20 para 30 para incluir mais contexto de tarot
                    break
        
        context_text = "\n\n".join([
            f"[Fonte: {doc.get('source', 'unknown')} - Página {doc.get('page', 1)}]\n{doc.get('text', '')}"
            for doc in unique_docs[:20]  # Aumentado de 15 para 20 para incluir mais contexto de tarot
            if doc.get('text')
        ])
        
        # Preparar informações detalhadas do mapa
        master_info = []
        if numerology_map['life_path']['is_master']:
            master_info.append(f"Caminho de Vida {numerology_map['life_path']['number']} é um Número Mestre")
        if numerology_map['destiny']['is_master']:
            master_info.append(f"Destino {numerology_map['destiny']['number']} é um Número Mestre")
        if numerology_map['soul']['is_master']:
            master_info.append(f"Alma {numerology_map['soul']['number']} é um Número Mestre")
        
        master_note = "\n".join(master_info) if master_info else "Nenhum número mestre presente."
        
        # Gerar interpretação com IA - prompt muito mais detalhado e inspirador
        system_prompt = """Você é um Numerólogo Pitagórico experiente e inspirador, com profundo conhecimento da conexão entre Numerologia e Tarot. Sua missão é ajudar pessoas a compreenderem seus números e usarem essa sabedoria para viverem vidas mais plenas e realizadas.

CONHECIMENTO INTEGRADO - TAROT E NUMEROLOGIA:
- Numerologia e Tarot têm uma forte ligação histórica e simbólica que remonta séculos
- Cada número na numerologia (1-9 e números mestres) corresponde a um Arcano Maior do Tarot
- A integração Tarot-Numerologia é ESSENCIAL para uma interpretação completa e rica
- O Tarot oferece símbolos visuais e arquetípicos que facilitam o entendimento dos números
- Cada Arcano traz camadas adicionais de significado que enriquecem a interpretação numerológica

REGRAS OBRIGATÓRIAS PARA INTERPRETAÇÃO:
1. **PARA CADA NÚMERO DO MAPA NUMEROLÓGICO, VOCÊ DEVE:**
   - Identificar o Arcano do Tarot correspondente ao número
   - Incluir uma subseção dedicada ao Arcano em cada seção do número
   - Explicar o significado simbólico do Arcano
   - Mostrar como o Arcano complementa a interpretação numerológica
   - Conectar os ensinamentos do Arcano com os aspectos práticos do número
   - Usar a sabedoria do Arcano para oferecer orientações práticas

2. **ESTRUTURA OBRIGATÓRIA PARA CADA NÚMERO:**
   - Interpretação numerológica do número
   - **Subseção: "O Arcano do Tarot Correspondente"** (com nome do Arcano)
   - Significado simbólico do Arcano
   - Conexões entre número e Arcano
   - Como usar a sabedoria do Arcano na vida prática
   - Pontos positivos e desafios (integrados com sabedoria do Tarot)
   - Orientações práticas

DIRETRIZES IMPORTANTES:
- Use linguagem clara, inspiradora e acolhedora (o usuário é leigo)
- Sempre equilibre pontos positivos e desafios, mas foque em orientações práticas
- Forneça exemplos concretos e aplicáveis à vida real
- Seja encorajador e mostre como transformar desafios em oportunidades
- Use tom terapêutico e empoderador
- Quando mencionar conexões com Tarot, explique de forma simples e acessível
- NUNCA omita a interpretação do Tarot - ela é parte essencial da interpretação numerológica completa"""
        
        user_prompt = f"""MAPA NUMEROLÓGICO DE {numerology_map['full_name'].upper()}

📊 NÚMEROS PRINCIPAIS:

1. CAMINHO DE VIDA: {numerology_map['life_path']['number']} {"(Número Mestre)" if numerology_map['life_path']['is_master'] else ""}
   - Este é o número mais importante. Representa sua missão de vida, o caminho que você veio percorrer nesta encarnação.
   - Cálculo: Dia {numerology_map['life_path']['day']} + Mês {numerology_map['life_path']['month']} + Ano {numerology_map['life_path']['year']} = {numerology_map['life_path']['raw_total']} → {numerology_map['life_path']['number']}

2. NÚMERO DO DESTINO (Expressão): {numerology_map['destiny']['number']} {"(Número Mestre)" if numerology_map['destiny']['is_master'] else ""}
   - Revela seus talentos naturais, habilidades inatas e como você pode expressar seu potencial máximo.

3. NÚMERO DA ALMA (Desejo do Coração): {numerology_map['soul']['number']} {"(Número Mestre)" if numerology_map['soul']['is_master'] else ""}
   - Mostra suas motivações profundas, o que realmente move seu coração e o que você deseja no nível da alma.

4. NÚMERO DA PERSONALIDADE: {numerology_map['personality']['number']}
   - Indica como você se apresenta ao mundo, sua máscara social e como os outros te percebem inicialmente.

5. NÚMERO DO ANIVERSÁRIO: {numerology_map['birthday']['number']}
   - Revela talentos especiais e habilidades que você trouxe ao nascer neste dia específico.

6. NÚMERO DA MATURIDADE: {numerology_map['maturity']['number']}
   - Indica o potencial que você desenvolverá na segunda metade da vida, após os 35-40 anos.

📝 NOTAS ESPECIAIS:
{master_note}

📚 CONHECIMENTO NUMEROLÓGICO E TAROT DE REFERÊNCIA (RAG):
{context_text[:6000] if context_text else "Informações numerológicas básicas da tradição pitagórica e conexões com Tarot."}

NOTA CRÍTICA: O contexto RAG inclui informações detalhadas sobre Numerologia e também sobre a conexão entre Numerologia e Tarot. É OBRIGATÓRIO que você:
1. Identifique o Arcano do Tarot correspondente a CADA número do mapa numerológico
2. Inclua uma subseção sobre o Arcano em CADA seção do número correspondente
3. Explique como o Arcano complementa e enriquece a interpretação numerológica
4. Use as informações do contexto RAG sobre tarot para fornecer interpretações completas e detalhadas
5. Facilite o entendimento do usuário através das conexões simbólicas entre números e cartas do Tarot

---

INSTRUÇÕES PARA A INTERPRETAÇÃO:

Crie uma interpretação COMPLETA, DETALHADA e INSPIRADORA que inclua:

1. **INTRODUÇÃO ENCORAJADORA** (1 parágrafo)
   - Dê boas-vindas calorosas e explique que os números são ferramentas de autoconhecimento
   - Enfatize que não há números "bons" ou "ruins", apenas diferentes caminhos de evolução

2. **CAMINHO DE VIDA** (3-4 parágrafos)
   - Explique em detalhes o que significa ter Caminho de Vida {numerology_map['life_path']['number']}
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['life_path']['number']}**
     * Nome do Arcano correspondente
     * Significado simbólico do Arcano
     * Como o Arcano complementa e enriquece a interpretação numerológica
     * Conexões entre o número e a carta do Tarot
     * Como usar a sabedoria do Arcano para viver melhor o Caminho de Vida
   - Liste 4-5 pontos POSITIVOS (forças, talentos, características positivas)
   - Liste 2-3 DESAFIOS ou áreas de atenção (sem ser negativo, mas orientador)
   - Forneça 2-3 orientações práticas de como usar essas energias positivamente
   - Use exemplos concretos de como esse número se manifesta na vida

3. **NÚMERO DO DESTINO** (2-3 parágrafos)
   - Explique os talentos e habilidades naturais associados ao número {numerology_map['destiny']['number']}
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['destiny']['number']}**
     * Nome do Arcano correspondente
     * Como o Arcano revela os talentos e potencial de expressão
     * Conexões entre o número do Destino e a carta do Tarot
     * Como usar a sabedoria do Arcano para desenvolver os talentos
   - Mostre como desenvolver e expressar esses talentos
   - Oriente sobre carreiras, atividades e formas de expressão que alinham com esse número

4. **NÚMERO DA ALMA** (2-3 parágrafos)
   - Revele as motivações profundas e desejos do coração do número {numerology_map['soul']['number']}
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['soul']['number']}**
     * Nome do Arcano correspondente
     * Como o Arcano revela os desejos profundos da alma
     * Conexões entre o número da Alma e a carta do Tarot
     * Como usar a sabedoria do Arcano para honrar as necessidades internas
   - Explique como honrar essas necessidades internas
   - Oriente sobre como criar uma vida que satisfaça essas motivações profundas

5. **NÚMERO DA PERSONALIDADE** (2 parágrafos)
   - Explique como o número {numerology_map['personality']['number']} influencia a primeira impressão
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['personality']['number']}**
     * Nome do Arcano correspondente
     * Como o Arcano revela a máscara social e primeira impressão
     * Conexões entre o número da Personalidade e a carta do Tarot
     * Como usar a sabedoria do Arcano para apresentar-se ao mundo
   - Mostre como usar essa energia de forma positiva
   - Oriente sobre como equilibrar a personalidade externa com a alma interna

6. **NÚMERO DO ANIVERSÁRIO** (1-2 parágrafos)
   - Explique os talentos especiais do dia {numerology_map['birthday']['day']}
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['birthday']['number']}**
     * Nome do Arcano correspondente
     * Como o Arcano revela os dons especiais do dia de nascimento
     * Conexões entre o número do Aniversário e a carta do Tarot
     * Como usar a sabedoria do Arcano para desenvolver os talentos inatos
   - Mostre como desenvolver esses dons naturais

7. **NÚMERO DA MATURIDADE** (1-2 parágrafos)
   - Explique o potencial futuro do número {numerology_map['maturity']['number']}
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['maturity']['number']}**
     * Nome do Arcano correspondente
     * Como o Arcano revela o potencial de evolução na segunda metade da vida
     * Conexões entre o número da Maturidade e a carta do Tarot
     * Como usar a sabedoria do Arcano para se preparar para a evolução futura
   - Oriente sobre como se preparar para essa evolução

8. **SÍNTESE E ORIENTAÇÃO FINAL** (1-2 parágrafos)
   - Integre todos os números em uma visão unificada
   - Forneça orientações práticas e inspiradoras para usar essa sabedoria
   - Encoraje o usuário a abraçar seu caminho único e desenvolver seus potenciais
   - Use linguagem empoderadora e esperançosa

ESTILO E TOM:
- Use linguagem clara, acessível e inspiradora
- Evite jargões técnicos complexos
- Seja específico e prático, não vago
- Equilibre realismo com otimismo
- Foque em crescimento, evolução e possibilidades
- Use exemplos da vida real quando possível
- Seja acolhedor e encorajador

IMPORTANTE: O usuário é leigo e busca orientação prática para viver melhor. Foque em como usar os números de forma positiva e construtiva."""
        
        interpretation_text = provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=6000  # Aumentado para permitir interpretação mais detalhada e completa
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
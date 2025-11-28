"""
API endpoints para interpretação astrológica usando RAG.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.core.database import get_db
from app.services.rag_service import get_rag_service
from app.services.transits_calculator import calculate_future_transits
from app.api.auth import get_current_user
from app.models.database import BirthChart

router = APIRouter()


class DailyAdviceRequest(BaseModel):
    """Request para conselhos diários."""
    moonHouse: int
    category: str  # 'love', 'career', 'family', 'health', 'period'
    planetaryPositions: Optional[List[Dict[str, Any]]] = None  # Lista de {name, house, sign}
    moonSign: Optional[str] = None


class InterpretationRequest(BaseModel):
    """Request para interpretação astrológica."""
    planet: Optional[str] = None
    sign: Optional[str] = None
    house: Optional[int] = None
    aspect: Optional[str] = None
    custom_query: Optional[str] = None
    use_groq: Optional[bool] = True  # Por padrão, usar Groq se disponível


class InterpretationResponse(BaseModel):
    """Response com interpretação astrológica."""
    interpretation: str
    sources: list
    query_used: str
    generated_by: Optional[str] = None  # 'groq', 'rag_only', ou 'none'


@router.post("/interpretation", response_model=InterpretationResponse)
def get_interpretation(
    request: InterpretationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém interpretação astrológica baseada nos parâmetros fornecidos.
    
    Exemplos de uso:
    - planet="Sol", sign="Libra" → Interpretação de Sol em Libra
    - planet="Mercúrio", house=3 → Interpretação de Mercúrio na Casa 3
    - custom_query="ascendente em aquário" → Query customizada
    """
    try:
        rag_service = get_rag_service()
        
        interpretation = rag_service.get_interpretation(
            planet=request.planet,
            sign=request.sign,
            house=request.house,
            aspect=request.aspect,
            custom_query=request.custom_query,
            use_groq=request.use_groq
        )
        
        return InterpretationResponse(
            interpretation=interpretation['interpretation'],
            sources=interpretation['sources'],
            query_used=interpretation['query_used'],
            generated_by=interpretation.get('generated_by', 'unknown')
        )
    except Exception as e:
        print(f"[ERROR] Erro na interpretação: {e}")
        return InterpretationResponse(
            interpretation=f"Erro ao processar interpretação: {str(e)}",
            sources=[],
            query_used=request.custom_query or f"{request.planet} {request.sign}".strip(),
            generated_by="error"
        )


@router.get("/interpretation/search")
def search_documents(
    query: str,
    top_k: int = 5,
    authorization: Optional[str] = Header(None)
):
    """
    Busca documentos relevantes para uma query.
    
    Args:
        query: Texto da consulta
        top_k: Número de resultados (padrão: 5)
    """
    try:
        rag_service = get_rag_service()
        
        # Verificar se o índice está carregado
        if rag_service.embeddings is None or len(rag_service.documents) == 0:
            return {
                "query": query,
                "results": [],
                "count": 0,
                "error": "Índice RAG não carregado. Execute build_rag_index.py primeiro."
            }
        
        results = rag_service.search(query, top_k=top_k)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        print(f"[ERROR] Erro na busca: {e}")
        return {
            "query": query,
            "results": [],
            "count": 0,
            "error": str(e)
        }


@router.get("/interpretation/status")
def get_rag_status():
    """Retorna o status do sistema RAG."""
    try:
        rag_service = get_rag_service()
        
        has_index = rag_service.embeddings is not None and len(rag_service.documents) > 0
        has_groq = rag_service.groq_client is not None
        has_model = rag_service.model is not None
        
        return {
            "available": has_index and has_model,
            "document_count": len(rag_service.documents) if has_index else 0,
            "has_dependencies": has_model,
            "has_groq": has_groq,
            "model_loaded": has_model,
            "index_loaded": has_index,
            "error": None if (has_index and has_model) else "Índice não carregado ou modelo não disponível"
        }
    except Exception as e:
        return {
            "available": False,
            "document_count": 0,
            "has_dependencies": False,
            "has_groq": False,
            "error": str(e)
        }


@router.get("/transits/future")
def get_future_transits(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    months_ahead: int = 24,
    max_transits: int = 10
):
    """
    Calcula trânsitos futuros baseados no mapa astral do usuário.
    
    Args:
        months_ahead: Quantos meses à frente calcular (padrão: 24)
        max_transits: Número máximo de trânsitos (padrão: 10, mínimo: 5, máximo: 10)
    """
    try:
        # Obter usuário atual
        current_user = get_current_user(authorization, db)
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Não autenticado"
            )
        
        # Buscar mapa astral do usuário
        birth_chart = db.query(BirthChart).filter(
            BirthChart.user_id == current_user.id,
            BirthChart.is_primary == True
        ).first()
        
        if not birth_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapa astral não encontrado"
            )
        
        # Validar parâmetros
        max_transits = max(5, min(10, max_transits))
        months_ahead = max(6, min(36, months_ahead))
        
        # Calcular trânsitos
        transits = calculate_future_transits(
            birth_date=birth_chart.birth_date,
            birth_time=birth_chart.birth_time,
            latitude=birth_chart.latitude,
            longitude=birth_chart.longitude,
            months_ahead=months_ahead,
            max_transits=max_transits
        )
        
        # Enriquecer descrições com RAG + Groq
        enriched_transits = []
        rag_service = None
        
        try:
            rag_service = get_rag_service()
        except Exception as e:
            print(f"[WARNING] RAG service não disponível: {e}")
        
        for transit in transits:
            # Tentar enriquecer com RAG + Groq se disponível
            if rag_service:
                # Criar query mais específica para busca RAG
                natal_point_names = {
                    'sun': 'Sol',
                    'moon': 'Lua',
                    'mercury': 'Mercúrio',
                    'venus': 'Vênus',
                    'mars': 'Marte',
                    'ascendant': 'Ascendente'
                }
                natal_point_display = natal_point_names.get(transit.get('natal_point', ''), transit.get('natal_point', '').capitalize())
                
                # Query mais específica para encontrar informações sobre o trânsito
                transit_query = f"{transit.get('planet', '')} {transit.get('aspect_type', '')} {natal_point_display} trânsito interpretação"
                
                try:
                    # Verificar se o índice RAG está carregado
                    if rag_service.embeddings is not None and len(rag_service.documents) > 0:
                        # Buscar documentos relevantes
                        rag_results = rag_service.search(transit_query, top_k=3)
                        
                        # Se RAG e Groq estiverem disponíveis, gerar interpretação enriquecida
                        if rag_service.groq_client and rag_results:
                            enriched_description = _generate_transit_interpretation_with_groq(
                                rag_service,
                                transit,
                                rag_results
                            )
                            if enriched_description:
                                transit['description'] = enriched_description
                                print(f"[INFO] Trânsito enriquecido com RAG+Groq: {transit.get('planet')} {transit.get('aspect_type')} com {natal_point_display}")
                except Exception as e:
                    print(f"[WARNING] Erro ao enriquecer trânsito com RAG/Groq: {e}")
                    # Manter descrição original em caso de erro
                    pass
            
            enriched_transits.append(transit)
        
        # Formatar resposta
        formatted_transits = []
        for transit in enriched_transits:
            try:
                transit_date = datetime.fromisoformat(transit['date'])
            except (KeyError, ValueError, TypeError):
                print(f"[WARNING] Erro ao processar data do trânsito: {transit.get('date', 'N/A')}")
                continue
            
            # Tentar obter start_date e end_date, com fallback
            try:
                start_date = datetime.fromisoformat(transit.get('start_date', transit['date']))
            except (KeyError, ValueError, TypeError):
                start_date = transit_date
            
            try:
                end_date = datetime.fromisoformat(transit.get('end_date', transit['date']))
            except (KeyError, ValueError, TypeError):
                # Se não tiver end_date, estimar baseado no tipo de aspecto
                duration_days = {
                    'conjunção': 30,
                    'sextil': 20,
                    'quadratura': 25,
                    'trígono': 20,
                    'oposição': 30
                }
                aspect_type = transit.get('aspect_type', 'conjunção')
                estimated_duration = duration_days.get(aspect_type, 30)
                end_date = start_date + timedelta(days=estimated_duration)
            
            # Determinar tipo para o frontend
            transit_type_map = {
                'conjunction': 'jupiter' if transit['planet'] == 'Júpiter' else 
                              'saturn-return' if transit['transit_type'] == 'saturn-return' else
                              'uranus' if transit['planet'] == 'Urano' else
                              'neptune' if transit['planet'] == 'Netuno' else
                              'pluto',
                'opposition': 'jupiter' if transit['planet'] == 'Júpiter' else
                             'uranus' if transit['planet'] == 'Urano' else
                             'neptune' if transit['planet'] == 'Netuno' else
                             'pluto',
                'square': 'uranus',
                'trine': 'jupiter'
            }
            
            transit_type = transit_type_map.get(transit['transit_type'], 'jupiter')
            if transit['transit_type'] == 'saturn-return':
                transit_type = 'saturn-return'
            
            # Formatar timeframe com datas reais
            months_pt = [
                'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
            ]
            timeframe = f"{months_pt[start_date.month - 1]} {start_date.year} - {months_pt[end_date.month - 1]} {end_date.year}"
            
            # Mapear tipo de aspecto para português
            aspect_type_pt = {
                'conjunção': 'Conjunção',
                'sextil': 'Sextil',
                'quadratura': 'Quadratura',
                'trígono': 'Trígono',
                'oposição': 'Oposição'
            }
            aspect_type_display = aspect_type_pt.get(transit['aspect_type'], transit['aspect_type'].capitalize())
            
            formatted_transits.append({
                'id': f"{transit['planet']}-{transit['natal_point']}-{start_date.isoformat()}",
                'type': transit_type,
                'title': transit['title'],
                'planet': transit['planet'],
                'timeframe': timeframe,
                'description': transit['description'],
                'isActive': transit['is_active'],
                'date': start_date.isoformat(),
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'aspect_type': transit['aspect_type'],
                'aspect_type_display': aspect_type_display,
                'natal_point': transit['natal_point']
            })
        
        return {
            "transits": formatted_transits,
            "count": len(formatted_transits)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular trânsitos: {str(e)}"
        )


def _generate_transit_interpretation_with_groq(
    rag_service,
    transit: Dict,
    rag_results: List[Dict]
) -> Optional[str]:
    """
    Gera interpretação enriquecida de trânsito usando RAG + Groq.
    
    Args:
        rag_service: Instância do serviço RAG
        transit: Dicionário com dados do trânsito
        rag_results: Resultados da busca RAG
    
    Returns:
        Descrição enriquecida ou None em caso de erro
    """
    if not rag_service.groq_client:
        return None
    
    # Preparar contexto dos documentos
    context_text = "\n\n".join([
        f"--- Documento {i+1} (Fonte: {doc['source']}, Página {doc['page']}) ---\n{doc['text']}"
        for i, doc in enumerate(rag_results)
    ])
    
    # Prompt otimizado para reduzir tokens
    system_prompt = """Astrólogo especialista em trânsitos. Crie interpretações práticas e acessíveis baseadas nos documentos. Foque em insights aplicáveis e orientações práticas."""
    
    # Converter nome do ponto natal
    natal_point_names = {
        'sun': 'Sol',
        'moon': 'Lua',
        'mercury': 'Mercúrio',
        'venus': 'Vênus',
        'mars': 'Marte',
        'ascendant': 'Ascendente'
    }
    natal_point_display = natal_point_names.get(transit.get('natal_point', ''), transit.get('natal_point', '').capitalize())
    
    aspect_names_pt = {
        'conjunção': 'conjunção',
        'oposição': 'oposição',
        'quadratura': 'quadratura',
        'trígono': 'trígono',
        'sextil': 'sextil'
    }
    aspect_name_pt = aspect_names_pt.get(transit.get('aspect_type', ''), transit.get('aspect_type', ''))
    
    user_prompt = f"""Trânsito: {transit.get('planet', '')} {aspect_name_pt} {natal_point_display}
Signo: {transit.get('natal_sign', '')} | Data: {transit.get('date', '')}

Contexto:
{context_text}

Crie interpretação prática (1-2 parágrafos): significado, impacto na área de vida do {natal_point_display}, orientações."""
    
    try:
        # Chamar Groq API
        chat_completion = rag_service.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model="llama-3.1-8b-instant",  # Modelo mais rápido e econômico
            temperature=0.7,
            max_tokens=350,  # Otimizado para 1-2 parágrafos
            top_p=1,
        )
        
        interpretation = chat_completion.choices[0].message.content
        return interpretation.strip()
        
    except Exception as e:
        print(f"[ERROR] Erro ao gerar interpretação de trânsito com Groq: {e}")
        return None


class PlanetInterpretationRequest(BaseModel):
    planet: str
    sign: Optional[str] = None
    house: Optional[int] = None


@router.post("/interpretation/planet")
def get_planet_interpretation(
    request: PlanetInterpretationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém interpretação de um planeta em um signo ou casa usando RAG + Groq.
    
    Body:
    {
        "planet": "Sol",
        "sign": "Libra",
        "house": 5  # opcional
    }
    """
    try:
        rag_service = get_rag_service()
        
        planet = request.planet
        sign = request.sign
        house = request.house
        
        if not planet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Planeta é obrigatório"
            )
        
        # Construir query para RAG
        query_parts = [planet]
        if sign:
            query_parts.append(f"em {sign}")
        if house:
            query_parts.append(f"casa {house}")
        
        query = " ".join(query_parts)
        
        # Buscar no RAG e gerar com Groq
        interpretation = rag_service.get_interpretation(
            planet=planet,
            sign=sign,
            house=house,
            use_groq=True
        )
        
        return {
            "interpretation": interpretation['interpretation'],
            "sources": interpretation['sources'],
            "query_used": interpretation['query_used'],
            "generated_by": interpretation.get('generated_by', 'rag_only')
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter interpretação: {str(e)}"
        )


class ChartRulerInterpretationRequest(BaseModel):
    ascendant: str
    ruler: str
    rulerSign: str
    rulerHouse: int


@router.post("/interpretation/chart-ruler")
def get_chart_ruler_interpretation(
    request: ChartRulerInterpretationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém interpretação do regente do mapa usando RAG + Groq.
    
    Body:
    {
        "ascendant": "Aquário",
        "ruler": "Urano",
        "rulerSign": "Escorpião",
        "rulerHouse": 3
    }
    """
    try:
        rag_service = get_rag_service()
        
        ascendant = request.ascendant
        ruler = request.ruler
        ruler_sign = request.rulerSign
        ruler_house = request.rulerHouse
        
        if not ascendant or not ruler:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ascendente e regente são obrigatórios"
            )
        
        # Construir query customizada
        query = f"regente do mapa {ruler} ascendente {ascendant}"
        if ruler_sign:
            query += f" {ruler} em {ruler_sign}"
        if ruler_house:
            query += f" casa {ruler_house}"
        
        # Buscar no RAG e gerar com Groq
        interpretation = rag_service.get_interpretation(
            custom_query=query,
            use_groq=True
        )
        
        return {
            "interpretation": interpretation['interpretation'],
            "sources": interpretation['sources'],
            "query_used": interpretation['query_used'],
            "generated_by": interpretation.get('generated_by', 'rag_only')
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter interpretação: {str(e)}"
        )


class PlanetHouseInterpretationRequest(BaseModel):
    planet: str
    house: int


@router.post("/interpretation/planet-house")
def get_planet_house_interpretation(
    request: PlanetHouseInterpretationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém interpretação de um planeta em uma casa usando RAG + Groq.
    
    Body:
    {
        "planet": "Sol",
        "house": 5
    }
    """
    try:
        rag_service = get_rag_service()
        
        planet = request.planet
        house = request.house
        
        if not planet or not house:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Planeta e casa são obrigatórios"
            )
        
        # Buscar no RAG e gerar com Groq
        interpretation = rag_service.get_interpretation(
            planet=planet,
            house=house,
            use_groq=True
        )
        
        return {
            "interpretation": interpretation['interpretation'],
            "sources": interpretation['sources'],
            "query_used": interpretation['query_used'],
            "generated_by": interpretation.get('generated_by', 'rag_only')
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter interpretação: {str(e)}"
        )


class AspectInterpretationRequest(BaseModel):
    planet1: str
    planet2: str
    aspect: str


@router.post("/interpretation/aspect")
def get_aspect_interpretation(
    request: AspectInterpretationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém interpretação de um aspecto entre planetas usando RAG + Groq.
    
    Body:
    {
        "planet1": "Sol",
        "planet2": "Lua",
        "aspect": "conjunção"
    }
    """
    try:
        rag_service = get_rag_service()
        
        planet1 = request.planet1
        planet2 = request.planet2
        aspect = request.aspect
        
        if not planet1 or not planet2 or not aspect:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Planeta1, Planeta2 e aspecto são obrigatórios"
            )
        
        # Construir query customizada
        query = f"{planet1} {aspect} {planet2} aspecto interpretação"
        
        # Buscar no RAG e gerar com Groq
        interpretation = rag_service.get_interpretation(
            custom_query=query,
            use_groq=True
        )
        
        return {
            "interpretation": interpretation['interpretation'],
            "sources": interpretation['sources'],
            "query_used": interpretation['query_used'],
            "generated_by": interpretation.get('generated_by', 'rag_only')
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter interpretação: {str(e)}"
        )


@router.post("/interpretation/daily-advice")
def get_daily_advice(
    request: DailyAdviceRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém conselhos diários baseados na casa lunar e posições planetárias.
    Usa RAG para buscar informações localmente e Groq para organizar e formatar.
    
    Body:
    {
        "moonHouse": 5,
        "category": "love",
        "moonSign": "Câncer",
        "planetaryPositions": [
            {"name": "Vênus", "house": 7, "sign": "Libra"},
            {"name": "Lua", "house": 4, "sign": "Câncer"}
        ]
    }
    """
    try:
        rag_service = get_rag_service()
        
        # Construir query baseada na categoria e casa lunar
        category_queries = {
            'love': ['amor relacionamentos romance parcerias', 'Vênus Lua Júpiter'],
            'career': ['carreira profissão trabalho dinheiro', 'Sol Saturno Marte Júpiter'],
            'family': ['família lar raízes parentes', 'Lua Vênus Saturno'],
            'health': ['saúde bem-estar corpo físico', 'Marte Saturno Lua Sol'],
            'period': ['período atual momento presente', 'Sol Lua Mercúrio Vênus Marte']
        }
        
        # Query base para a categoria
        base_query = category_queries.get(request.category, ['conselho astrológico'])
        
        # Construir query detalhada
        query_parts = []
        
        # Adicionar informação sobre casa lunar
        house_themes = {
            1: 'identidade autoconfiança novos começos',
            2: 'valores recursos financeiros segurança',
            3: 'comunicação aprendizado irmãos',
            4: 'lar família raízes',
            5: 'criatividade romance diversão',
            6: 'rotina saúde trabalho',
            7: 'parcerias relacionamentos',
            8: 'transformação intimidade',
            9: 'filosofia viagens expansão',
            10: 'carreira reconhecimento público',
            11: 'amizades grupos futuro',
            12: 'introspecção espiritualidade'
        }
        
        query_parts.append(f"casa {request.moonHouse} {house_themes.get(request.moonHouse, '')}")
        query_parts.extend(base_query)
        
        # Adicionar informações sobre planetas relevantes
        if request.planetaryPositions:
            relevant_planets = {
                'love': ['Vênus', 'Lua', 'Júpiter', 'Marte'],
                'career': ['Sol', 'Saturno', 'Marte', 'Júpiter'],
                'family': ['Lua', 'Vênus', 'Saturno'],
                'health': ['Marte', 'Saturno', 'Lua', 'Sol'],
                'period': ['Sol', 'Lua', 'Mercúrio', 'Vênus', 'Marte']
            }
            
            planets_to_include = relevant_planets.get(request.category, [])
            for planet_pos in request.planetaryPositions:
                planet_name = planet_pos.get('name', '')
                if planet_name in planets_to_include:
                    house = planet_pos.get('house')
                    sign = planet_pos.get('sign', '')
                    if house:
                        query_parts.append(f"{planet_name} casa {house}")
                    if sign:
                        query_parts.append(f"{planet_name} {sign}")
        
        # Construir query final
        query = " ".join(query_parts)
        
        # Buscar interpretação usando RAG + Groq
        interpretation = rag_service.get_interpretation(
            custom_query=query,
            use_groq=True
        )
        
        # Se Groq não estiver disponível ou falhar, usar fallback
        if interpretation.get('generated_by') != 'groq' and rag_service.groq_client:
            # Tentar gerar com Groq usando contexto mais específico
            try:
                # Buscar documentos relevantes
                rag_results = rag_service.search(query, top_k=8)
                if rag_results:
                    interpretation_text = rag_service._generate_with_groq(
                        f"Conselho astrológico sobre {request.category} considerando Lua na casa {request.moonHouse}",
                        rag_results
                    )
                    interpretation['interpretation'] = interpretation_text
                    interpretation['generated_by'] = 'groq'
            except Exception as e:
                print(f"[WARNING] Erro ao gerar com Groq: {e}")
        
        return {
            "interpretation": interpretation['interpretation'],
            "sources": interpretation['sources'],
            "query_used": interpretation['query_used'],
            "generated_by": interpretation.get('generated_by', 'rag_only')
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter conselho diário: {str(e)}"
        )


# ===== MAPA ASTRAL COMPLETO =====

class FullBirthChartRequest(BaseModel):
    """Request para geração do Mapa Astral Completo."""
    name: str
    birthDate: str  # DD/MM/AAAA
    birthTime: str  # HH:MM
    birthPlace: str  # Cidade, País
    
    # Dados do mapa natal (calculados pelo frontend ou backend)
    sunSign: str
    moonSign: str
    ascendant: str
    sunHouse: int
    moonHouse: int
    
    # Planetas pessoais
    mercurySign: Optional[str] = None
    mercuryHouse: Optional[int] = None
    venusSign: Optional[str] = None
    venusHouse: Optional[int] = None
    marsSign: Optional[str] = None
    marsHouse: Optional[int] = None
    
    # Planetas sociais
    jupiterSign: Optional[str] = None
    jupiterHouse: Optional[int] = None
    saturnSign: Optional[str] = None
    saturnHouse: Optional[int] = None
    
    # Planetas geracionais
    uranusSign: Optional[str] = None
    uranusHouse: Optional[int] = None
    neptuneSign: Optional[str] = None
    neptuneHouse: Optional[int] = None
    plutoSign: Optional[str] = None
    plutoHouse: Optional[int] = None
    
    # Nodos Lunares
    northNodeSign: Optional[str] = None
    northNodeHouse: Optional[int] = None
    southNodeSign: Optional[str] = None
    southNodeHouse: Optional[int] = None
    
    # Quíron
    chironSign: Optional[str] = None
    chironHouse: Optional[int] = None
    
    # Meio do Céu e Fundo do Céu
    midheavenSign: Optional[str] = None  # Casa 10
    icSign: Optional[str] = None  # Casa 4
    
    # Aspectos principais (opcional)
    aspects: Optional[List[Dict[str, Any]]] = None
    
    # Seção específica para gerar (se None, gera tudo)
    section: Optional[str] = None  # 'triad', 'roots', 'karma', 'career', 'love', 'synthesis'
    
    # Idioma
    language: Optional[str] = 'pt'  # 'pt' ou 'en'


class FullBirthChartResponse(BaseModel):
    """Response com o Mapa Astral Completo."""
    section: str
    title: str
    content: str
    generated_by: str


class FullBirthChartSectionsResponse(BaseModel):
    """Response com todas as seções do Mapa Astral."""
    name: str
    birthData: str
    sections: List[FullBirthChartResponse]
    generated_at: str


def _get_master_prompt(language: str = 'pt') -> str:
    """Retorna o prompt mestre para geração do Mapa Astral."""
    if language == 'en':
        return """**SYSTEM CONTEXT:**
You are COSMOS ASTRAL, an advanced astrological engine capable of interpreting Natal Charts with psychological, karmic, and predictive depth. Your function is to receive planetary positions and generate a coherent synthesis, not just a list of definitions.

You are a Senior Astrologer with 30 years of experience in Psychological Astrology (Jungian approach) and Evolutionary Astrology (focused on the soul's purpose). Your language should be welcoming but deeply analytical. You avoid the obvious and seek synthesis between the map's contradictions.

**HIERARCHY AND WEIGHT GUIDELINES (IMPORTANT):**

When interpreting the chart, you must respect the following order of relevance:

1. **Level 1 (Maximum Weight):** Sun, Moon, and Ascendant Ruler. These define the "skeleton" of the personality.
2. **Level 2 (High Weight):** Personal Planets (Mercury, Venus, Mars) and Aspects to Angles (Conjunctions to Ascendant/Midheaven).
3. **Level 3 (Medium Weight):** Lunar Nodes, Saturn and Jupiter. (Focus on Destiny and Social Structure).
4. **Level 4 (Refined Weight):** Chiron, Lilith and Transpersonal Planets (Uranus, Neptune, Pluto) in houses.
5. **Level 5 (Fine Detail):** Asteroids (Ceres, Juno, Pallas, Vesta) and Fixed Stars.

**CELESTIAL BODIES REFERENCE:**

• LUMINARIES AND PERSONAL PLANETS (Personality Core):
  - Sun: Essence, Conscious Ego, Vital Purpose
  - Moon: Unconscious, Emotions, Past, Nurturing
  - Mercury: Intellect, Communication, Data Processing
  - Venus: Affection, Values, Money, Small Happiness
  - Mars: Action, Desire, Conquest, Defense

• SOCIAL PLANETS (Interaction with Environment):
  - Jupiter: Expansion, Faith, Wisdom, Great Benefic
  - Saturn: Structure, Limits, Time, Karmic Master

• TRANSPERSONAL/GENERATIONAL PLANETS (Collective Unconscious):
  - Uranus: Revolution, The Unexpected, Higher Mind
  - Neptune: Spirituality, Illusion, Fusion, Arts
  - Pluto: Transformation, Death/Rebirth, Hidden Power

• MATHEMATICAL AND KARMIC POINTS (Destiny):
  - Ascendant (AC): Projected Identity (House 1 Cusp)
  - Midheaven (MC): Social Destiny (House 10 Cusp)
  - North Node: Life Mission, Where to go
  - South Node: Comfort Zone, Past Lives Baggage
  - Lilith (Black Moon): Shadow side, repressed sexuality, rebellion
  - Chiron: The Wounded Healer (Where it hurts and where we heal)

**SPECIFIC INTERPRETATION DEFINITIONS:**

• When analyzing LUNAR NODES: Don't just say "good or bad". Interpret the Nodal Axis as the soul's journey: South Node (what has been mastered/past) -> North Node (evolutionary challenge/future).

• When analyzing CHIRON: Focus on the "wound that becomes gift". Where the person feels inadequacy, but where they become a master at helping others.

• When analyzing LILITH: Interpret as visceral force, untamed desire, and where the person refuses submission.

• When analyzing SATURN: Interpret as the great teacher who demands maturity, discipline, and shows where rewards come late but solidly.

**SYNTHESIS RULES (COMBINATION):**

• If an Asteroid (e.g., Juno) aspects a Luminary (e.g., Moon), merge the meanings: "Your emotional need (Moon) is intrinsically linked to the need for committed partnership (Juno)."

• Never generate contradictions without explaining them. If the Sun asks for freedom and Saturn asks for restriction, explain this as an "internal tension of maturation."

**GENERAL DIRECTIVE:**
Do not make loose lists of meanings. I want a NARRATIVE that connects the dots. If the Sun says one thing and the Moon says another, explain the internal tension.

**STYLE RULES:**
1. Write in counseling tone, focusing on healing potential and free will
2. Avoid fatalism - show possibilities, not determinism
3. Be specific, not generic - connect the energies
4. Use practical examples to illustrate
5. Address the person directly using "you"
6. Explain astrological terms simply when you use them
7. Always prioritize the PSYCHOLOGY OF THE INDIVIDUAL before entering predictions or karmas"""
    else:
        return """**CONTEXTO DO SISTEMA:**
Você é o COSMOS ASTRAL, uma engine astrológica avançada capaz de interpretar Mapas Natais com profundidade psicológica, kármica e preditiva. Sua função é receber as posições planetárias e gerar uma síntese coerente, não apenas uma lista de definições.

Você é um Astrólogo Sênior com 30 anos de experiência em Astrologia Psicológica (linha Junguiana) e Astrologia Evolutiva (focada no propósito da alma). Sua linguagem deve ser acolhedora, mas profundamente analítica. Você foge do óbvio e busca a síntese entre as contradições do mapa.

**DIRETRIZES DE HIERARQUIA E PESO (IMPORTANTE):**

Ao interpretar o mapa, você deve respeitar a seguinte ordem de relevância:

1. **Nível 1 (Peso Máximo):** Sol, Lua e Regente do Ascendente. Estes definem o "esqueleto" da personalidade.
2. **Nível 2 (Peso Alto):** Planetas Pessoais (Mercúrio, Vênus, Marte) e Aspectos aos Ângulos (Conjunções ao Ascendente/Meio do Céu).
3. **Nível 3 (Peso Médio):** Nodos Lunares, Saturno e Júpiter. (Foco em Destino e Estrutura Social).
4. **Nível 4 (Peso Refinado):** Quíron, Lilith e Planetas Transpessoais (Urano, Netuno, Plutão) nas casas.
5. **Nível 5 (Detalhe Fino):** Asteroides (Ceres, Juno, Pallas, Vesta) e Estrelas Fixas.

**REFERÊNCIA DOS CORPOS CELESTES:**

• LUMINARES E PLANETAS PESSOAIS (Núcleo da Personalidade):
  - Sol: A Essência, o Ego Consciente, Propósito Vital
  - Lua: O Inconsciente, Emoções, Passado, Nutrição
  - Mercúrio: Intelecto, Comunicação, Processamento de Dados
  - Vênus: Afeto, Valores, Dinheiro, Pequena Felicidade
  - Marte: Ação, Desejo, Conquista, Defesa

• PLANETAS SOCIAIS (A Interação com o Meio):
  - Júpiter: Expansão, Fé, Sabedoria, Grande Benéfico
  - Saturno: Estrutura, Limites, Tempo, Mestre Kármico

• PLANETAS TRANSPESSOAIS/GERACIONAIS (O Inconsciente Coletivo):
  - Urano: A Revolução, O Inesperado, A Mente Superior
  - Netuno: A Espiritualidade, Ilusão, Fusão, Artes
  - Plutão: A Transformação, Morte/Renascimento, Poder Oculto

• PONTOS MATEMÁTICOS E KÁRMICOS (O Destino):
  - Ascendente (AC): A Identidade Projetada (Cúspide Casa 1)
  - Meio do Céu (MC): O Destino Social (Cúspide Casa 10)
  - Nodo Norte (Cabeça do Dragão): Missão de Vida, Onde se deve ir
  - Nodo Sul (Cauda do Dragão): Zona de Conforto, Bagagem de Vidas Passadas
  - Lilith (Lua Negra): O lado sombra, a sexualidade reprimida, a rebeldia
  - Quíron: O Curador Ferido (Onde dói e onde curamos)

**DEFINIÇÕES DE INTERPRETAÇÃO ESPECÍFICA:**

• Ao analisar NODOS LUNARES: Não diga apenas "bom ou ruim". Interprete o Eixo Nodal como a jornada da alma: Nodo Sul (o que já foi dominado/passado) -> Nodo Norte (o desafio evolutivo/futuro).

• Ao analisar QUÍRON: Foque na "ferida que vira dom". Onde a pessoa sente inadequação, mas onde ela se torna mestre em ajudar os outros.

• Ao analisar LILITH: Interprete como a força visceral, o desejo não domesticado e onde a pessoa recusa submissão.

• Ao analisar SATURNO: Interprete como o grande professor que exige maturidade, disciplina e mostra onde as recompensas vêm tarde, mas de forma sólida.

**REGRAS DE SÍNTESE (COMBINAÇÃO):**

• Se um Asteroide (ex: Juno) estiver em aspecto com um Luminar (ex: Lua), funda os significados: "Sua necessidade emocional (Lua) está intrinsecamente ligada à necessidade de parceria comprometida (Juno)."

• Nunca gere contradições sem explicá-las. Se o Sol pede liberdade e Saturno pede restrição, explique isso como uma "tensão interna de amadurecimento".

**DIRETRIZ GERAL:**
Não faça listas soltas de significados. Eu quero uma NARRATIVA que conecte os pontos. Se o Sol diz uma coisa e a Lua diz outra, explique a tensão interna.

**REGRAS DE ESTILO:**
1. Escreva em tom de aconselhamento, focando no potencial de cura e no livre-arbítrio
2. Evite fatalismos - mostre possibilidades, não determinismos
3. Seja específico, não genérico - conecte as energias
4. Use exemplos práticos para ilustrar
5. Trate a pessoa diretamente usando "você"
6. Explique termos astrológicos de forma simples quando usá-los
7. Sempre priorize a PSICOLOGIA DO INDIVÍDUO antes de entrar em previsões ou carmas"""


def _get_full_chart_context(request: FullBirthChartRequest, lang: str = 'pt') -> str:
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
- Mercúrio em {request.mercurySign or 'não calculado'} (Comunicação, Mente)
- Vênus em {request.venusSign or 'não calculado'} (Amor, Valores)
- Marte em {request.marsSign or 'não calculado'} (Ação, Desejo)

🪐 PLANETAS SOCIAIS (Nível 3):
- Júpiter em {request.jupiterSign or 'não calculado'} (Expansão, Sorte)
- Saturno em {request.saturnSign or 'não calculado'} (Limites, Mestre Kármico)

🌌 PLANETAS TRANSPESSOAIS (Nível 4):
- Urano em {request.uranusSign or 'não calculado'} (Revolução, Liberdade)
- Netuno em {request.neptuneSign or 'não calculado'} (Espiritualidade, Ilusão)
- Plutão em {request.plutoSign or 'não calculado'} (Transformação, Poder)

🎯 PONTOS KÁRMICOS:
- Ascendente em {request.ascendant} (Máscara Social)
- Meio do Céu em {request.midheavenSign or 'não calculado'} (Vocação, Reputação)
- Nodo Norte em {request.northNodeSign or 'não calculado'} (Destino, Evolução)
- Nodo Sul em {request.southNodeSign or 'não calculado'} (Passado, Zona de Conforto)
- Quíron em {request.chironSign or 'não calculado'} (Ferida/Dom de Cura)
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
- Mercury in {request.mercurySign or 'not calculated'} (Communication, Mind)
- Venus in {request.venusSign or 'not calculated'} (Love, Values)
- Mars in {request.marsSign or 'not calculated'} (Action, Desire)

🪐 SOCIAL PLANETS (Level 3):
- Jupiter in {request.jupiterSign or 'not calculated'} (Expansion, Luck)
- Saturn in {request.saturnSign or 'not calculated'} (Limits, Karmic Master)

🌌 TRANSPERSONAL PLANETS (Level 4):
- Uranus in {request.uranusSign or 'not calculated'} (Revolution, Freedom)
- Neptune in {request.neptuneSign or 'not calculated'} (Spirituality, Illusion)
- Pluto in {request.plutoSign or 'not calculated'} (Transformation, Power)

🎯 KARMIC POINTS:
- Ascendant in {request.ascendant} (Social Mask)
- Midheaven in {request.midheavenSign or 'not calculated'} (Vocation, Reputation)
- North Node in {request.northNodeSign or 'not calculated'} (Destiny, Evolution)
- South Node in {request.southNodeSign or 'not calculated'} (Past, Comfort Zone)
- Chiron in {request.chironSign or 'not calculated'} (Wound/Healing Gift)
"""


def _generate_section_prompt(request: FullBirthChartRequest, section: str) -> tuple[str, str]:
    """Gera o prompt específico para cada seção do mapa."""
    lang = request.language or 'pt'
    
    # Contexto completo do mapa para referência
    full_context = _get_full_chart_context(request, lang)
    
    if section == 'triad':
        title = "A Tríade da Personalidade" if lang == 'pt' else "The Personality Triad"
        if lang == 'pt':
            prompt = f"""{full_context}

SEÇÃO: A TRÍADE DA PERSONALIDADE (O "EU" CENTRAL)

FOCO DESTA SEÇÃO:
- Sol em {request.sunSign} na Casa {request.sunHouse} (Essência)
- Lua em {request.moonSign} na Casa {request.moonHouse} (Emoção)
- Ascendente em {request.ascendant} (Máscara)

INSTRUÇÃO: Analise a combinação de Sol (Essência), Lua (Emoção) e Ascendente (Máscara). Não leia separadamente. Explique como eles conversam, as tensões e harmonias entre eles.

EXEMPLO DE PROFUNDIDADE ESPERADA:
"Enquanto o seu Sol em Áries impulsiona você a liderar e buscar desafios rápidos, sua Lua em Touro puxa o freio de mão, exigindo segurança e conforto antes de qualquer risco. Isso cria um conflito interno: uma parte de você quer acelerar (Áries), mas a sua alma precisa de garantias (Touro). Seu Ascendente em Virgem entra aqui como o gerente que tenta organizar esse caos..."

Agora escreva a análise para este nativo, com no mínimo 3 parágrafos densos e conectados."""
        else:
            prompt = f"""{full_context}

SECTION: THE PERSONALITY TRIAD (THE CENTRAL "SELF")

FOCUS OF THIS SECTION:
- Sun in {request.sunSign} in House {request.sunHouse} (Essence)
- Moon in {request.moonSign} in House {request.moonHouse} (Emotion)
- Ascendant in {request.ascendant} (Mask)

INSTRUCTION: Analyze the combination of Sun (Essence), Moon (Emotion) and Ascendant (Mask). Don't read them separately. Explain how they converse, the tensions and harmonies between them.

Now write the analysis for this native, with at least 3 dense and connected paragraphs."""
    
    elif section == 'roots':
        title = "Raízes e Vida Privada" if lang == 'pt' else "Roots and Private Life"
        ic_sign = request.icSign or "não informado"
        if lang == 'pt':
            prompt = f"""{full_context}

SEÇÃO: RAÍZES E VIDA PRIVADA (O PASSADO)

FOCO DESTA SEÇÃO:
- Lua em {request.moonSign} na Casa {request.moonHouse}
- Fundo do Céu (IC/Casa 4) em {ic_sign}
- Saturno em {request.saturnSign or 'não informado'} (estrutura familiar)

INSTRUÇÃO: Descreva o clima emocional da infância e a imagem interna da família. Como isso moldou a forma como a pessoa busca segurança hoje?

EXEMPLO DE PROFUNDIDADE ESPERADA:
"Com o Fundo do Céu em Aquário, suas raízes podem ter sido instáveis ou pouco convencionais. Talvez você tenha sentido que 'lar' era um lugar de liberdade intelectual, mas com pouco calor físico (distanciamento). Isso faz com que hoje, na vida adulta, você precise de espaço dentro de casa para se sentir seguro..."

Agora escreva a análise para este nativo, conectando Lua, Casa 4 e Saturno."""
        else:
            prompt = f"""{full_context}

SECTION: ROOTS AND PRIVATE LIFE (THE PAST)

FOCUS OF THIS SECTION:
- Moon in {request.moonSign} in House {request.moonHouse}
- IC (House 4) in {ic_sign}
- Saturn in {request.saturnSign or 'not provided'} (family structure)

INSTRUCTION: Describe the emotional climate of childhood and the internal image of family. How did this shape the way the person seeks security today?

Now write the analysis for this native, connecting Moon, House 4 and Saturn."""
    
    elif section == 'karma':
        title = "Carma, Desafios e Evolução" if lang == 'pt' else "Karma, Challenges and Evolution"
        if lang == 'pt':
            prompt = f"""{full_context}

SEÇÃO: CARMA, DESAFIOS E EVOLUÇÃO (A MISSÃO DA ALMA)

FOCO DESTA SEÇÃO:
- Nodo Norte em {request.northNodeSign or 'não informado'} (Destino a conquistar)
- Nodo Sul em {request.southNodeSign or 'não informado'} (Zona de conforto/Passado)
- Saturno em {request.saturnSign or 'não informado'} (Mestre Kármico)
- Quíron em {request.chironSign or 'não informado'} (Ferida → Dom de Cura)

INSTRUÇÃO: Diferencie o que é zona de conforto (Nodo Sul) do que é o destino a ser conquistado (Nodo Norte). Onde está a ferida (Quíron em {request.chironSign or 'N/A'}) e como transformá-la em dom? O que Saturno exige de amadurecimento?

EXEMPLO DE PROFUNDIDADE ESPERADA:
"Seu Nodo Sul em Libra indica que, em vidas passadas ou na primeira metade desta vida, você se definiu através dos outros, sempre cedendo para manter a paz. Seu grande desafio kármico (Nodo Norte em Áries) é aprender a ser 'egoísta' no bom sentido: ter coragem de bancar suas vontades sozinho, sem esperar aprovação..."

Agora escreva a análise para este nativo, com profundidade sobre propósito de vida."""
        else:
            prompt = f"""{full_context}

SECTION: KARMA, CHALLENGES AND EVOLUTION (THE SOUL'S MISSION)

FOCUS OF THIS SECTION:
- North Node in {request.northNodeSign or 'not provided'} (Destiny to conquer)
- South Node in {request.southNodeSign or 'not provided'} (Comfort zone/Past)
- Saturn in {request.saturnSign or 'not provided'} (Karmic Master)
- Chiron in {request.chironSign or 'not provided'} (Wound → Healing Gift)

INSTRUCTION: Differentiate what is comfort zone (South Node) from what is the destiny to be conquered (North Node). Where is the wound (Chiron in {request.chironSign or 'N/A'}) and how to transform it into a gift?

Now write the analysis for this native, with depth about life purpose."""
    
    elif section == 'career':
        title = "Carreira, Vocação e Dinheiro" if lang == 'pt' else "Career, Vocation and Money"
        if lang == 'pt':
            prompt = f"""{full_context}

SEÇÃO: CARREIRA, VOCAÇÃO E DINHEIRO (O MUNDO MATERIAL)

FOCO DESTA SEÇÃO:
- Meio do Céu (MC) em {request.midheavenSign or 'não informado'} (Vocação, Reputação)
- Sol em {request.sunSign} na Casa {request.sunHouse} (Identidade profissional)
- Saturno em {request.saturnSign or 'não informado'} (Estrutura, Autoridade)
- Júpiter em {request.jupiterSign or 'não informado'} (Expansão, Sorte nos negócios)
- Marte em {request.marsSign or 'não informado'} (Ação, Ambição)

INSTRUÇÃO: Diferencie o "ganha-pão" (trabalho diário) da "missão de vida" (MC/Casa 10). Como a pessoa pode construir autoridade e reconhecimento? Onde está a expansão financeira (Júpiter)?

EXEMPLO DE PROFUNDIDADE ESPERADA:
"Sua Casa 6 em Gêmeos sugere que sua rotina precisa ser dinâmica, com comunicação e movimento; tédio é seu inimigo no escritório. Porém, seu Meio do Céu em Escorpião aponta para uma vocação mais profunda: você veio para transformar, investigar ou lidar com crises alheias..."

Agora escreva a análise vocacional completa para este nativo."""
        else:
            prompt = f"""{full_context}

SECTION: CAREER, VOCATION AND MONEY (THE MATERIAL WORLD)

FOCUS OF THIS SECTION:
- Midheaven (MC) in {request.midheavenSign or 'not provided'} (Vocation, Reputation)
- Sun in {request.sunSign} in House {request.sunHouse} (Professional identity)
- Saturn in {request.saturnSign or 'not provided'} (Structure, Authority)
- Jupiter in {request.jupiterSign or 'not provided'} (Expansion, Business luck)
- Mars in {request.marsSign or 'not provided'} (Action, Ambition)

INSTRUCTION: Differentiate the "livelihood" (daily work) from the "life mission" (MC/House 10). How can the person build authority and recognition?

Now write the complete vocational analysis for this native."""
    
    elif section == 'love':
        title = "O Jeito de Amar e Relacionar" if lang == 'pt' else "The Way of Loving and Relating"
        if lang == 'pt':
            prompt = f"""{full_context}

SEÇÃO: O JEITO DE AMAR E RELACIONAR

FOCO DESTA SEÇÃO:
- Vênus em {request.venusSign or 'não informado'} (O que deseja no amor)
- Marte em {request.marsSign or 'não informado'} (Como conquista)
- Lua em {request.moonSign} na Casa {request.moonHouse} (Necessidades emocionais)
- Ascendente em {request.ascendant} → Descendente (Casa 7) = tipo de parceiro que atrai
- Netuno em {request.neptuneSign or 'não informado'} (Idealização amorosa)

INSTRUÇÃO: Contraste o que a pessoa deseja no amor (Vênus) com como ela age para conquistar (Marte). O que a Lua precisa emocionalmente? O que o Descendente (Casa 7) revela sobre o tipo de parceiro que atrai?

EXEMPLO DE PROFUNDIDADE ESPERADA:
"Você tem Vênus em Capricórnio, o que significa que leva o amor muito a sério; busca estrutura, status e compromisso de longo prazo. Porém, seu Marte em Sagitário faz você agir de forma oposta: conquista fazendo piada, sendo aventureiro e livre. Isso pode confundir os parceiros..."

Agora escreva a análise amorosa e relacional completa para este nativo."""
        else:
            prompt = f"""{full_context}

SECTION: THE WAY OF LOVING AND RELATING

FOCUS OF THIS SECTION:
- Venus in {request.venusSign or 'not provided'} (What desires in love)
- Mars in {request.marsSign or 'not provided'} (How conquers)
- Moon in {request.moonSign} in House {request.moonHouse} (Emotional needs)
- Ascendant in {request.ascendant} → Descendant (House 7) = type of partner attracted
- Neptune in {request.neptuneSign or 'not provided'} (Love idealization)

INSTRUCTION: Contrast what the person desires in love (Venus) with how they act to conquer (Mars). What does the Moon need emotionally? What does the Descendant reveal about the type of partner they attract?

Now write the complete love and relationship analysis for this native."""
    
    elif section == 'synthesis':
        title = "Síntese e Orientações" if lang == 'pt' else "Synthesis and Guidance"
        if lang == 'pt':
            prompt = f"""{full_context}

SEÇÃO: SÍNTESE FINAL E ORIENTAÇÕES

INTEGRAÇÃO DE TODOS OS ELEMENTOS:
Use TODOS os dados do mapa astral acima para criar uma síntese coerente.

INSTRUÇÃO: Faça uma síntese integradora de TODO o mapa. Considere:
1. A Tríade Central (Sol, Lua, Ascendente)
2. Os Planetas Pessoais (Mercúrio, Vênus, Marte)
3. Os Mestres Sociais (Júpiter, Saturno)
4. As Forças Transpessoais (Urano, Netuno, Plutão)
5. O Eixo Kármico (Nodos Lunares, Quíron)

Quais são os 3-5 temas centrais da vida desta pessoa? Quais os maiores desafios e potenciais? Termine com orientações práticas e esperançosas.

Escreva uma síntese profunda que conecte TODOS os elementos do mapa em uma narrativa coerente sobre quem é {request.name}, sua missão e seu potencial."""
        else:
            prompt = f"""{full_context}

SECTION: FINAL SYNTHESIS AND GUIDANCE

INTEGRATION OF ALL ELEMENTS:
Use ALL birth chart data above to create a coherent synthesis.

INSTRUCTION: Make an integrating synthesis of the WHOLE chart. Consider:
1. The Central Triad (Sun, Moon, Ascendant)
2. The Personal Planets (Mercury, Venus, Mars)
3. The Social Masters (Jupiter, Saturn)
4. The Transpersonal Forces (Uranus, Neptune, Pluto)
5. The Karmic Axis (Lunar Nodes, Chiron)

What are the 3-5 central themes of this person's life? What are the biggest challenges and potentials? End with practical and hopeful guidance.

Write a deep synthesis that connects ALL chart elements into a coherent narrative about who {request.name} is, their mission and potential."""
    
    else:
        title = "Análise Astrológica"
        prompt = f"Análise astrológica para {request.name}"
    
    return title, prompt


@router.post("/full-birth-chart/section", response_model=FullBirthChartResponse)
def generate_birth_chart_section(
    request: FullBirthChartRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Gera uma seção específica do Mapa Astral Completo.
    
    Seções disponíveis:
    - triad: A Tríade da Personalidade (Sol, Lua, Ascendente)
    - roots: Raízes e Vida Privada (Casa 4, Lua)
    - karma: Carma, Desafios e Evolução (Nodos, Saturno, Quíron)
    - career: Carreira, Vocação e Dinheiro (MC, Casa 10)
    - love: O Jeito de Amar e Relacionar (Vênus, Marte, Casa 7)
    - synthesis: Síntese Final e Orientações
    """
    try:
        if not request.section:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Especifique uma seção: triad, roots, karma, career, love, synthesis"
            )
        
        rag_service = get_rag_service()
        lang = request.language or 'pt'
        
        # Obter prompt mestre e prompt da seção
        master_prompt = _get_master_prompt(lang)
        title, section_prompt = _generate_section_prompt(request, request.section)
        
        # Buscar contexto relevante do RAG
        search_queries = {
            'triad': f"Sol Lua Ascendente personalidade {request.sunSign} {request.moonSign} {request.ascendant}",
            'roots': f"Casa 4 Lua infância família raízes {request.moonSign} {request.icSign or ''}",
            'karma': f"Nodo Norte Sul karma evolução {request.northNodeSign or ''} Saturno Quíron propósito vida",
            'career': f"Meio do Céu Casa 10 carreira vocação profissão {request.midheavenSign or ''} Saturno",
            'love': f"Vênus Marte amor relacionamento Casa 7 {request.venusSign or ''} {request.marsSign or ''}",
            'synthesis': f"síntese mapa astral integração {request.sunSign} {request.moonSign} {request.ascendant}"
        }
        
        query = search_queries.get(request.section, "interpretação mapa astral")
        rag_results = rag_service.search(query, top_k=10)
        
        # Preparar contexto
        context_text = "\n\n".join([doc['text'] for doc in rag_results[:8]])
        
        # Gerar interpretação com Groq
        if rag_service.groq_client:
            try:
                from groq import Groq
                
                full_prompt = f"""{master_prompt}

---

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_text}

---

{section_prompt}"""
                
                chat_completion = rag_service.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": master_prompt},
                        {"role": "user", "content": f"{section_prompt}\n\nCONTEXTO ASTROLÓGICO:\n{context_text[:3000]}"}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.7,
                    max_tokens=1500,
                    top_p=0.9,
                )
                
                content = chat_completion.choices[0].message.content
                
                return FullBirthChartResponse(
                    section=request.section,
                    title=title,
                    content=content,
                    generated_by="groq"
                )
                
            except Exception as e:
                print(f"[ERROR] Erro ao gerar com Groq: {e}")
        
        # Fallback
        return FullBirthChartResponse(
            section=request.section,
            title=title,
            content=f"Não foi possível gerar a análise no momento. Por favor, tente novamente.",
            generated_by="error"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar seção do mapa: {str(e)}"
        )


@router.post("/full-birth-chart/all", response_model=FullBirthChartSectionsResponse)
def generate_full_birth_chart(
    request: FullBirthChartRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Gera o Mapa Astral Completo com todas as seções.
    
    Esta é a análise mais completa do sistema, gerando:
    1. A Tríade da Personalidade
    2. Raízes e Vida Privada
    3. Carma, Desafios e Evolução
    4. Carreira, Vocação e Dinheiro
    5. O Jeito de Amar e Relacionar
    6. Síntese Final e Orientações
    """
    try:
        sections_to_generate = ['triad', 'roots', 'karma', 'career', 'love', 'synthesis']
        generated_sections = []
        
        for section in sections_to_generate:
            request.section = section
            try:
                result = generate_birth_chart_section(request, authorization)
                generated_sections.append(result)
            except Exception as e:
                print(f"[WARNING] Erro ao gerar seção {section}: {e}")
                lang = request.language or 'pt'
                title, _ = _generate_section_prompt(request, section)
                generated_sections.append(FullBirthChartResponse(
                    section=section,
                    title=title,
                    content="Esta seção não pôde ser gerada no momento." if lang == 'pt' else "This section could not be generated at this time.",
                    generated_by="error"
                ))
        
        lang = request.language or 'pt'
        birth_data = f"{request.birthDate} às {request.birthTime} em {request.birthPlace}" if lang == 'pt' else f"{request.birthDate} at {request.birthTime} in {request.birthPlace}"
        
        return FullBirthChartSectionsResponse(
            name=request.name,
            birthData=birth_data,
            sections=generated_sections,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar mapa astral completo: {str(e)}"
        )

"""
API endpoints para interpretação astrológica usando RAG.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.services.rag_service import get_rag_service
from app.services.transits_calculator import calculate_future_transits
from app.api.auth import get_current_user
from app.models.database import BirthChart

router = APIRouter()


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
            use_groq=request.use_groq if request.use_groq is not None else True
        )
        
        return InterpretationResponse(**interpretation)
        
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
        
        results = rag_service.search(query, top_k=top_k)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na busca: {str(e)}"
        )


@router.get("/interpretation/status")
def get_rag_status():
    """Retorna o status do sistema RAG."""
    try:
        rag_service = get_rag_service()
        
        has_index = rag_service.embeddings is not None and len(rag_service.documents) > 0
        
        return {
            "available": has_index,
            "document_count": len(rag_service.documents) if has_index else 0,
            "has_dependencies": rag_service.model is not None,
            "has_groq": rag_service.groq_client is not None
        }
    except Exception as e:
        return {
            "available": False,
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
            transit_date = datetime.fromisoformat(transit['date'])
            
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
            
            # Formatar timeframe
            from datetime import timedelta
            end_date = transit_date + timedelta(days=90)  # Aproximação de 3 meses
            months_pt = [
                'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
            ]
            timeframe = f"{months_pt[transit_date.month - 1]} {transit_date.year} - {months_pt[end_date.month - 1]} {end_date.year}"
            
            formatted_transits.append({
                'id': f"{transit['planet']}-{transit['natal_point']}-{transit_date.isoformat()}",
                'type': transit_type,
                'title': transit['title'],
                'planet': transit['planet'],
                'timeframe': timeframe,
                'description': transit['description'],
                'isActive': transit['is_active'],
                'date': transit['date'],
                'aspect_type': transit['aspect_type'],
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
    
    # Criar prompt para o Groq
    system_prompt = """Você é um astrólogo experiente especializado em interpretação de trânsitos astrológicos.
Sua tarefa é criar interpretações precisas, práticas e úteis sobre trânsitos baseadas nos documentos fornecidos.

Diretrizes:
- Use APENAS as informações dos documentos fornecidos como base
- Seja claro, objetivo e prático
- Mantenha o tom profissional mas acessível
- Foque em insights aplicáveis à vida do usuário
- Explique o significado astrológico do trânsito
- Forneça orientações práticas sobre como navegar este período"""
    
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
    
    user_prompt = f"""Com base nos seguintes documentos sobre astrologia, crie uma interpretação detalhada e prática sobre este trânsito:

Trânsito: {transit.get('planet', '')} em {aspect_name_pt} com {natal_point_display}
Signo natal: {transit.get('natal_sign', '')}
Período: {transit.get('date', '')}

Documentos de referência:
{context_text}

Por favor, crie uma interpretação que:
1. Explique o significado astrológico deste trânsito específico
2. Descreva como este trânsito afeta a área de vida relacionada ao {natal_point_display}
3. Forneça insights práticos e orientações sobre como navegar este período
4. Seja baseada exclusivamente nas informações dos documentos fornecidos
5. Seja clara, útil e aplicável à vida cotidiana

Interpretação:"""
    
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
            model="llama-3.1-70b-versatile",
            temperature=0.7,
            max_tokens=400,
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


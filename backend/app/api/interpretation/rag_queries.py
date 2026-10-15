"""Interpretações por consulta ao RAG: genérica, aspectos e conselho diário.

Rotas recuperadas do commit 7bd56d5 (sumiram do backend numa merge, mas o front ainda as chama).
Política de acesso (autenticação e rate limit) é aplicada em app/api/interpretation/__init__.py.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.interpretation.solar_return import InterpretationResponse, SourceItem
from app.services.rag_service_fastembed import get_rag_service
from app.services.text_cleanup import deduplicate_text

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



@router.post("/interpretation", response_model=InterpretationResponse)
def get_interpretation(
    request: InterpretationRequest
):
    """
    Obtém interpretação astrológica baseada nos parâmetros fornecidos.
    
    NOTA: Para interpretação de planetas, use o endpoint específico /interpretation/planet
    que usa um prompt prático e menos técnico.
    
    Este endpoint é para queries genéricas ou aspectos, não para planetas individuais.
    
    Exemplos de uso:
    - aspect="conjunção Sol Lua" → Interpretação de aspecto
    - custom_query="ascendente em aquário" → Query customizada
    """
    try:
        # Redirecionar interpretações de planetas para o endpoint específico
        if request.planet and request.sign and not request.custom_query and not request.aspect:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para interpretação de planetas, use o endpoint específico: /api/interpretation/planet"
            )
        
        rag_service = get_rag_service()
        
        interpretation = rag_service.get_interpretation(
            planet=request.planet,
            sign=request.sign,
            house=request.house,
            aspect=request.aspect,
            custom_query=request.custom_query,
            use_groq=request.use_groq,
            category='astrology'  # Garantir que use apenas documentos de astrologia
        )
        
        # Converter sources para o formato correto
        sources_list = []
        for src in interpretation.get('sources', []):
            if isinstance(src, dict):
                sources_list.append(SourceItem(
                    source=src.get('source', 'unknown'),
                    page=src.get('page', 1),
                    relevance=src.get('relevance') or src.get('score')
                ))
        
        # Aplicar filtro de deduplicação na interpretação
        interpretation_text = interpretation['interpretation']
        if interpretation_text:
            interpretation_text = deduplicate_text(interpretation_text)
        
        return InterpretationResponse(
            interpretation=interpretation_text,
            sources=sources_list,
            query_used=interpretation['query_used'],
            generated_by=interpretation.get('generated_by', 'unknown')
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Erro na interpretação: {e}")
        return InterpretationResponse(
            interpretation=f"Erro ao processar interpretação: {str(e)}",
            sources=[],
            query_used=request.custom_query or f"{request.planet} {request.sign}".strip(),
            generated_by="error"
        )



class AspectInterpretationRequest(BaseModel):
    planet1: str
    planet2: str
    aspect: str


@router.post("/interpretation/aspect")
def get_aspect_interpretation(
    request: AspectInterpretationRequest
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
            use_groq=True,
            category='astrology'  # Garantir que use apenas documentos de astrologia
        )
        
        # Aplicar filtro de deduplicação na interpretação
        interpretation_text = interpretation['interpretation']
        if interpretation_text:
            interpretation_text = deduplicate_text(interpretation_text)
        
        return {
            "interpretation": interpretation_text,
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
    request: DailyAdviceRequest
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
            use_groq=True,
            category='astrology'  # Garantir que use apenas documentos de astrologia
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
                    # Aplicar filtro de deduplicação
                    interpretation_text = deduplicate_text(interpretation_text)
                    interpretation['interpretation'] = interpretation_text
                    interpretation['generated_by'] = 'groq'
            except Exception as e:
                print(f"[WARNING] Erro ao gerar com Groq: {e}")
        
        # Aplicar filtro de deduplicação na interpretação
        interpretation_text = interpretation['interpretation']
        if interpretation_text:
            interpretation_text = deduplicate_text(interpretation_text)
        
        return {
            "interpretation": interpretation_text,
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

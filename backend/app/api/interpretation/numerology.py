from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from app.api.dependencies import llm_rate_limit
from app.api.interpretation.solar_return import SourceItem
from app.core.database import get_db
from app.models.database import BirthChart


router = APIRouter()


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



@router.post("/numerology/interpretation", dependencies=[Depends(llm_rate_limit)], response_model=NumerologyInterpretationResponse)
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
        from app.services.numerology_interpretation.context import describe_master_numbers, retrieve_context
        from app.services.numerology_interpretation.prompts import SYSTEM_PROMPT, build_user_prompt
        from app.services.numerology_interpretation.queries import build_rag_queries
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
        queries = build_rag_queries(numerology_map)
        context_text, unique_docs = retrieve_context(rag_service, queries)
        master_note = describe_master_numbers(numerology_map)

        system_prompt = SYSTEM_PROMPT
        user_prompt = build_user_prompt(numerology_map, master_note, context_text)
        
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



@router.post("/numerology/birth-grid-quantities", dependencies=[Depends(llm_rate_limit)], response_model=BirthGridQuantitiesResponse)
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

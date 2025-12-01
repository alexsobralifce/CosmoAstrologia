"""
API routes para o RAG Service.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.rag_service import get_rag_service

router = APIRouter()


class InterpretationRequest(BaseModel):
    """Request para interpretação astrológica."""
    planet: Optional[str] = None
    sign: Optional[str] = None
    house: Optional[int] = None
    aspect: Optional[str] = None
    custom_query: Optional[str] = None
    use_groq: bool = True
    top_k: int = 8
    category: Optional[str] = None  # 'astrology' ou 'numerology'


class SearchRequest(BaseModel):
    """Request para busca de documentos."""
    query: str
    top_k: int = 5
    expand_query: bool = False
    category: Optional[str] = None


@router.post("/interpretation")
async def get_interpretation(request: InterpretationRequest):
    """
    Obtém interpretação astrológica ou numerológica usando RAG.
    """
    try:
        rag_service = get_rag_service()
        
        if not rag_service:
            raise HTTPException(
                status_code=503,
                detail="Serviço RAG não disponível. O índice ainda não foi construído ou as dependências não estão instaladas."
            )
        
        interpretation = rag_service.get_interpretation(
            planet=request.planet,
            sign=request.sign,
            house=request.house,
            aspect=request.aspect,
            custom_query=request.custom_query,
            use_groq=request.use_groq,
            top_k=request.top_k,
            category=request.category
        )
        
        return interpretation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter interpretação: {str(e)}")


@router.post("/search")
async def search_documents(request: SearchRequest):
    """
    Busca documentos relevantes na base de conhecimento.
    """
    try:
        rag_service = get_rag_service()
        
        if not rag_service:
            raise HTTPException(
                status_code=503,
                detail="Serviço RAG não disponível."
            )
        
        results = rag_service.search(
            query=request.query,
            top_k=request.top_k,
            expand_query=request.expand_query,
            category=request.category
        )
        
        return {
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")


@router.get("/search")
async def search_documents_get(
    query: str = Query(..., description="Query de busca"),
    top_k: int = Query(5, ge=1, le=50, description="Número de resultados"),
    expand_query: bool = Query(False, description="Expandir query"),
    category: Optional[str] = Query(None, description="Categoria: 'astrology' ou 'numerology'")
):
    """
    Busca documentos relevantes (versão GET).
    """
    try:
        rag_service = get_rag_service()
        
        if not rag_service:
            raise HTTPException(
                status_code=503,
                detail="Serviço RAG não disponível."
            )
        
        results = rag_service.search(
            query=query,
            top_k=top_k,
            expand_query=expand_query,
            category=category
        )
        
        return {
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")


@router.get("/status")
async def get_status():
    """
    Retorna o status do sistema RAG.
    """
    try:
        rag_service = get_rag_service()
        
        if not rag_service:
            return {
                "available": False,
                "message": "Serviço RAG não disponível. O índice ainda não foi construído ou as dependências não estão instaladas.",
                "has_dependencies": False,
                "has_index": False,
                "has_groq": False,
                "document_count": 0
            }
        
        # Verificar se tem índice
        has_index = False
        has_groq = False
        document_count = 0
        
        # Verificar se tem índice (FastEmbed usa documents e embeddings_matrix)
        if hasattr(rag_service, 'documents') and rag_service.documents:
            has_index = len(rag_service.documents) > 0
            if has_index:
                document_count = len(rag_service.documents)
        
        has_groq = rag_service.groq_client is not None
        
        return {
            "available": has_index,
            "has_dependencies": True,
            "has_index": has_index,
            "has_groq": has_groq,
            "document_count": document_count,
            "implementation": "fastembed"
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            "has_dependencies": False,
            "has_index": False,
            "has_groq": False,
            "document_count": 0
        }


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "rag-service"
    }


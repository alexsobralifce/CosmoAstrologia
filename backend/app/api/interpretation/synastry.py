import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional


logger = logging.getLogger(__name__)
router = APIRouter()


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
async def get_synastry_interpretation(request: SynastryRequest):
    """
    Sinastria entre dois signos: busca as características de cada signo no RAG
    (app.services.synastry.context) e pede a interpretação à LLM (prompts em .prompts).
    """
    try:
        from app.core.config import settings
        from app.services.ai_provider_service import get_ai_provider
        from app.services.rag_service_fastembed import get_rag_service
        from app.services.synastry.context import InsufficientContextError, build_synastry_context
        from app.services.synastry.prompts import build_prompts

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

        try:
            context = build_synastry_context(rag_service, sign1, sign2, lang)
        except InsufficientContextError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

        system_prompt, user_prompt = build_prompts(lang, sign1, sign2, context.full_context)
        interpretation = provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=4000,
            model=getattr(settings, 'GROQ_MODEL', 'llama-3.1-8b-instant')
        )

        return SynastryResponse(
            interpretation=interpretation.strip(),
            generated_by=provider.get_provider_name(),
            sign1_info=context.sign1_raw[:500] if context.sign1_raw else None,
            sign2_info=context.sign2_raw[:500] if context.sign2_raw else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erro ao gerar interpretação de sinastria")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar interpretação de sinastria: {str(e)}"
        )

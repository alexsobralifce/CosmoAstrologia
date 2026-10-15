from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Header
from fastapi import status
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


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

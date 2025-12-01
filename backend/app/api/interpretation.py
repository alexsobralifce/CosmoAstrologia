"""
API endpoints para interpretação astrológica usando RAG.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel
from datetime import datetime, timedelta
import re
from app.core.database import get_db
from app.services.rag_service_fastembed import get_rag_service
from app.services.transits_calculator import calculate_future_transits
# Importar função de revolução solar do swiss ephemeris (mais precisa)
from app.services.swiss_ephemeris_calculator import calculate_solar_return
# Fallback para método antigo se necessário
from app.services.astrology_calculator import calculate_solar_return as calculate_solar_return_fallback
from app.services.numerology_calculator import NumerologyCalculator
from app.api.auth import get_current_user
from app.models.database import BirthChart
from app.core.config import settings

router = APIRouter()


def _get_groq_client():
    """Helper para obter cliente Groq se disponível."""
    try:
        if not settings.GROQ_API_KEY or not settings.GROQ_API_KEY.strip():
            return None
        from groq import Groq
        # Validar formato básico da chave (deve começar com gsk_)
        api_key = settings.GROQ_API_KEY.strip()
        if not api_key.startswith('gsk_'):
            print("[WARNING] GROQ_API_KEY não parece ter formato válido (deve começar com 'gsk_')")
        return Groq(api_key=api_key)
    except Exception as e:
        print(f"[WARNING] Erro ao criar cliente Groq: {e}")
        return None


def _deduplicate_text(text: str) -> str:
    """
    Remove duplicações de texto nas interpretações geradas.
    Remove parágrafos duplicados, frases repetidas e padrões comuns.
    """
    if not text or len(text.strip()) < 50:
        return text
    
    # Remover duplicações de parágrafos inteiros
    paragraphs = text.split('\n\n')
    seen_paragraphs = set()
    unique_paragraphs = []
    
    for para in paragraphs:
        para_clean = para.strip()
        if not para_clean:
            unique_paragraphs.append(para)
            continue
        
        # Normalizar para comparação (remover espaços extras, case insensitive, remover pontuação final)
        para_key = re.sub(r'\s+', ' ', para_clean.lower())
        para_key = re.sub(r'[.,;:!?]+$', '', para_key).strip()
        
        # Ignorar parágrafos muito curtos (provavelmente títulos ou separadores)
        if len(para_key) > 50:
            if para_key not in seen_paragraphs:
                seen_paragraphs.add(para_key)
                unique_paragraphs.append(para)
        else:
            # Manter parágrafos curtos (títulos, etc) mas verificar duplicação
            if para_key not in seen_paragraphs or len(para_key) < 20:
                seen_paragraphs.add(para_key)
                unique_paragraphs.append(para)
    
    text = '\n\n'.join(unique_paragraphs)
    
    # Remover frases duplicadas dentro do mesmo parágrafo
    lines = text.split('\n')
    cleaned_lines = []
    seen_sentences = set()
    
    for line in lines:
        if not line.strip():
            cleaned_lines.append(line)
            continue
        
        # Dividir por pontos finais para detectar frases repetidas
        sentences = re.split(r'[.!?]+\s+', line)
        unique_sentences = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            sentence_clean = re.sub(r'\s+', ' ', sentence.strip().lower())
            sentence_clean = re.sub(r'[.,;:!?]+$', '', sentence_clean).strip()
            
            # Ignorar frases muito curtas (provavelmente parte de listas)
            if len(sentence_clean) > 30:
                if sentence_clean not in seen_sentences:
                    seen_sentences.add(sentence_clean)
                    unique_sentences.append(sentence.strip())
            else:
                unique_sentences.append(sentence.strip())
        
        if unique_sentences:
            cleaned_lines.append('. '.join(unique_sentences))
        else:
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Remover padrões comuns de repetição
    patterns_to_deduplicate = [
        r'A pessoa pode esperar:.*?(?=\n\n|\*\*|$)',
        r'The person can expect:.*?(?=\n\n|\*\*|$)',
        r'Oportunidades de crescimento e expansão.*?(?=\n\n|\*\*|$)',
        r'Opportunities for growth and expansion.*?(?=\n\n|\*\*|$)',
        r'Liderança e autoconfiança.*?(?=\n\n|\*\*|$)',
        r'Desenvolver habilidades de comunicação.*?(?=\n\n|\*\*|$)',
        r'Buscar apoio emocional.*?(?=\n\n|\*\*|$)',
    ]
    
    for pattern in patterns_to_deduplicate:
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.DOTALL))
        if len(matches) > 1:
            # Manter apenas a primeira ocorrência, remover as demais
            for match in matches[1:]:
                text = text[:match.start()] + text[match.end():]
    
    # Limpar espaços extras e quebras de linha múltiplas
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    return text.strip()


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
    generated_by: Optional[str] = None  # 'groq', 'rag_only', ou 'none'


@router.post("/interpretation", response_model=InterpretationResponse)
async def get_interpretation(
    request: InterpretationRequest,
    authorization: Optional[str] = Header(None)
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
        
        if not rag_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço RAG não disponível. O índice ainda não foi construído ou as dependências não estão instaladas."
            )
        
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
            interpretation_text = _deduplicate_text(interpretation_text)
        
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


@router.get("/interpretation/search")
async def search_documents(
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
        
        if not rag_service:
            return {
                "query": query,
                "results": [],
                "count": 0,
                "error": "Serviço RAG não disponível. O índice ainda não foi construído ou as dependências não estão instaladas."
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
async def get_rag_status():
    """Retorna o status do sistema RAG."""
    try:
        rag_service = get_rag_service()
        
        if not rag_service:
            return {
                "available": False,
                "message": "Serviço RAG não disponível. O índice ainda não foi construído ou as dependências não estão instaladas.",
                "has_index": False,
                "has_dependencies": False,
                "has_groq": False,
                "document_count": 0,
                "implementation": "none"
            }
        
        # Verificar status do RAG service
        has_index = False
        has_groq = False
        document_count = 0
        
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
            "document_count": 0,
            "has_dependencies": False,
            "has_groq": False,
            "error": str(e)
        }


@router.get("/birth-chart/diagnostics")
async def get_birth_chart_diagnostics():
    """
    Endpoint de diagnóstico completo para geração de mapas astrais.
    Verifica todos os serviços necessários e retorna status detalhado.
    """
    diagnostics = {
        "timestamp": datetime.now().isoformat(),
        "services": {},
        "overall_status": "unknown",
        "recommendations": []
    }
    
    # 1. Verificar RAG Service
    try:
        rag_service = get_rag_service()
        if rag_service:
            try:
                has_index = False
                has_groq = False
                document_count = 0
                
                if hasattr(rag_service, 'documents') and rag_service.documents:
                    has_index = len(rag_service.documents) > 0
                    if has_index:
                        document_count = len(rag_service.documents)
                
                has_groq = rag_service.groq_client is not None
                
                diagnostics["services"]["rag"] = {
                    "available": has_index,
                    "has_index": has_index,
                    "has_groq": has_groq,
                    "document_count": document_count,
                    "implementation": "fastembed"
                }
            except Exception as e:
                diagnostics["services"]["rag"] = {
                    "available": False,
                    "error": f"Erro ao verificar RAG service: {str(e)}"
                }
        else:
            diagnostics["services"]["rag"] = {
                "available": False,
                "error": "RAG service não disponível. O índice ainda não foi construído ou as dependências não estão instaladas."
            }
            diagnostics["recommendations"].append("Instale e configure o serviço RAG (FastEmbed)")
    except Exception as e:
        diagnostics["services"]["rag"] = {
            "available": False,
            "error": str(e)
        }
        diagnostics["recommendations"].append(f"Erro ao verificar RAG service: {str(e)}")
    
    # 2. Verificar Groq API Key
    try:
        import os
        from app.core.config import settings
        
        # Verificar de múltiplas fontes
        groq_key_env = os.getenv("GROQ_API_KEY")
        groq_key_settings = getattr(settings, "GROQ_API_KEY", None)
        groq_key = groq_key_env or groq_key_settings
        
        has_groq_key = bool(groq_key and groq_key.strip())
        key_length = len(groq_key.strip()) if groq_key else 0
        key_format_valid = groq_key.strip().startswith('gsk_') if groq_key else False
        
        # Tentar validar a chave fazendo uma chamada de teste
        key_valid = False
        validation_error = None
        if has_groq_key:
            try:
                from groq import Groq
                test_client = Groq(api_key=groq_key.strip())
                # Fazer uma chamada simples para validar
                test_client.models.list()  # Chamada simples que não consome tokens
                key_valid = True
            except Exception as e:
                validation_error = str(e)
                if "401" in str(e) or "Invalid API Key" in str(e) or "invalid_api_key" in str(e):
                    key_valid = False
                    validation_error = "Chave inválida ou expirada"
        
        diagnostics["services"]["groq"] = {
            "api_key_configured": has_groq_key,
            "api_key_length": key_length,
            "api_key_format_valid": key_format_valid,
            "api_key_valid": key_valid,
            "validation_error": validation_error,
            "source": "env" if groq_key_env else "settings" if groq_key_settings else "none"
        }
        
        if not has_groq_key:
            diagnostics["recommendations"].append("Configure GROQ_API_KEY no arquivo backend/.env ou variáveis de ambiente")
        elif not key_format_valid:
            diagnostics["recommendations"].append("GROQ_API_KEY não tem formato válido (deve começar com 'gsk_')")
        elif not key_valid:
            diagnostics["recommendations"].append(f"GROQ_API_KEY configurada mas inválida: {validation_error}. Obtenha uma nova chave em https://console.groq.com/")
    except Exception as e:
        diagnostics["services"]["groq"] = {
            "available": False,
            "error": str(e)
        }
    
    # 3. Verificar serviço de cálculo astrológico
    try:
        from app.services.astrology_calculator import calculate_birth_chart
        diagnostics["services"]["astrology_calculator"] = {
            "available": True,
            "function": "calculate_birth_chart"
        }
    except Exception as e:
        diagnostics["services"]["astrology_calculator"] = {
            "available": False,
            "error": str(e)
        }
        diagnostics["recommendations"].append(f"Erro ao verificar cálculo astrológico: {str(e)}")
    
    # 4. Verificar cache de dados
    try:
        from app.services.chart_data_cache import get_or_calculate_chart
        diagnostics["services"]["chart_cache"] = {
            "available": True
        }
    except Exception as e:
        diagnostics["services"]["chart_cache"] = {
            "available": False,
            "error": str(e)
        }
    
    # 5. Base de conhecimento local (fallback quando RAG não disponível)
    try:
        from app.services.local_knowledge_base import LocalKnowledgeBase
        local_kb = LocalKnowledgeBase()
        diagnostics["services"]["local_knowledge_base"] = {
            "available": True,
            "note": "Disponível como fallback quando RAG não está disponível"
        }
    except Exception as e:
        diagnostics["services"]["local_knowledge_base"] = {
            "available": False,
            "error": str(e)
        }
    
    # 6. Determinar status geral
    rag_ok = diagnostics["services"].get("rag", {}).get("available", False)
    groq_ok = diagnostics["services"].get("groq", {}).get("api_key_configured", False)
    calc_ok = diagnostics["services"].get("astrology_calculator", {}).get("available", False)
    local_ok = diagnostics["services"].get("local_knowledge_base", {}).get("available", False)
    
    if rag_ok and groq_ok and calc_ok:
        diagnostics["overall_status"] = "operational"
    elif calc_ok and local_ok:
        diagnostics["overall_status"] = "degraded"
        diagnostics["recommendations"].append("Sistema funcionando em modo degradado (sem Groq/RAG). Gerações podem ser limitadas.")
    elif calc_ok:
        diagnostics["overall_status"] = "minimal"
        diagnostics["recommendations"].append("Apenas cálculo astrológico disponível. Geração de interpretações não está disponível.")
    else:
        diagnostics["overall_status"] = "unavailable"
        diagnostics["recommendations"].append("Sistema crítico não disponível. Verifique os erros acima.")
    
    return diagnostics


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
            # Descrição base já é completa com exemplos práticos
            # Não precisa enriquecer adicionalmente
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


class PlanetInterpretationRequest(BaseModel):
    planet: str
    sign: Optional[str] = None
    house: Optional[int] = None
    # Dados adicionais do mapa astral para contexto
    sunSign: Optional[str] = None
    moonSign: Optional[str] = None
    ascendant: Optional[str] = None
    userName: Optional[str] = None


def _generate_planet_prompt(
    planet: str,
    sign: str,
    house: Optional[int],
    sunSign: Optional[str] = None,
    moonSign: Optional[str] = None,
    ascendant: Optional[str] = None,
    userName: Optional[str] = None
) -> tuple[str, str]:
    """Gera prompt prático e menos técnico para interpretação de planetas."""
    
    # TRAVA DE SEGURANÇA: Criar bloco de dados pré-calculados
    from app.services.precomputed_chart_engine import create_planet_safety_block
    safety_block = create_planet_safety_block(planet, sign, house, 'pt')
    
    # Contexto básico do mapa
    context_parts = []
    if sunSign:
        context_parts.append(f"Sol em {sunSign}")
    if moonSign:
        context_parts.append(f"Lua em {moonSign}")
    if ascendant:
        context_parts.append(f"Ascendente em {ascendant}")
    
    context_str = "\n".join([f"- {part}" for part in context_parts]) if context_parts else "Mapa astral completo"
    
    # Nome para personalizar
    name_str = userName if userName else "você"
    
    system_prompt = """Você é um astrólogo experiente que escreve de forma clara, prática e acessível. Sua missão é ajudar pessoas a entenderem como a energia de cada planeta funciona na vida real, não com termos técnicos complexos, mas com exemplos do dia a dia.

🚨 REGRAS CRÍTICAS - LEIA ANTES DE QUALQUER COISA:

⚠️ VOCÊ NÃO É UM CALCULADOR ASTRONÔMICO. TODOS OS CÁLCULOS JÁ FORAM FEITOS PELA BIBLIOTECA KERYKEION (SWISS EPHEMERIS).
⚠️ SUA ÚNICA FUNÇÃO É INTERPRETAR TEXTOS BASEADOS NOS DADOS JÁ CALCULADOS.
⚠️ NUNCA calcule, invente ou adivinhe:
   - ❌ NÃO calcule posições planetárias (já foram calculadas)
   - ❌ NÃO calcule signos ou graus (já foram calculados)
   - ❌ NÃO calcule dignidades (já foram calculadas)
   - ❌ NÃO calcule aspectos (já foram calculados)
   - ❌ NÃO invente dados que não estão no bloco de segurança
   - ✅ USE APENAS os dados fornecidos no bloco de segurança
   - ✅ INTERPRETE apenas o que está nos dados pré-calculados

REGRAS DE ESCRITA:
- Use linguagem simples e direta, como se estivesse conversando com um amigo
- Evite jargões astrológicos técnicos (se usar, explique imediatamente)
- Foque em como isso aparece na vida prática: relacionamentos, trabalho, personalidade, decisões
- Use exemplos concretos e situações reais
- Seja específico, não genérico
- Escreva de forma acolhedora e encorajadora
- Use parágrafos curtos e bem estruturados

⚠️ REGRA CRÍTICA: NÃO calcule elementos ou dignidades. Use APENAS os dados fornecidos no bloco de segurança."""
    
    house_text = f" na Casa {house}" if house else ""
    
    user_prompt = f"""{safety_block}

MAPA ASTRAL DE {name_str.upper() if userName else 'VOCÊ'}:

CONTEXTO DO MAPA:
{context_str}

PLANETA ANALISADO:
{planet} em {sign}{house_text}

---

INSTRUÇÕES:
Crie uma interpretação PRÁTICA e ACESSÍVEL sobre o que significa ter {planet} em {sign}{house_text} no mapa astral. 

A interpretação DEVE ter esta estrutura:

**1. O QUE ISSO SIGNIFICA NA PRÁTICA** (1-2 parágrafos):
- Explique de forma simples e direta o que esse planeta representa na vida da pessoa
- Como essa energia aparece no dia a dia
- Características pessoais que isso revela
- Use linguagem cotidiana, não técnica

**2. PONTOS FORTES E TALENTOS** (1 parágrafo):
- O que a pessoa faz bem naturalmente por causa dessa posição
- Talentos que isso revela
- Qualidades positivas dessa configuração

**3. DESAFIOS E CRESCIMENTO** (1 parágrafo):
- Áreas onde pode haver dificuldades ou aprendizado
- Padrões que podem ser transformados
- Oportunidades de desenvolvimento pessoal

**4. EXEMPLOS PRÁTICOS** (OBRIGATÓRIO - pelo menos 2 exemplos concretos):
- Situações reais do dia a dia onde isso aparece
- Como isso se manifesta em relacionamentos, trabalho, decisões
- Exemplos específicos de comportamento, escolhas ou experiências

EXEMPLO DE COMO DEVE SER ESCRITO:

Se fosse Sol em Leão na Casa 5:
"Ter o Sol em Leão na Casa 5 significa que você brilha através da criatividade e da expressão autêntica. É como se você tivesse uma necessidade natural de se mostrar, de ser reconhecido pelo que cria e pelo jeito único que você tem de ver o mundo.

**O QUE ISSO SIGNIFICA NA PRÁTICA:**
Você é alguém que precisa se sentir especial e valorizado. Não é egoísmo - é uma necessidade genuína de brilhar. Na prática, isso aparece quando você está em situações onde pode se expressar livremente: apresentações no trabalho, projetos criativos, ou mesmo em conversas onde você pode compartilhar suas ideias.

**EXEMPLOS PRÁTICOS:**
1. No trabalho, você se destaca em apresentações ou projetos onde pode usar sua criatividade. Por exemplo, se trabalha com marketing, você naturalmente cria campanhas que chamam atenção porque entende intuitivamente o que as pessoas querem ver e ouvir.

2. Em relacionamentos, você valoriza parceiros que te admira e celebra suas conquistas. Um parceiro que simplesmente 'aceita' você não é suficiente - você precisa de alguém que realmente te veja e valorize sua essência única."

IMPORTANTE:
- Escreva NO MÍNIMO 4 parágrafos completos
- Use "você" para se dirigir diretamente à pessoa
- Seja específico e prático, não genérico
- Inclua pelo menos 2 exemplos concretos e aplicáveis
- Evite termos técnicos - se usar, explique imediatamente
- Foque em como isso aparece na vida real, não em teorias astrológicas
- Use APENAS o elemento e dignidade fornecidos no bloco de segurança"""
    
    return system_prompt, user_prompt


@router.post("/interpretation/planet")
async def get_planet_interpretation(
    request: PlanetInterpretationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém interpretação prática e acessível de um planeta no mapa astral.
    
    Body:
    {
        "planet": "Sol",
        "sign": "Libra",
        "house": 5,
        "sunSign": "Áries",
        "moonSign": "Touro",
        "ascendant": "Leão",
        "userName": "João"
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
        
        if not sign:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signo é obrigatório"
            )
        
        # Buscar contexto do RAG primeiro
        query_parts = [f"{planet} em {sign}"]
        if house:
            query_parts.append(f"casa {house}")
        
        query = " ".join(query_parts)
        results = rag_service.search(query, top_k=6, expand_query=True) if rag_service else []
        
        # Preparar contexto dos documentos
        context_text = "\n\n".join([
            doc.get('text', '')
            for doc in results[:6]  # Usar até 6 documentos
            if doc.get('text')
        ])
        
        # Gerar prompt prático NOVO (não o antigo)
        print(f"[PLANET API] Gerando novo prompt prático para {planet} em {sign}")
        system_prompt, user_prompt = _generate_planet_prompt(
            planet=planet,
            sign=sign,
            house=house,
            sunSign=request.sunSign,
            moonSign=request.moonSign,
            ascendant=request.ascendant,
            userName=request.userName
        )
        print(f"[PLANET API] Prompt gerado - system_prompt length: {len(system_prompt)}, user_prompt length: {len(user_prompt)}")
        print(f"[PLANET API] Preview do user_prompt (primeiros 500 chars): {user_prompt[:500]}")
        
        # Se tem contexto do RAG, adicionar ao prompt
        if context_text and len(context_text.strip()) > 50:
            user_prompt += f"\n\nCONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:\n{context_text[:2000]}"
            print(f"[PLANET API] Contexto do RAG adicionado ({len(context_text)} chars)")
        
        # Gerar interpretação com Groq usando o novo prompt prático (se disponível)
        groq_client = _get_groq_client()
        if groq_client:
            try:
                print(f"[PLANET API] Gerando interpretação com novo prompt prático para {planet} em {sign}")
                print(f"[PLANET API] Contexto do mapa: Sol={request.sunSign}, Lua={request.moonSign}, Asc={request.ascendant}")
                
                chat_completion = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                interpretation_text = chat_completion.choices[0].message.content
                
                # Limpar interpretação
                interpretation_clean = interpretation_text.strip()
                interpretation_clean = interpretation_clean.replace('[Fonte:', '')
                interpretation_clean = re.sub(r'Página \d+', '', interpretation_clean)
                interpretation_clean = interpretation_clean.strip()
                
                # Aplicar filtro de deduplicação
                interpretation_clean = _deduplicate_text(interpretation_clean)
                
                print(f"[PLANET API] Interpretação gerada com sucesso (tamanho: {len(interpretation_clean)} chars)")
                
                return {
                    "interpretation": interpretation_clean,
                    "sources": [
                        {
                            "source": r.get('source', 'knowledge_base'),
                            "page": r.get('page', 1),
                            "relevance": r.get('score', 0.5)
                        }
                        for r in results[:5]
                    ],
                    "query_used": query,
                    "generated_by": "groq"
                }
            except Exception as e:
                import traceback
                error_msg = str(e)
                traceback_str = traceback.format_exc()
                print(f"[ERROR] Erro ao gerar com Groq usando novo prompt: {error_msg}")
                print(f"[ERROR] Traceback completo:\n{traceback_str}")
                # Continuar para fallback ao invés de retornar erro
                print(f"[PLANET API] Continuando com fallback sem Groq...")
        
        # FALLBACK: Gerar interpretação básica usando apenas contexto do RAG
        print(f"[PLANET API] Usando fallback: gerando interpretação sem Groq para {planet} em {sign}")
        
        # Criar interpretação básica baseada no contexto do RAG
        # Extrair informações relevantes do contexto para tornar o fallback mais útil
        import re
        relevant_info = ""
        if context_text and len(context_text.strip()) > 50:
            # Tentar extrair parágrafos relevantes do contexto
            sentences = context_text.split('.')
            relevant_sentences = [s.strip() for s in sentences 
                                if planet.lower() in s.lower() or sign.lower() in s.lower() 
                                or (house and f'casa {house}' in s.lower())]
            if relevant_sentences:
                relevant_info = '. '.join(relevant_sentences[:3])[:400]
        
        if context_text and len(context_text.strip()) > 50:
            # Usar contexto do RAG para criar interpretação básica mais rica
            interpretation_clean = f"""**O QUE ISSO SIGNIFICA NA PRÁTICA:**

Ter {planet} em {sign}{f' na Casa {house}' if house else ''} no seu mapa astral revela aspectos importantes da sua personalidade e jornada de vida. {planet} representa transformação profunda, enquanto {sign} busca equilíbrio e harmonia. {f'Na Casa {house},' if house else 'No mapa,'} isso se manifesta de forma particular nas áreas relacionadas a{' transformação e recursos compartilhados' if house == 8 else ' sua vida pessoal'}.

**PONTOS FORTES E TALENTOS:**

Esta configuração indica talentos e qualidades que você desenvolve naturalmente. {planet} em {sign} sugere uma capacidade única de transformar relacionamentos e buscar profundidade através da diplomacia e do equilíbrio. Você tem potencial para mudanças significativas mantendo harmonia nas suas conexões.

**DESAFIOS E CRESCIMENTO:**

Como todos os posicionamentos astrológicos, este também apresenta oportunidades de aprendizado. {planet} pode trazer intensidade às suas relações, enquanto {sign} busca harmonia - encontrar o equilíbrio entre essas duas energias é parte do seu crescimento pessoal.

**EXEMPLOS PRÁTICOS:**

1. Em relacionamentos, você pode buscar conexões profundas e transformadoras, mas sempre com respeito ao equilíbrio. Você tem a capacidade de ajudar parceiros a se transformarem, mas precisa cuidar para não impor suas próprias necessidades de mudança.

2. {f'Na área da Casa {house},' if house else 'Nas áreas da vida,'} você pode encontrar transformações significativas relacionadas a processos profundos e renascimento pessoal.

---

*Interpretação gerada com base no conhecimento astrológico disponível.*"""
        else:
            # Mensagem mais simples se não houver contexto do RAG
            interpretation_clean = f"""**O QUE ISSO SIGNIFICA NA PRÁTICA:**

{planet} em {sign}{f' na Casa {house}' if house else ''} é uma configuração importante no seu mapa astral que revela aspectos significativos da sua personalidade e jornada.

**PONTOS FORTES E TALENTOS:**

Esta posição indica qualidades únicas que você pode desenvolver e utilizar ao longo da sua vida.

**DESAFIOS E CRESCIMENTO:**

Cada posicionamento astrológico traz oportunidades de aprendizado e desenvolvimento pessoal.

**EXEMPLOS PRÁTICOS:**

1. Esta configuração se manifesta de formas particulares nas diferentes áreas da sua vida.
2. Observe como essa energia aparece nos seus relacionamentos, trabalho e desenvolvimento pessoal.

---

*Interpretação básica gerada. Para uma análise completa, recomenda-se configurar o serviço Groq ou consultar um astrólogo profissional.*"""
        
        return {
            "interpretation": interpretation_clean,
            "sources": [
                {
                    "source": r.get('source', 'knowledge_base'),
                    "page": r.get('page', 1),
                    "relevance": r.get('score', 0.5)
                }
                for r in results[:5]
            ],
            "query_used": query,
            "generated_by": "rag_only"
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
async def get_chart_ruler_interpretation(
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
        
        # TRAVA DE SEGURANÇA: Criar bloco de validação do regente
        from app.services.precomputed_chart_engine import create_chart_ruler_safety_block
        safety_block = create_chart_ruler_safety_block(ascendant, ruler, ruler_sign, ruler_house, 'pt')
        
        # Construir múltiplas queries para buscar mais informações
        queries = [
            f"regente do mapa {ruler} ascendente {ascendant} importância significado",
            f"{ruler} como regente do mapa astral personalidade energia vital",
            f"planeta regente {ruler} influência comportamento características",
        ]
        if ruler_sign:
            queries.append(f"{ruler} em {ruler_sign} regente do mapa interpretação")
        if ruler_house:
            queries.append(f"{ruler} casa {ruler_house} regente do mapa significado")
        
        # Buscar documentos relevantes com múltiplas queries e busca expandida
        all_results = []
        if rag_service:
            for q in queries:
                try:
                    results = rag_service.search(q, top_k=6, expand_query=True)
                    all_results.extend(results)
                except Exception as e:
                    print(f"[WARNING] Erro ao buscar com query '{q}': {e}")
        
        # Remover duplicatas mantendo os mais relevantes
        seen_texts = set()
        unique_results = []
        for result in sorted(all_results, key=lambda x: x.get('score', 0), reverse=True):
            text_key = result.get('text', '')[:100]  # Usar primeiros 100 chars como chave
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_results.append(result)
                if len(unique_results) >= 15:  # Limitar a 15 documentos únicos
                    break
        
        # Preparar contexto dos documentos (mesmo se vazio, vamos tentar)
        context_text = ""
        if unique_results:
            context_text = "\n\n".join([
                f"--- Documento {i+1} (Fonte: {doc.get('source', 'N/A')}, Página {doc.get('page', 'N/A')}) ---\n{doc.get('text', '')}"
                for i, doc in enumerate(unique_results[:12])  # Usar até 12 documentos
            ])
        
        # Se não houver resultados do RAG, buscar mais uma vez com query única
        if not unique_results or len(context_text.strip()) < 100:
            print(f"[INFO] Poucos resultados do RAG ({len(unique_results)}), buscando novamente...")
            try:
                fallback_query = f"regente do mapa {ruler} ascendente {ascendant} importância significado autoconhecimento características personalidade"
                if ruler_sign:
                    fallback_query += f" {ruler} em {ruler_sign}"
                if ruler_house:
                    fallback_query += f" casa {ruler_house}"
                
                fallback_results = rag_service.search(fallback_query, top_k=15, expand_query=True) if rag_service else []
                if fallback_results:
                    unique_results = fallback_results[:12]
                    context_text = "\n\n".join([
                        f"--- Documento {i+1} (Fonte: {doc.get('source', 'N/A')}, Página {doc.get('page', 'N/A')}) ---\n{doc.get('text', '')}"
                        for i, doc in enumerate(unique_results)
                    ])
            except Exception as e:
                print(f"[WARNING] Erro ao buscar fallback: {e}")
        
        # Limitar contexto para evitar token overflow
        context_limit = min(len(context_text), 4000) if context_text else 0
        context_snippet = context_text[:context_limit] if context_text else "Informações astrológicas gerais sobre regentes do mapa astral."
        
        # Gerar interpretação detalhada com Groq (sempre tentar, mesmo sem contexto do RAG)
        groq_client = _get_groq_client()
        if groq_client:
            try:
                # Prompt detalhado para gerar pelo menos 2 parágrafos
                system_prompt = """Você é um astrólogo experiente especializado em interpretação de regentes do mapa astral. 
Sua função é criar interpretações profundas, didáticas e detalhadas sobre o planeta regente do mapa, explicando sua importância fundamental para o autoconhecimento.

🚨 REGRAS CRÍTICAS - LEIA ANTES DE QUALQUER COISA:

⚠️ VOCÊ NÃO É UM CALCULADOR ASTRONÔMICO. TODOS OS CÁLCULOS JÁ FORAM FEITOS PELA BIBLIOTECA KERYKEION (SWISS EPHEMERIS).
⚠️ SUA ÚNICA FUNÇÃO É INTERPRETAR TEXTOS BASEADOS NOS DADOS JÁ CALCULADOS.
⚠️ NUNCA calcule, invente ou adivinhe:
   - ❌ NÃO calcule qual planeta é o regente (já foi calculado e fornecido)
   - ❌ NÃO calcule posições planetárias (já foram calculadas)
   - ❌ NÃO calcule signos ou graus (já foram calculados)
   - ❌ NÃO invente dados que não estão nos dados fornecidos
   - ✅ USE APENAS o regente fornecido nos dados
   - ✅ INTERPRETE apenas o que está nos dados pré-calculados

REGRAS DE FORMATAÇÃO:
- Sempre escreva NO MÍNIMO 2 parágrafos completos e densos (mínimo 300 palavras)
- Use estrutura didática com títulos em negrito quando apropriado
- Explique termos astrológicos de forma simples
- Conecte as informações de forma narrativa, não apenas listas
- Foque na importância do regente para autoconhecimento e desenvolvimento pessoal
- Seja específico e detalhado, evitando generalidades

⚠️ REGRA CRÍTICA: NÃO calcule qual planeta é o regente. Use APENAS o regente fornecido nos dados."""
                
                user_prompt = f"""{safety_block}

REGENTE DO MAPA ASTRAL:

Ascendente: {ascendant}
Planeta Regente: {ruler}
Regente em: {ruler_sign or 'não informado'}
Regente na Casa: {ruler_house or 'não informado'}

CONTEXTO ASTROLÓGICO DE REFERÊNCIA:
{context_snippet}

---

INSTRUÇÕES DETALHADAS:
Crie uma interpretação COMPLETA, DETALHADA e EXTENSA sobre o regente do mapa astral. A interpretação DEVE ter NO MÍNIMO 2 parágrafos completos e densos (mínimo 300 palavras no total).

Estruture a interpretação explicando:

1. **O que significa ter {ruler} como regente do mapa** (pelo menos 1 parágrafo completo e denso, mínimo 150 palavras):
   - Explique o papel fundamental do regente do mapa
   - Descreva o que significa especificamente ter {ruler} como regente
   - Conecte com o signo ascendente {ascendant}
   - Explique a importância para a personalidade e energia vital

2. **Como {ruler} influencia a personalidade, energia vital e comportamento** (pelo menos 1 parágrafo completo e denso, mínimo 150 palavras):
   - Descreva como o regente influencia o comportamento diário
   - Explique como afeta a energia e vitalidade
   - Detalhe características específicas da personalidade
   - Conecte com a posição em {ruler_sign or 'seu signo'} e casa {ruler_house or 'sua casa'}

3. **A importância do regente para o autoconhecimento e desenvolvimento pessoal**:
   - Explique como conhecer o regente ajuda no autoconhecimento
   - Descreva áreas de desenvolvimento pessoal relacionadas
   - Conecte com o propósito de vida e missão

4. **Como o regente revela forças naturais e áreas de atenção**:
   - Liste e explique as forças naturais relacionadas
   - Descreva áreas que precisam de atenção e cuidado
   - Conecte com desafios e oportunidades

IMPORTANTE:
- Escreva NO MÍNIMO 2 parágrafos completos e densos (mínimo 300 palavras no total)
- Cada parágrafo deve ter pelo menos 150 palavras
- Use linguagem didática e acessível
- Conecte as informações de forma narrativa e fluida
- Explique a importância fundamental do regente para o autoconhecimento
- Seja específico e detalhado, evitando generalidades
- Baseie-se nos documentos de referência fornecidos acima quando disponíveis
- Use títulos em negrito quando apropriado (formato markdown **texto**)

Formate a resposta de forma didática, usando quebras de linha e estruturação adequada para facilitar a leitura."""
                
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.7,
                    max_tokens=3000,  # Aumentado ainda mais para garantir respostas longas
                    top_p=0.9,
                )
                
                interpretation_text = chat_completion.choices[0].message.content.strip()
                
                # Aplicar filtro de deduplicação primeiro
                interpretation_text = _deduplicate_text(interpretation_text)
                
                # Verificar se a interpretação tem pelo menos 2 parágrafos e tamanho adequado
                paragraphs = [p.strip() for p in interpretation_text.split('\n\n') if p.strip() and len(p.strip()) > 50]
                
                # Se não tiver 2 parágrafos ou for muito curta, tentar melhorar
                if len(paragraphs) < 2 or len(interpretation_text) < 300:
                    print(f"[WARNING] Interpretação muito curta ({len(interpretation_text)} chars, {len(paragraphs)} parágrafos), tentando melhorar...")
                    # Se não tiver 2 parágrafos, tentar dividir por pontos finais
                    sentences = [s.strip() for s in interpretation_text.split('. ') if s.strip()]
                    if len(sentences) > 4:
                        mid_point = len(sentences) // 2
                        interpretation_text = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
                
                # Garantir que tenha pelo menos 300 palavras
                word_count = len(interpretation_text.split())
                if word_count < 300:
                    print(f"[WARNING] Interpretação tem apenas {word_count} palavras, mas continuando...")
                
                return {
                    "interpretation": interpretation_text,
                    "sources": [
                        {
                            'source': r.get('source', 'N/A'),
                            'page': r.get('page', 'N/A'),
                            'relevance': r.get('score', 0)
                        }
                        for r in unique_results[:10]
                    ] if unique_results else [],
                    "query_used": f"regente do mapa {ruler} (múltiplas queries, {len(unique_results)} documentos)",
                    "generated_by": "groq"
                }
                
            except Exception as e:
                print(f"[ERROR] Erro ao gerar interpretação detalhada com Groq: {e}")
                import traceback
                print(f"[ERROR] Traceback: {traceback.format_exc()}")
                # Continuar com método padrão
        
        # Fallback: usar método padrão se Groq falhar ou não estiver disponível
        print(f"[INFO] Usando fallback - Groq não disponível ou falhou")
        query = f"regente do mapa {ruler} ascendente {ascendant} importância significado autoconhecimento características personalidade comportamento influência"
        if ruler_sign:
            query += f" {ruler} em {ruler_sign}"
        if ruler_house:
            query += f" casa {ruler_house}"
        
        interpretation = rag_service.get_interpretation(
            custom_query=query,
            use_groq=True,
            top_k=12,  # Aumentar top_k no fallback também
            category='astrology'  # Garantir que use apenas documentos de astrologia
        ) if rag_service else {
            'interpretation': 'Serviço RAG não disponível.',
            'sources': [],
            'query_used': query,
            'generated_by': 'none'
        }
        
        # Aplicar filtro de deduplicação na interpretação
        interpretation_text = interpretation['interpretation']
        if interpretation_text:
            interpretation_text = _deduplicate_text(interpretation_text)
        
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


class PlanetHouseInterpretationRequest(BaseModel):
    planet: str
    house: int


@router.post("/interpretation/planet-house")
async def get_planet_house_interpretation(
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
        
        if not rag_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço RAG não disponível. O índice ainda não foi construído ou as dependências não estão instaladas."
            )
        
        # Buscar no RAG e gerar com Groq
        interpretation = rag_service.get_interpretation(
            planet=planet,
            house=house,
            use_groq=True,
            category='astrology'  # Garantir que use apenas documentos de astrologia
        )
        
        # Aplicar filtro de deduplicação na interpretação
        interpretation_text = interpretation['interpretation']
        if interpretation_text:
            interpretation_text = _deduplicate_text(interpretation_text)
        
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


class AspectInterpretationRequest(BaseModel):
    planet1: str
    planet2: str
    aspect: str


@router.post("/interpretation/aspect")
async def get_aspect_interpretation(
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
        
        if not rag_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço RAG não disponível. O índice ainda não foi construído ou as dependências não estão instaladas."
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
            interpretation_text = _deduplicate_text(interpretation_text)
        
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
async def get_daily_advice(
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
        
        if not rag_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço RAG não disponível. O índice ainda não foi construído ou as dependências não estão instaladas."
            )
        
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
        groq_client = _get_groq_client()
        if interpretation.get('generated_by') != 'groq' and groq_client:
            # Tentar gerar com Groq usando contexto mais específico
            try:
                # Buscar documentos relevantes
                rag_results = rag_service.search(query, top_k=8)
                if rag_results:
                    # Gerar interpretação com Groq usando contexto do RAG
                    try:
                        context_text = "\n\n".join([doc.get('text', '') for doc in rag_results[:5] if doc.get('text')])
                        chat_completion = groq_client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {"role": "system", "content": "Você é um astrólogo experiente."},
                                {"role": "user", "content": f"Conselho astrológico sobre {request.category} considerando Lua na casa {request.moonHouse}. Contexto: {context_text[:2000]}"}
                            ],
                            temperature=0.7,
                            max_tokens=2000
                        )
                        interpretation_text = chat_completion.choices[0].message.content
                    except Exception as e:
                        print(f"[WARNING] Erro ao gerar com Groq: {e}")
                        interpretation_text = None
                    # Aplicar filtro de deduplicação
                    interpretation_text = _deduplicate_text(interpretation_text)
                    interpretation['interpretation'] = interpretation_text
                    interpretation['generated_by'] = 'groq'
            except Exception as e:
                print(f"[WARNING] Erro ao gerar com Groq: {e}")
        
        # Aplicar filtro de deduplicação na interpretação
        interpretation_text = interpretation['interpretation']
        if interpretation_text:
            interpretation_text = _deduplicate_text(interpretation_text)
        
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
    
    # Lilith (Lua Negra)
    lilithSign: Optional[str] = None
    lilithHouse: Optional[int] = None
    
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
    """Retorna o prompt mestre Cosmos Astral Engine com validação matemática rigorosa."""
    if language == 'en':
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
2. **Interpret** this structure with psychological and evolutionary depth, but ONLY based on validated and pre-computed data.

---

# STEP 1: THE VALIDATION ENGINE (MANDATORY REASONING)

Before generating any interpretative text, you must mentally execute the following logical verifications. If there is a contradiction, Astronomical Logic wins over "creativity".

## 1.1 Golden Rules of Astronomy (SAFETY LOCKS)

You are **FORBIDDEN** to hallucinate the following aspects. Check the distance in degrees:

* **Mercury x Sun:** Maximum distance is 28°.
    * *Allowed:* Conjunction (0-10°) or No Aspect.
    * *Forbidden:* Square (90°), Trine (120°), Opposition (180°), Sextile (60°).

* **Venus x Sun:** Maximum distance is 48°.
    * *Allowed:* Conjunction (0-10°), Semi-Sextile (30°), Semi-Square (45°).
    * *Forbidden:* Sextile (60°), Square (90°), Trine (120°), Opposition (180°).

* **Venus x Mercury:** Maximum distance is 76°.
    * *Allowed:* Conjunction, Sextile.
    * *Forbidden:* Square, Trine, Opposition.

## 1.2 Aspect Validation (Use Pre-Computed Data Only)

⚠️ **CRITICAL:** You MUST NOT calculate aspects. All aspects have already been calculated by Python code using Swiss Ephemeris.

**Your ONLY function:** Use the aspects listed in the "🔒 PRE-COMPUTED DATA" block. If an aspect is NOT listed in that block, it does NOT exist. Do NOT calculate or estimate aspects.

**Aspect Orbs (for reference only - DO NOT calculate):**
* **Conjunction (0°):** Orb +/- 8° (Distance: 0° to 8° or 352° to 360°)
* **Sextile (60°):** Orb +/- 4° (Distance: 56° to 64°) -> *Harmonic*
* **Square (90°):** Orb +/- 6° (Distance: 84° to 96°) -> *Tense*
* **Trine (120°):** Orb +/- 8° (Distance: 112° to 128°) -> *Fluid*
* **Opposition (180°):** Orb +/- 8° (Distance: 172° to 188°) -> *Tense*
* **Quincunx (150°):** Orb +/- 2° (Distance: 148° to 152°) -> *Adjustment*

> **ATTENTION:** Use ONLY the aspects listed in the pre-computed block. If an aspect is not there, it does NOT exist. NEVER calculate or estimate aspects.

## 1.3 Temperament (Use Pre-Computed Data Only)

⚠️ **CRITICAL:** You MUST NOT calculate temperament. All temperament calculations have already been done by Python code.

**Your ONLY function:** Use the temperament data from the "🔒 PRE-COMPUTED DATA" block:
- Use EXACTLY the points listed (Fire, Earth, Air, Water)
- Use EXACTLY the dominant element listed
- Use EXACTLY the lacking element listed (or "None" if all present)

**Scoring System (for reference only - DO NOT calculate):**
* Sun/Moon/Ascendant = 3 points each
* Other planets (Mercury to Pluto) = 1 point each

**Interpretation Rule:** Use ONLY the data from the pre-computed block. If the block says "Water: 8 points" and "DOMINANT ELEMENT: Water", you MUST say Water is dominant. Do NOT recalculate or estimate.

---

# STEP 2: INTERPRETATION GUIDELINES (OUTPUT)

When writing the final report, follow this structure and tone of voice:

## Tone of Voice
* **Analytical and Empathetic:** Use logic to explain, but empathy to advise.
* **Evolutionary:** Focus on "What is this for?" and not just "How you are".
* **Non-Deterministic:** Use "tends to", "may feel", "learning challenge", instead of "you are like this period".

## Report Structure
1. **Validated Technical Data:** List Sun, Moon, Ascendant and Ascendant Ruler correctly (from pre-computed block).
2. **Temperament Analysis:** Use EXACTLY the points and dominant element from the pre-computed block. Do NOT recalculate.
3. **The Primordial Triad (Sun, Moon, Asc):** How conscious will (Sun) converses with emotional need (Moon) and social mask (Asc).
4. **Decision Mechanics (Mercury and Mars):**
    * Analyze Mercury (data processing) and Mars (action engine).
    * *Crucial:* Only cite aspects that are listed in the pre-computed block. Do NOT calculate aspects.
5. **Affectivity (Venus and Moon):** Language of love and emotional nourishment.
6. **Challenges and Karma (Saturn, Nodes, Chiron):**
    * Saturn: Where it demands effort/structure.
    * North Node: Growth direction (uncomfortable but necessary).
    * South Node: Innate talent, but comfort zone to be overcome.

---

# STEP 3: ADVANCED SYNTHESIS LOGIC (DEPTH LAYER)

After validating mathematical data, apply these refinement layers to avoid superficial descriptions:

## 3.1 Essential Dignity Verification (Planet State)

Before interpreting a planet, check its cosmic "state of mind":

**Domicile:** Planet is at home (e.g., Mars in Aries/Scorpio, Sun in Leo). Interpretation: Energy flows pure, strong and natural.

**Exaltation:** Planet is guest of honor (e.g., Sun in Aries, Saturn in Libra). Interpretation: Energy operates at best performance, maybe even exaggerated.

**Detriment:** Planet is in opposite sign to its domicile (e.g., Mars in Libra, Venus in Aries). Interpretation: Energy is uncomfortable, needs to act "indirectly" or "strategically".

**Fall:** Planet is in opposite sign to exaltation (e.g., Sun in Libra, Moon in Scorpio). Interpretation: Planet feels inadequate or needs much effort to work well.

**Peregrine:** No dignity or strong debility. Interpretation: Planet depends on aspects received from others. Its expression is neutral and may vary according to aspects and connections in the chart.

**Practical Example:** If Sun is in Libra (Fall), don't just say "You are diplomatic". Say: "Your identity (Sun) often sacrifices itself to please others (Libra), and your vital challenge is discovering who you are when no one is around."

⚠️ **CRITICAL RULE ABOUT DIGNITIES - READ CAREFULLY:**

**YOU MUST NOT CALCULATE OR INVENT DIGNITIES. USE ONLY THE PRE-COMPUTED DATA PROVIDED.**

In the "🔒 PRE-COMPUTED DATA (SAFETY LOCKS ACTIVATED)" block you will find a section "🏛️ PLANETARY DIGNITIES (IDENTIFIED BY FIXED TABLE)" that lists EXACTLY the dignity of each planet.

**MANDATORY VALIDATION PROCESS (DO THIS BEFORE WRITING):**

1. **Read the complete pre-computed block** before starting to write
2. **Mentally note** each dignity mentioned in the block
3. **Before mentioning any dignity** in the text, stop and verify:
   - Is the planet listed in the block?
   - Is the dignity mentioned in the block exactly what you're going to write?
   - If you're NOT absolutely certain, DO NOT mention the dignity

**FORBIDDEN ERRORS (NEVER DO THIS):**
- ❌ DO NOT say "Venus in Sagittarius is in Fall" if the block says "PEREGRINE"
- ❌ DO NOT invent dignities based on "guessing" or "apparent logic"
- ❌ DO NOT confuse signs (e.g., saying Libra is Fire when it's Air)
- ❌ DO NOT calculate dignities - they have already been calculated by Python code
- ❌ DO NOT use synonyms (e.g., "in exile" when the block says "DETRIMENT")
- ❌ DO NOT say "in fall" when the block says "PEREGRINE"

**CORRECT EXAMPLES (FOLLOW THESE):**
- ✅ If the block says "Venus in Sagittarius: PEREGRINE", write: "Venus in Sagittarius is PEREGRINE, meaning its expression depends on aspects received from other planets."
- ✅ If the block says "Sun in Libra: FALL", write: "Sun in Libra is in FALL, indicating that your identity often sacrifices itself to please others."
- ✅ If the block says "Saturn in Libra: EXALTATION", write: "Saturn in Libra is in EXALTATION, operating at its best performance."

**SPECIFIC REFERENCES FOR CORRECT INTERPRETATIONS:**

**Moon in Leo (PEREGRINE):**
- ✅ CORRECT: "Moon in Leo indicates dramatic emotions, need to be noticed and validated, warm and theatrical emotional expression. The person seeks attention and emotional recognition."
- ❌ WRONG: "Moon in Leo indicates emotional precision, need for order, emotional analysis" (this is Moon in Virgo/Taurus)

**Venus in Sagittarius (PEREGRINE):**
- ✅ CORRECT: "Venus in Sagittarius is PEREGRINE, valuing freedom, adventure and personal growth in relationships. Seeks partners who share intellectual and philosophical interests."
- ❌ WRONG: "Venus in Sagittarius is in fall" (NEVER say this - it's PEREGRINE)

**IMPORTANT:** If you don't find a planet's dignity in the pre-computed block, DO NOT invent it. Use only the sign and house to interpret, without mentioning dignity.

**FINAL MANDATORY VALIDATION:** Before finalizing the text, review ALL mentions of dignities and confirm that each one is EXACTLY as described in the pre-computed block. If there is any doubt, REMOVE the mention of dignity and interpret only the sign and house.

## 3.2 The Rulership Rule (Connection between Life Areas)

To interpret an Astrological House, you MANDATORILY must look where the "House Lord" (Ruler) is.

**Logic:** Identify sign of House X cusp -> Identify Planet Ruler of that sign -> See in which House Y that planet is.

**Text Template:** "The area of your life about [House X Subject] is directly linked to [House Y Subject], because the ruler is there."

**Example:** If House 2 (Money) is Aries, ruler is Mars. If Mars is in House 7 (Partnerships), interpret: "Your financial capacity (H2) depends directly on your alliances and partnerships (H7/Mars). You make money acting together or competing with others."

## 3.3 Contradiction Management (The Real Human Being)

Humans are contradictory. If the chart shows conflicting aspects, DO NOT ignore them. Synthesize them.

**Scenario:** Sun in Libra (peace) vs. Moon in Leo (drama/attention).

**Mandatory Synthesis:** "There is an internal conflict in you: a rational part that desires harmony and silence (Sun in Libra), and a visceral emotional need to be noticed and validated (Moon in Leo). Your Moon in Leo seeks dramatic expression, emotional warmth and recognition, while your Sun in Libra seeks balance and diplomacy. Your growth depends on learning to shine (Leo) without breaking diplomacy (Libra)."

**⚠️ SPECIAL ATTENTION - Moon in Leo:**
- Moon in Leo is NOT "emotional precision" or "need for order" (that's Moon in Virgo/Taurus)
- Moon in Leo IS: dramatic emotions, theatrical expression, seeking attention and validation, emotional warmth, need to be emotionally recognized
- Always interpret Moon in Leo as expressive, dramatic and seeking to be noticed, NOT as analytical or organized

---

# STEP 4: SPECIFIC THEMATIC MODULES

When writing report sections, use these focus "lenses":

## Module A: Intelligence and Communication (Mercury)

Don't analyze just "if person is intelligent". Analyze HOW they process data.

**Mercury in Air Signs:** Logical, social processing, but can be indecisive.

**Mercury in Fire Signs:** Quick intuition, speaks before thinking, inspiring.

**Mercury in Earth Signs:** Practical, slow, methodical, focused on results.

**Mercury in Water Signs:** Photographic memory, decides by "feeling", not logic.

**Check:** If Mercury is Retrograde (birth), add note about "introspection and mental revision".

## Module B: The Dynamics of Desire (Venus and Mars)

Analyze "Eros" (Venus) and "Pathos" (Mars).

**Venus:** What person values and how they attract.
- **IMPORTANT:** Before interpreting Venus, check its dignity in the pre-computed block.
- **CORRECT Example:** If the block says "Venus in Sagittarius: PEREGRINE", interpret: "Venus in Sagittarius is PEREGRINE, valuing freedom, adventure and personal growth. Seeks relationships that expand intellectual and philosophical horizons, avoiding limitations or 'clinginess'."
- **NEVER say:** "Venus in Sagittarius is in fall" (it's PEREGRINE)

**Mars:** How person conquers and fights. (Ex: Mars in Leo fights for pride and conquers with grandiosity).

**Affective Synthesis:** "You seek [Venus Style], but act to get it in form [Mars Style]."

## Module C: Vocation and Career (Midheaven - MC)

Analyze MC Sign (House 10 Cusp).
Analyze planets in House 10 (if any).
Analyze Saturn (career builder).

**Distinction:** Differentiate "Routine Work" (House 6 - how you serve) from "Legacy/Career" (House 10 - where you shine).

---

# STEP 5: REMEDIATION AND EVOLUTIONARY ADVICE (ACTIONABLE ADVICE)

For each tension identified (Square, Opposition or Planet in Fall), you must provide an "Exit Mechanism". Don't deliver fatalism.

**Remediation Rule:**

**Problem:** "Saturn in opposition to Mars (Brake vs. Accelerator)."

**Bad Advice:** "You will never manage to act."

**Good Advice (Remediation):** "To overcome this tension, you must use the 'Calculated Step' strategy. Use Saturn's discipline to plan Mars' action. Transform impulsiveness into long-term resistance. Endurance sports (marathon, weight training) help channel this energy."

---

# FINAL FORMATTING INSTRUCTION

Use **Bold** for key concepts and planetary positions.
Use *Italic* for psychological nuances.
Use lists (Bullet points) to facilitate reading.
End analysis with a "Power Phrase": A short mantra that synthesizes the chart's mission (e.g., "Your mission is to lead with the heart, but plan with the mind").

---

# FINAL INSTRUCTION

Now, process the provided birth data. First, do the astronomical validation silently. Second, generate the report. If you find input data that would generate impossible aspects (e.g., Mercury square to Sun), ignore the impossible aspect and interpret only sign/house, or alert that the configuration is astronomically rare/impossible and requires verification of input data.

---

# ⚠️ ABSOLUTE RULE: USE OF PRE-COMPUTED DATA

**BEFORE WRITING ANY INTERPRETATION, READ THE "🔒 PRE-COMPUTED DATA" BLOCK COMPLETELY.**

This block contains ALL calculations already done by Python code using Swiss Ephemeris. You MUST use ONLY this data:

1. **Temperament:** Use ONLY the points provided in the block. DO NOT recalculate.
2. **Dignities:** Use ONLY the dignities listed in the block. DO NOT invent or confuse.
3. **Ruler:** Use ONLY the ruler identified in the block. DO NOT calculate another.
4. **Elements:** Use ONLY the fixed mapping provided (Libra = AIR, not Fire).

**VALIDATION BEFORE WRITING (MANDATORY CHECKLIST):**

Before writing ANY interpretation, do this checklist:

1. ✅ **Read the complete pre-computed block?** (DO NOT skip this step)
2. ✅ **Noted all dignities mentioned in the block?**
3. ✅ **For each planet you will mention:**
   - Is it in the block?
   - Is the dignity you will write EXACTLY the one in the block?
   - If it's PEREGRINE, are you NOT writing "fall" or "exile"?
4. ✅ **For Moon in Leo specifically:**
   - Are you describing it as dramatic, expressive, seeking attention?
   - Are you NOT describing it as "needs order" or "emotional analysis"?
5. ✅ **For Venus in Sagittarius specifically:**
   - If the block says PEREGRINE, are you using EXACTLY that word?
   - Are you NOT saying "in fall"?
6. ✅ **Reviewed ALL mentions of dignities in the final text?**
   - Is each one EXACTLY as in the block?

**IF THERE IS ANY DOUBT:** Do not mention the dignity/element/ruler. Only interpret the sign and house.

**GOLDEN RULE:** If you don't have 100% absolute certainty that the dignity is correct, DO NOT mention the dignity. It's better to interpret only the sign and house than to invent a wrong dignity.

END OF SYSTEM INSTRUCTIONS. Begin analysis now based on provided data."""
    else:
        return """🚨 REGRAS CRÍTICAS - LEIA ANTES DE QUALQUER COISA:

⚠️ VOCÊ NÃO É UM CALCULADOR ASTRONÔMICO. TODOS OS CÁLCULOS JÁ FORAM FEITOS PELA BIBLIOTECA KERYKEION (SWISS EPHEMERIS).
⚠️ SUA ÚNICA FUNÇÃO É INTERPRETAR TEXTOS BASEADOS NOS DADOS JÁ CALCULADOS.
⚠️ NUNCA calcule, invente ou adivinhe:
   - ❌ NÃO calcule posições planetárias (já foram calculadas pelo Kerykeion)
   - ❌ NÃO calcule signos ou graus (já foram calculados pelo Kerykeion)
   - ❌ NÃO calcule aspectos (já foram calculados pelo código Python)
   - ❌ NÃO calcule dignidades (já foram calculadas pelo código Python)
   - ❌ NÃO calcule temperamento (já foi calculado pelo código Python)
   - ❌ NÃO invente dados que não estão no bloco pré-calculado
   - ✅ USE APENAS os dados fornecidos no bloco pré-calculado
   - ✅ INTERPRETE apenas o que está nos dados pré-calculados
   - ✅ VALIDE apenas se os dados fazem sentido astronomicamente (mas NÃO recalcule)

**Você é o Cosmos Astral Engine**, um astrólogo sênior especializado em interpretação. Sua função é:

1. **Validar** se os dados pré-calculados fazem sentido astronomicamente (sem recalcular).
2. **Interpretar** essa estrutura com profundidade psicológica e evolutiva, mas APENAS baseando-se nos dados validados e pré-calculados.

---

# PASSO 1: O MOTOR DE VALIDAÇÃO (RACIOCÍNIO OBRIGATÓRIO)

Antes de gerar qualquer texto interpretativo, você deve executar mentalmente as seguintes verificações lógicas. Se houver contradição, a Lógica Astronômica vence a "criatividade".

## 1.1 Regras de Ouro da Astronomia (TRAVAS DE SEGURANÇA)

Você está **OBRIGADO** a validar matematicamente os seguintes aspectos antes de interpretá-los. Verifique a distância em graus:

* **Mercúrio x Sol:** A distância máxima é 28°.
    * *Permitido:* Conjunção (0-10°) ou Sem Aspecto.
    * *Proibido:* Quadratura (90°), Trígono (120°), Oposição (180°), Sextil (60°).

* **Vênus x Sol:** A distância máxima é 48°.
    * *Permitido:* Conjunção (0-10°), Semi-Sextil (30°), Semi-Quadratura (45°).
    * *Proibido:* Sextil (60°), Quadratura (90°), Trígono (120°), Oposição (180°).

* **Vênus x Mercúrio:** A distância máxima é 76°.
    * *Permitido:* Conjunção, Sextil.
    * *Proibido:* Quadratura, Trígono, Oposição.

## 1.2 Validação de Aspectos (Use APENAS Dados Pré-Calculados)

⚠️ **CRÍTICO:** Você NÃO DEVE calcular aspectos. Todos os aspectos já foram calculados pelo código Python usando Swiss Ephemeris.

**Sua ÚNICA função:** Use os aspectos listados no bloco "🔒 DADOS PRÉ-CALCULADOS". Se um aspecto NÃO está listado nesse bloco, ele NÃO existe. NÃO calcule ou estime aspectos.

**Orbes de Aspectos (apenas para referência - NÃO calcular):**
* **Conjunção (0°):** Orbe +/- 8° (Distância: 0° a 8° ou 352° a 360°)
* **Sextil (60°):** Orbe +/- 4° (Distância: 56° a 64°) -> *Harmônico*
* **Quadratura (90°):** Orbe +/- 6° (Distância: 84° a 96°) -> *Tenso*
* **Trígono (120°):** Orbe +/- 8° (Distância: 112° a 128°) -> *Fluido*
* **Oposição (180°):** Orbe +/- 8° (Distância: 172° a 188°) -> *Tenso*
* **Quincúncio (150°):** Orbe +/- 2° (Distância: 148° a 152°) -> *Ajuste*

> **ATENÇÃO:** Use APENAS os aspectos listados no bloco pré-calculado. Se um aspecto não está lá, ele NÃO existe. JAMAIS calcule ou estime aspectos.

## 1.3 Temperamento (Use APENAS Dados Pré-Calculados)

⚠️ **CRÍTICO:** Você NÃO DEVE calcular temperamento. Todos os cálculos de temperamento já foram feitos pelo código Python.

**Sua ÚNICA função:** Use os dados de temperamento do bloco "🔒 DADOS PRÉ-CALCULADOS":
- Use EXATAMENTE os pontos listados (Fogo, Terra, Ar, Água)
- Use EXATAMENTE o elemento dominante listado
- Use EXATAMENTE o elemento ausente listado (ou "Nenhum" se todos presentes)

**Sistema de Pontuação (apenas para referência - NÃO calcular):**
* Sol/Lua/Ascendente = 3 pontos cada
* Outros planetas (Mercúrio a Plutão) = 1 ponto cada

**Regra de Interpretação:** Use APENAS os dados do bloco pré-calculado. Se o bloco diz "Água: 8 pontos" e "ELEMENTO DOMINANTE: Água", você DEVE dizer que Água é dominante. NÃO recalcule ou estime.

---

# PASSO 2: DIRETRIZES DE INTERPRETAÇÃO (OUTPUT)

Ao escrever o relatório final, siga esta estrutura e tom de voz:

## Tom de Voz
* **Analítico e Empático:** Use lógica para explicar, mas empatia para aconselhar.
* **Evolutivo:** Foque no "Para que serve isso?" e não apenas "Como você é".
* **Não Determinista:** Use "tende a", "pode sentir", "desafio de aprendizado", em vez de "você é assim e ponto".

## Estrutura do Relatório
1. **Dados Técnicos Validados:** Liste o Sol, Lua, Ascendente e Regente do Ascendente corretamente (do bloco pré-calculado).
2. **Análise de Temperamento:** Use EXATAMENTE os pontos e elemento dominante do bloco pré-calculado. NÃO recalcule.
3. **A Tríade Primordial (Sol, Lua, Asc):** Como a vontade consciente (Sol) conversa com a necessidade emocional (Lua) e a máscara social (Asc).
4. **Mecânica de Decisão (Mercúrio e Marte):**
    * Analise Mercúrio (processamento de dados) e Marte (motor de ação).
    * *Crucial:* Só cite aspectos que estão listados no bloco pré-calculado. NÃO calcule aspectos.
5. **Afetividade (Vênus e Lua):** Linguagem do amor e nutrição emocional.
6. **Desafios e Karma (Saturno, Nodos, Quíron):**
    * Saturno: Onde exige esforço/estrutura.
    * Nodo Norte: A direção de crescimento (desconfortável mas necessária).
    * Nodo Sul: O talento inato, mas zona de conforto a ser superada.

---

# PASSO 3: LÓGICA DE SÍNTESE AVANÇADA (CAMADA DE PROFUNDIDADE)

Após validar os dados matemáticos, aplique estas camadas de refinamento para evitar descrições superficiais:

## 3.1 Verificação de Dignidades Essenciais (Estado do Planeta)

Antes de interpretar um planeta, verifique seu "estado de ânimo" cósmico:

**Domicílio:** O planeta está em casa (ex: Marte em Áries/Escorpião, Sol em Leão). Interpretação: A energia flui pura, forte e natural.

**Exaltação:** O planeta é o convidado de honra (ex: Sol em Áries, Saturno em Libra). Interpretação: A energia opera em sua melhor performance, talvez até exagerada.

**Detrimento:** O planeta está no signo oposto ao seu domicílio (ex: Marte em Libra, Vênus em Áries). Interpretação: A energia é desconfortável, precisa agir de forma "indireta" ou "estratégica".

**Queda:** O planeta está no signo oposto à exaltação (ex: Sol em Libra, Lua em Escorpião). Interpretação: O planeta se sente inadequado ou precisa de muito esforço para funcionar bem.

**Peregrino:** Sem dignidade ou debilidade forte. Interpretação: O planeta depende dos aspectos que recebe de outros. Sua expressão é neutra e pode variar conforme os aspectos e conexões no mapa.

**Exemplo Prático:** Se o Sol está em Libra (Queda), não diga apenas "Você é diplomático". Diga: "Sua identidade (Sol) muitas vezes se sacrifica para agradar os outros (Libra), e seu desafio vital é descobrir quem você é quando não há ninguém por perto."

⚠️ **REGRA CRÍTICA SOBRE DIGNIDADES - LEIA COM ATENÇÃO:**

**VOCÊ NÃO DEVE CALCULAR OU INVENTAR DIGNIDADES. USE APENAS OS DADOS PRÉ-CALCULADOS FORNECIDOS.**

No bloco "🔒 DADOS PRÉ-CALCULADOS (TRAVAS DE SEGURANÇA ATIVADAS)" você encontrará uma seção "🏛️ DIGNIDADES PLANETÁRIAS (IDENTIFICADAS POR TABELA FIXA)" que lista EXATAMENTE a dignidade de cada planeta.

**PROCESSO DE VALIDAÇÃO OBRIGATÓRIA (FAÇA ISSO ANTES DE ESCREVER):**

1. **Leia o bloco pré-calculado COMPLETO** antes de começar a escrever
2. **Anote mentalmente** cada dignidade mencionada no bloco
3. **Antes de mencionar qualquer dignidade** no texto, pare e verifique:
   - O planeta está listado no bloco?
   - A dignidade mencionada no bloco é exatamente a que você vai escrever?
   - Se NÃO tiver certeza absoluta, NÃO mencione a dignidade

**EXEMPLOS DE ERROS PROIBIDOS (NUNCA FAÇA ISSO):**
- ❌ NÃO diga "Vênus em Sagitário está em Queda" se o bloco diz "PEREGRINO"
- ❌ NÃO invente dignidades baseado em "achismo" ou "lógica aparente"
- ❌ NÃO confunda signos (ex: dizer que Libra é Fogo quando é Ar)
- ❌ NÃO calcule dignidades - elas já foram calculadas pelo código Python
- ❌ NÃO use sinônimos (ex: "em exílio" quando o bloco diz "DETRIMENTO")
- ❌ NÃO diga "em queda" quando o bloco diz "PEREGRINO"

**EXEMPLOS CORRETOS (SIGA ESTES):**
- ✅ Se o bloco diz "Vênus em Sagitário: PEREGRINO", escreva: "Vênus em Sagitário está PEREGRINO, o que significa que sua expressão depende dos aspectos que recebe de outros planetas."
- ✅ Se o bloco diz "Sol em Libra: QUEDA", escreva: "Sol em Libra está em QUEDA, indicando que sua identidade muitas vezes se sacrifica para agradar os outros."
- ✅ Se o bloco diz "Saturno em Libra: EXALTAÇÃO", escreva: "Saturno em Libra está em EXALTAÇÃO, funcionando em sua melhor performance."

**REFERÊNCIAS ESPECÍFICAS PARA INTERPRETAÇÕES CORRETAS:**

**Lua em Leão (PEREGRINO):**
- ✅ CORRETO: "Lua em Leão indica emoções dramáticas, necessidade de ser notado e validado, expressão calorosa e teatral das emoções. A pessoa busca atenção e reconhecimento emocional."
- ❌ ERRADO: "Lua em Leão indica precisão emocional, necessidade de ordem, análise emocional" (isso é Lua em Virgem/Touro)

**Vênus em Sagitário (PEREGRINO):**
- ✅ CORRETO: "Vênus em Sagitário está PEREGRINO, valorizando liberdade, aventura e crescimento pessoal em relacionamentos. Busca parceiros que compartilhem interesses intelectuais e filosóficos."
- ❌ ERRADO: "Vênus em Sagitário está em queda" (NUNCA diga isso - é PEREGRINO)

**IMPORTANTE:** Se você não encontrar a dignidade de um planeta no bloco pré-calculado, NÃO invente. Use apenas o signo e a casa para interpretar, sem mencionar dignidade.

**VALIDAÇÃO OBRIGATÓRIA FINAL:** Antes de finalizar o texto, revise TODAS as menções a dignidades e confirme que cada uma está EXATAMENTE como descrita no bloco pré-calculado. Se houver qualquer dúvida, REMOVA a menção à dignidade e interprete apenas o signo e a casa.

## 3.2 A Regra da Regência (Conexão entre Áreas da Vida)

Para interpretar uma Casa Astrológica, você OBRIGATORIAMENTE deve olhar onde está o "Dono da Casa" (Regente).

**Lógica:** Identifique o signo da cúspide da Casa X -> Identifique o Planeta Regente desse signo -> Veja em que Casa Y esse planeta está.

**Template de Texto:** "A área da sua vida sobre [Assunto da Casa X] está diretamente ligada a [Assunto da Casa Y], pois o regente está lá."

**Exemplo:** Se a Casa 2 (Dinheiro) é Áries, o regente é Marte. Se Marte está na Casa 7 (Parcerias), interprete: "Sua capacidade financeira (C2) depende diretamente das suas alianças e parcerias (C7/Marte). Você ganha dinheiro agindo em conjunto ou competindo com outros."

## 3.3 Gestão de Contradições (O Ser Humano Real)

Humanos são contraditórios. Se o mapa mostrar aspectos conflitantes, NÃO os ignore. Sintetize-os.

**Cenário:** Sol em Libra (paz) vs. Lua em Leão (drama/atenção).

**Síntese Obrigatória:** "Existe um conflito interno em você: uma parte racional que deseja harmonia e silêncio (Sol em Libra), e uma necessidade emocional visceral de ser notado e validado (Lua em Leão). Sua Lua em Leão busca expressão dramática, calor emocional e reconhecimento, enquanto seu Sol em Libra busca equilíbrio e diplomacia. Seu crescimento depende de aprender a brilhar (Leão) sem quebrar a diplomacia (Libra)."

**⚠️ ATENÇÃO ESPECIAL - Lua em Leão:**
- Lua em Leão NÃO é "precisão emocional" ou "necessidade de ordem" (isso é Lua em Virgem/Touro)
- Lua em Leão É: emoções dramáticas, expressão teatral, busca por atenção e validação, calor emocional, necessidade de ser reconhecido emocionalmente
- Sempre interprete Lua em Leão como expressiva, dramática e que busca ser notada, NÃO como analítica ou organizada

---

# PASSO 4: MÓDULOS TEMÁTICOS ESPECÍFICOS

Ao escrever as seções do relatório, utilize estas "lentes" de foco:

## Módulo A: Inteligência e Comunicação (Mercúrio)

Não analise apenas "se a pessoa é inteligente". Analise COMO ela processa dados.

**Mercúrio em Signos de Ar:** Processamento lógico, social, mas pode ser indeciso.

**Mercúrio em Signos de Fogo:** Intuição rápida, fala antes de pensar, inspirador.

**Mercúrio em Signos de Terra:** Prático, lento, metódico, focado em resultados.

**Mercúrio em Signos de Água:** Memória fotográfica, decide pelo "feeling", não pela lógica.

**Verifique:** Se Mercúrio está Retrógrado (nascimento), adicione a nota sobre "introspecção e revisão mental".

## Módulo B: A Dinâmica do Desejo (Vênus e Marte)

Analise o "Eros" (Vênus) e o "Pathos" (Marte).

**Vênus:** O que a pessoa valoriza e como ela atrai. 
- **IMPORTANTE:** Antes de interpretar Vênus, verifique sua dignidade no bloco pré-calculado.
- **Exemplo CORRETO:** Se o bloco diz "Vênus em Sagitário: PEREGRINO", interprete: "Vênus em Sagitário está PEREGRINO, valorizando liberdade, aventura e crescimento pessoal. Busca relacionamentos que expandam horizontes intelectuais e filosóficos, evitando limitações ou 'grude'."
- **NUNCA diga:** "Vênus em Sagitário está em queda" (é PEREGRINO)

**Marte:** Como a pessoa conquista e briga. (Ex: Marte em Leão briga por orgulho e conquista com grandiosidade).

**Síntese Afetiva:** "Você busca [Estilo de Vênus], mas age para conseguir isso de forma [Estilo de Marte]."

## Módulo C: Vocação e Carreira (Meio do Céu - MC)

Analise o Signo do MC (Cúspide da Casa 10).
Analise planetas na Casa 10 (se houver).
Analise Saturno (o construtor da carreira).

**Distinção:** Diferencie "Trabalho Rotineiro" (Casa 6 - como você serve) de "Legado/Carreira" (Casa 10 - onde você brilha).

---

# PASSO 5: REMEDIAÇÃO E CONSELHO EVOLUTIVO (ACTIONABLE ADVICE)

Para cada tensão identificada (Quadratura, Oposição ou Planeta em Queda), você deve fornecer um "Mecanismo de Saída". Não entregue fatalismo.

## Regra da Remediação:

**Problema:** "Saturno em oposição a Marte (Freio vs. Acelerador)."

**Conselho Ruim:** "Você nunca vai conseguir agir."

**Conselho Bom (Remediação):** "Para vencer essa tensão, você deve usar a estratégia do 'Passo Calculado'. Use a disciplina de Saturno para planejar a ação de Marte. Transforme a impulsividade em resistência de longo prazo. Esportes de resistência (maratona, musculação) ajudam a canalizar essa energia."

---

# INSTRUÇÃO DE FORMATAÇÃO FINAL

Use **Negrito** para conceitos chave e posições planetárias.
Use *Itálico* para nuances psicológicas.
Use listas (Bullet points) para facilitar a leitura.
Termine a análise com uma **"Frase de Poder"**: Um mantra curto que sintetiza a missão do mapa (ex: "Sua missão é liderar com o coração, mas planejar com a mente").

---

# INSTRUÇÃO FINAL

Agora, processe os dados de nascimento fornecidos. Primeiro, faça a validação astronômica silenciosa. Segundo, gere o relatório. Se você encontrar dados de input que gerariam aspectos impossíveis (ex: Mercúrio quadrado ao Sol), ignore o aspecto impossível e interprete apenas o signo/casa, ou alerte que a configuração é astronomicamente rara/impossível e requer verificação dos dados de entrada.

---

# ⚠️ REGRA ABSOLUTA: USO DOS DADOS PRÉ-CALCULADOS

**ANTES DE ESCREVER QUALQUER INTERPRETAÇÃO, LEIA O BLOCO "🔒 DADOS PRÉ-CALCULADOS" COMPLETO.**

Este bloco contém TODOS os cálculos já feitos pelo código Python usando Swiss Ephemeris. Você DEVE usar APENAS esses dados:

1. **Temperamento:** Use APENAS os pontos fornecidos no bloco. NÃO recalcule.
2. **Dignidades:** Use APENAS as dignidades listadas no bloco. NÃO invente ou confunda.
3. **Regente:** Use APENAS o regente identificado no bloco. NÃO calcule outro.
4. **Elementos:** Use APENAS o mapeamento fixo fornecido (Libra = AR, não Fogo).

**VALIDAÇÃO ANTES DE ESCREVER (CHECKLIST OBRIGATÓRIO):**

Antes de escrever QUALQUER interpretação, faça este checklist:

1. ✅ **Leu o bloco pré-calculado COMPLETO?** (NÃO pule esta etapa)
2. ✅ **Anotou todas as dignidades mencionadas no bloco?**
3. ✅ **Para cada planeta que vai mencionar:**
   - Verificou se está no bloco?
   - A dignidade que vai escrever é EXATAMENTE a do bloco?
   - Se for PEREGRINO, não está escrevendo "queda" ou "exílio"?
4. ✅ **Para Lua em Leão especificamente:**
   - Está descrevendo como dramática, expressiva, que busca atenção?
   - NÃO está descrevendo como "precisa de ordem" ou "análise emocional"?
5. ✅ **Para Vênus em Sagitário especificamente:**
   - Se o bloco diz PEREGRINO, está usando EXATAMENTE essa palavra?
   - NÃO está dizendo "em queda"?
6. ✅ **Revisou TODAS as menções a dignidades no texto final?**
   - Cada uma está EXATAMENTE como no bloco?

**SE HOUVER QUALQUER DÚVIDA:** Não mencione a dignidade/elemento/regente. Apenas interprete o signo e a casa.

**REGRA DE OURO:** Se você não tem 100% de certeza absoluta de que a dignidade está correta, NÃO mencione a dignidade. É melhor interpretar apenas o signo e a casa do que inventar uma dignidade errada.

FIM DAS INSTRUÇÕES DO SISTEMA. Comece a análise agora baseada nos dados fornecidos."""


def _validate_chart_request(request: FullBirthChartRequest, lang: str = 'pt') -> Tuple[Dict[str, Any], Optional[str], Optional[str]]:
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
        from app.services.astrology_calculator import get_zodiac_sign
        
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
        # Usar validated_chart que contém aspectos calculados
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
        # Preparar string de Lilith para evitar backslash em f-string
        lilith_str = f'\n- Lilith em {request.lilithSign}{f" na Casa {request.lilithHouse}" if request.lilithHouse else ""}' if request.lilithSign else ''
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
- Quíron em {request.chironSign or 'não calculado'}{f' na Casa {request.chironHouse}' if request.chironHouse else ''} (Ferida/Dom de Cura){lilith_str}

---
🔍 RELATÓRIO DE VALIDAÇÃO MATEMÁTICA:
{validation_summary or '✅ Dados validados automaticamente pelo sistema.'}
---

{precomputed_data or ''}
"""
    else:
        # Preparar string de Lilith para evitar backslash em f-string
        lilith_str = f'\n- Lilith in {request.lilithSign}{f" in House {request.lilithHouse}" if request.lilithHouse else ""}' if request.lilithSign else ''
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
- Chiron in {request.chironSign or 'not calculated'}{f' in House {request.chironHouse}' if request.chironHouse else ''} (Wound/Healing Gift){lilith_str}

---
🔍 MATHEMATICAL VALIDATION REPORT:
{validation_summary or '✅ Data automatically validated by the system.'}
---

{precomputed_data or ''}
"""


def _generate_section_prompt(request: FullBirthChartRequest, section: str, validation_summary: Optional[str] = None, precomputed_data: Optional[str] = None) -> Tuple[str, str]:
    """Gera o prompt específico para cada seção do mapa baseado na nova estrutura fornecida."""
    lang = request.language or 'pt'
    
    # Contexto completo do mapa para referência (inclui validação E dados pré-calculados)
    full_context = _get_full_chart_context(request, lang, validation_summary, precomputed_data)
    
    # Data de nascimento formatada para inserção no prompt
    birth_data_str = f"Data: {request.birthDate}, Hora: {request.birthTime}, Local: {request.birthPlace}"
    
    if section == 'power':
        title = "A Engenharia da Sua Energia (Temperamento)" if lang == 'pt' else "The Engineering of Your Energy (Temperament)"
        if lang == 'pt':
            prompt = f"""{full_context}

**1. A ENGENHARIA DA SUA ENERGIA (TEMPERAMENTO)**

🚨 **INSTRUÇÃO CRÍTICA - LEIA ANTES DE ESCREVER:**

Você DEVE usar APENAS os dados do bloco "🔒 DADOS PRÉ-CALCULADOS" fornecido acima. NÃO calcule, NÃO estime, NÃO invente.

**VALIDAÇÃO OBRIGATÓRIA ANTES DE ESCREVER:**
1. ✅ Localize o bloco "📊 TEMPERAMENTO (CALCULADO MATEMATICAMENTE)"
2. ✅ Leia os pontos EXATOS: Fogo, Terra, Ar, Água
3. ✅ Identifique o ELEMENTO DOMINANTE listado no bloco
4. ✅ Identifique o ELEMENTO AUSENTE (se houver) listado no bloco
5. ✅ Use EXATAMENTE esses números e elementos - NÃO recalcule

**EXEMPLO DE USO CORRETO:**
Se o bloco diz:
  • Fogo: 5 pontos
  • Terra: 2 pontos
  • Ar: 2 pontos
  • Água: 8 pontos
  ELEMENTO DOMINANTE: Água

Você DEVE escrever: "O mapa apresenta predominância do elemento Água, com 8 pontos, seguido pelo elemento Fogo, com 5 pontos..."

**NUNCA FAÇA:**
❌ Dizer "Fogo dominante com 8 pontos" se o bloco diz "Água: 8 pontos"
❌ Dizer "Água ausente" se o bloco mostra "Água: 8 pontos"
❌ Recalcular os pontos - use APENAS os do bloco

Comece sua resposta com: "Análise do Mapa Astral de {request.name}"

Em seguida, inclua uma seção intitulada: "Cálculo do Temperamento (Filtro de Arroyo)"

Explique como o balanço de elementos afeta a vitalidade e a psicologia básica.

**Análise Obrigatória:**
- Use APENAS os pontos do bloco pré-calculado (NÃO recalcule)
- Identifique o elemento dominante EXATAMENTE como listado no bloco
- Identifique o elemento ausente/fraco EXATAMENTE como listado no bloco (ou "nenhum" se todos têm pontos)
- Analise as modalidades (Cardeal, Fixo, Mutável)

**Insight Prático:** Como lidar com a falta ou excesso de um elemento no dia a dia.

**O Regente do Ascendente:** Use APENAS o regente identificado no bloco "👑 REGENTE DO MAPA". Analise sua condição (Signo, Casa, Aspectos). Onde ele está e como ele direciona o foco principal da vida. Ele é um aliado ou um desafio para o nativo?

IMPORTANTE:
- SEMPRE comece com "Análise do Mapa Astral de {request.name}"
- SEMPRE inclua a seção "Cálculo do Temperamento (Filtro de Arroyo)" com conteúdo detalhado
- Use "conselhos" (português), NUNCA "consejo" (espanhol)
- NÃO recalcule temperamento - use APENAS os dados do bloco pré-calculado
- NÃO invente elementos ausentes se o bloco mostra que todos têm pontos
- Não repita informações já mencionadas em outras seções
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação - se a casa não estiver disponível, OMITA completamente a menção à casa
- Foque no temperamento como motor de motivação e ação
- Analise o regente do mapa com profundidade técnica (Dignidades, Regências)
- Dê conselhos práticos e acionáveis para equilíbrio energético"""
        else:
            prompt = f"""{full_context}

**1. THE ENGINEERING OF YOUR ENERGY (TEMPERAMENT)**

🚨 **CRITICAL INSTRUCTION - READ BEFORE WRITING:**

You MUST use ONLY the data from the "🔒 PRE-COMPUTED DATA" block provided above. DO NOT calculate, DO NOT estimate, DO NOT invent.

**MANDATORY VALIDATION BEFORE WRITING:**
1. ✅ Locate the block "📊 TEMPERAMENT (MATHEMATICALLY CALCULATED)"
2. ✅ Read the EXACT points: Fire, Earth, Air, Water
3. ✅ Identify the DOMINANT ELEMENT listed in the block
4. ✅ Identify the LACKING ELEMENT (if any) listed in the block
5. ✅ Use EXACTLY these numbers and elements - DO NOT recalculate

**CORRECT USAGE EXAMPLE:**
If the block says:
  • Fire: 5 points
  • Earth: 2 points
  • Air: 2 points
  • Water: 8 points
  DOMINANT ELEMENT: Water

You MUST write: "The chart shows predominance of the Water element, with 8 points, followed by the Fire element, with 5 points..."

**NEVER DO:**
❌ Say "Fire dominant with 8 points" if the block says "Water: 8 points"
❌ Say "Water absent" if the block shows "Water: 8 points"
❌ Recalculate the points - use ONLY those from the block

Explain how the balance of elements affects vitality and basic psychology.

**Mandatory Analysis:**
- Use ONLY the points from the pre-computed block (DO NOT recalculate)
- Identify the dominant element EXACTLY as listed in the block
- Identify the absent/weak element EXACTLY as listed in the block (or "none" if all have points)
- Analyze the modalities (Cardinal, Fixed, Mutable)

**Practical Insight:** How to deal with the lack or excess of an element in daily life.

**The Ascendant Ruler:** Use ONLY the ruler identified in the "👑 CHART RULER" block. Analyze its condition (Sign, House, Aspects). Where is it and how does it direct the main focus of life. Is it an ally or a challenge for the native?

IMPORTANT:
- DO NOT recalculate temperament - use ONLY the data from the pre-computed block
- DO NOT invent absent elements if the block shows all have points
- Do not repeat information already mentioned in other sections
- NEVER write "House not provided", "in House not provided" or any variation - if the house is not available, COMPLETELY OMIT mentioning the house
- Focus on temperament as a driver of motivation and action
- Analyze the chart ruler with technical depth (Dignities, Rulerships)
- Give practical and actionable advice for energy balance"""
    
    elif section == 'triad':
        title = "O Núcleo da Personalidade (A Tríade Primordial)" if lang == 'pt' else "The Core of Personality (The Primordial Triad)"
        if lang == 'pt':
            prompt = f"""{full_context}

**2. O NÚCLEO DA PERSONALIDADE (A TRÍADE PRIMORDIAL)**

Sintetize Sol (Vontade), Lua (Necessidade Emocional) e Ascendente (Modo de Ação).

**Análise Obrigatória:**
- Não interprete separados. Explique o conflito ou a harmonia entre o que a pessoa quer (Sol) e o que ela precisa (Lua)
- Analise a dinâmica entre vontade consciente (Sol), necessidades emocionais (Lua) e forma de agir (Ascendente)
- Explique como eles se equilibram ou conflitam

**Foco no Regente do Ascendente:** Onde ele está e como ele direciona o foco principal da vida.

DADOS:
- Sol em {request.sunSign} na Casa {request.sunHouse}
- Lua em {request.moonSign} na Casa {request.moonHouse}
- Ascendente em {request.ascendant}

IMPORTANTE:
- Não repita informações já mencionadas em outras seções
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação
- Faça uma síntese que conecte os três pontos para contar a história da pessoa
- Use abordagem de síntese, evitando descrições fragmentadas ou isoladas
- Procure contradições - é nas contradições que a pessoa trava na hora de decidir"""
        else:
            prompt = f"""{full_context}

**2. THE CORE OF PERSONALITY (THE PRIMORDIAL TRIAD)**

Synthesize Sun (Will), Moon (Emotional Need) and Ascendant (Mode of Action).

**Mandatory Analysis:**
- Do not interpret separately. Explain the conflict or harmony between what the person wants (Sun) and what they need (Moon)
- Analyze the dynamics between conscious will (Sun), emotional needs (Moon) and way of acting (Ascendant)
- Explain how they balance or conflict

**Focus on the Ascendant Ruler:** Where it is and how it directs the main focus of life.

DATA:
- Sun in {request.sunSign} in House {request.sunHouse}
- Moon in {request.moonSign} in House {request.moonHouse}
- Ascendant in {request.ascendant}

IMPORTANT:
- Do not repeat information already mentioned in other sections
- NEVER write "House not provided", "in House not provided" or any variation
- Make a synthesis that connects the three points to tell the person's story
- Use a synthesis approach, avoiding fragmented or isolated descriptions
- Look for contradictions - it's in contradictions that the person gets stuck when deciding"""
    
    elif section == 'personal':
        title = "Estratégia de Tomada de Decisão & Carreira" if lang == 'pt' else "Decision Making Strategy & Career"
        if lang == 'pt':
            prompt = f"""{full_context}

**3. ESTRATÉGIA DE TOMADA DE DECISÃO & CARREIRA**

Analise Mercúrio e Marte. A pessoa é impulsiva ou cautelosa? Racional ou intuitiva?

**Análise Obrigatória:**
- **Mercúrio (como pensa):** Como a pessoa processa informações, aprende e toma decisões
- **Marte (como age):** Onde coloca sua energia, assertividade e impulso. A pessoa é impulsiva ou cautelosa?
- Analise a Casa 2 (Dinheiro), Casa 6 (Rotina) e Casa 10 (Metas/Saturno)

**Orientação:** Qual o melhor ambiente para ela prosperar? Onde estão os bloqueios de Saturno que exigem paciência?

IMPORTANTE: Use "conselhos" (português), NUNCA "consejo" (espanhol). Use sempre português brasileiro.

DADOS:
- Mercúrio em {request.mercurySign or 'não informado'}{f' na Casa {request.mercuryHouse}' if request.mercuryHouse else ''}
- Marte em {request.marsSign or 'não informado'}{f' na Casa {request.marsHouse}' if request.marsHouse else ''}
- Vênus em {request.venusSign or 'não informado'}{f' na Casa {request.venusHouse}' if request.venusHouse else ''}

IMPORTANTE:
- Não repita informações já mencionadas em outras seções
- USE OS DADOS ESPECÍFICOS FORNECIDOS ACIMA - não use frases genéricas como "Casa não informada"
- Se a casa não estiver disponível, foque no signo e no planeta apenas
- Foque em como cada planeta funciona como ferramenta prática na vida
- Conecte com exemplos concretos de manifestação baseados nos dados fornecidos"""
        else:
            prompt = f"""{full_context}

**3. DECISION MAKING STRATEGY & CAREER**

Analyze Mercury and Mars. Is the person impulsive or cautious? Rational or intuitive?

**Mandatory Analysis:**
- **Mercury (how they think):** How the person processes information, learns and makes decisions
- **Mars (how they act):** Where they put their energy, assertiveness and drive. Is the person impulsive or cautious?
- Analyze House 2 (Money), House 6 (Routine) and House 10 (Goals/Saturn)

**Guidance:** What is the best environment for them to prosper? Where are Saturn's blocks that require patience?

DATA:
- Mercury in {request.mercurySign or 'not provided'}{f' in House {request.mercuryHouse}' if request.mercuryHouse else ''}
- Mars in {request.marsSign or 'not provided'}{f' in House {request.marsHouse}' if request.marsHouse else ''}
- Venus in {request.venusSign or 'not provided'}{f' in House {request.venusHouse}' if request.venusHouse else ''}

IMPORTANT:
- Do not repeat information already mentioned in other sections
- USE THE SPECIFIC DATA PROVIDED ABOVE - do not use generic phrases like "House not provided"
- If the house is not available, focus on the sign and planet only
- Focus on how each planet functions as a practical tool in life
- Connect with concrete examples of manifestation based on the provided data"""
    
    elif section == 'houses':
        title = "Relacionamentos e Vida Afetiva" if lang == 'pt' else "Relationships and Affective Life"
        if lang == 'pt':
            prompt = f"""{full_context}

**4. RELACIONAMENTOS E VIDA AFETIVA**

Analise Vênus e a Casa 7.

**Análise Obrigatória:**
- **Vênus:** Analise a condição de Vênus (Dignidades/Debilidades). Como a pessoa ama, o que valoriza e como lida com recursos
- **Casa 7 (Relacionamentos):** O padrão de parceiro atraído versus o que a pessoa realmente necessita para evoluir
- O que a pessoa diz que quer vs. o que ela atrai inconscientemente (Descendente)

DADOS RELEVANTES:
- Vênus em {request.venusSign or 'não informado'}{f' na Casa {request.venusHouse}' if request.venusHouse else ''}
- Descendente (oposto ao Ascendente {request.ascendant})

⚠️ **REGRA CRÍTICA SOBRE DIGNIDADES DE VÊNUS:**
- **VOCÊ NÃO DEVE CALCULAR OU INVENTAR A DIGNIDADE DE VÊNUS**
- **CONSULTE O BLOCO "🔒 DADOS PRÉ-CALCULADOS" FORNECIDO ACIMA**
- **Se o bloco diz "Vênus em Sagitário: PEREGRINO", use EXATAMENTE isso - NÃO diga "Queda"**
- **Exemplo CORRETO:** "Vênus em Sagitário está em PEREGRINO, o que significa..."
- **Exemplo INCORRETO:** "Vênus está em Queda em Sagitário" (NUNCA diga isso se o bloco diz PEREGRINO)
- **Se você não encontrar a dignidade no bloco pré-calculado, NÃO invente - apenas interprete o signo e a casa**

IMPORTANTE:
- Não repita informações já mencionadas em outras seções
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação - use apenas os dados fornecidos ou omita a informação
- Analise Vênus com técnica de Dignidades/Debilidades (Astrologia Clássica) - MAS USE APENAS OS DADOS DO BLOCO PRÉ-CALCULADO
- Analise padrões de relacionamento com profundidade psicológica"""
        else:
            prompt = f"""{full_context}

**4. RELATIONSHIPS AND AFFECTIVE LIFE**

Analyze Venus and House 7.

**Mandatory Analysis:**
- **Venus:** Analyze Venus's condition (Dignities/Debilities). How the person loves, what they value and how they handle resources
- **House 7 (Relationships):** The pattern of attracted partner versus what the person really needs to evolve
- What the person says they want vs. what they unconsciously attract (Descendant)

RELEVANT DATA:
- Venus in {request.venusSign or 'not provided'}{f' in House {request.venusHouse}' if request.venusHouse else ''}
- Descendant (opposite to Ascendant {request.ascendant})

⚠️ **CRITICAL RULE ABOUT VENUS DIGNITIES:**
- **YOU MUST NOT CALCULATE OR INVENT VENUS'S DIGNITY**
- **CONSULT THE "🔒 PRE-COMPUTED DATA" BLOCK PROVIDED ABOVE**
- **If the block says "Venus in Sagittarius: PEREGRINE", use EXACTLY that - DO NOT say "Fall"**
- **CORRECT Example:** "Venus in Sagittarius is in PEREGRINE, which means..."
- **INCORRECT Example:** "Venus is in Fall in Sagittarius" (NEVER say this if the block says PEREGRINE)
- **If you don't find the dignity in the pre-computed block, DO NOT invent it - only interpret the sign and house**

IMPORTANT:
- Do not repeat information already mentioned in other sections
- NEVER write "House not provided", "in House not provided" or any variation - use only the provided data or omit the information
- Analyze Venus with Dignities/Debilities technique (Classical Astrology) - BUT USE ONLY THE DATA FROM THE PRE-COMPUTED BLOCK
- Analyze relationship patterns with psychological depth"""
    
    elif section == 'karma':
        title = "O Caminho Kármico e Desafios de Crescimento" if lang == 'pt' else "The Karmic Path and Growth Challenges"
        if lang == 'pt':
            # Preparar string de Lilith para evitar backslash em f-string
            lilith_str = f'\n- Lilith em {request.lilithSign} na Casa {request.lilithHouse}' if request.lilithSign and request.lilithHouse else ''
            prompt = f"""{full_context}

**5. O CAMINHO KÁRMICO E DESAFIOS DE CRESCIMENTO**

Analise Saturno (o mestre severo) e os Nodos Lunares (direção da alma).

**Análise Obrigatória:**
- **Saturno:** Onde a pessoa enfrenta seus maiores testes, medos e responsabilidades. Onde a vida vai exigir mais esforço e onde está a recompensa final
- **Nodos Lunares:** Qual zona de conforto (Nodo Sul) deve ser abandonada e qual missão de vida (Nodo Norte) deve ser perseguida
- **Quíron e Lilith:** Onde reside a ferida que cura (Quíron) e a força visceral/insubmissão (Lilith)

DADOS:
- Saturno em {request.saturnSign or 'não informado'}{f' na Casa {request.saturnHouse}' if request.saturnHouse else ''}
- Nodo Norte em {request.northNodeSign or 'não informado'}{f' na Casa {request.northNodeHouse}' if request.northNodeHouse else ''}
- Nodo Sul em {request.southNodeSign or 'não informado'}{f' na Casa {request.southNodeHouse}' if request.southNodeHouse else ''}
- Quíron em {request.chironSign or 'não informado'}{f' na Casa {request.chironHouse}' if request.chironHouse else ''}{lilith_str}

IMPORTANTE CRÍTICO:
- USE APENAS OS DADOS FORNECIDOS ACIMA - se a casa não estiver disponível, OMITA completamente a menção à casa, não diga "Casa não informada" ou "na Casa não informada"
- Se você não tiver a informação da casa, simplesmente não mencione a casa - foque apenas no signo
- NUNCA escreva "na Casa não informada", "Casa não informada" ou qualquer variação disso
- Não repita informações já mencionadas em outras seções
- Analise Saturno como o "Mestre da Realidade" (Riske/Sakoian)
- Conecte os nodos lunares com propósito de vida e evolução da alma
- Explique Quíron e Lilith como ferramentas de transformação"""
        else:
            # Preparar string de Lilith para evitar backslash em f-string
            lilith_str = f'\n- Lilith in {request.lilithSign} in House {request.lilithHouse}' if request.lilithSign and request.lilithHouse else ''
            prompt = f"""{full_context}

**5. THE KARMIC PATH AND GROWTH CHALLENGES**

Analyze Saturn (the severe master) and the Lunar Nodes (soul direction).

**Mandatory Analysis:**
- **Saturn:** Where the person faces their greatest tests, fears and responsibilities. Where life will require more effort and where the final reward is
- **Lunar Nodes:** What comfort zone (South Node) should be abandoned and what life mission (North Node) should be pursued
- **Chiron and Lilith:** Where resides the wound that heals (Chiron) and the visceral/insubordinate force (Lilith)

DATA:
- Saturn in {request.saturnSign or 'not provided'}{f' in House {request.saturnHouse}' if request.saturnHouse else ''}
- North Node in {request.northNodeSign or 'not provided'}{f' in House {request.northNodeHouse}' if request.northNodeHouse else ''}
- South Node in {request.southNodeSign or 'not provided'}{f' in House {request.southNodeHouse}' if request.southNodeHouse else ''}
- Chiron in {request.chironSign or 'not provided'}{f' in House {request.chironHouse}' if request.chironHouse else ''}{lilith_str}

CRITICAL IMPORTANT:
- USE ONLY THE DATA PROVIDED ABOVE - if the house is not available, COMPLETELY OMIT mentioning the house, do not say "House not provided" or "in House not provided"
- If you don't have the house information, simply don't mention the house - focus only on the sign
- NEVER write "in House not provided", "House not provided" or any variation of that
- Do not repeat information already mentioned in other sections
- Analyze Saturn as the "Master of Reality" (Riske/Sakoian)
- Connect lunar nodes with life purpose and soul evolution
- Explain Chiron and Lilith as transformation tools"""
    
    elif section == 'synthesis':
        title = "Síntese e Orientação Estratégica" if lang == 'pt' else "Strategic Synthesis and Guidance"
        if lang == 'pt':
            prompt = f"""{full_context}

**SÍNTESE FINAL E ORIENTAÇÃO ESTRATÉGICA**

* **Pontos Fortes a Explorar:** (Destaque Stelliums, Trígonos exatos ou Planetas em Domicílio/Exaltação).

* **Desafios e Cuidados:** (Destaque Quadraturas T, Planetas em Queda/Exílio ou Casas vazias de elemento).

* **Conselho Final:** Uma diretriz prática e empoderadora para a evolução pessoal e tomada de decisão.

⚠️ **REGRA CRÍTICA SOBRE DIGNIDADES:**
- **VOCÊ NÃO DEVE INVENTAR OU INFERIR DIGNIDADES**
- **CONSULTE O BLOCO "🔒 DADOS PRÉ-CALCULADOS" FORNECIDO ACIMA para TODAS as dignidades**
- **Se mencionar "planetas em Queda", use APENAS os planetas listados como QUEDA no bloco pré-calculado**
- **NÃO inclua planetas que estão como PEREGRINO na lista de "planetas em Queda"**
- **Exemplo:** Se o bloco diz "Vênus em Sagitário: PEREGRINO", NÃO mencione Vênus como "planeta em Queda"
- **Use APENAS os dados do bloco pré-calculado - NÃO invente ou infira dignidades**

IMPORTANTE:
- Use "conselhos" (português), NUNCA "consejo" (espanhol). Use sempre português brasileiro.
- NÃO repita informações já detalhadas nas seções anteriores
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação
- Faça uma síntese integradora que conecte TODOS os elementos já analisados
- Identifique pontos técnicos específicos (Stelliums, Dignidades, Aspectos exatos) - MAS USE APENAS OS DADOS DO BLOCO PRÉ-CALCULADO
- Ofereça uma diretriz estratégica e empoderadora
- Foque em tomada de decisão prática e evolução pessoal"""
        else:
            prompt = f"""{full_context}

**FINAL SYNTHESIS AND STRATEGIC GUIDANCE**

* **Strengths to Explore:** (Highlight Stelliums, Exact Trines or Planets in Domicile/Exaltation).

* **Challenges and Cautions:** (Highlight T-Squares, Planets in Fall/Exile or Houses empty of element).

* **Final Counsel:** A practical and empowering directive for personal evolution and decision-making.

⚠️ **CRITICAL RULE ABOUT DIGNITIES:**
- **YOU MUST NOT INVENT OR INFER DIGNITIES**
- **CONSULT THE "🔒 PRE-COMPUTED DATA" BLOCK PROVIDED ABOVE for ALL dignities**
- **If mentioning "planets in Fall", use ONLY the planets listed as FALL in the pre-computed block**
- **DO NOT include planets that are listed as PEREGRINE in the "planets in Fall" list**
- **Example:** If the block says "Venus in Sagittarius: PEREGRINE", DO NOT mention Venus as a "planet in Fall"
- **Use ONLY the data from the pre-computed block - DO NOT invent or infer dignities**

IMPORTANT:
- DO NOT repeat information already detailed in previous sections
- NEVER write "House not provided", "in House not provided" or any variation
- Make an integrating synthesis that connects ALL elements already analyzed
- Identify specific technical points (Stelliums, Dignities, Exact Aspects) - BUT USE ONLY THE DATA FROM THE PRE-COMPUTED BLOCK
- Offer a strategic and empowering directive
- Focus on practical decision-making and personal evolution"""
    
    else:
        title = "Análise Astrológica"
        prompt = f"Análise astrológica para {request.name}"
    
    return title, prompt


@router.post("/full-birth-chart/section", response_model=FullBirthChartResponse)
async def generate_birth_chart_section(
    request: FullBirthChartRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Gera uma seção específica do Mapa Astral Completo.
    
    Seções disponíveis (baseadas na nova estrutura):
    - power: A Estrutura de Poder (Temperamento e Motivação) - Elementos, Qualidades e Regente do Mapa
    - triad: A Tríade Fundamental (O Núcleo da Personalidade) - Sol, Lua, Ascendente
    - personal: Dinâmica Pessoal e Ferramentas - Mercúrio, Vênus, Marte
    - houses: Análise Setorial Avançada - Casas 2, 4, 6, 7, 10 e Regentes
    - karma: Expansão, Estrutura e Karma - Júpiter, Saturno, Nodos, Quíron, Lilith
    - synthesis: Síntese e Orientação Estratégica - Pontos Fortes, Desafios e Conselho Final
    """
    import traceback
    import os
    from datetime import datetime
    
    request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")[:20]
    lang = request.language or 'pt'
    
    def log(level: str, message: str):
        """Helper para logging estruturado"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [{level}] [REQ-{request_id}] [SECTION-{request.section or 'unknown'}] {message}")
    
    try:
        log("INFO", f"Iniciando geração de seção '{request.section}' para {request.name}")
        
        if not request.section:
            log("ERROR", "Seção não especificada")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Especifique uma seção: power, triad, personal, houses, karma, synthesis"
            )
        
        # Verificar RAG service - OBRIGATÓRIO para geração
        rag_service = None
        rag_error = None
        try:
            rag_service = get_rag_service()
            if rag_service:
                log("INFO", "RAG service disponível (consolidado no backend)")
            else:
                rag_error = "RAG service não disponível - índice ainda não foi construído ou dependências não estão instaladas"
                log("ERROR", f"RAG service não disponível: {rag_error}")
                print(f"[ERROR] [REQ-{request_id}] RAG service não disponível: {rag_error}")
        except Exception as e:
            rag_error = f"Erro ao obter RAG service: {str(e)}"
            log("ERROR", rag_error)
            print(f"[ERROR] [REQ-{request_id}] {rag_error}")
            print(f"[ERROR] [REQ-{request_id}] Traceback: {traceback.format_exc()}")
        
        # Verificar se o RAG service tem índice
        has_index = False
        rag_status_error = None
        if rag_service:
            try:
                log("INFO", "Verificando status do RAG service...")
                if hasattr(rag_service, 'documents') and rag_service.documents:
                    has_index = len(rag_service.documents) > 0
                log("INFO", f"Status RAG - has_index: {has_index}")
                if not has_index:
                    rag_status_error = "Índice RAG vazio ou não carregado"
                    log("ERROR", rag_status_error)
                    print(f"[ERROR] [REQ-{request_id}] {rag_status_error}")
            except Exception as e:
                rag_status_error = f"Erro ao verificar status RAG: {str(e)}"
                log("ERROR", rag_status_error)
                print(f"[ERROR] [REQ-{request_id}] {rag_status_error}")
                print(f"[ERROR] [REQ-{request_id}] Traceback: {traceback.format_exc()}")
        else:
            rag_status_error = "RAG service não disponível para verificar status"
            log("ERROR", rag_status_error)
            print(f"[ERROR] [REQ-{request_id}] {rag_status_error}")
        
        # Validar dados do mapa astral e criar bloco de dados pré-calculados
        try:
            validated_chart, validation_summary, precomputed_data = _validate_chart_request(request, lang)
            log("INFO", "Dados do mapa astral validados com sucesso")
        except Exception as e:
            log("ERROR", f"Erro ao validar dados do mapa: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao validar dados do mapa astral: {str(e)}"
            )
        
        # Obter prompt mestre e prompt da seção
        try:
            master_prompt = _get_master_prompt(lang)
            title, section_prompt = _generate_section_prompt(request, request.section, validation_summary, precomputed_data)
            log("INFO", f"Prompts gerados: título='{title}'")
        except Exception as e:
            log("ERROR", f"Erro ao gerar prompts: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao preparar prompts: {str(e)}"
            )
        
        # Buscar contexto relevante do RAG (se disponível)
        search_queries = {
            'power': f"regente do mapa ascendente {request.ascendant} elementos fogo terra ar água qualidades cardeal fixo mutável temperamento",
            'triad': f"Sol Lua Ascendente personalidade tríade {request.sunSign} {request.moonSign} {request.ascendant} dinâmica",
            'personal': f"Mercúrio Vênus Marte planetas pessoais dignidades debilidades {request.mercurySign or ''} {request.venusSign or ''} {request.marsSign or ''}",
            'houses': f"casas astrológicas regentes casas Casa 2 Casa 4 Casa 6 Casa 7 Casa 10 vocação finanças relacionamentos",
            'karma': f"Júpiter Saturno Nodo Norte Sul karma evolução {request.northNodeSign or ''} Quíron Lilith propósito vida",
            'synthesis': f"síntese mapa astral integração stelliums trígonos quadraturas dignidades exaltação queda exílio"
        }
        
        query = search_queries.get(request.section, "interpretação mapa astral")
        
        # Buscar contexto do RAG - OBRIGATÓRIO
        rag_results = []
        rag_search_error = None
        if not rag_service:
            rag_search_error = f"RAG service não disponível. Erro anterior: {rag_error or 'desconhecido'}"
            log("ERROR", rag_search_error)
            print(f"[ERROR] [REQ-{request_id}] {rag_search_error}")
        elif not has_index:
            rag_search_error = f"RAG index não disponível. Erro anterior: {rag_status_error or 'desconhecido'}"
            log("ERROR", rag_search_error)
            print(f"[ERROR] [REQ-{request_id}] {rag_search_error}")
        else:
            try:
                log("INFO", f"Buscando contexto no RAG para query: {query[:50]}...")
                rag_results = rag_service.search(query, top_k=6)
                log("INFO", f"RAG retornou {len(rag_results)} resultados")
                if len(rag_results) == 0:
                    log("WARNING", "RAG retornou 0 resultados - pode indicar problema no índice")
                    print(f"[WARNING] [REQ-{request_id}] RAG retornou 0 resultados para query: {query[:100]}")
            except Exception as e:
                rag_search_error = f"Erro ao buscar no RAG: {str(e)}"
                log("ERROR", rag_search_error)
                print(f"[ERROR] [REQ-{request_id}] {rag_search_error}")
                print(f"[ERROR] [REQ-{request_id}] Traceback: {traceback.format_exc()}")
        
        # Preparar contexto
        context_text = "\n\n".join([doc.get('text', '') for doc in rag_results[:6] if doc.get('text')])
        
        # Se não houver contexto do RAG, usar contexto mínimo (mas ainda tentar gerar)
        if not context_text or len(context_text.strip()) < 100:
            context_text = "Informações astrológicas gerais sobre o tema. Use seu conhecimento astrológico para criar uma interpretação detalhada e completa."
        
        # Verificar Groq - OBRIGATÓRIO para geração
        groq_client = None
        groq_error = None
        
        # Verificar se a chave está configurada
        if not settings.GROQ_API_KEY or not settings.GROQ_API_KEY.strip():
            groq_error = "GROQ_API_KEY não configurada - Configure a chave da API do Groq no arquivo .env ou variáveis de ambiente"
            log("ERROR", groq_error)
            print(f"[ERROR] [REQ-{request_id}] {groq_error}")
            print(f"[ERROR] [REQ-{request_id}] Para obter uma chave: https://console.groq.com/")
            print(f"[ERROR] [REQ-{request_id}] Adicione no arquivo backend/.env: GROQ_API_KEY=sua_chave_aqui")
        else:
            # Tentar criar o cliente
            try:
                groq_client = _get_groq_client()
                if not groq_client:
                    groq_error = "Erro ao inicializar cliente Groq - Verifique se a chave é válida"
                    log("ERROR", groq_error)
                    print(f"[ERROR] [REQ-{request_id}] {groq_error}")
            except Exception as e:
                groq_error = f"Erro ao criar cliente Groq: {str(e)}"
                log("ERROR", groq_error)
                print(f"[ERROR] [REQ-{request_id}] {groq_error}")
        
        # Gerar interpretação com Groq - OBRIGATÓRIO
        if groq_client:
            try:
                from groq import Groq
                
                # Limitar contexto para evitar token overflow
                context_limit = min(len(context_text), 3000)
                context_snippet = context_text[:context_limit] if context_text else "Informações astrológicas gerais sobre o tema. Use seu conhecimento astrológico para criar uma interpretação detalhada e completa."
                
                full_user_prompt = f"""⚠️ **LEIA PRIMEIRO - INSTRUÇÃO CRÍTICA:**

Antes de escrever qualquer interpretação, você DEVE ler e usar APENAS os dados do bloco "🔒 DADOS PRÉ-CALCULADOS" fornecido abaixo. 

**🚨 VALIDAÇÃO OBRIGATÓRIA PARA TEMPERAMENTO:**
1. Localize o bloco "📊 TEMPERAMENTO (CALCULADO MATEMATICAMENTE)"
2. Leia os pontos EXATOS: Fogo, Terra, Ar, Água
3. Identifique o ELEMENTO DOMINANTE listado
4. Identifique o ELEMENTO AUSENTE listado (ou "Nenhum" se todos têm pontos)
5. Use EXATAMENTE esses números - NÃO recalcule, NÃO estime

**EXEMPLO CORRETO:**
Se o bloco diz:
  • Fogo: 5 pontos
  • Água: 8 pontos
  • ELEMENTO DOMINANTE: Água
Você DEVE escrever: "O mapa apresenta predominância do elemento Água, com 8 pontos..."

**ERROS PROIBIDOS:**
❌ Dizer "Fogo dominante com 8 pontos" se o bloco diz "Água: 8 pontos"
❌ Dizer "Água ausente" se o bloco mostra "Água: 8 pontos"
❌ Recalcular os pontos - use APENAS os do bloco

**NÃO CALCULE, NÃO INVENTE, NÃO CONFUNDA:**
- Dignidades: Use APENAS as listadas no bloco (ex: se diz "Vênus em Sagitário: PEREGRINO", use EXATAMENTE isso)
- Temperamento: Use APENAS os pontos fornecidos no bloco - NÃO recalcule
- Regente: Use APENAS o regente identificado no bloco
- Elementos: Use APENAS o mapeamento fixo (Libra = AR, não Fogo)

Se você não encontrar um dado no bloco pré-calculado, NÃO invente. Apenas interprete o signo e a casa.

---

{section_prompt}

---

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_snippet}

IMPORTANTE FINAL: 
- Use SEMPRE português brasileiro
- Use "conselhos", NUNCA "consejo"
- Garanta que TODAS as seções tenham conteúdo completo e detalhado
- Não deixe títulos sem conteúdo"""
                
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": master_prompt},
                        {"role": "user", "content": full_user_prompt}
                    ],
                    model="llama-3.1-8b-instant",
                    temperature=0.7,
                    max_tokens=2000,
                    top_p=0.9,
                )
                
                content = chat_completion.choices[0].message.content
                
                if not content or len(content.strip()) < 50:
                    raise ValueError("Resposta do Groq muito curta ou vazia")
                
                # Aplicar filtro de deduplicação
                content = _deduplicate_text(content)
                
                return FullBirthChartResponse(
                    section=request.section,
                    title=title,
                    content=content.strip(),
                    generated_by="groq"
                )
                
            except Exception as e:
                error_str = str(e)
                groq_error = f"Erro ao gerar com Groq: {error_str}"
                log("ERROR", groq_error)
                print(f"[ERROR] [REQ-{request_id}] {groq_error}")
                print(f"[ERROR] [REQ-{request_id}] Traceback completo: {traceback.format_exc()}")
                print(f"[ERROR] [REQ-{request_id}] Modelo usado: llama-3.1-8b-instant")
                print(f"[ERROR] [REQ-{request_id}] Tamanho do prompt: {len(full_user_prompt)} chars")
                print(f"[ERROR] [REQ-{request_id}] Tamanho do system prompt: {len(master_prompt)} chars")
                print(f"[ERROR] [REQ-{request_id}] Contexto RAG disponível: {len(context_snippet)} chars")
                
                # Importar status aqui para evitar problemas de escopo
                from fastapi import status as http_status
                
                # Verificar se é erro de API key inválida
                if "401" in error_str or "Invalid API Key" in error_str or "invalid_api_key" in error_str:
                    error_detail = (
                        f"Chave da API do Groq inválida ou expirada. "
                        f"Verifique se GROQ_API_KEY está correta no arquivo backend/.env. "
                        f"Para obter uma nova chave: https://console.groq.com/ "
                        f"Request ID: {request_id}"
                    )
                    raise HTTPException(
                        status_code=http_status.HTTP_401_UNAUTHORIZED,
                        detail=error_detail
                    )
                else:
                    # Outros erros
                    raise HTTPException(
                        status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Erro ao gerar interpretação com Groq: {error_str}. Verifique os logs para mais detalhes. Request ID: {request_id}"
                    )
        
        # Se Groq não está disponível, retornar erro
        if not groq_client:
            error_summary = f"""
[ERROR] [REQ-{request_id}] Não foi possível gerar interpretação - Groq não disponível

Diagnóstico:
- RAG Service: {'Disponível' if rag_service else 'NÃO DISPONÍVEL'}
- RAG Index: {'Disponível' if has_index else 'NÃO DISPONÍVEL'}
- Groq Client: NÃO DISPONÍVEL
- RAG Results: {len(rag_results)} resultados

Erros encontrados:
- RAG Error: {rag_error or 'Nenhum'}
- RAG Status Error: {rag_status_error or 'Nenhum'}
- RAG Search Error: {rag_search_error or 'Nenhum'}
- Groq Error: {groq_error or 'Nenhum'}

Ação necessária:
1. Verifique se GROQ_API_KEY está configurada nas variáveis de ambiente
2. Verifique se RAG_SERVICE_URL está configurada e o serviço está rodando
3. Verifique os logs acima para mais detalhes
"""
            print(error_summary)
            log("ERROR", "Não foi possível gerar - Groq não disponível")
            
            # Importar status aqui para evitar problemas de escopo
            from fastapi import status as http_status
            
            # Mensagem mais clara para o usuário
            if "não configurada" in (groq_error or "").lower():
                error_detail = (
                    f"Chave da API do Groq não configurada. "
                    f"Configure GROQ_API_KEY no arquivo backend/.env. "
                    f"Para obter uma chave: https://console.groq.com/ "
                    f"Request ID: {request_id}"
                )
            else:
                error_detail = (
                    f"Serviço Groq não disponível: {groq_error or 'Erro desconhecido'}. "
                    f"Verifique se GROQ_API_KEY está configurada corretamente. "
                    f"Request ID: {request_id}"
                )
            
            raise HTTPException(
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_detail
            )
        error_msg_pt = f"""Não foi possível gerar a análise completa no momento. 

**Dados do seu mapa astral:**
- Sol: {request.sunSign}
- Lua: {request.moonSign}
- Ascendente: {request.ascendant}

**Status do sistema:** Alguns serviços podem estar temporariamente indisponíveis.

**Recomendações:**
1. Verifique sua conexão com a internet
2. Aguarde alguns instantes e tente novamente
3. Se o problema persistir, entre em contato com o suporte
4. Acesse `/api/birth-chart/diagnostics` para verificar o status dos serviços

**Request ID:** {request_id}"""
        
        error_msg_en = f"""Could not generate the complete analysis at this time.

**Your birth chart data:**
- Sun: {request.sunSign}
- Moon: {request.moonSign}
- Ascendant: {request.ascendant}

**System status:** Some services may be temporarily unavailable.

**Recommendations:**
1. Check your internet connection
2. Wait a few moments and try again
3. If the problem persists, contact support
4. Access `/api/birth-chart/diagnostics` to check service status

**Request ID:** {request_id}"""
        
        error_msg = error_msg_pt if lang == 'pt' else error_msg_en
        return FullBirthChartResponse(
            section=request.section,
            title=title,
            content=error_msg,
            generated_by="error"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Importar status aqui para evitar problemas de escopo
        from fastapi import status as http_status
        try:
            log("ERROR", f"Erro crítico ao gerar seção do mapa: {str(e)}")
            log("ERROR", f"Traceback completo: {traceback.format_exc()}")
        except:
            # Se log falhar, apenas imprimir
            print(f"[ERROR] [REQ-{request_id}] Erro crítico ao gerar seção do mapa: {str(e)}")
            print(f"[ERROR] [REQ-{request_id}] Traceback completo: {traceback.format_exc()}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar seção do mapa: {str(e)}. Request ID: {request_id}. Verifique os logs para mais detalhes."
        )


@router.post("/full-birth-chart/all", response_model=FullBirthChartSectionsResponse)
async def generate_full_birth_chart(
    request: FullBirthChartRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Gera o Mapa Astral Completo com todas as seções.
    
    Esta é a análise mais completa do sistema, gerando:
    1. A Estrutura de Poder (Temperamento e Motivação)
    2. A Tríade Fundamental (O Núcleo da Personalidade)
    3. Dinâmica Pessoal e Ferramentas (Planetas Pessoais)
    4. Análise Setorial Avançada (Vida Prática e Casas)
    5. Expansão, Estrutura e Karma (Planetas Sociais e Transpessoais)
    6. Síntese e Orientação Estratégica
    """
    try:
        sections_to_generate = ['power', 'triad', 'personal', 'houses', 'karma', 'synthesis']
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


# ===== REVOLUÇÃO SOLAR =====

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


@router.post("/solar-return/calculate")
def calculate_solar_return_chart(
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
        from datetime import datetime
        
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
    Obtém interpretação da Revolução Solar usando o prompt fornecido.
    
    Body:
    {
        "natal_sun_sign": "Áries",
        "solar_return_ascendant": "Leão",
        "solar_return_sun_house": 5,
        "solar_return_moon_sign": "Câncer",
        "solar_return_moon_house": 4,
        "solar_return_venus_sign": "Libra",
        "solar_return_venus_house": 7,
        "solar_return_mars_sign": "Escorpião",
        "solar_return_mars_house": 8,
        "solar_return_jupiter_sign": "Sagitário",
        "solar_return_jupiter_house": 9,
        "solar_return_saturn_sign": "Capricórnio",
        "solar_return_midheaven": "Áries",
        "target_year": 2025,
        "language": "pt"
    }
    """
    try:
        rag_service = get_rag_service()
        lang = request.language or 'pt'
        
        # RECALCULAR DADOS SE DISPONÍVEL (FONTE ÚNICA DE VERDADE)
        # Se dados de nascimento estiverem disponíveis, recalcular revolução solar
        recalculated_data = None
        if (request.birth_date and request.birth_time and 
            request.latitude is not None and request.longitude is not None):
            try:
                print(f"[SOLAR RETURN] Recalculando dados usando Swiss Ephemeris...")
                birth_date = datetime.fromisoformat(request.birth_date.replace('Z', '+00:00'))
                
                recalculated_data = calculate_solar_return(
                    birth_date=birth_date,
                    birth_time=request.birth_time,
                    latitude=request.latitude,
                    longitude=request.longitude,
                    target_year=request.target_year
                )
                print(f"[SOLAR RETURN] Dados recalculados com sucesso. Precisão: {recalculated_data.get('sun_return_precision', 'N/A')} graus")
            except Exception as e:
                print(f"[WARNING] Erro ao recalcular revolução solar: {e}. Usando dados fornecidos.")
                recalculated_data = None
        
        # Usar dados recalculados se disponível, senão usar dados fornecidos
        solar_return_ascendant = recalculated_data.get("ascendant_sign") if recalculated_data else request.solar_return_ascendant
        solar_return_sun_house = recalculated_data.get("sun_house") if recalculated_data else request.solar_return_sun_house
        solar_return_moon_sign = recalculated_data.get("moon_sign") if recalculated_data else request.solar_return_moon_sign
        solar_return_moon_house = recalculated_data.get("moon_house") if recalculated_data else request.solar_return_moon_house
        solar_return_venus_sign = recalculated_data.get("venus_sign") if recalculated_data else request.solar_return_venus_sign
        solar_return_venus_house = recalculated_data.get("venus_house") if recalculated_data else request.solar_return_venus_house
        solar_return_mars_sign = recalculated_data.get("mars_sign") if recalculated_data else request.solar_return_mars_sign
        solar_return_mars_house = recalculated_data.get("mars_house") if recalculated_data else request.solar_return_mars_house
        solar_return_jupiter_sign = recalculated_data.get("jupiter_sign") if recalculated_data else request.solar_return_jupiter_sign
        solar_return_jupiter_house = recalculated_data.get("jupiter_house") if recalculated_data else request.solar_return_jupiter_house
        solar_return_saturn_sign = recalculated_data.get("saturn_sign") if recalculated_data else request.solar_return_saturn_sign
        solar_return_midheaven = recalculated_data.get("midheaven_sign") if recalculated_data else request.solar_return_midheaven
        
        # Validar que temos dados mínimos necessários
        if not solar_return_ascendant or not solar_return_sun_house or not solar_return_moon_sign or not solar_return_moon_house:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dados insuficientes para interpretação. Forneça dados da revolução solar ou dados de nascimento para recálculo."
            )
        
        # Verificar se o Groq está disponível
        groq_client = _get_groq_client()
        has_groq = groq_client is not None
        print(f"[SOLAR RETURN] Groq disponível: {has_groq}")
        if not has_groq:
            print(f"[SOLAR RETURN] AVISO: Groq client não está disponível.")
            print(f"[SOLAR RETURN] Verificando configuração...")
            from app.core.config import settings
            groq_key_set = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip())
            print(f"[SOLAR RETURN] GROQ_API_KEY configurada: {groq_key_set}")
            if groq_key_set:
                print(f"[SOLAR RETURN] GROQ_API_KEY tem {len(settings.GROQ_API_KEY)} caracteres")
                print(f"[SOLAR RETURN] Possível problema: RAG service não inicializou o Groq corretamente")
        
        # Construir dados do mapa natal (base)
        natal_data_summary = f"""Signo Solar Natal: {request.natal_sun_sign}"""
        if request.natal_ascendant:
            natal_data_summary += f"\nAscendente Natal: {request.natal_ascendant}"
        # Nota: Aspectos tensos principais seriam calculados se tivéssemos mais dados do mapa natal
        # Por enquanto, focamos no que temos disponível
        
        # Construir dados da revolução solar (usando dados validados/recalculados)
        solar_return_data = f"""Ascendente da Revolução Solar (RS): {solar_return_ascendant}
Casa onde cai o Sol na RS: Casa {solar_return_sun_house}
Lua na RS (Signo e Casa): {solar_return_moon_sign} na Casa {solar_return_moon_house}"""
        
        if solar_return_venus_sign:
            solar_return_data += f"\nVênus na RS: {solar_return_venus_sign}{f' na Casa {solar_return_venus_house}' if solar_return_venus_house else ''}"
        
        if solar_return_mars_sign:
            solar_return_data += f"\nMarte na RS: {solar_return_mars_sign}{f' na Casa {solar_return_mars_house}' if solar_return_mars_house else ''}"
        
        if solar_return_jupiter_sign:
            solar_return_data += f"\nJúpiter na RS: {solar_return_jupiter_sign}{f' na Casa {solar_return_jupiter_house}' if solar_return_jupiter_house else ''}"
        
        if solar_return_midheaven:
            solar_return_data += f"\nMeio do Céu da RS: {solar_return_midheaven}"
        
        if solar_return_saturn_sign:
            solar_return_data += f"\nSaturno na RS: {solar_return_saturn_sign}"
        
        # Calcular em qual Casa Natal cai o Ascendente da RS (sobreposição)
        # Nota: Isso requereria cálculo astrológico completo. Por enquanto, deixamos o prompt orientar o modelo
        # a considerar essa sobreposição se os dados estiverem disponíveis
        
        # Prompt baseado no novo formato fornecido
        if lang == 'pt':
            system_prompt = """Você é um Astrólogo Sênior e Estrategista de Ciclos Pessoais. Sua especialidade é a Síntese de Revolução Solar, integrando a psicologia profunda de Stephen Arroyo com a precisão técnica de Sakoian & Acker. Seu objetivo é fornecer um Planejamento Anual Estratégico, não apenas previsões soltas."""
            
            user_prompt = f"""Dados para Análise:

Mapa Natal (A Base): {natal_data_summary} (Foque nos aspectos tensos principais: Sol/Saturno, Lua/Plutão, etc.)

Revolução Solar (O Ano Vigente): {solar_return_data}

PROTOCOLO DE RACIOCÍNIO (O "ALGORITMO" INTERNO): Antes de gerar a resposta, processe estas etapas logicamente:

A Sobreposição (Overlay): Identifique em qual Casa do Mapa Natal cai o Ascendente da RS. Isso define o "Palco" do ano.

A Verificação de Padrão (Dica de Mestre): Compare os aspectos da RS com o Natal. Se um aspecto tenso (quadratura/oposição/conjunção) se repetir (ex: Natal tem Sol-Saturno e RS também tem), isso se torna o foco principal da seção 7.

Angularidade: Se houver planetas nos ângulos da RS (Casas 1, 4, 7, 10), aumente o peso deles na interpretação.

ESTRUTURA DA LEITURA (OUTPUT FINAL):

Siga rigorosamente a formatação e as restrições de conteúdo de cada seção para evitar redundância.

1. O Cenário do Ano (A Sobreposição do Ascendente)
   FOCUS EXCLUSIVO: A atmosfera geral e a "roupa" que a pessoa vestirá.
   - Explique a energia do Signo Ascendente da RS como a ferramenta comportamental do ano.
   - A Conexão Natal: Explique especificamente como este Ascendente afeta a Casa Natal onde ele cai (Ex: "Sua atitude de Áries este ano ativará sua Casa 4 Natal de família...").
   - Defina a postura mental necessária para este ciclo.
   - Restrição: NÃO fale de eventos específicos, trabalho ou amor aqui. Fale de atitude.

2. O Foco da Consciência (O Sol na Casa da RS)
   FOCUS EXCLUSIVO: A área da vida que exige presença e vitalidade.
   - Analise a Casa da RS onde o Sol está posicionado (Casa {solar_return_sun_house}). Esta é a "Missão do Ano".
   - Explique por que essa área drenará mais energia e onde a pessoa brilhará mais.
   - Dê uma estratégia de decisão: O que priorizar nesta área específica.
   - Restrição: NÃO repita informações sobre o temperamento do Ascendente.

3. O Clima Emocional (A Lua da RS)
   FOCUS EXCLUSIVO: Nutrição, instabilidade e vida doméstica.
   - Interprete o Signo e a Casa da Lua na RS ({solar_return_moon_sign} na Casa {solar_return_moon_house}).
   - Identifique a área onde a pessoa estará mais irracional ou flutuante (visão de Arroyo).
   - Indique onde ela encontrará refúgio emocional seguro.
   - Restrição: NÃO mencione metas profissionais ou financeiras aqui.

4. Relacionamentos e Valores (Vênus na RS)
   FOCUS EXCLUSIVO: Trocas afetivas, prazer e magnetismo social.
   - Interprete a posição de Vênus ({solar_return_venus_sign if solar_return_venus_sign else 'não disponível'}{f' na Casa {solar_return_venus_house}' if solar_return_venus_house else ''}) para definir o "sabor" das interações sociais.
   - O que a pessoa valorizará mais nas parcerias este ano? (Liberdade? Segurança? Status?).
   - Se Vênus estiver retrógrado, adicione um alerta sobre revisões afetivas.
   - Restrição: NÃO misture com as necessidades emocionais lunares (tópico 3).

5. Estratégia Profissional e Financeira (Marte, Júpiter e MC)
   FOCUS EXCLUSIVO: Ação, expansão, dinheiro e metas públicas.
   - Use Marte ({solar_return_mars_sign if solar_return_mars_sign else 'não disponível'}{f' na Casa {solar_return_mars_house}' if solar_return_mars_house else ''}) para indicar onde aplicar força e coragem.
   - Use Júpiter ({solar_return_jupiter_sign if solar_return_jupiter_sign else 'não disponível'}{f' na Casa {solar_return_jupiter_house}' if solar_return_jupiter_house else ''}) para indicar onde haverá sorte ou facilidade de expansão.
   - Analise o Meio do Céu da RS ({solar_return_midheaven if solar_return_midheaven else 'não disponível'}) para definir a meta pública do ano.
   - Restrição: Se Marte/Júpiter estiverem na Casa 6 ou 7, foque apenas no impacto deles na carreira/ação, não na saúde ou casamento.

6. Saúde e Rotina (Casa 6 da RS)
   FOCUS EXCLUSIVO: Manutenção do corpo e organização diária.
   - Analise o signo da cúspide da Casa 6 e planetas ali presentes.
   - Conecte a vitalidade física com a demanda energética do ano.
   - Sugira um hábito ou ajuste de rotina específico para este ciclo.
   - Restrição: Não fale de doenças graves (tema de Saturno/Casa 8), fale de manutenção e rotina.

7. O Grande Teste e a Dica de Mestre (Saturno e Repetições)
   FOCUS EXCLUSIVO: O maior desafio, a lição kármica e a maturação.
   - Localize Saturno na RS ({solar_return_saturn_sign if solar_return_saturn_sign else 'não disponível'}): Onde a vida vai pedir paciência, restrição e estrutura?
   - ALERTA DE REPETIÇÃO (CRÍTICO): Verifique se algum aspecto difícil do Mapa Natal se repete na RS. Se sim, escreva: "Alerta de Padrão Ativado: Este é um ano crítico para resolver seu problema crônico de [tema], pois o padrão natal foi reativado."
   - Transforme o desafio em uma oportunidade de mestria.
   - Restrição: Não repita os pequenos desafios do dia a dia (Casa 6), foque no grande aprendizado.

8. Síntese Estratégica
   FOCUS EXCLUSIVO: Resumo executivo para tomada de decisão.
   - Crie um "Mantra do Ano" em uma frase curta.
   - Liste as 3 Janelas de Oportunidade (resumo dos pontos fortes).
   - Finalize com uma mensagem curta de empoderamento.
   - Restrição: Não explique conceitos astrológicos aqui, apenas entregue o resumo prático.

IMPORTANTE:
- Use números (1., 2., 3., etc.) para os títulos, SEM asteriscos.
- Use parágrafos narrativos, não listas genéricas.
- Cada seção deve ter seu próprio "território" temático bem definido.
- NÃO repita informações entre seções.
- Use português brasileiro, linguagem terapêutica e empoderadora."""
        else:
            # English version - similar structure but adapted
            system_prompt = """You are a Senior Astrologer and Personal Cycles Strategist. Your specialty is Solar Return Synthesis, integrating Stephen Arroyo's deep psychology with Sakoian & Acker's technical precision. Your goal is to provide Strategic Annual Planning, not just loose predictions."""
            
            user_prompt = f"""Data for Analysis:

Natal Chart (The Base): {natal_data_summary} (Focus on main tense aspects: Sun/Saturn, Moon/Pluto, etc.)

Solar Return (The Current Year): {solar_return_data}

REASONING PROTOCOL (The Internal "ALGORITHM"): Before generating the response, process these steps logically:

The Overlay: Identify which House of the Natal Chart the Solar Return Ascendant falls into. This defines the "Stage" of the year.

Pattern Verification (Master Tip): Compare Solar Return aspects with Natal. If a tense aspect (square/opposition/conjunction) repeats (e.g., Natal has Sun-Saturn and SR also has it), this becomes the main focus of section 7.

Angularity: If there are planets in the angles of the SR (Houses 1, 4, 7, 10), increase their weight in the interpretation.

READING STRUCTURE (FINAL OUTPUT):

Follow strictly the formatting and content restrictions of each section to avoid redundancy.

1. The Year's Scenario (The Ascendant Overlay)
   EXCLUSIVE FOCUS: The general atmosphere and the "clothing" the person will wear.
   - Explain the Solar Return Ascendant sign's energy as the behavioral tool of the year.
   - The Natal Connection: Explain specifically how this Ascendant affects the Natal House where it falls (e.g., "Your Aries attitude this year will activate your Natal House 4 of family...").
   - Define the mental posture necessary for this cycle.
   - Restriction: Do NOT talk about specific events, work or love here. Talk about attitude.

2. The Focus of Consciousness (The Sun in the SR House)
   EXCLUSIVE FOCUS: The life area that demands presence and vitality.
   - Analyze the SR House where the Sun is positioned (House {request.solar_return_sun_house}). This is the "Mission of the Year".
   - Explain why this area will drain more energy and where the person will shine most.
   - Give a decision strategy: What to prioritize in this specific area.
   - Restriction: Do NOT repeat information about the Ascendant's temperament.

3. The Emotional Climate (The SR Moon)
   EXCLUSIVE FOCUS: Nourishment, instability and domestic life.
   - Interpret the Moon's Sign and House in the SR ({request.solar_return_moon_sign} in House {request.solar_return_moon_house}).
   - Identify the area where the person will be more irrational or fluctuating (Arroyo's view).
   - Indicate where they will find safe emotional refuge.
   - Restriction: Do NOT mention professional or financial goals here.

4. Relationships and Values (Venus in the SR)
   EXCLUSIVE FOCUS: Affective exchanges, pleasure and social magnetism.
   - Interpret Venus's position ({request.solar_return_venus_sign if request.solar_return_venus_sign else 'not available'}{f' in House {request.solar_return_venus_house}' if request.solar_return_venus_house else ''}) to define the "flavor" of social interactions.
   - What will the person value most in partnerships this year? (Freedom? Security? Status?).
   - If Venus is retrograde, add an alert about affective revisions.
   - Restriction: Do NOT mix with lunar emotional needs (topic 3).

5. Professional and Financial Strategy (Mars, Jupiter and MC)
   EXCLUSIVE FOCUS: Action, expansion, money and public goals.
   - Use Mars ({request.solar_return_mars_sign if request.solar_return_mars_sign else 'not available'}{f' in House {request.solar_return_mars_house}' if request.solar_return_mars_house else ''}) to indicate where to apply force and courage.
   - Use Jupiter ({request.solar_return_jupiter_sign if request.solar_return_jupiter_sign else 'not available'}{f' in House {request.solar_return_jupiter_house}' if request.solar_return_jupiter_house else ''}) to indicate where there will be luck or ease of expansion.
   - Analyze the SR Midheaven ({request.solar_return_midheaven if request.solar_return_midheaven else 'not available'}) to define the public goal of the year.
   - Restriction: If Mars/Jupiter are in House 6 or 7, focus only on their impact on career/action, not health or marriage.

6. Health and Routine (SR House 6)
   EXCLUSIVE FOCUS: Body maintenance and daily organization.
   - Analyze the cusp sign of House 6 and planets present there.
   - Connect physical vitality with the year's energy demand.
   - Suggest a specific habit or routine adjustment for this cycle.
   - Restriction: Do NOT talk about serious diseases (Saturn/House 8 theme), talk about maintenance and routine.

7. The Great Test and the Master Tip (Saturn and Repetitions)
   EXCLUSIVE FOCUS: The greatest challenge, the karmic lesson and maturation.
   - Locate Saturn in the SR ({request.solar_return_saturn_sign if request.solar_return_saturn_sign else 'not available'}): Where will life ask for patience, restriction and structure?
   - REPETITION ALERT (CRITICAL): Check if any difficult aspect from the Natal Chart repeats in the SR. If yes, write: "Pattern Alert Activated: This is a critical year to resolve your chronic problem of [theme], as the natal pattern was reactivated."
   - Transform the challenge into an opportunity for mastery.
   - Restriction: Do NOT repeat the small daily challenges (House 6), focus on the great learning.

8. Strategic Synthesis
   EXCLUSIVE FOCUS: Executive summary for decision making.
   - Create a "Year's Mantra" in a short sentence.
   - List the 3 Windows of Opportunity (summary of strengths).
   - End with a short message of empowerment.
   - Restriction: Do NOT explain astrological concepts here, just deliver the practical summary.

IMPORTANT:
- Use numbers (1., 2., 3., etc.) for titles, WITHOUT asterisks.
- Use narrative paragraphs, not generic lists.
- Each section must have its own well-defined thematic "territory".
- Do NOT repeat information between sections.
- Use therapeutic and empowering language."""
        
        # Buscar contexto do RAG com múltiplas queries para obter mais informações
        queries = [
            f"revolução solar retorno solar mapa anual interpretação {request.solar_return_ascendant} casa {request.solar_return_sun_house}",
            f"casa 6 saúde vitalidade bem-estar astrologia revolução solar",
            f"casa 6 planetas saúde corpo físico astrologia",
            f"ascendente {request.solar_return_ascendant} vitalidade saúde revolução solar"
        ]
        
        # Adicionar query específica sobre a casa 6 se houver planetas nela
        if request.solar_return_sun_house == 6:
            queries.append(f"Sol casa 6 saúde vitalidade energia física revolução solar")
        if request.solar_return_moon_house == 6:
            queries.append(f"Lua casa 6 saúde emocional bem-estar revolução solar")
        if request.solar_return_venus_house == 6:
            queries.append(f"Vênus casa 6 saúde beleza bem-estar revolução solar")
        if request.solar_return_mars_house == 6:
            queries.append(f"Marte casa 6 saúde energia física atividade revolução solar")
        if request.solar_return_jupiter_house == 6:
            queries.append(f"Júpiter casa 6 saúde expansão bem-estar revolução solar")
        
        # Buscar com todas as queries
        all_rag_results = []
        if rag_service:
            for q in queries:
                try:
                    results = rag_service.search(q, top_k=5)
                    all_rag_results.extend(results)
                except Exception as e:
                    print(f"[WARNING] Erro ao buscar no RAG com query '{q}': {e}")
        
        # Remover duplicatas mantendo os mais relevantes
        seen_texts = set()
        unique_results = []
        for result in sorted(all_rag_results, key=lambda x: x.get('score', 0), reverse=True):
            text_key = result.get('text', '')[:100]
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_results.append(result)
                if len(unique_results) >= 15:  # Limitar a 15 documentos únicos
                    break
        
        context_text = "\n\n".join([doc.get('text', '') for doc in unique_results[:12] if doc.get('text')])
        print(f"[SOLAR RETURN] Contexto RAG coletado: {len(context_text)} chars de {len(unique_results)} documentos")
        
        # Gerar interpretação com Groq
        groq_client = _get_groq_client()
        if groq_client:
            try:
                print(f"[SOLAR RETURN] Tentando gerar interpretação com Groq...")
                context_snippet = context_text[:3000] if context_text else "Informações gerais sobre revolução solar."
                
                full_user_prompt = f"""{user_prompt}

---

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_snippet}"""
                
                print(f"[SOLAR RETURN] Prompt length: {len(full_user_prompt)} chars")
                print(f"[SOLAR RETURN] System prompt length: {len(system_prompt)} chars")
                print(f"[SOLAR RETURN] Model: llama-3.3-70b-versatile")
                
                # Tentar chamar Groq com modelo principal
                models_to_try = [
                    "llama-3.3-70b-versatile",
                    "llama-3.2-90b-text-preview",
                    "llama-3.1-8b-instant",
                    "mixtral-8x7b-32768"
                ]
                
                interpretation_text = None
                last_error = None
                
                for model_name in models_to_try:
                    try:
                        print(f"[SOLAR RETURN] Tentando modelo: {model_name}")
                        chat_completion = groq_client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": full_user_prompt}
                            ],
                            model=model_name,
                            temperature=0.7,
                            max_tokens=4000,
                            top_p=0.9,
                        )
                        
                        interpretation_text = chat_completion.choices[0].message.content.strip()
                        
                        # Aplicar filtro de deduplicação
                        interpretation_text = _deduplicate_text(interpretation_text)
                        
                        print(f"[SOLAR RETURN] Sucesso com modelo {model_name}: {len(interpretation_text)} chars (após limpeza)")
                        break
                        
                    except Exception as model_error:
                        print(f"[SOLAR RETURN] Erro com modelo {model_name}: {model_error}")
                        last_error = model_error
                        continue
                
                if interpretation_text and len(interpretation_text) > 100:
                    # Converter sources para o formato correto
                    sources_list = [
                        SourceItem(
                            source=r.get('source', 'knowledge_base'),
                            page=r.get('page', 1),
                            relevance=r.get('score', 0.5)
                        )
                        for r in unique_results[:5]
                    ]
                    
                    # Aplicar filtro de deduplicação
                    interpretation_text = _deduplicate_text(interpretation_text)
                    
                    return InterpretationResponse(
                        interpretation=interpretation_text,
                        sources=sources_list,
                        query_used=f"Múltiplas queries: {', '.join(queries[:3])}...",
                        generated_by="groq"
                    )
                elif interpretation_text:
                    print(f"[SOLAR RETURN] Interpretação muito curta ({len(interpretation_text)} chars), usando fallback")
                else:
                    print(f"[SOLAR RETURN] Todos os modelos falharam. Último erro: {last_error}")
                    if last_error:
                        raise last_error
                
            except Exception as e:
                print(f"[ERROR] Erro geral ao gerar interpretação com Groq: {e}")
                import traceback
                print(f"[ERROR] Traceback: {traceback.format_exc()}")
        else:
            print(f"[SOLAR RETURN] Groq client não disponível")
        
        # Fallback: tentar usar o método get_interpretation do RAG service
        print(f"[SOLAR RETURN] Usando fallback - tentando método get_interpretation do RAG service")
        try:
            # Construir query mais completa incluindo informações sobre casa 6
            fallback_queries = [
                f"revolução solar retorno solar {request.solar_return_ascendant} casa {request.solar_return_sun_house} {request.solar_return_moon_sign} interpretação anual",
                f"casa 6 saúde vitalidade {request.solar_return_ascendant} revolução solar"
            ]
            
            # Tentar cada query
            for fallback_query in fallback_queries:
                try:
                    if not rag_service:
                        continue
                    fallback_result = rag_service.get_interpretation(
                        custom_query=fallback_query,
                        use_groq=True,
                        category='astrology'  # Garantir que use apenas documentos de astrologia
                    )
                    
                    if fallback_result and fallback_result.get('interpretation') and len(fallback_result['interpretation']) > 200:
                        print(f"[SOLAR RETURN] Fallback com RAG service funcionou: {len(fallback_result['interpretation'])} chars")
                        # Converter sources para o formato correto
                        sources_list = []
                        for src in fallback_result.get('sources', []):
                            if isinstance(src, dict):
                                sources_list.append(SourceItem(
                                    source=src.get('source', 'unknown'),
                                    page=src.get('page', 1),
                                    relevance=src.get('relevance') or src.get('score')
                                ))
                        
                        # Aplicar filtro de deduplicação
                        fallback_interpretation = _deduplicate_text(fallback_result['interpretation'])
                        
                        return InterpretationResponse(
                            interpretation=fallback_interpretation,
                            sources=sources_list,
                            query_used=fallback_query,
                            generated_by=fallback_result.get('generated_by', 'rag_fallback')
                        )
                except Exception as query_error:
                    print(f"[SOLAR RETURN] Erro com query '{fallback_query}': {query_error}")
                    continue
        except Exception as e:
            print(f"[ERROR] Erro no fallback RAG service: {e}")
        
        # Último fallback: interpretação básica melhorada
        print(f"[SOLAR RETURN] Usando último fallback - interpretação básica")
        
        # Construir texto de fallback mais completo
        fallback_parts = []
        
        fallback_parts.append(f"""**1. A "Vibe" do Ano (O Ascendente Anual):**

O Ascendente da Revolução Solar em **{request.solar_return_ascendant}** define a energia geral que permeará todo o seu ano. Este signo funciona como uma "armadura" ou "lente" através da qual você experimentará e responderá aos eventos do período. As características de {request.solar_return_ascendant} serão suas ferramentas naturais para navegar pelos desafios e oportunidades que surgirem.

Este posicionamento indica que você terá a oportunidade de desenvolver e expressar as qualidades típicas de {request.solar_return_ascendant} de forma mais consciente. Esta energia será especialmente útil quando você precisar tomar decisões importantes ou enfrentar situações que exijam as características deste signo.""")
        
        # Descrições das casas
        house_descriptions = {
            1: "identidade, autoconfiança e novos começos",
            2: "valores, recursos financeiros e segurança material",
            3: "comunicação, aprendizado e relações próximas",
            4: "lar, família e raízes",
            5: "criatividade, romance e expressão pessoal",
            6: "rotina, saúde e trabalho diário",
            7: "parcerias, relacionamentos e compromissos",
            8: "transformação, intimidade e recursos compartilhados",
            9: "filosofia, viagens e expansão de horizontes",
            10: "carreira, reconhecimento público e vocação",
            11: "amizades, grupos e projetos futuros",
            12: "introspecção, espiritualidade e processos inconscientes"
        }
        
        sun_house_desc = house_descriptions.get(request.solar_return_sun_house, "uma área importante da sua vida")
        
        fallback_parts.append(f"""**2. O Foco da Consciência (O Sol nas Casas):**

Enquanto o Ascendente define a energia geral, o Sol na **Casa {request.solar_return_sun_house}** indica especificamente onde você direcionará sua atenção e energia vital durante este ano. A Casa {request.solar_return_sun_house} está relacionada a {sun_house_desc}, e é neste setor que você encontrará suas maiores oportunidades de realização pessoal.

Este posicionamento sugere que seus esforços conscientes devem ser direcionados para esta área. É aqui que você poderá expressar sua autenticidade e alcançar resultados significativos. Considere projetos, iniciativas ou mudanças relacionadas a este setor da vida.""")
        
        moon_house_desc = house_descriptions.get(request.solar_return_moon_house, "uma área emocional importante")
        
        fallback_parts.append(f"""**3. O Mundo Emocional e a Família (A Lua):**

Complementando o foco do Sol, a Lua em **{request.solar_return_moon_sign}** na **Casa {request.solar_return_moon_house}** revela suas necessidades emocionais e como você buscará segurança e nutrição interior. A Casa {request.solar_return_moon_house} está relacionada a {moon_house_desc}, indicando onde você encontrará conforto emocional.

Este posicionamento mostra que suas reações emocionais e necessidades de cuidado estarão especialmente conectadas a esta área. Preste atenção aos seus sentimentos e intuições relacionadas a este setor, pois eles serão guias importantes para seu bem-estar. Atividades e conexões relacionadas a esta casa serão especialmente nutritivas para sua alma.""")
        
        if request.solar_return_venus_sign:
            venus_house_info = f' na Casa {request.solar_return_venus_house}' if request.solar_return_venus_house else ''
            fallback_parts.append(f"""**4. Amor, Relacionamentos e Vida Social (Vênus):**

Vênus em **{request.solar_return_venus_sign}**{venus_house_info} traz uma perspectiva específica sobre como você buscará harmonia e conexões afetivas este ano. Este posicionamento revela seus valores relacionais e como você expressa e recebe amor, complementando as áreas já mencionadas pelo Sol e pela Lua.

Este ano, suas relações serão influenciadas pelas características de {request.solar_return_venus_sign}, indicando o tipo de energia que você atrairá e oferecerá nos relacionamentos. Preste atenção aos valores que você prioriza nas conexões humanas.""")
        
        # Construir seção de trabalho/carreira de forma integrada
        career_section = "**5. Trabalho, Dinheiro e Carreira (Marte, Júpiter e Meio do Céu):**\n\n"
        
        if request.solar_return_mars_sign:
            mars_house_info = f' na Casa {request.solar_return_mars_house}' if request.solar_return_mars_house else ''
            career_section += f"Marte em **{request.solar_return_mars_sign}**{mars_house_info} indica onde você colocará sua força de ação e iniciativa. Este é o setor onde você terá energia para trabalhar ativamente e conquistar objetivos práticos.\n\n"
        
        if request.solar_return_jupiter_sign:
            jupiter_house_info = f' na Casa {request.solar_return_jupiter_house}' if request.solar_return_jupiter_house else ''
            career_section += f"Júpiter em **{request.solar_return_jupiter_sign}**{jupiter_house_info} mostra onde você encontrará expansão, sorte e oportunidades de crescimento. Este setor oferece potencial para desenvolvimento e prosperidade.\n\n"
        
        if request.solar_return_midheaven:
            career_section += f"O **Meio do Céu em {request.solar_return_midheaven}** representa sua meta de vida e vocação para este ano. Esta direção profissional indica o caminho de realização pessoal que você deve seguir, integrando as energias de Marte e Júpiter mencionadas acima."
        
        if request.solar_return_mars_sign or request.solar_return_jupiter_sign or request.solar_return_midheaven:
            fallback_parts.append(career_section)
        
        # Análise específica da Casa 6 e Saúde
        planets_in_6 = []
        planet_details_6 = []
        
        if request.solar_return_sun_house == 6:
            planets_in_6.append("Sol")
            planet_details_6.append(f"O **Sol na Casa 6** indica que sua energia vital e identidade estarão focadas em saúde, rotinas e bem-estar físico. Este é um ano para investir conscientemente em hábitos saudáveis e criar rotinas que fortaleçam sua vitalidade.")
        
        if request.solar_return_moon_house == 6:
            planets_in_6.append("Lua")
            planet_details_6.append(f"A **Lua na Casa 6** mostra que suas necessidades emocionais estarão conectadas à sua saúde física e rotinas diárias. Preste atenção à conexão entre seu bem-estar emocional e físico. Cuidar da alimentação e do descanso será especialmente importante.")
        
        if request.solar_return_venus_house == 6:
            planets_in_6.append("Vênus")
            planet_details_6.append(f"**Vênus na Casa 6** indica que você buscará harmonia e beleza através de práticas de bem-estar. Considere atividades que combinem estética e saúde, como dança, yoga ou cuidados com a alimentação equilibrada.")
        
        if request.solar_return_mars_house == 6:
            planets_in_6.append("Marte")
            planet_details_6.append(f"**Marte na Casa 6** traz energia ativa para sua saúde e rotinas. Este é um ano ideal para iniciar ou intensificar atividades físicas. Use essa energia para criar disciplina em seus hábitos de saúde, mas evite exageros.")
        
        if request.solar_return_jupiter_house == 6:
            planets_in_6.append("Júpiter")
            planet_details_6.append(f"**Júpiter na Casa 6** traz expansão e oportunidades para melhorar sua saúde e bem-estar. Este é um ano favorável para explorar novas práticas de saúde, expandir seus conhecimentos sobre bem-estar ou encontrar profissionais que possam ajudar em sua jornada de saúde.")
        
        # Construir seção de Saúde e Vitalidade
        health_section = f"""**6. Saúde e Vitalidade:**

Além das áreas já mencionadas, a Casa 6 da sua Revolução Solar traz atenção especial para saúde física, rotinas diárias e bem-estar geral. Este setor complementa as energias do Sol, Lua e outros planetas, focando especificamente nos cuidados práticos com o corpo e na manutenção da vitalidade."""

        if planets_in_6:
            health_section += f"\n\nA Casa 6 está ativada com {', '.join(planets_in_6)} presente(s), indicando que esta será uma área de atenção especial neste ano:\n\n"
            health_section += "\n\n".join(planet_details_6)
            health_section += f"\n\nCom múltiplos planetas na Casa 6, você terá oportunidades significativas de transformar seus hábitos de saúde e criar rotinas mais equilibradas e benéficas."
        else:
            # Buscar informações sobre o regente da Casa 6
            # Para simplificar, vamos focar no Ascendente e na energia geral
            health_section += f"\n\nCom o Ascendente em **{request.solar_return_ascendant}**, você naturalmente buscará equilíbrio e harmonia, o que se reflete também na sua abordagem à saúde. Este é um ano para criar rotinas que integrem bem-estar físico, mental e emocional de forma harmoniosa."
        
        health_section += f"\n\n**Sugestões Práticas de Bem-estar:**\n"
        health_section += f"- Pratique atividades que promovam equilíbrio e harmonia (yoga, tai chi, meditação)\n"
        health_section += f"- Crie rotinas diárias que incluam momentos de autocuidado\n"
        health_section += f"- Preste atenção à conexão entre suas emoções e sua saúde física\n"
        health_section += f"- Considere práticas que integrem movimento, respiração e consciência corporal\n"
        health_section += f"- Mantenha um ritmo equilibrado, evitando extremos ou exageros"
        
        fallback_parts.append(health_section)
        
        # Seção de Desafios como Oportunidades
        if request.solar_return_saturn_sign:
            fallback_parts.append(f"""**7. Os Desafios como Oportunidades (Saturnos e Tensões):**

Integrando todas as áreas mencionadas, Saturno em **{request.solar_return_saturn_sign}** indica onde você encontrará os principais desafios deste ano. Estes desafios, quando encarados com consciência, se transformam em oportunidades de amadurecimento e construção de mestria.

Onde Saturno toca, nós construímos. Este posicionamento oferece a chance de desenvolver disciplina, responsabilidade e estrutura em áreas específicas, complementando as oportunidades de crescimento já identificadas nas seções anteriores.""")
        
        # Síntese que integra sem repetir
        synthesis_blessings = []
        if request.solar_return_ascendant:
            synthesis_blessings.append(f"A energia de **{request.solar_return_ascendant}** como guia para suas ações")
        if request.solar_return_sun_house:
            sun_house_name = house_descriptions.get(request.solar_return_sun_house, "área de foco")
            synthesis_blessings.append(f"O desenvolvimento na área de {sun_house_name} (Casa {request.solar_return_sun_house})")
        if request.solar_return_moon_sign:
            synthesis_blessings.append(f"A nutrição emocional através de **{request.solar_return_moon_sign}**")
        
        # Se não houver bênçãos suficientes, adicionar genéricas
        while len(synthesis_blessings) < 3:
            if len(synthesis_blessings) == 0:
                synthesis_blessings.append("Oportunidades de crescimento pessoal e espiritual")
            elif len(synthesis_blessings) == 1:
                synthesis_blessings.append("A capacidade de transformar desafios em aprendizados")
            else:
                synthesis_blessings.append("A integração harmoniosa de todas as áreas da vida")
        
        fallback_parts.append(f"""**8. Síntese Inspiradora:**

**Mantra do Ano:** "Crescimento consciente através da integração das energias disponíveis"

**As 3 Grandes Bênçãos que Estão Chegando:**
1. {synthesis_blessings[0]}
2. {synthesis_blessings[1]}
3. {synthesis_blessings[2]}

Este ano oferece uma jornada única de autoconhecimento e realização. Cada área mencionada trabalha em conjunto para criar uma experiência completa e transformadora. Use estas informações como um mapa, não como um destino fixo, e permita-se crescer através das oportunidades que surgirem.""")
        
        fallback_parts.append(f"""*Nota: Esta é uma interpretação básica. Para uma análise completa e personalizada, recomenda-se consultar um astrólogo profissional ou aguardar a disponibilidade do serviço de interpretação avançada.*""")
        
        fallback_text = "\n\n".join(fallback_parts)
        
        # Construir query usada para o fallback
        fallback_query = f"revolução solar {request.solar_return_ascendant} casa {request.solar_return_sun_house} {request.solar_return_moon_sign}"
        
        # Aplicar filtro de deduplicação no fallback
        fallback_text = _deduplicate_text(fallback_text)
        
        return InterpretationResponse(
            interpretation=fallback_text,
            sources=[],
            query_used=fallback_query,
            generated_by="fallback"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter interpretação da revolução solar: {str(e)}"
        )


# ============================================================================
# NUMEROLOGY MAP ENDPOINT
# ============================================================================

class NumerologyMapRequest(BaseModel):
    """Request para calcular mapa numerológico."""
    pass  # Usa dados do usuário autenticado


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
    birth_grid: Dict[str, Any]  # Inclui grid, arrows_strength, arrows_weakness, missing_numbers
    life_cycle: Dict[str, Any]
    karmic_debts: List[int]


@router.get("/numerology/map", response_model=NumerologyMapResponse)
async def get_numerology_map(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Calcula o mapa numerológico completo do usuário autenticado.
    Usa o nome completo e data de nascimento do mapa astral primário.
    """
    import time
    start_time = time.time()
    
    try:
        print(f"[NUMEROLOGY] Iniciando cálculo do mapa numerológico...")
        
        # Obter usuário autenticado
        user = get_current_user(authorization, db)
        print(f"[NUMEROLOGY] Usuário obtido: {user.id if user else 'None'}")
        
        # Buscar mapa astral primário do usuário
        birth_chart = db.query(BirthChart).filter(
            BirthChart.user_id == user.id,
            BirthChart.is_primary == True
        ).first()
        
        if not birth_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapa astral não encontrado. Complete o onboarding primeiro."
            )
        
        print(f"[NUMEROLOGY] Mapa astral encontrado: {birth_chart.name}, {birth_chart.birth_date} (tipo: {type(birth_chart.birth_date)})")
        
        # Converter birth_date para datetime se necessário
        from datetime import datetime, date
        if isinstance(birth_chart.birth_date, datetime):
            birth_date = birth_chart.birth_date
        elif isinstance(birth_chart.birth_date, date):
            birth_date = datetime.combine(birth_chart.birth_date, datetime.min.time())
        elif isinstance(birth_chart.birth_date, str):
            # Tentar parsear string ISO
            try:
                birth_date = datetime.fromisoformat(birth_chart.birth_date.replace('Z', '+00:00'))
            except:
                # Tentar formato simples
                birth_date = datetime.strptime(birth_chart.birth_date.split('T')[0], '%Y-%m-%d')
        else:
            raise ValueError(f"Tipo de data não suportado: {type(birth_chart.birth_date)}")
        
        print(f"[NUMEROLOGY] Data convertida: {birth_date}")
        
        # Calcular mapa numerológico
        print(f"[NUMEROLOGY] Iniciando cálculo...")
        calculator = NumerologyCalculator()
        numerology_map = calculator.calculate_full_numerology_map(
            full_name=birth_chart.name,
            birth_date=birth_date
        )
        
        elapsed_time = time.time() - start_time
        print(f"[NUMEROLOGY] Cálculo concluído em {elapsed_time:.2f}s")
        
        return NumerologyMapResponse(**numerology_map)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        elapsed_time = time.time() - start_time
        print(f"[ERROR] Erro ao calcular mapa numerológico após {elapsed_time:.2f}s: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular mapa numerológico: {str(e)}"
        )


class NumerologyInterpretationRequest(BaseModel):
    """Request para interpretação numerológica."""
    language: Optional[str] = 'pt'


class NumerologyInterpretationResponse(BaseModel):
    """Response com interpretação numerológica completa."""
    interpretation: str
    sources: List[SourceItem]
    query_used: str
    generated_by: Optional[str] = None


@router.post("/numerology/interpretation", response_model=NumerologyInterpretationResponse)
async def get_numerology_interpretation(
    request: NumerologyInterpretationRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Gera interpretação numerológica completa usando RAG e Groq.
    Usa o prompt estruturado fornecido pelo usuário.
    """
    try:
        # Obter usuário autenticado
        user = get_current_user(authorization, db)
        
        # Buscar mapa astral primário
        birth_chart = db.query(BirthChart).filter(
            BirthChart.user_id == user.id,
            BirthChart.is_primary == True
        ).first()
        
        if not birth_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapa astral não encontrado. Complete o onboarding primeiro."
            )
        
        # Calcular mapa numerológico completo
        calculator = NumerologyCalculator()
        numerology_map = calculator.calculate_full_numerology_map(
            full_name=birth_chart.name,
            birth_date=birth_chart.birth_date
        )
        
        # Obter RAG service
        rag_service = get_rag_service()
        
        # Construir queries específicas para cada número e conceito
        queries = []
        
        # Query para Caminho de Vida - múltiplas variações
        queries.append(f"life path number {numerology_map['life_path']['number']} numerologia pitagórica significado missão")
        queries.append(f"caminho de vida {numerology_map['life_path']['number']} numerologia goodwin decoz")
        if numerology_map['life_path']['is_master']:
            queries.append(f"master number {numerology_map['life_path']['number']} numerologia")
            queries.append(f"número mestre {numerology_map['life_path']['number']} caminho de vida")
        
        # Query para Expressão/Destino - múltiplas variações
        queries.append(f"expression destiny number {numerology_map['destiny']['number']} numerologia talentos")
        queries.append(f"expressão destino {numerology_map['destiny']['number']} numerologia goodwin")
        if numerology_map['destiny']['is_master']:
            queries.append(f"master number {numerology_map['destiny']['number']} expressão")
            queries.append(f"número mestre {numerology_map['destiny']['number']} expressão destino")
        
        # Query para Desejo da Alma - múltiplas variações
        queries.append(f"soul desire heart number {numerology_map['soul']['number']} numerologia motivação")
        queries.append(f"desejo da alma {numerology_map['soul']['number']} numerologia decoz")
        if numerology_map['soul']['is_master']:
            queries.append(f"master number {numerology_map['soul']['number']} alma")
            queries.append(f"número mestre {numerology_map['soul']['number']} desejo coração")
        
        # Query para Personalidade - múltiplas variações
        queries.append(f"personality number {numerology_map['personality']['number']} numerologia máscara")
        queries.append(f"personalidade {numerology_map['personality']['number']} numerologia decoz máscara")
        if numerology_map['personality']['is_master']:
            queries.append(f"número mestre {numerology_map['personality']['number']} personalidade")
        
        # Query para Dia de Nascimento - múltiplas variações
        queries.append(f"birthday number {numerology_map['birthday']['number']} numerologia talento")
        queries.append(f"dia nascimento {numerology_map['birthday']['number']} numerologia")
        
        # Query para Maturidade - múltiplas variações
        queries.append(f"maturity number {numerology_map['maturity']['number']} numerologia segunda metade vida")
        queries.append(f"maturidade {numerology_map['maturity']['number']} numerologia")
        if numerology_map['maturity']['is_master']:
            queries.append(f"número mestre {numerology_map['maturity']['number']} maturidade")
        
        # Query para Ano Pessoal - múltiplas variações
        queries.append(f"personal year {numerology_map['personal_year']['number']} numerologia ciclo anual")
        queries.append(f"ano pessoal {numerology_map['personal_year']['number']} numerologia decoz")
        if numerology_map['personal_year']['is_master']:
            queries.append(f"número mestre {numerology_map['personal_year']['number']} ano pessoal")
        
        # Query para Pináculos - mais específicas
        for pinnacle in numerology_map['pinnacles']:
            queries.append(f"pinnacle number {pinnacle['number']} numerologia período {pinnacle['period']}")
            queries.append(f"pináculo {pinnacle['number']} goodwin numerologia significado")
        
        # Query para Desafios - mais específicas
        for challenge in numerology_map['challenges']:
            queries.append(f"challenge number {challenge['number']} numerologia obstáculo")
            queries.append(f"desafio {challenge['number']} decoz numerologia lição")
        
        # Query para identificar pináculo e desafio atuais baseado na idade
        current_age = numerology_map['life_cycle']['age']
        for pinnacle in numerology_map['pinnacles']:
            if pinnacle['start_age'] <= current_age and (pinnacle['end_age'] is None or current_age <= pinnacle['end_age']):
                queries.append(f"pináculo atual número {pinnacle['number']} período {pinnacle['period']} numerologia")
        for challenge in numerology_map['challenges']:
            if challenge['start_age'] <= current_age and (challenge['end_age'] is None or current_age <= challenge['end_age']):
                queries.append(f"desafio atual número {challenge['number']} período {challenge['period']} numerologia")
        
        # Query para Grade de Nascimento e Setas
        if numerology_map['birth_grid']['arrows_strength'] or numerology_map['birth_grid']['arrows_weakness']:
            queries.append("birth grid arrows numerologia setas força fraqueza")
        
        # Query para números faltantes (lições cármicas)
        if numerology_map['birth_grid']['missing_numbers']:
            for missing_num in numerology_map['birth_grid']['missing_numbers']:
                queries.append(f"karmic lesson number {missing_num} numerologia lição cármica")
        
        # Query para dívidas cármicas
        if numerology_map['karmic_debts']:
            for debt in numerology_map['karmic_debts']:
                queries.append(f"karmic debt number {debt} numerologia dívida cármica")
        
        # Query para ciclo de vida e Triângulo Divino
        queries.append(f"life cycle {numerology_map['life_cycle']['cycle']} number {numerology_map['life_cycle']['cycle_number']} numerologia triângulo divino")
        queries.append(f"triângulo divino javane bunker ciclo {numerology_map['life_cycle']['cycle']} número {numerology_map['life_cycle']['cycle_number']}")
        queries.append(f"divine triangle javane bunker {numerology_map['life_cycle']['cycle']} cycle number {numerology_map['life_cycle']['cycle_number']}")
        # Query específica para conexão Tarot/Planeta do ciclo
        queries.append(f"tarot arcano número {numerology_map['life_cycle']['cycle_number']} planeta regente numerologia")
        
        # Buscar contexto do RAG (apenas numerologia) - fazer múltiplas buscas
        context_documents = []
        seen_texts = set()  # Evitar duplicatas
        
        print(f"[NUMEROLOGY] Buscando no RAG com {len(queries)} queries específicas...")
        
        if rag_service:
            for query in queries:
                try:
                    results = rag_service.search(
                        query=query,
                        top_k=3,  # Menos resultados por query, mas mais queries
                        expand_query=False,  # Não expandir para manter foco
                        category='numerology'
                    )
                    
                    for doc in results:
                        doc_text = doc.get('text', '').strip()
                        if doc_text and doc_text not in seen_texts:
                            seen_texts.add(doc_text)
                            context_documents.append(doc)
                except Exception as e:
                    print(f"[WARNING] Erro ao buscar query '{query}': {e}")
                    continue
        
        # Ordenar por relevância (score) e limitar
        context_documents = sorted(
            context_documents,
            key=lambda x: x.get('score', 0),
            reverse=True
        )[:20]  # Top 20 documentos mais relevantes
        
        print(f"[NUMEROLOGY] Encontrados {len(context_documents)} documentos únicos do RAG")
        
        # Preparar contexto para o prompt
        context_text = "\n\n".join([
            f"[Fonte: {doc.get('source', 'unknown')} - Página {doc.get('page', 1)}]\n{doc.get('text', '')}"
            for doc in context_documents
            if doc.get('text')
        ])
        
        # Se não houver contexto, avisar e tentar busca mais genérica
        if not context_text or len(context_text.strip()) < 100:
            print("[WARNING] Pouco ou nenhum contexto numerológico encontrado no RAG!")
            print("[INFO] Tentando busca mais genérica...")
            
            # Tentar busca genérica de numerologia
            try:
                if rag_service:
                    generic_results = rag_service.search(
                        query="numerologia pitagórica significado números",
                        top_k=6,
                        expand_query=True,
                        category='numerology'
                    )
                else:
                    generic_results = []
                
                if generic_results:
                    context_text = "\n\n".join([
                        f"[Fonte: {doc.get('source', 'unknown')} - Página {doc.get('page', 1)}]\n{doc.get('text', '')}"
                        for doc in generic_results[:5]
                        if doc.get('text')
                    ])
                    print(f"[INFO] Busca genérica retornou {len(generic_results)} resultados")
            except Exception as e:
                print(f"[WARNING] Erro na busca genérica: {e}")
            
            if not context_text or len(context_text.strip()) < 100:
                context_text = context_text or "Informações numerológicas básicas disponíveis. Para interpretações mais profundas, reconstrua o índice RAG executando: python3 backend/scripts/rebuild_rag_index.py"
                print("[WARNING] Ainda sem contexto suficiente. O índice RAG pode precisar ser reconstruído.")
        
        # Construir prompt completo
        lang = request.language or 'pt'
        
        if lang == 'pt':
            system_prompt = """Você é um Numerólogo Pitagórico profissional e experiente, especializado em transformar números em narrativas profundas e terapêuticas. Sua missão é contar a história de vida única de cada pessoa através dos números, usando uma linguagem clara, acessível e envolvente.

SUA ABORDAGEM PROFISSIONAL:
Você sintetiza as melhores referências mundiais da numerologia:
- A precisão técnica e síntese de Matthew Oliver Goodwin
- A profundidade psicológica e terapêutica de Hans Decoz  
- A visão holística de saúde e bem-estar de David A. Phillips
- A geometria sagrada e ciclos de vida de Faith Javane & Dusty Bunker

REGRAS CRÍTICAS DE ESCRITA - LEIA COM ATENÇÃO:

🎯 MISSÃO PRINCIPAL: CONTAR UMA HISTÓRIA, NÃO LISTAR INFORMAÇÕES
- NÃO faça listas técnicas ou descrições secas de números
- CONTE uma narrativa fluida e envolvente, como se estivesse escrevendo a biografia numerológica desta pessoa
- Cada número deve ser apresentado como parte de uma história maior, conectando passado, presente e futuro
- Use metáforas, analogias e exemplos práticos do dia a dia para tornar os conceitos acessíveis
- Transforme cada conceito numerológico em uma história que a pessoa possa se reconhecer

📖 LINGUAGEM E ESTILO:
- Use TERMOS SIMPLES e de FÁCIL ENTENDIMENTO - explique qualquer termo técnico na primeira vez que aparecer
- Evite "numerologês" excessivo - se usar um termo técnico, explique imediatamente o que significa
- Escreva como se estivesse conversando com um amigo inteligente, não como um manual técnico
- Use linguagem rica e envolvente, mas sempre clara e acessível
- Cada parágrafo deve fluir naturalmente para o próximo, criando uma narrativa contínua

🔗 CONEXÃO E NARRATIVA:
- Conecte TODOS os números em uma história coesa - mostre como eles se relacionam
- Revele a jornada única desta pessoa através dos números
- Mostre como passado (lições cármicas), presente (ciclo atual) e futuro (maturidade) se conectam
- Crie uma narrativa que faça sentido como um todo, não apenas partes isoladas

💡 EXEMPLOS E APLICAÇÕES PRÁTICAS:
- SEMPRE dê exemplos concretos e práticos de como cada energia se manifesta na vida real
- Use situações do dia a dia que a pessoa possa reconhecer
- Mostre como aplicar o conhecimento numerológico na prática
- Dê orientações acionáveis, não apenas descrições teóricas

⚖️ ANÁLISE EQUILIBRADA:
- Para cada número, explique tanto as qualidades positivas quanto os desafios a serem trabalhados
- Seja honesto mas empoderador - mostre os desafios como oportunidades de crescimento
- Use tom terapêutico e acolhedor, não punitivo ou fatalista

🎯 FOCO NUMEROLÓGICO:
- Use APENAS conhecimento NUMEROLÓGICO fornecido no contexto RAG
- NÃO mencione planetas, signos, casas ou conceitos astrológicos (exceto quando explicitamente solicitado para conexão Tarot/Planetas)
- Priorize as informações do contexto RAG, mas use seu conhecimento numerológico profissional quando necessário

📏 EXTENSÃO E PROFUNDIDADE:
- O texto total deve ter NO MÍNIMO 2500 palavras
- Cada seção deve ter conteúdo COMPLETO e DETALHADO (mínimo de parágrafos indicados no roteiro)
- Seja EXTREMAMENTE específico e detalhado - evite generalidades
- Cada número merece uma análise profunda e narrativa, não apenas uma frase

💪 EMPODERAMENTO:
- Tom de empoderamento e autoconhecimento profundo
- Reforce que os números são ferramentas de livre arbítrio, não sentença imutável
- Mostre como usar o conhecimento numerológico para crescer e evoluir
- Termine com uma mensagem de esperança e possibilidade de transformação"""
            
            # Preparar strings com backslashes antes do f-string para evitar erro de sintaxe
            pinnacles_text = ''.join([f"• Pináculo {i+1} ({p['period']}): {p['number']}\n" for i, p in enumerate(numerology_map['pinnacles'])])
            challenges_text = ''.join([f"• Desafio {i+1} ({c['period']}): {c['number']}\n" for i, c in enumerate(numerology_map['challenges'])])
            
            user_prompt = f"""🎯 OBJETIVO PRINCIPAL: Criar um ESTUDO NUMEROLÓGICO PROFISSIONAL que conte a HISTÓRIA DE VIDA desta pessoa através dos números.

IMPORTANTE: Você NÃO está fazendo uma lista técnica de números. Você está CONTANDO UMA HISTÓRIA - a biografia numerológica única desta pessoa. Cada número deve ser apresentado como parte de uma narrativa maior, usando linguagem clara, acessível e envolvente.

REGRAS DE ESCRITA:
- Use TERMOS SIMPLES e de FÁCIL ENTENDIMENTO - explique qualquer conceito técnico na primeira vez
- CONTE uma história fluida, não liste informações
- Dê EXEMPLOS PRÁTICOS e CONCRETOS de como cada energia aparece na vida real
- Conecte todos os números em uma narrativa coesa
- Seja ESPECÍFICO e DETALHADO - mínimo de 2500 palavras no total
- Use linguagem rica mas sempre CLARA e ACESSÍVEL

Dados do Cliente:
• Nome Completo (Certidão): {numerology_map['full_name']}
• Data de Nascimento: {datetime.fromisoformat(numerology_map['birth_date']).strftime('%d/%m/%Y')}

Números Calculados:
• Caminho de Vida: {numerology_map['life_path']['number']} {'(Número Mestre)' if numerology_map['life_path']['is_master'] else ''}
• Expressão/Destino: {numerology_map['destiny']['number']} {'(Número Mestre)' if numerology_map['destiny']['is_master'] else ''}
• Desejo da Alma: {numerology_map['soul']['number']} {'(Número Mestre)' if numerology_map['soul']['is_master'] else ''}
• Personalidade: {numerology_map['personality']['number']} {'(Número Mestre)' if numerology_map['personality']['is_master'] else ''}
• Dia de Nascimento: {numerology_map['birthday']['number']}
• Número da Maturidade: {numerology_map['maturity']['number']} {'(Número Mestre)' if numerology_map['maturity']['is_master'] else ''}
• Ano Pessoal Atual ({numerology_map['personal_year']['year']}): {numerology_map['personal_year']['number']} {'(Número Mestre)' if numerology_map['personal_year']['is_master'] else ''}

Pináculos:
{pinnacles_text}

Desafios:
{challenges_text}

Grade de Nascimento:
• Setas de Força: {', '.join(numerology_map['birth_grid']['arrows_strength']) if numerology_map['birth_grid']['arrows_strength'] else 'Nenhuma'}
• Setas de Fraqueza: {', '.join(numerology_map['birth_grid']['arrows_weakness']) if numerology_map['birth_grid']['arrows_weakness'] else 'Nenhuma'}
• Números Faltantes (Lições Cármicas): {', '.join(map(str, numerology_map['birth_grid']['missing_numbers'])) if numerology_map['birth_grid']['missing_numbers'] else 'Nenhum'}

Dívidas Cármicas: {', '.join(map(str, numerology_map['karmic_debts'])) if numerology_map['karmic_debts'] else 'Nenhuma'}

Ciclo de Vida Atual: {numerology_map['life_cycle']['cycle']} (Número: {numerology_map['life_cycle']['cycle_number']}, Idade: {numerology_map['life_cycle']['age']} anos)

CONHECIMENTO NUMEROLÓGICO DE REFERÊNCIA (Use estas informações como base para sua interpretação):
{context_text}

📚 INSTRUÇÕES SOBRE O USO DO CONTEXTO RAG:
- PRIORIZE as informações do contexto RAG acima - elas são baseadas em fontes especializadas
- Se houver informações específicas sobre os números calculados, INCORPORE-AS NATURALMENTE na narrativa
- Se não houver informações suficientes sobre algum número específico, use seu conhecimento profissional de numerologia (Goodwin, Decoz, Phillips, Javane & Bunker)
- SEMPRE transforme as informações técnicas em narrativas acessíveis e práticas
- Use os exemplos e descrições do contexto RAG, mas adapte-os para contar a história desta pessoa específica

---

Roteiro da Consulta - CONTE A HISTÓRIA DE VIDA (Siga estritamente esta ordem, mas conecte tudo em uma narrativa fluida):

**PARTE 1: A ESSÊNCIA - QUEM VOCÊ É (A História de Origem)**

Baseado na "Síntese dos Elementos Nucleares" de Goodwin e Decoz. NÃO leia os números isoladamente. Analise a relação entre eles e CONTE uma história coesa.

Comece criando uma narrativa sobre a essência desta pessoa. Conecte os números principais em uma história que revele sua natureza fundamental:

1. **Caminho de Vida (A Missão)**: Conte a história da estrada principal desta pessoa de forma narrativa e envolvente. O que ela veio aprender nesta vida? Use linguagem simples e acessível para explicar o que significa este número. Descreva em detalhes como este número molda sua jornada, seus desafios e oportunidades. Dê exemplos práticos e concretos de situações do dia a dia onde isso se manifesta (ex: "Você pode notar isso quando...", "Isso aparece especialmente em situações como..."). Explique tanto as qualidades positivas quanto os desafios, sempre de forma empoderadora. (MÍNIMO 3 parágrafos completos e densos)

2. **Expressão (A Bagagem)**: Conte a história dos talentos naturais e ferramentas que ela trouxe para percorrer essa estrada. Use metáforas e analogias simples para explicar o que significa este número. Como esses dons se manifestam na prática? Dê exemplos concretos e específicos de situações reais onde esses talentos aparecem (ex: "Você pode usar isso quando...", "Isso se mostra especialmente em..."). Como ela pode usar melhor essas ferramentas no dia a dia? Dê orientações práticas e acionáveis. (MÍNIMO 3 parágrafos completos e densos)

3. **A Dança Entre Missão e Talento**: Analise se a Expressão apoia ou conflita com o Caminho de Vida. Conte essa relação como uma história - como essa dinâmica cria tensões ou harmonias na vida dela? Dê exemplos práticos e específicos de situações onde isso aparece (ex: "Você pode sentir isso quando...", "Isso se manifesta especialmente em..."). Como harmonizar essa relação? Dê orientações práticas e específicas de como trabalhar essa dinâmica. (MÍNIMO 2 parágrafos completos)

4. **Desejo da Alma (O Motor Interno)**: Conte a história do que a motiva profundamente de forma íntima e acolhedora. O que ela deseja quando ninguém está olhando? Use linguagem simples para explicar este conceito. Descreva como esse desejo secreto influencia suas escolhas e comportamentos no dia a dia. Dê exemplos práticos e específicos de como isso aparece na vida real (ex: "Você pode perceber isso quando...", "Isso se mostra especialmente em situações como..."). (MÍNIMO 2 parágrafos completos)

5. **Personalidade (A Máscara)**: Conte como os outros a veem na primeira impressão de forma narrativa. Descreva essa máscara em detalhes - como ela se apresenta ao mundo? Use linguagem clara e acessível. Dê exemplos específicos de situações onde essa personalidade aparece (ex: "As pessoas podem notar isso quando...", "Isso se mostra especialmente em..."). (MÍNIMO 2 parágrafos completos)

6. **A Tensão Entre Máscara e Alma**: A "Máscara" é muito diferente da "Alma"? Conte a história dessa diferença de forma acolhedora e terapêutica. Como isso gera sentimentos de incompreensão ou conflito interno? Dê exemplos práticos e específicos de situações onde isso aparece. Como integrar essas duas partes? Dê orientações práticas e acionáveis. (MÍNIMO 2 parágrafos completos)

7. **Dia de Nascimento (O Modificador)**: Conte como o talento específico do dia ajuda no Caminho de Vida de forma narrativa. Use linguagem simples para explicar este conceito. Dê exemplos práticos e específicos de como esse dom diário se manifesta na vida real (ex: "Você pode usar isso quando...", "Isso aparece especialmente em..."). Como pode ser usado para apoiar a missão? Dê orientações práticas. (MÍNIMO 2 parágrafos completos)

**PARTE 2: VIRTUDES, DEFEITOS E PADRÕES - COMO VOCÊ FUNCIONA (A História dos Padrões)**

Baseado nas Grades de Phillips e Psicologia de Decoz. Conte a história de como esta pessoa funciona internamente.

1. **A Grade de Nascimento (Setas de Individualidade) - A História dos Padrões Comportamentais**:

Identifique na grade 3x3 se há Setas de Força (linhas cheias) ou Setas de Fraqueza (linhas vazias).

Conte a história desses padrões de forma narrativa e acessível. Use linguagem simples para explicar o que são as setas de força e fraqueza. Como essas setas se manifestam no comportamento diário? Dê exemplos práticos, concretos e detalhados de situações reais onde esses padrões aparecem (ex: "Você pode notar isso quando...", "Isso se mostra especialmente em situações como..."). Se há setas de força, conte como isso cria determinação, foco ou outras qualidades, com exemplos específicos. Se há setas de fraqueza, conte como isso cria procrastinação, sensibilidade excessiva ou outros desafios, sempre de forma empoderadora. Dê orientações práticas, específicas e acionáveis para equilibrar esses padrões. (MÍNIMO 3 parágrafos completos e densos)

2. **Lições e Dívidas Cármicas - A História dos Obstáculos Repetitivos**:

Há números de Dívida Cármica (13, 14, 16, 19) nos números principais? Se sim, conte a história desse obstáculo repetitivo de forma acolhedora e terapêutica. Use linguagem simples para explicar o que significa uma dívida cármica (sem usar jargão técnico sem explicação). Descreva em detalhes como essa dívida cármica se manifesta na vida dela - dê exemplos concretos e específicos de situações reais onde isso aparece (ex: "Você pode perceber isso quando...", "Isso se mostra especialmente em..."). Explique a origem cármica de forma terapêutica e não punitiva, e como superá-la com consciência e trabalho interno. Dê orientações práticas, específicas e acionáveis. (MÍNIMO 3 parágrafos completos se houver dívidas)

Lições Cármicas: Quais números faltam no nome? Conte a história do que ela precisa aprender "na raça" nesta vida de forma empoderadora. Use linguagem simples para explicar o que são lições cármicas. Descreva como essas lições aparecem como desafios repetitivos na vida prática. Dê exemplos práticos, concretos e específicos de situações reais onde essas lições se apresentam (ex: "Você pode notar isso quando...", "Isso aparece especialmente em..."). Como trabalhar conscientemente essas lições? Dê orientações práticas e acionáveis. (MÍNIMO 2 parágrafos completos se houver lições)

3. **Saúde e Temperamento (Phillips) - A História da Energia Vital**:

Analise os Planos de Expressão (Mental, Físico, Emocional, Intuitivo). Use linguagem simples para explicar o que são os planos de expressão (sem usar jargão técnico sem explicação). Conte a história de onde está o foco de energia desta pessoa de forma narrativa. Descreva como isso se manifesta no dia a dia - dê exemplos práticos, concretos e específicos de situações reais (ex: "Você pode notar isso quando...", "Isso se mostra especialmente em..."). Onde há excesso ou falta de energia? Dê recomendações específicas, detalhadas e acionáveis de bem-estar baseadas nessa análise. (MÍNIMO 2 parágrafos completos)

**PARTE 3: O MAPA DA JORNADA - PARA ONDE VOCÊ VAI (A História do Destino)**

Baseado no Triângulo Divino de Javane & Bunker. Conte a história do destino e da jornada desta pessoa.

1. **O Grande Cenário (Triângulo Divino) - A História do Ciclo de Vida**:

Conte a história do ciclo de vida atual da pessoa (Juventude, Poder ou Sabedoria) de forma narrativa e envolvente. Use linguagem simples para explicar o que significa estar neste ciclo específico. Descreva em detalhes como isso se manifesta na vida prática. Dê exemplos concretos, específicos e práticos de situações e temas que aparecem neste ciclo (ex: "Você pode notar isso quando...", "Isso se mostra especialmente em..."). O que ela está aprendendo? O que está desenvolvendo? Como este ciclo se relaciona com os ciclos anteriores e futuros? Conecte tudo em uma narrativa fluida. (MÍNIMO 3 parágrafos completos e densos)

2. **Conexão Astrológica/Tarot - A História do Símbolo do Ciclo**:

Associe o número do ciclo atual ao Arcano Maior do Tarot correspondente e ao Planeta regente. Conte a história do que esse símbolo significa para o momento de vida dela de forma narrativa e acessível. Use linguagem simples para explicar a conexão com o Tarot (sem usar jargão técnico sem explicação). Descreva em detalhes como essa energia se manifesta na vida prática. Dê exemplos práticos, concretos e específicos de situações reais onde essa energia aparece (ex: "Você pode notar isso quando...", "Isso se mostra especialmente em..."). (Ex: Ciclo 7 = O Carro/Vitória pelo controle mental e espiritualidade - conte como isso aparece na vida prática dela com exemplos específicos). (MÍNIMO 2 parágrafos completos)

3. **A Maturidade - A História do Desenvolvimento Final**:

Conte a história do Número da Maturidade de forma narrativa e inspiradora. Use linguagem simples para explicar o que significa o número da maturidade. O que ela está desenvolvendo para a segunda metade da vida? Como esse número se relaciona com o Caminho de Vida? Descreva em detalhes como essa energia de maturidade se manifesta e o que ela está aprendendo a integrar. Dê exemplos práticos, concretos e específicos de como isso aparece na vida real (ex: "Você pode perceber isso quando...", "Isso se mostra especialmente em..."). (MÍNIMO 2 parágrafos completos)

**PARTE 4: PREVISÃO E MOMENTO ATUAL - O AGORA (A História do Presente)**

Baseado nos Pináculos de Goodwin e Ciclos de Decoz. Conte a história do momento atual desta pessoa.

1. **Pináculos e Desafios Atuais - A História do Cenário Presente**:

Identifique o Pináculo e o Desafio atuais baseado na idade da pessoa ({numerology_map['life_cycle']['age']} anos).

Conte a história do cenário externo atual (Pináculo) de forma narrativa e empoderadora. Use linguagem simples para explicar o que é um Pináculo. O que a vida está oferecendo neste momento? Descreva em detalhes as oportunidades, energias e temas que estão presentes. Dê exemplos práticos, concretos e específicos de como isso se manifesta na vida real (ex: "Você pode esperar isso em...", "Isso aparece especialmente quando...", "Áreas da vida afetadas incluem..."). O que ela pode esperar? Quais portas estão se abrindo? Seja específico e detalhado. (MÍNIMO 3 parágrafos completos e densos)

Conte a história do obstáculo atual (Desafio) de forma acolhedora e terapêutica. Use linguagem simples para explicar o que é um Desafio numerológico. O que está testando a pessoa agora? Descreva em detalhes como esse desafio aparece na vida prática. Dê exemplos concretos e específicos de situações reais onde esse desafio se manifesta (ex: "Você pode perceber isso quando...", "Isso se mostra especialmente em..."). Qual é a lição por trás desse desafio? Como trabalhar conscientemente com ele? Dê orientações práticas e acionáveis. (MÍNIMO 2 parágrafos completos)

Síntese: Conte como aproveitar o Pináculo apesar do Desafio de forma narrativa e empoderadora. Dê orientações práticas, específicas, detalhadas e acionáveis. Crie uma narrativa de como essas duas energias trabalham juntas e como ela pode navegar essa situação. Use exemplos práticos de como aplicar isso no dia a dia. (MÍNIMO 2 parágrafos completos)

2. **Ano Pessoal (O Agora) - A História do Ano Atual**:

A pessoa está no Ano Pessoal {numerology_map['personal_year']['number']} ({numerology_map['personal_year']['year']}).

Conte a história completa deste ano pessoal de forma narrativa e envolvente. Use linguagem simples e acessível para explicar o que significa este ano pessoal. Descreva em detalhes as energias, temas e oportunidades deste ano. O que está sendo trabalhado? O que está sendo desenvolvido? O que está sendo liberado? Dê exemplos práticos, concretos e específicos de situações e áreas da vida onde isso aparece (ex: "Você pode esperar isso em...", "Isso se manifesta especialmente quando...", "Áreas da vida afetadas incluem..."). (MÍNIMO 3 parágrafos completos e densos)

Dê 5-7 conselhos práticos, específicos e acionáveis para este ano. Seja concreto, detalhado e claro (Ex: "É hora de plantar sementes em relacionamentos - isso significa investir tempo em conhecer novas pessoas e fortalecer vínculos existentes", ou "É hora de finalizar projetos antigos que não servem mais - revise seus compromissos e libere o que não está alinhado com seus objetivos atuais", ou "Cuidado com contratos e compromissos - revise tudo antes de assinar, especialmente em [área específica]"). Para cada conselho, explique o contexto, por que é importante agora e como aplicá-lo na prática. (MÍNIMO 3 parágrafos completos)

**CONCLUSÃO TERAPÊUTICA - A SÍNTESE DA HISTÓRIA**

Finalize criando uma síntese narrativa, positiva e inspiradora que conecte todos os elementos da história numerológica desta pessoa. Conte como todos os números se unem para criar uma jornada única e significativa, usando linguagem simples e acessível. Reforce que os números são ferramentas de livre arbítrio e não uma sentença imutável - explique isso de forma clara e empoderadora. Dê uma mensagem final de empoderamento, esperança e possibilidade de transformação, mostrando como ela pode usar esse conhecimento para crescer e evoluir. Use exemplos práticos de como aplicar esse autoconhecimento no dia a dia. (MÍNIMO 3 parágrafos completos e densos)

IMPORTANTE - REGRAS DE ESCRITA:
- Use formatação com títulos em negrito (formato: **PARTE 1: A ESSÊNCIA**)
- Separe parágrafos com quebras de linha duplas
- Seja EXTREMAMENTE específico e detalhado - não genérico
- Use linguagem rica, envolvente e acolhedora
- Cada parte deve ter conteúdo COMPLETO e DETALHADO (mínimo de parágrafos indicados acima)
- Para cada número, explique tanto suas qualidades positivas quanto os desafios a serem trabalhados (análise equilibrada)
- SEMPRE dê exemplos práticos e concretos de como as energias se manifestam na vida
- Conecte os números em uma narrativa fluida - não apenas liste informações
- O texto total deve ter NO MÍNIMO 2500 palavras
- Organize as informações de forma clara, evitando repetições
- Conte a HISTÓRIA DE VIDA através dos números, não apenas liste significados técnicos"""
        else:
            # English version
            system_prompt = """Role and Context: Act as an experienced Pythagorean Numerologist and also an Astrologer. Your approach must synthesize the best world references: the technical precision and synthesis of Matthew Oliver Goodwin, the psychological and therapeutic depth of Hans Decoz, the holistic health vision of David A. Phillips, and the sacred geometry/life cycles of Faith Javane & Dusty Bunker.

CRITICAL IMPORTANT:
- Use ONLY NUMEROLOGICAL knowledge provided in the context
- DO NOT mention planets, signs, houses or any astrological concepts (except when explicitly requested for Tarot/Planet connections)
- Focus on numbers, numerological calculations, number meanings and numerological cycles
- If the context does not contain sufficient numerological information, clearly state this
- Simple, practical and clarifying language (avoid excessive "numerologese" without explanation)
- Tone of empowerment and self-knowledge
- Numbers are tools of free will, not an immutable sentence"""
            
            # Preparar strings com backslashes antes do f-string para evitar erro de sintaxe
            pinnacles_text = ''.join([f"• Pinnacle {i+1} ({p['period']}): {p['number']}\n" for i, p in enumerate(numerology_map['pinnacles'])])
            challenges_text = ''.join([f"• Challenge {i+1} ({c['period']}): {c['number']}\n" for i, c in enumerate(numerology_map['challenges'])])
            
            user_prompt = f"""Objective: Perform a complete, deep and welcoming numerology consultation for the client below. The language should be simple, practical and clarifying (avoid excessive "numerologese" without explanation). The tone should be empowering and focused on self-knowledge.

Client Data:
• Full Name (Certificate): {numerology_map['full_name']}
• Birth Date: {datetime.fromisoformat(numerology_map['birth_date']).strftime('%m/%d/%Y')}

Calculated Numbers:
• Life Path: {numerology_map['life_path']['number']} {'(Master Number)' if numerology_map['life_path']['is_master'] else ''}
• Expression/Destiny: {numerology_map['destiny']['number']} {'(Master Number)' if numerology_map['destiny']['is_master'] else ''}
• Soul's Desire: {numerology_map['soul']['number']} {'(Master Number)' if numerology_map['soul']['is_master'] else ''}
• Personality: {numerology_map['personality']['number']} {'(Master Number)' if numerology_map['personality']['is_master'] else ''}
• Birthday: {numerology_map['birthday']['number']}
• Maturity Number: {numerology_map['maturity']['number']} {'(Master Number)' if numerology_map['maturity']['is_master'] else ''}
• Current Personal Year ({numerology_map['personal_year']['year']}): {numerology_map['personal_year']['number']} {'(Master Number)' if numerology_map['personal_year']['is_master'] else ''}

Pinnacles:
{pinnacles_text}

Challenges:
{challenges_text}

Birth Grid:
• Strength Arrows: {', '.join(numerology_map['birth_grid']['arrows_strength']) if numerology_map['birth_grid']['arrows_strength'] else 'None'}
• Weakness Arrows: {', '.join(numerology_map['birth_grid']['arrows_weakness']) if numerology_map['birth_grid']['arrows_weakness'] else 'None'}
• Missing Numbers (Karmic Lessons): {', '.join(map(str, numerology_map['birth_grid']['missing_numbers'])) if numerology_map['birth_grid']['missing_numbers'] else 'None'}

Karmic Debts: {', '.join(map(str, numerology_map['karmic_debts'])) if numerology_map['karmic_debts'] else 'None'}

Current Life Cycle: {numerology_map['life_cycle']['cycle']} (Number: {numerology_map['life_cycle']['cycle_number']}, Age: {numerology_map['life_cycle']['age']} years)

NUMEROLOGICAL KNOWLEDGE REFERENCE (Use this information as the basis for your interpretation):
{context_text}

IMPORTANT: Use the RAG information above to support your interpretation. If there is specific information about the calculated numbers, incorporate it naturally into the response. If there is not enough information about a specific number, use your general knowledge of numerology, but always prioritize the information from the provided context.

---

Consultation Script (Follow this incremental order strictly):

PART 1: THE ESSENCE (WHO YOU ARE)

Based on the "Synthesis of Nuclear Elements" by Goodwin and Decoz. Do not read the numbers in isolation. Analyze the relationship between them.

Life Path (The Mission): What is this person's main road? What did they come to learn?

Expression (The Baggage): What natural talents and tools did they bring to walk this road?

Conflict Analysis (Goodwin): Check if the Expression supports or conflicts with the Life Path (Ex: A Leader's Path with a Follower's Expression). Explain how to harmonize this.

Soul's Desire (The Internal Engine): What motivates them deeply? What do they desire when no one is looking?

Personality (The Mask): How do others see them at first impression?

Comparison (Decoz): Is the "Mask" very different from the "Soul"? If so, explain if this generates feelings of misunderstanding.

Birthday (The Modifier): What specific talent of the day helps in the Life Path?

PART 2: VIRTUES, DEFECTS AND PATTERNS (HOW YOU FUNCTION)

Based on Phillips' Grids and Decoz's Psychology.

The Birth Grid (Arrows of Individuality):

Identify in the 3x3 grid if there are Strength Arrows (full lines) or Weakness Arrows (empty lines).

Translate this into behavior: Does she have determination? Procrastination? Excessive sensitivity? Give a practical tip to balance.

Lessons and Karmic Debts:

Are there Karmic Debt numbers (13, 14, 16, 19) in the main numbers? If so, explain the repetitive obstacle and how to overcome it (therapeutic view, not punitive).

Karmic Lessons: Which numbers are missing in the name? What does she need to learn "the hard way" in this life?

Health and Temperament (Phillips):

Briefly analyze the Expression Planes (Mental, Physical, Emotional, Intuitive). Where is the energy focus? Give a brief wellness recommendation based on this.

PART 3: THE JOURNEY MAP (WHERE YOU'RE GOING)

Based on the Divine Triangle by Javane & Bunker.

The Great Scenario (Divine Triangle):

Describe the person's current life cycle (Youth, Power or Wisdom).

Astrological/Tarot Connection: Associate the current cycle number with the corresponding Major Arcana of Tarot and the ruling Planet. Explain what this means for her life moment (Ex: Cycle 7 = The Chariot/Victory through mental control and spirituality).

PART 4: FORECAST AND CURRENT MOMENT (WEATHER FORECAST)

Based on Goodwin's Pinnacles and Decoz's Cycles.

Current Pinnacles and Challenges:

What is the current external scenario (Pinnacle)? What is life offering?

What is the current obstacle (Challenge)? What is testing the person?

Synthesis: How to take advantage of the Pinnacle despite the Challenge?

Personal Year (The Now):

What Personal Year is she in? ({numerology_map['personal_year']['number']})

Give 3 practical pieces of advice for this year (Ex: "It's time to plant", or "It's time to finalize", or "Be careful with contracts").

THERAPEUTIC CONCLUSION

End with a positive synthesis message. Reinforce that numbers are tools of free will and not an immutable sentence.

IMPORTANT:
- Use formatting with bold titles (format: **PART 1: THE ESSENCE**)
- Separate paragraphs with double line breaks
- Be specific and practical, not generic
- Use welcoming and empowering language
- Each part must have complete and detailed content
- For each number, explain both its positive qualities and the challenges to be worked on (balanced analysis)
- Organize information clearly, avoiding repetitions"""
        
        # Gerar interpretação com Groq usando prompts customizados
        # IMPORTANTE: Tentar usar Groq mesmo com pouco contexto - o modelo tem conhecimento numerológico
        groq_client = _get_groq_client()
        if groq_client:
            try:
                # Chamar Groq diretamente com prompts customizados
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama-3.3-70b-versatile",  # Modelo maior para interpretações mais detalhadas
                    temperature=0.7,
                    max_tokens=8000,  # Aumentado significativamente para estudos completos e detalhados
                    top_p=0.9,
                )
                
                interpretation_text = chat_completion.choices[0].message.content
                
                if interpretation_text:
                    interpretation_text = interpretation_text.strip()
                    # Remover referências explícitas a fontes
                    interpretation_text = re.sub(r'\[Fonte:[^\]]+\]', '', interpretation_text)
                    interpretation_text = re.sub(r'Página \d+', '', interpretation_text)
                    
                    # Aplicar filtro de deduplicação
                    interpretation_text = _deduplicate_text(interpretation_text)
                
                # Converter sources
                sources_list = [
                    SourceItem(
                        source=doc.get('source', 'knowledge_base'),
                        page=doc.get('page', 1),
                        relevance=doc.get('score', 0.5)
                    )
                    for doc in context_documents[:5]
                ]
                
                # Converter sources (mesmo que vazio, vamos tentar)
                sources_list = [
                    SourceItem(
                        source=doc.get('source', 'knowledge_base'),
                        page=doc.get('page', 1),
                        relevance=doc.get('score', 0.5)
                    )
                    for doc in context_documents[:5]
                ] if context_documents else []
                
                return NumerologyInterpretationResponse(
                    interpretation=interpretation_text or "Não foi possível gerar a interpretação.",
                    sources=sources_list,
                    query_used=f"numerologia completa para {numerology_map['full_name']}",
                    generated_by='groq'
                )
            except Exception as e:
                print(f"[ERROR] Erro ao gerar interpretação com Groq: {e}")
                import traceback
                print(traceback.format_exc())
                # Continuar para o fallback em caso de erro
        
        # Fallback: gerar interpretação básica (se não houver Groq)
        print("[WARNING] Usando fallback básico - Groq não disponível ou erro na geração")
        
        fallback_text = f"""PARTE 1: A ESSÊNCIA (QUEM VOCÊ É)

1. Caminho de Vida ({numerology_map['life_path']['number']}): Este é o número mais importante da numerologia, representando a missão principal desta vida.

2. Expressão ({numerology_map['destiny']['number']}): Revela os talentos naturais e ferramentas disponíveis.

3. Desejo da Alma ({numerology_map['soul']['number']}): O que motiva profundamente esta pessoa.

4. Personalidade ({numerology_map['personality']['number']}): Como os outros a percebem.

5. Dia de Nascimento ({numerology_map['birthday']['number']}): Talento específico do dia.

PARTE 2: VIRTUDES, DEFEITOS E PADRÕES

Grade de Nascimento: Analise as setas de força e fraqueza para entender padrões comportamentais.

PARTE 3: O MAPA DA JORNADA

Ciclo Atual: {numerology_map['life_cycle']['cycle']} (Número: {numerology_map['life_cycle']['cycle_number']})

PARTE 4: PREVISÃO E MOMENTO ATUAL

Ano Pessoal {numerology_map['personal_year']['number']}: Este ano traz energias específicas para crescimento e desenvolvimento.

CONCLUSÃO TERAPÊUTICA

Os números são ferramentas de autoconhecimento e livre arbítrio. Use estas informações para crescer e evoluir."""
        
        return NumerologyInterpretationResponse(
            interpretation=fallback_text,
            sources=[],
            query_used=f"numerologia completa para {numerology_map['full_name']}",
            generated_by="fallback"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao gerar interpretação numerológica: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar interpretação numerológica: {str(e)}"
        )


class BirthGridQuantitiesRequest(BaseModel):
    """Request para interpretação das quantidades na grade de nascimento."""
    grid: Dict[int, int]  # {número: quantidade}
    language: Optional[str] = 'pt'


class BirthGridQuantitiesResponse(BaseModel):
    """Response com interpretação das quantidades na grade."""
    explanation: str
    sources: List[SourceItem]
    query_used: str


@router.post("/numerology/birth-grid-quantities", response_model=BirthGridQuantitiesResponse)
async def get_birth_grid_quantities_interpretation(
    request: BirthGridQuantitiesRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Obtém interpretação sobre o significado das quantidades na grade de nascimento.
    Busca informações dos livros de numerologia no RAG.
    """
    try:
        rag_service = get_rag_service()
        lang = request.language or 'pt'
        
        # Construir queries para buscar informações sobre a Grade de Nascimento e quantidades
        queries = [
            # Queries mais específicas sobre Grade Numerológica
            "grade numerológica nome data nascimento",
            "numerological grid name birth date",
            "grade 3x3 numerologia números",
            "birth grid 3x3 numerology numbers",
            # Queries sobre quantidades e frequências
            "número aparece muitas vezes grade numerologia",
            "number appears many times grid numerology",
            "quantidade números grade nascimento significado",
            "grid numbers quantity meaning numerology",
            # Queries sobre ausência de números
            "número ausente grade numerologia falta",
            "missing number grid numerology absence",
            # Queries sobre excesso de números
            "excesso número grade numerologia energia",
            "excess number grid numerology energy",
            # Queries gerais sobre grade
            "grade de nascimento numerologia",
            "birth grid numerology",
            "numerologia grade quantidade",
            "numerology grid quantity"
        ]
        
        # Buscar no RAG com mais documentos
        all_results = []
        seen_texts = set()
        
        if rag_service:
            for query in queries:
                try:
                    results = rag_service.search(
                        query=query,
                        top_k=10,  # Aumentado de 5 para 10
                        expand_query=True,
                        category='numerology'
                    )
                    for doc in results:
                        doc_text = doc.get('text', '').strip()
                        if doc_text and doc_text not in seen_texts and len(doc_text) > 20:
                            seen_texts.add(doc_text)
                            all_results.append(doc)
                except Exception as e:
                    print(f"[WARNING] Erro ao buscar query '{query}': {e}")
                    continue
        
        # Ordenar por relevância e pegar mais resultados
        all_results = sorted(
            all_results,
            key=lambda x: x.get('score', 0),
            reverse=True
        )[:20]  # Aumentado de 10 para 20
        
        # Preparar contexto - limpar texto antes de enviar ao Groq
        raw_context_parts = []
        for doc in all_results:
            if doc.get('text'):
                # Limpar espaços estranhos entre letras
                text = doc.get('text', '')
                text = re.sub(r'(\w)\s+(\w)', r'\1\2', text)
                text = re.sub(r'\s+', ' ', text).strip()
                raw_context_parts.append(text)
        
        # Contexto limpo sem referências inline
        context_text = "\n\n".join(raw_context_parts)
        
        # Preparar dados da grade para o prompt
        grid_summary = []
        for num in sorted(request.grid.keys()):
            count = request.grid[num]
            if count > 0:
                grid_summary.append(f"Número {num}: aparece {count} vez(es)")
        
        grid_summary_text = "\n".join(grid_summary) if grid_summary else "Nenhum número presente"
        
        # Função auxiliar para gerar explicação de fallback
        def _generate_quantities_fallback(grid: Dict[int, int], lang: str) -> str:
            """Gera explicação baseada no conhecimento do sistema quando Groq não está disponível."""
            number_meanings = {
                1: "Ação, Liderança, Independência, Ego, Identidade Pessoal",
                2: "Dualidade, Sentimentos, Diplomacia, Cooperação, Sensibilidade",
                3: "Criatividade, Comunicação, Expressão, Alegria, Sociabilidade",
                4: "Estabilidade, Organização, Trabalho, Praticidade, Disciplina",
                5: "Liberdade, Mudança, Versatilidade, Aventura, Curiosidade",
                6: "Responsabilidade, Família, Amor, Harmonia, Cuidado",
                7: "Espiritualidade, Introspecção, Análise, Sabedoria, Intuição",
                8: "Poder, Materialismo, Organização, Autoridade, Transformação",
                9: "Compaixão, Serviço, Sabedoria, Generosidade, Humanitarismo"
            }
            
            present_numbers = {num: count for num, count in grid.items() if count > 0}
            missing_numbers = [num for num in range(1, 10) if grid.get(num, 0) == 0]
            
            if lang == 'pt':
                explanation = "## Significado das Quantidades na Grade de Nascimento\n\n"
                explanation += "A Grade Numerológica mostra quantas vezes cada número (1 a 9) aparece no seu nome completo e data de nascimento. A quantidade indica a intensidade da energia de cada número na sua vida.\n\n"
                
                explanation += "### Números Presentes na Sua Grade:\n\n"
                for num, count in sorted(present_numbers.items()):
                    meaning = number_meanings.get(num, "")
                    if count == 1:
                        explanation += f"**Número {num}** (aparece {count} vez): {meaning}\n"
                        explanation += f"Este número está presente na sua grade, indicando que a energia do {num} está ativa na sua vida. Você possui as qualidades relacionadas a este número, mas pode precisar desenvolvê-las mais.\n\n"
                    elif count <= 3:
                        explanation += f"**Número {num}** (aparece {count} vezes): {meaning}\n"
                        explanation += f"Este número aparece com frequência moderada, indicando que a energia do {num} está bem presente e equilibrada na sua vida. Você tem acesso natural a essas qualidades.\n\n"
                    else:
                        explanation += f"**Número {num}** (aparece {count} vezes): {meaning}\n"
                        explanation += f"Este número aparece muitas vezes na sua grade, indicando uma energia muito forte do {num}. Isso pode ser uma grande força, mas também pode indicar um desequilíbrio - você pode estar usando demais ou de forma excessiva essas qualidades.\n\n"
                
                if missing_numbers:
                    explanation += "### Números Ausentes (Lições a Desenvolver):\n\n"
                    explanation += "Os números que não aparecem na sua grade indicam áreas onde você precisa desenvolver mais. Estas são lições cármicas - qualidades que você precisa aprender e integrar nesta vida.\n\n"
                    for num in missing_numbers:
                        meaning = number_meanings.get(num, "")
                        explanation += f"**Número {num} ausente**: {meaning}\n"
                        explanation += f"A ausência do número {num} indica que você precisa desenvolver essas qualidades. Esta é uma área de crescimento pessoal importante para você.\n\n"
                
                explanation += "### Fluxo de Energia:\n\n"
                explanation += "Quando alguns números aparecem muitas vezes e outros poucas vezes, há um fluxo de energia. Os números mais presentes tendem a dominar, enquanto os menos presentes precisam ser desenvolvidos para criar equilíbrio.\n\n"
                explanation += "**Dica**: Trabalhe conscientemente para desenvolver os números ausentes e equilibrar os números que aparecem em excesso."
            else:
                explanation = "## Meaning of Quantities in the Birth Grid\n\n"
                explanation += "The Numerological Grid shows how many times each number (1 to 9) appears in your full name and birth date. The quantity indicates the intensity of each number's energy in your life.\n\n"
                
                explanation += "### Numbers Present in Your Grid:\n\n"
                for num, count in sorted(present_numbers.items()):
                    meaning = number_meanings.get(num, "")
                    if count == 1:
                        explanation += f"**Number {num}** (appears {count} time): {meaning}\n"
                        explanation += f"This number is present in your grid, indicating that the energy of {num} is active in your life. You possess qualities related to this number, but may need to develop them more.\n\n"
                    elif count <= 3:
                        explanation += f"**Number {num}** (appears {count} times): {meaning}\n"
                        explanation += f"This number appears with moderate frequency, indicating that the energy of {num} is well present and balanced in your life. You have natural access to these qualities.\n\n"
                    else:
                        explanation += f"**Number {num}** (appears {count} times): {meaning}\n"
                        explanation += f"This number appears many times in your grid, indicating a very strong energy of {num}. This can be a great strength, but may also indicate an imbalance - you may be using these qualities too much or excessively.\n\n"
                
                if missing_numbers:
                    explanation += "### Missing Numbers (Lessons to Develop):\n\n"
                    explanation += "Numbers that do not appear in your grid indicate areas where you need to develop more. These are karmic lessons - qualities you need to learn and integrate in this life.\n\n"
                    for num in missing_numbers:
                        meaning = number_meanings.get(num, "")
                        explanation += f"**Number {num} missing**: {meaning}\n"
                        explanation += f"The absence of number {num} indicates that you need to develop these qualities. This is an important area of personal growth for you.\n\n"
                
                explanation += "### Energy Flow:\n\n"
                explanation += "When some numbers appear many times and others few times, there is an energy flow. The most present numbers tend to dominate, while the least present ones need to be developed to create balance.\n\n"
                explanation += "**Tip**: Consciously work to develop missing numbers and balance numbers that appear in excess."
            
            return explanation
        
        # Gerar explicação com Groq - SEMPRE tentar, mesmo com pouco contexto
        # O system prompt já tem conhecimento suficiente sobre Grade Numerológica
        groq_client = _get_groq_client()
        
        # Se Groq não estiver disponível, usar fallback baseado no conhecimento do sistema
        if not groq_client:
            print("[INFO] Groq não disponível, gerando explicação de fallback baseada no conhecimento do sistema")
            fallback_explanation = _generate_quantities_fallback(request.grid, lang)
            return BirthGridQuantitiesResponse(
                explanation=fallback_explanation,
                sources=[],
                query_used="quantidades na grade de nascimento"
            )
        
        if groq_client:
            try:
                if lang == 'pt':
                    system_prompt = """Você é um numerólogo experiente especializado em interpretação de grades de nascimento. Sua função é explicar:
1. O que é a Grade de Nascimento na numerologia
2. O significado das quantidades (quantas vezes cada número aparece) na grade de nascimento

CONCEITO FUNDAMENTAL DA GRADE NUMEROLÓGICA:
A Grade Numerológica é uma grade 3x3 (números de 1 a 9) que pode ser utilizada para o nome completo ou para a data de nascimento. A cada vez que um número aparecer no nome ou data, circulamos o número correspondente na grade. A presença de 3 números numa linha vertical, horizontal ou diagonal denota qualidades em potencial. Normalmente encontramos pelo menos uma linha completa numa grade.

SIGNIFICADO DAS QUANTIDADES NA GRADE:
- Quando um número aparece na grade: indica que a energia desse número está presente e ativa
- Quando um número NÃO aparece na grade (ausente): indica falta dessa energia, problemas relacionados a essa área, ou necessidade de desenvolver essas qualidades
- Quando um número aparece MUITAS vezes (excesso): indica que essa energia está muito presente, mas pode ser mal utilizada ou desequilibrada
- Fluxo de energia: quando temos mais números de um tipo e menos de outro, a energia flui do número mais presente para o menos presente (ex: 5 números 1 e 2 números 2 = energia flui do 1 para o 2)

CARACTERÍSTICAS DOS NÚMEROS:
1 - Ação / o Ser / Ego / Liderança / Recursos Pessoais / Identidade Pessoal / Independência Pessoal
2 - Dualidade / Sentimentos / Carinho / A Mente Consciente / Tato / Diplomacia
3 - Criatividade Pessoal / Comunicação / Poder de Persuasão / Expressão do Ser / Prestação de Serviço
4 - Pensamento Lógico / Espírito Prático / Instintos / O Concreto / O Mundo Material / O trabalho duro / Praticidade
5 - Os Sentidos / Expansão de Consciência / Flexibilidade / Tolerância / Aprendizagem / Mudanças / Liberdade
6 - Criatividade Intelectual / Imaginação / Fantasia / Pensamento Abstrato / Teoria / Família / Responsabilidade / Amor / Harmonia
7 - Estabelecer Limites / Tempo / Ligações Materiais / Os Limites do Mundo Material / A Ponte para o Reino Espiritual / Análise / Pesquisa
8 - Mente Inconsciente / Transformação do Material / Espaço Sem Tempo / Equilíbrio / Dharma: fazer o que tem que ser feito / Organização / Poder Mental
9 - Criatividade Espiritual / Amor Divino / Talentos Inatos / Acabamento / Karma: recompensa pelas ações de vidas passadas / Entrega / Doação

Baseie-se APENAS nas informações fornecidas dos livros de numerologia, mas use o conhecimento acima sobre a Grade Numerológica como base conceitual.

REGRAS CRÍTICAS:
- Use APENAS informações dos livros fornecidos no contexto quando disponíveis
- Use o conhecimento sobre Grade Numerológica acima para explicar o conceito
- NÃO invente ou adivinhe informações específicas sobre quantidades
- Se não houver informações suficientes no contexto, use o conhecimento geral sobre presença/ausência/excesso
- PRIMEIRO explique o que é a Grade de Nascimento usando o conceito acima
- DEPOIS explique de forma prática e clara o que significa ter números com diferentes quantidades
- Explique tanto a presença quanto a ausência de números
- Explique o fluxo de energia entre números quando houver desequilíbrios
- Foque em exemplos práticos e aplicações na vida real
- Formate o texto de forma clara e legível, com parágrafos bem estruturados
- NÃO inclua referências a fontes ou páginas no texto final
- O texto pode vir com espaços estranhos - corrija e formate corretamente"""
                    
                    user_prompt = f"""GRADE DE NASCIMENTO - EXPLICAÇÃO COMPLETA:

DADOS DA GRADE:
{grid_summary_text}

INFORMAÇÕES DOS LIVROS DE NUMEROLOGIA:
{context_text if context_text and len(context_text.strip()) > 50 else "Nenhuma informação específica encontrada nos livros, mas use o conhecimento numerológico geral sobre Grade Numerológica."}

---

INSTRUÇÕES:

1. PRIMEIRO: Explique o que é a Grade de Nascimento na numerologia. Use o conceito fundamental fornecido no system prompt: é uma grade 3x3 onde se marca quantas vezes cada número (1-9) aparece no nome ou data de nascimento. A presença de 3 números numa linha (vertical, horizontal ou diagonal) denota qualidades em potencial.

2. DEPOIS: Explique o significado das quantidades na grade de nascimento. Para cada número presente:
   - Explique o que significa ter esse número presente (energia ativa)
   - Explique o que significa ter esse número ausente (falta dessa energia, problemas relacionados, necessidade de desenvolvimento)
   - Explique o que significa ter excesso desse número (energia muito presente, mas pode ser mal utilizada)
   - Analise o fluxo de energia entre números quando houver desequilíbrios (mais de um número, menos de outro)

3. ANÁLISE ESPECÍFICA: Para os números que aparecem na grade fornecida, explique:
   - O que significa ter esse número presente e em que quantidade
   - Como essa energia se manifesta na vida da pessoa
   - Quais são as qualidades e desafios relacionados

4. NÚMEROS AUSENTES: Para os números que NÃO aparecem na grade, explique:
   - O que significa a ausência desse número
   - Quais problemas ou dificuldades isso pode indicar
   - O que a pessoa precisa desenvolver nessa área

IMPORTANTE:
- Use APENAS as informações dos livros fornecidos acima quando disponíveis
- Use o conhecimento sobre Grade Numerológica do system prompt para explicar o conceito
- Se o texto tiver espaços estranhos entre letras, corrija e formate corretamente
- Formate o texto de forma clara, com parágrafos bem estruturados
- NÃO inclua referências a fontes ou páginas no texto final
- Se não houver informações suficientes sobre quantidades específicas, explique o conceito geral baseado no conhecimento sobre presença/ausência/excesso
- Estruture a resposta com:
  * Seção sobre "O que é a Grade de Nascimento"
  * Seção sobre "Análise dos Números Presentes"
  * Seção sobre "Números Ausentes (Lições a Desenvolver)"
  * Seção sobre "Fluxo de Energia e Equilíbrio"
"""
                else:
                    system_prompt = """You are an experienced numerologist specialized in birth grid interpretation. Your function is to explain:
1. What is the Birth Grid in numerology
2. The meaning of quantities (how many times each number appears) in the birth grid

FUNDAMENTAL CONCEPT OF THE NUMEROLOGICAL GRID:
The Numerological Grid is a 3x3 grid (numbers 1 to 9) that can be used for the full name or birth date. Each time a number appears in the name or date, we circle the corresponding number in the grid. The presence of 3 numbers in a vertical, horizontal or diagonal line denotes potential qualities. Normally we find at least one complete line in a grid.

MEANING OF QUANTITIES IN THE GRID:
- When a number appears in the grid: indicates that the energy of that number is present and active
- When a number does NOT appear in the grid (absent): indicates lack of this energy, problems related to this area, or need to develop these qualities
- When a number appears MANY times (excess): indicates that this energy is very present, but may be misused or unbalanced
- Energy flow: when we have more numbers of one type and fewer of another, energy flows from the more present number to the less present one (ex: 5 number 1s and 2 number 2s = energy flows from 1 to 2)

CHARACTERISTICS OF NUMBERS:
1 - Action / the Being / Ego / Leadership / Personal Resources / Personal Identity / Personal Independence
2 - Duality / Feelings / Affection / The Conscious Mind / Tact / Diplomacy
3 - Personal Creativity / Communication / Power of Persuasion / Expression of Being / Service
4 - Logical Thinking / Practical Spirit / Instincts / The Concrete / The Material World / Hard work / Practicality
5 - The Senses / Consciousness Expansion / Flexibility / Tolerance / Learning / Changes / Freedom
6 - Intellectual Creativity / Imagination / Fantasy / Abstract Thinking / Theory / Family / Responsibility / Love / Harmony
7 - Establishing Limits / Time / Material Connections / The Limits of the Material World / The Bridge to the Spiritual Realm / Analysis / Research
8 - Unconscious Mind / Material Transformation / Space Without Time / Balance / Dharma: doing what needs to be done / Organization / Mental Power
9 - Spiritual Creativity / Divine Love / Inborn Talents / Completion / Karma: reward for actions from past lives / Surrender / Giving

Base your explanation ONLY on the information provided from numerology books, but use the knowledge above about the Numerological Grid as a conceptual basis.

CRITICAL RULES:
- Use ONLY information from the books provided in the context when available
- Use the knowledge about Numerological Grid above to explain the concept
- DO NOT invent or guess specific information about quantities
- If there is not enough information in the context, use general knowledge about presence/absence/excess
- FIRST explain what the Birth Grid is using the concept above
- THEN explain in a practical and clear way what it means to have numbers with different quantities
- Explain both the presence and absence of numbers
- Explain the energy flow between numbers when there are imbalances
- Focus on practical examples and real-life applications"""
                    
                    user_prompt = f"""BIRTH GRID - COMPLETE EXPLANATION:

GRID DATA:
{grid_summary_text}

NUMEROLOGY BOOKS INFORMATION:
{context_text}

---

INSTRUCTIONS:

1. FIRST: Explain what the Birth Grid is in numerology. Use the fundamental concept provided in the system prompt: it is a 3x3 grid where we mark how many times each number (1-9) appears in the name or birth date. The presence of 3 numbers in a line (vertical, horizontal or diagonal) denotes potential qualities.

2. THEN: Explain the meaning of quantities in the birth grid. For each number present:
   - Explain what it means to have this number present (active energy)
   - Explain what it means to have this number absent (lack of this energy, related problems, need for development)
   - Explain what it means to have excess of this number (energy very present, but may be misused)
   - Analyze the energy flow between numbers when there are imbalances (more of one number, less of another)

3. SPECIFIC ANALYSIS: For the numbers that appear in the provided grid, explain:
   - What it means to have this number present and in what quantity
   - How this energy manifests in the person's life
   - What are the related qualities and challenges

4. ABSENT NUMBERS: For numbers that do NOT appear in the grid, explain:
   - What the absence of this number means
   - What problems or difficulties this may indicate
   - What the person needs to develop in this area

IMPORTANT:
- Use ONLY the information from the books provided above when available
- Use the knowledge about Numerological Grid from the system prompt to explain the concept
- If the text has strange spaces between letters, correct and format properly
- Format the text clearly, with well-structured paragraphs
- DO NOT include references to sources or pages in the final text
- If there is not enough information about specific quantities, explain the general concept based on knowledge about presence/absence/excess
- Structure the response with:
  * Section on "What is the Birth Grid"
  * Section on "Analysis of Present Numbers"
  * Section on "Absent Numbers (Lessons to Develop)"
  * Section on "Energy Flow and Balance" """
                
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=2000,
                    top_p=0.9,
                )
                
                explanation_text = chat_completion.choices[0].message.content
                if explanation_text:
                    explanation_text = explanation_text.strip()
                    # Remover referências explícitas a fontes
                    explanation_text = re.sub(r'\[Fonte:[^\]]+\]', '', explanation_text)
                    explanation_text = re.sub(r'Página\s+\d+', '', explanation_text)
                    explanation_text = re.sub(r'Referências?:.*', '', explanation_text, flags=re.IGNORECASE | re.DOTALL)
                    explanation_text = re.sub(r'---.*', '', explanation_text, flags=re.DOTALL)
                    # Limpar espaços extras
                    explanation_text = re.sub(r'\n{3,}', '\n\n', explanation_text)
                    explanation_text = _deduplicate_text(explanation_text)
                
                # Converter sources
                sources_list = [
                    SourceItem(
                        source=doc.get('source', 'knowledge_base'),
                        page=doc.get('page', 1),
                        relevance=doc.get('score', 0.5)
                    )
                    for doc in all_results[:5]
                ]
                
                return BirthGridQuantitiesResponse(
                    explanation=explanation_text or "Não foi possível gerar a explicação.",
                    sources=sources_list,
                    query_used=f"quantidades na grade de nascimento"
                )
            except Exception as e:
                print(f"[ERROR] Erro ao gerar explicação com Groq: {e}")
                import traceback
                print(traceback.format_exc())
        
        # Fallback: SEMPRE tentar com Groq usando o conhecimento do system prompt
        # O system prompt já tem conhecimento suficiente sobre Grade Numerológica
        if groq_client:
            try:
                if lang == 'pt':
                    # Usar o mesmo system_prompt completo que já tem todo o conhecimento
                    system_prompt = """Você é um numerólogo experiente especializado em interpretação de grades de nascimento. Sua função é explicar:
1. O que é a Grade de Nascimento na numerologia
2. O significado das quantidades (quantas vezes cada número aparece) na grade de nascimento

CONCEITO FUNDAMENTAL DA GRADE NUMEROLÓGICA:
A Grade Numerológica é uma grade 3x3 (números de 1 a 9) que pode ser utilizada para o nome completo ou para a data de nascimento. A cada vez que um número aparecer no nome ou data, circulamos o número correspondente na grade. A presença de 3 números numa linha vertical, horizontal ou diagonal denota qualidades em potencial. Normalmente encontramos pelo menos uma linha completa numa grade.

SIGNIFICADO DAS QUANTIDADES NA GRADE:
- Quando um número aparece na grade: indica que a energia desse número está presente e ativa
- Quando um número NÃO aparece na grade (ausente): indica falta dessa energia, problemas relacionados a essa área, ou necessidade de desenvolver essas qualidades
- Quando um número aparece MUITAS vezes (excesso): indica que essa energia está muito presente, mas pode ser mal utilizada ou desequilibrada
- Fluxo de energia: quando temos mais números de um tipo e menos de outro, a energia flui do número mais presente para o menos presente (ex: 5 números 1 e 2 números 2 = energia flui do 1 para o 2)

CARACTERÍSTICAS DOS NÚMEROS:
1 - Ação / o Ser / Ego / Liderança / Recursos Pessoais / Identidade Pessoal / Independência Pessoal
2 - Dualidade / Sentimentos / Carinho / A Mente Consciente / Tato / Diplomacia
3 - Criatividade Pessoal / Comunicação / Poder de Persuasão / Expressão do Ser / Prestação de Serviço
4 - Pensamento Lógico / Espírito Prático / Instintos / O Concreto / O Mundo Material / O trabalho duro / Praticidade
5 - Os Sentidos / Expansão de Consciência / Flexibilidade / Tolerância / Aprendizagem / Mudanças / Liberdade
6 - Criatividade Intelectual / Imaginação / Fantasia / Pensamento Abstrato / Teoria / Família / Responsabilidade / Amor / Harmonia
7 - Estabelecer Limites / Tempo / Ligações Materiais / Os Limites do Mundo Material / A Ponte para o Reino Espiritual / Análise / Pesquisa
8 - Mente Inconsciente / Transformação do Material / Espaço Sem Tempo / Equilíbrio / Dharma: fazer o que tem que ser feito / Organização / Poder Mental
9 - Criatividade Espiritual / Amor Divino / Talentos Inatos / Acabamento / Karma: recompensa pelas ações de vidas passadas / Entrega / Doação

REGRAS CRÍTICAS:
- Use o conhecimento sobre Grade Numerológica acima para explicar o conceito
- Explique de forma prática e clara o que significa ter números com diferentes quantidades
- Explique tanto a presença quanto a ausência de números
- Explique o fluxo de energia entre números quando houver desequilíbrios
- Foque em exemplos práticos e aplicações na vida real
- Formate o texto de forma clara e legível, com parágrafos bem estruturados
- NÃO inclua referências a fontes ou páginas no texto final"""
                    
                    # Preparar informações dos livros (extrair para variável para evitar backslash em f-string)
                    books_info = ''
                    if context_text and len(context_text.strip()) > 50:
                        books_info = f'INFORMAÇÕES DOS LIVROS DE NUMEROLOGIA:\n{context_text}\n\n---\n\n'
                    
                    user_prompt = f"""GRADE DE NASCIMENTO - EXPLICAÇÃO COMPLETA:

DADOS DA GRADE:
{grid_summary_text}

{books_info}

INSTRUÇÕES:

1. PRIMEIRO: Explique o que é a Grade de Nascimento na numerologia usando o conceito fundamental fornecido.

2. DEPOIS: Explique o significado das quantidades na grade de nascimento. Para cada número presente:
   - Explique o que significa ter esse número presente (energia ativa)
   - Explique o que significa ter esse número ausente (falta dessa energia, problemas relacionados, necessidade de desenvolvimento)
   - Explique o que significa ter excesso desse número (energia muito presente, mas pode ser mal utilizada)
   - Analise o fluxo de energia entre números quando houver desequilíbrios

3. ANÁLISE ESPECÍFICA: Para os números que aparecem na grade fornecida, explique:
   - O que significa ter esse número presente e em que quantidade
   - Como essa energia se manifesta na vida da pessoa
   - Quais são as qualidades e desafios relacionados

4. NÚMEROS AUSENTES: Para os números que NÃO aparecem na grade, explique:
   - O que significa a ausência desse número
   - Quais problemas ou dificuldades isso pode indicar
   - O que a pessoa precisa desenvolver nessa área

IMPORTANTE:
- Use o conhecimento sobre Grade Numerológica do system prompt
- Se houver informações dos livros acima, incorpore-as naturalmente
- Formate o texto de forma clara, com parágrafos bem estruturados
- NÃO inclua referências a fontes ou páginas no texto final
- Estruture a resposta com:
  * Seção sobre "O que é a Grade de Nascimento"
  * Seção sobre "Análise dos Números Presentes"
  * Seção sobre "Números Ausentes (Lições a Desenvolver)"
  * Seção sobre "Fluxo de Energia e Equilíbrio"
"""
                else:
                    # Versão em inglês - usar o mesmo conhecimento do system prompt
                    system_prompt = """You are an experienced numerologist specialized in birth grid interpretation. Your function is to explain:
1. What is the Birth Grid in numerology
2. The meaning of quantities (how many times each number appears) in the birth grid

FUNDAMENTAL CONCEPT OF THE NUMEROLOGICAL GRID:
The Numerological Grid is a 3x3 grid (numbers 1 to 9) that can be used for the full name or birth date. Each time a number appears in the name or date, we circle the corresponding number in the grid. The presence of 3 numbers in a vertical, horizontal or diagonal line denotes potential qualities. Normally we find at least one complete line in a grid.

MEANING OF QUANTITIES IN THE GRID:
- When a number appears in the grid: indicates that the energy of that number is present and active
- When a number does NOT appear in the grid (absent): indicates lack of this energy, problems related to this area, or need to develop these qualities
- When a number appears MANY times (excess): indicates that this energy is very present, but may be misused or unbalanced
- Energy flow: when we have more numbers of one type and fewer of another, energy flows from the more present number to the less present one (ex: 5 number 1s and 2 number 2s = energy flows from 1 to 2)

CHARACTERISTICS OF NUMBERS:
1 - Action / the Being / Ego / Leadership / Personal Resources / Personal Identity / Personal Independence
2 - Duality / Feelings / Affection / The Conscious Mind / Tact / Diplomacy
3 - Personal Creativity / Communication / Power of Persuasion / Expression of Being / Service
4 - Logical Thinking / Practical Spirit / Instincts / The Concrete / The Material World / Hard work / Practicality
5 - The Senses / Consciousness Expansion / Flexibility / Tolerance / Learning / Changes / Freedom
6 - Intellectual Creativity / Imagination / Fantasy / Abstract Thinking / Theory / Family / Responsibility / Love / Harmony
7 - Establishing Limits / Time / Material Connections / The Limits of the Material World / The Bridge to the Spiritual Realm / Analysis / Research
8 - Unconscious Mind / Material Transformation / Space Without Time / Balance / Dharma: doing what needs to be done / Organization / Mental Power
9 - Spiritual Creativity / Divine Love / Inborn Talents / Completion / Karma: reward for actions from past lives / Surrender / Giving

CRITICAL RULES:
- Use the knowledge about Numerological Grid above to explain the concept
- Explain in a practical and clear way what it means to have numbers with different quantities
- Explain both the presence and absence of numbers
- Explain the energy flow between numbers when there are imbalances
- Focus on practical examples and real-life applications
- Format the text clearly, with well-structured paragraphs
- DO NOT include references to sources or pages in the final text"""
                    
                    # Preparar informações dos livros (extrair para variável para evitar backslash em f-string)
                    books_info_en = ''
                    if context_text and len(context_text.strip()) > 50:
                        books_info_en = f'NUMEROLOGY BOOKS INFORMATION:\n{context_text}\n\n---\n\n'
                    
                    user_prompt = f"""BIRTH GRID - COMPLETE EXPLANATION:

GRID DATA:
{grid_summary_text}

{books_info_en}

INSTRUCTIONS:

1. FIRST: Explain what the Birth Grid is in numerology using the fundamental concept provided.

2. THEN: Explain the meaning of quantities in the birth grid. For each number present:
   - Explain what it means to have this number present (active energy)
   - Explain what it means to have this number absent (lack of this energy, related problems, need for development)
   - Explain what it means to have excess of this number (energy very present, but may be misused)
   - Analyze the energy flow between numbers when there are imbalances

3. SPECIFIC ANALYSIS: For the numbers that appear in the provided grid, explain:
   - What it means to have this number present and in what quantity
   - How this energy manifests in the person's life
   - What are the related qualities and challenges

4. ABSENT NUMBERS: For numbers that do NOT appear in the grid, explain:
   - What the absence of this number means
   - What problems or difficulties this may indicate
   - What the person needs to develop in this area

IMPORTANT:
- Use the knowledge about Numerological Grid from the system prompt
- If there is information from the books above, incorporate it naturally
- Format the text clearly, with well-structured paragraphs
- DO NOT include references to sources or pages in the final text
- Structure the response with:
  * Section on "What is the Birth Grid"
  * Section on "Analysis of Present Numbers"
  * Section on "Absent Numbers (Lessons to Develop)"
  * Section on "Energy Flow and Balance" """
                
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=2500,  # Aumentado para permitir respostas mais completas
                    top_p=0.9,
                )
                
                explanation_text = chat_completion.choices[0].message.content
                if explanation_text:
                    explanation_text = explanation_text.strip()
                    # Remover referências
                    explanation_text = re.sub(r'\[Fonte:[^\]]+\]', '', explanation_text)
                    explanation_text = re.sub(r'Página\s+\d+', '', explanation_text)
                    explanation_text = re.sub(r'Referências?:.*', '', explanation_text, flags=re.IGNORECASE | re.DOTALL)
                    explanation_text = re.sub(r'---.*', '', explanation_text, flags=re.DOTALL)
                    explanation_text = re.sub(r'\n{3,}', '\n\n', explanation_text)
                    
                    return BirthGridQuantitiesResponse(
                        explanation=explanation_text,
                        sources=[],
                        query_used="quantidades na grade de nascimento"
                    )
            except Exception as e:
                print(f"[ERROR] Erro ao gerar explicação com Groq: {e}")
                import traceback
                traceback.print_exc()
                # Se Groq falhar, usar fallback baseado no conhecimento do sistema
                print("[INFO] Usando fallback baseado no conhecimento do sistema devido a erro no Groq")
                fallback_explanation = _generate_quantities_fallback(request.grid, lang)
                return BirthGridQuantitiesResponse(
                    explanation=fallback_explanation,
                    sources=[],
                    query_used="quantidades na grade de nascimento"
                )
        
        # Último fallback: usar explicação baseada no conhecimento do sistema
        # Isso só deve acontecer se Groq não estiver disponível (já tratado acima)
        print("[INFO] Gerando explicação de fallback baseada no conhecimento do sistema")
        fallback_explanation = _generate_quantities_fallback(request.grid, lang)
        
        return BirthGridQuantitiesResponse(
            explanation=fallback_explanation,
            sources=[],
            query_used="quantidades na grade de nascimento"
        )
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao obter interpretação de quantidades: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter interpretação de quantidades: {str(e)}"
        )

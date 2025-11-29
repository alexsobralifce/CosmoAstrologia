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
from app.services.rag_service_wrapper import get_rag_service
from app.services.transits_calculator import calculate_future_transits
from app.services.astrology_calculator import calculate_solar_return
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
def get_interpretation(
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
        
        interpretation = rag_service.get_interpretation(
            planet=request.planet,
            sign=request.sign,
            house=request.house,
            aspect=request.aspect,
            custom_query=request.custom_query,
            use_groq=request.use_groq
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
        
        return InterpretationResponse(
            interpretation=interpretation['interpretation'],
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
        # Verificar se o índice está disponível
        has_index = False
        if hasattr(rag_service, 'index'):
            has_index = rag_service.index is not None
        elif hasattr(rag_service, 'embeddings'):
            has_index = rag_service.embeddings is not None and hasattr(rag_service, 'documents') and len(rag_service.documents) > 0
        
        if not has_index:
            return {
                "query": query,
                "results": [],
                "count": 0,
                "error": "Índice RAG não carregado. Execute build_rag_index_llamaindex.py primeiro."
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
        
        # Verificar se é LlamaIndex ou implementação antiga
        has_llamaindex = hasattr(rag_service, 'index')
        
        if has_llamaindex:
            # Implementação LlamaIndex
            has_index = rag_service.index is not None
            has_groq = rag_service.groq_client is not None
            # Para LlamaIndex, verificar se o índice foi carregado
            try:
                from llama_index.core import VectorStoreIndex
                has_dependencies = True
            except ImportError:
                has_dependencies = False
            
            return {
                "available": has_index and has_dependencies,
                "document_count": 0,  # LlamaIndex não expõe contagem direta
                "has_dependencies": has_dependencies,
                "has_groq": has_groq,
                "model_loaded": has_dependencies,
                "index_loaded": has_index,
                "implementation": "llamaindex",
                "error": None if (has_index and has_dependencies) else "LlamaIndex não instalado ou índice não carregado"
            }
        else:
            # Implementação antiga (não deveria acontecer, mas mantido para compatibilidade)
            has_index = hasattr(rag_service, 'embeddings') and rag_service.embeddings is not None and hasattr(rag_service, 'documents') and len(rag_service.documents) > 0
            has_groq = rag_service.groq_client is not None
            has_model = hasattr(rag_service, 'model') and rag_service.model is not None
            
            return {
                "available": has_index and has_model,
                "document_count": len(rag_service.documents) if has_index else 0,
                "has_dependencies": has_model,
                "has_groq": has_groq,
                "model_loaded": has_model,
                "index_loaded": has_index,
                "implementation": "legacy",
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
                    has_index = (hasattr(rag_service, 'index') and rag_service.index is not None) or \
                               (hasattr(rag_service, 'embeddings') and rag_service.embeddings is not None and 
                                hasattr(rag_service, 'documents') and len(rag_service.documents) > 0)
                    if has_index:
                        # A descrição base já é completa com exemplos práticos
                        # Não precisa enriquecer com RAG/Groq para não cortar o texto
                        print(f"[INFO] Usando descrição base completa: {transit.get('planet')} {transit.get('aspect_type')} com {natal_point_display}")
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

REGRAS DE ESCRITA:
- Use linguagem simples e direta, como se estivesse conversando com um amigo
- Evite jargões astrológicos técnicos (se usar, explique imediatamente)
- Foque em como isso aparece na vida prática: relacionamentos, trabalho, personalidade, decisões
- Use exemplos concretos e situações reais
- Seja específico, não genérico
- Escreva de forma acolhedora e encorajadora
- Use parágrafos curtos e bem estruturados"""
    
    house_text = f" na Casa {house}" if house else ""
    
    user_prompt = f"""MAPA ASTRAL DE {name_str.upper() if userName else 'VOCÊ'}:

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
- Foque em como isso aparece na vida real, não em teorias astrológicas"""
    
    return system_prompt, user_prompt


@router.post("/interpretation/planet")
def get_planet_interpretation(
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
        results = rag_service.search(query, top_k=10, expand_query=True)
        
        # Preparar contexto dos documentos
        context_text = "\n\n".join([
            doc.get('text', '')
            for doc in results[:8]  # Usar até 8 documentos
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
        if rag_service.groq_client:
            try:
                print(f"[PLANET API] Gerando interpretação com novo prompt prático para {planet} em {sign}")
                print(f"[PLANET API] Contexto do mapa: Sol={request.sunSign}, Lua={request.moonSign}, Asc={request.ascendant}")
                
                chat_completion = rag_service.groq_client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
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
        for q in queries:
            try:
                results = rag_service.search(q, top_k=10, expand_query=True)
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
                
                fallback_results = rag_service.search(fallback_query, top_k=15, expand_query=True)
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
        if rag_service.groq_client:
            try:
                # Prompt detalhado para gerar pelo menos 2 parágrafos
                system_prompt = """Você é um astrólogo experiente especializado em interpretação de regentes do mapa astral. 
Sua função é criar interpretações profundas, didáticas e detalhadas sobre o planeta regente do mapa, explicando sua importância fundamental para o autoconhecimento.

REGRAS DE FORMATAÇÃO:
- Sempre escreva NO MÍNIMO 2 parágrafos completos e densos (mínimo 300 palavras)
- Use estrutura didática com títulos em negrito quando apropriado
- Explique termos astrológicos de forma simples
- Conecte as informações de forma narrativa, não apenas listas
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
                
                chat_completion = rag_service.groq_client.chat.completions.create(
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
            top_k=12  # Aumentar top_k no fallback também
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
    """Retorna o prompt mestre para geração do Mapa Astral baseado na nova estrutura fornecida."""
    if language == 'en':
        return """**Role:** You are a Senior Astrologer, specialist in integrating **Modern Psychological Astrology** (Stephen Arroyo's line) with the technical precision of **Classical/Traditional Astrology** (Dignities, Rulerships) and the depth of **Karmic Astrology**. Your language is empathetic, therapeutic, but focused on practical guidance and strategic decision-making.

**Task:** Perform a deep and complete interpretation of the Natal Chart below.

**Birth Data:** [INSERT DATE, TIME AND PLACE HERE]

**Analysis Guidelines:**

Use a synthesis approach. Do not describe isolated positions (e.g., "Sun in house X means Y"); instead, connect the points to tell the person's story, integrating conscious will, emotional needs and destiny.

**CRITICAL RULES - AVOID REPETITIONS:**
- NEVER repeat information already mentioned in previous sections or interpretations
- Each section must bring NEW and UNIQUE insights
- If you've already explained something about a planet, sign, or house in one section, do NOT repeat it in another section
- Connect different information, don't duplicate
- Always bring fresh perspectives and new connections
- Avoid generic phrases that could apply to anyone - be specific to THIS person's chart

**STYLE:**
- Use clear, empathetic and therapeutic language
- Focus on practical guidance and strategic decision-making
- Avoid excessive "astrologuese" without explanation
- Empower the consultee with actionable insights

**ADDITIONAL RULES:**
- DO NOT include Python code, code blocks or orbital periods of planets
- DO NOT include information about Vedic Astrology, Jyotish, Sidereal zodiac, Dasas, Vargas or differences between Tropical and Sidereal
- NEVER write "House not provided", "in House not provided", "Casa não informada" or any variation - if the house is not available in the data, simply OMIT mentioning the house and focus only on the sign"""
    else:
        return """**Role:** Você é um Astrólogo Sênior, especialista em integrar a **Astrologia Psicológica Moderna** (linha de Stephen Arroyo) com a precisão técnica da **Astrologia Clássica/Tradicional** (Dignidades, Regências) e a profundidade da **Astrologia Kármica**. Sua linguagem é empática, terapêutica, mas focada em orientações práticas e tomada de decisão estratégica.

**Tarefa:** Realizar uma interpretação profunda e completa do Mapa Natal abaixo.

**Dados do Nascimento:** [INSERIR DATA, HORA E LOCAL AQUI]

**Diretrizes de Análise:**

Utilize uma abordagem de síntese. Não descreva posições isoladas (ex: "Sol na casa X significa Y"); em vez disso, conecte os pontos para contar a história da pessoa, integrando a vontade consciente, necessidades emocionais e destino.

**REGRAS CRÍTICAS - EVITAR REPETIÇÕES:**
- NUNCA repita informações já mencionadas em seções ou interpretações anteriores
- Cada seção deve trazer insights NOVOS e ÚNICOS
- Se você já explicou algo sobre um planeta, signo ou casa em uma seção, NÃO repita em outra seção
- Conecte informações diferentes, não duplique
- Sempre traga perspectivas frescas e novas conexões
- Evite frases genéricas que poderiam se aplicar a qualquer pessoa - seja específico ao mapa DESTA pessoa

**ESTILO:**
- Use linguagem clara, empática e terapêutica
- Foco em orientações práticas e tomada de decisão estratégica
- Evite "astrologuês" excessivo sem explicação
- Empodere o consulente com insights acionáveis

**REGRAS ADICIONAIS:**
- NÃO inclua código Python, blocos de código ou períodos orbitais dos planetas
- NÃO inclua informações sobre Astrologia Védica, Jyotish, zodíaco Sideral, Dasas, Vargas ou diferenças entre Tropical e Sideral
- NUNCA escreva "Casa não informada", "na Casa não informada", "House not provided" ou qualquer variação - se a casa não estiver disponível nos dados, simplesmente OMITA a menção à casa e foque apenas no signo"""


def _get_full_chart_context(request: FullBirthChartRequest, lang: str = 'pt') -> str:
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
- Quíron em {request.chironSign or 'não calculado'}{f' na Casa {request.chironHouse}' if request.chironHouse else ''} (Ferida/Dom de Cura){lilith_str}"""
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
- Chiron in {request.chironSign or 'not calculated'}{f' in House {request.chironHouse}' if request.chironHouse else ''} (Wound/Healing Gift){lilith_str}"""


def _generate_section_prompt(request: FullBirthChartRequest, section: str) -> Tuple[str, str]:
    """Gera o prompt específico para cada seção do mapa baseado na nova estrutura fornecida."""
    lang = request.language or 'pt'
    
    # Contexto completo do mapa para referência
    full_context = _get_full_chart_context(request, lang)
    
    # Data de nascimento formatada para inserção no prompt
    birth_data_str = f"Data: {request.birthDate}, Hora: {request.birthTime}, Local: {request.birthPlace}"
    
    if section == 'power':
        title = "A Estrutura de Poder (Temperamento e Motivação)" if lang == 'pt' else "The Power Structure (Temperament and Motivation)"
        if lang == 'pt':
            prompt = f"""{full_context}

**SEÇÃO 1: A ESTRUTURA DE PODER (TEMPERAMENTO E MOTIVAÇÃO)**

* **Balanço de Elementos e Qualidades:** Analise a distribuição de Fogo, Terra, Ar e Água e as modalidades (Cardeal, Fixo, Mutável). Identifique excessos (o que sobra) e escassez (o que falta). Dê conselhos práticos de como equilibrar isso na rotina.

* **O Regente do Mapa:** Identifique o planeta regente do Ascendente {request.ascendant} e analise sua condição (Signo, Casa, Aspectos). Ele é um aliado ou um desafio para o nativo?

IMPORTANTE:
- Não repita informações já mencionadas em outras seções
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação - se a casa não estiver disponível, OMITA completamente a menção à casa
- Foque no temperamento como motor de motivação e ação
- Analise o regente do mapa com profundidade técnica (Dignidades, Regências)
- Dê conselhos práticos e acionáveis para equilíbrio energético"""
        else:
            prompt = f"""{full_context}

**SECTION 1: THE POWER STRUCTURE (TEMPERAMENT AND MOTIVATION)**

* **Balance of Elements and Qualities:** Analyze the distribution of Fire, Earth, Air and Water and the modalities (Cardinal, Fixed, Mutable). Identify excesses (what is in surplus) and scarcity (what is lacking). Give practical advice on how to balance this in routine.

* **The Chart Ruler:** Identify the planet ruling the Ascendant {request.ascendant} and analyze its condition (Sign, House, Aspects). Is it an ally or a challenge for the native?

IMPORTANT:
- Do not repeat information already mentioned in other sections
- NEVER write "House not provided", "in House not provided" or any variation - if the house is not available, COMPLETELY OMIT mentioning the house
- Focus on temperament as a driver of motivation and action
- Analyze the chart ruler with technical depth (Dignities, Rulerships)
- Give practical and actionable advice for energy balance"""
    
    elif section == 'triad':
        title = "A Tríade Fundamental (O Núcleo da Personalidade)" if lang == 'pt' else "The Fundamental Triad (The Core of Personality)"
        if lang == 'pt':
            prompt = f"""{full_context}

**SEÇÃO 2: A TRÍADE FUNDAMENTAL (O NÚCLEO DA PERSONALIDADE)**

* Faça uma síntese de **Sol** (Identidade/Essência), **Lua** (Emoções/Passado/Reações) e **Ascendente** (Persona/Corpo).

* Explique a dinâmica entre eles: a vontade consciente (Sol) está em harmonia com as necessidades emocionais (Lua) e a forma de agir (Ascendente)?

DADOS:
- Sol em {request.sunSign} na Casa {request.sunHouse}
- Lua em {request.moonSign} na Casa {request.moonHouse}
- Ascendente em {request.ascendant}

IMPORTANTE:
- Não repita informações já mencionadas em outras seções
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação
- Faça uma síntese que conecte os três pontos para contar a história da pessoa
- Analise a dinâmica entre vontade consciente (Sol), necessidades emocionais (Lua) e forma de agir (Ascendente)
- Use abordagem de síntese, evitando descrições fragmentadas ou isoladas
- Explique como eles se equilibram ou conflitam"""
        else:
            prompt = f"""{full_context}

**SECTION 2: THE FUNDAMENTAL TRIAD (THE CORE OF PERSONALITY)**

* Make a synthesis of **Sun** (Identity/Essence), **Moon** (Emotions/Past/Reactions) and **Ascendant** (Persona/Body).

* Explain the dynamics between them: is conscious will (Sun) in harmony with emotional needs (Moon) and way of acting (Ascendant)?

DATA:
- Sun in {request.sunSign} in House {request.sunHouse}
- Moon in {request.moonSign} in House {request.moonHouse}
- Ascendant in {request.ascendant}

IMPORTANT:
- Do not repeat information already mentioned in other sections
- NEVER write "House not provided", "in House not provided" or any variation
- Make a synthesis that connects the three points to tell the person's story
- Analyze the dynamics between conscious will (Sun), emotional needs (Moon) and way of acting (Ascendant)
- Use a synthesis approach, avoiding fragmented or isolated descriptions
- Explain how they balance or conflict"""
    
    elif section == 'personal':
        title = "Dinâmica Pessoal e Ferramentas (Planetas Pessoais)" if lang == 'pt' else "Personal Dynamics and Tools (Personal Planets)"
        if lang == 'pt':
            prompt = f"""{full_context}

**SEÇÃO 3: DINÂMICA PESSOAL E FERRAMENTAS (PLANETAS PESSOAIS)**

* **Intelecto (Mercúrio):** Como a pessoa processa informações, aprende e toma decisões.

* **Afeto e Valores (Vênus):** Analise a condição de Vênus (Dignidades/Debilidades). Como a pessoa ama, o que valoriza e como lida com recursos.

* **Ação e Conquista (Marte):** Onde coloca sua energia, assertividade e impulso sexual.

DADOS:
- Mercúrio em {request.mercurySign or 'não informado'}{f' na Casa {request.mercuryHouse}' if request.mercuryHouse else ''}
- Vênus em {request.venusSign or 'não informado'}{f' na Casa {request.venusHouse}' if request.venusHouse else ''}
- Marte em {request.marsSign or 'não informado'}{f' na Casa {request.marsHouse}' if request.marsHouse else ''}

IMPORTANTE:
- Não repita informações já mencionadas em outras seções
- USE OS DADOS ESPECÍFICOS FORNECIDOS ACIMA - não use frases genéricas como "Casa não informada"
- Se a casa não estiver disponível, foque no signo e no planeta apenas
- Analise Vênus com técnica de Dignidades/Debilidades (Astrologia Clássica)
- Foque em como cada planeta funciona como ferramenta prática na vida
- Conecte com exemplos concretos de manifestação baseados nos dados fornecidos"""
        else:
            prompt = f"""{full_context}

**SECTION 3: PERSONAL DYNAMICS AND TOOLS (PERSONAL PLANETS)**

* **Intellect (Mercury):** How the person processes information, learns and makes decisions.

* **Affection and Values (Venus):** Analyze Venus's condition (Dignities/Debilities). How the person loves, what they value and how they handle resources.

* **Action and Conquest (Mars):** Where they put their energy, assertiveness and sexual drive.

DATA:
- Mercury in {request.mercurySign or 'not provided'}{f' in House {request.mercuryHouse}' if request.mercuryHouse else ''}
- Venus in {request.venusSign or 'not provided'}{f' in House {request.venusHouse}' if request.venusHouse else ''}
- Mars in {request.marsSign or 'not provided'}{f' in House {request.marsHouse}' if request.marsHouse else ''}

IMPORTANT:
- Do not repeat information already mentioned in other sections
- USE THE SPECIFIC DATA PROVIDED ABOVE - do not use generic phrases like "House not provided"
- If the house is not available, focus on the sign and planet only
- Analyze Venus with Dignities/Debilities technique (Classical Astrology)
- Focus on how each planet functions as a practical tool in life
- Connect with concrete examples of manifestation based on the provided data"""
    
    elif section == 'houses':
        title = "Análise Setorial Avançada (Vida Prática e Casas)" if lang == 'pt' else "Advanced Sectorial Analysis (Practical Life and Houses)"
        if lang == 'pt':
            prompt = f"""{full_context}

**SEÇÃO 4: ANÁLISE SETORIAL AVANÇADA (VIDA PRÁTICA E CASAS)**

* **Instrução:** Para as casas abaixo, analise não apenas os planetas presentes, mas também a condição dos **Regentes das Casas** (os "donos" da área).

* **Finanças e Vocação (Casas 2, 6 e 10):** Onde está o potencial financeiro real? Qual a vocação que traz realização versus a rotina de trabalho?

* **Relacionamentos (Casa 7):** O padrão de parceiro atraído versus o que a pessoa realmente necessita para evoluir.

* **Família e Base (Casa 4):** Dinâmicas familiares, raízes e o ambiente doméstico necessário para recarregar (Lua).

* **Saúde (Casa 6):** Pontos de atenção vital e sugestões de equilíbrio baseadas nos Elementos.

DADOS RELEVANTES:
- Meio do Céu em {request.midheavenSign or 'não informado'}
- Fundo do Céu (IC) em {request.icSign or 'não informado'}
- Lua em {request.moonSign} na Casa {request.moonHouse}

IMPORTANTE:
- Não repita informações já mencionadas em outras seções
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação - use apenas os dados fornecidos ou omita a informação
- Analise os REGENTES das casas, não apenas os planetas presentes
- Diferencie vocação (Casa 10) de rotina de trabalho (Casa 6)
- Analise padrões de relacionamento com profundidade psicológica"""
        else:
            prompt = f"""{full_context}

**SECTION 4: ADVANCED SECTORIAL ANALYSIS (PRACTICAL LIFE AND HOUSES)**

* **Instruction:** For the houses below, analyze not only the planets present, but also the condition of the **House Rulers** (the "owners" of the area).

* **Finances and Vocation (Houses 2, 6 and 10):** Where is the real financial potential? What vocation brings fulfillment versus work routine?

* **Relationships (House 7):** The pattern of attracted partner versus what the person really needs to evolve.

* **Family and Base (House 4):** Family dynamics, roots and the domestic environment necessary to recharge (Moon).

* **Health (House 6):** Vital attention points and balance suggestions based on Elements.

RELEVANT DATA:
- Midheaven in {request.midheavenSign or 'not provided'}
- IC in {request.icSign or 'not provided'}
- Moon in {request.moonSign} in House {request.moonHouse}

IMPORTANT:
- Do not repeat information already mentioned in other sections
- NEVER write "House not provided", "in House not provided" or any variation - use only the provided data or omit the information
- Analyze the HOUSE RULERS, not just the planets present
- Differentiate vocation (House 10) from work routine (House 6)
- Analyze relationship patterns with psychological depth"""
    
    elif section == 'karma':
        title = "Expansão, Estrutura e Karma (Planetas Sociais e Transpessoais)" if lang == 'pt' else "Expansion, Structure and Karma (Social and Transpersonal Planets)"
        if lang == 'pt':
            # Preparar string de Lilith para evitar backslash em f-string
            lilith_str = f'\n- Lilith em {request.lilithSign} na Casa {request.lilithHouse}' if request.lilithSign and request.lilithHouse else ''
            prompt = f"""{full_context}

**SEÇÃO 5: EXPANSÃO, ESTRUTURA E KARMA (PLANETAS SOCIAIS E TRANSPESSOAIS)**

* **Júpiter e Saturno:** Onde a pessoa tem sorte/fé natural e onde enfrenta seus maiores testes, medos e responsabilidades.

* **O Caminho da Alma (Nodos Lunares):** Qual zona de conforto (Nodo Sul) deve ser abandonada e qual missão de vida (Nodo Norte) deve ser perseguida?

* **Feridas e Sombras (Quíron e Lilith):** Onde reside a ferida que cura (Quíron) e a força visceral/insubmissão (Lilith).

DADOS:
- Júpiter em {request.jupiterSign or 'não informado'}{f' na Casa {request.jupiterHouse}' if request.jupiterHouse else ''}
- Saturno em {request.saturnSign or 'não informado'}{f' na Casa {request.saturnHouse}' if request.saturnHouse else ''}
- Nodo Norte em {request.northNodeSign or 'não informado'}{f' na Casa {request.northNodeHouse}' if request.northNodeHouse else ''}
- Nodo Sul em {request.southNodeSign or 'não informado'}{f' na Casa {request.southNodeHouse}' if request.southNodeHouse else ''}
- Quíron em {request.chironSign or 'não informado'}{f' na Casa {request.chironHouse}' if request.chironHouse else ''}{lilith_str}

IMPORTANTE CRÍTICO:
- USE APENAS OS DADOS FORNECIDOS ACIMA - se a casa não estiver disponível, OMITA completamente a menção à casa, não diga "Casa não informada" ou "na Casa não informada"
- Se você não tiver a informação da casa, simplesmente não mencione a casa - foque apenas no signo
- NUNCA escreva "na Casa não informada", "Casa não informada" ou qualquer variação disso
- Não repita informações já mencionadas em outras seções
- Analise Júpiter e Saturno como polaridades (expansão vs. estrutura)
- Conecte os nodos lunares com propósito de vida e evolução da alma
- Explique Quíron e Lilith como ferramentas de transformação"""
        else:
            # Preparar string de Lilith para evitar backslash em f-string
            lilith_str = f'\n- Lilith in {request.lilithSign} in House {request.lilithHouse}' if request.lilithSign and request.lilithHouse else ''
            prompt = f"""{full_context}

**SECTION 5: EXPANSION, STRUCTURE AND KARMA (SOCIAL AND TRANSPERSONAL PLANETS)**

* **Jupiter and Saturn:** Where the person has natural luck/faith and where they face their greatest tests, fears and responsibilities.

* **The Path of the Soul (Lunar Nodes):** What comfort zone (South Node) should be abandoned and what life mission (North Node) should be pursued?

* **Wounds and Shadows (Chiron and Lilith):** Where resides the wound that heals (Chiron) and the visceral/insubordinate force (Lilith).

DATA:
- Jupiter in {request.jupiterSign or 'not provided'}{f' in House {request.jupiterHouse}' if request.jupiterHouse else ''}
- Saturn in {request.saturnSign or 'not provided'}{f' in House {request.saturnHouse}' if request.saturnHouse else ''}
- North Node in {request.northNodeSign or 'not provided'}{f' in House {request.northNodeHouse}' if request.northNodeHouse else ''}
- South Node in {request.southNodeSign or 'not provided'}{f' in House {request.southNodeHouse}' if request.southNodeHouse else ''}
- Chiron in {request.chironSign or 'not provided'}{f' in House {request.chironHouse}' if request.chironHouse else ''}{lilith_str}

CRITICAL IMPORTANT:
- USE ONLY THE DATA PROVIDED ABOVE - if the house is not available, COMPLETELY OMIT mentioning the house, do not say "House not provided" or "in House not provided"
- If you don't have the house information, simply don't mention the house - focus only on the sign
- NEVER write "in House not provided", "House not provided" or any variation of that
- Do not repeat information already mentioned in other sections
- Analyze Jupiter and Saturn as polarities (expansion vs. structure)
- Connect lunar nodes with life purpose and soul evolution
- Explain Chiron and Lilith as transformation tools"""
    
    elif section == 'synthesis':
        title = "Síntese e Orientação Estratégica" if lang == 'pt' else "Strategic Synthesis and Guidance"
        if lang == 'pt':
            prompt = f"""{full_context}

**SEÇÃO 6: SÍNTESE E ORIENTAÇÃO ESTRATÉGICA**

* **Pontos Fortes a Explorar:** (Destaque Stelliums, Trígonos exatos ou Planetas em Domicílio/Exaltação).

* **Desafios e Cuidados:** (Destaque Quadraturas T, Planetas em Queda/Exílio ou Casas vazias de elemento).

* **Conselho Final:** Uma diretriz prática e empoderadora para a evolução pessoal e tomada de decisão.

IMPORTANTE:
- NÃO repita informações já detalhadas nas seções anteriores
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação
- Faça uma síntese integradora que conecte TODOS os elementos já analisados
- Identifique pontos técnicos específicos (Stelliums, Dignidades, Aspectos exatos)
- Ofereça uma diretriz estratégica e empoderadora
- Foque em tomada de decisão prática e evolução pessoal"""
        else:
            prompt = f"""{full_context}

**SECTION 6: STRATEGIC SYNTHESIS AND GUIDANCE**

* **Strengths to Explore:** (Highlight Stelliums, Exact Trines or Planets in Domicile/Exaltation).

* **Challenges and Cautions:** (Highlight T-Squares, Planets in Fall/Exile or Houses empty of element).

* **Final Counsel:** A practical and empowering directive for personal evolution and decision-making.

IMPORTANT:
- DO NOT repeat information already detailed in previous sections
- NEVER write "House not provided", "in House not provided" or any variation
- Make an integrating synthesis that connects ALL elements already analyzed
- Identify specific technical points (Stelliums, Dignities, Exact Aspects)
- Offer a strategic and empowering directive
- Focus on practical decision-making and personal evolution"""
    
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
    
    Seções disponíveis (baseadas na nova estrutura):
    - power: A Estrutura de Poder (Temperamento e Motivação) - Elementos, Qualidades e Regente do Mapa
    - triad: A Tríade Fundamental (O Núcleo da Personalidade) - Sol, Lua, Ascendente
    - personal: Dinâmica Pessoal e Ferramentas - Mercúrio, Vênus, Marte
    - houses: Análise Setorial Avançada - Casas 2, 4, 6, 7, 10 e Regentes
    - karma: Expansão, Estrutura e Karma - Júpiter, Saturno, Nodos, Quíron, Lilith
    - synthesis: Síntese e Orientação Estratégica - Pontos Fortes, Desafios e Conselho Final
    """
    try:
        if not request.section:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Especifique uma seção: power, triad, personal, houses, karma, synthesis"
            )
        
        rag_service = get_rag_service()
        lang = request.language or 'pt'
        
        # Verificar se o RAG service está funcionando
        if not rag_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço RAG não disponível. Verifique a configuração."
            )
        
        # Tentar carregar índice se não estiver carregado
        has_index = False
        if hasattr(rag_service, 'index'):
            has_index = rag_service.index is not None
        elif hasattr(rag_service, 'documents'):
            has_index = len(rag_service.documents) > 0
        
        if not has_index:
            print("[WARNING] Índice RAG vazio, tentando carregar...")
            if hasattr(rag_service, 'load_index'):
                if not rag_service.load_index():
                    print("[WARNING] Não foi possível carregar índice RAG. Continuando com base local.")
            else:
                print("[WARNING] Método load_index não disponível. Continuando com base local.")
        
        # Obter prompt mestre e prompt da seção
        master_prompt = _get_master_prompt(lang)
        title, section_prompt = _generate_section_prompt(request, request.section)
        
        # Buscar contexto relevante do RAG
        search_queries = {
            'power': f"regente do mapa ascendente {request.ascendant} elementos fogo terra ar água qualidades cardeal fixo mutável temperamento",
            'triad': f"Sol Lua Ascendente personalidade tríade {request.sunSign} {request.moonSign} {request.ascendant} dinâmica",
            'personal': f"Mercúrio Vênus Marte planetas pessoais dignidades debilidades {request.mercurySign or ''} {request.venusSign or ''} {request.marsSign or ''}",
            'houses': f"casas astrológicas regentes casas Casa 2 Casa 4 Casa 6 Casa 7 Casa 10 vocação finanças relacionamentos",
            'karma': f"Júpiter Saturno Nodo Norte Sul karma evolução {request.northNodeSign or ''} Quíron Lilith propósito vida",
            'synthesis': f"síntese mapa astral integração stelliums trígonos quadraturas dignidades exaltação queda exílio"
        }
        
        query = search_queries.get(request.section, "interpretação mapa astral")
        
        # Buscar contexto do RAG com tratamento de erro
        rag_results = []
        try:
            rag_results = rag_service.search(query, top_k=10)
        except Exception as e:
            print(f"[WARNING] Erro ao buscar no RAG: {e}")
            # Continuar sem RAG se houver erro
        
        # Preparar contexto
        context_text = "\n\n".join([doc.get('text', '') for doc in rag_results[:8] if doc.get('text')])
        
        # Se não houver contexto do RAG, usar base local
        if not context_text or len(context_text.strip()) < 100:
            try:
                from app.services.local_knowledge_base import LocalKnowledgeBase
                local_kb = LocalKnowledgeBase()
                local_results = local_kb.get_context(
                    planet=request.sunSign if request.section == 'triad' else None,
                    sign=request.sunSign,
                    house=request.sunHouse if request.section == 'roots' else None,
                    query=query
                )
                if local_results:
                    context_text = "\n\n".join([ctx.get('text', '') for ctx in local_results[:5] if ctx.get('text')])
            except Exception as e:
                print(f"[WARNING] Erro ao usar base local: {e}")
        
        # Gerar interpretação com Groq
        if rag_service.groq_client:
            try:
                from groq import Groq
                
                # Limitar contexto para evitar token overflow
                context_limit = min(len(context_text), 3000)
                context_snippet = context_text[:context_limit] if context_text else "Informações astrológicas gerais sobre o tema."
                
                full_user_prompt = f"""{section_prompt}

---

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_snippet}"""
                
                chat_completion = rag_service.groq_client.chat.completions.create(
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
                
                return FullBirthChartResponse(
                    section=request.section,
                    title=title,
                    content=content.strip(),
                    generated_by="groq"
                )
                
            except Exception as e:
                print(f"[ERROR] Erro ao gerar com Groq: {e}")
                import traceback
                print(f"[ERROR] Traceback: {traceback.format_exc()}")
                # Tentar fallback com RAG apenas
                if rag_results and len(rag_results) > 0:
                    fallback_content = "\n\n".join([doc['text'] for doc in rag_results[:3]])
                    if fallback_content and len(fallback_content) > 100:
                        return FullBirthChartResponse(
                            section=request.section,
                            title=title,
                            content=fallback_content[:2000],  # Limitar tamanho
                            generated_by="rag_only"
                        )
        
        # Fallback final: usar base de conhecimento local
        try:
            from app.services.local_knowledge_base import LocalKnowledgeBase
            local_kb = LocalKnowledgeBase()
            local_context = local_kb.get_context(
                planet=request.sunSign if request.section == 'triad' else None,
                sign=request.sunSign,
                house=request.sunHouse if request.section == 'roots' else None,
                query=query
            )
            
            if local_context and len(local_context) > 0:
                fallback_text = "\n\n".join([ctx.get('text', '') for ctx in local_context[:2] if ctx.get('text')])
                if fallback_text and len(fallback_text) > 100:
                    return FullBirthChartResponse(
                        section=request.section,
                        title=title,
                        content=fallback_text[:2000],
                        generated_by="local_kb"
                    )
        except Exception as e:
            print(f"[ERROR] Erro ao usar base local: {e}")
        
        # Último fallback: mensagem de erro
        error_msg = "Não foi possível gerar a análise no momento. Por favor, tente novamente." if lang == 'pt' else "Could not generate the analysis at this time. Please try again."
        return FullBirthChartResponse(
            section=request.section,
            title=title,
            content=error_msg,
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
    
    # Dados da revolução solar
    solar_return_ascendant: str
    solar_return_sun_house: int
    solar_return_moon_sign: str
    solar_return_moon_house: int
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
def get_solar_return_interpretation(
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
        
        # Verificar se o Groq está disponível
        has_groq = rag_service.groq_client is not None
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
        
        # Construir dados do cliente para o prompt
        client_data = f"""Signo Solar Natal: {request.natal_sun_sign}
Ascendente da Revolução Solar (RS): {request.solar_return_ascendant}
Casa onde cai o Sol na RS: Casa {request.solar_return_sun_house}
Lua na RS (Signo e Casa): {request.solar_return_moon_sign} na Casa {request.solar_return_moon_house}"""
        
        if request.solar_return_venus_sign:
            client_data += f"\nVênus na RS: {request.solar_return_venus_sign}{f' na Casa {request.solar_return_venus_house}' if request.solar_return_venus_house else ''}"
        
        if request.solar_return_mars_sign:
            client_data += f"\nMarte na RS: {request.solar_return_mars_sign}{f' na Casa {request.solar_return_mars_house}' if request.solar_return_mars_house else ''}"
        
        if request.solar_return_jupiter_sign:
            client_data += f"\nJúpiter na RS: {request.solar_return_jupiter_sign}{f' na Casa {request.solar_return_jupiter_house}' if request.solar_return_jupiter_house else ''}"
        
        if request.solar_return_midheaven:
            client_data += f"\nMeio do Céu da RS: {request.solar_return_midheaven}"
        
        if request.solar_return_saturn_sign:
            client_data += f"\nSaturno na RS: {request.solar_return_saturn_sign}"
        
        # Prompt baseado no fornecido pelo usuário
        if lang == 'pt':
            system_prompt = """Você é um Astrólogo Experiente, com uma abordagem humanista, psicológica e evolutiva. Sua comunicação é clara, didática, empática e profundamente inspiradora. Você evita o fatalismo; seu foco é o livre-arbítrio e como a pessoa pode aproveitar as energias disponíveis para crescer."""
            
            user_prompt = f"""Tarefa: Realizar a interpretação detalhada de um Mapa de Revolução Solar (Retorno Solar) para o período de um ano.

Dados do Cliente:
{client_data}

⚠️ REGRAS CRÍTICAS DE ESTRUTURA E CONTINUIDADE:
- Cada tópico deve contar uma parte ÚNICA e COMPLEMENTAR da história do ano
- NÃO repita informações já mencionadas em tópicos anteriores
- Cada tópico deve ADICIONAR novas informações, não repetir
- Os 8 tópicos devem formar uma NARRATIVA CONTÍNUA e COESIVA
- Se um tópico menciona algo, os próximos devem COMPLEMENTAR, não REPETIR
- Evite frases genéricas que possam se aplicar a qualquer tópico
- Cada seção deve ter seu próprio "território" temático bem definido

Estrutura da Leitura (Siga rigorosamente estes tópicos, SEM REPETIÇÕES):

Use formatação com números e bullets, SEM asteriscos para títulos. Formate assim:

1. A "Vibe" do Ano (O Ascendente Anual)
   FOCUS: A energia geral e a "personalidade" do ano
   - Explique didaticamente o que é o Ascendente da Revolução Solar (apenas aqui, não repita depois).
   - Interprete a energia deste signo como a "ferramenta" ou "armadura" que a pessoa usará este ano.
   - Como esse signo ajuda a pessoa a vencer obstáculos?
   - NÃO mencione casas, planetas específicos ou áreas de vida aqui - apenas o Ascendente e sua energia geral.

2. O Foco da Consciência (O Sol nas Casas)
   FOCUS: A área específica de realização e brilho pessoal
   - Analise APENAS a Casa onde o Sol está posicionado (Casa {request.solar_return_sun_house}).
   - Explique que esta é a área da vida onde ela brilhará e colocará sua energia vital.
   - Dê exemplos práticos ESPECÍFICOS do que fazer nesta área.
   - NÃO repita informações sobre o Ascendente ou outros planetas aqui.

3. O Mundo Emocional e a Família (A Lua)
   FOCUS: Necessidades emocionais, família e nutrição interior
   - Analise APENAS a Lua (signo {request.solar_return_moon_sign} e casa {request.solar_return_moon_house}).
   - Onde a pessoa buscará nutrição emocional? (específico para esta Lua)
   - Aborde questões familiares e o lar relacionadas a esta posição lunar.
   - Dica Positiva: Como cuidar do coração neste ciclo? (baseado na Lua, não genérico)
   - NÃO repita informações sobre o Sol ou outras áreas já mencionadas.

4. Amor, Relacionamentos e Vida Social (Vênus)
   FOCUS: Relacionamentos, valores afetivos e harmonia social
   - Interprete APENAS a posição de Vênus ({request.solar_return_venus_sign if request.solar_return_venus_sign else 'não disponível'}).
   - O que esperar do amor e das parcerias baseado nesta posição específica de Vênus.
   - Foque nos valores pessoais e na harmonia relacionada a Vênus.
   - NÃO repita informações sobre Lua, Sol ou outras áreas.

5. Trabalho, Dinheiro e Carreira (Marte, Júpiter e Meio do Céu)
   FOCUS: Ação profissional, expansão material e vocação
   - Onde está a força de ação (Marte)? Onde está a sorte/expansão (Júpiter)?
   - Qual a meta de vida para este ano (Meio do Céu)?
   - Dê orientações ESPECÍFICAS para tomada de decisão profissional e financeira baseadas nestes planetas.
   - NÃO repita informações sobre outras áreas ou planetas já mencionados.

6. Saúde e Vitalidade
   FOCUS: Bem-estar físico, rotinas e cuidados com o corpo
   - Analise APENAS a Casa 6 e os planetas que estão nela (se houver).
   - Considere como o Ascendente influencia a vitalidade (conexão específica, não repetição).
   - Sugira práticas de bem-estar ESPECÍFICAS baseadas nos planetas na Casa 6.
   - Seja específico sobre áreas do corpo ou sistemas baseado nos planetas presentes.
   - NÃO repita informações sobre outras casas ou áreas já mencionadas.

7. Os Desafios como Oportunidades (Saturnos e Tensões)
   FOCUS: Transformação de dificuldades em crescimento
   - Identifique o maior desafio do ano baseado em Saturno e aspectos tensos.
   - Reframe-o como uma oportunidade de amadurecimento ESPECÍFICA.
   - Use linguagem encorajadora: "Onde Saturno toca, nós construímos mestria".
   - NÃO repita desafios já mencionados em outros tópicos.

8. Síntese Inspiradora
   FOCUS: Integração final e mensagem de esperança
   - Crie um "Mantra do Ano" curto que sintetize os temas principais (sem repetir tudo).
   - Resuma as 3 grandes bênçãos que estão chegando (seja específico, não genérico).
   - Termine com uma mensagem de esperança e empoderamento que integre os temas principais.
   - NÃO repita detalhes já mencionados - apenas sintetize e inspire.

Estilo de Escrita e Formatação:
- Use números (1., 2., 3., etc.) para os títulos dos 8 tópicos principais, SEM asteriscos.
- Use bullets (- ou •) para listar pontos dentro de cada tópico quando apropriado.
- Use metáforas para facilitar o entendimento.
- Divida em parágrafos curtos.
- Cada tópico deve ter 2-4 parágrafos bem desenvolvidos.
- Garanta que cada parágrafo adicione informação nova, não repetida.
- NÃO use asteriscos (**) para títulos - use apenas números.
- NÃO use formatações como "A pessoa pode esperar:" seguido de listas - integre as informações em parágrafos narrativos.
- NÃO repita o mesmo texto ou ideias em diferentes tópicos.
- Formate os títulos assim: "1. Título do Tópico" (sem asteriscos, sem negrito)."""
        else:
            system_prompt = """You are an Experienced Astrologer, with a humanistic, psychological and evolutionary approach. Your communication is clear, didactic, empathetic and deeply inspiring. You avoid fatalism; your focus is free will and how the person can take advantage of available energies to grow."""
            
            user_prompt = f"""Task: Perform a detailed interpretation of a Solar Return Chart for a one-year period.

Client Data:
{client_data}

⚠️ CRITICAL STRUCTURE AND CONTINUITY RULES:
- Each topic must tell a UNIQUE and COMPLEMENTARY part of the year's story
- DO NOT repeat information already mentioned in previous topics
- Each topic must ADD new information, not repeat
- The 8 topics must form a CONTINUOUS and COHESIVE narrative
- If a topic mentions something, the next ones must COMPLEMENT, not REPEAT
- Avoid generic phrases that could apply to any topic
- Each section must have its own well-defined thematic "territory"

Reading Structure (Follow these topics strictly, WITHOUT REPETITIONS):

Use formatting with numbers and bullets, WITHOUT asterisks for titles. Format like this:

1. The Year's "Vibe" (The Annual Ascendant)
   FOCUS: The general energy and "personality" of the year
   - Explain what the Solar Return Ascendant is (only here, don't repeat later).
   - Interpret this sign's energy as the "tool" or "armor" the person will use this year.
   - How does this sign help the person overcome obstacles?
   - DO NOT mention houses, specific planets or life areas here - only the Ascendant and its general energy.

2. The Focus of Consciousness (The Sun in Houses)
   FOCUS: The specific area of fulfillment and personal shine
   - Analyze ONLY the House where the Sun is positioned (House {request.solar_return_sun_house}).
   - Explain that this is the area of life where they will shine and place their vital energy.
   - Give SPECIFIC practical examples of what to do in this area.
   - DO NOT repeat information about the Ascendant or other planets here.

3. The Emotional World and Family (The Moon)
   FOCUS: Emotional needs, family and inner nourishment
   - Analyze ONLY the Moon (sign {request.solar_return_moon_sign} and house {request.solar_return_moon_house}).
   - Where will the person seek emotional nourishment? (specific to this Moon)
   - Address family and home issues related to this lunar position.
   - Positive Tip: How to take care of the heart in this cycle? (based on the Moon, not generic)
   - DO NOT repeat information about the Sun or other areas already mentioned.

4. Love, Relationships and Social Life (Venus)
   FOCUS: Relationships, emotional values and social harmony
   - Interpret ONLY Venus's position ({request.solar_return_venus_sign if request.solar_return_venus_sign else 'not available'}).
   - What to expect from love and partnerships based on this specific Venus position.
   - Focus on personal values and harmony related to Venus.
   - DO NOT repeat information about Moon, Sun or other areas.

5. Work, Money and Career (Mars, Jupiter and Midheaven)
   FOCUS: Professional action, material expansion and vocation
   - Where is the force of action (Mars)? Where is luck/expansion (Jupiter)?
   - What is the life goal for this year (Midheaven)?
   - Give SPECIFIC guidance for professional and financial decision making based on these planets.
   - DO NOT repeat information about other areas or planets already mentioned.

6. Health and Vitality
   FOCUS: Physical well-being, routines and body care
   - Analyze ONLY House 6 and the planets in it (if any).
   - Consider how the Ascendant influences vitality (specific connection, not repetition).
   - Suggest SPECIFIC wellness practices based on planets in House 6.
   - Be specific about body areas or systems based on present planets.
   - DO NOT repeat information about other houses or areas already mentioned.

7. Challenges as Opportunities (Saturn and Tensions)
   FOCUS: Transforming difficulties into growth
   - Identify the year's greatest challenge based on Saturn and tense aspects.
   - Reframe it as a SPECIFIC opportunity for maturation.
   - Use encouraging language: "Where Saturn touches, we build mastery".
   - DO NOT repeat challenges already mentioned in other topics.

8. Inspiring Synthesis
   FOCUS: Final integration and message of hope
   - Create a short "Year's Mantra" that synthesizes the main themes (without repeating everything).
   - Summarize the 3 great blessings that are coming (be specific, not generic).
   - End with a message of hope and empowerment that integrates the main themes.
   - DO NOT repeat details already mentioned - only synthesize and inspire.

Writing Style and Formatting:
- Use numbers (1., 2., 3., etc.) for the 8 main topic titles, WITHOUT asterisks.
- Use bullets (- or •) to list points within each topic when appropriate.
- Use metaphors to facilitate understanding.
- Divide into short paragraphs.
- Each topic should have 2-4 well-developed paragraphs.
- Ensure each paragraph adds new, non-repeated information.
- DO NOT use asterisks (**) for titles - use only numbers.
- DO NOT use formats like "The person can expect:" followed by lists - integrate information into narrative paragraphs.
- DO NOT repeat the same text or ideas in different topics.
- Format titles like this: "1. Topic Title" (no asterisks, no bold)."""
        
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
        if rag_service.groq_client:
            try:
                print(f"[SOLAR RETURN] Tentando gerar interpretação com Groq...")
                context_snippet = context_text[:3000] if context_text else "Informações gerais sobre revolução solar."
                
                full_user_prompt = f"""{user_prompt}

---

CONHECIMENTO ASTROLÓGICO DE REFERÊNCIA:
{context_snippet}"""
                
                print(f"[SOLAR RETURN] Prompt length: {len(full_user_prompt)} chars")
                print(f"[SOLAR RETURN] System prompt length: {len(system_prompt)} chars")
                print(f"[SOLAR RETURN] Model: llama-3.1-70b-versatile")
                
                # Tentar chamar Groq com modelo principal
                models_to_try = [
                    "llama-3.1-70b-versatile",
                    "llama-3.1-8b-instant",
                    "mixtral-8x7b-32768"
                ]
                
                interpretation_text = None
                last_error = None
                
                for model_name in models_to_try:
                    try:
                        print(f"[SOLAR RETURN] Tentando modelo: {model_name}")
                        chat_completion = rag_service.groq_client.chat.completions.create(
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
                        
                        # Limpeza: remover duplicações de texto comum
                        # Remover duplicações de padrões como "A pessoa pode esperar:" e listas repetidas
                        import re
                        
                        # Padrão para detectar e remover duplicações de "A pessoa pode esperar:" e similares
                        patterns_to_deduplicate = [
                            r'A pessoa pode esperar:.*?(?=\n\n|\*\*|$)',
                            r'The person can expect:.*?(?=\n\n|\*\*|$)',
                            r'Oportunidades de crescimento e expansão.*?(?=\n\n|\*\*|$)',
                            r'Opportunities for growth and expansion.*?(?=\n\n|\*\*|$)',
                        ]
                        
                        # Encontrar todas as ocorrências
                        found_patterns = []
                        for pattern in patterns_to_deduplicate:
                            matches = list(re.finditer(pattern, interpretation_text, re.IGNORECASE | re.DOTALL))
                            if len(matches) > 1:
                                # Manter apenas a primeira ocorrência, remover as demais
                                for match in matches[1:]:
                                    interpretation_text = interpretation_text[:match.start()] + interpretation_text[match.end():]
                        
                        # Remover duplicações de parágrafos inteiros (mesmo texto aparecendo 2+ vezes)
                        paragraphs = interpretation_text.split('\n\n')
                        seen_paragraphs = set()
                        unique_paragraphs = []
                        for para in paragraphs:
                            para_clean = para.strip()
                            # Normalizar para comparação (remover espaços extras, case insensitive)
                            para_key = re.sub(r'\s+', ' ', para_clean.lower())
                            # Ignorar parágrafos muito curtos (provavelmente títulos ou separadores)
                            if len(para_key) > 50 and para_key not in seen_paragraphs:
                                seen_paragraphs.add(para_key)
                                unique_paragraphs.append(para)
                            elif len(para_key) <= 50:
                                # Manter parágrafos curtos (títulos, etc)
                                unique_paragraphs.append(para)
                        
                        interpretation_text = '\n\n'.join(unique_paragraphs)
                        
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
                    fallback_result = rag_service.get_interpretation(
                        custom_query=fallback_query,
                        use_groq=True
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
                        
                        return InterpretationResponse(
                            interpretation=fallback_result['interpretation'],
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

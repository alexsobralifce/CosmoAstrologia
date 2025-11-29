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
            top_k=12  # Aumentar top_k no fallback também
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
    """Retorna o prompt mestre para geração do Mapa Astral baseado na nova estrutura otimizada."""
    if language == 'en':
        return """**Role:** You are a Senior Astrologer and Strategic Consultant. Your specialty is Precision Astrological Synthesis, integrating Stephen Arroyo's energetic vision, the rigorous technique of Sakoian & Acker (aspects and orbs) and the practical application of Kris Brandt Riske's Houses.

**Objective:** Analyze the Natal Chart below to provide Strategic Life Direction and support Decision Making. I don't want generic descriptions; I want the mechanics of how this person functions.

**Birth Data:** [INSERT DATA HERE]

**ANALYSIS PROTOCOL (THE "ALGORITHM"):**

Follow these reasoning steps before generating the final response:

**Temperament Calculation (Arroyo's Filter):** Evaluate the balance of the 4 Elements (Fire, Earth, Air, Water). Identify the dominant element (the fuel) and the absent/weak element (the blind spot). Use this to nuance all guidance.

**Hierarchy of Strength:** Give maximum priority in interpretation to:
- The Ascendant Ruler (The Captain of Life).
- Planets in Angular Houses (1, 4, 7, 10).
- Exact/Partile Aspects (orb less than 2°). These are the "screams" of the chart.

**Decision Mechanics:** Analyze Mercury (how they think) and Mars (how they act) to explain how this person makes decisions and where they usually err.

**GOLDEN RULES (GUIDELINES):**

**Synthesis, not List:** Never list "Sun in Aries, Moon in Taurus...". Say: "Your Arian will to initiate is slowed by a Taurean need for security..."

**Precision:** If there is a tense aspect (Square/Opposition) involving personal planets, treat this as a "Critical Attention Point".

**Language:** Therapeutic, direct, empowering. Use metaphors to explain complex energies.

**No repetitions:** Each section must reveal a new layer of the individual.

**House Treatment:** If the time is not exact or the house is not provided, focus on the psychology of planets in signs and ignore life areas (Houses)."""
    else:
        return """**Role:** Você é um Astrólogo Sênior e Consultor Estratégico. Sua especialidade é a Síntese Astrológica de Precisão, integrando a visão energética de Stephen Arroyo, a técnica rigorosa de Sakoian & Acker (aspectos e orbes) e a aplicação prática das Casas de Kris Brandt Riske.

**Objetivo:** Analisar o Mapa Natal abaixo para fornecer Direcionamento Estratégico de Vida e apoiar a Tomada de Decisões. Não quero descrições genéricas; quero a mecânica de funcionamento desta pessoa.

**Dados do Nascimento:** [INSERIR DADOS AQUI]

**PROTOCOLO DE ANÁLISE (O "ALGORITMO"):**

Siga estas etapas de raciocínio antes de gerar a resposta final:

**Cálculo do Temperamento (Filtro de Arroyo):** Avalie o balanço dos 4 Elementos (Fogo, Terra, Ar, Água). Identifique o elemento dominante (o combustível) e o elemento ausente/fraco (o ponto cego). Use isso para matizar todas as orientações.

**Hierarquia de Força:** Dê prioridade máxima na interpretação para:
- O Regente do Ascendente (O Capitão da Vida).
- Planetas em Casas Angulares (1, 4, 7, 10).
- Aspectos Partis/Exatos (orbe menor que 2°). Estes são os "gritos" do mapa.

**Mecânica de Decisão:** Analise Mercúrio (como pensa) e Marte (como age) para explicar como esta pessoa toma decisões e onde ela costuma errar.

**REGRAS DE OURO (GUIDELINES):**

**Síntese, não Lista:** Nunca liste "Sol em áries, Lua em touro...". Diga: "Sua vontade ariana de iniciar é freada por uma necessidade taurina de segurança..."

**Precisão:** Se houver um aspecto tenso (Quadratura/Oposição) envolvendo planetas pessoais, trate isso como um "Ponto de Atenção Crítica".

**Linguagem:** Terapêutica, direta, empoderadora. Use metáforas para explicar energias complexas.

**Sem repetições:** Cada seção deve revelar uma nova camada do indivíduo.

**Tratamento de Casas:** Se a hora não for exata ou a casa não for informada, foque na psicologia dos planetas nos signos e ignore as áreas da vida (Casas)."""


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
        title = "A Engenharia da Sua Energia (Temperamento)" if lang == 'pt' else "The Engineering of Your Energy (Temperament)"
        if lang == 'pt':
            prompt = f"""{full_context}

**1. A ENGENHARIA DA SUA ENERGIA (TEMPERAMENTO)**

Comece sua resposta com: "Análise do Mapa Astral de {request.name}"

Em seguida, inclua uma seção intitulada: "Cálculo do Temperamento (Filtro de Arroyo)"

Explique como o balanço de elementos afeta a vitalidade e a psicologia básica.

**Análise Obrigatória:**
- Avalie o balanço dos 4 Elementos (Fogo, Terra, Ar, Água)
- Identifique o elemento dominante (o combustível) e o elemento ausente/fraco (o ponto cego)
- Analise as modalidades (Cardeal, Fixo, Mutável)

**Insight Prático:** Como lidar com a falta ou excesso de um elemento no dia a dia.

**O Regente do Ascendente:** Identifique o planeta regente do Ascendente {request.ascendant} e analise sua condição (Signo, Casa, Aspectos). Onde ele está e como ele direciona o foco principal da vida. Ele é um aliado ou um desafio para o nativo?

IMPORTANTE:
- SEMPRE comece com "Análise do Mapa Astral de {request.name}"
- SEMPRE inclua a seção "Cálculo do Temperamento (Filtro de Arroyo)" com conteúdo detalhado
- Use "conselhos" (português), NUNCA "consejo" (espanhol)
- Não repita informações já mencionadas em outras seções
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação - se a casa não estiver disponível, OMITA completamente a menção à casa
- Foque no temperamento como motor de motivação e ação
- Analise o regente do mapa com profundidade técnica (Dignidades, Regências)
- Dê conselhos práticos e acionáveis para equilíbrio energético"""
        else:
            prompt = f"""{full_context}

**1. THE ENGINEERING OF YOUR ENERGY (TEMPERAMENT)**

Explain how the balance of elements affects vitality and basic psychology.

**Mandatory Analysis:**
- Evaluate the balance of the 4 Elements (Fire, Earth, Air, Water)
- Identify the dominant element (the fuel) and the absent/weak element (the blind spot)
- Analyze the modalities (Cardinal, Fixed, Mutable)

**Practical Insight:** How to deal with the lack or excess of an element in daily life.

**The Ascendant Ruler:** Identify the planet ruling the Ascendant {request.ascendant} and analyze its condition (Sign, House, Aspects). Where is it and how does it direct the main focus of life. Is it an ally or a challenge for the native?

IMPORTANT:
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

IMPORTANTE:
- Não repita informações já mencionadas em outras seções
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação - use apenas os dados fornecidos ou omita a informação
- Analise Vênus com técnica de Dignidades/Debilidades (Astrologia Clássica)
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

IMPORTANT:
- Do not repeat information already mentioned in other sections
- NEVER write "House not provided", "in House not provided" or any variation - use only the provided data or omit the information
- Analyze Venus with Dignities/Debilities technique (Classical Astrology)
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

IMPORTANTE:
- Use "conselhos" (português), NUNCA "consejo" (espanhol). Use sempre português brasileiro.
- NÃO repita informações já detalhadas nas seções anteriores
- NUNCA escreva "Casa não informada", "na Casa não informada" ou qualquer variação
- Faça uma síntese integradora que conecte TODOS os elementos já analisados
- Identifique pontos técnicos específicos (Stelliums, Dignidades, Aspectos exatos)
- Ofereça uma diretriz estratégica e empoderadora
- Foque em tomada de decisão prática e evolução pessoal"""
        else:
            prompt = f"""{full_context}

**FINAL SYNTHESIS AND STRATEGIC GUIDANCE**

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
{context_snippet}

IMPORTANTE FINAL: 
- Use SEMPRE português brasileiro
- Use "conselhos", NUNCA "consejo"
- Garanta que TODAS as seções tenham conteúdo completo e detalhado
- Não deixe títulos sem conteúdo"""
                
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
                
                # Aplicar filtro de deduplicação
                content = _deduplicate_text(content)
                
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
        
        # Construir dados do mapa natal (base)
        natal_data_summary = f"""Signo Solar Natal: {request.natal_sun_sign}"""
        if request.natal_ascendant:
            natal_data_summary += f"\nAscendente Natal: {request.natal_ascendant}"
        # Nota: Aspectos tensos principais seriam calculados se tivéssemos mais dados do mapa natal
        # Por enquanto, focamos no que temos disponível
        
        # Construir dados da revolução solar
        solar_return_data = f"""Ascendente da Revolução Solar (RS): {request.solar_return_ascendant}
Casa onde cai o Sol na RS: Casa {request.solar_return_sun_house}
Lua na RS (Signo e Casa): {request.solar_return_moon_sign} na Casa {request.solar_return_moon_house}"""
        
        if request.solar_return_venus_sign:
            solar_return_data += f"\nVênus na RS: {request.solar_return_venus_sign}{f' na Casa {request.solar_return_venus_house}' if request.solar_return_venus_house else ''}"
        
        if request.solar_return_mars_sign:
            solar_return_data += f"\nMarte na RS: {request.solar_return_mars_sign}{f' na Casa {request.solar_return_mars_house}' if request.solar_return_mars_house else ''}"
        
        if request.solar_return_jupiter_sign:
            solar_return_data += f"\nJúpiter na RS: {request.solar_return_jupiter_sign}{f' na Casa {request.solar_return_jupiter_house}' if request.solar_return_jupiter_house else ''}"
        
        if request.solar_return_midheaven:
            solar_return_data += f"\nMeio do Céu da RS: {request.solar_return_midheaven}"
        
        if request.solar_return_saturn_sign:
            solar_return_data += f"\nSaturno na RS: {request.solar_return_saturn_sign}"
        
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
   - Analise a Casa da RS onde o Sol está posicionado (Casa {request.solar_return_sun_house}). Esta é a "Missão do Ano".
   - Explique por que essa área drenará mais energia e onde a pessoa brilhará mais.
   - Dê uma estratégia de decisão: O que priorizar nesta área específica.
   - Restrição: NÃO repita informações sobre o temperamento do Ascendente.

3. O Clima Emocional (A Lua da RS)
   FOCUS EXCLUSIVO: Nutrição, instabilidade e vida doméstica.
   - Interprete o Signo e a Casa da Lua na RS ({request.solar_return_moon_sign} na Casa {request.solar_return_moon_house}).
   - Identifique a área onde a pessoa estará mais irracional ou flutuante (visão de Arroyo).
   - Indique onde ela encontrará refúgio emocional seguro.
   - Restrição: NÃO mencione metas profissionais ou financeiras aqui.

4. Relacionamentos e Valores (Vênus na RS)
   FOCUS EXCLUSIVO: Trocas afetivas, prazer e magnetismo social.
   - Interprete a posição de Vênus ({request.solar_return_venus_sign if request.solar_return_venus_sign else 'não disponível'}{f' na Casa {request.solar_return_venus_house}' if request.solar_return_venus_house else ''}) para definir o "sabor" das interações sociais.
   - O que a pessoa valorizará mais nas parcerias este ano? (Liberdade? Segurança? Status?).
   - Se Vênus estiver retrógrado, adicione um alerta sobre revisões afetivas.
   - Restrição: NÃO misture com as necessidades emocionais lunares (tópico 3).

5. Estratégia Profissional e Financeira (Marte, Júpiter e MC)
   FOCUS EXCLUSIVO: Ação, expansão, dinheiro e metas públicas.
   - Use Marte ({request.solar_return_mars_sign if request.solar_return_mars_sign else 'não disponível'}{f' na Casa {request.solar_return_mars_house}' if request.solar_return_mars_house else ''}) para indicar onde aplicar força e coragem.
   - Use Júpiter ({request.solar_return_jupiter_sign if request.solar_return_jupiter_sign else 'não disponível'}{f' na Casa {request.solar_return_jupiter_house}' if request.solar_return_jupiter_house else ''}) para indicar onde haverá sorte ou facilidade de expansão.
   - Analise o Meio do Céu da RS ({request.solar_return_midheaven if request.solar_return_midheaven else 'não disponível'}) para definir a meta pública do ano.
   - Restrição: Se Marte/Júpiter estiverem na Casa 6 ou 7, foque apenas no impacto deles na carreira/ação, não na saúde ou casamento.

6. Saúde e Rotina (Casa 6 da RS)
   FOCUS EXCLUSIVO: Manutenção do corpo e organização diária.
   - Analise o signo da cúspide da Casa 6 e planetas ali presentes.
   - Conecte a vitalidade física com a demanda energética do ano.
   - Sugira um hábito ou ajuste de rotina específico para este ciclo.
   - Restrição: Não fale de doenças graves (tema de Saturno/Casa 8), fale de manutenção e rotina.

7. O Grande Teste e a Dica de Mestre (Saturno e Repetições)
   FOCUS EXCLUSIVO: O maior desafio, a lição kármica e a maturação.
   - Localize Saturno na RS ({request.solar_return_saturn_sign if request.solar_return_saturn_sign else 'não disponível'}): Onde a vida vai pedir paciência, restrição e estrutura?
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

from app.api.interpretation.solar_return import SourceItem
from app.core.database import get_db
from app.models.database import BirthChart
from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Header
from fastapi import status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

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



@router.post("/numerology/interpretation", response_model=NumerologyInterpretationResponse)
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
        lang = request.language or 'pt'
        
        # Queries específicas para cada número do mapa
        queries = [
            # Caminho de Vida (mais importante)
            f"life path number {numerology_map['life_path']['number']} numerologia pitagórica significado missão pontos positivos negativos",
            f"caminho de vida {numerology_map['life_path']['number']} numerologia características forças fraquezas",
            f"number {numerology_map['life_path']['number']} numerology positive negative traits strengths weaknesses",
            
            # Número do Destino/Expressão
            f"expression destiny number {numerology_map['destiny']['number']} numerologia talentos habilidades",
            f"número expressão destino {numerology_map['destiny']['number']} numerologia pontos fortes desafios",
            f"destiny number {numerology_map['destiny']['number']} numerology talents abilities",
            
            # Número da Alma/Desejo do Coração
            f"soul desire heart number {numerology_map['soul']['number']} numerologia motivação desejos internos",
            f"número alma desejo coração {numerology_map['soul']['number']} numerologia motivações",
            f"soul number {numerology_map['soul']['number']} numerology inner desires motivations",
            
            # Número da Personalidade
            f"personality number {numerology_map['personality']['number']} numerologia como se apresenta mundo",
            f"número personalidade {numerology_map['personality']['number']} numerologia aparência externa",
            
            # Número do Aniversário
            f"birthday number {numerology_map['birthday']['number']} numerologia talentos especiais habilidades",
            f"número aniversário {numerology_map['birthday']['number']} numerologia dons naturais",
            
            # Número da Maturidade
            f"maturity number {numerology_map['maturity']['number']} numerologia segunda metade vida potencial",
            f"número maturidade {numerology_map['maturity']['number']} numerologia evolução futuro",
        ]
        
        # Adicionar queries para números mestres se aplicável
        if numerology_map['life_path']['is_master']:
            queries.append(f"master number {numerology_map['life_path']['number']} numerologia significado especial")
        if numerology_map['destiny']['is_master']:
            queries.append(f"master number {numerology_map['destiny']['number']} expression destiny")
        if numerology_map['soul']['is_master']:
            queries.append(f"master number {numerology_map['soul']['number']} soul heart desire")
        
        # Adicionar queries expandidas sobre tarot e numerologia para CADA número (forte ligação)
        # Caminho de Vida - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['life_path']['number']} arcano correspondente significado",
            f"arcano maior número {numerology_map['life_path']['number']} tarot numerologia",
            f"carta tarot número {numerology_map['life_path']['number']} numerologia pitagórica",
            f"tarot arcano {numerology_map['life_path']['number']} caminho de vida numerologia",
            f"numerologia tarot conexão número {numerology_map['life_path']['number']} interpretação",
            f"arcanos maiores tarot numerologia número {numerology_map['life_path']['number']} significado completo",
        ])
        
        # Número do Destino - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['destiny']['number']} arcano destino expressão",
            f"arcano maior número {numerology_map['destiny']['number']} tarot numerologia destino",
            f"carta tarot número {numerology_map['destiny']['number']} numerologia expressão",
            f"tarot arcano {numerology_map['destiny']['number']} destino numerologia",
            f"numerologia tarot conexão número {numerology_map['destiny']['number']} talentos",
        ])
        
        # Número da Alma - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['soul']['number']} arcano alma desejo coração",
            f"arcano maior número {numerology_map['soul']['number']} tarot numerologia alma",
            f"carta tarot número {numerology_map['soul']['number']} numerologia desejo coração",
            f"tarot arcano {numerology_map['soul']['number']} alma numerologia motivações",
            f"numerologia tarot conexão número {numerology_map['soul']['number']} desejos internos",
        ])
        
        # Número da Personalidade - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['personality']['number']} arcano personalidade",
            f"arcano maior número {numerology_map['personality']['number']} tarot numerologia personalidade",
            f"carta tarot número {numerology_map['personality']['number']} numerologia aparência",
            f"tarot arcano {numerology_map['personality']['number']} personalidade numerologia",
        ])
        
        # Número do Aniversário - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['birthday']['number']} arcano aniversário",
            f"arcano maior número {numerology_map['birthday']['number']} tarot numerologia aniversário",
            f"carta tarot número {numerology_map['birthday']['number']} numerologia dia nascimento",
            f"tarot arcano {numerology_map['birthday']['number']} aniversário numerologia talentos",
        ])
        
        # Número da Maturidade - Tarot
        queries.extend([
            f"tarot numerologia número {numerology_map['maturity']['number']} arcano maturidade",
            f"arcano maior número {numerology_map['maturity']['number']} tarot numerologia maturidade",
            f"carta tarot número {numerology_map['maturity']['number']} numerologia segunda metade vida",
            f"tarot arcano {numerology_map['maturity']['number']} maturidade numerologia futuro",
        ])
        
        # Buscar contexto do RAG com mais resultados (aumentado para incluir mais contexto de tarot)
        context_documents = []
        if rag_service:
            for query in queries:
                try:
                    results = rag_service.search(query, top_k=5, expand_query=True, category='numerology')
                    context_documents.extend(results)
                except Exception as e:
                    print(f"[WARNING] Erro ao buscar query '{query}': {e}")
        
        # Remover duplicatas e ordenar por relevância (aumentado limite para mais contexto de tarot)
        seen_texts = set()
        unique_docs = []
        for doc in sorted(context_documents, key=lambda x: x.get('score', 0), reverse=True):
            doc_text = doc.get('text', '').strip()
            if doc_text and doc_text not in seen_texts and len(doc_text) > 50:
                seen_texts.add(doc_text)
                unique_docs.append(doc)
                if len(unique_docs) >= 30:  # Aumentado de 20 para 30 para incluir mais contexto de tarot
                    break
        
        context_text = "\n\n".join([
            f"[Fonte: {doc.get('source', 'unknown')} - Página {doc.get('page', 1)}]\n{doc.get('text', '')}"
            for doc in unique_docs[:20]  # Aumentado de 15 para 20 para incluir mais contexto de tarot
            if doc.get('text')
        ])
        
        # Preparar informações detalhadas do mapa
        master_info = []
        if numerology_map['life_path']['is_master']:
            master_info.append(f"Caminho de Vida {numerology_map['life_path']['number']} é um Número Mestre")
        if numerology_map['destiny']['is_master']:
            master_info.append(f"Destino {numerology_map['destiny']['number']} é um Número Mestre")
        if numerology_map['soul']['is_master']:
            master_info.append(f"Alma {numerology_map['soul']['number']} é um Número Mestre")
        
        master_note = "\n".join(master_info) if master_info else "Nenhum número mestre presente."
        
        # Gerar interpretação com IA - prompt muito mais detalhado e inspirador
        system_prompt = """Você é um Numerólogo Pitagórico experiente e inspirador, com profundo conhecimento da conexão entre Numerologia e Tarot. Sua missão é ajudar pessoas a compreenderem seus números e usarem essa sabedoria para viverem vidas mais plenas e realizadas.

CONHECIMENTO INTEGRADO - TAROT E NUMEROLOGIA:
- Numerologia e Tarot têm uma forte ligação histórica e simbólica que remonta séculos
- Cada número na numerologia (1-9 e números mestres) corresponde a um Arcano Maior do Tarot
- A integração Tarot-Numerologia é ESSENCIAL para uma interpretação completa e rica
- O Tarot oferece símbolos visuais e arquetípicos que facilitam o entendimento dos números
- Cada Arcano traz camadas adicionais de significado que enriquecem a interpretação numerológica

REGRAS OBRIGATÓRIAS PARA INTERPRETAÇÃO:
1. **PARA CADA NÚMERO DO MAPA NUMEROLÓGICO, VOCÊ DEVE:**
   - Identificar o Arcano do Tarot correspondente ao número
   - Incluir uma subseção dedicada ao Arcano em cada seção do número
   - Explicar o significado simbólico do Arcano
   - Mostrar como o Arcano complementa a interpretação numerológica
   - Conectar os ensinamentos do Arcano com os aspectos práticos do número
   - Usar a sabedoria do Arcano para oferecer orientações práticas

2. **ESTRUTURA OBRIGATÓRIA PARA CADA NÚMERO:**
   - Interpretação numerológica do número
   - **Subseção: "O Arcano do Tarot Correspondente"** (com nome do Arcano)
   - Significado simbólico do Arcano
   - Conexões entre número e Arcano
   - Como usar a sabedoria do Arcano na vida prática
   - Pontos positivos e desafios (integrados com sabedoria do Tarot)
   - Orientações práticas

DIRETRIZES IMPORTANTES:
- Use linguagem clara, inspiradora e acolhedora (o usuário é leigo)
- Sempre equilibre pontos positivos e desafios, mas foque em orientações práticas
- Forneça exemplos concretos e aplicáveis à vida real
- Seja encorajador e mostre como transformar desafios em oportunidades
- Use tom terapêutico e empoderador
- Quando mencionar conexões com Tarot, explique de forma simples e acessível
- NUNCA omita a interpretação do Tarot - ela é parte essencial da interpretação numerológica completa"""
        
        user_prompt = f"""MAPA NUMEROLÓGICO DE {numerology_map['full_name'].upper()}

📊 NÚMEROS PRINCIPAIS:

1. CAMINHO DE VIDA: {numerology_map['life_path']['number']} {"(Número Mestre)" if numerology_map['life_path']['is_master'] else ""}
   - Este é o número mais importante. Representa sua missão de vida, o caminho que você veio percorrer nesta encarnação.
   - Cálculo: Dia {numerology_map['life_path']['day']} + Mês {numerology_map['life_path']['month']} + Ano {numerology_map['life_path']['year']} = {numerology_map['life_path']['raw_total']} → {numerology_map['life_path']['number']}

2. NÚMERO DO DESTINO (Expressão): {numerology_map['destiny']['number']} {"(Número Mestre)" if numerology_map['destiny']['is_master'] else ""}
   - Revela seus talentos naturais, habilidades inatas e como você pode expressar seu potencial máximo.

3. NÚMERO DA ALMA (Desejo do Coração): {numerology_map['soul']['number']} {"(Número Mestre)" if numerology_map['soul']['is_master'] else ""}
   - Mostra suas motivações profundas, o que realmente move seu coração e o que você deseja no nível da alma.

4. NÚMERO DA PERSONALIDADE: {numerology_map['personality']['number']}
   - Indica como você se apresenta ao mundo, sua máscara social e como os outros te percebem inicialmente.

5. NÚMERO DO ANIVERSÁRIO: {numerology_map['birthday']['number']}
   - Revela talentos especiais e habilidades que você trouxe ao nascer neste dia específico.

6. NÚMERO DA MATURIDADE: {numerology_map['maturity']['number']}
   - Indica o potencial que você desenvolverá na segunda metade da vida, após os 35-40 anos.

📝 NOTAS ESPECIAIS:
{master_note}

📚 CONHECIMENTO NUMEROLÓGICO E TAROT DE REFERÊNCIA (RAG):
{context_text[:6000] if context_text else "Informações numerológicas básicas da tradição pitagórica e conexões com Tarot."}

NOTA CRÍTICA: O contexto RAG inclui informações detalhadas sobre Numerologia e também sobre a conexão entre Numerologia e Tarot. É OBRIGATÓRIO que você:
1. Identifique o Arcano do Tarot correspondente a CADA número do mapa numerológico
2. Inclua uma subseção sobre o Arcano em CADA seção do número correspondente
3. Explique como o Arcano complementa e enriquece a interpretação numerológica
4. Use as informações do contexto RAG sobre tarot para fornecer interpretações completas e detalhadas
5. Facilite o entendimento do usuário através das conexões simbólicas entre números e cartas do Tarot

---

INSTRUÇÕES PARA A INTERPRETAÇÃO:

Crie uma interpretação COMPLETA, DETALHADA e INSPIRADORA que inclua:

1. **INTRODUÇÃO ENCORAJADORA** (1 parágrafo)
   - Dê boas-vindas calorosas e explique que os números são ferramentas de autoconhecimento
   - Enfatize que não há números "bons" ou "ruins", apenas diferentes caminhos de evolução

2. **CAMINHO DE VIDA** (3-4 parágrafos)
   - Explique em detalhes o que significa ter Caminho de Vida {numerology_map['life_path']['number']}
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['life_path']['number']}**
     * Nome do Arcano correspondente
     * Significado simbólico do Arcano
     * Como o Arcano complementa e enriquece a interpretação numerológica
     * Conexões entre o número e a carta do Tarot
     * Como usar a sabedoria do Arcano para viver melhor o Caminho de Vida
   - Liste 4-5 pontos POSITIVOS (forças, talentos, características positivas)
   - Liste 2-3 DESAFIOS ou áreas de atenção (sem ser negativo, mas orientador)
   - Forneça 2-3 orientações práticas de como usar essas energias positivamente
   - Use exemplos concretos de como esse número se manifesta na vida

3. **NÚMERO DO DESTINO** (2-3 parágrafos)
   - Explique os talentos e habilidades naturais associados ao número {numerology_map['destiny']['number']}
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['destiny']['number']}**
     * Nome do Arcano correspondente
     * Como o Arcano revela os talentos e potencial de expressão
     * Conexões entre o número do Destino e a carta do Tarot
     * Como usar a sabedoria do Arcano para desenvolver os talentos
   - Mostre como desenvolver e expressar esses talentos
   - Oriente sobre carreiras, atividades e formas de expressão que alinham com esse número

4. **NÚMERO DA ALMA** (2-3 parágrafos)
   - Revele as motivações profundas e desejos do coração do número {numerology_map['soul']['number']}
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['soul']['number']}**
     * Nome do Arcano correspondente
     * Como o Arcano revela os desejos profundos da alma
     * Conexões entre o número da Alma e a carta do Tarot
     * Como usar a sabedoria do Arcano para honrar as necessidades internas
   - Explique como honrar essas necessidades internas
   - Oriente sobre como criar uma vida que satisfaça essas motivações profundas

5. **NÚMERO DA PERSONALIDADE** (2 parágrafos)
   - Explique como o número {numerology_map['personality']['number']} influencia a primeira impressão
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['personality']['number']}**
     * Nome do Arcano correspondente
     * Como o Arcano revela a máscara social e primeira impressão
     * Conexões entre o número da Personalidade e a carta do Tarot
     * Como usar a sabedoria do Arcano para apresentar-se ao mundo
   - Mostre como usar essa energia de forma positiva
   - Oriente sobre como equilibrar a personalidade externa com a alma interna

6. **NÚMERO DO ANIVERSÁRIO** (1-2 parágrafos)
   - Explique os talentos especiais do dia {numerology_map['birthday']['day']}
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['birthday']['number']}**
     * Nome do Arcano correspondente
     * Como o Arcano revela os dons especiais do dia de nascimento
     * Conexões entre o número do Aniversário e a carta do Tarot
     * Como usar a sabedoria do Arcano para desenvolver os talentos inatos
   - Mostre como desenvolver esses dons naturais

7. **NÚMERO DA MATURIDADE** (1-2 parágrafos)
   - Explique o potencial futuro do número {numerology_map['maturity']['number']}
   - **OBRIGATÓRIO: Inclua uma subseção sobre o Arcano do Tarot correspondente ao número {numerology_map['maturity']['number']}**
     * Nome do Arcano correspondente
     * Como o Arcano revela o potencial de evolução na segunda metade da vida
     * Conexões entre o número da Maturidade e a carta do Tarot
     * Como usar a sabedoria do Arcano para se preparar para a evolução futura
   - Oriente sobre como se preparar para essa evolução

8. **SÍNTESE E ORIENTAÇÃO FINAL** (1-2 parágrafos)
   - Integre todos os números em uma visão unificada
   - Forneça orientações práticas e inspiradoras para usar essa sabedoria
   - Encoraje o usuário a abraçar seu caminho único e desenvolver seus potenciais
   - Use linguagem empoderadora e esperançosa

ESTILO E TOM:
- Use linguagem clara, acessível e inspiradora
- Evite jargões técnicos complexos
- Seja específico e prático, não vago
- Equilibre realismo com otimismo
- Foque em crescimento, evolução e possibilidades
- Use exemplos da vida real quando possível
- Seja acolhedor e encorajador

IMPORTANTE: O usuário é leigo e busca orientação prática para viver melhor. Foque em como usar os números de forma positiva e construtiva."""
        
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



@router.post("/numerology/birth-grid-quantities", response_model=BirthGridQuantitiesResponse)
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

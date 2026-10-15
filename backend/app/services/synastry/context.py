"""Montagem do contexto de RAG para a sinastria entre dois signos.

Funções puras (o RAG entra por parâmetro), para testar sem banco nem índice.
"""
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Protocol

logger = logging.getLogger(__name__)

TOP_K_POR_CONSULTA = 8
TRECHOS_POR_CONTEXTO = 10
MIN_CHARS_CONTEXTO_BRUTO = 100
MIN_CHARS_CONTEXTO_VALIDADO = 200

_SIGN_QUERIES = {
    'pt': [
        "{s} características personalidade traços comportamento",
        "{s} emoções valores comunicação relacionamentos",
        "{s} signo elemento modalidade",
        "{s} planeta regente casa natural",
    ],
    'en': [
        "{s} characteristics personality traits behavior",
        "{s} emotions values communication relationships",
        "{s} sign element modality",
        "{s} ruling planet natural house",
    ],
}
_PAIR_QUERIES = {
    'pt': [
        "sinastria compatibilidade {a} com {b}",
        "relacionamento {a} {b} dinâmica",
        "{a} {b} pontos fortes desafios",
        "compatibilidade {a} {b} casal",
    ],
    'en': [
        "synastry compatibility {a} with {b}",
        "relationship {a} {b} dynamics",
        "{a} {b} strengths challenges",
        "compatibility {a} {b} couple",
    ],
}
_CLEAN_KEYWORDS = (
    'característica', 'personalidade', 'traço', 'comportamento',
    'emoção', 'valor', 'comunicação', 'relacionamento',
    'elemento', 'modalidade', 'rege', 'regente',
    'characteristic', 'personality', 'trait', 'behavior',
    'emotion', 'value', 'communication', 'relationship',
    'element', 'modality', 'rules', 'ruling',
)
_VALIDATE_KEYWORDS = (
    'característica', 'personalidade', 'traço', 'comportamento',
    'elemento', 'modalidade', 'rege', 'regente',
    'characteristic', 'personality', 'trait', 'behavior',
    'element', 'modality', 'rules', 'ruling',
)
_RULERSHIP_WORDS = ('rege', 'regente', 'rules', 'ruling')


class KnowledgeSearch(Protocol):
    def search(self, query: str, top_k: int, category: str, expand_query: bool) -> List[Dict[str, Any]]: ...


class InsufficientContextError(Exception):
    """A base de conhecimento não trouxe informação suficiente sobre os signos."""


@dataclass(frozen=True)
class SynastryContext:
    sign1_raw: str
    sign2_raw: str
    full_context: str


def _search(rag: KnowledgeSearch, query: str, top_k: int) -> List[Dict[str, Any]]:
    return rag.search(query=query, top_k=top_k, category='astrology', expand_query=True)


def _join(results: List[Dict[str, Any]], limit: int) -> str:
    return "\n\n".join(r.get('text', '') for r in results[:limit])


def search_unique(rag: KnowledgeSearch, queries: List[str]) -> List[Dict[str, Any]]:
    """Roda as consultas, remove trechos repetidos (pelos 200 primeiros caracteres) e ordena por score."""
    all_results: List[Dict[str, Any]] = []
    for query in queries:
        all_results.extend(_search(rag, query, TOP_K_POR_CONSULTA))
    seen, unique = set(), []
    for r in all_results:
        key = r.get('text', '')[:200]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    unique.sort(key=lambda x: x.get('score', 0), reverse=True)
    return unique


def _sign_context(rag: KnowledgeSearch, sign: str, lang: str) -> str:
    queries = [q.format(s=sign) for q in _SIGN_QUERIES[lang]]
    context = _join(search_unique(rag, queries), TRECHOS_POR_CONTEXTO)
    if not context or len(context) < MIN_CHARS_CONTEXTO_BRUTO:
        logger.warning("Pouco contexto sobre %s; tentando busca genérica", sign)
        alt = _search(rag, sign, 10)
        if alt:
            context = _join(alt, 5)
    return context


def clean_context(text: str, sign_name: str) -> str:
    """Mantém só linhas sobre características gerais ou que citam o signo."""
    if not text:
        return text
    kept = [
        line for line in text.split('\n')
        if any(k in line.lower() for k in _CLEAN_KEYWORDS) or sign_name.lower() in line.lower()
    ]
    return '\n'.join(kept) if kept else text


def validate_context(context_text: str, sign_name: str) -> tuple[str, List[str]]:
    """Remove linhas que parecem posicionamento planetário inventado; devolve (texto, avisos)."""
    if not context_text:
        return "", []
    warnings: List[str] = []
    name = sign_name.lower()
    validated: List[str] = []
    for line in context_text.split('\n'):
        low = line.lower()
        if any(p in low for p in (f'{name} em ', f'{name} na casa', f'in {name}', f'em {name} na')):
            if any(w in low for w in _RULERSHIP_WORDS):
                validated.append(line)
            else:
                warnings.append(f"Removida linha que pode conter posicionamento inventado: {line[:100]}")
                continue
        if any(k in low for k in _VALIDATE_KEYWORDS) or name in low:
            validated.append(line)
    text = '\n'.join(validated)
    if len(text) < 50:
        warnings.append(f"Contexto validado muito pequeno para {sign_name}")
    return text, warnings


def _render(sign1: str, sign2: str, c1: str, c2: str, pair: str) -> str:
    return f"""
INFORMAÇÕES SOBRE {sign1.upper()} (CARACTERÍSTICAS GERAIS DO SIGNO - VALIDADAS):
{c1}

---

INFORMAÇÕES SOBRE {sign2.upper()} (CARACTERÍSTICAS GERAIS DO SIGNO - VALIDADAS):
{c2}

---

INFORMAÇÕES SOBRE COMPATIBILIDADE ENTRE {sign1.upper()} E {sign2.upper()} (VALIDADAS):
{pair}
"""


def build_synastry_context(rag: KnowledgeSearch, sign1: str, sign2: str, lang: str) -> SynastryContext:
    """Busca, limpa e valida o contexto; levanta InsufficientContextError se for pouco demais."""
    lang = 'pt' if lang == 'pt' else 'en'
    c1 = _sign_context(rag, sign1, lang)
    c2 = _sign_context(rag, sign2, lang)
    pair_queries = [q.format(a=sign1, b=sign2) for q in _PAIR_QUERIES[lang]]
    pair = _join(search_unique(rag, pair_queries), TRECHOS_POR_CONTEXTO)

    v1, w1 = validate_context(clean_context(c1, sign1), sign1)
    v2, w2 = validate_context(clean_context(c2, sign2), sign2)
    vp, wp = validate_context(clean_context(pair, f"{sign1} {sign2}"), f"{sign1} {sign2}")
    for warning in w1 + w2 + wp:
        logger.warning("Validação de contexto: %s", warning)

    total = len(v1) + len(v2) + len(vp)
    if total < MIN_CHARS_CONTEXTO_VALIDADO:
        raise InsufficientContextError(
            f"Contexto validado insuficiente sobre {sign1} e {sign2}. "
            f"Informações encontradas: {total} caracteres (mínimo: {MIN_CHARS_CONTEXTO_VALIDADO})."
        )
    return SynastryContext(sign1_raw=c1, sign2_raw=c2, full_context=_render(sign1, sign2, v1, v2, vp))

"""Serviços da interpretação numerológica: consultas, contexto e prompts (sem RAG/LLM reais)."""
import pytest

from app.services.numerology_interpretation.context import describe_master_numbers, retrieve_context
from app.services.numerology_interpretation.prompts import SYSTEM_PROMPT, build_user_prompt
from app.services.numerology_interpretation.queries import build_rag_queries


def mapa(master=False):
    def item(n, m=False):
        return {'number': n, 'is_master': m}
    return {
        'full_name': 'Maria Teste',
        'life_path': {**item(11, master), 'day': 6, 'month': 1, 'year': 1, 'total': 11} if master else {**item(7), 'day': 6, 'month': 1, 'year': 1, 'total': 7},
        'destiny': item(22, master), 'soul': item(3), 'personality': item(5),
        'birthday': item(15), 'maturity': item(9),
    }


class FakeRag:
    def __init__(self):
        self.queries = []

    def search(self, query, top_k, expand_query, category):
        self.queries.append(query)
        return [{'text': 'x' * 60, 'score': 0.9, 'source': 'livro', 'page': 2}, {'text': 'curto', 'score': 0.8}]


@pytest.mark.unit
def test_consultas_cobrem_todos_os_numeros_e_o_tarot():
    queries = build_rag_queries(mapa())
    assert any('tarot' in q and '7' in q for q in queries)
    assert any('maturity' in q or 'maturidade' in q for q in queries)


@pytest.mark.unit
def test_numeros_mestres_acrescentam_consultas():
    assert len(build_rag_queries(mapa(master=True))) == len(build_rag_queries(mapa())) + 2


@pytest.mark.unit
def test_nota_de_numeros_mestres():
    assert describe_master_numbers(mapa()) == "Nenhum número mestre presente."
    assert "Número Mestre" in describe_master_numbers(mapa(master=True))


@pytest.mark.unit
def test_contexto_remove_repetidos_e_trechos_curtos():
    rag = FakeRag()
    texto, docs = retrieve_context(rag, ['a', 'b', 'c'])
    assert len(docs) == 1 and 'curto' not in texto
    assert texto.startswith('[Fonte: livro - Página 2]')
    assert rag.queries == ['a', 'b', 'c']


@pytest.mark.unit
def test_contexto_sem_rag_fica_vazio():
    assert retrieve_context(None, ['a']) == ("", [])


@pytest.mark.unit
def test_user_prompt_inclui_nome_nota_e_contexto():
    from datetime import datetime
    from app.services.numerology_calculator import NumerologyCalculator
    real = NumerologyCalculator().calculate_full_numerology_map(full_name='Maria Teste', birth_date=datetime(1990, 1, 15))
    prompt = build_user_prompt(real, "NOTA-MESTRE", "CONTEXTO-RAG")
    assert 'MARIA TESTE' in prompt and 'NOTA-MESTRE' in prompt and 'CONTEXTO-RAG' in prompt
    assert 'Tarot' in SYSTEM_PROMPT

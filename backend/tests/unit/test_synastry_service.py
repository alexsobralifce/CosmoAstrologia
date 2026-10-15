"""Testes dos serviços da sinastria (contexto de RAG e prompts), sem banco nem índice."""
import pytest

from app.services.synastry.context import (
    InsufficientContextError, build_synastry_context, clean_context, search_unique, validate_context,
)
from app.services.synastry.prompts import build_prompts


class FakeRag:
    def __init__(self, texts):
        self.texts = texts
        self.queries = []

    def search(self, query, top_k, category, expand_query):
        self.queries.append(query)
        return [{'text': t, 'score': 1 - i / 10} for i, t in enumerate(self.texts)]


@pytest.mark.unit
def test_search_unique_remove_repetidos_e_ordena_por_score():
    rag = FakeRag(['a', 'a', 'b'])
    resultado = search_unique(rag, ['q1', 'q2'])
    assert [r['text'] for r in resultado] == ['a', 'b']
    assert len(rag.queries) == 2


@pytest.mark.unit
def test_validate_remove_posicionamento_inventado_mas_mantem_regencia():
    texto = "Libra em Casa 7 domina tudo\nVênus rege Libra em equilíbrio\nLibra tem personalidade amável"
    validado, avisos = validate_context(texto, "Libra")
    assert "Casa 7" not in validado
    assert "Vênus rege Libra" in validado
    assert any("posicionamento inventado" in a for a in avisos)


@pytest.mark.unit
def test_clean_context_mantem_so_linhas_relevantes_e_nao_esvazia():
    assert clean_context("irrelevante\nLibra é ar", "Libra") == "Libra é ar"
    assert clean_context("nada a ver", "Libra") == "nada a ver"


@pytest.mark.unit
def test_contexto_insuficiente_levanta_erro_de_dominio():
    with pytest.raises(InsufficientContextError):
        build_synastry_context(FakeRag(['nada']), "Libra", "Escorpião", "pt")


@pytest.mark.unit
def test_contexto_suficiente_monta_blocos_validados():
    trecho = "Libra tem características de personalidade e comportamento " + "x" * 80
    ctx = build_synastry_context(FakeRag([trecho]), "Libra", "Escorpião", "pt")
    assert "LIBRA" in ctx.full_context and "ESCORPIÃO" in ctx.full_context
    assert "VALIDADAS" in ctx.full_context


@pytest.mark.unit
@pytest.mark.parametrize("lang,marcador", [("pt", "SINASTRIA / COMPATIBILIDADE"), ("en", "SYNASTRY / COMPATIBILITY"), ("fr", "SYNASTRY / COMPATIBILITY")])
def test_prompts_por_idioma(lang, marcador):
    system, user = build_prompts(lang, "Libra", "Leão", "CTX")
    assert marcador in user and "LIBRA" in user and "CTX" in user and system

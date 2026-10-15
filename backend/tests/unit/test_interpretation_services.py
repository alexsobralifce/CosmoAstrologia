"""Etapas extraídas dos handlers de revolução solar e mapa completo."""
from types import SimpleNamespace

import pytest

from app.services.birth_chart_section import build_full_user_prompt, resolve_coordinates
from app.services.solar_return_interpretation import build_rag_queries, retrieve_context


def pedido(place="", lat=None, lon=None):
    return SimpleNamespace(birthPlace=place, latitude=lat, longitude=lon)


@pytest.mark.unit
def test_coordenadas_do_cliente_tem_prioridade():
    assert resolve_coordinates(pedido("Sobral", -1.0, -2.0)) == (-1.0, -2.0)


@pytest.mark.unit
def test_coordenadas_por_nome_de_cidade_conhecida():
    assert resolve_coordinates(pedido("Sobral, CE, Brasil")) == (-3.6883, -40.3497)


@pytest.mark.unit
def test_coordenadas_desconhecidas_caem_em_sao_paulo():
    assert resolve_coordinates(pedido("Lugar Nenhum")) == (-23.5505, -46.6333)


@pytest.mark.unit
def test_prompt_do_usuario_limita_o_contexto_e_tem_valor_padrao():
    longo = build_full_user_prompt("x" * 5000, "SECAO")
    assert longo.startswith("SECAO") and longo.count("x") == 3000
    assert "Informações astrológicas gerais." in build_full_user_prompt("", "SECAO")


@pytest.mark.unit
def test_revolucao_solar_consultas_e_contexto_sem_rag():
    req = SimpleNamespace(target_year=2026, language='pt', birth_date=None)
    queries = build_rag_queries(req, "Leão", 3, "Touro", 1)
    assert queries and all(isinstance(q, str) for q in queries)
    texto, unicos = retrieve_context(queries, None)
    assert texto == "" and unicos == []

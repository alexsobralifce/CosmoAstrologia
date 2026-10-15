"""
Testes da API de interpretação.

Os endpoints antigos de RAG (/api/interpretation, /status, /search) saíram do backend
(o RAG virou serviço à parte); estes testes cobrem o contrato atual do pacote.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient

# Rotas que chamam LLM: exigem usuário autenticado (custo e abuso).
ROTAS_LLM = [
    ("post", "/api/interpretation"),
    ("post", "/api/interpretation/aspect"),
    ("post", "/api/interpretation/daily-advice"),
    ("post", "/api/interpretation/planet"),
    ("post", "/api/interpretation/chart-ruler"),
    ("post", "/api/interpretation/complete-chart"),
    ("post", "/api/solar-return/interpretation"),
    ("post", "/api/numerology/interpretation"),
    ("post", "/api/numerology/birth-grid-quantities"),
    ("post", "/api/full-birth-chart/section"),
    ("post", "/api/synastry/interpretation"),
]


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


class TestInterpretationPackage:
    @pytest.mark.api
    @pytest.mark.unit
    def test_api_imports_without_syntax_errors(self):
        from app.api import interpretation
        assert interpretation.router is not None

    @pytest.mark.api
    @pytest.mark.unit
    @pytest.mark.parametrize("metodo,caminho", ROTAS_LLM)
    def test_rotas_llm_estao_registradas(self, client, metodo, caminho):
        from app.main import app
        registradas = {(m.lower(), r.path) for r in app.routes if hasattr(r, "methods") for m in r.methods}
        assert (metodo, caminho) in registradas


class TestAutenticacaoObrigatoria:
    @pytest.mark.api
    @pytest.mark.security
    @pytest.mark.unit
    @pytest.mark.parametrize("metodo,caminho", ROTAS_LLM)
    def test_rotas_llm_sem_token_retornam_401(self, client, metodo, caminho):
        resposta = getattr(client, metodo)(caminho, json={})
        assert resposta.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.api
    @pytest.mark.security
    @pytest.mark.unit
    def test_token_invalido_retorna_401(self, client):
        resposta = client.post(
            "/api/interpretation/planet", json={}, headers={"Authorization": "Bearer invalido"}
        )
        assert resposta.status_code == status.HTTP_401_UNAUTHORIZED


class FakeRag:
    groq_client = None

    def get_interpretation(self, **kwargs):
        return {
            'interpretation': 'Texto do RAG ' * 10,
            'sources': [{'source': 'livro', 'page': 3, 'score': 0.9}],
            'query_used': kwargs.get('custom_query') or 'q',
            'generated_by': 'rag_only',
        }

    def search(self, *args, **kwargs):
        return []


@pytest.fixture
def client_autenticado(monkeypatch):
    from app.api.dependencies import require_user
    from app.main import app

    app.dependency_overrides[require_user] = lambda: type('U', (), {'id': 999})()
    monkeypatch.setattr('app.api.interpretation.rag_queries.get_rag_service', lambda: FakeRag())
    yield TestClient(app)
    app.dependency_overrides.pop(require_user, None)


class TestRotasRecuperadas:
    @pytest.mark.api
    @pytest.mark.unit
    def test_interpretacao_generica(self, client_autenticado):
        r = client_autenticado.post('/api/interpretation', json={'house': 4, 'custom_query': 'Casa 4'})
        assert r.status_code == 200
        corpo = r.json()
        assert corpo['query_used'] == 'Casa 4' and corpo['sources'][0]['source'] == 'livro'

    @pytest.mark.api
    @pytest.mark.unit
    def test_planeta_em_signo_usa_o_endpoint_especifico(self, client_autenticado):
        r = client_autenticado.post('/api/interpretation', json={'planet': 'Sol', 'sign': 'Áries'})
        assert r.status_code == 400

    @pytest.mark.api
    @pytest.mark.unit
    def test_aspecto(self, client_autenticado):
        r = client_autenticado.post('/api/interpretation/aspect', json={'planet1': 'Sol', 'planet2': 'Lua', 'aspect': 'conjunção'})
        assert r.status_code == 200
        assert 'Sol conjunção Lua' in r.json()['query_used']

    @pytest.mark.api
    @pytest.mark.unit
    def test_conselho_diario_monta_consulta_com_a_casa_lunar(self, client_autenticado):
        r = client_autenticado.post('/api/interpretation/daily-advice', json={
            'moonHouse': 5, 'category': 'love', 'planetaryPositions': [{'name': 'Vênus', 'house': 7, 'sign': 'Libra'}]})
        assert r.status_code == 200
        consulta = r.json()['query_used']
        assert 'casa 5' in consulta and 'Vênus casa 7' in consulta

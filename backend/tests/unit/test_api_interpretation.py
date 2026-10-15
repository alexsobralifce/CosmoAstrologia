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

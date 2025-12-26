"""
Testes de integração específicos para endpoints do backend que usam RAG.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

# Configurar RAG_SERVICE_URL para testes
os.environ["RAG_SERVICE_URL"] = "http://localhost:8001"

client = TestClient(app)


def test_interpretation_endpoint_planet_sign():
    """Testa endpoint de interpretação com planeta e signo."""
    response = client.post(
        "/api/interpretation",
        json={
            "planet": "Sol",
            "sign": "Libra",
            "use_groq": True
        }
    )
    
    # Pode retornar 503 se RAG service não estiver disponível
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "interpretation" in data
        assert "sources" in data
        assert "query_used" in data
        assert len(data.get("interpretation", "")) > 0


def test_interpretation_endpoint_custom_query():
    """Testa endpoint de interpretação com query customizada."""
    response = client.post(
        "/api/interpretation",
        json={
            "custom_query": "ascendente em aquário significado",
            "use_groq": True
        }
    )
    
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "interpretation" in data


def test_interpretation_endpoint_planet():
    """Testa endpoint específico de interpretação de planeta."""
    response = client.post(
        "/api/interpretation/planet",
        json={
            "planet": "Sol",
            "sign": "Libra",
            "sunSign": "Leão",
            "moonSign": "Câncer",
            "ascendant": "Áries"
        }
    )
    
    # Pode retornar 503 se RAG service não estiver disponível
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "interpretation" in data
        assert "sources" in data


def test_interpretation_endpoint_chart_ruler():
    """Testa endpoint de interpretação do regente do mapa."""
    response = client.post(
        "/api/interpretation/chart-ruler",
        json={
            "ascendant": "Áries",
            "ruler": "Marte",
            "rulerSign": "Leão",
            "rulerHouse": 5
        }
    )
    
    assert response.status_code in [200, 503, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "interpretation" in data


def test_search_endpoint():
    """Testa endpoint de busca."""
    response = client.get(
        "/api/interpretation/search",
        params={
            "query": "Sol em Libra",
            "top_k": 5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert "count" in data
    assert isinstance(data["results"], list)


def test_status_endpoint():
    """Testa endpoint de status do RAG."""
    response = client.get("/api/interpretation/status")
    
    assert response.status_code == 200
    data = response.json()
    # Pode retornar available=False se RAG service não estiver rodando
    assert "available" in data or "status" in data


def test_diagnostics_endpoint():
    """Testa endpoint de diagnósticos que verifica RAG."""
    response = client.get("/birth-chart/diagnostics")
    
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "rag" in data.get("services", {})


@pytest.mark.asyncio
async def test_rag_client_error_handling():
    """Testa tratamento de erros do cliente RAG."""
    from app.services.rag_client import RAGClient
    
    # Cliente com URL inválida
    invalid_client = RAGClient(base_url="http://localhost:9999")
    
    try:
        status = await invalid_client.get_status()
        # Se não conseguir conectar, deve lançar exceção
        pytest.fail("Deveria ter lançado exceção de conexão")
    except Exception as e:
        # Esperado: erro de conexão
        assert "conectar" in str(e).lower() or "connect" in str(e).lower() or "timeout" in str(e).lower()


def test_interpretation_without_rag_service():
    """Testa comportamento quando RAG service não está disponível."""
    # Remover RAG_SERVICE_URL temporariamente
    original_url = os.environ.get("RAG_SERVICE_URL")
    os.environ.pop("RAG_SERVICE_URL", None)
    
    try:
        from app.services.rag_client import get_rag_client
        rag_client = get_rag_client()
        
        # Deve retornar None se RAG_SERVICE_URL não estiver configurado
        assert rag_client is None
    finally:
        # Restaurar
        if original_url:
            os.environ["RAG_SERVICE_URL"] = original_url


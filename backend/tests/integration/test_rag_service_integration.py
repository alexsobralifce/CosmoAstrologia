"""
Testes de integração para o RAG Service (microsserviço).
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

# Configurar URL do RAG service para testes
RAG_SERVICE_URL = "http://localhost:8001"


@pytest.fixture
def client():
    """Cliente de teste para o backend."""
    return TestClient(app)


@pytest.fixture
def rag_service_client():
    """Cliente HTTP para o RAG service."""
    return httpx.AsyncClient(base_url=RAG_SERVICE_URL, timeout=30.0)


@pytest.mark.asyncio
async def test_rag_service_health(rag_service_client):
    """Testa se o RAG service está respondendo."""
    try:
        response = await rag_service_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        assert data.get("service") == "rag-service"
    except httpx.ConnectError:
        pytest.skip("RAG service não está rodando. Inicie com: docker-compose up rag-service")


@pytest.mark.asyncio
async def test_rag_service_status(rag_service_client):
    """Testa o endpoint de status do RAG service."""
    try:
        response = await rag_service_client.get("/api/rag/status")
        assert response.status_code == 200
        data = response.json()
        assert "available" in data
        assert "has_index" in data
        assert "has_groq" in data
    except httpx.ConnectError:
        pytest.skip("RAG service não está rodando")


@pytest.mark.asyncio
async def test_rag_service_search(rag_service_client):
    """Testa busca de documentos no RAG service."""
    try:
        response = await rag_service_client.post(
            "/api/rag/search",
            json={
                "query": "Sol em Libra",
                "top_k": 5,
                "expand_query": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data
        assert isinstance(data["results"], list)
    except httpx.ConnectError:
        pytest.skip("RAG service não está rodando")


@pytest.mark.asyncio
async def test_rag_service_interpretation(rag_service_client):
    """Testa interpretação no RAG service."""
    try:
        response = await rag_service_client.post(
            "/api/rag/interpretation",
            json={
                "planet": "Sol",
                "sign": "Libra",
                "use_groq": True,
                "top_k": 8
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "interpretation" in data
        assert "sources" in data
        assert "query_used" in data
        assert len(data.get("interpretation", "")) > 0
    except httpx.ConnectError:
        pytest.skip("RAG service não está rodando")


def test_backend_rag_status_endpoint(client):
    """Testa se o backend consegue verificar status do RAG via cliente HTTP."""
    response = client.get("/api/interpretation/status")
    assert response.status_code == 200
    data = response.json()
    # Pode retornar available=False se RAG service não estiver rodando
    assert "available" in data or "status" in data


def test_backend_interpretation_endpoint_with_rag(client):
    """Testa endpoint de interpretação do backend que usa RAG service."""
    # Configurar RAG_SERVICE_URL se não estiver configurado
    import os
    if not os.getenv("RAG_SERVICE_URL"):
        os.environ["RAG_SERVICE_URL"] = RAG_SERVICE_URL
    
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


def test_backend_search_endpoint_with_rag(client):
    """Testa endpoint de busca do backend que usa RAG service."""
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


@pytest.mark.asyncio
async def test_rag_client_integration():
    """Testa o cliente RAG diretamente."""
    from app.services.rag_client import get_rag_client
    
    # Configurar URL
    import os
    os.environ["RAG_SERVICE_URL"] = RAG_SERVICE_URL
    
    rag_client = get_rag_client()
    
    if rag_client is None:
        pytest.skip("RAG_SERVICE_URL não configurado")
    
    try:
        # Testar health check
        health = await rag_client.health_check()
        assert health.get("status") == "healthy"
        
        # Testar status
        status = await rag_client.get_status()
        assert "available" in status
        
        # Testar busca
        results = await rag_client.search("Sol em Libra", top_k=3)
        assert isinstance(results, list)
        
        # Testar interpretação (se disponível)
        if status.get("available"):
            interpretation = await rag_client.get_interpretation(
                planet="Sol",
                sign="Libra",
                use_groq=True
            )
            assert "interpretation" in interpretation
            assert len(interpretation.get("interpretation", "")) > 0
            
    except Exception as e:
        # Se não conseguir conectar, pular teste
        if "Connect" in str(e) or "timeout" in str(e).lower():
            pytest.skip(f"RAG service não está rodando: {e}")
        else:
            raise


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_integration_flow():
    """
    Teste completo de integração: Backend -> RAG Service -> Resposta
    """
    from app.services.rag_client import get_rag_client
    import os
    
    # Configurar
    os.environ["RAG_SERVICE_URL"] = RAG_SERVICE_URL
    
    rag_client = get_rag_client()
    if rag_client is None:
        pytest.skip("RAG_SERVICE_URL não configurado")
    
    try:
        # 1. Verificar se RAG service está disponível
        status = await rag_client.get_status()
        if not status.get("available"):
            pytest.skip("RAG service não está disponível (índice não carregado)")
        
        # 2. Buscar contexto
        results = await rag_client.search("Sol em Libra significado", top_k=5)
        assert len(results) > 0
        
        # 3. Obter interpretação completa
        interpretation = await rag_client.get_interpretation(
            planet="Sol",
            sign="Libra",
            use_groq=status.get("has_groq", False),
            top_k=8
        )
        
        assert "interpretation" in interpretation
        assert len(interpretation.get("interpretation", "")) > 50
        assert "sources" in interpretation
        assert "query_used" in interpretation
        
    except Exception as e:
        if "Connect" in str(e) or "timeout" in str(e).lower():
            pytest.skip(f"RAG service não está rodando: {e}")
        else:
            raise


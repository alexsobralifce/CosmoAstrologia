"""
Testes de integração entre Backend e RAG Service.
Testa a comunicação HTTP entre os serviços.
"""

import pytest
import httpx
import asyncio
from pathlib import Path


@pytest.fixture
def backend_url():
    """URL do backend para testes."""
    return "http://localhost:8000"


@pytest.fixture
def rag_service_url():
    """URL do RAG service para testes."""
    return "http://localhost:8001"


@pytest.mark.asyncio
async def test_rag_service_health(rag_service_url):
    """Testa se o RAG service está respondendo."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{rag_service_url}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
        except httpx.ConnectError:
            pytest.skip("RAG service não está rodando")


@pytest.mark.asyncio
async def test_rag_service_status(rag_service_url):
    """Testa endpoint de status do RAG service."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{rag_service_url}/api/rag/status")
            assert response.status_code in [200, 503]
            
            if response.status_code == 200:
                data = response.json()
                assert "available" in data
                assert "has_dependencies" in data
        except httpx.ConnectError:
            pytest.skip("RAG service não está rodando")


@pytest.mark.asyncio
async def test_backend_rag_client_integration(backend_url):
    """Testa se o backend consegue se comunicar com o RAG service."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Testar endpoint de diagnóstico
            response = await client.get(f"{backend_url}/api/health/diagnostics")
            assert response.status_code == 200
            
            data = response.json()
            # Verificar se há informação sobre RAG
            assert "services" in data
            if "rag" in data["services"]:
                rag_status = data["services"]["rag"]
                assert "available" in rag_status
        except httpx.ConnectError:
            pytest.skip("Backend não está rodando")


@pytest.mark.asyncio
async def test_full_interpretation_flow(backend_url, rag_service_url):
    """Testa fluxo completo de interpretação."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Verificar se RAG service está disponível
            rag_response = await client.get(f"{rag_service_url}/health")
            if rag_response.status_code != 200:
                pytest.skip("RAG service não está disponível")
            
            # 2. Testar busca no RAG service diretamente
            search_response = await client.post(
                f"{rag_service_url}/api/rag/search",
                json={
                    "query": "Sol em Libra",
                    "top_k": 5
                }
            )
            
            # Pode retornar 503 se índice não estiver carregado
            assert search_response.status_code in [200, 503]
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                assert "results" in search_data
                assert "count" in search_data
            
            # 3. Testar interpretação via backend (se autenticado)
            # Nota: Este teste pode precisar de autenticação
            # interpretation_response = await client.post(
            #     f"{backend_url}/api/interpretation/planet",
            #     json={
            #         "planet": "Sol",
            #         "sign": "Libra"
            #     }
            # )
            
        except httpx.ConnectError as e:
            pytest.skip(f"Serviço não está rodando: {e}")


@pytest.mark.asyncio
async def test_rag_service_search_endpoint(rag_service_url):
    """Testa endpoint de busca do RAG service."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"{rag_service_url}/api/rag/search",
                json={
                    "query": "ascendente em aquário",
                    "top_k": 6,
                    "expand_query": False,
                    "category": "astrology"
                }
            )
            
            assert response.status_code in [200, 503]
            
            if response.status_code == 200:
                data = response.json()
                assert "results" in data
                assert "count" in data
                assert isinstance(data["results"], list)
                
                # Verificar estrutura dos resultados
                if len(data["results"]) > 0:
                    result = data["results"][0]
                    assert "text" in result
                    assert "score" in result
                    assert "source" in result
                    
        except httpx.ConnectError:
            pytest.skip("RAG service não está rodando")


@pytest.mark.asyncio
async def test_rag_service_interpretation_endpoint(rag_service_url):
    """Testa endpoint de interpretação do RAG service."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{rag_service_url}/api/rag/interpretation",
                json={
                    "planet": "Sol",
                    "sign": "Libra",
                    "use_groq": False,  # Sem Groq para teste mais rápido
                    "top_k": 6
                }
            )
            
            assert response.status_code in [200, 503]
            
            if response.status_code == 200:
                data = response.json()
                assert "interpretation" in data
                assert "sources" in data
                assert "query_used" in data
                assert "generated_by" in data
                
        except httpx.ConnectError:
            pytest.skip("RAG service não está rodando")


class TestRAGClientIntegration:
    """Testes de integração do RAG Client no backend."""
    
    @pytest.mark.asyncio
    async def test_rag_client_initialization(self):
        """Testa inicialização do RAG client."""
        try:
            from backend.app.services.rag_client import get_rag_client
            
            client = get_rag_client()
            # Pode ser None se RAG_SERVICE_URL não estiver configurado
            assert client is None or hasattr(client, 'search')
        except ImportError:
            pytest.skip("RAG client não disponível")
    
    @pytest.mark.asyncio
    async def test_rag_client_search(self, rag_service_url):
        """Testa busca usando RAG client."""
        try:
            from backend.app.services.rag_client import RAGClient
            
            client = RAGClient(base_url=rag_service_url)
            
            # Verificar se serviço está disponível
            try:
                await client.health_check()
            except Exception:
                pytest.skip("RAG service não está disponível")
            
            # Testar busca
            results = await client.search("Sol em Libra", top_k=6)
            assert isinstance(results, list)
            
            if len(results) > 0:
                assert "text" in results[0]
                assert "score" in results[0]
                
        except ImportError:
            pytest.skip("RAG client não disponível")
        except httpx.ConnectError:
            pytest.skip("RAG service não está rodando")


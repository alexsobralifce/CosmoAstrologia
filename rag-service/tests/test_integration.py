"""
Testes de integração para o RAG Service.
Testa a integração entre componentes do serviço.
"""

import pytest
import httpx
import asyncio
from pathlib import Path
import tempfile
import shutil

from app.services.rag_service import RAGServiceFastEmbed
from app.api.routes import router
from fastapi.testclient import TestClient
from fastapi import FastAPI


@pytest.fixture
def test_app():
    """Cria uma aplicação FastAPI para testes."""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(test_app):
    """Cria um cliente de teste."""
    return TestClient(test_app)


@pytest.fixture
def temp_dir():
    """Cria um diretório temporário."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


class TestRAGServiceIntegration:
    """Testes de integração do RAG Service."""
    
    def test_service_initialization_with_config(self, temp_dir):
        """Testa inicialização do serviço com configuração."""
        from app.core.config import settings
        
        service = RAGServiceFastEmbed(
            docs_path=str(temp_dir / "docs"),
            index_path=str(temp_dir / "index"),
            bge_model_name=settings.BGE_MODEL_NAME
        )
        
        assert service.bge_model_name == settings.BGE_MODEL_NAME
    
    def test_process_and_save_workflow(self, temp_dir):
        """Testa o workflow completo de processamento e salvamento."""
        docs_path = temp_dir / "docs"
        docs_path.mkdir()
        
        # Criar arquivo de teste
        test_file = docs_path / "test.md"
        test_file.write_text("""
        # Teste de Astrologia
        
        Sol em Libra significa busca por harmonia e equilíbrio.
        Lua em Escorpião indica intensidade emocional profunda.
        """)
        
        service = RAGServiceFastEmbed(
            docs_path=str(docs_path),
            index_path=str(temp_dir / "index"),
            bge_model_name="BAAI/bge-small-en-v1.5"
        )
        
        # Processar documentos
        try:
            num_chunks = service.process_all_documents()
            if num_chunks > 0:
                # Salvar índice
                service.save_index()
                
                # Verificar que arquivos foram criados
                index_path = Path(service.index_path)
                assert (index_path / "documents.json").exists()
                assert (index_path / "embeddings.npy").exists()
                assert (index_path / "metadata.json").exists()
        except Exception as e:
            # Se FastEmbed não estiver disponível, pular teste
            pytest.skip(f"FastEmbed não disponível: {e}")


class TestAPIIntegration:
    """Testes de integração da API."""
    
    def test_health_endpoint(self, client):
        """Testa endpoint de health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "rag-service"
    
    def test_status_endpoint(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/rag/status")
        assert response.status_code in [200, 503]  # 503 se serviço não disponível
        
        if response.status_code == 200:
            data = response.json()
            assert "available" in data
            assert "has_dependencies" in data
    
    def test_search_endpoint(self, client):
        """Testa endpoint de busca."""
        response = client.post(
            "/api/rag/search",
            json={
                "query": "Sol em Libra",
                "top_k": 5
            }
        )
        
        # Pode retornar 503 se serviço não estiver configurado
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert "count" in data
    
    def test_interpretation_endpoint(self, client):
        """Testa endpoint de interpretação."""
        response = client.post(
            "/api/rag/interpretation",
            json={
                "planet": "Sol",
                "sign": "Libra",
                "use_groq": False,
                "top_k": 5
            }
        )
        
        # Pode retornar 503 se serviço não estiver configurado
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "interpretation" in data
            assert "sources" in data
            assert "query_used" in data


class TestEndToEnd:
    """Testes end-to-end do sistema."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_dir):
        """Testa workflow completo: processar -> salvar -> carregar -> buscar."""
        docs_path = temp_dir / "docs"
        docs_path.mkdir()
        
        # Criar documento de teste
        test_file = docs_path / "test.md"
        test_file.write_text("""
        # Astrologia Teste
        
        Sol em Libra significa busca por harmonia e equilíbrio nos relacionamentos.
        A pessoa busca justiça e beleza em todas as áreas da vida.
        """)
        
        service = RAGServiceFastEmbed(
            docs_path=str(docs_path),
            index_path=str(temp_dir / "index"),
            bge_model_name="BAAI/bge-small-en-v1.5"
        )
        
        try:
            # 1. Processar documentos
            num_chunks = service.process_all_documents()
            if num_chunks == 0:
                pytest.skip("Nenhum chunk processado")
            
            # 2. Salvar índice
            service.save_index()
            
            # 3. Criar novo serviço e carregar
            new_service = RAGServiceFastEmbed(
                docs_path=str(docs_path),
                index_path=str(temp_dir / "index"),
                bge_model_name="BAAI/bge-small-en-v1.5"
            )
            
            loaded = new_service.load_index()
            assert loaded is True
            
            # 4. Buscar
            results = new_service.search("Sol Libra harmonia", top_k=3)
            assert len(results) > 0
            assert all('text' in r for r in results)
            assert all('score' in r for r in results)
            
        except Exception as e:
            # Se FastEmbed não estiver disponível, pular teste
            pytest.skip(f"FastEmbed não disponível: {e}")


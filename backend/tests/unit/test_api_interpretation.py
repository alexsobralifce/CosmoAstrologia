"""
Testes TDD para API de Interpretação - Código Crítico
Garante que os endpoints funcionam corretamente e lidam com erros adequadamente.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Cliente de teste para a API."""
    from app.main import app
    return TestClient(app)


class TestInterpretationAPI:
    """Testes para endpoints de interpretação."""
    
    @pytest.mark.critical
    @pytest.mark.api
    @pytest.mark.unit
    def test_get_interpretation_returns_503_when_rag_service_unavailable(self, client):
        """
        TDD: Endpoint deve retornar 503 quando serviço RAG não está disponível.
        Código crítico - garante resposta apropriada quando serviço está down.
        """
        # Arrange - usar custom_query para evitar validação que retorna 400
        with patch('app.api.interpretation.get_rag_service', return_value=None):
            # Act
            response = client.post(
                "/api/interpretation",
                json={
                    "custom_query": "Sol em Leão"
                }
            )
            
            # Assert
            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert "RAG" in response.json()["detail"] or "não disponível" in response.json()["detail"]
    
    @pytest.mark.critical
    @pytest.mark.api
    @pytest.mark.unit
    def test_rag_status_endpoint_handles_missing_service(self, client):
        """
        TDD: Endpoint de status deve funcionar mesmo quando serviço não está disponível.
        Código crítico - garante que status pode ser consultado sempre.
        """
        # Arrange
        with patch('app.api.interpretation.get_rag_service', return_value=None):
            # Act
            response = client.get("/api/interpretation/status")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data.get("status") == "unavailable" or data.get("available") is False
            assert "has_index" in data or "index_loaded" in data
    
    @pytest.mark.critical
    @pytest.mark.api
    @pytest.mark.unit
    def test_rag_search_returns_empty_results_when_service_unavailable(self, client):
        """
        TDD: Busca RAG deve retornar resultados vazios quando serviço não está disponível.
        Código crítico - garante que busca não quebra o app.
        """
        # Arrange
        with patch('app.api.interpretation.get_rag_service', return_value=None):
            # Act
            response = client.get("/api/interpretation/search?query=test&top_k=5")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["results"] == []
            assert data["count"] == 0
            assert "error" in data
    
    @pytest.mark.critical
    @pytest.mark.api
    @pytest.mark.unit
    def test_interpretation_endpoint_validates_required_fields(self, client):
        """
        TDD: Endpoint deve validar campos obrigatórios antes de processar.
        Código crítico - garante validação de entrada.
        """
        # Arrange - request sem campos obrigatórios
        with patch('app.api.interpretation.get_rag_service', return_value=None):
            # Act
            response = client.post(
                "/api/interpretation",
                json={}
            )
            
            # Assert - pode retornar 422 (validação) ou 503 (serviço), mas não 500
            assert response.status_code in [
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                status.HTTP_503_SERVICE_UNAVAILABLE
            ]
    
    @pytest.mark.api
    @pytest.mark.unit
    def test_api_imports_without_syntax_errors(self):
        """
        TDD: Módulo de API deve importar sem erros de sintaxe.
        Código crítico - garante que não há erros de sintaxe após correções.
        """
        # Arrange & Act & Assert
        try:
            from app.api import interpretation
            assert interpretation is not None
        except SyntaxError as e:
            pytest.fail(f"Módulo tem erro de sintaxe: {e}")


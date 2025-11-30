"""
Testes TDD para RAG Service Wrapper - Código Crítico
Garante que o wrapper funciona corretamente mesmo quando LlamaIndex não está disponível.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys

# Importações que serão testadas
from app.services.rag_service_wrapper import (
    get_rag_service,
    get_rag_implementation,
    is_llamaindex_available
)


class TestRAGServiceWrapper:
    """Testes para o wrapper do serviço RAG."""
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_get_rag_service_returns_none_when_llamaindex_unavailable(self, mock_llamaindex_unavailable):
        """
        TDD: Quando LlamaIndex não está disponível, get_rag_service deve retornar None.
        Código crítico - garante que o app não quebra se dependências não estiverem instaladas.
        """
        # Arrange & Act
        service = get_rag_service()
        
        # Assert
        assert service is None, "Service deve ser None quando LlamaIndex não está disponível"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_get_rag_service_handles_import_error_gracefully(self):
        """
        TDD: Wrapper deve lidar com ImportError sem quebrar a aplicação.
        Código crítico - garante resiliência a falhas de importação.
        """
        # Arrange
        with patch('app.services.rag_service_wrapper._implementation_available', False):
            with patch('app.services.rag_service_wrapper._get_rag_service', None):
                # Act
                service = get_rag_service()
                
                # Assert
                assert service is None, "Service deve retornar None quando não disponível"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_is_llamaindex_available_returns_boolean(self):
        """
        TDD: is_llamaindex_available deve sempre retornar um booleano.
        Código crítico - garante tipo de retorno consistente.
        """
        # Act
        result = is_llamaindex_available()
        
        # Assert
        assert isinstance(result, bool), "Deve retornar boolean"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_get_rag_implementation_returns_string(self):
        """
        TDD: get_rag_implementation deve sempre retornar uma string.
        Código crítico - garante tipo de retorno consistente.
        """
        # Act
        result = get_rag_implementation()
        
        # Assert
        assert isinstance(result, str), "Deve retornar string"
        assert result == "llamaindex", "Deve retornar 'llamaindex'"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_get_rag_service_handles_exception_during_initialization(self):
        """
        TDD: Wrapper deve capturar exceções durante inicialização do serviço.
        Código crítico - garante que exceções não quebrem o app.
        """
        # Arrange
        mock_service_func = MagicMock(side_effect=Exception("Erro de inicialização"))
        
        with patch('app.services.rag_service_wrapper._get_rag_service', mock_service_func):
            with patch('app.services.rag_service_wrapper._implementation_available', True):
                # Act
                service = get_rag_service()
                
                # Assert
                assert service is None, "Deve retornar None quando há exceção"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_wrapper_does_not_crash_on_import_failure(self):
        """
        TDD: Importação do wrapper não deve quebrar mesmo se LlamaIndex falhar.
        Código crítico - garante que o módulo pode ser importado sempre.
        """
        # Arrange & Act & Assert
        try:
            # Tentar importar o wrapper deve sempre funcionar
            from app.services import rag_service_wrapper
            assert rag_service_wrapper is not None
        except ImportError as e:
            pytest.fail(f"Importação do wrapper não deve falhar: {e}")


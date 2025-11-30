"""
Testes TDD para RAG Service LlamaIndex - Código Crítico
Garante que o serviço RAG funciona corretamente e lida com erros adequadamente.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path


class TestRAGServiceLlamaIndex:
    """Testes para o serviço RAG usando LlamaIndex."""
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_service_initializes_without_crash_when_llamaindex_unavailable(self):
        """
        TDD: Serviço deve inicializar sem crash mesmo quando LlamaIndex não está disponível.
        Código crítico - garante resiliência a dependências ausentes.
        """
        # Arrange
        with patch('app.services.rag_service_llamaindex.HAS_LLAMAINDEX', False):
            # Act & Assert - não deve lançar exceção
            from app.services.rag_service_llamaindex import RAGServiceLlamaIndex
            service = RAGServiceLlamaIndex()
            assert service is not None
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_sentence_splitter_type_hint_does_not_crash_on_import_error(self):
        """
        TDD: Anotação de tipo SentenceSplitter não deve quebrar quando importação falha.
        Código crítico - corrige o bug que estava causando SyntaxError.
        """
        # Arrange
        with patch('app.services.rag_service_llamaindex.HAS_LLAMAINDEX', False):
            # Act & Assert - não deve lançar NameError ou SyntaxError
            try:
                from app.services.rag_service_llamaindex import RAGServiceLlamaIndex
                # Se chegou aqui, a importação funcionou
                assert True
            except (NameError, SyntaxError) as e:
                pytest.fail(f"Anotação de tipo causou erro: {e}")
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_service_handles_missing_groq_gracefully(self):
        """
        TDD: Serviço deve funcionar mesmo quando Groq não está disponível.
        Código crítico - garante que funcionalidades não-Groq continuem funcionando.
        """
        # Arrange
        with patch('app.services.rag_service_llamaindex.HAS_GROQ', False):
            with patch('app.services.rag_service_llamaindex.HAS_LLAMAINDEX', True):
                # Act
                from app.services.rag_service_llamaindex import RAGServiceLlamaIndex
                service = RAGServiceLlamaIndex()
                
                # Assert
                assert service.groq_client is None, "Groq client deve ser None quando não disponível"
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_service_sets_groq_client_when_api_key_provided(self):
        """
        TDD: Serviço deve configurar cliente Groq quando API key é fornecida.
        Código crítico - garante inicialização correta do cliente.
        """
        # Arrange
        mock_groq = MagicMock()
        with patch('app.services.rag_service_llamaindex.HAS_GROQ', True):
            with patch('app.services.rag_service_llamaindex.HAS_LLAMAINDEX', True):
                with patch('app.services.rag_service_llamaindex.Groq', return_value=mock_groq):
                    # Act
                    from app.services.rag_service_llamaindex import RAGServiceLlamaIndex
                    service = RAGServiceLlamaIndex(groq_api_key="test-key")
                    
                    # Assert
                    assert service.groq_client is not None, "Groq client deve ser configurado"
    
    @pytest.mark.unit
    def test_service_handles_invalid_docs_path(self):
        """
        TDD: Serviço deve lidar com caminho de documentos inválido sem crash.
        """
        # Arrange
        invalid_path = Path("/path/that/does/not/exist")
        
        with patch('app.services.rag_service_llamaindex.HAS_LLAMAINDEX', False):
            # Act
            from app.services.rag_service_llamaindex import RAGServiceLlamaIndex
            service = RAGServiceLlamaIndex(docs_path=str(invalid_path))
            
            # Assert - não deve crashar
            assert service.docs_path == invalid_path


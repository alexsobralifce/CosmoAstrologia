"""
Configuração compartilhada de pytest para todos os testes.
Fixtures e configurações globais para TDD.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Generator
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))


@pytest.fixture
def mock_rag_service():
    """Fixture para mock do RAG service."""
    mock_service = MagicMock()
    mock_service.index = None
    mock_service.search = MagicMock(return_value=[])
    mock_service.get_interpretation = MagicMock(return_value={
        'interpretation': 'Mock interpretation',
        'sources': [],
        'query_used': 'test query'
    })
    return mock_service


@pytest.fixture
def mock_llamaindex_unavailable():
    """Fixture para simular LlamaIndex não disponível."""
    with patch('app.services.rag_service_llamaindex.HAS_LLAMAINDEX', False):
        yield


@pytest.fixture
def mock_groq_client():
    """Fixture para mock do cliente Groq."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = MagicMock()
    return mock_client


@pytest.fixture
def sample_birth_data():
    """Dados de nascimento de exemplo para testes."""
    return {
        'birth_date': '1990-05-15',
        'birth_time': '10:30:00',
        'birth_place': 'São Paulo, SP, Brazil',
        'latitude': -23.5505,
        'longitude': -46.6333
    }


@pytest.fixture
def sample_numerology_data():
    """Dados numerológicos de exemplo para testes."""
    return {
        'full_name': 'João Silva',
        'birth_date': '1990-05-15'
    }


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Reset variáveis de ambiente antes de cada teste."""
    # Limpar variáveis sensíveis antes de cada teste
    monkeypatch.delenv('GROQ_API_KEY', raising=False)
    monkeypatch.delenv('DATABASE_URL', raising=False)
    yield
    # Cleanup após teste (se necessário)


@pytest.fixture
def db_session():
    """Fixture para sessão de banco de dados (mock)."""
    mock_session = MagicMock()
    mock_session.query = MagicMock()
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_session.rollback = MagicMock()
    return mock_session


@pytest.fixture
def test_client():
    """Fixture para cliente de teste FastAPI."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


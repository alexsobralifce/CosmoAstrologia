"""
Configuração de fixtures compartilhadas para testes de integração.
"""

import pytest
import sys
from pathlib import Path

# Adicionar paths necessários
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path / "backend"))
sys.path.insert(0, str(root_path / "rag-service"))


@pytest.fixture(scope="session")
def services_config():
    """Configuração dos serviços para testes."""
    return {
        "backend_url": "http://localhost:8000",
        "rag_service_url": "http://localhost:8001",
        "timeout": 30.0
    }


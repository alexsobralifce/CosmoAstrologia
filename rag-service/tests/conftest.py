"""
Configuração de fixtures compartilhadas para testes.
"""

import pytest
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_config():
    """Configuração de teste."""
    return {
        "docs_path": "tests/fixtures/docs",
        "index_path": "tests/fixtures/index",
        "bge_model_name": "BAAI/bge-small-en-v1.5"
    }


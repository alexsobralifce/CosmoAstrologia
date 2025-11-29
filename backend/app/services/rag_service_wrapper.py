"""
Wrapper para o serviço RAG usando LlamaIndex.
"""

from typing import Optional
from pathlib import Path
from app.core.config import settings

# Usar apenas a implementação LlamaIndex
try:
    from app.services.rag_service_llamaindex import get_rag_service_llamaindex as _get_rag_service
    print(f"[RAG] Usando implementação LlamaIndex")
    _implementation_available = True
except ImportError as e:
    print(f"[ERROR] LlamaIndex não disponível: {e}")
    raise ImportError("LlamaIndex RAG service é obrigatório. Instale as dependências necessárias.")


def get_rag_service():
    """
    Retorna o serviço RAG usando LlamaIndex.
    """
    return _get_rag_service()


def get_rag_implementation() -> str:
    """Retorna qual implementação está sendo usada."""
    return "llamaindex"


def is_llamaindex_available() -> bool:
    """Verifica se a implementação LlamaIndex está disponível."""
    return _implementation_available


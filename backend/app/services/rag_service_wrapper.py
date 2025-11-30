"""
Wrapper para o serviço RAG usando LlamaIndex.
"""

from typing import Optional
from pathlib import Path
from app.core.config import settings

# Usar apenas a implementação LlamaIndex
_get_rag_service = None
_implementation_available = False

try:
    from app.services.rag_service_llamaindex import get_rag_service_llamaindex as _get_rag_service
    print(f"[RAG] Usando implementação LlamaIndex")
    _implementation_available = True
except ImportError as e:
    print(f"[WARNING] LlamaIndex não disponível: {e}")
    print(f"[WARNING] RAG service estará desabilitado. Aplicação continuará usando fallback local.")
    _implementation_available = False
except Exception as e:
    print(f"[WARNING] Erro ao inicializar LlamaIndex: {e}")
    print(f"[WARNING] RAG service estará desabilitado. Aplicação continuará usando fallback local.")
    _implementation_available = False


def get_rag_service():
    """
    Retorna o serviço RAG usando LlamaIndex.
    Retorna None se o LlamaIndex não estiver disponível.
    """
    if not _implementation_available or _get_rag_service is None:
        return None
    try:
        return _get_rag_service()
    except Exception as e:
        print(f"[WARNING] Erro ao obter serviço RAG: {e}")
        return None


def get_rag_implementation() -> str:
    """Retorna qual implementação está sendo usada."""
    return "llamaindex"


def is_llamaindex_available() -> bool:
    """Verifica se a implementação LlamaIndex está disponível."""
    return _implementation_available


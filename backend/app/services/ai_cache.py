"""Cache de respostas de LLM (padrão Decorator sobre AIProviderService).

O mesmo mapa/seção/idioma gera o mesmo prompt; sem cache, cada abertura de tela paga a LLM de novo.
A chave é o hash do pedido inteiro (provedor, prompts e parâmetros), então qualquer mudança de
prompt invalida sozinha as entradas antigas.
"""
import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Protocol

from app.services.ai_provider_service import AIProviderService

logger = logging.getLogger(__name__)


class CacheStore(Protocol):
    def get(self, key: str, max_age: timedelta) -> Optional[str]: ...
    def set(self, key: str, provider: str, response: str) -> None: ...


class SqlAlchemyCacheStore:
    """Persiste no banco da aplicação (sobrevive a reinícios e vale para todas as instâncias)."""

    def get(self, key: str, max_age: timedelta) -> Optional[str]:
        from app.core.database import SessionLocal
        from app.models.database import LLMCacheEntry

        with SessionLocal() as db:
            entry = db.get(LLMCacheEntry, key)
            if entry is None:
                return None
            created = entry.created_at
            if created is not None and created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            if created is not None and datetime.now(timezone.utc) - created > max_age:
                return None
            return entry.response

    def set(self, key: str, provider: str, response: str) -> None:
        from app.core.database import SessionLocal
        from app.models.database import LLMCacheEntry

        with SessionLocal() as db:
            db.merge(LLMCacheEntry(key=key, provider=provider, response=response,
                                   created_at=datetime.now(timezone.utc)))
            db.commit()


def build_cache_key(provider_name: str, system_prompt: str, user_prompt: str,
                    temperature: float, max_tokens: int, extra: dict) -> str:
    payload = json.dumps(
        [provider_name, system_prompt, user_prompt, temperature, max_tokens, extra],
        sort_keys=True, ensure_ascii=False, default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CachedAIProvider(AIProviderService):
    """Mesma interface do provedor real; consulta o cache antes de chamar a LLM.

    Falha do cache nunca derruba a requisição: em erro, segue direto para o provedor.
    """

    def __init__(self, inner: AIProviderService, store: CacheStore, ttl: timedelta):
        self._inner = inner
        self._store = store
        self._ttl = ttl

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.7,
                      max_tokens: int = 2000, **kwargs) -> str:
        key = build_cache_key(self._inner.get_provider_name(), system_prompt, user_prompt,
                              temperature, max_tokens, kwargs)
        try:
            cached = self._store.get(key, self._ttl)
            if cached is not None:
                return cached
        except Exception:
            logger.warning("Falha ao ler cache de LLM; seguindo sem cache", exc_info=True)

        text = self._inner.generate_text(system_prompt, user_prompt, temperature, max_tokens, **kwargs)

        if text:
            try:
                self._store.set(key, self._inner.get_provider_name(), text)
            except Exception:
                logger.warning("Falha ao gravar cache de LLM", exc_info=True)
        return text

    def is_available(self) -> bool:
        return self._inner.is_available()

    def get_provider_name(self) -> str:
        return self._inner.get_provider_name()

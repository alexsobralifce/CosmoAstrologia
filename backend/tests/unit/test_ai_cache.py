"""Testes do cache de respostas de LLM (Decorator sobre AIProviderService)."""
from datetime import timedelta

import pytest

from app.services.ai_cache import CachedAIProvider, SqlAlchemyCacheStore, build_cache_key
from app.services.ai_provider_service import AIProviderService


class FakeProvider(AIProviderService):
    def __init__(self):
        self.calls = 0

    def generate_text(self, system_prompt, user_prompt, temperature=0.7, max_tokens=2000, **kwargs):
        self.calls += 1
        return f"resposta {self.calls}"

    def is_available(self):
        return True

    def get_provider_name(self):
        return "fake"


class MemoryStore:
    def __init__(self):
        self.data = {}

    def get(self, key, max_age):
        return self.data.get(key)

    def set(self, key, provider, response):
        self.data[key] = response


class BrokenStore:
    def get(self, key, max_age):
        raise RuntimeError("banco fora")

    def set(self, key, provider, response):
        raise RuntimeError("banco fora")


@pytest.mark.unit
def test_segunda_chamada_igual_vem_do_cache():
    inner = FakeProvider()
    provider = CachedAIProvider(inner, MemoryStore(), timedelta(days=1))
    assert provider.generate_text("sys", "mapa X") == "resposta 1"
    assert provider.generate_text("sys", "mapa X") == "resposta 1"
    assert inner.calls == 1


@pytest.mark.unit
def test_prompt_diferente_chama_o_provedor_de_novo():
    inner = FakeProvider()
    provider = CachedAIProvider(inner, MemoryStore(), timedelta(days=1))
    provider.generate_text("sys", "mapa X")
    provider.generate_text("sys", "mapa Y")
    assert inner.calls == 2


@pytest.mark.unit
def test_falha_do_cache_nao_derruba_a_requisicao():
    inner = FakeProvider()
    provider = CachedAIProvider(inner, BrokenStore(), timedelta(days=1))
    assert provider.generate_text("sys", "mapa X") == "resposta 1"


@pytest.mark.unit
def test_chave_muda_com_parametros():
    base = build_cache_key("p", "s", "u", 0.7, 2000, {})
    assert base == build_cache_key("p", "s", "u", 0.7, 2000, {})
    assert base != build_cache_key("p", "s", "u", 0.2, 2000, {})
    assert base != build_cache_key("outro", "s", "u", 0.7, 2000, {})


@pytest.mark.unit
def test_store_sqlalchemy_persiste_e_respeita_ttl():
    store = SqlAlchemyCacheStore()
    store.set("k" * 64, "fake", "texto")
    assert store.get("k" * 64, timedelta(days=1)) == "texto"
    assert store.get("k" * 64, timedelta(seconds=-1)) is None
    assert store.get("z" * 64, timedelta(days=1)) is None

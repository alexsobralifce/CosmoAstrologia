"""Rate limit em memória, por chave, com janela deslizante.

Vale por processo: com vários workers/instâncias o limite efetivo é multiplicado.
Para limite global, trocar `SlidingWindowLimiter` por uma versão com Redis mantendo a interface.
"""
import threading
import time
from collections import defaultdict, deque


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int):
        super().__init__(f"limite excedido; tente em {retry_after}s")
        self.retry_after = retry_after


class SlidingWindowLimiter:
    def __init__(self, max_calls: int, window_seconds: float = 60.0, clock=time.monotonic):
        self._max_calls = max_calls
        self._window = window_seconds
        self._clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> None:
        """Registra uma chamada para `key`; levanta RateLimitExceeded se passou do limite."""
        now = self._clock()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= self._window:
                hits.popleft()
            if len(hits) >= self._max_calls:
                raise RateLimitExceeded(retry_after=max(1, int(self._window - (now - hits[0])) + 1))
            hits.append(now)

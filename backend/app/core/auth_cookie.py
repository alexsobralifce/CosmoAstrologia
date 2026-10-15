"""Cookie httpOnly do token de login.

O JavaScript da página não consegue ler o cookie (some o risco de roubo por XSS). O backend continua
aceitando `Authorization: Bearer`, e este middleware traduz o cookie para esse cabeçalho, de modo
que nenhuma rota precisa saber da diferença.

Para o navegador enviar o cookie, front e API precisam ficar no mesmo site (por exemplo,
via proxy do Next em /api); com SameSite=Lax ele não viaja entre sites diferentes.
"""
import os

from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings

COOKIE_NAME = "auth_token"
_MAX_AGE_SECONDS = 30 * 24 * 3600


def _secure() -> bool:
    if settings.COOKIE_SECURE is not None:
        return settings.COOKIE_SECURE
    return bool(os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PRODUCTION") == "true")


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        COOKIE_NAME, token, max_age=_MAX_AGE_SECONDS, httponly=True,
        samesite="lax", secure=_secure(), path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, samesite="lax", secure=_secure())


class CookieToBearerMiddleware:
    """Sem cabeçalho Authorization, usa o token do cookie como `Bearer`."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = list(scope["headers"])
            has_auth = any(k == b"authorization" for k, _ in headers)
            if not has_auth:
                token = self._cookie_token(headers)
                if token:
                    headers.append((b"authorization", f"Bearer {token}".encode()))
                    scope = {**scope, "headers": headers}
        await self.app(scope, receive, send)

    @staticmethod
    def _cookie_token(headers) -> str | None:
        for key, value in headers:
            if key == b"cookie":
                for part in value.decode("latin-1").split(";"):
                    name, _, val = part.strip().partition("=")
                    if name == COOKIE_NAME and val:
                        return val
        return None

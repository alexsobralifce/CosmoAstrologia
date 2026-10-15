"""Dependências FastAPI compartilhadas pelas rotas (autenticação e rate limit)."""
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import RateLimitExceeded, SlidingWindowLimiter
from app.models.database import User

_llm_limiter = SlidingWindowLimiter(max_calls=settings.LLM_RATE_LIMIT_PER_MINUTE)


def require_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Exige usuário autenticado; 401 caso contrário."""
    user = get_current_user(authorization, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def llm_rate_limit(user: User = Depends(require_user)) -> None:
    """Limita chamadas a rotas que consomem LLM, por usuário."""
    try:
        _llm_limiter.check(str(user.id))
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas requisições. Aguarde um instante e tente novamente.",
            headers={"Retry-After": str(exc.retry_after)},
        )

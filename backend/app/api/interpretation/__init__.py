"""Rotas de interpretação, divididas por tema. `router` agrega todas.

Política de acesso (centralizada aqui, não em cada rota):
- todas exigem usuário autenticado, exceto `daily` (autenticação opcional);
- as que chamam LLM também têm rate limit por usuário.
"""
from fastapi import APIRouter, Depends

from app.api.dependencies import llm_rate_limit, require_user
from app.api.interpretation.best_timing import router as best_timing_router
from app.api.interpretation.birth_chart import router as birth_chart_router
from app.api.interpretation.birth_chart_prompts import _get_master_prompt  # noqa: F401 (compatibilidade)
from app.api.interpretation.complete_chart import router as complete_chart_router
from app.api.interpretation.daily import router as daily_router
from app.api.interpretation.numerology import router as numerology_router
from app.api.interpretation.planets import router as planets_router
from app.api.interpretation.solar_return import router as solar_return_router
from app.api.interpretation.synastry import router as synastry_router
from app.api.interpretation.transits import router as transits_router

router = APIRouter()

# Rotas públicas (autenticação opcional dentro da própria rota)
router.include_router(daily_router)

# Rotas autenticadas sem LLM
for _r in (best_timing_router, transits_router):
    router.include_router(_r, dependencies=[Depends(require_user)])

# Rotas autenticadas que chamam LLM em todos os endpoints
for _r in (planets_router, complete_chart_router, birth_chart_router, synastry_router):
    router.include_router(_r, dependencies=[Depends(require_user), Depends(llm_rate_limit)])

# Módulos mistos: o rate limit de LLM é aplicado por rota (ver `dependencies=` nos decoradores)
for _r in (solar_return_router, numerology_router):
    router.include_router(_r, dependencies=[Depends(require_user)])

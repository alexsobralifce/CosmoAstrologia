"""Rotas de interpretação, divididas por tema. `router` agrega todas."""
from fastapi import APIRouter

from app.api.interpretation.daily import router as daily_router
from app.api.interpretation.planets import router as planets_router
from app.api.interpretation.complete_chart import router as complete_chart_router
from app.api.interpretation.transits import router as transits_router
from app.api.interpretation.best_timing import router as best_timing_router
from app.api.interpretation.solar_return import router as solar_return_router
from app.api.interpretation.numerology import router as numerology_router
from app.api.interpretation.birth_chart import router as birth_chart_router
from app.api.interpretation.synastry import router as synastry_router
from app.api.interpretation.birth_chart_prompts import _get_master_prompt  # noqa: F401 (compatibilidade)

router = APIRouter()
router.include_router(daily_router)
router.include_router(planets_router)
router.include_router(complete_chart_router)
router.include_router(transits_router)
router.include_router(best_timing_router)
router.include_router(solar_return_router)
router.include_router(numerology_router)
router.include_router(birth_chart_router)
router.include_router(synastry_router)

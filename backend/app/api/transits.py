"""
API endpoints for astrological transits
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.schemas import BirthChartResponse, DailyTransit, FutureTransit
from app.services.transit_service import transit_service

router = APIRouter()

@router.post("/daily", response_model=DailyTransit)
async def get_daily_transits(
    chart: BirthChartResponse,
    date: str = None
):
    """
    Get daily transits for a given date (or today if not specified)
    """
    try:
        target_date = None
        if date:
            target_date = datetime.fromisoformat(date)
        
        # Convert chart to dict format expected by service
        chart_dict = {
            "houses": [
                {
                    "cusp_degree": h.cusp_degree,
                    "number": h.number
                }
                for h in chart.houses
            ],
            "planets": [
                {
                    "planet": p.planet,
                    "longitude": p.degree + (p.minutes / 60.0)  # Approximate
                }
                for p in chart.planets
            ],
            "birth_data": {
                "birth_date": chart.birth_data.birth_date,
                "birth_time": chart.birth_data.birth_time
            }
        }
        
        transit_data = transit_service.get_daily_transits(chart_dict, target_date)
        
        return DailyTransit(**transit_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting daily transits: {str(e)}")

@router.post("/future", response_model=list[FutureTransit])
async def get_future_transits(
    chart: BirthChartResponse,
    months_ahead: int = 24
):
    """
    Get future important transits
    """
    try:
        # Convert chart to dict format
        chart_dict = {
            "houses": [
                {
                    "cusp_degree": h.cusp_degree,
                    "number": h.number
                }
                for h in chart.houses
            ],
            "planets": [
                {
                    "planet": p.planet,
                    "longitude": p.degree + (p.minutes / 60.0),  # Approximate
                    "sign": p.sign,
                    "house": p.house
                }
                for p in chart.planets
            ],
            "birth_data": {
                "birth_date": chart.birth_data.birth_date,
                "birth_time": chart.birth_data.birth_time
            }
        }
        
        transits = transit_service.get_future_transits(chart_dict, months_ahead)
        
        return [FutureTransit(**t) for t in transits]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting future transits: {str(e)}")


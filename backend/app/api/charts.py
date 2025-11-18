"""
API endpoints for birth chart calculations and storage
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.schemas import (
    BirthData, 
    BirthChartResponse,
    PlanetPosition,
    House,
    Aspect,
    BigThree
)
from app.models.database import User, BirthChart as BirthChartDB
from app.services.astrology_calculator import AstrologyCalculator
from app.api.auth import get_current_user
from app.core.database import get_db
from datetime import datetime
import json

router = APIRouter()
calculator = AstrologyCalculator()

@router.post("/calculate", response_model=BirthChartResponse)
async def calculate_chart(birth_data: BirthData):
    """
    Calculate complete birth chart from birth data
    """
    try:
        # Calculate chart
        chart_data = calculator.calculate_chart(
            birth_data.birth_date,
            birth_data.birth_time,
            birth_data.birth_place
        )
        
        # Convert to response format
        planets = [
            PlanetPosition(
                planet=p['planet'],
                sign=p['sign'],
                house=p['house'],
                degree=p['degree'],
                minutes=p['minutes']
            )
            for p in chart_data['planets']
        ]
        
        houses = [
            House(
                number=h.number,
                cusp_sign=h.cusp_sign,
                cusp_degree=h.cusp_degree,
                planets_in_house=h.planets_in_house
            )
            for h in chart_data['houses']
        ]
        
        aspects = [
            Aspect(
                planet1=a['planet1'],
                planet2=a['planet2'],
                type=a['type'],
                orb=a['orb'],
                is_positive=a['is_positive']
            )
            for a in chart_data['aspects']
        ]
        
        big_three = BigThree(**chart_data['big_three'])
        chart_ruler = chart_data['chart_ruler']
        
        return BirthChartResponse(
            birth_data=birth_data,
            big_three=big_three,
            planets=planets,
            houses=houses,
            aspects=aspects,
            elements=chart_data['elements'],
            modalities=chart_data['modalities'],
            chart_ruler=chart_ruler
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating chart: {str(e)}")

@router.post("/save", response_model=dict)
async def save_chart(
    chart: BirthChartResponse,
    is_primary: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a calculated birth chart to database
    """
    try:
        # If this is set as primary, unset other primary charts for this user
        if is_primary:
            db.query(BirthChartDB).filter(
                BirthChartDB.user_id == current_user.id,
                BirthChartDB.is_primary == True
            ).update({"is_primary": False})
        
        # Create chart record
        chart_db = BirthChartDB(
            user_id=current_user.id,
            name=chart.birth_data.name,
            birth_date=chart.birth_data.birth_date,
            birth_time=chart.birth_data.birth_time,
            birth_place=chart.birth_data.birth_place,
            sun_sign=chart.big_three.sun,
            moon_sign=chart.big_three.moon,
            ascendant_sign=chart.big_three.ascendant,
            chart_data=chart.model_dump(),  # Store full chart as JSON
            is_primary=is_primary
        )
        
        db.add(chart_db)
        db.commit()
        db.refresh(chart_db)
        
        return {
            "message": "Chart saved successfully",
            "chart_id": chart_db.id,
            "is_primary": chart_db.is_primary
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving chart: {str(e)}")

@router.get("/", response_model=List[dict])
async def get_user_charts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all saved charts for current user
    """
    charts = db.query(BirthChartDB).filter(
        BirthChartDB.user_id == current_user.id
    ).order_by(BirthChartDB.is_primary.desc(), BirthChartDB.created_at.desc()).all()
    
    return [
        {
            "id": chart.id,
            "name": chart.name,
            "birth_date": chart.birth_date,
            "birth_time": chart.birth_time,
            "birth_place": chart.birth_place,
            "sun_sign": chart.sun_sign,
            "moon_sign": chart.moon_sign,
            "ascendant_sign": chart.ascendant_sign,
            "is_primary": chart.is_primary,
            "created_at": chart.created_at.isoformat() if chart.created_at else None
        }
        for chart in charts
    ]

@router.get("/{chart_id}", response_model=BirthChartResponse)
async def get_chart(
    chart_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific saved chart by ID
    """
    chart = db.query(BirthChartDB).filter(
        BirthChartDB.id == chart_id,
        BirthChartDB.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    # Reconstruct BirthChartResponse from stored JSON
    chart_data = chart.chart_data
    return BirthChartResponse(**chart_data)

@router.put("/{chart_id}/primary")
async def set_primary_chart(
    chart_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set a chart as primary for the user
    """
    chart = db.query(BirthChartDB).filter(
        BirthChartDB.id == chart_id,
        BirthChartDB.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    # Unset other primary charts
    db.query(BirthChartDB).filter(
        BirthChartDB.user_id == current_user.id,
        BirthChartDB.is_primary == True
    ).update({"is_primary": False})
    
    # Set this chart as primary
    chart.is_primary = True
    db.commit()
    
    return {"message": "Primary chart updated", "chart_id": chart_id}

@router.delete("/{chart_id}")
async def delete_chart(
    chart_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a saved chart
    """
    chart = db.query(BirthChartDB).filter(
        BirthChartDB.id == chart_id,
        BirthChartDB.user_id == current_user.id
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    db.delete(chart)
    db.commit()
    
    return {"message": "Chart deleted successfully", "chart_id": chart_id}

@router.get("/primary/current", response_model=BirthChartResponse)
async def get_primary_chart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's primary chart
    """
    chart = db.query(BirthChartDB).filter(
        BirthChartDB.user_id == current_user.id,
        BirthChartDB.is_primary == True
    ).first()
    
    if not chart:
        raise HTTPException(status_code=404, detail="No primary chart found")
    
    # Reconstruct BirthChartResponse from stored JSON
    chart_data = chart.chart_data
    return BirthChartResponse(**chart_data)

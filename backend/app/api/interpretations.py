"""
API endpoints for astrological interpretations using RAG
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    BirthChartResponse,
    PlanetInterpretation,
    HouseInterpretation,
    AspectInterpretation,
    InterpretationRequest,
    InterpretationResponse
)
from app.services.rag_service import rag_service

router = APIRouter()

@router.post("/planet/{planet_name}", response_model=PlanetInterpretation)
async def get_planet_interpretation(
    planet_name: str,
    sign: str,
    house: int,
    chart: BirthChartResponse
):
    """
    Get interpretation for a planet in a sign and house
    """
    try:
        chart_context = {
            "big_three": {
                "sun": chart.big_three.sun,
                "moon": chart.big_three.moon,
                "ascendant": chart.big_three.ascendant
            }
        }
        
        interpretation = rag_service.get_planet_interpretation(
            planet_name, sign, house, chart_context
        )
        
        return PlanetInterpretation(
            planet=planet_name,
            sign=sign,
            house=house,
            in_sign=interpretation["in_sign"],
            in_house=interpretation["in_house"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting interpretation: {str(e)}")

@router.post("/house/{house_number}", response_model=HouseInterpretation)
async def get_house_interpretation(
    house_number: int,
    chart: BirthChartResponse
):
    """
    Get interpretation for a house
    """
    try:
        house_data = next((h for h in chart.houses if h.number == house_number), None)
        if not house_data:
            raise HTTPException(status_code=404, detail=f"House {house_number} not found")
        
        chart_context = {
            "big_three": {
                "sun": chart.big_three.sun,
                "moon": chart.big_three.moon,
                "ascendant": chart.big_three.ascendant
            }
        }
        
        interpretation = rag_service.get_house_interpretation(
            house_number,
            house_data.cusp_sign,
            house_data.planets_in_house,
            chart_context
        )
        
        # Get theme based on house number
        themes = {
            1: "Identidade e Aparência",
            2: "Valores e Recursos",
            3: "Comunicação e Aprendizado",
            4: "Lar, Raízes e Família",
            5: "Criatividade e Romance",
            6: "Rotina e Saúde",
            7: "Parcerias e Relacionamentos",
            8: "Transformação e Recursos Compartilhados",
            9: "Filosofia e Viagens",
            10: "Carreira e Reputação",
            11: "Amizades e Grupos",
            12: "Espiritualidade e Inconsciente"
        }
        
        return HouseInterpretation(
            house_number=house_number,
            theme=themes.get(house_number, f"Casa {house_number}"),
            interpretation=interpretation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting interpretation: {str(e)}")

@router.post("/aspect", response_model=AspectInterpretation)
async def get_aspect_interpretation(
    planet1: str,
    planet2: str,
    aspect_type: str,
    orb: float,
    chart: BirthChartResponse
):
    """
    Get interpretation for an aspect
    """
    try:
        chart_context = {
            "big_three": {
                "sun": chart.big_three.sun,
                "moon": chart.big_three.moon,
                "ascendant": chart.big_three.ascendant
            }
        }
        
        result = rag_service.get_aspect_interpretation(
            planet1, planet2, aspect_type, orb, chart_context
        )
        
        from app.models.schemas import Aspect
        aspect = Aspect(
            planet1=planet1,
            planet2=planet2,
            type=aspect_type,
            orb=orb,
            is_positive=aspect_type in ["trine", "sextile", "conjunction"]
        )
        
        return AspectInterpretation(
            aspect=aspect,
            interpretation=result["interpretation"],
            tags=result["tags"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting interpretation: {str(e)}")

@router.post("/chart-ruler", response_model=dict)
async def get_chart_ruler_interpretation(chart: BirthChartResponse):
    """
    Get interpretation for chart ruler
    """
    try:
        chart_context = {
            "big_three": {
                "sun": chart.big_three.sun,
                "moon": chart.big_three.moon,
                "ascendant": chart.big_three.ascendant
            }
        }
        
        ruler = chart.chart_ruler
        interpretation = rag_service.get_chart_ruler_interpretation(
            ruler.ascendant,
            ruler.ruler,
            ruler.ruler_sign,
            ruler.ruler_house,
            chart_context
        )
        
        return interpretation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting interpretation: {str(e)}")

@router.post("/custom", response_model=InterpretationResponse)
async def get_custom_interpretation(request: InterpretationRequest):
    """
    Get custom interpretation for any topic
    """
    try:
        chart_context = {
            "big_three": {
                "sun": request.chart.big_three.sun,
                "moon": request.chart.big_three.moon,
                "ascendant": request.chart.big_three.ascendant
            }
        }
        
        interpretation_text = rag_service.get_interpretation(request.topic, chart_context)
        
        # Split into sections (simple parsing - could be improved)
        sections = []
        paragraphs = interpretation_text.split('\n\n')
        current_heading = None
        current_content = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if it's a heading (short line, might be bold in markdown)
            if len(para) < 100 and para.count('\n') == 0:
                if current_heading:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n\n".join(current_content)
                    })
                current_heading = para.replace('#', '').strip()
                current_content = []
            else:
                current_content.append(para)
        
        if current_heading or current_content:
            sections.append({
                "heading": current_heading or "Interpretação",
                "content": "\n\n".join(current_content) if current_content else interpretation_text
            })
        
        if not sections:
            sections = [{
                "heading": "Interpretação",
                "content": interpretation_text
            }]
        
        return InterpretationResponse(
            title=request.topic,
            content=sections
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting interpretation: {str(e)}")


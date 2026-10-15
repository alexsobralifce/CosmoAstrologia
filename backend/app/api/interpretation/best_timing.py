from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.database import BirthChart


router = APIRouter()


# ============================================================================
# AGENDA DE MELHORES MOMENTOS - Endpoints
# ============================================================================

class BestTimingRequest(BaseModel):
    """Request para cálculo de melhores momentos."""
    action_type: str  # Ex: 'pedir_aumento', 'assinar_contrato', 'primeiro_encontro'
    days_ahead: int = 30  # Quantos dias à frente calcular



@router.post("/best-timing/calculate")
async def calculate_best_timing(
    request: BestTimingRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Calcula os melhores momentos para uma ação específica baseado em aspectos e casas astrológicas.
    
    IMPORTANTE:
    - Todos os cálculos são feitos pela biblioteca local (Swiss Ephemeris)
    - A IA apenas organiza e contextualiza os dados calculados, NUNCA inventa momentos
    - Retorna apenas momentos reais calculados matematicamente
    
    Args:
        request: Tipo de ação e parâmetros
        authorization: Token JWT do usuário autenticado
    
    Returns:
        Lista de melhores momentos com scores e aspectos
    """
    try:
        # Obter usuário autenticado
        from app.api.auth import get_current_user
        current_user = get_current_user(authorization, db)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Não autenticado"
            )
        
        # Obter mapa astral primário do usuário
        birth_chart = db.query(BirthChart).filter(
            BirthChart.user_id == current_user.id,
            BirthChart.is_primary == True
        ).first()
        
        if not birth_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapa astral não encontrado. Por favor, registre seu mapa astral primeiro."
            )
        
        # Importar calculador
        from app.services.best_timing_calculator import calculate_best_timing
        
        # Calcular melhores momentos usando biblioteca local
        result = calculate_best_timing(
            action_type=request.action_type,
            birth_date=birth_chart.birth_date,
            birth_time=birth_chart.birth_time,
            latitude=birth_chart.latitude,
            longitude=birth_chart.longitude,
            days_ahead=min(request.days_ahead, 90)  # Máximo 90 dias
        )
        
        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )
        
        # VALIDAÇÃO FINAL: Garantir que best_moments é uma lista válida
        if 'best_moments' not in result:
            result['best_moments'] = []
        elif not isinstance(result['best_moments'], list):
            result['best_moments'] = []
        
        # Garantir que todos os momentos retornados são válidos
        validated_moments = []
        for moment in result.get('best_moments', []):
            if (isinstance(moment, dict) and 
                'date' in moment and 
                'score' in moment and 
                'aspects' in moment and
                isinstance(moment.get('aspects'), list) and
                len(moment.get('aspects', [])) > 0):
                validated_moments.append(moment)
        
        result['best_moments'] = validated_moments
        result['total_valid'] = len(validated_moments)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular melhores momentos: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular melhores momentos: {str(e)}"
        )

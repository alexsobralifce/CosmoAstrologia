from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.database import BirthChart


router = APIRouter()


# ============================================================================
# INFORMAÇÕES DO DIA ATUAL - Endpoint
# ============================================================================

@router.get("/daily-info")
async def get_daily_info(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Retorna informações astrológicas do dia atual:
    - Data formatada
    - Fase lunar
    - Signo da Lua
    
    Todos os cálculos são feitos usando Swiss Ephemeris (biblioteca padrão).
    """
    try:
        from app.services.daily_info_calculator import get_daily_info
        
        # Tentar obter coordenadas do usuário autenticado
        user_lat = latitude
        user_lon = longitude
        
        if authorization:
            try:
                from app.api.auth import get_current_user
                current_user = get_current_user(authorization, db)
                if current_user:
                    # Tentar obter coordenadas do mapa astral
                    birth_chart = db.query(BirthChart).filter(
                        BirthChart.user_id == current_user.id,
                        BirthChart.is_primary == True
                    ).first()
                    
                    if birth_chart:
                        user_lat = birth_chart.latitude
                        user_lon = birth_chart.longitude
            except:
                pass  # Se não conseguir autenticar, usar coordenadas padrão
        
        # Usar coordenadas padrão (São Paulo) se não fornecidas
        if user_lat is None or user_lon is None:
            user_lat = -23.5505
            user_lon = -46.6333
        
        # Calcular informações do dia
        daily_info = get_daily_info(
            latitude=user_lat,
            longitude=user_lon
        )
        
        return daily_info
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular informações do dia: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular informações do dia: {str(e)}"
        )

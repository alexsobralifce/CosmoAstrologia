from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.database import BirthChart


router = APIRouter()


@router.get("/transits/future")
async def get_future_transits(
    months_ahead: int = 24,
    max_transits: int = 10,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Calcula trânsitos futuros baseados no mapa astral do usuário.
    
    IMPORTANTE: 
    - Todos os cálculos são feitos pela biblioteca local (Swiss Ephemeris via kerykeion)
    - A IA apenas interpreta os dados calculados, NUNCA inventa trânsitos
    - Retorna apenas trânsitos reais calculados matematicamente
    
    Args:
        months_ahead: Quantos meses à frente calcular (padrão: 24, mínimo: 6, máximo: 60)
        max_transits: Número máximo de trânsitos a retornar (padrão: 10, mínimo: 5, máximo: 20)
        authorization: Token JWT do usuário autenticado
    
    Returns:
        Lista de trânsitos futuros ordenados por data, com interpretações geradas pela IA
    """
    try:
        # Validar parâmetros
        months_ahead = max(6, min(60, months_ahead))
        max_transits = max(5, min(20, max_transits))
        
        # Obter usuário autenticado (importação local para evitar circular)
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
        
        # Importar calculador de trânsitos
        from app.services.transits_calculator import calculate_future_transits
        
        # Calcular trânsitos usando biblioteca local (NÃO IA)
        # GARANTIA: Todos os cálculos são matemáticos, usando Swiss Ephemeris
        transits = calculate_future_transits(
            birth_date=birth_chart.birth_date,
            birth_time=birth_chart.birth_time,
            latitude=birth_chart.latitude,
            longitude=birth_chart.longitude,
            months_ahead=months_ahead,
            max_transits=max_transits
        )
        
        # FILTRAR TRANSTOS PASSADOS - Apenas transitos válidos (futuros/atuais)
        # Um trânsito é válido se end_date >= hoje (ainda não terminou)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        valid_transits = []
        
        for transit in transits:
            try:
                # Parsear end_date do trânsito
                end_date_str = transit.get('end_date', '')
                if end_date_str:
                    # Parsear ISO format string
                    if isinstance(end_date_str, str):
                        # Remover timezone e extrair apenas data
                        if 'T' in end_date_str:
                            date_part = end_date_str.split('T')[0]
                            end_date = datetime.strptime(date_part, '%Y-%m-%d')
                        else:
                            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    elif isinstance(end_date_str, datetime):
                        end_date = end_date_str.replace(hour=0, minute=0, second=0, microsecond=0)
                    else:
                        continue  # Formato desconhecido, pular
                    
                    # Filtrar: apenas transitos que ainda não terminaram
                    if end_date >= today:
                        valid_transits.append(transit)
                    else:
                        print(f"[TRANSITS] Removendo trânsito passado: {transit.get('title', 'N/A')} (end_date: {end_date_str})")
                else:
                    # Se não tem end_date, verificar start_date
                    start_date_str = transit.get('start_date', transit.get('date', ''))
                    if start_date_str:
                        # Parsear ISO format string
                        if isinstance(start_date_str, str):
                            # Remover timezone e extrair apenas data
                            if 'T' in start_date_str:
                                date_part = start_date_str.split('T')[0]
                                start_date = datetime.strptime(date_part, '%Y-%m-%d')
                            else:
                                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                        elif isinstance(start_date_str, datetime):
                            start_date = start_date_str.replace(hour=0, minute=0, second=0, microsecond=0)
                        else:
                            continue  # Formato desconhecido, pular
                        
                        # Se start_date >= hoje, incluir (trânsito futuro)
                        if start_date >= today:
                            valid_transits.append(transit)
                        else:
                            print(f"[TRANSITS] Removendo trânsito passado: {transit.get('title', 'N/A')} (start_date: {start_date_str})")
                    else:
                        # Se não tem nenhuma data, não incluir
                        print(f"[TRANSITS] Removendo trânsito sem data: {transit.get('title', 'N/A')}")
            except (ValueError, TypeError) as e:
                print(f"[WARNING] Erro ao processar data do trânsito {transit.get('title', 'N/A')}: {e}")
                # Em caso de erro, não incluir o trânsito (segurança)
                continue
        
        print(f"[TRANSITS] Total calculado: {len(transits)}, Válidos (não passados): {len(valid_transits)}")
        
        # Formatar trânsitos válidos para o frontend
        formatted_transits = []
        for transit in valid_transits:
            # Mapear tipo de aspecto para display
            aspect_type_display_map = {
                'conjunção': 'Conjunção',
                'oposição': 'Oposição',
                'quadratura': 'Quadratura',
                'trígono': 'Trígono',
                'sextil': 'Sextil'
            }
            
            aspect_type_display = aspect_type_display_map.get(
                transit.get('aspect_type', ''), 
                transit.get('aspect_type', 'Aspecto')
            )
            
            # Determinar tipo de trânsito para o frontend
            transit_type = transit.get('transit_type', 'jupiter')
            if transit_type == 'saturn-return':
                transit_type_frontend = 'saturn-return'
            elif transit.get('planet') == 'Júpiter':
                transit_type_frontend = 'jupiter'
            elif transit.get('planet') == 'Urano':
                transit_type_frontend = 'uranus'
            elif transit.get('planet') == 'Netuno':
                transit_type_frontend = 'neptune'
            elif transit.get('planet') == 'Plutão':
                transit_type_frontend = 'pluto'
            else:
                transit_type_frontend = 'jupiter'  # Default
            
            # Criar ID único
            transit_id = f"{transit.get('planet', '')}_{transit.get('aspect_type', '')}_{transit.get('natal_point', '')}_{transit.get('date', '')}"
            
            formatted_transits.append({
                'id': transit_id,
                'type': transit_type_frontend,
                'title': transit.get('title', 'Trânsito'),
                'planet': transit.get('planet', ''),
                'timeframe': f"{transit.get('start_date', '')} - {transit.get('end_date', '')}",
                'description': transit.get('description', ''),
                'isActive': transit.get('is_active', False),
                'date': transit.get('date', ''),
                'start_date': transit.get('start_date', ''),
                'end_date': transit.get('end_date', ''),
                'aspect_type': transit.get('aspect_type', ''),
                'aspect_type_display': aspect_type_display,
                'natal_point': transit.get('natal_point', '')
            })
        
        return {
            "transits": formatted_transits,
            "count": len(formatted_transits)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular trânsitos: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular trânsitos: {str(e)}"
        )



# ============================================================================
# TRÂNSITOS PESSOAIS EM TEMPO REAL - Endpoints
# ============================================================================

@router.get("/transits/current")
async def get_current_personal_transits(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Calcula trânsitos pessoais em tempo real (hoje/agora) baseados no mapa astral do usuário.
    
    IMPORTANTE: 
    - Todos os cálculos são feitos pela biblioteca local (Swiss Ephemeris)
    - A IA apenas interpreta os dados calculados, NUNCA inventa trânsitos
    - Retorna apenas trânsitos reais calculados matematicamente para HOJE
    
    Args:
        authorization: Token JWT do usuário autenticado
    
    Returns:
        Dicionário com trânsitos atuais e Lua Fora de Curso
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
        
        # Importar calculadores
        from app.services.transits_calculator import calculate_future_transits
        from app.services.moon_void_calculator import calculate_moon_void_of_course
        
        # Calcular trânsitos para hoje (apenas 1 dia à frente para pegar trânsitos ativos)
        today_transits = calculate_future_transits(
            birth_date=birth_chart.birth_date,
            birth_time=birth_chart.birth_time,
            latitude=birth_chart.latitude,
            longitude=birth_chart.longitude,
            months_ahead=1,  # Apenas 1 mês para pegar trânsitos ativos
            max_transits=20  # Mais trânsitos para filtrar os ativos
        )
        
        # Filtrar apenas trânsitos ATIVOS (que estão acontecendo hoje)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        active_transits = []
        
        for transit in today_transits:
            try:
                start_date_str = transit.get('start_date', '')
                end_date_str = transit.get('end_date', '')
                
                if start_date_str and end_date_str:
                    # Parsear datas
                    if isinstance(start_date_str, str):
                        if 'T' in start_date_str:
                            date_part = start_date_str.split('T')[0]
                            start_date = datetime.strptime(date_part, '%Y-%m-%d')
                        else:
                            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    else:
                        start_date = start_date_str.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    if isinstance(end_date_str, str):
                        if 'T' in end_date_str:
                            date_part = end_date_str.split('T')[0]
                            end_date = datetime.strptime(date_part, '%Y-%m-%d')
                        else:
                            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                    else:
                        end_date = end_date_str.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    # Trânsito ativo se hoje está entre start_date e end_date
                    if start_date <= today <= end_date:
                        active_transits.append(transit)
            except Exception as e:
                print(f"[WARNING] Erro ao processar trânsito para hoje: {e}")
                continue
        
        # Calcular Lua Fora de Curso
        moon_void = calculate_moon_void_of_course(
            check_date=datetime.now(),
            latitude=birth_chart.latitude,
            longitude=birth_chart.longitude
        )
        
        # Formatar trânsitos ativos
        formatted_active_transits = []
        for transit in active_transits:
            aspect_type_display_map = {
                'conjunção': 'Conjunção',
                'oposição': 'Oposição',
                'quadratura': 'Quadratura',
                'trígono': 'Trígono',
                'sextil': 'Sextil'
            }
            
            aspect_type_display = aspect_type_display_map.get(
                transit.get('aspect_type', ''), 
                transit.get('aspect_type', 'Aspecto')
            )
            
            transit_type = transit.get('transit_type', 'jupiter')
            if transit.get('planet') == 'Júpiter':
                transit_type_frontend = 'jupiter'
            elif transit.get('planet') == 'Urano':
                transit_type_frontend = 'uranus'
            elif transit.get('planet') == 'Netuno':
                transit_type_frontend = 'neptune'
            elif transit.get('planet') == 'Plutão':
                transit_type_frontend = 'pluto'
            elif transit_type == 'saturn-return':
                transit_type_frontend = 'saturn-return'
            else:
                transit_type_frontend = 'jupiter'
            
            transit_id = f"{transit.get('planet', '')}_{transit.get('aspect_type', '')}_{transit.get('natal_point', '')}_{transit.get('date', '')}"
            
            formatted_active_transits.append({
                'id': transit_id,
                'type': transit_type_frontend,
                'title': transit.get('title', 'Trânsito'),
                'planet': transit.get('planet', ''),
                'description': transit.get('description', ''),
                'isActive': True,
                'start_date': transit.get('start_date', ''),
                'end_date': transit.get('end_date', ''),
                'aspect_type': transit.get('aspect_type', ''),
                'aspect_type_display': aspect_type_display,
                'natal_point': transit.get('natal_point', '')
            })
        
        # Formatar Lua Fora de Curso
        void_info = {
            'is_void': moon_void.get('is_void', False),
            'void_end': moon_void.get('void_end').isoformat() if moon_void.get('void_end') else None,
            'void_start': moon_void.get('void_start').isoformat() if moon_void.get('void_start') else None,
            'next_aspect': moon_void.get('next_aspect', ''),
            'next_aspect_time': moon_void.get('next_aspect_time').isoformat() if moon_void.get('next_aspect_time') else None,
            'current_moon_sign': moon_void.get('current_moon_sign', ''),
            'void_duration_hours': moon_void.get('void_duration_hours')
        }
        
        return {
            "active_transits": formatted_active_transits,
            "moon_void_of_course": void_info,
            "date": datetime.now().isoformat(),
            "count": len(formatted_active_transits)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular trânsitos atuais: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular trânsitos atuais: {str(e)}"
        )

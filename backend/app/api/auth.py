from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime
import bcrypt
from typing import Optional
from app.core.database import get_db
from app.models.database import User, BirthChart
from app.models.schemas import (
    UserRegister, UserResponse, BirthChartResponse, Token, UserCreate, UserUpdateRequest, UserLogin
)
from app.services.astrology_calculator import calculate_birth_chart
from jose import JWTError, jwt
from app.core.config import settings

router = APIRouter()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict):
    """Create a JWT access token."""
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from JWT token."""
    if not authorization:
        return None
    
    try:
        # Extrair token do header "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.email == email).first()
    return user


@router.post("/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registra um novo usuário e calcula seu mapa astral.
    """
    try:
        # Verificar se o usuário já existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Hash da senha (se fornecida)
        password_hash = None
        if user_data.password:
            password_hash = hash_password(user_data.password)
            print(f"[DEBUG] Senha fornecida, hash criado: {password_hash[:20]}...")
        else:
            print("[DEBUG] Nenhuma senha fornecida no registro")
        
        # Calcular signos astrológicos
        birth_data = user_data.birth_data
        print(f"[DEBUG] Calculando mapa astral para: {birth_data.birth_date}, {birth_data.birth_time}, lat: {birth_data.latitude}, lon: {birth_data.longitude}")
        
        try:
            chart_data = calculate_birth_chart(
                birth_date=birth_data.birth_date,
                birth_time=birth_data.birth_time,
                latitude=birth_data.latitude,
                longitude=birth_data.longitude
            )
            print(f"[DEBUG] Mapa astral calculado: {chart_data}")
        except Exception as e:
            import traceback
            print(f"[ERROR] Erro ao calcular mapa astral: {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao calcular mapa astral: {str(e)}"
            )
    
        # Criar usuário
        db_user = User(
            email=user_data.email,
            password_hash=password_hash,
            name=user_data.name
        )
        db.add(db_user)
        db.flush()  # Para obter o ID do usuário
        
        # Verificar se a senha foi salva
        print(f"[DEBUG] Usuário criado - Email: {db_user.email}, Password hash: {'Sim' if db_user.password_hash else 'Não'}")
        
        # Criar mapa astral
        db_birth_chart = BirthChart(
            user_id=db_user.id,
            name=birth_data.name,
            birth_date=birth_data.birth_date,
            birth_time=birth_data.birth_time,
            birth_place=birth_data.birth_place,
            latitude=birth_data.latitude,
            longitude=birth_data.longitude,
            sun_sign=chart_data["sun_sign"],
            moon_sign=chart_data["moon_sign"],
            ascendant_sign=chart_data["ascendant_sign"],
            sun_degree=chart_data.get("sun_degree"),
            moon_degree=chart_data.get("moon_degree"),
            ascendant_degree=chart_data.get("ascendant_degree"),
            is_primary=True
        )
        db.add(db_birth_chart)
        db.commit()
        db.refresh(db_user)
        db.refresh(db_birth_chart)
        
        # Criar token JWT
        access_token = create_access_token(data={"sub": db_user.email})
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro geral no registro: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um token JWT.
    """
    # Buscar usuário pelo email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Verificar senha
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )
    
    # Criar token JWT
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Retorna informações do usuário atual."""
    current_user = get_current_user(authorization, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    return current_user


@router.get("/birth-chart", response_model=BirthChartResponse)
def get_user_birth_chart(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Retorna o mapa astral primário do usuário, recalculando se necessário."""
    current_user = get_current_user(authorization, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    
    birth_chart = db.query(BirthChart).filter(
        BirthChart.user_id == current_user.id,
        BirthChart.is_primary == True
    ).first()
    
    if not birth_chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapa astral não encontrado"
        )
    
    # Recalcular o mapa astral para garantir que está usando as fórmulas mais recentes
    try:
        chart_data = calculate_birth_chart(
            birth_date=birth_chart.birth_date,
            birth_time=birth_chart.birth_time,
            latitude=birth_chart.latitude,
            longitude=birth_chart.longitude
        )
        
        # Atualizar os signos recalculados (apenas os que estão no banco)
        birth_chart.sun_sign = chart_data["sun_sign"]
        birth_chart.moon_sign = chart_data["moon_sign"]
        birth_chart.ascendant_sign = chart_data["ascendant_sign"]
        birth_chart.sun_degree = chart_data.get("sun_degree")
        birth_chart.moon_degree = chart_data.get("moon_degree")
        birth_chart.ascendant_degree = chart_data.get("ascendant_degree")
        
        db.commit()
        db.refresh(birth_chart)
        
        # Adicionar dados dos planetas calculados ao objeto de retorno
        # (mesmo que não estejam no banco, retornamos para o frontend)
        birth_chart_dict = {
            "id": birth_chart.id,
            "user_id": birth_chart.user_id,
            "name": birth_chart.name,
            "birth_date": birth_chart.birth_date,
            "birth_time": birth_chart.birth_time,
            "birth_place": birth_chart.birth_place,
            "latitude": birth_chart.latitude,
            "longitude": birth_chart.longitude,
            "sun_sign": birth_chart.sun_sign,
            "moon_sign": birth_chart.moon_sign,
            "ascendant_sign": birth_chart.ascendant_sign,
            "sun_degree": birth_chart.sun_degree,
            "moon_degree": birth_chart.moon_degree,
            "ascendant_degree": birth_chart.ascendant_degree,
            "is_primary": birth_chart.is_primary,
            "created_at": birth_chart.created_at,
            "updated_at": birth_chart.updated_at,
            # Adicionar planetas calculados
            "mercury_sign": chart_data.get("mercury_sign"),
            "venus_sign": chart_data.get("venus_sign"),
            "mars_sign": chart_data.get("mars_sign"),
            "jupiter_sign": chart_data.get("jupiter_sign"),
            "saturn_sign": chart_data.get("saturn_sign"),
            "uranus_sign": chart_data.get("uranus_sign"),
            "neptune_sign": chart_data.get("neptune_sign"),
            "pluto_sign": chart_data.get("pluto_sign"),
            "midheaven_sign": chart_data.get("midheaven_sign"),
            "midheaven_degree": chart_data.get("midheaven_degree"),
            "planets_conjunct_midheaven": chart_data.get("planets_conjunct_midheaven"),
            "uranus_on_midheaven": chart_data.get("uranus_on_midheaven"),
        }
        
        return birth_chart_dict
    except Exception as e:
        # Se houver erro no recálculo, retornar dados existentes
        print(f"[WARNING] Erro ao recalcular mapa astral: {str(e)}")
        import traceback
        traceback.print_exc()
        # Retornar dados do banco mesmo em caso de erro
        pass
    
    return birth_chart


@router.put("/me")
def update_user(
    user_update: UserUpdateRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Atualiza informações do usuário e mapa astral."""
    current_user = get_current_user(authorization, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    
    # Atualizar dados do usuário
    if user_update.name:
        current_user.name = user_update.name
    
    if user_update.email:
        # Verificar se email já está em uso por outro usuário
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso"
            )
        current_user.email = user_update.email
    
    if user_update.password:
        current_user.password_hash = hash_password(user_update.password)
    
    # Atualizar mapa astral se fornecido
    if user_update.birth_data:
        birth_data = user_update.birth_data
        birth_chart = db.query(BirthChart).filter(
            BirthChart.user_id == current_user.id,
            BirthChart.is_primary == True
        ).first()
        
        if not birth_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mapa astral não encontrado"
            )
        
        # Calcular novos signos
        try:
            chart_data = calculate_birth_chart(
                birth_date=birth_data.birth_date,
                birth_time=birth_data.birth_time,
                latitude=birth_data.latitude,
                longitude=birth_data.longitude
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao calcular mapa astral: {str(e)}"
            )
        
        # Atualizar dados do mapa astral
        birth_chart.name = birth_data.name
        birth_chart.birth_date = birth_data.birth_date
        birth_chart.birth_time = birth_data.birth_time
        birth_chart.birth_place = birth_data.birth_place
        birth_chart.latitude = birth_data.latitude
        birth_chart.longitude = birth_data.longitude
        birth_chart.sun_sign = chart_data["sun_sign"]
        birth_chart.moon_sign = chart_data["moon_sign"]
        birth_chart.ascendant_sign = chart_data["ascendant_sign"]
        birth_chart.sun_degree = chart_data.get("sun_degree")
        birth_chart.moon_degree = chart_data.get("moon_degree")
        birth_chart.ascendant_degree = chart_data.get("ascendant_degree")
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Dados atualizados com sucesso"}


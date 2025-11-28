from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import datetime
import bcrypt
from typing import Optional
from app.core.database import get_db
from app.models.database import User, BirthChart
from pydantic import BaseModel
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
    # Normalizar email (lowercase e trim) para garantir busca correta
    normalized_email = credentials.email.strip().lower()
    
    # Buscar usuário pelo email (case-insensitive)
    from sqlalchemy import func
    user = db.query(User).filter(func.lower(User.email) == normalized_email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado. Este e-mail não está cadastrado."
        )
    
    # Verificar senha
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Esta conta não possui senha. Tente entrar com Google."
        )
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta. Verifique e tente novamente."
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
            # Nodos Lunares
            "north_node_sign": chart_data.get("north_node_sign"),
            "north_node_degree": chart_data.get("north_node_degree"),
            "south_node_sign": chart_data.get("south_node_sign"),
            "south_node_degree": chart_data.get("south_node_degree"),
            # Quíron (a ferida do curador)
            "chiron_sign": chart_data.get("chiron_sign"),
            "chiron_degree": chart_data.get("chiron_degree"),
            # Graus dos planetas
            "mercury_degree": chart_data.get("mercury_degree"),
            "venus_degree": chart_data.get("venus_degree"),
            "mars_degree": chart_data.get("mars_degree"),
            "jupiter_degree": chart_data.get("jupiter_degree"),
            "saturn_degree": chart_data.get("saturn_degree"),
            "uranus_degree": chart_data.get("uranus_degree"),
            "neptune_degree": chart_data.get("neptune_degree"),
            "pluto_degree": chart_data.get("pluto_degree"),
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


class GoogleVerifyRequest(BaseModel):
    """Request para verificar token do Google"""
    credential: str


class GoogleVerifyResponse(BaseModel):
    """Resposta da verificação do token Google"""
    email: str
    name: str
    picture: Optional[str] = None
    google_id: str


class GoogleAuthRequest(BaseModel):
    """Request para autenticação via Google"""
    email: str
    name: str
    google_id: str  # Mantido para referência futura, mas não salvo no banco por enquanto


class GoogleAuthResponse(BaseModel):
    """Resposta da autenticação Google"""
    access_token: str
    token_type: str
    is_new_user: bool
    needs_onboarding: bool


@router.post("/google/verify", response_model=GoogleVerifyResponse)
def verify_google_token(request: GoogleVerifyRequest):
    """
    Verifica o token JWT do Google e retorna dados do usuário.
    """
    try:
        credential = request.credential
        if not credential:
            raise HTTPException(status_code=400, detail="Credencial não fornecido")
        
        # Tentar validar token com Google
        # Se google-auth não estiver instalado, usar decodificação básica do JWT
        try:
            from google.auth.transport import requests as google_requests
            from google.oauth2 import id_token
            import os
            
            CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or settings.GOOGLE_CLIENT_ID
            if not CLIENT_ID:
                # Se não tiver CLIENT_ID configurado, decodificar JWT manualmente
                import base64
                import json
                
                # JWT tem 3 partes separadas por ponto
                parts = credential.split('.')
                if len(parts) != 3:
                    raise HTTPException(status_code=400, detail="Token JWT inválido")
                
                # Decodificar payload (segunda parte)
                payload = parts[1]
                # Adicionar padding se necessário
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                
                decoded = base64.urlsafe_b64decode(payload)
                idinfo = json.loads(decoded)
                
                email = idinfo.get("email")
                name = idinfo.get("name")
                picture = idinfo.get("picture")
                google_id = idinfo.get("sub")
            else:
                # Validar token com Google oficialmente
                idinfo = id_token.verify_oauth2_token(
                    credential,
                    google_requests.Request(),
                    CLIENT_ID
                )
                
                email = idinfo.get("email")
                name = idinfo.get("name")
                picture = idinfo.get("picture")
                google_id = idinfo.get("sub")
        except ImportError:
            # Se google-auth não estiver instalado, usar decodificação manual
            import base64
            import json
            
            parts = credential.split('.')
            if len(parts) != 3:
                raise HTTPException(status_code=400, detail="Token JWT inválido")
            
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            try:
                decoded = base64.urlsafe_b64decode(payload)
                idinfo = json.loads(decoded)
                
                email = idinfo.get("email")
                name = idinfo.get("name")
                picture = idinfo.get("picture")
                google_id = idinfo.get("sub")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erro ao decodificar token: {str(e)}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Token inválido: {str(e)}")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email não encontrado no token")
        
        return GoogleVerifyResponse(
            email=email,
            name=name or email.split('@')[0],
            picture=picture,
            google_id=google_id or credential[:50]  # Fallback se não tiver sub
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao verificar token Google: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar token: {str(e)}"
        )


@router.post("/google/verify", response_model=GoogleVerifyResponse)
def verify_google_token(request: GoogleVerifyRequest):
    """
    Verifica o token JWT do Google e retorna dados do usuário.
    """
    try:
        credential = request.credential
        if not credential:
            raise HTTPException(status_code=400, detail="Credencial não fornecido")
        
        # Tentar validar token com Google
        # Se google-auth não estiver instalado, usar decodificação básica do JWT
        try:
            from google.auth.transport import requests as google_requests
            from google.oauth2 import id_token
            
            CLIENT_ID = settings.GOOGLE_CLIENT_ID
            if not CLIENT_ID:
                # Se não tiver CLIENT_ID configurado, decodificar JWT manualmente
                import base64
                import json
                
                # JWT tem 3 partes separadas por ponto
                parts = credential.split('.')
                if len(parts) != 3:
                    raise HTTPException(status_code=400, detail="Token JWT inválido")
                
                # Decodificar payload (segunda parte)
                payload = parts[1]
                # Adicionar padding se necessário
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                
                decoded = base64.urlsafe_b64decode(payload)
                idinfo = json.loads(decoded)
                
                email = idinfo.get("email")
                name = idinfo.get("name")
                picture = idinfo.get("picture")
                google_id = idinfo.get("sub")
            else:
                # Validar token com Google oficialmente
                idinfo = id_token.verify_oauth2_token(
                    credential,
                    google_requests.Request(),
                    CLIENT_ID
                )
                
                email = idinfo.get("email")
                name = idinfo.get("name")
                picture = idinfo.get("picture")
                google_id = idinfo.get("sub")
        except ImportError:
            # Se google-auth não estiver instalado, usar decodificação manual
            import base64
            import json
            
            parts = credential.split('.')
            if len(parts) != 3:
                raise HTTPException(status_code=400, detail="Token JWT inválido")
            
            payload = parts[1]
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            try:
                decoded = base64.urlsafe_b64decode(payload)
                idinfo = json.loads(decoded)
                
                email = idinfo.get("email")
                name = idinfo.get("name")
                picture = idinfo.get("picture")
                google_id = idinfo.get("sub")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erro ao decodificar token: {str(e)}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Token inválido: {str(e)}")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email não encontrado no token")
        
        return GoogleVerifyResponse(
            email=email,
            name=name or email.split('@')[0],
            picture=picture,
            google_id=google_id or credential[:50]  # Fallback se não tiver sub
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao verificar token Google: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar token: {str(e)}"
        )


@router.post("/google", response_model=GoogleAuthResponse)
def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Autentica um usuário via Google OAuth.
    - Se o usuário não existe, cria um novo sem senha
    - Se o usuário existe mas não tem mapa astral, retorna needs_onboarding=True
    - Se o usuário já tem mapa astral, retorna needs_onboarding=False
    """
    try:
        # Normalizar email (lowercase e trim) para garantir busca correta
        normalized_email = request.email.strip().lower()
        print(f"[GOOGLE_AUTH] Email recebido: '{request.email}' -> normalizado: '{normalized_email}'")
        
        # Verificar se o usuário já existe pelo email (usando func.lower para case-insensitive)
        from sqlalchemy import func
        existing_user = db.query(User).filter(func.lower(User.email) == normalized_email).first()
        
        print(f"[GOOGLE_AUTH] Usuário encontrado: {existing_user is not None}")
        if existing_user:
            print(f"[GOOGLE_AUTH] Usuário ID: {existing_user.id}, Email no banco: '{existing_user.email}'")
            # Usuário já existe - verificar se tem mapa astral
            birth_chart = db.query(BirthChart).filter(
                BirthChart.user_id == existing_user.id,
                BirthChart.is_primary == True
            ).first()
            
            # Criar token JWT (usar email normalizado)
            access_token = create_access_token(data={"sub": normalized_email})
            
            return GoogleAuthResponse(
                access_token=access_token,
                token_type="bearer",
                is_new_user=False,
                needs_onboarding=birth_chart is None
            )
        else:
            # Novo usuário via Google - criar sem senha
            db_user = User(
                email=normalized_email,  # Usar email normalizado
                password_hash=None,  # Usuário Google não tem senha
                name=request.name
                # google_id será adicionado quando a migração do banco for feita
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            # Criar token JWT (usar email normalizado)
            access_token = create_access_token(data={"sub": normalized_email})
            
            return GoogleAuthResponse(
                access_token=access_token,
                token_type="bearer",
                is_new_user=True,
                needs_onboarding=True  # Novo usuário sempre precisa de onboarding
            )
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro na autenticação Google: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na autenticação Google: {str(e)}"
        )


class OnboardingRequest(BaseModel):
    """Request para completar onboarding"""
    name: str
    birth_date: str  # ISO format
    birth_time: str  # HH:MM
    birth_place: str
    latitude: float
    longitude: float


@router.post("/complete-onboarding", response_model=BirthChartResponse)
def complete_onboarding(
    data: OnboardingRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Completa o onboarding de um usuário criando seu mapa astral.
    Usado após login Google para coletar dados de nascimento.
    """
    current_user = get_current_user(authorization, db)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado"
        )
    
    # Verificar se já tem mapa astral
    existing_chart = db.query(BirthChart).filter(
        BirthChart.user_id == current_user.id,
        BirthChart.is_primary == True
    ).first()
    
    if existing_chart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já possui mapa astral"
        )
    
    try:
        # Atualizar nome do usuário se necessário
        if data.name and data.name != current_user.name:
            current_user.name = data.name
        
        # Converter data de nascimento
        birth_date = datetime.fromisoformat(data.birth_date.replace('Z', '+00:00'))
        
        # Calcular mapa astral
        chart_data = calculate_birth_chart(
            birth_date=birth_date,
            birth_time=data.birth_time,
            latitude=data.latitude,
            longitude=data.longitude
        )
        
        # Criar mapa astral
        db_birth_chart = BirthChart(
            user_id=current_user.id,
            name=data.name,
            birth_date=birth_date,
            birth_time=data.birth_time,
            birth_place=data.birth_place,
            latitude=data.latitude,
            longitude=data.longitude,
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
        db.refresh(db_birth_chart)
        
        # Retornar dados completos com planetas calculados
        return {
            "id": db_birth_chart.id,
            "user_id": db_birth_chart.user_id,
            "name": db_birth_chart.name,
            "birth_date": db_birth_chart.birth_date,
            "birth_time": db_birth_chart.birth_time,
            "birth_place": db_birth_chart.birth_place,
            "latitude": db_birth_chart.latitude,
            "longitude": db_birth_chart.longitude,
            "sun_sign": db_birth_chart.sun_sign,
            "moon_sign": db_birth_chart.moon_sign,
            "ascendant_sign": db_birth_chart.ascendant_sign,
            "sun_degree": db_birth_chart.sun_degree,
            "moon_degree": db_birth_chart.moon_degree,
            "ascendant_degree": db_birth_chart.ascendant_degree,
            "is_primary": db_birth_chart.is_primary,
            "created_at": db_birth_chart.created_at,
            "updated_at": db_birth_chart.updated_at,
            # Dados calculados
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
            "north_node_sign": chart_data.get("north_node_sign"),
            "north_node_degree": chart_data.get("north_node_degree"),
            "south_node_sign": chart_data.get("south_node_sign"),
            "south_node_degree": chart_data.get("south_node_degree"),
            "chiron_sign": chart_data.get("chiron_sign"),
            "chiron_degree": chart_data.get("chiron_degree"),
        }
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao completar onboarding: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar mapa astral: {str(e)}"
        )


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


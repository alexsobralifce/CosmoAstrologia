"""
API endpoints for Google OAuth authentication
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.database import User, BirthChart
from app.models.schemas import BirthData, UserUpdate, UserRegister

router = APIRouter()
oauth = OAuth()

# Configure Google OAuth
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str = Depends(oauth2_scheme)) -> dict:
    """Verify JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception

def get_current_user(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from database"""
    user_id = token_data.get("sub")
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Extract database ID from JWT token
    if isinstance(user_id, str) and user_id.startswith("google_"):
        # Old format - find by google_id
        db_user = db.query(User).filter(User.google_id == user_id.replace("google_", "")).first()
    else:
        # New format - direct database ID
        try:
            db_user_id = int(user_id)
            db_user = db.query(User).filter(User.id == db_user_id).first()
        except (ValueError, TypeError):
            db_user = None
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return db_user

@router.get("/login")
async def login(request: Request):
    """Initiate Google OAuth login"""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env")
    
    # Build redirect URI from request URL
    base_url = str(request.base_url).rstrip('/')
    redirect_uri = f"{base_url}/api/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")
        
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            # Try to get from token directly
            if 'id_token' in token:
                import base64
                try:
                    # Decode JWT id_token
                    id_token_parts = token['id_token'].split('.')
                    if len(id_token_parts) >= 2:
                        # Decode payload (add padding if needed)
                        payload = id_token_parts[1]
                        payload += '=' * (4 - len(payload) % 4)
                        decoded = base64.urlsafe_b64decode(payload)
                        import json
                        user_info = json.loads(decoded)
                except:
                    pass
            
            if not user_info:
                raise HTTPException(status_code=400, detail="Failed to get user info")
        
        # Extract user data
        google_id = user_info.get('sub') or user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name', email)
        picture = user_info.get('picture')
        
        if not google_id or not email:
            raise HTTPException(status_code=400, detail="Missing required user information")
        
        # Create or update user in database
        db_user = db.query(User).filter(User.google_id == google_id).first()
        
        if not db_user:
            # Create new user
            db_user = User(
                google_id=google_id,
                email=email,
                name=name,
                picture=picture
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        else:
            # Update existing user
            db_user.email = email
            db_user.name = name
            db_user.picture = picture
            db.commit()
            db.refresh(db_user)
        
        # Create JWT token with database user ID
        access_token = create_access_token(data={"sub": str(db_user.id), "email": email})
        
        # Redirect to frontend with token
        frontend_url = "http://localhost:3000"
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?token={access_token}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@router.put("/me")
async def update_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user info"""
    if user_update.name:
        current_user.name = user_update.name
        db.commit()
        db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture": current_user.picture,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }

@router.get("/birth-data")
async def get_user_birth_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's birth data if exists"""
    # Find user's primary birth chart
    birth_chart = db.query(BirthChart).filter(
        BirthChart.user_id == current_user.id,
        BirthChart.is_primary == True
    ).first()
    
    if not birth_chart:
        raise HTTPException(status_code=404, detail="Birth data not found")
    
    return {
        "name": birth_chart.name,
        "birth_date": birth_chart.birth_date,
        "birth_time": birth_chart.birth_time,
        "birth_place": birth_chart.birth_place
    }

@router.post("/birth-data")
async def save_user_birth_data(
    birth_data: BirthData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save or update user's birth data"""
    # Check if user already has a primary birth chart
    existing_chart = db.query(BirthChart).filter(
        BirthChart.user_id == current_user.id,
        BirthChart.is_primary == True
    ).first()
    
    if existing_chart:
        # Update existing chart
        existing_chart.name = birth_data.name
        existing_chart.birth_date = birth_data.birth_date
        existing_chart.birth_time = birth_data.birth_time
        existing_chart.birth_place = birth_data.birth_place
        db.commit()
        db.refresh(existing_chart)
        return {"message": "Birth data updated successfully"}
    else:
        # Create new primary chart
        new_chart = BirthChart(
            user_id=current_user.id,
            name=birth_data.name,
            birth_date=birth_data.birth_date,
            birth_time=birth_data.birth_time,
            birth_place=birth_data.birth_place,
            sun_sign="",  # Will be calculated later
            moon_sign="",
            ascendant_sign="",
            chart_data={},  # Will be filled when chart is calculated
            is_primary=True
        )
        db.add(new_chart)
        db.commit()
        db.refresh(new_chart)
        return {"message": "Birth data saved successfully"}

@router.post("/register")
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user with email, name and birth data"""
    try:
        # Check if user with this email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        
        if existing_user:
            # If user exists, update birth data if needed
            # Check if user already has primary birth chart
            existing_chart = db.query(BirthChart).filter(
                BirthChart.user_id == existing_user.id,
                BirthChart.is_primary == True
            ).first()
            
            if existing_chart:
                # Update existing chart
                existing_chart.name = user_data.birth_data.name
                existing_chart.birth_date = user_data.birth_data.birth_date
                existing_chart.birth_time = user_data.birth_data.birth_time
                existing_chart.birth_place = user_data.birth_data.birth_place
            else:
                # Create new primary chart
                new_chart = BirthChart(
                    user_id=existing_user.id,
                    name=user_data.birth_data.name,
                    birth_date=user_data.birth_data.birth_date,
                    birth_time=user_data.birth_data.birth_time,
                    birth_place=user_data.birth_data.birth_place,
                    sun_sign="",
                    moon_sign="",
                    ascendant_sign="",
                    chart_data={},
                    is_primary=True
                )
                db.add(new_chart)
            
            db.commit()
            
            # Create JWT token
            access_token = create_access_token(data={"sub": str(existing_user.id), "email": existing_user.email})
            
            return {
                "message": "User data updated successfully",
                "token": access_token,
                "user": {
                    "id": existing_user.id,
                    "email": existing_user.email,
                    "name": existing_user.name,
                    "picture": existing_user.picture
                }
            }
        else:
            # Create new user
            new_user = User(
                email=user_data.email,
                name=user_data.name,
                google_id=None,  # No Google OAuth
                picture=None
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Create primary birth chart
            new_chart = BirthChart(
                user_id=new_user.id,
                name=user_data.birth_data.name,
                birth_date=user_data.birth_data.birth_date,
                birth_time=user_data.birth_data.birth_time,
                birth_place=user_data.birth_data.birth_place,
                sun_sign="",
                moon_sign="",
                ascendant_sign="",
                chart_data={},
                is_primary=True
            )
            db.add(new_chart)
            db.commit()
            
            # Create JWT token
            access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email})
            
            return {
                "message": "User registered successfully",
                "token": access_token,
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "name": new_user.name,
                    "picture": new_user.picture
                }
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user"""
    # In production, you would invalidate the token
    return {"message": "Logged out successfully"}

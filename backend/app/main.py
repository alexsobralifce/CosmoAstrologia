from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api import charts, interpretations, transits, auth
from app.core.config import settings
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Astrologia API",
    description="API para cálculo e interpretação de mapas astrológicos usando RAG",
    version="1.0.0"
)

# Session Middleware (required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    max_age=3600,  # 1 hour
    same_site="lax"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(charts.router, prefix="/api/charts", tags=["charts"])
app.include_router(interpretations.router, prefix="/api/interpretations", tags=["interpretations"])
app.include_router(transits.router, prefix="/api/transits", tags=["transits"])

@app.get("/")
async def root():
    return {"message": "Astrologia API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}


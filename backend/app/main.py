from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth
from app.api import interpretation

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Astrologia API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(interpretation.router, prefix="/api", tags=["interpretation"])


@app.get("/")
def root():
    return {"message": "Astrologia API"}


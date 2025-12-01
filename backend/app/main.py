from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth
from app.api import interpretation
import os

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Astrologia API")

# CORS - Garantir que domínios de produção estejam incluídos
if isinstance(settings.CORS_ORIGINS, list):
    cors_origins = list(settings.CORS_ORIGINS)
elif isinstance(settings.CORS_ORIGINS, str):
    cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(',') if origin.strip()]
else:
    cors_origins = []

# Adicionar domínios de produção se não estiverem presentes
production_domains = [
    "https://www.cosmoastral.com.br",
    "https://cosmoastral.com.br",
    "http://www.cosmoastral.com.br",
    "http://cosmoastral.com.br"
]

for domain in production_domains:
    if domain not in cors_origins:
        cors_origins.append(domain)

# Log das origens permitidas
print("=" * 80)
print("🌐 CORS Configuration:")
print(f"   Allowed Origins: {cors_origins}")
print("=" * 80)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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


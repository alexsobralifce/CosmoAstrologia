from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth
from app.api import interpretation
import os
import traceback

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

# Exception handlers para garantir CORS mesmo em erros
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Garante que headers CORS sejam adicionados mesmo em erros HTTP"""
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    # Adicionar headers CORS manualmente
    origin = request.headers.get("origin")
    if origin and origin in cors_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Garante que headers CORS sejam adicionados mesmo em erros gerais"""
    print(f"[ERROR] Exception não tratada: {str(exc)}")
    print(f"[ERROR] Traceback: {traceback.format_exc()}")
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Erro interno do servidor: {str(exc)}"}
    )
    # Adicionar headers CORS manualmente
    origin = request.headers.get("origin")
    if origin and origin in cors_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(interpretation.router, prefix="/api", tags=["interpretation"])


@app.get("/")
def root():
    return {"message": "Astrologia API"}


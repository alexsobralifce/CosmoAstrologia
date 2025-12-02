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

# Migração automática: Adicionar colunas e tabelas necessárias
# (apenas para PostgreSQL, SQLite já foi migrado manualmente)
try:
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    
    # Verificar e adicionar colunas de verificação de email na tabela users
    try:
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'email_verified' not in columns:
            print("[MIGRATION] Adicionando colunas de verificação de email...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE"))
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code TEXT"))
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code_expires TIMESTAMP"))
                conn.execute(text("ALTER TABLE users ALTER COLUMN is_active SET DEFAULT FALSE"))
                conn.commit()
                print("[MIGRATION] ✅ Colunas de verificação adicionadas com sucesso!")
    except Exception as e:
        print(f"[MIGRATION] Aviso ao verificar colunas users: {e}")
    
    # Verificar se tabela pending_registrations existe
    try:
        tables = inspector.get_table_names()
        if 'pending_registrations' not in tables:
            print("[MIGRATION] Criando tabela pending_registrations...")
            with engine.connect() as conn:
                # Criar tabela pending_registrations
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS pending_registrations (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR UNIQUE NOT NULL,
                        password_hash VARCHAR,
                        name VARCHAR,
                        verification_code VARCHAR NOT NULL,
                        verification_code_expires TIMESTAMP NOT NULL,
                        birth_chart_data TEXT NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                # Criar índices
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pending_registrations_email ON pending_registrations(email)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pending_registrations_expires ON pending_registrations(verification_code_expires)"))
                conn.commit()
                print("[MIGRATION] ✅ Tabela pending_registrations criada com sucesso!")
        else:
            print("[MIGRATION] ✅ Tabela pending_registrations já existe")
    except Exception as e:
        print(f"[MIGRATION] Aviso ao verificar tabela pending_registrations: {e}")
        # Tentar criar via SQLAlchemy como fallback
        try:
            from app.models.database import PendingRegistration
            PendingRegistration.__table__.create(bind=engine, checkfirst=True)
            print("[MIGRATION] ✅ Tabela pending_registrations criada via SQLAlchemy")
        except Exception as e2:
            print(f"[MIGRATION] Erro ao criar pending_registrations: {e2}")
    
    # Verificar e corrigir foreign key constraint com CASCADE
    try:
        # Verificar se a constraint existe e se tem CASCADE
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    rc.delete_rule
                FROM information_schema.referential_constraints AS rc
                JOIN information_schema.table_constraints AS tc
                  ON rc.constraint_name = tc.constraint_name
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = 'birth_charts' 
                  AND tc.constraint_type = 'FOREIGN KEY'
                  AND kcu.column_name = 'user_id'
                LIMIT 1
            """))
            constraint = result.fetchone()
            
            if constraint and constraint[0] != 'CASCADE':
                print("[MIGRATION] Corrigindo foreign key constraint para CASCADE...")
                # Remover constraint antiga
                conn.execute(text("ALTER TABLE birth_charts DROP CONSTRAINT IF EXISTS birth_charts_user_id_fkey"))
                # Recriar com CASCADE
                conn.execute(text("""
                    ALTER TABLE birth_charts 
                    ADD CONSTRAINT birth_charts_user_id_fkey 
                    FOREIGN KEY (user_id) 
                    REFERENCES users(id) 
                    ON DELETE CASCADE
                """))
                conn.commit()
                print("[MIGRATION] ✅ Foreign key constraint corrigida com CASCADE!")
            elif constraint and constraint[0] == 'CASCADE':
                print("[MIGRATION] ✅ Foreign key constraint já tem CASCADE")
    except Exception as e:
        print(f"[MIGRATION] Aviso ao verificar foreign key constraint: {e}")
            
except Exception as e:
    print(f"[MIGRATION] Aviso: Não foi possível executar migração automática: {e}")
    print("[MIGRATION] Execute os scripts de migração manualmente se necessário.")

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

@app.get("/health")
def health_check():
    """Health check endpoint para monitoramento e Docker health checks"""
    try:
        # Verificar conexão com banco de dados
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "service": "astrologia-api"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "service": "astrologia-api"
            }
        )


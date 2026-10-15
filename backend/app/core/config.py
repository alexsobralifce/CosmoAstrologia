from pydantic_settings import BaseSettings
from pydantic import field_validator
from pathlib import Path
from typing import List, Union
import os


class Settings(BaseSettings):
    """
    Configurações da aplicação.
    
    As variáveis podem ser definidas via:
    1. Arquivo .env no diretório backend/
    2. Variáveis de ambiente do sistema
    3. Valores padrão (definidos abaixo)
    
    Para desenvolvimento local, crie a pasta backend/.env baseada em .env.example
    Para produção (Railway), configure as variáveis diretamente no painel.
    """
    
    # Database
    # Default to SQLite for local development, PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./astrologia.db"
    
    # Security
    # ⚠️ IMPORTANT: Change this in production!
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate limit das rotas que chamam LLM (por usuário, janela de 60 s)
    LLM_RATE_LIMIT_PER_MINUTE: int = 30
    
    # Email Configuration (Brevo/SendinBlue)
    BREVO_API_KEY: str = ""
    # Email do remetente (deve ser um email verificado no Brevo)
    EMAIL_FROM: str = "noreply@cosmoastral.com.br"
    # Nome do remetente
    EMAIL_FROM_NAME: str = "CosmoAstral"
    
    # Google OAuth (Optional)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # CORS - can be set via environment variable as comma-separated string
    # Example: CORS_ORIGINS="http://localhost:5173,https://yourapp.com"
    # Default includes common local development ports
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:5173"
    ]
    
    # AI Provider Configuration
    AI_PROVIDER: str = "groq"  # Padrão: groq (rápido e profissional)
    
    # API Keys - Múltiplos provedores
    DEEPSEEK_API_KEY: str = ""  # Fallback
    GROQ_API_KEY: str = ""  # Provedor padrão
    
    # Groq Model Configuration (modelos profissionais disponíveis)
    GROQ_MODEL: str = "llama-3.1-8b-instant"  # Modelo rápido e profissional (8B - sempre disponível)
    # Outras opções disponíveis (verificar na console.groq.com quais estão habilitados):
    # - llama-3.1-8b-instant (8B - rápido, padrão, sempre disponível)
    # - llama-3.3-70b-versatile (70B - pode estar bloqueado no projeto)
    # - mixtral-8x7b-32768 (56B - pode precisar ser habilitado no projeto)
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    # RAG Configuration (consolidado no backend)
    DOCS_PATH: str = "docs"
    INDEX_PATH: str = "rag_index_fastembed"
    BGE_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string (comma-separated) or list."""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    class Config:
        # Look for .env file in the backend directory (parent of app/core)
        # Path: backend/.env
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()

# Warn if using default SECRET_KEY in what looks like production
if settings.SECRET_KEY == "your-secret-key-change-in-production":
    # Check if we're likely in production (has DATABASE_URL with postgresql or railway/vercel env)
    is_production = (
        "postgresql" in settings.DATABASE_URL.lower() or
        os.getenv("RAILWAY_ENVIRONMENT") is not None or
        os.getenv("VERCEL") is not None or
        os.getenv("PRODUCTION") == "true"
    )
    if is_production:
        import warnings
        import sys
        warnings.warn(
            "⚠️ SECURITY WARNING: Using default SECRET_KEY in production! "
            "Please set a secure SECRET_KEY in your environment variables. "
            "Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"",
            UserWarning
        )
        # Em produção, também logar como erro crítico
        print("=" * 80, file=sys.stderr)
        print("🚨 CRITICAL SECURITY ERROR: Default SECRET_KEY detected in production!", file=sys.stderr)
        print("   The application may not work correctly. Set SECRET_KEY immediately!", file=sys.stderr)
        print("=" * 80, file=sys.stderr)


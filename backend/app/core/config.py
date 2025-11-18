from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

# Get the root directory (one level up from backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    SECRET_KEY: str = "your-secret-key-change-in-production"  # Para JWT
    ALGORITHM: str = "HS256"
    
    # RAG Configuration
    RAG_MODEL: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # PDFs path
    PDFS_PATH: str = "../pdf"
    
    # Additional variables from .env (optional)
    DEBUG: str = "False"
    ALLOWED_HOSTS: str = ""
    DATABASE_URL: str = ""
    GROQ_API_KEY: str = ""
    
    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()


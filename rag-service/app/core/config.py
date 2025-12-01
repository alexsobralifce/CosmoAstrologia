"""
Configurações do RAG Service.
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List, Union


class Settings(BaseSettings):
    """Configurações do RAG Service."""
    
    # API Keys
    GROQ_API_KEY: str = ""
    
    # RAG Configuration
    DOCS_PATH: str = "docs"
    INDEX_PATH: str = "rag_index_fastembed"
    BGE_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from string (comma-separated) or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()


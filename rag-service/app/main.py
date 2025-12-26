"""
RAG Service - Microsserviço para Retrieval-Augmented Generation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router

app = FastAPI(
    title="RAG Service API",
    description="Microsserviço para interpretações astrológicas usando RAG",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(router, prefix="/api/rag", tags=["rag"])


@app.get("/")
def root():
    return {
        "message": "RAG Service API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/api/rag/status",
            "interpretation": "/api/rag/interpretation",
            "search": "/api/rag/search"
        }
    }


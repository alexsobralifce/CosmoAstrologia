# Main entry point for Railway deployment
# Railway auto-detects this file and runs it with uvicorn for FastAPI

from app.main import app

# This file exists so Railway can auto-detect the FastAPI application
# The actual app is defined in app/main.py


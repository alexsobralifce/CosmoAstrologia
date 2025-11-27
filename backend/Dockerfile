FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and RAG files
# NOTE: .dockerignore will exclude venv/, astrologia.db, etc.
# but will INCLUDE docs/ and rag_index.pkl which are needed for RAG service
COPY . .

# Expose the port
EXPOSE 8000

# Command to run the application
# Railway automatically provides PORT environment variable
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

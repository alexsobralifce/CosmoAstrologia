FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, wheel first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install all dependencies with increased timeout and retries
# Using extended timeout (600s = 10min) and multiple retries to handle network issues
RUN pip install --no-cache-dir --user \
    --timeout=600 \
    --retries=5 \
    --default-timeout=600 \
    -r requirements.txt

# Final stage - runtime only
FROM python:3.11-slim

WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app/ ./app/
COPY rag_index_llamaindex/ ./rag_index_llamaindex/

# Expose port
EXPOSE 8000

# Command to run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --loop asyncio

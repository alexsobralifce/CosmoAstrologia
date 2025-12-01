FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies (including swig for pyswisseph/kerykeion)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    swig \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Use production requirements (without test dependencies)
# This significantly reduces build time
COPY requirements-prod.txt requirements.txt

# Install dependencies in small batches to avoid timeout
# Each batch has 3min timeout, ML dependencies have 10min
# Batch 1: FastAPI core
RUN pip install --no-cache-dir --user \
    --timeout=180 \
    --retries=3 \
    fastapi==0.115.0 \
    uvicorn[standard]==0.32.0

# Batch 2: Database
RUN pip install --no-cache-dir --user \
    --timeout=180 \
    --retries=3 \
    sqlalchemy==2.0.36 \
    psycopg2-binary>=2.9.0

# Batch 3: Pydantic
RUN pip install --no-cache-dir --user \
    --timeout=180 \
    --retries=3 \
    pydantic==2.10.0 \
    pydantic-settings==2.6.0 \
    "pydantic[email]==2.10.0" \
    email-validator==2.2.0

# Batch 4: Auth
RUN pip install --no-cache-dir --user \
    --timeout=180 \
    --retries=3 \
    python-jose[cryptography]==3.3.0 \
    bcrypt==4.2.0 \
    python-multipart==0.0.12

# Batch 5: Astronomy
RUN pip install --no-cache-dir --user \
    --timeout=180 \
    --retries=3 \
    ephem==4.1.5 \
    kerykeion>=5.3.0 \
    pytz>=2024.1 \
    timezonefinder>=6.4.1

# Batch 6: Google & Groq
RUN pip install --no-cache-dir --user \
    --timeout=180 \
    --retries=3 \
    google-auth>=2.0.0 \
    google-auth-oauthlib>=1.0.0 \
    google-auth-httplib2>=0.2.0 \
    groq>=0.4.1

# Batch 7: Utilities & HTTP Client
RUN pip install --no-cache-dir --user \
    --timeout=180 \
    --retries=3 \
    "numpy<2.0" \
    httpx>=0.27.0 \
    PyPDF2==3.0.1

# Batch 8: RAG Dependencies (consolidado no backend)
RUN pip install --no-cache-dir --user \
    --timeout=600 \
    --retries=3 \
    fastembed>=0.2.0

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Runtime dependencies only (libpq5 for PostgreSQL, libc6 for compiled extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libc6 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH \
    PORT=8000

# Copy installed packages
COPY --from=builder /root/.local /root/.local

# Copy application
COPY app/ ./app/

EXPOSE 8000

# Use PORT environment variable (defaults to 8000 if not set)
# Railway e outras plataformas definem PORT automaticamente
CMD sh -c 'uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --loop asyncio'

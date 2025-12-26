FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install dependencies in batches for better caching
# Batch 1: FastEmbed (ML dependency - mais leve que llama-index)
RUN pip install --no-cache-dir --user \
    --timeout=300 \
    --retries=3 \
    fastembed>=0.2.0 numpy<2.0

# Batch 2: Core API dependencies
RUN pip install --no-cache-dir --user \
    --timeout=180 \
    --retries=3 \
    fastapi==0.115.0 \
    uvicorn[standard]==0.32.0 \
    pydantic==2.10.0 \
    pydantic-settings==2.6.0

# Batch 3: Utilities
RUN pip install --no-cache-dir --user \
    --timeout=180 \
    --retries=3 \
    groq>=0.4.1 \
    PyPDF2==3.0.1

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

# Copy installed packages
COPY --from=builder /root/.local /root/.local

# Copy application
COPY app/ ./app/

# Nota: docs/ e rag_index_fastembed/ são montados via volumes no docker-compose
# Não precisam ser copiados durante o build

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]


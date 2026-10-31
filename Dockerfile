# Production Dockerfile for RepairForge AI / Forge Command Backend (Railway Ready)
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Install minimal OS dependencies required for Git operations, repository inspection, and testing
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications first to leverage Docker layer caching
COPY requirements.txt pyproject.toml ./

# Install python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy backend codebase, agent engine, skills, fixtures, and evaluations
COPY repairforge/ ./repairforge/
COPY web_api/ ./web_api/
COPY skills/ ./skills/
COPY examples/ ./examples/
COPY results/ ./results/
COPY README.md LICENSE.md ./

# Install repairforge package in editable mode so CLI and imports work everywhere
RUN pip install --no-deps -e .

# Expose the default port (Railway will override via dynamic $PORT)
EXPOSE 8000

# Health check using curl against /api/health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health || exit 1

# Start Uvicorn ASGI server with dynamic port binding for Railway
CMD ["sh", "-c", "uvicorn web_api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]


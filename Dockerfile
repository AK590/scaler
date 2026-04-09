FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Set Python path
ENV PYTHONPATH="/app:$PYTHONPATH"

# Expose both ports globally
EXPOSE 7860
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the FastAPI server on BOTH ports to satisfy HuggingFace (7860) and OpenEnv Evaluator (8000)
CMD uvicorn email_triage_env.server.app:app --host 0.0.0.0 --port 7860 & uvicorn email_triage_env.server.app:app --host 0.0.0.0 --port 8000

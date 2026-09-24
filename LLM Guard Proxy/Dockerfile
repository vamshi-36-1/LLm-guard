# LLM-Guard Proxy - Production Dockerfile
# Person 1 - Week 4
# Multi-stage build for optimized image

FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# Final stage
# ============================================

FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Set environment variables
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application files
COPY proxy_monitoring.py .
COPY rate_limiter_circuitbreaker.py .
COPY monitoring_metrics.py .
COPY ../Jailbreak Detection System/jailbreak_patterns.json .

# Copy models (Person 2's detector)
COPY ../Jailbreak Detection System/models/ ./models/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8888/ || exit 1

# Expose port
EXPOSE 8888

# Run proxy
CMD ["python", "proxy_monitoring.py"]

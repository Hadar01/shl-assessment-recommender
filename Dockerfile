# Build stage - Alpine for minimal size
FROM python:3.12-alpine as builder

WORKDIR /app

# Install minimal build dependencies
RUN apk add --no-cache gcc musl-dev linux-headers

# Copy requirements - ultra-minimal
COPY requirements-base.txt .

# Install Python dependencies with aggressive optimization
# --prefer-binary: use pre-built wheels (no compilation)
# --no-cache-dir: don't cache pip downloads
# --no-deps: no dependency resolution (trust requirements.txt)
RUN pip install --user --no-cache-dir --prefer-binary --no-deps -r requirements-base.txt && \
    find /root/.local -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -type f -name "*.pyc" -delete && \
    find /root/.local -type f -name "*.dist-info" -delete 2>/dev/null || true

# Runtime stage - Alpine for minimal final image
FROM python:3.12-alpine

WORKDIR /app

# Install minimal runtime dependencies
RUN apk add --no-cache curl

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set PATH to use local pip packages
ENV PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy application code
COPY . .

# Create non-root user
RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start API server
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

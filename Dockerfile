# Multi-stage Dockerfile for Nexus Letter AI Analyzer
# Security-focused build with minimal Alpine base and non-root user

# Build stage for dependencies
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    rust

# Create build directory
WORKDIR /build

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-alpine AS production

# Install runtime dependencies only
RUN apk add --no-cache \
    sqlite \
    ca-certificates \
    tzdata \
    && rm -rf /var/cache/apk/*

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Set up application directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Make sure Python can find the packages
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH="/home/appuser/.local/lib/python3.11/site-packages:$PYTHONPATH"

# Copy application code
COPY --chown=appuser:appgroup . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/test_logs && \
    chown -R appuser:appgroup /app/data /app/logs /app/test_logs

# Make health check script executable
RUN chmod +x health_check.py

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# Health check using our custom script
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python health_check.py || exit 1

# Expose port
EXPOSE 8501

# Production command
CMD ["streamlit", "run", "app_production.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false"]
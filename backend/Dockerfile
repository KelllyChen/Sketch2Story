# Multi-stage build to reduce image size
FROM python:3.10-slim-bookworm as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install to user directory (smaller footprint)
COPY requirements.txt .
RUN pip install --user --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# Final stage - much smaller
FROM python:3.10-slim-bookworm

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Create non-root user
RUN useradd -m -u 1001 appuser

WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY . .

# Set ownership and permissions
RUN chown -R appuser:appuser /app && \
    mkdir -p /app/voice_samples /app/logs && \
    chown -R appuser:appuser /app/voice_samples /app/logs

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$PORT/health || exit 1

# Run application
CMD ["python", "app.py"]
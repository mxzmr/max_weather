# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

# Copy wheels from builder stage
COPY --from=builder /app/wheels /app/wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /app/wheels/*

# Copy application code
COPY app/ ./app/
COPY main.py wsgi.py ./

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run with Gunicorn
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:8080", "wsgi:app"]

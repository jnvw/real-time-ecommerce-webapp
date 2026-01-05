# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY collab_commerce/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY collab_commerce/ /app/

# Create directory for media files
RUN mkdir -p /app/media

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port (Railway will set PORT env var to 8000)
EXPOSE 8000

# Create startup script to handle Railway's PORT variable properly
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'echo "=== Starting Collab Commerce ==="' >> /app/start.sh && \
    echo 'echo "Running migrations..."' >> /app/start.sh && \
    echo 'python manage.py migrate --noinput' >> /app/start.sh && \
    echo 'echo "Collecting static files..."' >> /app/start.sh && \
    echo 'python manage.py collectstatic --noinput' >> /app/start.sh && \
    echo 'if [ -z "$PORT" ]; then' >> /app/start.sh && \
    echo '  PORT=8000' >> /app/start.sh && \
    echo '  echo "WARNING: PORT not set, using default 8000"' >> /app/start.sh && \
    echo 'else' >> /app/start.sh && \
    echo '  echo "PORT environment variable is set to: $PORT"' >> /app/start.sh && \
    echo 'fi' >> /app/start.sh && \
    echo 'echo "Starting Daphne server on 0.0.0.0:$PORT"' >> /app/start.sh && \
    echo 'exec daphne -b 0.0.0.0 -p "$PORT" collab_commerce.asgi:application' >> /app/start.sh && \
    chmod +x /app/start.sh

# Railway sets PORT automatically - use startup script
CMD ["/app/start.sh"]


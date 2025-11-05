#!/bin/sh
# Entrypoint script for backend-inference-api
# Handles environment variable conversion and starts uvicorn

# Convert LOG_LEVEL to lowercase for uvicorn
if [ -n "$LOG_LEVEL" ]; then
    LOG_LEVEL=$(echo "$LOG_LEVEL" | tr '[:upper:]' '[:lower:]')
fi

# Set defaults
PORT=${PORT:-8000}
WORKERS=${WORKERS:-4}
LOG_LEVEL=${LOG_LEVEL:-info}

# Start uvicorn with environment variables
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level "$LOG_LEVEL" \
    --access-log \
    --proxy-headers \
    --forwarded-allow-ips '*'


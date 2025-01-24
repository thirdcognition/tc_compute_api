#!/bin/bash

SERVER_PORT=${SERVER_PORT:-8080}

# Function to handle cleanup on script exit
cleanup() {
    kill $(ps aux | grep spawn_main | awk '{print $2}')

    echo "Stopping Uvicorn..."
    kill "$UVICORN_PID"

    echo "Stopping Celery worker..."
    kill "$CELERY_WORKER_PID"

    echo "Stopping Flower..."
    kill "$FLOWER_PID"

    wait
    echo "Shutdown complete."
}

# Trap SIGINT and call cleanup()
trap cleanup SIGINT

# Check if running inside Docker
if [ -f /.dockerenv ]; then
    playwright install chromium
    playwright install-deps

    echo "Running inside Docker, starting server without reload."
    uvicorn app.server:app --host 0.0.0.0 --port "$SERVER_PORT" --log-config logging_prod.ini &
    UVICORN_PID=$!

    echo "Starting Celery worker"
    celery -A app.core.celery_app worker -B &
    CELERY_WORKER_PID=$!

    echo "Starting Flower on port $FLOWER_PORT"
    celery -A app.core.celery_app flower &
    FLOWER_PID=$!
else
    if ! docker inspect tc-redis &> /dev/null; then
        echo "tc-redis not found, starting Redis container..."
        docker run --name tc-redis -d -p 6379:6379 redis
    fi

    docker start tc-redis

    .venv/bin/playwright install chromium
    .venv/bin/playwright install-deps

    echo "Not running inside Docker, starting server with reload."
    .venv/bin/uvicorn app.server:app --host 0.0.0.0 --port "$SERVER_PORT" --reload --log-config logging.ini &
    UVICORN_PID=$!

    echo "Starting Celery worker"
    .venv/bin/celery -A app.core.celery_app worker -B &
    CELERY_WORKER_PID=$!

    echo "Starting Flower on port $FLOWER_PORT"
    .venv/bin/celery -A app.core.celery_app flower &
    FLOWER_PID=$!
fi

wait

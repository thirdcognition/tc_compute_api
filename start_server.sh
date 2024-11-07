#!/bin/bash

SERVER_PORT=${SERVER_PORT:-8080}

# Check if running inside Docker
if [ -f /.dockerenv ]; then
    echo "Running inside Docker, starting server without reload."
    uvicorn app.server:app --host 0.0.0.0 --port "$SERVER_PORT"
else
    echo "Not running inside Docker, starting server with reload."
    uvicorn app.server:app --host 0.0.0.0 --port "$SERVER_PORT" --reload
fi

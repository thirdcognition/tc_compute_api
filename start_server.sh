#!/bin/bash

SERVER_PORT=${SERVER_PORT:-8080}

uvicorn app.server:app --host 0.0.0.0 --port "$SERVER_PORT"
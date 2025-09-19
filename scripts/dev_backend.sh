#!/usr/bin/env bash
set -euo pipefail

export TESTING=${TESTING:-1}
export CORS_ALLOW_ORIGINS=${CORS_ALLOW_ORIGINS:-http://localhost:3000,http://127.0.0.1:3000}

echo "Starting InfinityAI backend (TESTING=$TESTING) with CORS_ALLOW_ORIGINS=$CORS_ALLOW_ORIGINS"
exec uvicorn engine.app.main:app --host 0.0.0.0 --port 8000 --log-level info

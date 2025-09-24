#!/usr/bin/env bash
set -euo pipefail

APP_URL="${APP_URL:-https://infinityai-backend-app.azurewebsites.net}"
ENDPOINT="${ENDPOINT:-/health}"
INTERVAL="${INTERVAL:-5}"
TIMEOUT="${TIMEOUT:-300}"

usage() {
  cat <<EOF
Usage: APP_URL=<url> TIMEOUT=300 INTERVAL=5 bash scripts/poll_health.sh
Environment variables:
  APP_URL   Base URL (default: https://infinityai-backend-app.azurewebsites.net)
  ENDPOINT  Health path (default: /health)
  INTERVAL  Seconds between polls (default: 5)
  TIMEOUT   Total seconds before giving up (default: 300)
EOF
}

start_time=$(date +%s)
echo "Polling $APP_URL$ENDPOINT until database=connected (timeout ${TIMEOUT}s)"

while true; do
  now=$(date +%s)
  elapsed=$(( now - start_time ))
  if (( elapsed > TIMEOUT )); then
    echo "Timed out after ${elapsed}s without database=connected" >&2
    exit 1
  fi
  json=$(curl -fsS -m 8 "$APP_URL$ENDPOINT" || true)
  if [[ -n "$json" ]]; then
    status=$(echo "$json" | sed -n 's/.*"database":"\([^"]*\)".*/\1/p') || true
    echo "[$elapsed s] database=$status"
    if [[ "$status" == "connected" ]]; then
      echo "SUCCESS: database connected after ${elapsed}s"
      exit 0
    fi
  else
    echo "[$elapsed s] no response"
  fi
  sleep "$INTERVAL"
done

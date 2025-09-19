#!/usr/bin/env bash
set -euo pipefail

# Use Node 18 with nvm in this shell
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
  . "$NVM_DIR/nvm.sh"
elif [ -s "/usr/local/share/nvm/nvm.sh" ]; then
  . "/usr/local/share/nvm/nvm.sh"
else
  echo "nvm not found in this container. Please install or source nvm before running." >&2
  exit 1
fi

nvm install 18
nvm use 18

export REACT_APP_API_URL=${REACT_APP_API_URL:-http://localhost:8000}
echo "Starting dashboard with Node $(node -v), API=$REACT_APP_API_URL"

cd "$(dirname "$0")/../dashboard"
npm ci || npm install
npm start

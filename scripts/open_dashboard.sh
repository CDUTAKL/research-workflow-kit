#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DASHBOARD_DIR="${ROOT_DIR}/dashboard-web"
URL="${DASHBOARD_URL:-http://127.0.0.1:5173/}"

export PATH="/opt/homebrew/bin:${PATH}"

if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm not found. Install it with: brew install pnpm"
  exit 1
fi

cd "${DASHBOARD_DIR}"

if [ ! -d "node_modules" ]; then
  echo "Installing dashboard dependencies..."
  pnpm install
fi

echo "Preparing dashboard data..."
pnpm run prepare:data

if ! lsof -ti tcp:8765 >/dev/null 2>&1; then
  echo "Starting dashboard control server on 127.0.0.1:8765..."
  (cd "${ROOT_DIR}" && python3 scripts/dashboard_control_server.py --host 127.0.0.1 --port 8765) &
fi

echo "Opening ${URL}"
open "${URL}" >/dev/null 2>&1 || true

echo "Starting dashboard server. Keep this terminal window open while using the dashboard."
pnpm exec vite --host 127.0.0.1

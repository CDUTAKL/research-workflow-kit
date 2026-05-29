#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DASHBOARD_DIR="${ROOT_DIR}/dashboard-web"
URL="${DASHBOARD_URL:-http://127.0.0.1:5173/}"
LOG_DIR="${ROOT_DIR}/tmp/dashboard"
CONTROL_LOG="${LOG_DIR}/control-server.log"
VITE_LOG="${LOG_DIR}/vite.log"
OPEN_BROWSER=1

if [ "${1:-}" = "--no-open" ]; then
  OPEN_BROWSER=0
fi

export PATH="/opt/homebrew/bin:${PATH}"
export NO_PROXY="127.0.0.1,localhost,${NO_PROXY:-}"
export no_proxy="127.0.0.1,localhost,${no_proxy:-}"

mkdir -p "${LOG_DIR}"

if ! command -v pnpm >/dev/null 2>&1; then
  osascript -e 'display dialog "未找到 pnpm。请先运行：brew install pnpm" buttons {"好"} default button "好"'
  exit 1
fi

cd "${DASHBOARD_DIR}"

if [ ! -d "node_modules" ]; then
  pnpm install >>"${VITE_LOG}" 2>&1
fi

pnpm run prepare:data >>"${VITE_LOG}" 2>&1

if ! lsof -ti tcp:8765 >/dev/null 2>&1; then
  nohup python3 "${ROOT_DIR}/scripts/dashboard_control_server.py" --host 127.0.0.1 --port 8765 >"${CONTROL_LOG}" 2>&1 &
fi

if ! lsof -ti tcp:5173 >/dev/null 2>&1; then
  nohup pnpm run dev -- --host 127.0.0.1 >"${VITE_LOG}" 2>&1 &
fi

python3 - <<'PY'
import time
import urllib.request

url = "http://127.0.0.1:5173/"
for _ in range(60):
    try:
        with urllib.request.urlopen(url, timeout=0.4) as response:
            if response.status < 500:
                break
    except Exception:
        time.sleep(0.3)
PY

if [ "${OPEN_BROWSER}" = "1" ]; then
  open "${URL}"
fi

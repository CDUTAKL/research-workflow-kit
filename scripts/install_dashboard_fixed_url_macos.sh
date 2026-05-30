#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_DIR="${HOME}/Library/LaunchAgents"
PLIST_PATH="${PLIST_DIR}/com.researchworkflow.dashboard.plist"
LABEL="com.researchworkflow.dashboard"
SUPPORT_DIR="${HOME}/Library/Application Support/ResearchWorkflowDashboard"
RUNNER_PATH="${SUPPORT_DIR}/start-dashboard.sh"

mkdir -p "${PLIST_DIR}"
mkdir -p "${SUPPORT_DIR}"

cat >"${RUNNER_PATH}" <<RUNNER
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${ROOT_DIR}"
SUPPORT_DIR="${SUPPORT_DIR}"
DASHBOARD_DIR="\${ROOT_DIR}/dashboard-web"
LOG_DIR="\${SUPPORT_DIR}/logs"
CONTROL_LOG="\${LOG_DIR}/control-server.log"
VITE_LOG="\${LOG_DIR}/vite.log"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:\${PATH:-}"
export NO_PROXY="127.0.0.1,localhost,\${NO_PROXY:-}"
export no_proxy="127.0.0.1,localhost,\${no_proxy:-}"

mkdir -p "\${LOG_DIR}"

if ! command -v pnpm >/dev/null 2>&1; then
  echo "pnpm not found. Install it with: brew install pnpm" >>"\${VITE_LOG}"
  exit 1
fi

cd "\${DASHBOARD_DIR}"

if [ ! -d "node_modules" ]; then
  pnpm install >>"\${VITE_LOG}" 2>&1
fi

mkdir -p "\${DASHBOARD_DIR}/public/data"
cd "\${ROOT_DIR}"
python3 scripts/research_workflow_doctor.py --write-data --json-out dashboard-web/public/data/dashboard-data.json --warn-only >>"\${VITE_LOG}" 2>&1 || true
python3 scripts/export_evidence_graph.py --out dashboard-web/public/data/evidence-graph.json --mermaid dashboard-web/public/data/evidence-graph.mmd >>"\${VITE_LOG}" 2>&1 || true

if ! lsof -ti tcp:8765 >/dev/null 2>&1; then
  nohup python3 "\${ROOT_DIR}/scripts/dashboard_control_server.py" --host 127.0.0.1 --port 8765 >"\${CONTROL_LOG}" 2>&1 &
fi

if lsof -ti tcp:5173 >/dev/null 2>&1; then
  echo "Dashboard frontend already listening on 127.0.0.1:5173" >>"\${VITE_LOG}"
  while true; do
    sleep 300
  done
fi

cd "\${DASHBOARD_DIR}"
exec pnpm exec vite --host 127.0.0.1
RUNNER

chmod +x "${RUNNER_PATH}"
xattr -dr com.apple.quarantine "${RUNNER_PATH}" >/dev/null 2>&1 || true

cat >"${PLIST_PATH}" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>${RUNNER_PATH}</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>300</integer>
  <key>StandardOutPath</key>
  <string>${SUPPORT_DIR}/logs/launch-agent.log</string>
  <key>StandardErrorPath</key>
  <string>${SUPPORT_DIR}/logs/launch-agent.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)" "${PLIST_PATH}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "${PLIST_PATH}"
launchctl kickstart -k "gui/$(id -u)/${LABEL}"

rm -f "${HOME}/Desktop/科研工作流总控台.app"

echo "Installed fixed local dashboard URL service:"
echo "  ${PLIST_PATH}"
echo "  ${RUNNER_PATH}"
echo "Open in your browser:"
echo "  http://127.0.0.1:5173/"

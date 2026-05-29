#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_DIR="${HOME}/Library/LaunchAgents"
PLIST_PATH="${PLIST_DIR}/com.researchworkflow.dashboard.plist"
LABEL="com.researchworkflow.dashboard"

mkdir -p "${PLIST_DIR}"

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
    <string>${ROOT_DIR}/scripts/open_dashboard_background.sh</string>
    <string>--no-open</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StartInterval</key>
  <integer>300</integer>
  <key>StandardOutPath</key>
  <string>${ROOT_DIR}/tmp/dashboard/launch-agent.log</string>
  <key>StandardErrorPath</key>
  <string>${ROOT_DIR}/tmp/dashboard/launch-agent.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$(id -u)" "${PLIST_PATH}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "${PLIST_PATH}"
launchctl kickstart -k "gui/$(id -u)/${LABEL}"

rm -f "${HOME}/Desktop/科研工作流总控台.app"

echo "Installed fixed local dashboard URL service:"
echo "  ${PLIST_PATH}"
echo "Open in your browser:"
echo "  http://127.0.0.1:5173/"

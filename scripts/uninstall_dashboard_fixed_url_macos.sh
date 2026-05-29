#!/usr/bin/env bash
set -euo pipefail

PLIST_PATH="${HOME}/Library/LaunchAgents/com.researchworkflow.dashboard.plist"
LABEL="com.researchworkflow.dashboard"

launchctl bootout "gui/$(id -u)" "${PLIST_PATH}" >/dev/null 2>&1 || true
rm -f "${PLIST_PATH}"

lsof -ti tcp:5173 -sTCP:LISTEN | xargs -r kill
lsof -ti tcp:8765 -sTCP:LISTEN | xargs -r kill

echo "Removed ${LABEL} and stopped dashboard services."

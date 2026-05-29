#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_NAME="科研工作流总控台.app"
APP_PATH="${HOME}/Applications/${APP_NAME}"
DESKTOP_LINK="${HOME}/Desktop/${APP_NAME}"

mkdir -p "${HOME}/Applications"

osascript_source="do shell script \"cd ${ROOT_DIR} && /bin/bash scripts/open_dashboard_background.sh >/tmp/research-workflow-dashboard-launch.log 2>&1 &\""
osacompile -o "${APP_PATH}" -e "${osascript_source}"

rm -f "${DESKTOP_LINK}"
ln -s "${APP_PATH}" "${DESKTOP_LINK}"

echo "Installed: ${APP_PATH}"
echo "Desktop shortcut: ${DESKTOP_LINK}"

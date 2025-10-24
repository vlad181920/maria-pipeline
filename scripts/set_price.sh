#!/bin/bash
set -euo pipefail

PRICE="${1:-}"
if [[ -z "$PRICE" ]]; then
  echo "usage: set_price.sh <PRICE_USD>" >&2
  exit 1
fi

USER_ID="$(id -u)"

if launchctl kickstart -k "gui/${USER_ID}/com.maria.earn.loop" 2>/dev/null; then
  echo "[set_price] loop kickstarted with $PRICE"
else
  echo "[set_price] kickstart failed, trying load"
  launchctl load "$HOME/Library/LaunchAgents/com.maria.earn.loop.plist" 2>/dev/null || true
fi

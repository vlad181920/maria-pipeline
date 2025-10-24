#!/bin/bash
set -euo pipefail

ts_iso() { date +"%Y-%m-%dT%H:%M:%S%z"; }
log() { echo "[guard] $(ts_iso) $*"; }
err() { echo "[guard][ERR] $(ts_iso) $*" >&2; }

export HOME="${HOME:-/Users/macbook}"
export PATH="${PATH:-/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin}"
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

TMP_OUT="/tmp/maria_health.out"
TMP_ERR="/tmp/maria_health.err"
LOG_DIR="$REPO_ROOT/artifacts/earn/logs"
mkdir -p "$LOG_DIR"

log "guard start (cwd=$REPO_ROOT)"

if ./bin/maria health >"$TMP_OUT" 2>"$TMP_ERR"; then
  log "health executed OK"
else
  err "health returned non-zero"
fi

USER_ID="$(id -u)"
if launchctl print "gui/${USER_ID}/com.maria.earn.loop" >/dev/null 2>&1; then
  if launchctl kickstart -k "gui/${USER_ID}/com.maria.earn.loop" 2>>"$TMP_ERR"; then
    log "loop kickstart OK"
  else
    err "loop kickstart failed"
  fi
else
  if launchctl load "$HOME/Library/LaunchAgents/com.maria.earn.loop.plist" 2>>"$TMP_ERR"; then
    log "loop load OK"
  else
    err "loop load failed"
  fi
fi

USER_ID2="$(id -u)"
launchctl print "gui/${USER_ID2}/com.maria.earn.loop" 2>/dev/null \
  | awk '/--target-price/{print $0}' \
  | head -n1 > "$TMP_OUT.targetprice" 2>/dev/null || true

if [[ -s "$TMP_OUT.targetprice" ]]; then
  target_price_launchd="$(awk '{last=$0}END{print last}' "$TMP_OUT.targetprice")"
else
  target_price_launchd="unknown"
fi

log "pricing (launchd target-price) = $target_price_launchd"
log "guard end"

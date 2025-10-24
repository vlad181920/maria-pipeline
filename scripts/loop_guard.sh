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
TMP_PRICE_RAW="/tmp/maria_target_price_raw"
LOG_DIR="$REPO_ROOT/artifacts/earn/logs"
CONFIG_DIR="$REPO_ROOT/config"
ENV_FILE="$CONFIG_DIR/earn.env"

mkdir -p "$LOG_DIR" "$CONFIG_DIR"

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

launchctl print "gui/${USER_ID}/com.maria.earn.loop" 2>/dev/null \
  | awk '/--target-price/{found=1;next} found{print $0;exit}' \
  > "$TMP_PRICE_RAW" 2>/dev/null || true

if [[ -s "$TMP_PRICE_RAW" ]]; then
  launchd_price="$(tr -d '[:space:]' < "$TMP_PRICE_RAW")"
else
  launchd_price="unknown"
fi

current_target="unknown"
if [[ -f "$ENV_FILE" ]]; then
  current_target="$(grep '^TARGET_PRICE=' "$ENV_FILE" | head -n1 | cut -d'=' -f2- | tr -d '[:space:]' || true)"
fi

log "pricing launchd=$launchd_price target_env=$current_target"

if [[ "$current_target" != "unknown" && "$launchd_price" != "$current_target" ]]; then
  if [[ -x "$REPO_ROOT/bin/maria" ]]; then
    log "price drift detected ($launchd_price != $current_target) -> maria price $current_target"
    "$REPO_ROOT/bin/maria" price "$current_target" >>"$TMP_ERR" 2>&1 || err "maria price failed"
  else
    err "maria binary missing, cannot sync price"
  fi
fi

log "guard end"

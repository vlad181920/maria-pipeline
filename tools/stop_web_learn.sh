#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
PIDF="artifacts/logs/web_learn.pid"
[ -f "$PIDF" ] && kill "$(cat "$PIDF")" 2>/dev/null || true
rm -f artifacts/logs/web_learn.pid artifacts/logs/web_learn.port
echo "[ok] web_learn stopped"

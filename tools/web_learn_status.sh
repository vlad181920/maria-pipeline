#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
PORT=$(cat artifacts/logs/web_learn.port 2>/dev/null || echo "n/a")
PID=$(cat artifacts/logs/web_learn.pid 2>/dev/null || echo "")
if [ -n "$PID" ] && ps -p "$PID" >/dev/null 2>&1; then
  echo "[status] running pid=$PID port=$PORT"
else
  echo "[status] not running"
fi
echo "--- err ---"
tail -n 50 artifacts/logs/web_learn_server.err 2>/dev/null || true
echo "--- out ---"
tail -n 10 artifacts/logs/web_learn_server.out 2>/dev/null || true

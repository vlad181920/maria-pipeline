#!/usr/bin/env bash
cd "$(dirname "$0")/.."
PID_FILE="artifacts/logs/pipeline_daemon.pid"
LOG_OK="artifacts/logs/pipeline_daemon.out"
LOG_ERR="artifacts/logs/pipeline_daemon.err"
if [ ! -f "$PID_FILE" ]; then
  echo "[status] not running (no pid file)"; exit 1
fi
PID=$(cat "$PID_FILE")
if ps -p "$PID" >/dev/null 2>&1; then
  echo "[status] running pid=$PID"
else
  echo "[status] not running (stale pid=$PID)"; exit 2
fi
echo "--- last out ---"; tail -n 10 "$LOG_OK" 2>/dev/null || true
echo "--- last err ---"; tail -n 10 "$LOG_ERR" 2>/dev/null || true

#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
PID_FILE="artifacts/logs/pipeline_daemon.pid"
if [ -f "$PID_FILE" ]; then
  kill "$(cat "$PID_FILE")" 2>/dev/null || true
  rm -f "$PID_FILE"
  echo "[ok] stopped pipeline_daemon"
else
  echo "[info] no pid file"
fi

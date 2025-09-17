#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
LOG_DIR="artifacts/logs"
OUT="$LOG_DIR/pipeline_daemon.out"
ERR="$LOG_DIR/pipeline_daemon.err"
mkdir -p "$LOG_DIR"
nohup python3 tools/pipeline_daemon.py >>"$OUT" 2>>"$ERR" &
echo $! > "$LOG_DIR/pipeline_daemon.pid"
echo "[ok] started pipeline_daemon pid=$(cat "$LOG_DIR/pipeline_daemon.pid")"

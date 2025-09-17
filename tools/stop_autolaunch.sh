#!/usr/bin/env bash
set -e
PIDFILE="artifacts/logs/autolaunch.pid"
if [ -f "$PIDFILE" ]; then
  kill "$(cat "$PIDFILE")" 2>/dev/null || true
  rm -f "$PIDFILE"
  echo "[ok] autolaunch stopped"
else
  echo "[info] no autolaunch pid"
fi

#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
PIDF=artifacts/logs/nightly_summary.pid
if [ -f "$PIDF" ] && ps -p "$(cat "$PIDF")" >/dev/null 2>&1; then
  echo "[status] nightly_summary running pid=$(cat "$PIDF")"
else
  echo "[status] nightly_summary not running"
fi
echo "--- err ---"; tail -n 20 artifacts/logs/nightly_summary.err 2>/dev/null || true
echo "--- out ---"; tail -n 10 artifacts/logs/nightly_summary.out 2>/dev/null || true
